# pylint: disable=wildcard-import, unused-wildcard-import, import-error
import pytest

from messenger_plugins import *  # noqa: F403 F401


# root conftest for service messenger
pytest_plugins = ['messenger_plugins.pytest_plugins']


@pytest.fixture(autouse=True)
def _mock_personal(mockserver):
    @mockserver.json_handler('/personal/v1/phones/retrieve')
    def _phones_retrieve(request):
        return {'id': '557f191e810c19729de860ea', 'value': '+70001112233'}

    @mockserver.json_handler('/personal/v1/telegram_logins/retrieve')
    def _logins_retrieve(request):
        return {'id': 'login_pdid', 'value': 'marge'}

    @mockserver.json_handler('/personal/v1/telegram_logins/find')
    def _logins_find(request):
        return {'id': 'login_pdid', 'value': 'marge'}


class FakeMdsContext:
    error = None
    _storage: dict = {}

    def put_object(self, bucket, key, body, *args, **kwargs):
        self._storage.setdefault(bucket, {})
        self._storage[bucket][key] = bytearray(body)

    def get_object(self, bucket, key) -> bytearray:
        return self._storage.get(bucket, {}).get(key)

    def list_objects(self, bucket, prefix) -> dict:
        results = {k: v for k, v in self._storage.get(bucket, {}).items()}
        return results

    def set_error(self, error):
        self.error = error


def mds_s3_server_list_response(
        objects: dict, bucket: str, prefix: str, max_keys: int,
) -> str:
    buffer = '<?xml version="1.0" encoding="UTF-8"?>'
    buffer += (
        '<ListBucketResult '
        + 'xmlns="http://s3.amazonaws.com/doc/2006-03-01/">'
    )
    buffer += '<Name>' + bucket + '</Name>'
    buffer += '<Prefix>' + prefix + '</Prefix>'
    buffer += '<MaxKeys>' + str(max_keys) + '</MaxKeys>'
    buffer += '<IsTruncated>false</IsTruncated>'
    buffer += '<Contents>'
    for k, value in objects.items():
        if prefix not in k:
            continue
        buffer += '<Key>' + k + '</Key>'
        buffer += '<LastModified>2022-01-11T21:50:41.838Z</LastModified>'
        buffer += '<Owner>'
        buffer += '<ID>1120000000515612</ID>'
        buffer += '<DisplayName>1120000000515612</DisplayName>'
        buffer += '</Owner>'
        buffer += '<ETag>&#34;153b0c2531a4b24ca251cfa5e78f9158&#34;</ETag>'
        buffer += '<Size>' + str(len(value)) + '</Size>'
        buffer += '<StorageClass>STANDARD</StorageClass>'
    buffer += '</Contents>'
    buffer += '<Marker></Marker>'
    buffer += '</ListBucketResult>'
    return buffer


@pytest.fixture(name='mds_s3', autouse=True)
def mds_s3_client(mockserver):
    context = FakeMdsContext()

    @mockserver.handler('/mds-s3', prefix=True)
    def _mock_mds_s3(request):
        if context.error:
            return mockserver.make_response(
                f'Error {context.error}', context.error,
            )
        bucket = 'media'
        path_parts = request.path.split('/')
        path = '/'.join(path_parts[2:])
        if request.method == 'PUT':
            context.put_object(bucket, path, request.get_data())
            return mockserver.make_response('', 200)
        if request.method == 'GET':
            if request.args.get('prefix') is not None:
                prefix = request.args.get('prefix')
                max_keys = 1
                founded = context.list_objects(bucket, prefix)
                if founded:
                    data = mds_s3_server_list_response(
                        founded, bucket, prefix, max_keys,
                    )
                    return mockserver.make_response(data, 200)
            else:
                data = context.get_object(bucket, path)
                if data:
                    return mockserver.make_response(data, 200)
        return mockserver.make_response('NotFound', 404)

    return context
