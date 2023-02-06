import logging
import pytest

from sandbox import common

from sandbox.yasandbox.manager import tests as manager_tests
from sandbox.tests.common import base as tests_base


logger = logging.getLogger(__name__)


RESOURCE_KEYS = [
    'dummy', 'name', 'task_id', 'skynet_id', 'timestamp', 'arch', 'id',
    'size', 'file_md5', 'url', 'host', 'attrs', 'file_name', 'state'
]


class TestXmlrpcBase:
    default_resource_fields = {
        'resource_desc': 'xmlrpc test resource',
        'resource_type': 'TEST_TASK_RESOURCE',
        'resource_filename': 'xmlrpc_resource',
    }

    default_task_fields = {
        'owner': tests_base.api_session_login(),
        'type_name': 'UNIT_TEST',
        'descr': 'Test description',
    }

    def create_task(self, task_manager, owner=None, author=None, parameters=None):
        return manager_tests._create_task(
            task_manager, owner=owner, author=author, arch='any', parameters=parameters)

    def create_resource(self, task_manager, parameters=None, mark_ready=True, task=None):
        fields = self.default_resource_fields.copy()
        if parameters:
            fields.update(parameters)
        return manager_tests._create_resource(
            task_manager, fields, mark_ready, task=task)

    def create_real_resource(self, task_manager, parameters=None, mark_ready=True, task=None):
        fields = self.default_resource_fields.copy()
        if parameters:
            fields.update(parameters)
        return manager_tests._create_real_resource(
            task_manager, fields, mark_ready, task)

    def compare_resources_dicts(self, resource_dict1, resource_dict2, strict=False):
        problem_fields = {}
        for resource_field in RESOURCE_KEYS:
            if not resource_dict1[resource_field] == resource_dict2[resource_field]:
                if not strict:
                    if resource_field == 'timestamp':
                        if round(resource_dict1[resource_field]) == round(resource_dict2[resource_field]):
                            continue
                problem_fields[resource_field] = (resource_dict1[resource_field], resource_dict2[resource_field])
        return problem_fields


class TestROMode(TestXmlrpcBase):
    @pytest.mark.usefixtures("server")
    def test__ro(self, task_manager, settings_controller, api_session, api_session_login):
        task = self.create_task(task_manager, owner=api_session_login)
        settings_controller.set_mode(settings_controller.OperationMode.READ_ONLY)
        api_session.total_wait = 1
        pytest.raises(common.proxy.ReliableServerProxy.TimeoutExceeded, api_session.cancel_task, task.id)
        settings_controller.set_mode(settings_controller.OperationMode.NORMAL)
        api_session.total_wait = None
        api_session.cancel_task(task.id)
