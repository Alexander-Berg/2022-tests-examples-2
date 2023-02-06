import mock

from sandbox.tasklet.sidecars.resource_manager.handlers import sb as sandbox_handler


class TestSandboxHandler:
    def test_download_resource(self, patch_handlers, api_session_class, agentr_session_class):
        resource_handler = sandbox_handler.SandboxHandler("TEST_TOKEN", 1, mock.MagicMock())
        path = resource_handler.download_resource(1)
        assert path == agentr_session_class.PATH_PREFIX + "/1"

    def test_create_resource(self, patch_handlers, api_session_class, agentr_session_class, new_resource):
        resource_handler = sandbox_handler.SandboxHandler("TEST_TOKEN", 1, mock.MagicMock())

        resource1 = resource_handler.create_resource(**new_resource)
        new_resource2 = {
            "type": new_resource["resource_type"],
            "arch": new_resource["arch"],
            "attrs": new_resource["attributes"],
            "path": new_resource["path"],
            "name": new_resource["description"]
        }
        agentr_mock = agentr_session_class()
        resource2 = agentr_mock.resource_complete(agentr_mock.resource_register(**new_resource2)["id"])
        assert resource1 == resource2
