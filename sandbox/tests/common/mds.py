import io
import os
import json
import time
import random
import socket
import hashlib
import tarfile
import datetime as dt
import textwrap
import threading as th
import xml.parsers.expat
import xml.etree.ElementTree

import six
import pytest
from six.moves.urllib import parse as urlparse


from sandbox.common import mds as common_mds
from sandbox.common import itertools as common_itertools
import sandbox.common.types.resource as ctr


pytest_plugins = (
    "sandbox.tests.common.network",
)


# noinspection PyPep8Naming
class MDSSimulatorHandler(six.moves.BaseHTTPServer.BaseHTTPRequestHandler):
    OK_TMPL = textwrap.dedent("""
        <?xml version="1.0" encoding="utf-8"?>
        <post obj="namespace.filename" id="81d8ba78...666dd3d1" groups="3" size="{size}" key="{key}">
          <complete addr="141.8.145.55:1032" path="/src/storage/8/data-0.0" group="223" status="0"/>
          <complete addr="141.8.145.116:1032" path="/srv/storage/8/data-0.0" group="221" status="0"/>
          <complete addr="141.8.145.119:1029" path="/srv/storage/5/data-0.0" group="225" status="0"/>
          <written>3</written>
        </post>
    """).strip()

    FORBIDDEN_TMPL = textwrap.dedent("""
        <?xml version="1.0" encoding="utf-8"?>
        <post>
          <key>{key}</key>
        </post>
    """).strip()

    UPLOAD_PREFIX = "/upload-"
    GET_PREFIX = "/get-"
    DELETE_PREFIX = "/delete-"
    ANNOUNCE = "/announce"
    SKYNET_ID = b"rbtorrent:024f2df8b6090cb45e9c6c4f4ab5f8f3784377d1"
    RANGE_PREFIX = "bytes="

    def do_GET(self):
        if self.path.startswith(self.GET_PREFIX):
            return self.get_data()
        if self.path.startswith(self.DELETE_PREFIX):
            return self.delete_data()
        self.send_response(six.moves.http_client.NOT_FOUND)
        self.end_headers()

    def do_POST(self):
        if self.path == self.ANNOUNCE:
            return self.announce()
        return self.upload()

    def get_data(self):
        namespace, _, key = self.path[len(self.GET_PREFIX):].partition("/")
        if not key:
            self.send_response(six.moves.http_client.BAD_REQUEST)
            self.end_headers()
            return
        data = self.server.get(namespace, key)
        if data is None:
            self.send_response(six.moves.http_client.NOT_FOUND)
            self.end_headers()
            return
        data_range = self.headers.get("Range")
        if data_range and data_range.startswith(self.RANGE_PREFIX):
            data_range = data_range[len(self.RANGE_PREFIX):]
            range_arr = data_range.split("-", 1)
            data_from, data_to = 0, len(data) - 1
            if len(range_arr) > 0 and range_arr[0] != "":
                data_from = int(range_arr[0])
            if len(range_arr) > 1 and range_arr[1] != "":
                data_to = int(range_arr[1])
            data = data[data_from: data_to + 1]

        self.send_response(six.moves.http_client.OK)
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Content-Type", "text/plain")
        self.end_headers()
        self.wfile.write(six.ensure_binary(data))

    def delete_data(self):
        namespace, _, key = self.path[len(self.DELETE_PREFIX):].partition("/")
        if not key:
            self.send_response(six.moves.http_client.BAD_REQUEST)
        elif self.server.delete(namespace, key):
            self.send_response(six.moves.http_client.OK)
        else:
            self.send_response(six.moves.http_client.NOT_FOUND)
        self.end_headers()

    def upload(self):
        content_length = self.headers.get("Content-Length")
        if content_length is not None:
            content_length = int(content_length)
        data = self.rfile.read(content_length)
        if not self.path.startswith(self.UPLOAD_PREFIX):
            self.send_response(six.moves.http_client.NOT_FOUND)
            self.end_headers()
            return
        namespace, _, filename = self.path[len(self.UPLOAD_PREFIX):].partition("/")
        if not filename:
            self.send_response(six.moves.http_client.BAD_REQUEST)
            self.end_headers()
            return
        success, key = self.server.add(namespace, filename, data)
        if success:
            status = six.moves.http_client.OK
            result = self.OK_TMPL.format(size=len(data), key=key)
        else:
            status = six.moves.http_client.FORBIDDEN
            result = self.FORBIDDEN_TMPL.format(key=key)
        self.send_response(status)
        self.send_header("Content-type", "text/xml")
        self.end_headers()
        response = io.BytesIO()
        response.write(six.ensure_binary(result))
        self.wfile.write(response.getvalue())

    def announce(self):
        response = self.SKYNET_ID
        self.send_response(six.moves.http_client.OK)
        self.send_header("Content-Length", str(len(response)))
        self.send_header("Content-Type", "text/plain")
        self.end_headers()
        self.wfile.write(response)


class MDSSimulator(six.moves.BaseHTTPServer.HTTPServer):
    address_family = socket.AF_INET6
    COUPLE_ID = 42

    def __init__(self, *args, **kws):
        self.storage = {}
        six.moves.BaseHTTPServer.HTTPServer.__init__(self, *args, **kws)

    def server_bind(self):
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        six.moves.BaseHTTPServer.HTTPServer.server_bind(self)

    def _key(self, filename):
        return "{}/{}".format(self.COUPLE_ID, filename)

    def add(self, namespace, filename, data):
        key = self._key(filename)
        storage = self.storage.setdefault(namespace, {})
        if key in storage:
            return False, key
        storage[key] = data
        return True, key

    def list(self, namespace, prefix=None):
        storage = self.storage.setdefault(namespace, {})
        for key, data in storage.items():
            if prefix is None or key.startswith(prefix):
                yield key, data

    def get(self, namespace, key):
        storage = self.storage.setdefault(namespace, {})
        return storage.get(key)

    def delete(self, namespace, key):
        storage = self.storage.setdefault(namespace, {})
        return storage.pop(key, None) is not None


@pytest.fixture
def mds_simulator(request, mds_port, config_path):
    server = MDSSimulator(("localhost", mds_port), MDSSimulatorHandler)
    server_thread = th.Thread(target=server.serve_forever)
    server_thread.setDaemon(True)
    server_thread.start()

    def finalizer():
        server.shutdown()
        server.server_close()
        server_thread.join()

    request.addfinalizer(finalizer)
    return server


# noinspection PyPep8Naming
class S3SimulatorHandler(MDSSimulatorHandler):
    BUCKET_STATS_PREFIX = "/stats/buckets/"
    BUCKET_MAX_SIZE = 1 << 20
    GET_PREFIX = "/"
    DELETE_OBJECTS_TMPL = textwrap.dedent("""
        <?xml version='1.0' encoding='UTF-8'?>
        <DeleteResult xmlns="http://s3.amazonaws.com/doc/2006-03-01/">
            {objs}
        </DeleteResult>
    """)
    LIST_BUCKET_TMPL = textwrap.dedent("""
        <?xml version="1.0" encoding="UTF-8"?>
        <ListBucketResult xmlns="http://s3.amazonaws.com/doc/2006-03-01/">
            <IsTruncated>false</IsTruncated>
            {items}
            <Name>{bucket}</Name>
            <Prefix>{prefix}</Prefix>
            <MaxKeys>{max_keys}</MaxKeys>
            <KeyCount>{key_count}</KeyCount>
        </ListBucketResult>
    """)
    LIST_BUCKET_ITEM_TMPL = textwrap.dedent("""
            <Contents>
                <Key>{key}</Key>
                <Size>{size}</Size>
                <ETag>{etag}</ETag>
                <LastModified>{last_modified}</LastModified>
                <StorageClass>STANDARD</StorageClass>
            </Contents>
    """)

    def do_GET(self):
        if self.path.startswith(self.BUCKET_STATS_PREFIX):
            bucket = self.path[len(self.BUCKET_STATS_PREFIX):]
            data = json.dumps({"name": bucket, "max_size": self.BUCKET_MAX_SIZE, "used_space": 0})
            self.send_response(six.moves.http_client.OK)
            self.send_header("Content-Length", str(len(data)))
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(six.ensure_binary(data))
        else:
            bucket, _, query_string = self.path[1:].partition("?")
            params = urlparse.parse_qs(query_string)
            if params.get("list-type") == ["2"]:
                return self.list_bucket(bucket, params)
            self.get_data()

    def list_bucket(self, bucket, params):
        items = []
        prefix = params.get("prefix", [None])[0]
        for key, data in self.server.list(bucket, prefix=prefix):
            items.append(self.LIST_BUCKET_ITEM_TMPL.format(
                key=key,
                size=len(data),
                etag=hashlib.md5(data).hexdigest(),
                last_modified=dt.datetime.utcnow().isoformat() + "Z"
            ))
        result = self.LIST_BUCKET_TMPL.format(
            bucket=bucket,
            prefix=prefix or "",
            max_keys=1000,
            key_count=len(items),
            items="\n".join(items)
        )
        self.send_response(six.moves.http_client.OK)
        self.send_header("Content-type", "text/xml")
        self.end_headers()
        response = io.BytesIO()
        response.write(
            six.ensure_binary(
                result.strip()
            )
        )
        self.wfile.write(response.getvalue())

    def do_POST(self):
        bucket, _, params = self.path[1:].partition("?")
        if params != "delete":
            self.send_response(six.moves.http_client.BAD_REQUEST)
            self.end_headers()
            return
        content_length = self.headers.get("Content-Length")
        if content_length is not None:
            content_length = int(content_length)
        data = self.rfile.read(content_length)
        keys = []
        for obj in xml.etree.ElementTree.fromstring(data):
            key = obj[0].text
            self.server.delete(bucket, key)
            keys.append(key)
        self.send_response(six.moves.http_client.OK)
        self.send_header("Content-type", "text/xml")
        self.end_headers()
        response = io.BytesIO()
        response.write(
            six.ensure_binary(
                self.DELETE_OBJECTS_TMPL.format(
                    objs="".join("<Object><Key>{}</Key></Object>".format(key) for key in keys)
                ).strip()
            )
        )
        self.wfile.write(response.getvalue())

    def do_PUT(self):
        self.upload()

    def do_DELETE(self):
        self.delete_data()

    def upload(self):
        bucket, _, key = self.path[1:].partition("/")
        content_length = self.headers.get("Content-Length")
        if content_length is not None:
            content_length = int(content_length)
        data = self.rfile.read(content_length)
        if not key:
            self.send_response(six.moves.http_client.BAD_REQUEST)
            self.end_headers()
            return
        self.server.add(bucket, key, data)
        self.send_response(six.moves.http_client.OK)
        self.end_headers()
        self.wfile.write(b"")

    def delete_data(self):
        bucket, _, key = self.path[1:].partition("/")
        if bucket and key:
            self.server.delete(bucket, key)
        self.send_response(six.moves.http_client.NO_CONTENT)
        self.end_headers()


def get_failed_s3_handler(status_code, methods):
    class FailedS3SimulatorHandler(S3SimulatorHandler):
        ERROR_CODE_DATA = {
            429: ("TooManyRequests", "Too Many Requests"),
            404: ("NoSuchBucket", "The specified bucket does not exist.")
        }
        RESPONSE_DATA = textwrap.dedent("""
            <?xml version='1.0' encoding='UTF-8'?>
            <Error>
                <Code>{error_data[0]}</Code>
                <Message>{error_data[1]}</Message>
            </Error>
        """).strip()

        def send_error_response(self):
            # start reading content to ignore additional 100-Continue response to S3 client
            content_length = self.headers.get("Content-Length")
            if content_length is not None:
                content_length = int(content_length)
                self.rfile.read(content_length)
            self.send_response(status_code)
            self.send_header("Content-Type", "text/xml")
            self.end_headers()
            self.wfile.write(
                six.ensure_binary(
                    self.RESPONSE_DATA.format(
                        error_data=self.ERROR_CODE_DATA[status_code]
                    )
                )
            )

        def do_GET(self):
            if "GET" in methods:
                self.send_error_response()
            else:
                S3SimulatorHandler.do_GET(self)

        def do_DELETE(self):
            if "DELETE" in methods:
                self.send_error_response()
            else:
                S3SimulatorHandler.do_DELETE(self)

        def do_POST(self):
            if "POST" in methods:
                self.send_error_response()
            else:
                S3SimulatorHandler.do_POST(self)
            self.send_error_response()

        def do_PUT(self):
            if "PUT" in methods:
                self.send_error_response()
            else:
                S3SimulatorHandler.do_PUT(self)

    return FailedS3SimulatorHandler


class S3Simulator(MDSSimulator, object):
    forced_status_counter = None
    forced_status_timeout = None

    def _key(self, filename):
        return filename

    def force_error_responses(self, status_code, methods=("POST", "PUT"), timer=None, counter=None):
        self.original_handler = self.RequestHandlerClass
        self.RequestHandlerClass = get_failed_s3_handler(status_code, methods)
        assert timer or counter, "Either timer or counter must be provided"
        if timer:
            self.forced_status_timeout = time.time() + timer
        elif counter:
            self.forced_status_counter = counter

    def process_request(self, request, client_address):
        if self.forced_status_timeout and self.forced_status_timeout < time.time():
            self.RequestHandlerClass = self.original_handler
            self.forced_status_timeout = None
        if self.forced_status_counter is not None:
            self.forced_status_counter -= 1
            if self.forced_status_counter < 0:
                self.RequestHandlerClass = self.original_handler
                self.forced_status_counter = None
        return super(S3Simulator, self).process_request(request, client_address)


@pytest.fixture
def s3_simulator(request, s3_port, config_path, monkeypatch):
    server = S3Simulator(("localhost", s3_port), S3SimulatorHandler)
    server_thread = th.Thread(target=server.serve_forever)
    server_thread.setDaemon(True)
    server_thread.start()
    print("Started S3 simulator at localhost:{}".format(s3_port))

    def finalizer():
        server.shutdown()
        server.server_close()
        server_thread.join()

    request.addfinalizer(finalizer)
    monkeypatch.setenv("AWS_ACCESS_KEY_ID", "1234567890")
    monkeypatch.setenv("AWS_SECRET_ACCESS_KEY", "1234567890")
    return server


@pytest.fixture
def sample_file(tmpdir):
    filepath = os.path.join(str(tmpdir), "sample_file")
    open(filepath, "wb").write(b"sample file data")
    with open(filepath, "rb") as f:
        return os.path.basename(filepath), filepath, f.read()


def random_data(size, entropy=.5, symbol_size=32):
    symbol = None
    total_symbols, last_symbol_size = divmod(size, symbol_size)
    for i in six.moves.xrange(total_symbols + 1):
        if symbol is None or random.random() < entropy:
            symbol = os.urandom(symbol_size)
        if i < total_symbols:
            yield symbol
        elif last_symbol_size:
            yield symbol[:last_symbol_size]


@pytest.fixture
def file1_data():
    return b"".join(random_data(5 << 19))


@pytest.fixture
def file2_data():
    return b"".join(random_data(5 << 19))


def _sample_dir(tmpdir, file1_data, file2_data, old_style=False):
    dirpath = os.path.join(str(tmpdir), "resource")
    os.mkdir(dirpath)
    os.mkdir(os.path.join(dirpath, "empty"))
    file1_path = os.path.join(dirpath, "file1")
    open(file1_path, "wb").write(file1_data)
    os.mkdir(os.path.join(dirpath, "subdir"))
    file2_path = os.path.join(dirpath, "subdir", "file2")
    open(file2_path, "wb").write(file2_data)
    os.symlink("../file1", os.path.join(dirpath, "subdir", "symlink"))
    os.symlink("subdir", os.path.join(dirpath, "subdir_symlink"))
    mds_name = common_mds.S3._mds_name if old_style else lambda *_: None
    return dirpath, sorted([
        dict(common_mds.schema.MDSFileMeta.create(
            key=mds_name(None, "resource/file1"), type=ctr.FileType.FILE,
            path="resource/file1", size=os.path.getsize(file1_path),
            md5=hashlib.md5(file1_data).hexdigest(),
            sha1_blocks=[
                hashlib.sha1(chunk).hexdigest()
                for chunk in common_itertools.chunker(file1_data, common_mds.HashCalculator.SHA1_BLOCK_SIZE)
            ],
            mime=common_mds.MimeTypes.get_type(file1_path),
        )),
        dict(common_mds.schema.MDSFileMeta.create(
            key=mds_name(None, "resource/subdir/file2"), type=ctr.FileType.FILE,
            path="resource/subdir/file2", size=os.path.getsize(file2_path),
            md5=hashlib.md5(file2_data).hexdigest(),
            sha1_blocks=[
                hashlib.sha1(chunk).hexdigest()
                for chunk in common_itertools.chunker(file2_data, common_mds.HashCalculator.SHA1_BLOCK_SIZE)
            ],
            mime=common_mds.MimeTypes.get_type(file2_path),
        )),
        dict(common_mds.schema.MDSFileMeta.create(
            type=ctr.FileType.SYMLINK, path="resource/subdir/symlink", symlink="../file1"
        )),
        dict(common_mds.schema.MDSFileMeta.create(
            type=ctr.FileType.SYMLINK, path="resource/subdir_symlink", symlink="subdir"
        )),
        dict(common_mds.schema.MDSFileMeta.create(
            type=ctr.FileType.DIR, path="resource/empty"
        )),
        dict(common_mds.schema.MDSFileMeta.create(
            type=ctr.FileType.DIR, path="resource"
        )),
        dict(common_mds.schema.MDSFileMeta.create(
            type=ctr.FileType.DIR, path="resource/subdir"
        )),
    ], key=lambda _: _["path"])


@pytest.fixture
def sample_dir(tmpdir, file1_data, file2_data):
    return _sample_dir(tmpdir, file1_data, file2_data)


@pytest.fixture
def sample_dir_old_style(tmpdir, file1_data, file2_data):
    return _sample_dir(tmpdir, file1_data, file2_data, old_style=True)


@pytest.fixture
def tar_sample_dir(tmpdir, sample_dir):
    dirpath, metadata = sample_dir
    for item in metadata:
        item["key"] = None
        item["md5"] = None
        item["sha1_blocks"] = None
    metadata.insert(
        0, dict(common_mds.schema.MDSFileMeta.create(
            type=ctr.FileType.DIR,
            path="",
        ))
    )
    return dirpath, sorted(metadata, key=lambda _: _["path"])


@pytest.fixture
def empty_file(tmpdir):
    filepath = os.path.join(str(tmpdir), "resource")
    open(filepath, "wb").close()
    return filepath, [
        dict(common_mds.schema.MDSFileMeta.create(
            type=ctr.FileType.TOUCH, path="resource"
        ))
    ]


TEST_TAR_NAME = "test.tar"
TEST_TGZ_NAME = "test.tgz"


def tar_file(path, tmpdir):
    full_path = os.path.join(str(tmpdir), TEST_TAR_NAME)
    listdir = os.listdir
    os.listdir = lambda _: sorted(listdir(_))
    try:
        with tarfile.open(full_path, mode="w", format=tarfile.GNU_FORMAT) as tar:
            tar.add(path, arcname=os.path.basename(path))
        return open(full_path, "rb")
    finally:
        os.listdir = listdir


def tgz_file(path, tmpdir):
    full_path = os.path.join(str(tmpdir), TEST_TGZ_NAME)
    listdir = os.listdir
    os.listdir = lambda _: sorted(listdir(_))
    try:
        with tarfile.open(full_path, mode="w:gz") as tar:
            tar.add(path, arcname=os.path.basename(path))
        return open(full_path, "rb")
    finally:
        os.listdir = listdir
