import json
import random
import string

import pytest


SESSION_HEADER = 'X-Driver-Session'
TAXIMETER = 'taximeter'


def driver_session_key(client_id, park_id, session):
    return 'DriverSession:C' + client_id + ':P' + park_id + ':S' + session


def driver_key(client_id, park_id, uuid):
    return 'Driver:C' + client_id + ':P' + park_id + ':U' + uuid


def generate(ses_len=16):
    letters = string.hexdigits
    return ''.join(random.choice(letters) for i in range(ses_len))


class DriverAuthorizerContext:
    def __init__(self):
        self.sessions = {}
        self.drivers = {}

    # returns session - new or updated
    def create_client_session(self, client_id, park_id, driver_id):
        key = driver_key(client_id, park_id, driver_id)
        if key not in self.drivers:
            self.drivers[key] = generate()
        return self.drivers[key]

    def create_session(self, park_id, driver_id):
        return self.create_client_session(TAXIMETER, park_id, driver_id)

    def set_client_session(self, client_id, park_id, session, driver_id):
        self.sessions[
            driver_session_key(client_id, park_id, session)
        ] = driver_id
        self.drivers[driver_key(client_id, park_id, driver_id)] = session

    def set_session(self, db, session, driver_id):
        self.set_client_session(TAXIMETER, db, session, driver_id)

    def get_client_uuid(self, client_id, park_id, session):
        session_key = driver_session_key(client_id, park_id, session)
        if session_key in self.sessions:
            return self.sessions[session_key]
        return ''

    def get_uuid(self, park_id, session):
        return self.get_client_uuid(TAXIMETER, park_id, session)

    def get_client_session(self, client_id, park_id, driver_id):
        key = driver_key(client_id, park_id, driver_id)
        if key in self.drivers:
            return self.drivers[key]
        return ''

    def get_session(self, park_id, driver_id):
        return self.get_client_session(TAXIMETER, park_id, driver_id)

    def delete_client_session(self, client_id, park_id, driver_id):
        key = driver_key(client_id, park_id, driver_id)
        if key in self.drivers:
            session = self.drivers[key]
            session_key = driver_session_key(client_id, park_id, session)
            if session_key in self.sessions:
                self.sessions.pop(session_key)
            self.drivers.pop(key)

    def delete_session(self, park_id, driver_id):
        self.delete_client_session(TAXIMETER, park_id, driver_id)


@pytest.fixture
def driver_authorizer_service(mockserver):
    context = DriverAuthorizerContext()
    context.set_session('test_db', 'test_session', 'a000000000000000')

    def mock_driver_authorizer_driver_session(context, request):
        db = request.args.get('db')
        session = request.args.get('session')
        uuid = context.get_uuid(db, session)
        if uuid == '':
            return mockserver.make_response('unauthorized', 401)
        return {'uuid': uuid}

    @mockserver.json_handler(
        '/driver-authorizer.taxi.yandex.net/driver_session',
    )
    def mock_driver_authorizer(request):
        return mock_driver_authorizer_driver_session(context, request)

    @mockserver.json_handler(
        '/driver-authorizer.taxi.yandex.net/driver/sessions/check',
    )
    def mock_driver_authorizer_driver_sessions_check(request):
        req = json.loads(request.get_data(as_text=True))
        client_id = req['client_id']
        park_id = req['park_id']
        session = request.headers[SESSION_HEADER]
        uuid = context.get_client_uuid(client_id, park_id, session)
        if uuid == '':
            return mockserver.make_response('unauthorized', 401)
        return {'uuid': uuid, 'ttl': 3600}

    def mock_driver_authorizer_get_session(context, request):
        client_id = request.args.get('client_id')
        park_id = request.args.get('park_id')
        driver_id = request.args.get('uuid')
        # process BadRequest ?
        session = context.get_client_session(client_id, park_id, driver_id)
        if session == '':
            return mockserver.make_response(
                json.dumps({'message': 'session not found'}), status=404,
            )
        return mockserver.make_response(
            json.dumps({'ttl': 3600}),
            status=200,
            headers={SESSION_HEADER: session},
        )

    def mock_driver_authorizer_create_session(context, request):
        client_id = request.args.get('client_id')
        park_id = request.args.get('park_id')
        driver_id = request.args.get('uuid')
        # process BadRequest ?
        session = context.create_client_session(client_id, park_id, driver_id)
        return mockserver.make_response(
            json.dumps({'ttl': 3600}),
            status=200,
            headers={SESSION_HEADER: session},
        )

    def mock_driver_authorizer_delete_session(context, request):
        client_id = request.args.get('client_id')
        park_id = request.args.get('park_id')
        driver_id = request.args.get('uuid')
        # process BadRequest?
        context.delete_client_session(client_id, park_id, driver_id)
        return mockserver.make_response(status=200)

    @mockserver.json_handler(
        '/driver-authorizer.taxi.yandex.net/driver/sessions',
    )
    def mock_driver_authorizer_driver_sessions_check2(request):
        if request.method == 'GET':
            return mock_driver_authorizer_get_session(context, request)
        if request.method == 'PUT':
            return mock_driver_authorizer_create_session(context, request)
        if request.method == 'DELETE':
            return mock_driver_authorizer_delete_session(context, request)
        return mockserver.make_response('Wrong method', status=405)

    def bulk_json(park_id, driver_id, client_id):
        session = context.get_client_session(client_id, park_id, driver_id)
        if not session:
            return {
                'client_id': client_id,
                'status': 'not_found',
                'park_id': park_id,
                'uuid': driver_id,
            }
        return {
            'client_id': client_id,
            'status': 'ok',
            'session': session,
            'park_id': park_id,
            'uuid': driver_id,
        }

    @mockserver.handler(
        '/driver-authorizer.taxi.yandex.net/driver/sessions/bulk_retrieve',
    )
    def mock_driver_authorizer_driver_sessions_bulk_retrieve(request):
        if request.method != 'POST':
            return mockserver.make_response('POST required', status=405)
        body = {'sessions': []}

        reqs = json.loads(request.get_data(as_text=True))
        assert 'drivers' in reqs
        for req in reqs['drivers']:
            assert 'park_id' in req
            assert 'uuid' in req
            client_id = req.get('client_id', 'taximeter')
            body['sessions'].append(
                bulk_json(req['park_id'], req['uuid'], client_id),
            )
        return mockserver.make_response(json.dumps(body), status=200)

    return context
