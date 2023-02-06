# pylint: disable=wildcard-import, unused-wildcard-import, import-error
import logging
import typing

from media_storage_plugins import *  # noqa: F403 F401
import pytest


logger = logging.getLogger(__name__)


class FakeMdsContext:
    def __init__(self):
        self._storage = {}

    def get_size(self, bucket):
        return len(self._storage.get(bucket, {}))

    def put_object(self, bucket, key, body):
        self._storage.setdefault(bucket, {})
        self._storage[bucket][key] = bytearray(body)

    def get_object(self, bucket, key) -> bytearray:
        return self._storage.get(bucket, {}).get(key)

    def delete_object(self, bucket, key) -> typing.Optional[bytearray]:
        return self._storage.get(bucket, {}).pop(key, None)


@pytest.fixture(name='mds_s3')
def _mds_s3(mockserver):
    context = FakeMdsContext()

    @mockserver.handler('/mds-s3-secret', prefix=True)
    def _mock_secret(request):
        return _process('secret', request)

    @mockserver.handler('/mds-s3-public', prefix=True)
    def _mock_public(request):
        return _process('public', request)

    def _process(bucket, request):
        _, _, path = request.path.split('/', 2)
        if request.method == 'PUT':
            context.put_object(bucket, path, request.get_data())
            return mockserver.make_response('OK', 200)
        if request.method == 'GET':
            data = context.get_object(bucket, path)
            if data:
                return mockserver.make_response(data, 200)
            return mockserver.make_response('NotFound', 404)
        if request.method == 'DELETE':
            data = context.delete_object(bucket, path)
            if data:
                return mockserver.make_response(status=204)
            return mockserver.make_response('NotFound', 404)

        return mockserver.make_response('Wrong Method', 400)

    return context


@pytest.fixture(name='avatars')
def avatars_mds_mock(mockserver):
    namespace = 'media-storage'

    def make_put_response(image_name, group_id):
        return {
            'imagename': image_name,
            'group-id': group_id,
            'meta': {'orig-format': 'JPEG'},
            'sizes': {
                'orig': {
                    'height': 640,
                    'path': f'/get-{namespace}/{group_id}/{image_name}/orig',
                    'width': 1024,
                },
                'sizename': {
                    'height': 200,
                    'path': (
                        f'/get-{namespace}/{group_id}/{image_name}/sizename'
                    ),
                    'width': 200,
                },
            },
        }

    class Context:
        def __init__(self):
            self.group_id = 123
            self.media = set()

        def set_group_id(self, group_id):
            self.group_id = group_id

        def add_media(self, image_name, group_id=None):
            if group_id is None:
                group_id = self.group_id
            logger.debug(f'Avatars: add {group_id}_{image_name}')
            self.media.add(f'{group_id}_{image_name}')

        def delete_media(self, image_name, group_id=None):
            if group_id is None:
                group_id = self.group_id
            logger.debug(f'Avatars: delete {group_id}_{image_name}')
            self.media.remove(f'{group_id}_{image_name}')

    context = Context()

    @mockserver.json_handler(
        fr'/avatars-mds/put-{namespace}/(?P<image_name>\w+)', regex=True,
    )
    def _mock_put_named_handler(request, image_name):
        context.add_media(image_name)
        return make_put_response(image_name, context.group_id)

    @mockserver.handler(
        fr'/avatars-mds/delete-{namespace}/(?P<group_id>\w+)/(?P<image_name>\w+)',  # noqa: E501
        regex=True,
    )
    def _mock_delete_named_handler(request, group_id, image_name):
        context.delete_media(image_name, group_id)
        return mockserver.make_response('OK', 200)

    return context
