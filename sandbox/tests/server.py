import grpc

from sandbox.tasklet.sidecars.resource_manager.proto import resource_manager_api_pb2_grpc
from sandbox.tasklet.sidecars.resource_manager.tests import common as common_tests


class TestResourceManagerServer:
    def test_resource_storage_server(
        self, resource_manager, sample_file, sample_dir, proto_create_resource_request, clear_storage
    ):
        resource_manager = resource_manager_api_pb2_grpc.ResourceManagerAPIStub(grpc.insecure_channel(resource_manager))
        common_tests.resource_storage_test_impl(
            resource_manager, sample_file, sample_dir, proto_create_resource_request, mock_context=False
        )
