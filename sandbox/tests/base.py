import mock

import sandbox.common.types.resource as ctr

from sandbox.tasklet.sidecars.resource_manager.handlers import base as base_handler


class TestBaseHandler:
    def test_get_resources(
        self, patch_handlers, api_session_class, agentr_session_class,
        full_resource1, full_resource_query, owner_resource_query
    ):
        resource_handler = base_handler.BaseHandler("TEST_TOKEN", mock.MagicMock())

        resource_list1 = resource_handler.get_resources(**full_resource_query)
        assert len(resource_list1) == 1
        assert resource_list1[0] == full_resource1
        assert len(resource_handler.api_client.audit) == 1
        path1, query1 = resource_handler.api_client.audit[-1]
        assert path1 == "/resource"
        assert query1 == {
            "id": [1, 3],
            "type": "TEST_TASK_2_RESOURCE",
            "state": ctr.State.READY,
            "owner": "SANDBOX",
            "task_id": [1, 2],
            "any_attr": True,
            "attributes": {
                "ttl": "14",
                "released": "prestable"
            },
            "limit": 1,
            "order": ["-id"]
        }
