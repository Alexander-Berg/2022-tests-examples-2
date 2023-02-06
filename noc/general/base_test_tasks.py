from abc import abstractmethod
from datetime import datetime
from http import HTTPStatus
from json.decoder import JSONDecodeError

import requests
import ujson
from retrying import retry

from balancer_agent import definitions as defs
from balancer_agent.core import json_logger, metrics, status_codes
from balancer_agent.core.exceptions import PollingTasksError, SendTaskStatusTimeoutExceed
from balancer_agent.operations.balancer_configs.config_containers import BalancerConfigState
from balancer_agent.operations.settings import TaskPollingIntervalCalculator
from balancer_agent.operations.tasks.handlers.base import TASK_RESULT, TasksHandler, retryable_exceptions
from balancer_agent.operations.tasks.helpers import DiagInfoContext, raise_custom_on_retry_error
from balancer_agent.operations.tasks.task_containers import TaskToTest
from balancer_agent.operations.tasks.task_queue import TaskQueue

import typing
from typing import TYPE_CHECKING, Dict, Type

if TYPE_CHECKING:
    # To avoid circular imports and not importing unnecessary libs in runtime
    from balancer_agent.operations.tasks.task_containers import TaskBase

logger = json_logger.Logger().get("Tasks")


class BaseTestTasksHandler(TasksHandler):
    COLLECT_TASKS_URI = "/tasks/current"

    task: TaskToTest

    def __init__(self, agent_settings):
        super().__init__(agent_settings)

    @TaskPollingIntervalCalculator.tasks_by_time
    @metrics.METRICS_REPORTER.push_errors(sync=False)
    @retry(
        retry_on_exception=retryable_exceptions,
        stop_max_attempt_number=TasksHandler.COLLECT_TASK_ATTEMPTS,
        wait_exponential_multiplier=TasksHandler.COLLECT_TASK_EXPONENTIAL_MULTIPLIER_MS,
        wait_exponential_max=TasksHandler.COLLECT_TASK_WAIT_MAX_MS,
    )
    def collect_tasks(self) -> int:
        """
        Collects tasks from L3 API, validates and evaluates the correctness of tasks
        """
        # TODO: Move setting tasks queue attriute to __init__
        self.tasks_queue = TaskQueue(self.agent_settings, TaskToTest)

        try:
            l3_response = requests.post(
                self._collect_tasks_url,
                headers=self.headers,
                data=ujson.dumps(
                    {
                        **self._get_self_identities(),
                        **{"ts": datetime.now().timestamp(), "error": {"message": None, "code": 0}},
                    }
                ),
                verify=False,
                timeout=defs.L3_TIMEOUTS,
            )
        except (IOError, ValueError):
            logger.exception(f"Could not collect tasks from {self.agent_settings.l3_hosts_pool.current_host}")
            raise PollingTasksError(f"Could not collect tasks from {self.agent_settings.l3_hosts_pool.current_host}")

        if l3_response.status_code == HTTPStatus.NOT_FOUND:
            logger.info("No active tasks")
            return 0

        if l3_response.status_code != HTTPStatus.OK:
            logger.error(
                f"Unexpected repsponse code from L3 API host {self.agent_settings.l3_hosts_pool.current_host} "
                f"while collecting tasks: {l3_response.status_code}\n"
                f"Response body: {l3_response.text}"
            )
            raise PollingTasksError(
                f"Unexpected repsponse code from L3 API host {self.agent_settings.l3_hosts_pool.current_host} "
                f"while collecting tasks: {l3_response.status_code}"
            )

        try:
            tasks = l3_response.json()
        except ValueError as e:
            logger.exception(f"Could not jsonify response from {self.agent_settings.l3_hosts_pool.current_host}")
            raise PollingTasksError(
                f"Could not jsonify response from {self.agent_settings.l3_hosts_pool.current_host} due to: {e}"
            )

        self.tasks_queue.add_new_tasks(tasks)

        if self.tasks_queue.invalid_tasks:
            for task, validation_error in self.tasks_queue.invalid_tasks:
                try:
                    metrics.METRICS_REPORTER.push_errors(sync=False)(
                        self.send_invalid_task_status_to_l3(task, validation_error)
                    )
                except Exception:
                    try:
                        # Validate can jsonify
                        ujson.dumps(getattr(task, "task", None))

                        logger.exception(
                            "Could not report deploy failure. Invalid task body",
                            extra=dict(additional=getattr(task, "task", None)),
                        )
                    except (ValueError, TypeError):
                        pass

                    # TODO: check which exception stack will be logged
                    logger.exception(
                        f"Could not report deploy failure. Invalid task body {getattr(task, 'task', None)}"
                    )

        logger.info(f"Collected tasks: valid {self.tasks_queue.amount}, invalid {len(self.tasks_queue.invalid_tasks)}")

        return self.tasks_queue.amount

    @metrics.METRICS_REPORTER.push_execution_time
    @DiagInfoContext.store_report
    def handle_task(self) -> None:
        """
        Task deployment workflow.
        If a task execution has not succeed by any reson (like not enough RSs for quorum up)
        Execution exception will happen and we will try to send the current status of the task
        to L3.
        """
        task: typing.Optional[TaskToTest] = self.tasks_queue.get_next_task()

        if not task:
            return

        self.task = task
        logger.info(f"Starting processing task: {self.task.id} config id: {self.task.config.body.id}")
        self.process_task()

    @abstractmethod
    def process_task(self) -> None:
        raise NotImplementedError()

    @raise_custom_on_retry_error(exc=SendTaskStatusTimeoutExceed, message="Send task status to l3 timeout exceed")
    @retry(
        retry_on_result=lambda task_result: task_result.response_code >= 400
        and task_result.response_code not in {HTTPStatus.CONFLICT, HTTPStatus.NOT_FOUND},
        stop_max_attempt_number=TasksHandler.SEND_TASK_STATUS_ATTEMPTS,
        wait_exponential_multiplier=TasksHandler.SEND_TASK_STATUS_EXPONENTIAL_MULTIPLIER_MS,
        wait_exponential_max=TasksHandler.SEND_TASK_STATUS_WAIT_MAX_MS,
    )
    @DiagInfoContext.add_task_result
    def send_task_status_to_l3(self, error=None) -> TASK_RESULT:
        """
        Send execution result of a valid (having correct parameters) task.
        """

        task_status = {
            "id": self.task.id,
            "overall_deployment_status": self.task.config.state.overall_deployment_status(),
            "vss": self.task.config.state.vs_deployment_status,
            "ts": datetime.now().timestamp(),
            "error": self._get_status_error_field(error),
        }

        logger.info("Task execution status", extra=dict(additional=dict(task_status=task_status)))

        l3_response = requests.put(
            # Check for a number for unknown status code
            self.get_task_execution_report_url(self.task.id),
            headers=self.headers,
            data=ujson.dumps(task_status),
            verify=False,
            allow_redirects=True,
            timeout=defs.L3_TIMEOUTS,
        )

        if l3_response.status_code >= 300:
            try:
                body = l3_response.json()
                logger.error(
                    f"Unexpected response from L3. Code: {l3_response.status_code}",
                    extra=dict(additional=dict(response_body=body)),
                )
            except JSONDecodeError:
                logger.error(
                    f"Unexpected response from L3. Code: {l3_response.status_code}, body:\n {l3_response.text}"
                )

        return TASK_RESULT(l3_response.status_code, task_status)

    # @metrics.METRICS_REPORTER.push_execution_time
    # @metrics.METRICS_REPORTER.push_errors(sync=False)
    # def restore_config(self) -> None:
    #     """
    #     Replace failed Keepalived config to empty config
    #     and save failed config to history
    #     """
    #     try:
    #         self.task = cast(TaskToTest, self.task)
    #         self.keepalived.restore_config(self.task.config.body.service.fqdn, self.task.config.body.id)
    #         self.ipvs.reset()
    #     except Exception as e:
    #         logger.exception("Config restoration failed")
    #         raise RestoreConfigError(e) from e
    #     else:
    #         logger.info("Config restoration succeed")

    def rollback_config(self) -> None:
        """
        There is no rollback for test agent
        """
        logger.info("Config rollback succeed")

    def send_rollback_status_to_l3(self) -> None:
        """
        There is no rollback for test agent
        """
        pass

    @retry(
        retry_on_result=lambda response_code: response_code >= 400
        and response_code not in {HTTPStatus.CONFLICT, HTTPStatus.NOT_FOUND},
        stop_max_attempt_number=TasksHandler.SEND_TASK_STATUS_ATTEMPTS,
        wait_exponential_multiplier=TasksHandler.SEND_TASK_STATUS_EXPONENTIAL_MULTIPLIER_MS,
        wait_exponential_max=TasksHandler.SEND_TASK_STATUS_WAIT_MAX_MS,
    )
    def send_invalid_task_status_to_l3(self, task: Type["TaskBase"], validation_error: str) -> int:
        task_status = {
            "id": getattr(task, "id", 0),
            "overall_deployment_status": BalancerConfigState.FAILURE_STATUS,
            "vss": [],
            "ts": datetime.now().timestamp(),
            "error": {"message": validation_error, "code": status_codes.ServiceErrorCodes.TASK_VALIDATION_ERROR.value},
        }

        l3_response = requests.put(
            self.get_task_execution_report_url(getattr(task, "id", 0)),
            headers=self.headers,
            data=ujson.dumps(task_status),
            verify=False,
            allow_redirects=True,
            timeout=defs.L3_TIMEOUTS,
        )

        if l3_response.status_code >= 300:
            try:
                body = l3_response.json()
                logger.error(
                    f"Unexpected response from L3. Code: {l3_response.status_code}",
                    extra=dict(additional=dict(response_body=body)),
                )
            except JSONDecodeError:
                logger.error(
                    f"Unexpected response from L3. Code: {l3_response.status_code}, body:\n {l3_response.text}"
                )
        else:
            logger.warning("Reported invalid task status to L3", extra=dict(additional=dict(task_status=task_status)))

        return l3_response.status_code

    @property
    def _collect_tasks_url(self) -> str:
        return self.l3_host + "/" + defs.LB_NAME + self.COLLECT_TASKS_URI

    def _get_self_identities(self) -> Dict[str, str]:
        return {"id": defs.LB_NAME, "generator_version": self.agent_settings.generator_version}

    def get_task_execution_report_url(self, task_id: int) -> str:
        return self.l3_host + "/" + defs.LB_NAME + "/tasks/" + str(task_id) + "/deployment-status"
