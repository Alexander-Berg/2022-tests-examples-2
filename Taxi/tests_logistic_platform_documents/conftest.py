import typing as tp

import pytest

# pylint: disable=wildcard-import, unused-wildcard-import, import-error
from logistic_platform_documents_plugins import *  # noqa: F403 F401


@pytest.fixture(name='get_notification', autouse=True)
def _get_notification(mockserver):
    @mockserver.json_handler(
        '/logistic-platform-uservices/api/internal/documents/notify_task',  # noqa E501
    )
    def get_notification(request):
        return {'message': 'OK'}

    return get_notification


@pytest.fixture(name='s3_storage', autouse=True)
def _s3_storage():
    class FakeMdsClient:
        def __init__(self) -> None:
            self._storage: tp.Dict[str, bytearray] = {
                '/mds-s3/report_some_employer/already_done.csv': bytearray(
                    b'some file',
                ),
                '/mds-s3/report_some_employer/already_done.zip': bytearray(
                    b'some file',
                ),
            }

        def put_object(self, key, body):
            assert key.startswith('/mds-s3'), key
            self._storage[key] = body

        def get_object(self, key) -> tp.Optional[bytearray]:
            assert key.startswith('/mds-s3'), key
            return self._storage.get(key)

        def delete_object(self, key) -> bool:
            assert key.startswith('/mds-s3'), key
            return True

    client = FakeMdsClient()
    return client


@pytest.fixture(name='s3_mock', autouse=True)
def _s3_mock(mockserver, s3_storage):
    @mockserver.handler('/mds-s3', prefix=True)
    def _mock_all(request):
        if request.method == 'GET':
            data = s3_storage.get_object(request.path)
            if data is None:
                return mockserver.make_response(
                    f'Not found with key {request.path}', 404,
                )
            return mockserver.make_response(data, 200)
        if request.method == 'PUT':
            s3_storage.put_object(request.path, request.get_data())
            return mockserver.make_response('OK', 200)
        if request.method == 'DELETE':
            data = s3_storage.delete_object(request.path)
            if data:
                return mockserver.make_response('OK', 200)
        return mockserver.make_response('Not found or invalid method', 404)
