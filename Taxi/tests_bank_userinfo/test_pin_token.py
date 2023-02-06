import jwt
import pytest
import re

from tests_bank_userinfo import common
from tests_bank_userinfo import utils
from bank_testing.pg_state import PgState, Arbitrary

REGEX_UUID_V4 = re.compile(
    r'^[a-f0-9]{8}-?[a-f0-9]{4}-?4[a-f0-9]{3}-?[89ab][a-f0-9]{3}-?[a-f0-9]{12}\Z',  # noqa
    re.I,
)
REGEX_16BYTES_BASE64 = re.compile(r'^[A-Za-z0-9+/]{21}[AQgw]\Z')

UID = '024e7db5-9bd6-4f45-a1cd-2a442e15bdc1'
BUID = '7948e3a9-623c-4524-a390-9e4264d27a77'
PHONE_ID = '024e7db5-9bd6-4f45-a1cd-2a442e15bdf1'
DEVICE_ID = 'my_device_id'


def mess_base64(msg, shift=1):
    alphabet = (
        'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/'
    )
    trans = str.maketrans(alphabet, alphabet[shift:] + alphabet[:shift])
    return chr(trans[ord(msg[0])]) + msg[1:]


def passport_only_headers(session_uuid=None):
    headers = common.get_headers(
        uid=UID, phone_id=PHONE_ID, session_uuid=session_uuid,
    )
    headers['X-YaBank-AuthorizedByAuthproxy'] = 'yes'
    return headers


def authorized_headers(
        session_uuid, idempotency_token=None, verification_token=None,
):
    return customer_headers(
        session_status=common.SESSION_STATUS_OK,
        session_uuid=session_uuid,
        verification_token=verification_token,
        idempotency_token=idempotency_token,
    )


def customer_headers(
        session_uuid,
        session_status,
        idempotency_token=None,
        verification_token=None,
):
    headers = common.get_headers(
        uid=UID,
        buid=BUID,
        phone_id=PHONE_ID,
        session_uuid=session_uuid,
        verification_token=verification_token,
        idempotency_token=idempotency_token,
    )
    headers['X-Ya-User-Ticket'] = 'user_ticket_1'
    if session_status != common.SESSION_STATUS_OK:
        headers['X-YaBank-AuthorizedByAuthproxy'] = 'no'
    headers['X-YaBank-SessionStatus'] = session_status
    return headers


def create_pin_pgstate(pgsql):
    pgstate = PgState(pgsql, 'bank_userinfo')
    pgstate.add_table(
        'bank_userinfo.pin_adoptions',
        'version',
        ['version', 'buid', 'pin_adopted', 'created_at'],
        alias='adoptions',
        defaults={'created_at': Arbitrary()},
    )
    pgstate.add_table(
        'bank_userinfo.pin_token_requests',
        'id',
        [
            'id',
            'buid',
            'device_id',
            'app_type',
            'idempotency_token',
            'track_id',
            'status',
            'created_at',
        ],
        alias='requests',
        defaults={'created_at': Arbitrary()},
    )
    pgstate.add_table(
        'bank_userinfo.pin_tokens',
        'id',
        [
            'id',
            'value',
            'buid',
            'device_id',
            'app_type',
            'idempotency_token',
            'request_id',
            'failed_attempts',
            'status',
            'status_reason',
            'created_at',
        ],
        alias='tokens',
        defaults={'created_at': Arbitrary()},
    )
    return pgstate


@pytest.fixture(name='mock_bank_authorization')
def _mock_bank_authorization(mockserver):
    class BankAuthorizationMock:
        @mockserver.json_handler(
            '/bank-authorization/authorization-internal/v1/create_track',
        )
        @staticmethod
        async def create_track(request):
            return {
                'track_id': request.headers['X-Idempotency-Token'] + '-track',
            }

    return BankAuthorizationMock()


@pytest.mark.config(BANK_AUTHORIZATION_JWT_PUBLIC_KEYS=common.JWT_PUBLIC_KEYS)
@pytest.mark.experiments3(filename='exp_require_pin.json')
async def test_happy_path_unauthorized_with_auth(
        taxi_bank_userinfo,
        pgsql,
        mock_bank_authorization,
        bank_applications,
        stq,
):
    db = create_pin_pgstate(pgsql)
    db.assert_valid()

    # -------- Request 0: try start session without pin token --------
    headers = passport_only_headers()
    response = await taxi_bank_userinfo.post(
        '/v1/userinfo/v1/start_session',
        json={'antifraud_info': {'device_id': 'my_device_id'}},
        headers=headers,
    )
    assert response.status_code == 200
    resp = response.json()
    session_uuid = resp['yabank_session_uuid']
    assert resp == {
        'action': common.ACTION_PIN_TOKEN_REISSUE,
        'yandex_uid': UID,
        'yabank_session_uuid': session_uuid,
    }
    db.assert_valid()
    session = utils.select_session(pgsql, session_uuid)
    assert session.pin_token_id is None

    # -------- Request 1: fetch auth track --------
    for iter in range(3):
        session = utils.select_session(pgsql, session_uuid)
        assert session.status == common.SESSION_STATUS_PIN_TOKEN_REISSUE
        headers = customer_headers(
            session_uuid, session.status, idempotency_token='req1',
        )
        response = await taxi_bank_userinfo.post(
            '/v1/userinfo/v1/issue_pin_token',
            json={'device_id': DEVICE_ID},
            headers=headers,
        )
        assert response.status_code == 200
        assert response.json() == {
            'action': 'AUTHORIZATION',
            'authorization_track_id': 'req1-track',
        }
        if iter == 0:
            db.expect_insert(
                'requests',
                {
                    'id': 1,
                    'buid': BUID,
                    'device_id': DEVICE_ID,
                    'app_type': 'default',
                    'idempotency_token': 'req1',
                    'track_id': 'req1-track',
                    'status': 'pending',
                },
            )
        db.assert_valid()
        session = utils.select_session(pgsql, session_uuid)
        assert session.pin_token_id is None

    # -------- Request 2: confirm auth track & receive PIN token --------
    verification_token = jwt.encode(
        {
            'track_id': 'req1-track',
            'verification_result': 'OK',
            'valid_to': '2131-06-13T14:00:00Z',
        },
        common.JWT_PRIVATE_KEY,
        algorithm='PS512',
    )

    prev_id_value = None
    for iter in range(3):
        session = utils.select_session(pgsql, session_uuid)
        assert session.status == common.SESSION_STATUS_PIN_TOKEN_REISSUE
        headers = customer_headers(
            session_uuid,
            session.status,
            idempotency_token='req2',
            verification_token=verification_token,
        )
        response = await taxi_bank_userinfo.post(
            '/v1/userinfo/v1/issue_pin_token',
            json={'device_id': DEVICE_ID},
            headers=headers,
        )
        assert response.status_code == 200
        response_json = response.json()
        token_id = response_json['pin_token']['id']
        assert re.match(REGEX_UUID_V4, token_id)
        token_value = response_json['pin_token']['value']
        assert re.match(REGEX_16BYTES_BASE64, token_value)

        if prev_id_value is not None:
            assert prev_id_value == (token_id, token_value)
        prev_id_value = (token_id, token_value)

        assert response_json == {
            'action': 'NONE',
            'pin_token': {'id': token_id, 'value': token_value},
        }

        if iter == 0:
            db.expect_update('requests', 1, {'status': 'completed'})
            db.expect_insert(
                'tokens',
                {
                    'id': token_id,
                    'value': token_value,
                    'buid': BUID,
                    'device_id': DEVICE_ID,
                    'app_type': 'default',
                    'idempotency_token': 'req2',
                    'request_id': 1,
                    'failed_attempts': 0,
                    'status': 'pending',
                    'status_reason': None,
                },
            )
        db.assert_valid()
        session = utils.select_session(pgsql, session_uuid)
        assert session.pin_token_id is None
    pin_token_id = prev_id_value[0]
    assert stq.bank_userinfo_delete_sessions.times_called == 0

    # -------- Request 3: start using PIN token --------
    headers = passport_only_headers(session_uuid=session_uuid)
    headers['X-PIN-Token'] = prev_id_value[0] + '.' + prev_id_value[1]
    response = await taxi_bank_userinfo.post(
        '/v1/userinfo/v1/start_session',
        json={'antifraud_info': {'device_id': 'my_device_id'}},
        headers=headers,
    )
    assert response.status_code == 200
    resp = response.json()
    session_uuid = resp['yabank_session_uuid']
    assert resp == {
        'action': common.ACTION_NONE,
        'yandex_uid': UID,
        'yabank_session_uuid': session_uuid,
    }

    assert stq.bank_userinfo_delete_sessions.times_called == 0

    db.expect_insert(
        'adoptions', {'version': 1, 'buid': BUID, 'pin_adopted': True},
    )
    db.expect_update('tokens', token_id, {'status': 'active'})
    db.assert_valid()
    session = utils.select_session(pgsql, session_uuid)
    assert session.pin_token_id == pin_token_id


@pytest.mark.config(BANK_AUTHORIZATION_JWT_PUBLIC_KEYS=common.JWT_PUBLIC_KEYS)
@pytest.mark.experiments3(filename='exp_auto_pin.json')
@pytest.mark.experiments3(filename='exp_skip_auth.json')
async def test_happy_path_authorized_without_auth_and_exhaust(
        taxi_bank_userinfo,
        pgsql,
        mock_bank_authorization,
        bank_applications,
        stq,
):
    db = create_pin_pgstate(pgsql)
    db.assert_valid()

    # -------- Request 0: start session without pin token --------
    headers = passport_only_headers()
    response = await taxi_bank_userinfo.post(
        '/v1/userinfo/v1/start_session',
        json={'antifraud_info': {'device_id': 'my_device_id'}},
        headers=headers,
    )
    assert response.status_code == 200
    resp = response.json()
    session_uuid = resp['yabank_session_uuid']
    assert resp == {
        'action': common.ACTION_NONE,
        'yandex_uid': UID,
        'yabank_session_uuid': session_uuid,
    }
    db.assert_valid()
    session = utils.select_session(pgsql, session_uuid)
    assert session.pin_token_id is None

    # -------- Request 1: just receive PIN token --------
    prev_id_value = None
    for iter in range(3):
        headers = authorized_headers(session_uuid, idempotency_token='req2')
        response = await taxi_bank_userinfo.post(
            '/v1/userinfo/v1/issue_pin_token',
            json={'device_id': DEVICE_ID},
            headers=headers,
        )
        assert response.status_code == 200
        response_json = response.json()
        token_id = response_json['pin_token']['id']
        assert re.match(REGEX_UUID_V4, token_id)
        token_value = response_json['pin_token']['value']
        assert re.match(REGEX_16BYTES_BASE64, token_value)

        if prev_id_value is not None:
            assert prev_id_value == (token_id, token_value)
        prev_id_value = (token_id, token_value)

        assert response_json == {
            'action': 'NONE',
            'pin_token': {'id': token_id, 'value': token_value},
        }

        if iter == 0:
            db.expect_insert(
                'tokens',
                {
                    'id': token_id,
                    'value': token_value,
                    'buid': BUID,
                    'device_id': DEVICE_ID,
                    'app_type': 'default',
                    'idempotency_token': 'req2',
                    'request_id': None,
                    'failed_attempts': 0,
                    'status': 'pending',
                    'status_reason': None,
                },
            )
        db.assert_valid()
        session = utils.select_session(pgsql, session_uuid)
        assert session.pin_token_id is None
    pin_token_id = prev_id_value[0]

    # -------- Request 2a: try start using PIN token (wrong PIN) --------
    headers = passport_only_headers(session_uuid=session_uuid)
    headers['X-PIN-Token'] = (
        prev_id_value[0] + '.' + mess_base64(prev_id_value[1])
    )
    response = await taxi_bank_userinfo.post(
        '/v1/userinfo/v1/start_session',
        json={'antifraud_info': {'device_id': 'my_device_id'}},
        headers=headers,
    )
    assert response.status_code == 200
    resp = response.json()
    session_uuid = resp['yabank_session_uuid']
    assert resp == {
        'action': common.ACTION_PIN_TOKEN_RETRY,
        'yandex_uid': UID,
        'yabank_session_uuid': session_uuid,
        'pin_attempts_left': 9,
    }
    db.expect_update(
        'tokens', token_id, {'status': 'active', 'failed_attempts': 1},
    )
    db.assert_valid()
    session = utils.select_session(pgsql, session_uuid)
    assert session.pin_token_id is None
    assert stq.bank_userinfo_delete_sessions.times_called == 0

    # -------- Request 2b: start using PIN token (success) --------
    headers = passport_only_headers(session_uuid=session_uuid)
    headers['X-PIN-Token'] = prev_id_value[0] + '.' + prev_id_value[1]
    response = await taxi_bank_userinfo.post(
        '/v1/userinfo/v1/start_session',
        json={'antifraud_info': {'device_id': 'my_device_id'}},
        headers=headers,
    )
    assert response.status_code == 200
    resp = response.json()
    session_uuid = resp['yabank_session_uuid']
    assert resp == {
        'action': common.ACTION_NONE,
        'yandex_uid': UID,
        'yabank_session_uuid': session_uuid,
    }
    db.expect_insert(
        'adoptions', {'version': 1, 'buid': BUID, 'pin_adopted': True},
    )
    db.expect_update('tokens', token_id, {'failed_attempts': 0})
    db.assert_valid()
    session = utils.select_session(pgsql, session_uuid)
    assert session.pin_token_id == pin_token_id

    assert stq.bank_userinfo_delete_sessions.times_called == 1
    assert stq.bank_userinfo_delete_sessions.next_call()['kwargs'] == {
        'filter': {'buid': BUID, 'pin_token_empty': 'empty'},
        'log_extra': Arbitrary(),
    }

    # -------- Request 2c: try start session without pin token --------
    headers = passport_only_headers()
    response = await taxi_bank_userinfo.post(
        '/v1/userinfo/v1/start_session',
        json={'antifraud_info': {'device_id': 'my_device_id'}},
        headers=headers,
    )
    assert response.status_code == 200
    resp = response.json()
    session_uuid = resp['yabank_session_uuid']
    assert resp == {
        'action': common.ACTION_PIN_TOKEN_REISSUE,
        'yandex_uid': UID,
        'yabank_session_uuid': session_uuid,
    }
    db.assert_valid()
    session = utils.select_session(pgsql, session_uuid)
    assert session.pin_token_id is None

    # -------- Request 3: exhaust attempts --------
    MAX_ATTEMPTS = 10
    for attempts_count in range(1, MAX_ATTEMPTS + 1):
        headers = passport_only_headers(session_uuid=session_uuid)
        headers['X-PIN-Token'] = (
            prev_id_value[0] + '.' + mess_base64(prev_id_value[1])
        )
        response = await taxi_bank_userinfo.post(
            '/v1/userinfo/v1/start_session',
            json={'antifraud_info': {'device_id': 'my_device_id'}},
            headers=headers,
        )
        assert response.status_code == 200
        resp = response.json()
        session_uuid = resp['yabank_session_uuid']
        if attempts_count < MAX_ATTEMPTS:
            assert resp == {
                'action': common.ACTION_PIN_TOKEN_RETRY,
                'yandex_uid': UID,
                'yabank_session_uuid': session_uuid,
                'pin_attempts_left': MAX_ATTEMPTS - attempts_count,
            }
            db.expect_update(
                'tokens', token_id, {'failed_attempts': attempts_count},
            )
            assert stq.bank_userinfo_delete_sessions.times_called == 0
        else:
            assert resp == {
                'action': common.ACTION_PIN_TOKEN_REISSUE,
                'action_reason': 'PIN_TOKEN_REISSUE_TOO_MANY_FAILED_ATTEMPTS',
                'yandex_uid': UID,
                'yabank_session_uuid': session_uuid,
            }
            db.expect_update(
                'tokens',
                token_id,
                {
                    'failed_attempts': attempts_count,
                    'status': 'revoked',
                    'status_reason': 'revoked_too_many_failed_attempts',
                },
            )
            assert stq.bank_userinfo_delete_sessions.times_called == 1
            assert stq.bank_userinfo_delete_sessions.next_call()['kwargs'] == {
                'filter': {'buid': BUID, 'pin_token': pin_token_id},
                'log_extra': Arbitrary(),
            }
        db.assert_valid()
        session = utils.select_session(pgsql, session_uuid)
        assert session.pin_token_id is None


@pytest.mark.pgsql(
    'bank_userinfo',
    files=['pg_bank_userinfo.sql', 'pg_registration_sessions.sql'],
)
@pytest.mark.experiments3(filename='exp_require_pin.json')
@pytest.mark.parametrize(
    'session_uuid',
    [
        pytest.param(
            '00000000-0000-0000-0000-000000000001', id='NOT_REGISTERED',
        ),
        pytest.param(
            '00000000-0000-0000-0000-000000000002',
            id='REQUIRED_APPLICATION_IN_PROGRESS',
        ),
    ],
)
async def test_registration(
        taxi_bank_userinfo, pgsql, bank_applications, session_uuid,
):
    headers = passport_only_headers(session_uuid=session_uuid)
    response = await taxi_bank_userinfo.post(
        '/v1/userinfo/v1/start_session',
        json={'antifraud_info': {'device_id': 'my_device_id'}},
        headers=headers,
    )
    assert response.status_code == 200
    resp = response.json()
    session_uuid = resp['yabank_session_uuid']
    assert resp == {
        'action': common.ACTION_PIN_TOKEN_REISSUE,
        'action_reason': 'PIN_TOKEN_REISSUE_REGISTRATION',
        'yandex_uid': UID,
        'yabank_session_uuid': session_uuid,
    }

    session = utils.select_session(pgsql, session_uuid)
    assert session.status == common.SESSION_STATUS_PIN_TOKEN_REGISTRATION


@pytest.mark.parametrize(
    'session_status',
    [
        common.SESSION_STATUS_OK,
        common.SESSION_STATUS_PIN_TOKEN_REISSUE,
        common.SESSION_STATUS_PIN_TOKEN_RETRY,
        common.SESSION_STATUS_PIN_TOKEN_REGISTRATION,
    ],
)
async def test_issue_pin_token_access_allowed(
        taxi_bank_userinfo, pgsql, mock_bank_authorization, session_status,
):
    headers = customer_headers(
        session_status=session_status,
        session_uuid='f1fba9fd-012b-4b3d-8b60-032d203a284f',
        idempotency_token='22b24cac-bee2-401b-bc4f-03754b18fef1',
    )
    response = await taxi_bank_userinfo.post(
        '/v1/userinfo/v1/issue_pin_token',
        json={'device_id': DEVICE_ID},
        headers=headers,
    )
    assert response.json() == {
        'action': 'AUTHORIZATION',
        'authorization_track_id': '22b24cac-bee2-401b-bc4f-03754b18fef1-track',
    }
    assert response.status_code == 200


@pytest.mark.parametrize(
    'session_status',
    [
        common.SESSION_STATUS_INVALID_TOKEN,
        common.SESSION_STATUS_BANNED,
        common.SESSION_STATUS_ACCOUNT_RECOVERY_REQUIRED,
        common.SESSION_STATUS_APP_UPDATE_REQUIRED,
        common.SESSION_STATUS_BANK_PHONE_WITHOUT_BUID,
        common.SESSION_STATUS_BANK_RISK_DENY,
        common.SESSION_STATUS_NO_PRODUCT,
        common.SESSION_STATUS_NOT_AUTHORIZED,
        common.SESSION_STATUS_NOT_REGISTERED,
        common.SESSION_STATUS_PHONE_RECOVERY_REQUIRED,
        common.SESSION_STATUS_PIN_TOKEN_CLEAR,
        common.SESSION_STATUS_REQUIRED_APPLICATION_IN_PROGRESS,
        common.SESSION_STATUS_SPEND_ALL_ATTEMPTS_TO_VERIFY_CODE,
    ],
)
async def test_issue_pin_token_access_denied(
        taxi_bank_userinfo, pgsql, mock_bank_authorization, session_status,
):
    headers = customer_headers(
        session_status=session_status,
        session_uuid='f1fba9fd-012b-4b3d-8b60-032d203a284f',
        idempotency_token='22b24cac-bee2-401b-bc4f-03754b18fef1',
    )
    response = await taxi_bank_userinfo.post(
        '/v1/userinfo/v1/issue_pin_token',
        json={'device_id': DEVICE_ID},
        headers=headers,
    )
    assert response.json() == {
        'code': 'Unauthorized',
        'message': 'Not authorized by authproxy',
    }
    assert response.status_code == 401


@pytest.mark.parametrize(
    'session_status, session_auth, issue_type',
    [
        (common.SESSION_STATUS_OK, True, 'voluntarily'),
        (common.SESSION_STATUS_PIN_TOKEN_REISSUE, True, 'start_session'),
        (common.SESSION_STATUS_PIN_TOKEN_RETRY, True, 'start_session'),
        (common.SESSION_STATUS_PIN_TOKEN_REGISTRATION, False, 'registration'),
    ],
)
@pytest.mark.parametrize(
    'risk_code, risk_body, risk_auth',
    [
        (
            200,
            {
                'resolution': 'ALLOW',
                'action': [],
                'af_decision_id': '04f05d2e-6139-3436-3166-663863363864',
            },
            False,
        ),
        (
            200,
            {
                'resolution': 'ALLOW',
                'action': ['2fa'],
                'af_decision_id': '04f05d2e-6139-3436-3166-663863363864',
            },
            True,
        ),
        (500, {'code': 'error', 'message': 'oops'}, None),
    ],
)
@pytest.mark.experiments3(filename='exp_risk_auth.json')
async def test_issue_pin_token_risk(
        taxi_bank_userinfo,
        pgsql,
        mockserver,
        mock_bank_authorization,
        risk_code,
        risk_body,
        risk_auth,
        session_status,
        session_auth,
        issue_type,
):
    @mockserver.json_handler('/bank-risk/risk/calculation/pin_request')
    async def risk_calculation_pin_request(request):
        timestamp = request.json['timestamp']
        assert request.json == {
            'buid': BUID,
            'device_id': DEVICE_ID,
            'ip': '',
            'session_id': 'f1fba9fd-012b-4b3d-8b60-032d203a284f',
            'timestamp': timestamp,
            'type': issue_type,
            'yandex_uid': UID,
        }

        return mockserver.make_response(status=risk_code, json=risk_body)

    expected_auth = session_auth if risk_auth is None else risk_auth
    headers = customer_headers(
        session_status=session_status,
        session_uuid='f1fba9fd-012b-4b3d-8b60-032d203a284f',
        idempotency_token='22b24cac-bee2-401b-bc4f-03754b18fef1',
    )
    response = await taxi_bank_userinfo.post(
        '/v1/userinfo/v1/issue_pin_token',
        json={'device_id': DEVICE_ID},
        headers=headers,
    )
    assert response.status_code == 200
    if expected_auth:
        assert response.json() == {
            'action': 'AUTHORIZATION',
            'authorization_track_id': (
                '22b24cac-bee2-401b-bc4f-03754b18fef1-track'
            ),
        }
    else:
        json = response.json()
        pin_token_id = json.get('pin_token', {}).get('id')
        pin_token_value = json.get('pin_token', {}).get('value')
        assert json == {
            'action': 'NONE',
            'pin_token': {'id': pin_token_id, 'value': pin_token_value},
        }
