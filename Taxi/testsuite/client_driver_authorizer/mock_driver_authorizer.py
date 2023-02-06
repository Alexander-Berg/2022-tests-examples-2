import json

import pytest


SESSION_HEADER = 'X-Driver-Session'
TAXIMETER = 'taximeter'
_SESSION_MARKER = 'driver_session'


def driver_session_key(park_id, session):
    return 'DriverSession:P' + park_id + ':S' + session


def driver_key(park_id, uuid, driver_app_profile_id):
    key = 'Driver:P' + park_id + ':U' + uuid
    if driver_app_profile_id is not None:
        if driver_app_profile_id != uuid:
            key = key + ':A' + driver_app_profile_id
    return key


class SessionGenerator:
    def __init__(self):
        self.counter = 0

    def generate(self):
        self.counter += 1
        return 'session' + str(self.counter)


class DriverAuthorizerContext:
    def __init__(self):
        self.sessions = {}
        self.drivers = {}
        self.session_generator = SessionGenerator()

    # returns a session - new or updated
    def create_client_session(
            self, client_id, park_id, driver_id, driver_app_profile_id=None,
    ):
        key = driver_key(park_id, driver_id, driver_app_profile_id)
        if key not in self.drivers:
            self.drivers[key] = self.session_generator.generate()
        return self.drivers[key]

    def create_session(self, park_id, driver_id, driver_app_profile_id=None):
        return self.create_client_session(
            TAXIMETER, park_id, driver_id, driver_app_profile_id,
        )

    def set_client_session(
            self,
            client_id,
            park_id,
            session,
            driver_id,
            driver_app_profile_id=None,
            yandex_uid=None,
    ):
        self.sessions[driver_session_key(park_id, session)] = {
            'client_id': client_id,
            'driver_id': driver_id,
            'driver_app_profile_id': driver_app_profile_id,
            'yandex_uid': yandex_uid,
        }
        self.drivers[
            driver_key(park_id, driver_id, driver_app_profile_id)
        ] = session

    def set_session(self, db, session, driver_id, driver_app_profile_id=None):
        self.set_client_session(
            TAXIMETER, db, session, driver_id, driver_app_profile_id,
        )

    def get_uuid(self, park_id, session):
        session_key = driver_session_key(park_id, session)
        if session_key in self.sessions:
            return self.sessions[session_key]['driver_id']
        return ''

    def get_client_id(self, park_id, session):
        session_key = driver_session_key(park_id, session)
        if session_key in self.sessions:
            return self.sessions[session_key]['client_id']
        return ''

    def get_driver_app_profile_id(self, park_id, session):
        session_key = driver_session_key(park_id, session)
        if session_key in self.sessions:
            if self.sessions[session_key]['driver_app_profile_id'] is not None:
                return self.sessions[session_key]['driver_app_profile_id']
        return self.get_uuid(park_id, session)

    def get_session(self, park_id, driver_id, driver_app_profile_id=None):
        key = driver_key(park_id, driver_id, driver_app_profile_id)
        if key in self.drivers:
            return self.drivers[key]
        return ''

    def delete_session(self, park_id, driver_id, driver_app_profile_id=None):
        key = driver_key(park_id, driver_id, driver_app_profile_id)
        if key in self.drivers:
            session = self.drivers[key]
            session_key = driver_session_key(park_id, session)
            if session_key in self.sessions:
                self.sessions.pop(session_key)
            self.drivers.pop(key)


def pytest_configure(config):
    config.addinivalue_line('markers', f'{_SESSION_MARKER}: driver session')


@pytest.fixture(name='driver_authorizer')
def _driver_authorizer(mockserver, request):
    context = DriverAuthorizerContext()
    context.set_session('test_db', 'test_session', 'test_uuid')

    def _get_mock_session(park_id, session):
        markers = request.node.iter_markers(_SESSION_MARKER)
        for marker in markers:
            if (
                    session == marker.kwargs['session']
                    and park_id == marker.kwargs['park_id']
            ):
                return (
                    marker.kwargs['uuid'],
                    marker.kwargs.get('driver_app_profile_id', ''),
                    marker.kwargs.get('client_id', 'taximeter'),
                    marker.kwargs.get('yandex_uid', ''),
                    marker.kwargs.get('eats_courier_id'),
                )
        return '', '', '', '', ''

    def _make_error_response(mockserver, message, status):
        return mockserver.make_response(
            response=json.dumps({'message': message}), status=status,
        )

    @mockserver.json_handler('/driver-authorizer/driver_session')
    def _mock_driver_authorizer_driver_session(request):
        park_id = request.args.get('db')
        session = request.args.get('session')
        if not park_id or not session:
            return _make_error_response(mockserver, 'empty param', 400)
        uuid = context.get_uuid(park_id, session)
        if uuid == '':
            uuid, _, _, _, _ = _get_mock_session(park_id, session)
        if uuid == '':
            return _make_error_response(mockserver, 'unauthorized', 401)
        return {'uuid': uuid}

    @mockserver.json_handler('/driver-authorizer/driver/sessions/check')
    def _mock_driver_authorizer_driver_sessions_check(request):
        req = request.json
        client_id = req.get('client_id')
        park_id = req['park_id']
        session = request.headers[SESSION_HEADER]
        if not session:
            return _make_error_response(mockserver, 'empty param', 400)
        uuid = context.get_uuid(park_id, session)
        yandex_uid = ''
        eats_courier_id = None
        if uuid == '':
            (
                uuid,
                driver_app_profile_id,
                stored_client_id,
                yandex_uid,
                eats_courier_id,
            ) = _get_mock_session(park_id, session)
        else:
            stored_client_id = context.get_client_id(park_id, session)
        if uuid == '':
            return _make_error_response(mockserver, 'unauthorized', status=401)

        if client_id and stored_client_id != client_id:
            return _make_error_response(mockserver, 'client_id mismatch', 401)

        driver_app_profile_id = context.get_driver_app_profile_id(
            park_id, session,
        )
        data = {
            'ttl': 3600,
            'uuid': uuid,
            'driver_app_profile_id': driver_app_profile_id,
            'client_id': stored_client_id,
        }
        if yandex_uid:
            data['yandex_uid'] = yandex_uid
        if eats_courier_id:
            data['eats_courier_id'] = eats_courier_id
        return mockserver.make_response(
            response=json.dumps(data), headers={SESSION_HEADER: session},
        )

    def _mock_driver_authorizer_get_session(context, request):
        park_id = request.args.get('park_id')
        driver_id = request.args.get('uuid')
        driver_app_profile_id = request.args.get('driver_app_profile_id')
        if not driver_id:
            return _make_error_response(mockserver, 'empty param', 400)
        session = context.get_session(
            park_id, driver_id, driver_app_profile_id,
        )
        if session == '':
            return _make_error_response(mockserver, 'session not found', 404)
        return mockserver.make_response(
            json.dumps({'ttl': 3600}),
            status=200,
            headers={SESSION_HEADER: session},
        )

    def _mock_driver_authorizer_create_session(context, request):
        client_id = request.args.get('client_id')
        park_id = request.args.get('park_id')
        driver_id = request.args.get('uuid')
        driver_app_profile_id = request.args.get('driver_app_profile_id')
        if not client_id or not driver_id:
            return _make_error_response(mockserver, 'empty param', 400)
        session = context.create_client_session(
            client_id, park_id, driver_id, driver_app_profile_id,
        )
        return mockserver.make_response(
            json.dumps({'ttl': 3600}),
            status=200,
            headers={SESSION_HEADER: session},
        )

    def _mock_driver_authorizer_delete_session(context, request):
        park_id = request.args.get('park_id')
        driver_id = request.args.get('uuid')
        driver_app_profile_id = request.args.get('driver_app_profile_id')
        if not driver_id:
            return _make_error_response(mockserver, 'empty param', 400)
        context.delete_session(park_id, driver_id, driver_app_profile_id)
        return mockserver.make_response(json.dumps({}), status=200)

    @mockserver.json_handler('/driver-authorizer/driver/sessions')
    def _mock_driver_authorizer_driver_sessions_check2(request):
        if request.method == 'GET':
            return _mock_driver_authorizer_get_session(context, request)
        if request.method == 'PUT':
            return _mock_driver_authorizer_create_session(context, request)
        if request.method == 'DELETE':
            return _mock_driver_authorizer_delete_session(context, request)
        return mockserver.make_response('Wrong method', status=405)

    return context
