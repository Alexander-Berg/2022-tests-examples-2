import json
import pytest

from sandbox import common
import sandbox.common.types.resource as ctr
from sandbox.yasandbox.database import mapping
from sandbox.yasandbox.manager.tests import _create_task
import sandbox.yasandbox.services.update_sandbox_resources

from sandbox.sandboxsdk import environments as env


@pytest.fixture()
def update_sandbox_resources(server):
    return sandbox.yasandbox.services.update_sandbox_resources.UpdateSandboxResources(
        stopping=lambda: False, logger=None, rwlock=None
    )


def create_resource(task_id, resource_type, attributes):
    return mapping.Resource(
        type=resource_type,
        name="test_resource",
        state=ctr.State.READY,
        path="test_path",
        task_id=task_id,
        owner="guest",
        arch="any",
        time=mapping.Resource.Time(),
        attributes=[mapping.Resource.Attribute(key=k, value=v) for k, v in attributes.iteritems()]
    ).save()


class TestUpdateSandboxResources(object):
    def test__env_resources(self, update_sandbox_resources, task_manager):
        task = _create_task(task_manager)
        r_svn = create_resource(
            task.id,
            env.SvnEnvironment.resource_type,
            {
                "platform": "lucid,precise,trusty",
                "version": "1.0",
            }
        )
        r_gcc = create_resource(
            task.id,
            env.GCCEnvironment.resource_type,
            {
                "platform": "trusty",  # binary compatible with xenial
                "version": "1.0",
                "released": "stable",
            }
        )

        r_node_1 = create_resource(
            task.id,
            env.NodeJS.resource_type,
            {
                "platform": "precise",
                "version": "1.0",
                "released": "stable",
            }
        )

        r_node_2 = create_resource(
            task.id,
            env.NodeJS.resource_type,
            {
                "platform": "precise",
                "version": "1.1",
            }
        )

        update_sandbox_resources.update_env_resources()
        cache = json.loads(update_sandbox_resources.model.context["cache"])
        platform = common.platform.get_platform_alias
        assert cache[env.SvnEnvironment.resource_type][platform("lucid")]["1.0"] == r_svn.id
        assert cache[env.SvnEnvironment.resource_type][platform("precise")]["1.0"] == r_svn.id
        assert cache[env.SvnEnvironment.resource_type][platform("trusty")]["1.0"] == r_svn.id

        assert cache[env.GCCEnvironment.resource_type][platform("trusty")]["1.0"] == r_gcc.id
        assert cache[env.GCCEnvironment.resource_type][platform("xenial")]["1.0"] == r_gcc.id

        assert cache[env.NodeJS.resource_type][platform("precise")][""] == r_node_1.id
        assert cache[env.NodeJS.resource_type][platform("precise")]["1.0"] == r_node_1.id
        assert cache[env.NodeJS.resource_type][platform("precise")]["1.1"] == r_node_2.id

        for res in [r_svn, r_gcc, r_node_1, r_node_2]:
            res.delete()
