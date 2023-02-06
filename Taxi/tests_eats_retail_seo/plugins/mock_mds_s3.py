import datetime as dt
import hashlib
import pathlib
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

        def _get_keys_by_prefix(self, prefix):
            filtered_keys = []
            for key in self.storage:
                filepath = pathlib.Path(key)
                if str(filepath.parent) != prefix:
                    continue
                filtered_keys.append(key)
            return filtered_keys

        def get_list(self, prefix='', max_keys=None, marker=None):
            if max_keys is None:
                max_keys = 1000
            if marker is None:
                marker = ''
            empty_result = {'files': [], 'is_truncated': False}
            prefix = prefix.rstrip('/')
            keys = sorted(self._get_keys_by_prefix(prefix))
            if not keys:
                return empty_result
            from_index = 0
            if marker != '':
                if marker > keys[-1]:
                    return empty_result
                for i, key in enumerate(keys):
                    if key > marker:
                        from_index = i
                        break
            if from_index >= len(keys):
                return empty_result
            files = [
                self.storage[key]
                for key in keys[from_index : from_index + max_keys]
            ]
            is_truncated = from_index + max_keys >= len(keys)
            return {'files': files, 'is_truncated': is_truncated}

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
