import copy
import hashlib
import shutil
import time

import mock
import os
import pytest
import requests
import signal
import subprocess as sp

import grpc
import yatest.common

from sandbox.agentr import client as aclient
from sandbox.common import mds as common_mds
from sandbox.common import rest as common_rest
import sandbox.common.types.resource as ctr

from sandbox.tasklet.sidecars.resource_manager.lib import storage
from sandbox.tasklet.sidecars.resource_manager.lib import types
from sandbox.tasklet.sidecars.resource_manager.proto import resource_manager_api_pb2
from sandbox.tasklet.sidecars.resource_manager.proto import resource_manager_api_pb2_grpc


@pytest.fixture()
def patch_handlers(monkeypatch, api_session_class, agentr_session_class):
    monkeypatch.setattr(aclient, "Session", agentr_session_class)
    monkeypatch.setattr(common_rest, "Client", api_session_class)


@pytest.fixture()
def full_resource1():
    return {
        "id": 1,
        "state": ctr.State.READY,
        "task": {"id": 1},
        "time": {
            "created": "2022-04-17T15:40:26.222Z",
            "accessed": "2022-04-17T15:41:26.222Z",
            "expires": "2022-04-17T15:42:26.222Z",
            "updated": "2022-04-17T15:43:26.222Z"
        },
        "owner": "SANDBOX",
        "size": 192891829,
        "md5": "wirohvowirvn",
        "skynet_id": "rbtorrent:iwebowjkec24rv",
        "mds": {
            "key": "mds_key",
            "namespace": "mds_namespace",
            "url": "http://kek/mds_namespace/mds_key"
        },
        "multifile": False,
        "executable": False,
        "type": "TEST_TASK_2_RESOURCE",
        "arch": "linux",
        "description": "kek",
        "attributes": {
            "ttl": "14",
            "released": "stable"
        },
        "file_name": "timelog",
    }


@pytest.fixture()
def full_resource2():
    return {
        "id": 2,
        "state": ctr.State.READY,
        "task": {"id": 1},
        "time": {
            "created": "2022-04-17T15:40:26.222Z",
            "accessed": "2022-04-17T15:41:26.222Z",
            "expires": "2022-04-17T15:42:26.222Z",
            "updated": "2022-04-17T15:43:26.222Z"
        },
        "owner": "KEKBOX",
        "size": 0,
        "md5": "wirohvowirvn",
        "skynet_id": "rbtorrent:iwebowjkec24rv",
        "mds": {
            "key": "mds_key",
            "namespace": "mds_namespace",
            "url": "http://kek/mds_namespace/mds_key"
        },
        "multifile": False,
        "executable": False,
        "type": "KEK_RESOURCE",
        "arch": "linux",
        "description": "kek",
        "attributes": {
            "released": "prestable"
        },
        "file_name": "timelog",
    }


@pytest.fixture()
def empty_resource():
    return {
        "id": 3,
        "type": "TEST_TASK_2_RESOURCE",
        "arch": "linux",
        "state": ctr.State.READY,
        "owner": "SANDBOX",
        "task": {"id": 2},
        "description": "Some test resource",
        "time": None,
        "attributes": {},
        "size": 0,
        "md5": None,
        "skynet_id": None,
        "file_name": "lifelog",
        "mds": None,
        "multifile": None,
        "executable": None
    }


@pytest.fixture()
def api_session_class(full_resource1, full_resource2, empty_resource):
    class ApiClientMock(mock.MagicMock):
        RESOURCES = {resource["id"]: resource for resource in (full_resource1, full_resource2, empty_resource)}

        def __init__(self, *args, **kwargs) -> None:
            super(ApiClientMock, self).__init__(*args, **kwargs)
            self.path = kwargs.get("path", "")
            self.audit = kwargs.get("audit", [])

        def read(self, **kwargs) -> dict:
            self.audit.append((self.path, kwargs))
            return {
                "items": storage.Storage.filter_resources(self.RESOURCES, kwargs),
                "limit": kwargs["limit"],
                "offset": kwargs.get("offset", 0),
                "total": 0
            }

        def __getattr__(self, item: str):
            if item in ("read", "path", "audit"):
                return super(ApiClientMock, self).__getattr__(item)
            if item in ("resource", "task"):
                return type(self)(path=self.path + "/" + item, audit=self.audit)
            return super(ApiClientMock, self).__getattr__(item)
    return ApiClientMock


@pytest.fixture()
def agentr_session_class():
    class AgentRClientMock(mock.MagicMock):
        PATH_PREFIX = "/place/sandbox-data/tasks/0/1/10"
        RESOURCE_TEMPLATE = {
            "state": ctr.State.NOT_READY,
            "task": {"id": 1},
            "time": {
                "created": "2022-04-17T15:40:26.222Z",
                "accessed": "2022-04-17T15:41:26.222Z",
                "expires": "2022-04-17T15:42:26.222Z",
                "updated": "2022-04-17T15:43:26.222Z"
            },
            "owner": "SANDBOX",
            "size": 192891829,
            "md5": "wirohvowirvn",
            "skynet_id": "rbtorrent:iwebowjkec24rv",
            "mds": {
                "key": "mds_key",
                "namespace": "mds_namespace",
                "url": "http://kek/mds_namespace/mds_key"
            },
            "multifile": False,
            "executable": False
        }

        def __init__(self, *args, **kwargs):
            super(AgentRClientMock, self).__init__(*args, **kwargs)
            self.storage = {}
            self.next_id = 1

        def resource_sync(self, resource_id: int) -> str:
            return self.PATH_PREFIX + "/{}".format(resource_id)

        def resource_register(
            self, path: str, type: str, name: str, arch: str, attrs: dict[str, str]
        ) -> dict:
            resource = {
                "type": type,
                "arch": arch or "any",
                "description": name,
                "attributes": attrs,
                "file_name": os.path.basename(path),
            }
            resource.update(copy.deepcopy(self.RESOURCE_TEMPLATE))
            resource["id"] = self.next_id
            self.storage[self.next_id] = resource
            self.next_id += 1
            return resource

        def resource_complete(self, rid: int) -> dict:
            self.storage[rid]["state"] = ctr.State.READY
            return self.storage[rid]
    return AgentRClientMock


@pytest.fixture()
def full_proto_resource_query():
    proto_resource_query = resource_manager_api_pb2.GetResourcesRequest()
    proto_resource_query.ids.append(1)
    proto_resource_query.ids.append(3)
    proto_resource_query.type = "TEST_TASK_2_RESOURCE"
    proto_resource_query.state = ctr.State.READY
    proto_resource_query.owner = "SANDBOX"
    proto_resource_query.task_ids.append(1)
    proto_resource_query.task_ids.append(2)
    proto_resource_query.attributes_query.any_attr = True

    proto_resource_query.attributes_query.attributes["ttl"] = "14"
    proto_resource_query.attributes_query.attributes["released"] = "prestable"

    proto_resource_query.offset = 0
    proto_resource_query.limit = 1
    proto_resource_query.order.append("-id")

    return proto_resource_query


@pytest.fixture()
def full_resource_query():
    return {
        "ids": [1, 3],
        "resource_type": "TEST_TASK_2_RESOURCE",
        "state": ctr.State.READY,
        "owner": "SANDBOX",
        "task_ids": [1, 2],
        "any_attr": True,
        "attributes": {
            "ttl": "14",
            "released": "prestable"
        },
        "offset": 0,
        "limit": 1,
        "order": ["-id"]
    }


@pytest.fixture()
def owner_proto_resource_query():
    proto_resource_query = resource_manager_api_pb2.GetResourcesRequest()
    proto_resource_query.owner = "SANDBOX"
    proto_resource_query.limit = 3
    return proto_resource_query


@pytest.fixture()
def owner_resource_query():
    return {
        "ids": [],
        "resource_type": "",
        "state": "",
        "owner": "SANDBOX",
        "task_ids": [],
        "any_attr": False,
        "attributes": {},
        "offset": 0,
        "limit": 3,
        "order": []
    }


@pytest.fixture()
def proto_create_resource_request(agentr_session_class):
    proto_create_resource_request = resource_manager_api_pb2.CreateResourceRequest()
    proto_create_resource_request.type = "TEST_TASK_2_RESOURCE"
    proto_create_resource_request.arch = "linux"
    proto_create_resource_request.owner = "SANDBOX"
    proto_create_resource_request.attributes["attr1"] = "value1"
    proto_create_resource_request.attributes["ttl"] = "14"
    proto_create_resource_request.path = agentr_session_class.PATH_PREFIX + "/lifelog"
    proto_create_resource_request.description = "Some test resource"
    return proto_create_resource_request


def generate_new_resource(path):
    return {
        "resource_type": "TEST_TASK_2_RESOURCE",
        "arch": "linux",
        "owner": "SANDBOX",
        "attributes": {
            "attr1": "value1",
            "ttl": "14"
        },
        "path": path,
        "description": "Some test resource"
    }


@pytest.fixture()
def new_resource(agentr_session_class):
    return generate_new_resource(agentr_session_class.PATH_PREFIX + "/lifelog")


@pytest.fixture()
def full_resource1_with_mds(s3_simulator, sample_file, tmpdir, full_resource1):
    filename, filepath, filedata = sample_file

    with open(filepath, "rb") as f:
        s3_key = common_mds.S3().upload_file(f, filename, size=len(filedata), executable=False)[0]
    assert requests.get(common_mds.s3_link(s3_key)).content == filedata
    full_resource1.update({
        "mds": {
            "key": s3_key,
            "namespace": None
        },
        "file_name": filename,
        "multifile": False,
        "size": len(filedata),
        "executable": False,
        "md5": hashlib.md5(filedata).hexdigest()
    })
    return full_resource1


@pytest.fixture()
def sample_file_new_resource(sample_file):
    filename, filepath, filedata = sample_file
    return generate_new_resource(filepath)


@pytest.fixture()
def sample_dir_new_resource(sample_dir):
    return generate_new_resource(sample_dir[0])


@pytest.fixture(scope="session")
def resource_manager_port(port_manager):
    return port_manager.get_port()


@pytest.fixture()
def clear_storage():
    local_storage = storage.Storage()
    if local_storage.resources:
        for resource in local_storage.resources.values():
            dir_path = local_storage._resource_directory(resource["id"])
            try:
                shutil.rmtree(dir_path)
            except:
                pass
        try:
            os.unlink(local_storage.metadata_path)
        except:
            pass
    local_storage = storage.Storage()
    assert len(local_storage.resources) == 0
    return local_storage


@pytest.fixture()
def resource_manager(request, resource_manager_port, config_path, tmpdir):
    env = {
        "SANDBOX_CONFIG": config_path,
    }
    resource_manager_path = yatest.common.binary_path("sandbox/tasklet/sidecars/resource_manager/resource_manager")
    address = "[::]:{}".format(resource_manager_port)
    cmd = [
        resource_manager_path,
        "--runtime", types.Runtime.TEST.value,
        "--address", address,
        "--workers", "2"
    ]
    process = sp.Popen(cmd, env=env, cwd=tmpdir)

    def finalizer():
        process.kill()
        process.wait(3)
        if process.poll() is None:
            process.send_signal(signal.SIGKILL)
    request.addfinalizer(finalizer)

    while True:
        resource_manager = resource_manager_api_pb2_grpc.ResourceManagerAPIStub(grpc.insecure_channel(address))
        try:
            query = resource_manager_api_pb2.CreateResourceRequest()
            query.owner = "TEST"
            resource_manager.GetResources(query)
            break
        except:
            time.sleep(0.5)
    return address
