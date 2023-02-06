import os
import hashlib

import pytest
import requests

from sandbox.agentr import utils as autils

from sandbox.common import mds as common_mds
from sandbox.common import rest as common_rest
import sandbox.common.types.misc as ctm
import sandbox.common.types.resource as ctr

from sandbox.tests.common.mds import tar_file


def get_directory_resource():
    return {
        "type": "TEST_TASK_2_RESOURCE",
        "owner": "SANDBOX",
        "author": "zomb-sandbox",
        "multifile": True,
        "state": ctr.State.READY,
        "sources": [],
        "md5": None,
        "size": None,
        "file_name": None,
        "time": {
            "created": "2022-06-16T21:00:00Z",
        },
        "task": {
            "id": 1
        }
    }


def get_file_resource():
    return {
        "type": "TEST_TASK_2_RESOURCE",
        "owner": "SANDBOX",
        "author": "zomb-sandbox",
        "multifile": False,
        "state": ctr.State.READY,
        "sources": [],
        "md5": None,
        "size": None,
        "file_name": None,
        "time": {
            "created": "2022-06-16T21:00:00Z",
        },
        "task": {
            "id": 1
        }
    }


def _upload_test_dir(sample_dir, serviceapi_simulator, tar_dir):
    sample_dir_path, sample_dir_metadata = sample_dir
    s3_key, metadata = common_mds.S3().upload_directory(sample_dir_path, resource_id=1, tar_dir=tar_dir)

    resource_meta = get_directory_resource()
    resource_meta["size"] = autils.get_disk_usage(str(sample_dir[0]), allow_files=True)[1]
    resource_meta["file_name"] = os.path.basename(str(sample_dir[0]))
    resource_meta["mds"] = {"namespace": None, "key": s3_key}

    serviceapi_client = common_rest.Client("http://localhost:{}/api/v1.0".format(serviceapi_simulator.server_port))
    resource = serviceapi_client.resource.create(resource_meta)
    return resource


def _upload_test_file(sample_file, serviceapi_simulator):
    filename, filepath, filedata = sample_file
    s3_key = common_mds.S3().upload_file(filepath, filename, executable=False)[0]

    resource_meta = get_file_resource()
    resource_meta["size"] = autils.get_disk_usage(str(sample_file[0]), allow_files=True)[1]
    resource_meta["file_name"] = os.path.basename(str(sample_file[0]))
    resource_meta["md5"] = hashlib.md5(filedata).hexdigest()
    resource_meta["mds"] = {"namespace": None, "key": s3_key}

    serviceapi_client = common_rest.Client("http://localhost:{}/api/v1.0".format(serviceapi_simulator.server_port))
    resource = serviceapi_client.resource.create(resource_meta)
    return resource, resource_meta


def _upload_tar_file(tar_sample_dir, tmpdir, serviceapi_simulator):
    s3_name = "test_tar"
    sample_dir_path, sample_dir_metadata = tar_sample_dir
    file_obj = tar_file(sample_dir_path, tmpdir)
    file_obj.seek(0, os.SEEK_END)
    size = file_obj.tell()
    file_obj.seek(0)
    s3_key, metadata = common_mds.S3().upload_tar(file_obj, s3_name, resource_id=1, size=size)

    resource_meta = get_file_resource()
    resource_meta["size"] = size
    file_obj.seek(0)
    resource_meta["file_name"] = s3_name
    resource_meta["md5"] = hashlib.md5(file_obj.read()).hexdigest()
    resource_meta["mds"] = {"namespace": None, "key": s3_key}

    serviceapi_client = common_rest.Client("http://localhost:{}/api/v1.0".format(serviceapi_simulator.server_port))
    resource = serviceapi_client.resource.create(resource_meta)
    return resource, resource_meta


@pytest.mark.parametrize(
    ["sample_dir_fixture_name", "tar_dir"],
    [
        ("sample_dir", True),
        ("sample_dir_old_style", False),
    ]
)
def test_browse_resource_directory_from_s3(
    request, sample_dir_fixture_name, tar_dir, file1_data, proxy, serviceapi_simulator, s3_simulator
):
    sample_dir = request.getfixturevalue(sample_dir_fixture_name)
    resource = _upload_test_dir(sample_dir, serviceapi_simulator, tar_dir)

    result = requests.get("http://{}/{}/file1".format(proxy, resource["id"]))
    assert result.content == file1_data

    return requests.get("http://{}/{}".format(proxy, resource["id"])).text


@pytest.mark.parametrize(
    ["sample_dir_fixture_name", "tar_dir"],
    [
        ("sample_dir", True),
        ("sample_dir_old_style", False),
    ]
)
def test_browse_resource_directory_from_s3_as_json(
    request, sample_dir_fixture_name, tar_dir, proxy, serviceapi_simulator, s3_simulator
):
    sample_dir = request.getfixturevalue(sample_dir_fixture_name)
    resource = _upload_test_dir(sample_dir, serviceapi_simulator, tar_dir)
    headers = {ctm.HTTPHeader.ACCEPT: common_mds.MimeTypes.JSON, ctm.HTTPHeader.HOST: "localhost"}
    return (
        requests.get(f"http://{proxy}/{resource['id']}", headers=headers).text,
        requests.get(f"http://{proxy}/{resource['id']}/empty", headers=headers).text,
        requests.get(f"http://{proxy}/{resource['id']}/subdir", headers=headers).text,
    )


def test_download_file_from_s3(sample_file, proxy, serviceapi_simulator, s3_simulator):
    resource, resource_meta = _upload_test_file(sample_file, serviceapi_simulator)

    result = requests.get("http://{}/{}".format(proxy, resource["id"]))
    assert hashlib.md5(result.content).hexdigest() == resource_meta["md5"]


def test_browse_tar_file(
    tar_sample_dir, sample_dir, tmpdir, file1_data, file2_data, proxy, serviceapi_simulator, s3_simulator
):
    resource, resource_meta = _upload_tar_file(tar_sample_dir, tmpdir, serviceapi_simulator)

    result = requests.get("http://{}/{}".format(proxy, resource["id"]))
    assert hashlib.md5(result.content).hexdigest() == resource_meta["md5"]

    result = requests.get("http://{}/{}/resource/file1".format(proxy, resource["id"]))
    assert len(result.content) == len(file1_data)

    result = requests.get("http://{}/{}/".format(proxy, resource["id"])).text
    result += requests.get("http://{}/{}/resource".format(proxy, resource["id"])).text
    return result


def test_browse_tar_file_as_json(
    tar_sample_dir, sample_dir, tmpdir, file1_data, file2_data, proxy, serviceapi_simulator, s3_simulator
):
    resource, resource_meta = _upload_tar_file(tar_sample_dir, tmpdir, serviceapi_simulator)
    headers = {ctm.HTTPHeader.ACCEPT: common_mds.MimeTypes.JSON, ctm.HTTPHeader.HOST: "localhost"}
    return (
        requests.get(f"http://{proxy}/{resource['id']}/", headers=headers).text,
        requests.get(f"http://{proxy}/{resource['id']}/resource", headers=headers).text,
        requests.get(f"http://{proxy}/{resource['id']}/resource/empty", headers=headers).text,
        requests.get(f"http://{proxy}/{resource['id']}/resource/subdir", headers=headers).text,
    )


def test_download_file_from_s3_too_many_requests(sample_file, proxy, serviceapi_simulator, s3_simulator):
    resource, resource_meta = _upload_test_file(sample_file, serviceapi_simulator)

    s3_simulator.force_error_responses(429, methods=("GET",), counter=1)
    result = requests.get(f"http://{proxy}/{resource['id']}")
    assert result.status_code == requests.codes.too_many_requests


def test_download_resource_directory_from_s3_stream(sample_dir, file1_data, proxy, serviceapi_simulator, s3_simulator):
    resource = _upload_test_dir(sample_dir, serviceapi_simulator, True)

    result = requests.get(f"http://{proxy}/{resource['id']}?stream=tar")
    assert result.status_code == 200

    result = requests.get(f"http://{proxy}/{resource['id']}?stream=tgz")
    assert result.status_code == 200


def test_browse_resource_directory_from_s3_not_found(sample_dir, file1_data, proxy, serviceapi_simulator, s3_simulator):
    resource = _upload_test_dir(sample_dir, serviceapi_simulator, True)

    s3_simulator.force_error_responses(404, methods=("GET",), counter=2)
    result = requests.get(f"http://{proxy}/{resource['id']}/file1")

    assert result.status_code == 404


def test_download_single_file_without_metadata(sample_file, proxy, serviceapi_simulator, s3_simulator):
    resource, resource_meta = _upload_test_file(sample_file, serviceapi_simulator)

    s3_simulator.force_error_responses(404, methods=("GET",), counter=1)
    result = requests.get(f"http://{proxy}/{resource['id']}")

    assert hashlib.md5(result.content).hexdigest() == resource_meta["md5"]
