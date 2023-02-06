import json
import pytest
import httplib

import sandbox.common.types.resource as ctr

from sandbox import sdk2
from sandbox.common import rest


class TestResource(object):
    @pytest.mark.usefixtures("sdk2_dispatched_rest_session")
    def test__find_resource(self, task_manager, resource_manager):
        from sandbox.yasandbox.manager import tests as manager_tests

        ids = [manager_tests._create_resource(task_manager).id for _ in xrange(15)]
        found = list(sdk2.Resource.find(id=ids).limit(len(ids)))
        assert found and len(found) == len(ids)

        with pytest.raises(rest.Client.HTTPError) as ex:
            list(sdk2.Resource.find().limit(10000))
        assert ex.value.status == httplib.BAD_REQUEST

        query = sdk2.Resource.find(id=ids)
        assert query.order(sdk2.Resource.id).first().id == sorted(ids)[0]
        assert query.offset(10).first().id == ids[10]  # default order is +id
        assert query.offset(10).order(-sdk2.Resource.id).first().id == ids[-11]
        with pytest.raises(AssertionError):
            sdk2.Resource.find().order(sdk2.Resource.arch).first()

        for type_ in ("SANDBOX_TASKS_ARCHIVE", "SANDBOX_ARCHIVE"):
            rid = manager_tests._create_resource(task_manager, {"resource_type": type_}).id
            query = sdk2.Resource.find(type=type_).limit(10)
            assert query() and query.count == 1 and query.first().id == rid

        data = {
            "resource_type": "OTHER_RESOURCE",
            "attrs": {
                "abc": "938",
                "def": 189
            }
        }
        res = manager_tests._create_resource(task_manager, data)
        for key, value in data["attrs"].items():
            for casted_value in map(lambda t: t(value), (str, int)):
                assert sdk2.Resource.find(attrs={key: casted_value}).limit(1).first().id == res.id, (key, casted_value)

        upd = {"ghi": json.dumps({1: 2}), "jkl": json.dumps([1, 5])}
        res.attrs.update(upd)
        resource_manager.update(res)
        for k, v in upd.items():
            assert sdk2.Resource.find(attrs={k: v}).limit(1).first().id == res.id

    @pytest.mark.usefixtures("sdk2_dispatched_rest_session")
    def test__reload_resource(self, task_manager, resource_manager):
        from sandbox.yasandbox.manager import tests as manager_tests

        resource = manager_tests._create_resource(task_manager)
        resource_id = resource.id

        resource_via_find = sdk2.Resource.find(id=resource_id).first()
        resource_by_id = sdk2.Resource[resource_id]
        assert resource_via_find is not resource
        assert resource_via_find is resource_by_id
        assert resource_by_id.state == ctr.State.READY

        attrs = {"qwer": "123", "asdf": "321"}
        resource.attrs.update(attrs)
        resource.state = ctr.State.DELETED
        resource_manager.update(resource)

        resource_by_id.reload()
        assert resource_by_id.state == ctr.State.DELETED
        assert resource_by_id.qwer == attrs["qwer"]
        assert resource_by_id.asdf == attrs["asdf"]

    def test__encode_resource(self):
        rc = sdk2.Resource["TEST_TASK_RESOURCE"]
        encoded_rc = rc.__getstate__()
        assert encoded_rc[0]["name"] == "TEST_TASK_RESOURCE"
        assert encoded_rc[0]["parent"] == "RESOURCE"
        assert encoded_rc[0]["on_restart"] == ctr.RestartPolicy.DELETE

    def test__decode_resource(self):
        decoded_resource = {
            "any_arch": True,
            "attributes": {
                "restart_policy": {"value": "DELETE"},
                "test_attr": {
                    "class_name": "Integer",
                    "default": None,
                    "description": "Test attribute",
                    "required": False
                },
                "test_required_attr": {
                    "class_name": "String",
                    "default": u"value",
                    "description": "Test required attribute",
                    "required": True
                }
            },
            "auto_backup": False,
            "calc_md5": True,
            "executable": False,
            "name": "TEST_KEK_RESOURCE",
            "on_restart": "RESET",
            "parent": "ABSTRACT_RESOURCE",
            "release_subscribers": ["sdfsdf", "ggggggggg", "testtesttesttest"],
            "releaseable": True,
            "releasers": ["guest", "test-robot-api-test", "robot-geosearch"],
            "share": True
        }

        child_resource = {
            "any_arch": True,
            "attributes": {
                "new_attr": {
                    "class_name": "Integer",
                    "default": None,
                    "description": "test3",
                    "required": True
                },
                "test_attr": {"value": 25}},
            "auto_backup": False,
            "calc_md5": True,
            "executable": False,
            "name": "CHILD_TEST_RESOURCE_CLASS",
            "on_restart": "RESET",
            "parent": "TEST_KEK_RESOURCE",
            "release_subscribers": ["sdfsdf", "ggggggggg", "testtesttesttest"],
            "releaseable": True,
            "releasers": ["guest", "test-robot-api-test", "robot-geosearch"],
            "share": True
        }

        rc = sdk2.Resource.__setstate__([decoded_resource])
        assert issubclass(rc, sdk2.resource.AbstractResource)
        assert rc.__name__ == decoded_resource["name"]
        assert issubclass(rc.__attrs__["test_attr"], sdk2.Attributes.Integer)
        assert rc.__attrs__["test_attr"].description == decoded_resource["attributes"]["test_attr"]["description"]
        assert issubclass(rc.__attrs__["test_required_attr"], sdk2.Attributes.String)
        attributes = decoded_resource["attributes"]
        assert rc.__attrs__["test_required_attr"].description == attributes["test_required_attr"]["description"]
        assert rc.__attrs__["test_required_attr"].required == attributes["test_required_attr"]["required"]
        assert rc.on_restart == attributes["restart_policy"]["value"]

        ch_rc = sdk2.Resource.__setstate__([child_resource])

        assert issubclass(ch_rc, rc)
        assert ch_rc.__name__ == child_resource["name"]
        assert ch_rc.__attrs__["test_required_attr"] is rc.__attrs__["test_required_attr"]
        assert ch_rc.__attrs__["test_attr"].default == child_resource["attributes"]["test_attr"]["value"]
        assert issubclass(ch_rc.__attrs__["new_attr"], sdk2.Attributes.Integer)
        assert ch_rc.__attrs__["new_attr"].description == child_resource["attributes"]["new_attr"]["description"]
        assert ch_rc.__attrs__["new_attr"].required
        assert ch_rc.on_restart == attributes["restart_policy"]["value"]
