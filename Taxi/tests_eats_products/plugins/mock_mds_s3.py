import datetime as dt
import hashlib
from typing import Mapping
from typing import Optional

import pytest


class S3Data:
    data: Optional[bytearray] = None
    meta: Optional[Mapping[str, str]] = None

    def __init__(self, data, meta: Optional[Mapping[str, str]] = None):
        self.data = data
        self.meta = meta


@pytest.fixture(name='mds_s3_storage', autouse=True)
def _mds_s3_storage():
    """
    Copy-paste from media-storage service
    """

    class FakeMdsClient:
        storage = {}

        @staticmethod
        def _generate_etag(data):
            return hashlib.md5(data).hexdigest()

        def put_object(self, key, body):
            meta = {
                'ETag': self._generate_etag(body),
                'Last-Modified': str(dt.datetime.now()),
            }
            self.storage[key] = S3Data(body, meta)
            return meta

        def get_object(self, key) -> S3Data:
            return self.storage.get(key)

    client = FakeMdsClient()

    return client


@pytest.fixture(name='mds_s3', autouse=True)
def _mds_s3(mockserver, mds_s3_storage):
    path_prefix = '/mds-s3'

    def _extract_key(request):
        return request.path[len(path_prefix) + 1 :]

    @mockserver.handler(path_prefix, prefix=True)
    def _mock_all(request):

        key = _extract_key(request)

        if request.method == 'PUT':
            copy_source = request.headers.get('x-amz-copy-source', None)
            if copy_source is not None:
                dest_bucket = request.headers['Host'].split('.')[0]
                source_bucket, source_key = copy_source.split('/')[1:3]
                # coping between buckets isn't supported yet
                assert source_bucket == dest_bucket

                data = mds_s3_storage.get_object(source_key).data
            else:
                data = request.get_data()
            meta = mds_s3_storage.put_object(key, data)
            return mockserver.make_response('OK', 200, headers=meta)
        if request.method == 'GET':
            s3_object = mds_s3_storage.get_object(key)
            if s3_object:
                return mockserver.make_response(
                    s3_object.data, 200, headers=s3_object.meta,
                )
        if request.method == 'HEAD':
            s3_object = mds_s3_storage.get_object(key)
            if s3_object:
                return mockserver.make_response(
                    'OK', 200, headers=s3_object.meta,
                )
        return mockserver.make_response('Not found or invalid method', 404)
