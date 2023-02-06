import os
import py
import sys
import json
import hashlib
import subprocess as sp

from sandbox import common
from sandbox.agentr import types as atypes


def _worker_run(args, fails=False):
    p = sp.Popen(args, stdout=sp.PIPE, stderr=sp.PIPE)
    stdout, stderr = p.communicate()
    assert bool(p.returncode) == fails, "STDOUT: {}\n\n STDERR {}\n\n".format(stdout, stderr)
    return stdout, stderr, p.returncode


def test__worker_tidy_up(tmpdir, user):
    os.makedirs(os.path.join(tmpdir, "testdir", "innerdir"))
    testdir = os.path.join(tmpdir, "testdir")
    files = (
        (os.path.join(testdir, "foo"), 1024),
        (os.path.join(testdir, "foo0"), 0),
        (os.path.join(testdir, "innerdir", "bar"), 2048),
        (os.path.join(testdir, "innerdir", "bar0"), 0),
    )
    for file_path, file_size in files:
        py.path.local(file_path, "w").write("1" * file_size)

    worker_path = os.path.join(os.path.dirname(__file__), os.pardir, "bin", "worker.py")

    _worker_run([sys.executable, worker_path, "tidy_up", user, testdir])
    for file_path, _ in files:
        assert os.path.exists(file_path), file_path

    common.fs.chmod_for_path(testdir, "a+w")

    _worker_run([sys.executable, worker_path, "tidy_up", user, testdir, "--rm_empty_files"])
    for file_path, file_size in files:
        assert os.path.exists(file_path) == (file_size > 0)


def test__worker_download(s3_simulator, sample_file, tmpdir):
    filename, filepath, filedata = sample_file
    with open(filepath, "rb") as f:
        s3_key = common.mds.S3().upload_file(f, filename, size=len(filedata), executable=False)[0]

    resource_path = os.path.join(str(tmpdir), "downloaded_resource")
    os.mkdir(resource_path)
    worker_path = os.path.join(os.path.dirname(__file__), os.pardir, "bin", "worker.py")
    resource = {
        "id": 1,
        "mds": {
            "key": s3_key,
            "namespace": None
        },
        "file_name": filename,
        "multifile": False,
        "size": len(filedata),
        "executable": False,
        "md5": hashlib.md5(filedata).hexdigest()
    }

    path = _worker_run([sys.executable, worker_path, "download", json.dumps(resource), resource_path])[0].strip()
    assert path == os.path.join(resource_path, filename)
    with open(path, "rb") as f:
        downloaded_filedata = f.read()
        assert downloaded_filedata == filedata, "{}\n{}".format(downloaded_filedata, filedata)

    resource["executable"] = None
    assert _worker_run(
        [sys.executable, worker_path, "download", json.dumps(resource), resource_path], fails=True
    )[2] == atypes.MDS_DOWNLOAD_NOT_ALLOWED

    resource["mds"]["key"] = "error"
    resource["executable"] = False

    assert _worker_run(
        [sys.executable, worker_path, "download", json.dumps(resource), resource_path], fails=True
    )[2] == 1
