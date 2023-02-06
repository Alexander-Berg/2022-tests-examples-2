# pylint: disable=wildcard-import, unused-wildcard-import, import-error, C0411
import pytest
from rescue_plugins import *  # noqa: F403 F401


DEFAULT = '__default__'


DEFAULT_PERSONAL_RESPONSE = {'value': '123', 'id': '123'}
DEFAULT_DRIVER_PROFILES_RESPONSE = {
    'profiles': [
        {
            'park_driver_profile_id': 'db1_uuid1',
            'data': {'phone_pd_ids': [{'pd_id': '123'}]},
        },
    ],
}


class ApiTrackerContext:
    def __init__(self):
        self.response = {DEFAULT: {}}
        self.headers = {DEFAULT: {}}
        self.status = {DEFAULT: 201}

    def set_response(self, response, headers=None, handler=DEFAULT):
        self.response[handler] = response
        self.status[handler] = 201
        self.headers[handler] = headers

    def set_error(self, status=500, headers=None, handler=DEFAULT):
        self.response[handler] = dict(statusCode=status, errorMessages=[])
        self.status[handler] = status
        self.headers[handler] = headers


@pytest.fixture(name='api_tracker', autouse=True)
def api_tracker_request(mockserver):
    context = ApiTrackerContext()

    @mockserver.json_handler('/taxi-api-tracker/v2/issues')
    def _issues(request):
        handler = 'v2/issues'
        return mockserver.make_response(
            json=context.response.get(handler, context.response[DEFAULT]),
            status=context.status.get(handler, context.status[DEFAULT]),
            headers=context.headers.get(handler, context.headers[DEFAULT]),
        )

    @mockserver.json_handler('/taxi-api-tracker/v2/attachments')
    def _attachments(request):
        handler = 'v2/attachments'
        response = context.response.get(handler, context.response[DEFAULT])
        status = context.status.get(handler, context.status[DEFAULT])
        headers = context.headers.get(handler, context.headers[DEFAULT])
        if status == 201:
            response.update(dict(name=request.query['filename']))
        return mockserver.make_response(
            json=response, status=status, headers=headers,
        )

    @mockserver.json_handler('/taxi-api-tracker/v2/issues/', prefix=True)
    def _comments(request):
        handler = 'v2/issues/{issue}/comments'
        return mockserver.make_response(
            json=context.response.get(handler, context.response[DEFAULT]),
            status=context.status.get(handler, context.status[DEFAULT]),
            headers=context.headers.get(handler, context.headers[DEFAULT]),
        )

    return context


class FakeMdsContext:
    error = None
    _storage: dict = {}

    def put_object(self, bucket, key, body, *args, **kwargs):
        self._storage.setdefault(bucket, {})
        self._storage[bucket][key] = bytearray(body)

    def get_object(self, bucket, key) -> bytearray:
        return self._storage.get(bucket, {}).get(key)

    def set_error(self, error):
        self.error = error


@pytest.fixture(name='mds_s3', autouse=True)
def mds_s3_client(mockserver):
    context = FakeMdsContext()

    @mockserver.handler('/mds-s3', prefix=True)
    def _mock_mds_s3(request):
        if context.error:
            return mockserver.make_response(
                f'Error {context.error}', context.error,
            )
        _, _, bucket, path = request.path.split('/', 3)
        if request.method == 'PUT':
            context.put_object(bucket, path, request.get_data())
            return mockserver.make_response('OK', 200)
        if request.method == 'GET':
            data = context.get_object(bucket, path)
            if data:
                return mockserver.make_response(data, 200)
        return mockserver.make_response('NotFound', 404)

    return context


class DriverProfilesContext:
    def __init__(self):
        self.response = DEFAULT_DRIVER_PROFILES_RESPONSE
        self.status = 200

    def set_response(self, response, status=200):
        self.response = response
        self.status = status

    def set_error(self, status=500):
        self.response = dict(code=str(status), message='error')
        self.status = status


@pytest.fixture(name='driver_profiles', autouse=True)
def driver_profiles_request(mockserver):
    context = DriverProfilesContext()

    @mockserver.json_handler('/driver-profiles/v1/driver/profiles/retrieve')
    def _retrieve(request):
        return mockserver.make_response(
            json=context.response, status=context.status,
        )

    return context


class PersonalContext:
    def __init__(self):
        self.response = DEFAULT_PERSONAL_RESPONSE
        self.status = 200

    def set_response(self, response, status=200):
        self.response = response
        self.status = status

    def set_error(self, status=500):
        self.response = dict(code=str(status), message='error')
        self.status = status


@pytest.fixture(name='personal', autouse=True)
def personal_request(mockserver):
    context = PersonalContext()

    @mockserver.json_handler('/personal/v1/phones/retrieve')
    def _phones_retrieve(request):
        return mockserver.make_response(
            json=context.response, status=context.status,
        )

    return context


class OrderCoreContext:
    def __init__(self):
        self.response = {}
        self.status = 200

    def set_response(self, response, status=200):
        self.response = response
        self.status = status

    def set_error(self, status=500):
        self.response = dict(code=str(status), message='error')
        self.status = status


@pytest.fixture(name='order_core', autouse=True)
def order_core_request(mockserver):
    context = OrderCoreContext()

    @mockserver.json_handler('/order-core/v1/tc/order-fields')
    def _fields_retrieve(request):
        return mockserver.make_response(
            json=context.response, status=context.status,
        )

    return context


class FakeMediaStorageContext:
    error = None
    _storage: dict = {}

    def store_object(self, media_id):
        self._storage[media_id] = True

    def get_object(self, media_id):
        return media_id in self._storage

    def set_error(self, error):
        self.error = error

    def delete_object(self, media_id):
        del self._storage[media_id]


@pytest.fixture(name='media_storage', autouse=True)
def media_storage_client(mockserver):
    context = FakeMediaStorageContext()

    @mockserver.handler(
        '/media-storage/service/sos-audio/v1/store', prefix=True,
    )
    def _mock_store(request):
        if context.error:
            return mockserver.make_response(
                f'Error {context.error}', context.error,
            )
        token = request.headers['X-Idempotency-Token']
        context.store_object(token)
        return mockserver.make_response(
            json={'id': token, 'version': token}, status=200,
        )

    @mockserver.handler(
        '/media-storage/service/sos-audio/v1/retrieve', prefix=True,
    )
    def _mock_retrieve(request):
        if context.error:
            return mockserver.make_response(
                f'Error {context.error}', context.error,
            )
        media_id = request.query['id']
        if context.get_object(media_id):
            return mockserver.make_response(
                json={'url': 'some_url', 'version': media_id}, status=200,
            )
        return mockserver.make_response('NotFound', 404)

    @mockserver.handler(
        '/media-storage/service/sos-audio/v1/delete', prefix=True,
    )
    def _mock_delete(request):
        if context.error:
            return mockserver.make_response(
                f'Error {context.error}', context.error,
            )
        media_id = request.query['id']
        if context.get_object(media_id):
            context.delete_object(media_id)
            return mockserver.make_response(json={'deleted': 1}, status=200)
        return mockserver.make_response(
            json={'code': 'NOT_FOUND', 'message': 'Not found.'}, status=404,
        )

    return context
