import mock

from sandbox.tasklet.sidecars.resource_manager.lib import model
from sandbox.tasklet.sidecars.resource_manager.lib import types
from sandbox.tasklet.sidecars.resource_manager.proto import resource_pb2
from sandbox.tasklet.sidecars.resource_manager.proto import resource_manager_api_pb2
from sandbox.tasklet.sidecars.resource_manager.run import service as rm_service
from sandbox.tasklet.sidecars.resource_manager.tests import common as common_tests


class TestResourceManagerServiceSb:
    def _resource_manager(self):
        resource_manager = rm_service.ResourceManagerAPI(runtime=types.Runtime.SANDBOX.value, iteration=1)
        return resource_manager

    def test_download_resource_sb(self, patch_handlers, agentr_session_class):
        resource_manager = self._resource_manager()
        resource_download_query1 = resource_manager_api_pb2.DownloadResourceRequest()
        resource_download_query1.id = 1
        resource_download_response1 = resource_manager.DownloadResource(resource_download_query1, mock.MagicMock())
        assert resource_download_response1.path == agentr_session_class.PATH_PREFIX + "/1"

        resource_download_query2 = resource_manager_api_pb2.DownloadResourceRequest()
        resource_download_query2.id = 2
        resource_download_response2 = resource_manager.DownloadResource(resource_download_query2, mock.MagicMock())
        assert resource_download_response2.path == agentr_session_class.PATH_PREFIX + "/2"

    def test_create_resource_sb(self, patch_handlers, agentr_session_class, proto_create_resource_request):
        resource_manager = self._resource_manager()
        proto_resource1 = resource_manager.CreateResource(proto_create_resource_request, mock.MagicMock()).resource

        agentr_mock = agentr_session_class()
        resource2 = agentr_mock.resource_complete(agentr_mock.resource_register(
            path=proto_create_resource_request.path, type=proto_create_resource_request.type,
            name=proto_create_resource_request.description, arch=proto_create_resource_request.arch,
            attrs=dict(proto_create_resource_request.attributes)
        )["id"])
        proto_resource2 = resource_pb2.Resource()
        model.ResourceProto.resource(proto_resource2, resource2)
        assert proto_resource1 == proto_resource2

    def test_get_resources(
        self, patch_handlers, full_resource1, full_resource2, empty_resource,
        full_proto_resource_query, owner_proto_resource_query
    ):
        resource_manager = self._resource_manager()

        proto_resource_array1 = resource_manager.GetResources(full_proto_resource_query, mock.MagicMock())
        assert len(proto_resource_array1.resources) == 1
        proto_original_resource1 = resource_pb2.Resource()
        model.ResourceProto.resource(proto_original_resource1, full_resource1)
        assert proto_resource_array1.resources[0] == proto_original_resource1

        proto_resource_array2 = resource_manager.GetResources(owner_proto_resource_query, mock.MagicMock())
        assert len(proto_resource_array2.resources) == 2
        proto_original_resource2 = resource_pb2.Resource()
        model.ResourceProto.resource(proto_original_resource2, empty_resource)
        assert proto_resource_array2.resources[0] == proto_original_resource2
        assert proto_resource_array2.resources[1] == proto_original_resource1


class TestResourceManagerServiceYt:
    def _resource_manager(self):
        resource_manager = rm_service.ResourceManagerAPI(runtime=types.Runtime.YT.value)
        return resource_manager

    def test_download_resource_yt(self, patch_handlers, sample_file, full_resource1_with_mds):
        resource_manager = self._resource_manager()

        filename, _, filedata = sample_file

        resource_download_query = resource_manager_api_pb2.DownloadResourceRequest()
        resource_download_query.id = 1
        resource_download_response = resource_manager.DownloadResource(resource_download_query, mock.MagicMock())
        downloaded_filename = resource_download_response.path
        assert downloaded_filename.endswith(filename)
        with open(downloaded_filename, "rb") as f:
            downloaded_filedata = f.read()
            assert downloaded_filedata == filedata, "{}\n{}".format(downloaded_filedata, filedata)


class TestResourceManagerServiceTest:
    def _resource_manager(self):
        resource_manager = rm_service.ResourceManagerAPI(runtime=types.Runtime.TEST.value)
        return resource_manager

    def test_resource_storage(self, sample_file, sample_dir, proto_create_resource_request, clear_storage):
        resource_manager = self._resource_manager()
        common_tests.resource_storage_test_impl(resource_manager, sample_file, sample_dir, proto_create_resource_request)
