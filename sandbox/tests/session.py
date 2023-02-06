import py
import mock
import pytest
import logging

from sandbox.agentr import errors


@pytest.mark.agentr
class TestRegistry(object):
    logger = logging.getLogger("agentr")

    class MockJob(object):
        def __init__(self, logger):
            self.sid = 1
            self.connection = None
            self.log = logger

    def test__disconnect_service_session(self, tasks_registry):
        """Service session disconnect doesn't imply task #0 removal from database"""
        _CID = "09876asdsa"

        service_session = tasks_registry.service(_CID)
        assert service_session is not None

        tasks_registry.disconnected(_CID, self.logger)
        assert tasks_registry.account(service_session.id, 1233333, True) is not None

    def test__disconnect_task_session(self, tasks_registry):
        """Task session disconnect doesn't imply task removal from database"""
        _TOKEN = "12345678901234567890123456789000"
        _CID = "087ytyfvhgbnjkoiu"
        task_session = self.__create_task_session(tasks_registry, _TOKEN)

        tasks_registry.associate(task_session, _CID)
        tasks_registry.disconnected(_CID, self.logger)

        assert tasks_registry.account(task_session.id, 1234444, True) is not None

    def test__new_resource(self, tasks_registry):
        _TOKEN = "12345678901234567890123456789001"
        task_session = self.__create_task_session(tasks_registry, _TOKEN)
        res = {
            "attributes": {},
            "file_name": "bar",
            "id": 1234,
            "type": "string",
            "meta": {
                "file_name": "bar"
            }
        }
        tasks_registry.new_resource(task_session, res, py.path.local("/tmp/foo"), False, False)
        assert tasks_registry.check_resource(task_session.id, res["id"]) is not None

        # same file with another ID
        res["id"] += 1
        with pytest.raises(errors.InvalidResource):
            tasks_registry.new_resource(task_session, res, py.path.local("/tmp/foo"), False, False)

    def __create_task_session(self, registry, token):
        job = self.MockJob(self.logger)
        with mock.patch.object(registry, '_get_current_task_info', new_callable=lambda: self.__mock_task_info):
            with mock.patch.object(registry, '_register_task_log_resource', new_callable=lambda: self.__mock_empty):
                task_session = registry.add(job, token, 1, None, 0, 0, None)
        assert task_session is not None
        return task_session

    @staticmethod
    def __mock_empty(*args, **kwags):
        pass

    @staticmethod
    def __mock_task_info(*args, **kwargs):
        data = {
            "id": 10,
            "requirements":
                {
                    "resources": {
                        "count": 0
                    }
                }
        }
        dependencies = []
        return data, dependencies
