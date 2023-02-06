from sandbox.tasklet.sidecars.resource_manager.lib import model
from sandbox.tasklet.sidecars.resource_manager.proto import resource_pb2
from sandbox.tasklet.sidecars.resource_manager.proto import resource_manager_api_pb2


class TestResourceProto:
    def test_time(self):
        time1 = {
            "created": "2022-04-17T15:40:26.222Z",
            "accessed": "2022-04-17T15:41:26.222Z",
            "expires": "2022-04-17T15:42:26.222Z",
            "updated": "2022-04-17T15:43:26.222Z"
        }
        proto_time1 = resource_pb2.Time()
        model.ResourceProto.time(proto_time1, time1)
        for item in ("created", "accessed", "expires", "updated"):
            assert getattr(proto_time1, item + "_time").ToJsonString() == time1[item]

        time2 = {
            "created": "2022-04-17T15:40:26.222Z",
            "accessed": "2022-04-17T15:41:26.222Z",
            "expires": "2022-04-17T15:42:26.222Z",
        }
        proto_time2 = resource_pb2.Time()
        model.ResourceProto.time(proto_time2, time2)
        for item in ("created", "accessed", "expires"):
            assert getattr(proto_time1, item + "_time").ToJsonString() == time1[item]

        time3 = None
        proto_time3 = resource_pb2.Time()
        model.ResourceProto.time(proto_time3, time3)
        common_time = proto_time3.created_time
        for item in ("created", "accessed", "expires", "updated"):
            assert getattr(proto_time3, item + "_time") == common_time

        time4 = {
            "created": None,
            "accessed": None,
            "expires": None,
            "updated": None
        }
        proto_time4 = resource_pb2.Time()
        model.ResourceProto.time(proto_time4, time4)
        common_time = proto_time3.created_time
        for item in ("created", "accessed", "expires", "updated"):
            assert getattr(proto_time3, item + "_time") == common_time

    def test_mds(self):
        mds1 = {
            "key": "mds_key",
            "namespace": "mds_namespace",
            "url": "http://kek/mds_namespace/mds_key"
        }
        proto_mds1 = resource_pb2.Mds()
        model.ResourceProto.mds(proto_mds1, mds1)
        for item in ("key", "namespace", "url"):
            assert mds1[item] == getattr(proto_mds1, item)

        mds2 = None
        proto_mds2 = resource_pb2.Mds()
        model.ResourceProto.mds(proto_mds2, mds2)
        for item in ("key", "namespace", "url"):
            assert getattr(proto_mds2, item) == ""

        mds3 = {
            "key": None,
            "namespace": None,
            "url": None
        }
        proto_mds3 = resource_pb2.Mds()
        model.ResourceProto.mds(proto_mds3, mds3)
        for item in ("key", "namespace", "url"):
            assert getattr(proto_mds3, item) == ""

    def test_resource(self, full_resource1, empty_resource):
        resource1 = full_resource1
        proto_resource1 = resource_pb2.Resource()
        model.ResourceProto.resource(proto_resource1, resource1)

        def compare1(proto_resource, resource):
            for item in (
                "id", "type", "arch", "state", "owner", "description", "size", "md5", "skynet_id",
                "multifile", "executable"
            ):
                assert getattr(proto_resource, item) == resource[item]
            assert proto_resource.filename == resource["file_name"]
            assert resource["task"]["id"] == proto_resource.task
            for item in ("created", "accessed", "expires", "updated"):
                assert getattr(proto_resource.time, item + "_time").ToJsonString() == resource["time"][item]
            assert dict(proto_resource.attributes) == resource["attributes"]
            for item in ("key", "namespace", "url"):
                assert getattr(proto_resource.mds, item) == resource["mds"][item]
        compare1(proto_resource1, resource1)

        resource2 = empty_resource
        proto_resource2 = resource_pb2.Resource()
        model.ResourceProto.resource(proto_resource2, resource2)

        def compare2(proto_resource, resource):
            for item in (
                "id", "type", "arch", "state", "owner", "description", "size",
            ):
                assert getattr(proto_resource, item) == resource[item]
            assert proto_resource.filename == resource["file_name"]
            assert proto_resource.task == resource["task"]["id"]
            for item in ("md5", "skynet_id"):
                assert getattr(proto_resource, item) == ""
            for item in ("multifile", "executable"):
                assert not getattr(proto_resource, item)
            proto_item = proto_resource.time.created_time
            for item in ("created", "accessed", "expires", "updated"):
                assert getattr(proto_resource.time, item + "_time") == proto_item
            assert len(proto_resource.attributes) == 0
            for item in ("key", "namespace", "url"):
                assert getattr(proto_resource.mds, item) == ""
        compare2(proto_resource2, resource2)

        resources_array1 = [resource1, resource2]
        get_resource_response1 = resource_manager_api_pb2.GetResourcesResponse()
        model.ResourceProto.resource_array(get_resource_response1, resources_array1)
        assert len(get_resource_response1.resources) == len(resources_array1)
        compare1(get_resource_response1.resources[0], resource1)
        compare2(get_resource_response1.resources[1], resource2)

        resources_array2 = []
        get_resource_response2 = resource_manager_api_pb2.GetResourcesResponse()
        model.ResourceProto.resource_array(get_resource_response2, resources_array2)
        assert len(get_resource_response2.resources) == 0


class TestResourceDict:
    def test_new_resource(self, proto_create_resource_request, new_resource):
        assert new_resource == model.ResourceDict.new_resource(proto_create_resource_request)

    def test_resource_query(
        self, full_proto_resource_query, full_resource_query, owner_proto_resource_query, owner_resource_query
    ):
        assert full_resource_query == model.ResourceDict.resource_query(full_proto_resource_query)
        assert owner_resource_query == model.ResourceDict.resource_query(owner_proto_resource_query)
