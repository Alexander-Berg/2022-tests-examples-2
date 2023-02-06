import os
import mock

from sandbox.tasklet.sidecars.resource_manager.proto import resource_manager_api_pb2


def call_rpc_method(method, arg, mock_context):
    if mock_context:
        return method(arg, mock.MagicMock())
    else:
        return method(arg)


def resource_storage_test_impl(
    resource_manager, sample_file, sample_dir, proto_create_resource_request, mock_context=True
):
    sample_filename, sample_filepath, sample_filedata = sample_file
    sample_dir_path = sample_dir[0]
    proto_file_new_resource = resource_manager_api_pb2.CreateResourceRequest()
    proto_file_new_resource.CopyFrom(proto_create_resource_request)
    proto_file_new_resource.path = sample_filepath

    resource1 = call_rpc_method(resource_manager.CreateResource, proto_file_new_resource, mock_context).resource
    resource_download_query1 = resource_manager_api_pb2.DownloadResourceRequest()
    resource_download_query1.id = resource1.id
    resource_file_name1 = call_rpc_method(
        resource_manager.DownloadResource, resource_download_query1, mock_context
    ).path
    with open(resource_file_name1, "rb") as f:
        assert f.read() == sample_filedata

    proto_dir_new_resource = resource_manager_api_pb2.CreateResourceRequest()
    proto_dir_new_resource.CopyFrom(proto_create_resource_request)
    proto_dir_new_resource.path = sample_dir_path
    proto_dir_new_resource.owner = "TEST"
    resource2 = call_rpc_method(resource_manager.CreateResource, proto_dir_new_resource, mock_context).resource
    resource_download_query2 = resource_manager_api_pb2.DownloadResourceRequest()
    resource_download_query2.id = resource2.id
    resource_file_name2 = call_rpc_method(
        resource_manager.DownloadResource, resource_download_query2, mock_context
    ).path
    assert os.listdir(sample_dir_path) == os.listdir(resource_file_name2)

    resource_query1 = resource_manager_api_pb2.GetResourcesRequest()
    resource_query1.owner = "TEST"
    resource_array1 = call_rpc_method(
        resource_manager.GetResources, resource_query1, mock_context
    )
    assert len(resource_array1.resources) == 1
    assert resource_array1.resources[0] == resource2

    resource_query2 = resource_manager_api_pb2.GetResourcesRequest()
    resource_query2.attributes_query.attributes["attr1"] = "value1"
    resource_query2.attributes_query.any_attr = True
    resource_query2.order.append("id")
    resource_query2.limit = 2

    resource_array2 = call_rpc_method(
        resource_manager.GetResources, resource_query2, mock_context
    )
    assert len(resource_array2.resources) == 2
    response_resource1, response_resource2 = resource_array2.resources
    assert response_resource1 == resource1, "Different ids {} and {}".format(response_resource1.id, resource1.id)
    assert response_resource2 == resource2, "Different ids {} and {}".format(response_resource2.id, resource2.id)

    resource_query3 = resource_manager_api_pb2.GetResourcesRequest()
    resource_query3.CopyFrom(resource_query2)
    resource_query3.attributes_query.attributes["wrong_attr"] = "wrong_value"
    resource_query3.attributes_query.any_attr = False

    resource_array3 = call_rpc_method(
        resource_manager.GetResources, resource_query3, mock_context
    )
    assert len(resource_array3.resources) == 0
