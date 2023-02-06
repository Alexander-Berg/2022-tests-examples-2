import jwt
import pytest

from tests_bank_card import common
from tests_bank_card import db_helpers

GOOD_TOKEN = jwt.encode(
    {
        'track_id': 'default_track_id',
        'verification_result': 'OK',
        'valid_to': '2131-06-13T14:00:00Z',
    },
    common.JWT_PRIVATE_KEY,
    algorithm='PS512',
)

EXPIRED_TOKEN = jwt.encode(
    {
        'track_id': 'default_track_id',
        'verification_result': 'OK',
        'valid_to': '2000-01-01T14:00:00Z',
    },
    common.JWT_PRIVATE_KEY,
    algorithm='PS512',
)

BAD_PAYLOAD_TOKEN = jwt.encode(
    {
        'track_id': 'default_track_id',
        'verification_result': 'OK',
        # missing 'valid_to'
    },
    common.JWT_PRIVATE_KEY,
    algorithm='PS512',
)

BAD_ALGO_TOKEN = jwt.encode(
    {
        'track_id': 'default_track_id',
        'verification_result': 'OK',
        'valid_to': '2131-06-13T14:00:00Z',
    },
    common.JWT_PRIVATE_KEY,
    algorithm='PS384',
)


@pytest.fixture(name='bank_authorization')
def _bank_authorization(mockserver, mocked_time):
    class Context:
        def __init__(self):
            self.create_track_handler = None
            self.http_status_code = 200
            self.response_create_track = {'track_id': 'default_track_id'}

        def set_http_status_code(self, code):
            self.http_status_code = code

        def set_response_create_track(self, new_response):
            self.response_create_track = new_response

    context = Context()

    @mockserver.json_handler(
        '/bank-authorization/authorization-internal/v1/create_track',
    )
    def _create_track_handler(request):
        assert request.method == 'POST'
        return mockserver.make_response(
            status=context.http_status_code,
            json=context.response_create_track,
        )

    context.create_track_handler = _create_track_handler

    return context


# v_t = verification_token
@pytest.mark.config(BANK_AUTHORIZATION_JWT_PUBLIC_KEYS=common.JWT_PUBLIC_KEYS)
async def test_set_status_with_valid_v_t(
        taxi_bank_card, core_card_mock, mockserver, pgsql,
):
    headers = common.headers_with_idemp_token()
    headers['X-YaBank-Verification-Token'] = GOOD_TOKEN

    db_helpers.add_authorization_info(pgsql, headers['X-Idempotency-Token'])
    response = await taxi_bank_card.post(
        'v1/card/v1/set_status',
        headers=headers,
        json={'card_id': 'some_card_id', 'status': 'ACTIVE'},
    )

    assert response.status_code == 200


@pytest.mark.parametrize(
    'verification_token', [EXPIRED_TOKEN, BAD_PAYLOAD_TOKEN, BAD_ALGO_TOKEN],
)
@pytest.mark.config(BANK_AUTHORIZATION_JWT_PUBLIC_KEYS=common.JWT_PUBLIC_KEYS)
async def test_set_status_with_invalid_v_t(taxi_bank_card, verification_token):
    headers = common.headers_with_idemp_token()
    headers['X-YaBank-Verification-Token'] = verification_token

    response = await taxi_bank_card.post(
        'v1/card/v1/set_status',
        headers=headers,
        json={'card_id': 'some_card_id', 'status': 'ACTIVE'},
    )

    assert response.status_code == 400


@pytest.mark.config(BANK_AUTHORIZATION_JWT_PUBLIC_KEYS=common.JWT_PUBLIC_KEYS)
async def test_set_status_with_v_t_no_track_id(taxi_bank_card):
    headers = common.headers_with_idemp_token()
    headers['X-YaBank-Verification-Token'] = GOOD_TOKEN

    response = await taxi_bank_card.post(
        'v1/card/v1/set_status',
        headers=headers,
        json={'card_id': 'some_card_id', 'status': 'ACTIVE'},
    )

    assert response.status_code == 404


@pytest.mark.config(BANK_AUTHORIZATION_JWT_PUBLIC_KEYS=common.JWT_PUBLIC_KEYS)
async def test_set_status_with_v_t_bad_params(taxi_bank_card, pgsql):
    headers = common.headers_with_idemp_token()
    headers['X-YaBank-Verification-Token'] = GOOD_TOKEN

    db_helpers.add_authorization_info(
        pgsql, headers['X-Idempotency-Token'], params='bad_params',
    )
    response = await taxi_bank_card.post(
        'v1/card/v1/set_status',
        headers=headers,
        json={'card_id': 'some_card_id', 'status': 'ACTIVE'},
    )

    assert response.status_code == 409


@pytest.mark.config(BANK_AUTHORIZATION_JWT_PUBLIC_KEYS=common.JWT_PUBLIC_KEYS)
async def test_set_status_with_v_t_bad_idemp_key(taxi_bank_card, pgsql):
    headers = common.headers_with_idemp_token()
    headers['X-YaBank-Verification-Token'] = GOOD_TOKEN

    db_helpers.add_authorization_info(
        pgsql,
        headers['X-Idempotency-Token'],
        bind_idempotency_key='bad_token',
    )
    response = await taxi_bank_card.post(
        'v1/card/v1/set_status',
        headers=headers,
        json={'card_id': 'some_card_id', 'status': 'ACTIVE'},
    )

    assert response.status_code == 409


async def test_set_status_old_operation_id_new_af_resolution(
        taxi_bank_card, mockserver, core_card_mock, pgsql,
):
    headers = common.headers_with_idemp_token()
    db_helpers.add_operation_id(pgsql, headers['X-Idempotency-Token'])
    response = await taxi_bank_card.post(
        'v1/card/v1/set_status',
        headers=headers,
        json={'card_id': 'some_card_id', 'status': 'ACTIVE'},
    )

    assert response.status_code == 200


@pytest.mark.parametrize(
    'af_resolution', ['ALLOWED', 'AUTHORIZATION_REQUIRED', 'DENIED'],
)
async def test_set_status_old_operation_id_old_af_resolution(
        taxi_bank_card,
        testpoint,
        mockserver,
        core_card_mock,
        pgsql,
        bank_authorization,
        af_resolution,
):
    @testpoint('existed_af_resolution_used')
    def _existed_af_resolution_used(data):
        pass

    headers = common.headers_with_idemp_token()
    operation_id = db_helpers.add_operation_id(
        pgsql, headers['X-Idempotency-Token'],
    )
    db_helpers.add_af_resolution(pgsql, operation_id, af_resolution)
    response = await taxi_bank_card.post(
        'v1/card/v1/set_status',
        headers=headers,
        json={'card_id': 'some_card_id', 'status': 'ACTIVE'},
    )

    response_json = response.json()
    if af_resolution == 'ALLOWED':
        assert 'success_data' in response_json
        assert bank_authorization.create_track_handler.times_called == 0
    if af_resolution == 'AUTHORIZATION_REQUIRED':
        assert response_json['authorization_info'] == {
            'authorization_track_id': db_helpers.DEFAULT_TRACK_ID,
        }
        assert bank_authorization.create_track_handler.times_called == 1
    if af_resolution == 'DENIED':
        assert 'support_url' in response_json['fail_data']
        assert bank_authorization.create_track_handler.times_called == 0

    assert _existed_af_resolution_used.times_called == 1
    assert response.status_code == 200


@pytest.mark.parametrize(
    'af_resolution, actions',
    [('ALLOW', []), ('ALLOW', ['2fa']), ('DENY', [])],
)
async def test_set_status_new_operation_id(
        taxi_bank_card,
        testpoint,
        mockserver,
        core_card_mock,
        bank_authorization,
        af_resolution,
        actions,
        bank_risk,
):
    @testpoint('new_af_resolution_created')
    def _new_af_resolution_created(data):
        pass

    bank_risk.set_response(af_resolution, actions)
    headers = common.headers_with_idemp_token()
    response = await taxi_bank_card.post(
        'v1/card/v1/set_status',
        headers=headers,
        json={'card_id': 'some_card_id', 'status': 'ACTIVE'},
    )

    response_json = response.json()
    if af_resolution == 'ALLOW' and '2fa' not in actions:
        assert 'success_data' in response_json
        assert response_json['result_status'] == 'ALLOWED'
        assert bank_authorization.create_track_handler.times_called == 0
    if af_resolution == 'ALLOW' and '2fa' in actions:
        assert response_json['result_status'] == 'AUTHORIZATION_REQUIRED'
        assert response_json['authorization_info'] == {
            'authorization_track_id': db_helpers.DEFAULT_TRACK_ID,
        }
        assert bank_authorization.create_track_handler.times_called == 1
    if af_resolution == 'DENY':
        assert response_json['result_status'] == 'DENIED'
        assert 'support_url' in response_json['fail_data']
        assert bank_authorization.create_track_handler.times_called == 0

    assert _new_af_resolution_created.times_called == 1
    assert response.status_code == 200


@pytest.mark.config(BANK_AUTHORIZATION_JWT_PUBLIC_KEYS=common.JWT_PUBLIC_KEYS)
async def test_set_status_2fa_two_times_different_i_t(
        taxi_bank_card,
        testpoint,
        mockserver,
        core_card_mock,
        bank_authorization,
        bank_risk,
):
    @testpoint('new_af_resolution_created')
    def _new_af_resolution_created(data):
        pass

    bank_risk.set_response('ALLOW', ['2fa'])
    headers = common.headers_with_idemp_token()
    response = await taxi_bank_card.post(
        'v1/card/v1/set_status',
        headers=headers,
        json={'card_id': 'some_card_id', 'status': 'ACTIVE'},
    )

    response_json = response.json()
    assert response_json['result_status'] == 'AUTHORIZATION_REQUIRED'
    assert response_json['authorization_info'] == {
        'authorization_track_id': db_helpers.DEFAULT_TRACK_ID,
    }
    assert bank_authorization.create_track_handler.times_called == 1
    assert _new_af_resolution_created.times_called == 1
    assert response.status_code == 200

    bank_risk.set_response('ALLOW', [])
    headers['X-YaBank-Verification-Token'] = GOOD_TOKEN
    headers['X-Idempotency-Token'] = '83f0378f-c1fd-4af4-8950-178114165807'
    response_retry = await taxi_bank_card.post(
        'v1/card/v1/set_status',
        headers=headers,
        json={'card_id': 'some_card_id', 'status': 'ACTIVE'},
    )
    assert response_retry.status_code == 409


@pytest.mark.parametrize('bank_authorization_status_code', [409, 500])
async def test_set_status_error_from_bank_authorization(
        taxi_bank_card,
        bank_authorization_status_code,
        bank_authorization,
        bank_risk,
):
    bank_risk.set_response('ALLOW', ['2fa'])
    headers = common.headers_with_idemp_token()
    bank_authorization.set_http_status_code(bank_authorization_status_code)
    response = await taxi_bank_card.post(
        'v1/card/v1/set_status',
        headers=headers,
        json={'card_id': 'some_card_id', 'status': 'ACTIVE'},
    )

    assert bank_authorization.create_track_handler.times_called == 1
    assert response.status_code == 500


async def test_set_status_500_from_bank_risk_fallback(
        taxi_bank_card, mockserver, core_card_mock, pgsql, bank_risk,
):
    bank_risk.set_http_status_code(500)
    headers = common.headers_with_idemp_token()
    response = await taxi_bank_card.post(
        'v1/card/v1/set_status',
        headers=headers,
        json={'card_id': 'some_card_id', 'status': 'ACTIVE'},
    )

    assert response.status_code == 200
