from balancer_agent.core import json_logger, metrics
from balancer_agent.core.exceptions import KeepalivedWaitTimeoutExceed, RestoreConfigError, TaskDeployError
from balancer_agent.operations.balancer_configs.config_renderers import RENDERERS
from balancer_agent.operations.systems import ipvs, keepalived
from balancer_agent.operations.tasks.handlers import waiter
from balancer_agent.operations.tasks.handlers.base_test_tasks import BaseTestTasksHandler

logger = json_logger.Logger().get("Tasks")


class TestTasksHandler(BaseTestTasksHandler):
    def __init__(self, agent_settings):
        super().__init__(agent_settings)
        self.ipvs = ipvs.IPVS()
        self.keepalived: keepalived.ConfigurationTestingManager = keepalived.KeepalivedTest()

    def process_task(self) -> None:
        try:
            generator = RENDERERS[self.agent_settings.generator_version]
            self.keepalived.apply_config(
                generator(self.task.config.body).get_full_config(test=True), self.task.config.body
            )
            waiter.wait_for(self.task.config, self.ipvs.get_services)
            self.send_task_status_to_l3()
        except Exception as e:
            # KeepalivedWaitTimeoutExceed is expected exception, no need fo metric report
            if not isinstance(e, KeepalivedWaitTimeoutExceed):
                metrics.METRICS_REPORTER.push_exc(e, metrics.METRICS_REPORTER)
            logger.exception("Task deployment error")
            try:
                self.send_task_status_to_l3(e)
            except Exception as e:
                metrics.METRICS_REPORTER.push_exc(e, metrics.METRICS_REPORTER)
                logger.exception("Could not report deployment status to L3")

            raise TaskDeployError
        else:
            try:
                self.keepalived.erase_config()
                self.ipvs.reset()
            except Exception as e:
                logger.exception("Could not erase config after deploy")
                metrics.METRICS_REPORTER.push_exc(e, metrics.METRICS_REPORTER)

                raise TaskDeployError from e

    @metrics.METRICS_REPORTER.push_execution_time
    @metrics.METRICS_REPORTER.push_errors(sync=False)
    def restore_config(self) -> None:
        """
        Replace failed Keepalived config to empty config
        and save failed config to history
        """
        try:
            self.keepalived.restore_config(self.task.config.body.service.fqdn, self.task.config.body.id)
            self.ipvs.reset()
        except Exception as e:
            logger.exception("Config restoration failed")
            raise RestoreConfigError(e) from e
        else:
            logger.info("Config restoration succeed")
