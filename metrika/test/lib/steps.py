import datetime
import logging
import pprint

import psycopg2.errors
import walle_api.client
from hamcrest import equal_to, not_, has_item, has_entry

import allure
import metrika.admin.python.cms.lib.action as action
import metrika.admin.python.cms.lib.agent.client as agent_client
import metrika.admin.python.cms.lib.client as lib_client
import metrika.admin.python.cms.lib.fsm.states as fsm
import metrika.admin.python.cms.test.lib.mock_cluster_api as mock_cluster_api
import metrika.core.test_framework.utils.wait as wait
import metrika.pylib.mtapi.cluster as cluster
from metrika.admin.python.cms.test.lib.mock_agent_api import MockAgentApi
from metrika.admin.python.cms.test.lib.mock_cluster_api import MockClusterApi, MockRecord
from metrika.admin.python.cms.test.lib.mock_internal_api import MockInternalApi
from metrika.admin.python.cms.test.lib.mock_walle_api import MockWalleApi
from metrika.core.test_framework.steps.verification import VerificationSteps

logger = logging.getLogger(__name__)


class InputSteps:
    def __init__(self, http_input_steps, queue, internal_api_mock: MockInternalApi, cluster_api_mock: MockClusterApi, agent_api_mock: MockAgentApi, walle_api_mock: MockWalleApi):
        self.http = http_input_steps
        self.queue = queue
        self.internal_api = internal_api_mock
        self.cluster_api = cluster_api_mock
        self.agent_api = agent_api_mock
        self.walle_api = walle_api_mock

    @allure.step
    def clean_queue(self):
        try:
            while self.queue.list():
                try:
                    with self.queue.try_get_item() as item:
                        item.consume()
                except psycopg2.errors.Error:
                    logger.warning("Exception in clean_queue. Continue.", exc_info=True)
        except:
            logger.warning("Exception in queue listing. Continue.", exc_info=True)

    @allure.step
    def clean_mocks(self):
        self.setup_cluster_api([])
        self.setup_not_loaded_tasks_empty()
        self.setup_agent_api_mock()

    @allure.step
    def ping(self):
        return self.http.request("/ping", raise_for_status=False).ok

    @allure.step
    def status(self):
        return self.http.request("/status", raise_for_status=False).json()

    @property
    def next_walle_id(self):
        return datetime.datetime.now().timestamp()

    @allure.step
    def setup_cluster_api(self, mapping):
        self.cluster_api.mapping = mapping

    @allure.step
    def setup_cluster_api_for_cmsstand(self):
        self.setup_cluster_api(
            [
                MockRecord(handle="/get", params={"fqdn": "mtcmsstand01kt"},
                                            response=[{'type': "mtcmsstand", 'shard_id': "mtcmsstand-testing", 'environment': "testing"}]),
                MockRecord(handle="/get", params={"fqdn": "mtcmsstand02kt"},
                                            response=[{'type': "mtcmsstand", 'shard_id': "mtcmsstand-testing", 'environment': "testing"}]),
                MockRecord(handle="/list/fqdn", params={"fqdn": "!mtcmsstand01kt", "shard_id": "mtcmsstand-testing"},
                                            response=['mtcmsstand02kt']),
                MockRecord(handle="/list/fqdn", params={"fqdn": "!mtcmsstand02kt", "shard_id": "mtcmsstand-testing"},
                                            response=['mtcmsstand01kt']),
                MockRecord(handle="/get", params={"fqdn": ["mtcmsstand01kt"]},
                                            response=[{'fqdn': 'mtcmsstand01kt', 'type': "mtcmsstand", 'shard_id': "mtcmsstand-testing", 'environment': "testing"}]),
                MockRecord(handle="/get", params={"fqdn": ["mtcmsstand02kt"]},
                                            response=[{'fqdn': 'mtcmsstand02kt', 'type': "mtcmsstand", 'shard_id': "mtcmsstand-testing", 'environment': "testing"}])
            ]
        )

    @allure.step
    def setup_cluster_api_for_mtcalclog(self):
        self.setup_cluster_api(
            [
                MockRecord(handle="/get", params={"fqdn": "mtcalclog01kt"},
                                            response=[{'type': "mtcalclog", 'shard_id': "mtcalclog-testing", 'environment': "testing"}]),
                MockRecord(handle="/get", params={"fqdn": "mtcalclog02kt"},
                                            response=[{'type': "mtcalclog", 'shard_id': "mtcalclog-testing", 'environment': "testing"}]),
                MockRecord(handle="/list/fqdn", params={"fqdn": "!mtcalclog01kt", "shard_id": "mtcalclog-testing"},
                                            response=['mtcalclog02kt']),
                MockRecord(handle="/list/fqdn", params={"fqdn": "!mtcalclog02kt", "shard_id": "mtcalclog-testing"},
                                            response=['mtcalclog01kt']),
                MockRecord(handle="/get", params={"fqdn": ["mtcalclog01kt"]},
                                            response=[{'fqdn': 'mtcalclog01kt', 'type': "mtcalclog", 'shard_id': "mtcalclog-testing", 'environment': "testing"}]),
                MockRecord(handle="/get", params={"fqdn": ["mtcalclog02kt"]},
                                            response=[{'fqdn': 'mtcalclog02kt', 'type': "mtcalclog", 'shard_id': "mtcalclog-testing", 'environment': "testing"}])
            ]
        )

    @allure.step
    def setup_cluster_api_for_mtlast(self):
        self.setup_cluster_api(
            [
                mock_cluster_api.MockRecord(
                    handle="/get", params={"fqdn": "mtlast01it"},
                    response=[{'type': "mtlast", 'shard_id': "mtlast-testing", 'environment': "testing"}]
                ),
                mock_cluster_api.MockRecord(
                    handle="/list/fqdn", params={"fqdn": "!mtlast01it", "shard_id": "mtlast-testing"}, response=[]),
                mock_cluster_api.MockRecord(
                    handle="/get", params={"fqdn": ["mtlast01it"]},
                    response=[{'fqdn': 'mtlast01it', 'type': "mtlast", 'shard_id': "mtlast-testing", 'environment': "testing"}]
                ),
            ]
        )

    @allure.step
    def setup_not_loaded_tasks(self, tasks):
        self.internal_api.not_loaded_tasks = tasks

    @allure.step
    def setup_not_loaded_tasks_empty(self):
        self.setup_not_loaded_tasks([])

    @allure.step
    def setup_not_loaded_host(self, host, internal_status):
        self.setup_not_loaded_tasks(
            [
                {
                    "walle_hosts": [host],
                    "internal_status": internal_status
                }
            ]
        )

    @allure.step
    def setup_agent_api_mock(self, ping=True, host_status=None, unloading_status=None, loading_status=None, after_loading_status=None,
                             loading_initiate_status=None, loading_finalize_status=None):
        self.agent_api.ping_result = ping
        self.agent_api.host_status_response = host_status
        self.agent_api.unloading_status_response = unloading_status
        self.agent_api.loading_status_response = loading_status
        self.agent_api.after_loading_status_response = after_loading_status
        self.agent_api.loading_initiate_status_response = loading_initiate_status
        self.agent_api.loading_finalize_status_response = loading_finalize_status
        self.agent_api.start_loading_initiate_calls = 0
        self.agent_api.stop_loading_initiate_calls = 0
        self.agent_api.start_loading_finalize_calls = 0
        self.agent_api.stop_loading_finalize_calls = 0
        self.agent_api.start_unloading_calls = 0

    @allure.step
    def setup_walle_host_status_ready(self):
        self.walle_api.set_ready_response()

    @allure.step
    def setup_walle_host_status_not_ready(self):
        self.walle_api.set_dead_response()

    @allure.step
    def setup_walle_host_status_not_ready_yet(self):
        self.walle_api.set_switching_response()

    @allure.step
    def create_walle_task(self, *hosts, action="reboot"):
        walle_id = "func-testing-{}".format(self.next_walle_id)

        self.internal_api.task_mapping = {
            walle_id: {
                "walle_id": walle_id,
                "walle_type": "manual",
                "walle_issuer": "func-test",
                "walle_action": action,
                "walle_hosts": hosts,
                "walle_comment": "some-comment",
                "walle_extra": {"k": "v"},
                "internal_status": fsm.States.MAKING_DECISION
            }
        }

        now = datetime.datetime.now()

        self.internal_api.audit_mapping = {
            walle_id: [
                {"timestamp": now.isoformat(), "source_state": fsm.States.INITIAL, "target_state": fsm.States.MAKING_DECISION, "success": True,
                 "subject": "x", "message": "z", "obj": None, "reason": None}
            ]
        }

        self.queue.put({"walle_id": walle_id})

        return walle_id

    @allure.step
    def create_walle_task_and_delete_before_handling(self, *hosts):
        walle_id = "func-testing-{}".format(self.next_walle_id)

        self.internal_api.task_mapping = {
            walle_id: {
                "walle_id": walle_id,
                "walle_type": "manual",
                "walle_issuer": "func-test",
                "walle_action": "reboot",
                "walle_hosts": hosts,
                "walle_comment": "some-comment",
                "walle_extra": {"k": "v"},
                "internal_status": fsm.States.WAIT_FOR_APPROVAL_DUTY_INTERVENTION_LOAD
            }
        }

        now = datetime.datetime.now()
        dts = [datetime.timedelta(seconds=s) for s in range(2)]

        self.internal_api.audit_mapping = {
            walle_id: [
                {"timestamp": (now + dts[0]).isoformat(), "source_state": fsm.States.INITIAL, "target_state": fsm.States.MAKING_DECISION, "success": True},
                {"timestamp": (now + dts[1]).isoformat(), "source_state": fsm.States.MAKING_DECISION, "target_state": fsm.States.WAIT_FOR_APPROVAL_DUTY_INTERVENTION_LOAD, "success": True},
            ]
        }

        self.queue.put({"walle_id": walle_id})

        return walle_id

    @allure.step
    def create_walle_task_in_past(self, *hosts):
        walle_id = "func-testing-{}".format(self.next_walle_id)

        self.internal_api.task_mapping = {
            walle_id: {
                "walle_id": walle_id,
                "walle_type": "manual",
                "walle_issuer": "func-test",
                "walle_action": "reboot",
                "walle_hosts": hosts,
                "walle_comment": "some-comment",
                "walle_extra": {"k": "v"},
                "internal_status": fsm.States.MAKING_DECISION
            }
        }

        now = datetime.datetime.now() - datetime.timedelta(weeks=1)

        self.internal_api.audit_mapping = {
            walle_id: [
                {"timestamp": now.isoformat(), "source_state": fsm.States.INITIAL, "target_state": fsm.States.MAKING_DECISION, "success": True,
                 "subject": "x", "message": "z", "obj": None, "reason": None}
            ]
        }

        self.queue.put({"walle_id": walle_id})

        return walle_id

    @allure.step
    def create_walle_task_invalid_action(self, *hosts, bypass=False):
        walle_id = "func-testing-{}".format(self.next_walle_id)

        self.internal_api.task_mapping = {
            walle_id: {
                "walle_id": walle_id,
                "walle_type": "manual",
                "walle_issuer": "func-test",
                "walle_action": "reboot",
                "walle_hosts": hosts,
                "walle_comment": "some-comment",
                "walle_extra": {"k": "v"},
                "internal_status": fsm.States.UNLOADING
            }
        }

        now = datetime.datetime.now()
        dts = [datetime.timedelta(seconds=s) for s in range(2)]

        self.internal_api.audit_mapping = {
            walle_id: [
                {"timestamp": (now + dts[0]).isoformat(), "source_state": fsm.States.INITIAL, "target_state": fsm.States.MAKING_DECISION, "success": True},
                {"timestamp": (now + dts[1]).isoformat(), "source_state": fsm.States.MAKING_DECISION, "target_state": fsm.States.UNLOADING, "success": True},
            ]
        }

        payload = {"walle_id": walle_id, "action": "xxx"}
        if bypass:
            payload["bypass"] = True

        self.queue.put(payload)

        return walle_id

    @allure.step
    def create_walle_task_load(self, *hosts, bypass=False):
        walle_id = "func-testing-{}".format(self.next_walle_id)

        self.internal_api.task_mapping = {
            walle_id: {
                "walle_id": walle_id,
                "walle_type": "manual",
                "walle_issuer": "func-test",
                "walle_action": "reboot",
                "walle_hosts": hosts,
                "walle_comment": "some-comment",
                "walle_extra": {"k": "v"},
                "internal_status": fsm.States.INITIATE_LOADING
            }
        }

        now = datetime.datetime.now()
        dts = [datetime.timedelta(seconds=s) for s in range(4)]

        self.internal_api.audit_mapping = {
            walle_id: [
                {"timestamp": (now + dts[0]).isoformat(), "source_state": fsm.States.INITIAL, "target_state": fsm.States.MAKING_DECISION, "success": True},
                {"timestamp": (now + dts[1]).isoformat(), "source_state": fsm.States.MAKING_DECISION, "target_state": fsm.States.WAIT_FOR_APPROVAL_DUTY_INTERVENTION, "success": True},
                {"timestamp": (now + dts[2]).isoformat(), "source_state": fsm.States.WAIT_FOR_APPROVAL_DUTY_INTERVENTION, "target_state": fsm.States.OK_WAIT_FOR_WALLE_DELETE, "success": True},
                {"timestamp": (now + dts[3]).isoformat(), "source_state": fsm.States.OK_WAIT_FOR_WALLE_DELETE, "target_state": fsm.States.INITIATE_LOADING, "success": True}
            ]
        }

        payload = {"walle_id": walle_id, "action": action.Action.INITIATE_LOADING}
        if bypass:
            payload["bypass"] = True

        self.queue.put(payload)

        return walle_id

    @allure.step
    def create_walle_task_load_wait(self, *hosts, bypass=False):
        walle_id = "func-testing-{}".format(self.next_walle_id)

        self.internal_api.task_mapping = {
            walle_id: {
                "walle_id": walle_id,
                "walle_type": "manual",
                "walle_issuer": "func-test",
                "walle_action": "reboot",
                "walle_hosts": hosts,
                "walle_comment": "some-comment",
                "walle_extra": {"k": "v"},
                "internal_status": fsm.States.WAIT_FOR_LOADING_COMPLETE
            }
        }

        now = datetime.datetime.now()
        dts = [datetime.timedelta(seconds=s) for s in range(5)]

        self.internal_api.audit_mapping = {
            walle_id: [
                {"timestamp": (now + dts[0]).isoformat(), "source_state": fsm.States.INITIAL, "target_state": fsm.States.MAKING_DECISION, "success": True},
                {"timestamp": (now + dts[1]).isoformat(), "source_state": fsm.States.MAKING_DECISION, "target_state": fsm.States.WAIT_FOR_APPROVAL_DUTY_INTERVENTION, "success": True},
                {"timestamp": (now + dts[2]).isoformat(), "source_state": fsm.States.WAIT_FOR_APPROVAL_DUTY_INTERVENTION, "target_state": fsm.States.OK_WAIT_FOR_WALLE_DELETE, "success": True},
                {"timestamp": (now + dts[3]).isoformat(), "source_state": fsm.States.OK_WAIT_FOR_WALLE_DELETE, "target_state": fsm.States.INITIATE_LOADING, "success": True},
                {"timestamp": (now + dts[4]).isoformat(), "source_state": fsm.States.INITIATE_LOADING, "target_state": fsm.States.WAIT_FOR_LOADING_COMPLETE, "success": True}
            ]
        }

        payload = {"walle_id": walle_id, "action": action.Action.WAIT_FOR_LOADING_COMPLETE}
        if bypass:
            payload["bypass"] = True

        self.queue.put(payload)

        return walle_id

    @allure.step
    def create_walle_task_load_finalize(self, *hosts, bypass=False):
        walle_id = "func-testing-{}".format(self.next_walle_id)

        self.internal_api.task_mapping = {
            walle_id: {
                "walle_id": walle_id,
                "walle_type": "manual",
                "walle_issuer": "func-test",
                "walle_action": "reboot",
                "walle_hosts": hosts,
                "walle_comment": "some-comment",
                "walle_extra": {"k": "v"},
                "internal_status": fsm.States.FINALIZE_LOADING
            }
        }

        now = datetime.datetime.now()
        dts = [datetime.timedelta(seconds=s) for s in range(6)]

        self.internal_api.audit_mapping = {
            walle_id: [
                {"timestamp": (now + dts[0]).isoformat(), "source_state": fsm.States.INITIAL, "target_state": fsm.States.MAKING_DECISION, "success": True},
                {"timestamp": (now + dts[1]).isoformat(), "source_state": fsm.States.MAKING_DECISION, "target_state": fsm.States.WAIT_FOR_APPROVAL_DUTY_INTERVENTION, "success": True},
                {"timestamp": (now + dts[2]).isoformat(), "source_state": fsm.States.WAIT_FOR_APPROVAL_DUTY_INTERVENTION, "target_state": fsm.States.OK_WAIT_FOR_WALLE_DELETE, "success": True},
                {"timestamp": (now + dts[3]).isoformat(), "source_state": fsm.States.OK_WAIT_FOR_WALLE_DELETE, "target_state": fsm.States.INITIATE_LOADING, "success": True},
                {"timestamp": (now + dts[4]).isoformat(), "source_state": fsm.States.INITIATE_LOADING, "target_state": fsm.States.WAIT_FOR_LOADING_COMPLETE, "success": True},
                {"timestamp": (now + dts[5]).isoformat(), "source_state": fsm.States.WAIT_FOR_LOADING_COMPLETE, "target_state": fsm.States.FINALIZE_LOADING, "success": True}
            ]
        }

        payload = {"walle_id": walle_id, "action": action.Action.FINALIZE_LOADING}
        if bypass:
            payload["bypass"] = True

        self.queue.put(payload)

        return walle_id

    @allure.step
    def create_walle_task_load_in_past(self, *hosts, bypass=False):
        walle_id = "func-testing-{}".format(self.next_walle_id)

        self.internal_api.task_mapping = {
            walle_id: {
                "walle_id": walle_id,
                "walle_type": "manual",
                "walle_issuer": "func-test",
                "walle_action": "reboot",
                "walle_hosts": hosts,
                "walle_comment": "some-comment",
                "walle_extra": {"k": "v"},
                "internal_status": fsm.States.INITIATE_LOADING
            }
        }

        now = datetime.datetime.now() - datetime.timedelta(weeks=1)
        dts = [datetime.timedelta(seconds=s) for s in range(4)]

        self.internal_api.audit_mapping = {
            walle_id: [
                {"timestamp": (now + dts[0]).isoformat(), "source_state": fsm.States.INITIAL, "target_state": fsm.States.MAKING_DECISION, "success": True},
                {"timestamp": (now + dts[1]).isoformat(), "source_state": fsm.States.MAKING_DECISION, "target_state": fsm.States.WAIT_FOR_APPROVAL_DUTY_INTERVENTION, "success": True},
                {"timestamp": (now + dts[2]).isoformat(), "source_state": fsm.States.WAIT_FOR_APPROVAL_DUTY_INTERVENTION, "target_state": fsm.States.OK_WAIT_FOR_WALLE_DELETE, "success": True},
                {"timestamp": (now + dts[3]).isoformat(), "source_state": fsm.States.OK_WAIT_FOR_WALLE_DELETE, "target_state": fsm.States.INITIATE_LOADING, "success": True}
            ]
        }

        payload = {"walle_id": walle_id, "action": action.Action.INITIATE_LOADING}
        if bypass:
            payload["bypass"] = True

        self.queue.put(payload)

        return walle_id

    @allure.step
    def create_walle_task_unload(self, *hosts, bypass=False):
        walle_id = "func-testing-{}".format(self.next_walle_id)

        self.internal_api.task_mapping = {
            walle_id: {
                "walle_id": walle_id,
                "walle_type": "manual",
                "walle_issuer": "func-test",
                "walle_action": "reboot",
                "walle_hosts": hosts,
                "walle_comment": "some-comment",
                "walle_extra": {"k": "v"},
                "internal_status": fsm.States.UNLOADING
            }
        }

        now = datetime.datetime.now()
        dts = [datetime.timedelta(seconds=s) for s in range(2)]

        self.internal_api.audit_mapping = {
            walle_id: [
                {"timestamp": (now + dts[0]).isoformat(), "source_state": fsm.States.INITIAL, "target_state": fsm.States.MAKING_DECISION, "success": True},
                {"timestamp": (now + dts[1]).isoformat(), "source_state": fsm.States.MAKING_DECISION, "target_state": fsm.States.UNLOADING, "success": True},
            ]
        }

        payload = {"walle_id": walle_id, "action": action.Action.UNLOAD}
        if bypass:
            payload["bypass"] = True

        self.queue.put(payload)

        return walle_id

    @allure.step
    def create_walle_task_and_delete_before_unload(self, *hosts):
        walle_id = "func-testing-{}".format(self.next_walle_id)

        self.internal_api.task_mapping = {
            walle_id: {
                "walle_id": walle_id,
                "walle_type": "manual",
                "walle_issuer": "func-test",
                "walle_action": "reboot",
                "walle_hosts": hosts,
                "walle_comment": "some-comment",
                "walle_extra": {"k": "v"},
                "internal_status": fsm.States.WAIT_FOR_APPROVAL_DUTY_INTERVENTION_LOAD
            }
        }

        now = datetime.datetime.now()
        dts = [datetime.timedelta(seconds=s) for s in range(3)]

        self.internal_api.audit_mapping = {
            walle_id: [
                {"timestamp": (now + dts[0]).isoformat(), "source_state": fsm.States.INITIAL, "target_state": fsm.States.MAKING_DECISION, "success": True},
                {"timestamp": (now + dts[1]).isoformat(), "source_state": fsm.States.MAKING_DECISION, "target_state": fsm.States.UNLOADING, "success": True},
                {"timestamp": (now + dts[2]).isoformat(), "source_state": fsm.States.UNLOADING, "target_state": fsm.States.WAIT_FOR_APPROVAL_DUTY_INTERVENTION_LOAD, "success": True},
            ]
        }

        payload = {"walle_id": walle_id, "action": action.Action.UNLOAD}

        self.queue.put(payload)

        return walle_id

    @allure.step
    def create_walle_task_unload_in_past(self, *hosts, bypass=False):
        walle_id = "func-testing-{}".format(self.next_walle_id)

        self.internal_api.task_mapping = {
            walle_id: {
                "walle_id": walle_id,
                "walle_type": "manual",
                "walle_issuer": "func-test",
                "walle_action": "reboot",
                "walle_hosts": hosts,
                "walle_comment": "some-comment",
                "walle_extra": {"k": "v"},
                "internal_status": fsm.States.UNLOADING
            }
        }

        now = datetime.datetime.now() - datetime.timedelta(weeks=1)
        dts = [datetime.timedelta(seconds=s) for s in range(2)]

        self.internal_api.audit_mapping = {
            walle_id: [
                {"timestamp": (now + dts[0]).isoformat(), "source_state": fsm.States.INITIAL, "target_state": fsm.States.MAKING_DECISION, "success": True},
                {"timestamp": (now + dts[1]).isoformat(), "source_state": fsm.States.MAKING_DECISION, "target_state": fsm.States.UNLOADING, "success": True},
            ]
        }

        payload = {"walle_id": walle_id, "action": action.Action.UNLOAD}
        if bypass:
            payload["bypass"] = True

        self.queue.put(payload)

        return walle_id

    @allure.step
    def create_walle_task_not_making_decision(self, *hosts):
        walle_id = "func-testing-{}".format(self.next_walle_id)

        self.internal_api.task_mapping = {
            walle_id: {
                "walle_id": walle_id,
                "walle_type": "manual",
                "walle_issuer": "func-test",
                "walle_action": "reboot",
                "walle_hosts": hosts,
                "walle_comment": "some-comment",
                "walle_extra": {"k": "v"},
                "internal_status": fsm.States.WAIT_FOR_APPROVAL_DUTY_INTERVENTION
            }
        }

        now = datetime.datetime.now()
        dts = [datetime.timedelta(seconds=s) for s in range(2)]

        self.internal_api.audit_mapping = {
            walle_id: [
                {"timestamp": (now + dts[0]).isoformat(), "source_state": fsm.States.INITIAL, "target_state": fsm.States.MAKING_DECISION, "success": True},
                {"timestamp": (now + dts[1]).isoformat(), "source_state": fsm.States.MAKING_DECISION, "target_state": fsm.States.WAIT_FOR_APPROVAL_DUTY_INTERVENTION, "success": True},
            ]
        }

        self.queue.put({"walle_id": walle_id})

        return walle_id

    @allure.step
    def create_walle_task_not_initiate_loading(self, *hosts):
        walle_id = "func-testing-{}".format(self.next_walle_id)

        self.internal_api.task_mapping = {
            walle_id: {
                "walle_id": walle_id,
                "walle_type": "manual",
                "walle_issuer": "func-test",
                "walle_action": "reboot",
                "walle_hosts": hosts,
                "walle_comment": "some-comment",
                "walle_extra": {"k": "v"},
                "internal_status": fsm.States.WAIT_FOR_APPROVAL_DUTY_INTERVENTION_LOAD
            }
        }

        now = datetime.datetime.now()
        dts = [datetime.timedelta(seconds=s) for s in range(6)]

        self.internal_api.audit_mapping = {
            walle_id: [
                {"timestamp": (now + dts[0]).isoformat(), "source_state": fsm.States.INITIAL, "target_state": fsm.States.MAKING_DECISION, "success": True},
                {"timestamp": (now + dts[1]).isoformat(), "source_state": fsm.States.MAKING_DECISION, "target_state": fsm.States.WAIT_FOR_APPROVAL_UNLOAD, "success": True},
                {"timestamp": (now + dts[2]).isoformat(), "source_state": fsm.States.WAIT_FOR_APPROVAL_UNLOAD, "target_state": fsm.States.UNLOADING, "success": True},
                {"timestamp": (now + dts[3]).isoformat(), "source_state": fsm.States.UNLOADING, "target_state": fsm.States.OK_WAIT_FOR_WALLE_DELETE, "success": True},
                {"timestamp": (now + dts[4]).isoformat(), "source_state": fsm.States.OK_WAIT_FOR_WALLE_DELETE, "target_state": fsm.States.INITIATE_LOADING, "success": True},
                {"timestamp": (now + dts[5]).isoformat(), "source_state": fsm.States.INITIATE_LOADING, "target_state": fsm.States.WAIT_FOR_APPROVAL_DUTY_INTERVENTION_LOAD, "success": True},
            ]
        }

        self.queue.put({"walle_id": walle_id, "action": action.Action.UNLOAD})

        return walle_id

    @allure.step
    def create_walle_task_not_wait_for_loading_complete(self, *hosts):
        walle_id = "func-testing-{}".format(self.next_walle_id)

        self.internal_api.task_mapping = {
            walle_id: {
                "walle_id": walle_id,
                "walle_type": "manual",
                "walle_issuer": "func-test",
                "walle_action": "reboot",
                "walle_hosts": hosts,
                "walle_comment": "some-comment",
                "walle_extra": {"k": "v"},
                "internal_status": fsm.States.WAIT_FOR_APPROVAL_DUTY_INTERVENTION_LOAD
            }
        }

        now = datetime.datetime.now()
        dts = [datetime.timedelta(seconds=s) for s in range(7)]

        self.internal_api.audit_mapping = {
            walle_id: [
                {"timestamp": (now + dts[0]).isoformat(), "source_state": fsm.States.INITIAL, "target_state": fsm.States.MAKING_DECISION, "success": True},
                {"timestamp": (now + dts[1]).isoformat(), "source_state": fsm.States.MAKING_DECISION, "target_state": fsm.States.WAIT_FOR_APPROVAL_UNLOAD, "success": True},
                {"timestamp": (now + dts[2]).isoformat(), "source_state": fsm.States.WAIT_FOR_APPROVAL_UNLOAD, "target_state": fsm.States.UNLOADING, "success": True},
                {"timestamp": (now + dts[3]).isoformat(), "source_state": fsm.States.UNLOADING, "target_state": fsm.States.OK_WAIT_FOR_WALLE_DELETE, "success": True},
                {"timestamp": (now + dts[4]).isoformat(), "source_state": fsm.States.OK_WAIT_FOR_WALLE_DELETE, "target_state": fsm.States.INITIATE_LOADING, "success": True},
                {"timestamp": (now + dts[5]).isoformat(), "source_state": fsm.States.INITIATE_LOADING, "target_state": fsm.States.WAIT_FOR_LOADING_COMPLETE, "success": True},
                {"timestamp": (now + dts[6]).isoformat(), "source_state": fsm.States.WAIT_FOR_LOADING_COMPLETE, "target_state": fsm.States.WAIT_FOR_APPROVAL_DUTY_INTERVENTION_LOAD, "success": True},
            ]
        }

        self.queue.put({"walle_id": walle_id, "action": action.Action.WAIT_FOR_LOADING_COMPLETE})

        return walle_id

    @allure.step
    def create_walle_task_not_finalize_loading(self, *hosts):
        walle_id = "func-testing-{}".format(self.next_walle_id)

        self.internal_api.task_mapping = {
            walle_id: {
                "walle_id": walle_id,
                "walle_type": "manual",
                "walle_issuer": "func-test",
                "walle_action": "reboot",
                "walle_hosts": hosts,
                "walle_comment": "some-comment",
                "walle_extra": {"k": "v"},
                "internal_status": fsm.States.WAIT_FOR_APPROVAL_DUTY_INTERVENTION_LOAD
            }
        }

        now = datetime.datetime.now()
        dts = [datetime.timedelta(seconds=s) for s in range(8)]

        self.internal_api.audit_mapping = {
            walle_id: [
                {"timestamp": (now + dts[0]).isoformat(), "source_state": fsm.States.INITIAL, "target_state": fsm.States.MAKING_DECISION, "success": True},
                {"timestamp": (now + dts[1]).isoformat(), "source_state": fsm.States.MAKING_DECISION, "target_state": fsm.States.WAIT_FOR_APPROVAL_UNLOAD, "success": True},
                {"timestamp": (now + dts[2]).isoformat(), "source_state": fsm.States.WAIT_FOR_APPROVAL_UNLOAD, "target_state": fsm.States.UNLOADING, "success": True},
                {"timestamp": (now + dts[3]).isoformat(), "source_state": fsm.States.UNLOADING, "target_state": fsm.States.OK_WAIT_FOR_WALLE_DELETE, "success": True},
                {"timestamp": (now + dts[4]).isoformat(), "source_state": fsm.States.OK_WAIT_FOR_WALLE_DELETE, "target_state": fsm.States.INITIATE_LOADING, "success": True},
                {"timestamp": (now + dts[5]).isoformat(), "source_state": fsm.States.INITIATE_LOADING, "target_state": fsm.States.WAIT_FOR_LOADING_COMPLETE, "success": True},
                {"timestamp": (now + dts[6]).isoformat(), "source_state": fsm.States.WAIT_FOR_LOADING_COMPLETE, "target_state": fsm.States.FINALIZE_LOADING, "success": True},
                {"timestamp": (now + dts[7]).isoformat(), "source_state": fsm.States.WAIT_FOR_LOADING_COMPLETE, "target_state": fsm.States.WAIT_FOR_APPROVAL_DUTY_INTERVENTION_LOAD, "success": True},
            ]
        }

        self.queue.put({"walle_id": walle_id, "action": action.Action.FINALIZE_LOADING})

        return walle_id

    @allure.step
    def create_walle_task_not_unloading(self, *hosts):
        walle_id = "func-testing-{}".format(self.next_walle_id)

        self.internal_api.task_mapping = {
            walle_id: {
                "walle_id": walle_id,
                "walle_type": "manual",
                "walle_issuer": "func-test",
                "walle_action": "reboot",
                "walle_hosts": hosts,
                "walle_comment": "some-comment",
                "walle_extra": {"k": "v"},
                "internal_status": fsm.States.WAIT_FOR_APPROVAL_DUTY_INTERVENTION
            }
        }

        now = datetime.datetime.now()
        dts = [datetime.timedelta(seconds=s) for s in range(4)]

        self.internal_api.audit_mapping = {
            walle_id: [
                {"timestamp": (now + dts[0]).isoformat(), "source_state": fsm.States.INITIAL, "target_state": fsm.States.MAKING_DECISION, "success": True},
                {"timestamp": (now + dts[1]).isoformat(), "source_state": fsm.States.MAKING_DECISION, "target_state": fsm.States.WAIT_FOR_APPROVAL_UNLOAD, "success": True},
                {"timestamp": (now + dts[2]).isoformat(), "source_state": fsm.States.WAIT_FOR_APPROVAL_UNLOAD, "target_state": fsm.States.UNLOADING, "success": True},
                {"timestamp": (now + dts[3]).isoformat(), "source_state": fsm.States.UNLOADING, "target_state": fsm.States.WAIT_FOR_APPROVAL_DUTY_INTERVENTION, "success": True},
            ]
        }

        self.queue.put({"walle_id": walle_id, "action": action.Action.UNLOAD})

        return walle_id


class OutputSteps:
    def __init__(self, monkeypatch, queue, internal_api_mock: MockInternalApi, cluster_api_mock: MockClusterApi, agent_api_mock: MockAgentApi, walle_api_mock: MockWalleApi):
        self.monkeypatch = monkeypatch
        self.queue = queue
        self.internal_api = internal_api_mock
        self.cluster_api = cluster_api_mock
        self.agent_api = agent_api_mock
        self.walle_api = walle_api_mock

    @allure.step
    def setup_internal_api_mock(self):
        self.monkeypatch.setattr(lib_client, "InternalApi", self.internal_api)

    @allure.step
    def setup_cluster_api_mock(self):
        self.monkeypatch.setattr(cluster, "ClusterAPI", self.cluster_api)

    @allure.step
    def setup_agent_api_mock(self):
        self.monkeypatch.setattr(agent_client, "AgentApi", self.agent_api)

    @allure.step
    def setup_walle_mock(self):
        self.monkeypatch.setattr(walle_api.client, "WalleClient", self.walle_api)

    def wait_until_finish_processing(self, walle_id):
        self.wait_until_audit(walle_id, message="Finish processing")

    def wait_until_audit(self, walle_id, source_state=None, target_state=None, message=None, reason=None, success=None):
        def predicate():
            def mapper(a):
                value = True
                value &= walle_id is None or a.get("walle_id") == walle_id
                value &= source_state is None or a.get("source_state") == source_state
                value &= target_state is None or a.get("target_state") == target_state
                value &= message is None or a.get("message") == message
                value &= reason is None or a.get("reason") == reason
                value &= success is None or a.get("success") == success
                return value

            with allure.step("Check Audit Records"):
                return any(map(mapper, self.internal_api.recorded_audits))

        with allure.step(f"wait audit {source_state} -> {target_state} {success} reason: {reason} message: {message}"):
            wait.wait_for(predicate)

    def wait_until_transition(self, walle_id, source_state, target_state):
        def predicate():
            def mapper(a):
                value = True
                value = value and a["walle_id"] == walle_id
                value = value and a["source_state"] == source_state
                value = value and a["target_state"] == target_state

                return value

            with allure.step("Check Transitions"):
                return any(map(mapper, self.internal_api.recorded_transitions))

        with allure.step(f"wait transition {source_state} -> {target_state}"):
            wait.wait_for(predicate)

    @allure.step
    def wait_until_unloading_started(self, n_times=1):
        wait.wait_for(lambda: self.agent_api.start_unloading_calls >= n_times)

    @allure.step
    def wait_until_loading_started(self, n_times=1):
        wait.wait_for(lambda: self.agent_api.start_loading_initiate_calls >= n_times)

    @allure.step
    def dump_audit(self):
        allure.attach("Recorded audit", pprint.pformat(self.internal_api.recorded_audits))

    @allure.step
    def get_queue_items(self):
        items = self.queue.list()
        allure.attach("Queue", "\n".join([pprint.pformat(i) for i in items]))
        return items

    @allure.step
    def wait_until_queue_task_processed(self, walle_id):
        def predicate():
            return all([item["payload"]["walle_id"] != walle_id for item in self.get_queue_items()])

        wait.wait_for(predicate)


class Assert:
    def __init__(self, verification_steps: VerificationSteps, queue):
        self.verification = verification_steps
        self.queue = queue

    @allure.step
    def get_queue_items(self):
        items = self.queue.list()
        allure.attach("Queue", "\n".join([pprint.pformat(i) for i in items]))
        return items

    def task_is_not_processed(self, walle_id):
        self.verification.assert_that(f"задача {walle_id} не была обработана", self.get_queue_items(),
                                      has_item(has_entry("payload", has_entry("walle_id", equal_to(walle_id)))))
        self.verification.verify()

    def task_is_processed(self, walle_id):
        self.verification.assert_that(f"задача {walle_id} была обработана", self.get_queue_items(),
                                      not_(has_item(has_entry("payload", has_entry("walle_id", equal_to(walle_id))))))
        self.verification.verify()


class Steps:
    def __init__(self, config, input_steps: InputSteps, output_steps: OutputSteps, assert_that: Assert):
        self.config = config
        self.input = input_steps
        self.output = output_steps
        self.assert_that = assert_that

    def cleanup(self):
        self.output.dump_audit()
        self.input.clean_queue()
        self.input.clean_mocks()
