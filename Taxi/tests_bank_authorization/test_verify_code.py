import jwt
import pytest

from tests_bank_authorization import common

PUBLIC_KEY = """-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAtpFv4ajBvQDxTD6u94P/
wbKRUpcv8HBpj7Ue8FtwcEWpLQFEUCpSDOuCLsWEoA+U9rjlM8lPS3hspWDBjJiD
oZAHjjil2NDMvU6+8CS4HpJ/kHyXA1lUfnD4xpWE7HJqW9wePJWZ4isddIfdH/ie
/9ETVcDo1nlK4Mg7VOct95uggPbhuMzidJ5+/gr4rZHQEyiJfUXSmKEmfpRJnTEY
vnHVbjMyKYnIH+2EpWsbEvv/qIjkxsg1sjsIc2w0RwS6WAKSraqvpwW/1doT2Xxd
wFgDqPzXcJYGHS8oAdYTQSLJY678di04XzIztP0adPu2uS6lKYUHg0sQ2qZLIpjE
DQIDAQAB
-----END PUBLIC KEY-----"""
PG_TRACK_ID_FPS = 'ccccb408-af20-4a4a-908b-e92cd5971796'


def select_attempts(pgsql, code_id):
    cursor = pgsql['bank_authorization'].cursor()
    cursor.execute(
        (
            f'SELECT attempted_hmac, key_id '
            f'FROM bank_authorization.attempts '
            f'WHERE code_id = \'{code_id}\''
        ),
    )
    return cursor.fetchall()


@pytest.mark.now('2021-06-13T14:00:00Z')
async def test_404(taxi_bank_authorization):
    response = await taxi_bank_authorization.post(
        'v1/authorization/v1/verify_code',
        headers=common.get_headers('buid1'),
        json={
            'track_id': '9948e3a9-623c-4524-a390-9e4264d27a77',
            'code': '1234',
        },
    )

    assert response.status_code == 404
    assert response.json()['code'] == 'NotFound'
    assert response.json()['message'] == 'Track_id is not found'


@pytest.mark.parametrize(
    'track_id, buid, code_id, code',
    [
        [
            '7948e3a9-623c-4524-a390-9e4264d27a77',
            'buid1',
            '7948e3a9-623c-4524-a390-9e4264d27b77',
            '1234',
        ],
        [PG_TRACK_ID_FPS, common.FPS_BANK_UID, PG_TRACK_ID_FPS, '888888'],
    ],
)
@pytest.mark.now('2021-06-13T14:00:00Z')
async def test_ok(
        taxi_bank_authorization,
        pgsql,
        risk_mock,
        core_faster_payments_mock,
        track_id,
        buid,
        code_id,
        code,
):
    response = await taxi_bank_authorization.post(
        'v1/authorization/v1/verify_code',
        headers=common.get_headers(buid),
        json={'track_id': track_id, 'code': code},
    )

    assert response.status_code == 200
    assert response.json()['verification_result'] == 'OK'

    # same request
    response = await taxi_bank_authorization.post(
        'v1/authorization/v1/verify_code',
        headers=common.get_headers(buid),
        json={'track_id': track_id, 'code': code},
    )

    assert response.status_code == 200
    assert response.json()['verification_result'] == 'OK'
    token = response.json()['ok_data']['verification_token']
    assert jwt.decode(token, key=PUBLIC_KEY, algorithms=['PS512']) == {
        'track_id': track_id,
        'verification_result': 'OK',
        'valid_to': '2021-06-13T14:15:00+00:00',
    }

    attempts = select_attempts(pgsql, code_id)
    assert len(attempts) == 1
    # attempted_hmac
    if track_id != PG_TRACK_ID_FPS:
        assert attempts[0][0] == '702a66ec4fd40d57920526e8a7958cc0bb960285'
        assert risk_mock.risk_calculation_handler.has_calls


@pytest.mark.parametrize(
    'track_id, buid, code_id, code',
    [
        [
            '7948e3a9-623c-4524-a390-9e4264d27a66',
            'buid2',
            '7948e3a9-623c-4524-a390-9e4264d27b66',
            1231,
        ],
        [PG_TRACK_ID_FPS, common.FPS_BANK_UID, PG_TRACK_ID_FPS, 888885],
    ],
)
@pytest.mark.now('2021-06-13T14:00:00Z')
async def test_fail(
        taxi_bank_authorization,
        pgsql,
        risk_mock,
        core_faster_payments_mock,
        track_id,
        buid,
        code_id,
        code,
):
    response = await taxi_bank_authorization.post(
        'v1/authorization/v1/verify_code',
        headers=common.get_headers(buid),
        json={'track_id': track_id, 'code': str(code)},
    )

    assert response.status_code == 200
    assert response.json() == {
        'verification_result': 'FAIL',
        'fail_data': {'result_code': 'CODE_MISMATCH', 'attempts_left': 2},
    }

    # same request
    response = await taxi_bank_authorization.post(
        'v1/authorization/v1/verify_code',
        headers=common.get_headers(buid),
        json={'track_id': track_id, 'code': str(code)},
    )

    assert response.status_code == 200
    assert response.json() == {
        'verification_result': 'FAIL',
        'fail_data': {'result_code': 'CODE_MISMATCH', 'attempts_left': 2},
    }

    response = await taxi_bank_authorization.post(
        'v1/authorization/v1/verify_code',
        headers=common.get_headers(buid),
        json={'track_id': track_id, 'code': str(code + 1)},
    )

    assert response.status_code == 200
    assert response.json() == {
        'verification_result': 'FAIL',
        'fail_data': {'result_code': 'CODE_MISMATCH', 'attempts_left': 1},
    }

    response = await taxi_bank_authorization.post(
        'v1/authorization/v1/verify_code',
        headers=common.get_headers(buid),
        json={'track_id': track_id, 'code': str(code + 2)},
    )

    assert response.status_code == 200
    assert response.json() == {
        'verification_result': 'FAIL',
        'fail_data': {'result_code': 'CODE_MISMATCH', 'attempts_left': 0},
    }

    # try valid code with no attempts
    response = await taxi_bank_authorization.post(
        'v1/authorization/v1/verify_code',
        headers=common.get_headers(buid),
        json={'track_id': track_id, 'code': str(code + 3)},
    )

    assert response.status_code == 200
    assert response.json() == {
        'verification_result': 'FAIL',
        'fail_data': {'result_code': 'NO_ATTEMPTS_LEFT', 'attempts_left': 0},
    }

    attempts = select_attempts(pgsql, code_id)
    assert len(attempts) == 3
    assert not risk_mock.risk_calculation_handler.has_calls


@pytest.mark.now('2021-06-13T14:00:00Z')
async def test_race1(taxi_bank_authorization, pgsql, testpoint, risk_mock):
    @testpoint('data_collected')
    def _data_collected(stats):
        cursor = pgsql['bank_authorization'].cursor()
        cursor.execute(
            (
                f'UPDATE bank_authorization.codes '
                f'SET attempts_left = 1 '
                f'WHERE id = \'7948e3a9-623c-4524-a390-9e4264d27b55\'::UUID;'
            ),
        )

    response = await taxi_bank_authorization.post(
        'v1/authorization/v1/verify_code',
        headers=common.get_headers('buid3'),
        json={
            'track_id': '7948e3a9-623c-4524-a390-9e4264d27a55',
            'code': '1111',
        },
    )

    assert response.status_code == 500

    response = await taxi_bank_authorization.post(
        'v1/authorization/v1/verify_code',
        headers=common.get_headers('buid3'),
        json={
            'track_id': '7948e3a9-623c-4524-a390-9e4264d27a55',
            'code': '1111',
        },
    )
    assert response.status_code == 200
    assert response.json()['verification_result'] == 'OK'
    assert response.json()['ok_data']['verification_token'] != ''


@pytest.mark.now('2021-06-13T14:00:00Z')
async def test_race2(taxi_bank_authorization, pgsql, testpoint, risk_mock):
    @testpoint('data_collected')
    def _data_collected(stats):
        cursor = pgsql['bank_authorization'].cursor()
        cursor.execute(
            (
                f'INSERT INTO bank_authorization.attempts '
                f'(code_id, attempted_hmac, key_id, buid)'
                f'VALUES (\'7948e3a9-623c-4524-a390-9e4264d27b55\', '
                f'\'23a163139ee5d9dfba62adb61c1c6f61f0dbd4b0\', '
                f'\'key_id3\', \'buid3\') ON CONFLICT DO NOTHING;'
            ),
        )

    response = await taxi_bank_authorization.post(
        'v1/authorization/v1/verify_code',
        headers=common.get_headers('buid3'),
        json={
            'track_id': '7948e3a9-623c-4524-a390-9e4264d27a55',
            'code': '1111',
        },
    )

    assert response.status_code == 500

    response = await taxi_bank_authorization.post(
        'v1/authorization/v1/verify_code',
        headers=common.get_headers('buid3'),
        json={
            'track_id': '7948e3a9-623c-4524-a390-9e4264d27a55',
            'code': '1111',
        },
    )

    assert response.status_code == 200
    assert response.json()['verification_result'] == 'OK'
    assert response.json()['ok_data']['verification_token'] != ''


@pytest.mark.now('2021-06-13T14:00:00Z')
async def test_key_not_found(taxi_bank_authorization, pgsql):
    response = await taxi_bank_authorization.post(
        'v1/authorization/v1/verify_code',
        headers=common.get_headers('buid4'),
        json={
            'track_id': '7948e3a9-623c-4524-a390-9e4264d27a44',
            'code': '1234',
        },
    )

    assert response.status_code == 404


@pytest.mark.now('2021-06-13T14:00:00Z')
async def test_old_key(taxi_bank_authorization, pgsql, risk_mock):
    response = await taxi_bank_authorization.post(
        'v1/authorization/v1/verify_code',
        headers=common.get_headers('buid5'),
        json={
            'track_id': '7948e3a9-623c-4524-a390-9e4264d27a33',
            'code': '1234',
        },
    )

    assert response.status_code == 200
    assert response.json()['verification_result'] == 'OK'
    assert response.json()['ok_data']['verification_token'] != ''


@pytest.mark.parametrize(
    'track_id, buid',
    [
        ['7948e3a9-623c-4524-a390-9e4264d27a22', 'buid6'],
        [PG_TRACK_ID_FPS, common.FPS_BANK_UID],
    ],
)
@pytest.mark.now('2021-06-13T15:00:00Z')
async def test_old_code(taxi_bank_authorization, pgsql, track_id, buid):
    response = await taxi_bank_authorization.post(
        'v1/authorization/v1/verify_code',
        headers=common.get_headers(buid),
        json={'track_id': track_id, 'code': '1234'},
    )

    assert response.status_code == 404


@pytest.mark.now('2021-06-13T14:00:00Z')
@pytest.mark.parametrize(
    'session_status',
    [
        'not_authorized',
        'pin_token_reissue',
        'pin_token_retry',
        'pin_token_registration',
    ],
)
async def test_verify_not_full_session_allow(
        taxi_bank_authorization, mockserver, risk_mock, session_status,
):
    headers = common.get_headers('buid1')
    headers['X-YaBank-AuthorizedByAuthproxy'] = 'no'
    headers['X-YaBank-SessionStatus'] = session_status
    response = await taxi_bank_authorization.post(
        'v1/authorization/v1/verify_code',
        headers=headers,
        json={
            'track_id': '7948e3a9-623c-4524-a390-9e4264d27a77',
            'code': '1234',
        },
    )
    assert response.status_code == 200


@pytest.mark.now('2021-06-13T14:00:00Z')
async def test_verify_not_full_session_not_allow(taxi_bank_authorization):
    headers = common.get_headers('buid1')
    headers['X-YaBank-AuthorizedByAuthproxy'] = 'no'
    headers['X-YaBank-SessionStatus'] = 'not_registered'
    response = await taxi_bank_authorization.post(
        'v1/authorization/v1/verify_code',
        headers=headers,
        json={
            'track_id': '7948e3a9-623c-4524-a390-9e4264d27a77',
            'code': '1234',
        },
    )
    assert response.status_code == 401


@pytest.mark.now('2021-06-13T14:00:00Z')
@pytest.mark.parametrize('risk_error_reason', [400, 500, 'timeout'])
async def test_risk_error(
        taxi_bank_authorization, mockserver, risk_error_reason,
):
    @mockserver.json_handler('/bank-risk/risk/calculation/otp_verify')
    def _risk_calculation_handler(request):
        if isinstance(risk_error_reason, int):
            return mockserver.make_response(status=risk_error_reason)

        raise mockserver.TimeoutError()

    response = await taxi_bank_authorization.post(
        'v1/authorization/v1/verify_code',
        headers=common.get_headers('buid1'),
        json={
            'track_id': '7948e3a9-623c-4524-a390-9e4264d27a77',
            'code': '1234',
        },
    )

    assert response.status_code == 200
    assert response.json()['verification_result'] == 'OK'


@pytest.mark.now('2021-06-13T14:00:00Z')
async def test_risk_payload(taxi_bank_authorization, mockserver):
    @mockserver.json_handler('/bank-risk/risk/calculation/otp_verify')
    def _risk_calculation_handler(request):
        assert request.json.pop('idempotent_token')
        assert request.json['code'].pop('updated_at')
        assert request.json['track'].pop('updated_at')
        for attempt in request.json['attempts']:
            assert attempt.pop('created_at')
            assert attempt.pop('updated_at')

        assert request.json == {
            'msg_type': 'otp_verify',
            'timestamp': '2021-06-13T14:00:00+00:00',
            'session_uuid': 'session_uuid',
            'client_ip': '',
            'yandex_uid': 'uid',
            'buid': 'buid1',
            'af_decision_id': 'antifraud_context_id',
            'code': {
                'id': '7948e3a9-623c-4524-a390-9e4264d27b77',
                'idempotency_token': 'idempotency_token1',
                'key_id': 'key_1',
                'track_id': '7948e3a9-623c-4524-a390-9e4264d27a77',
                'attempts_left': 3,
                'created_at': '2021-06-13T13:55:00+00:00',
            },
            'track': {
                'id': '7948e3a9-623c-4524-a390-9e4264d27a77',
                'idempotency_token': '78a4e507-f6f0-4b6c-b9b5-b00ebbfe0da1',
                'operation_type': 'start_session',
                'created_at': '2021-06-12T11:50:00+00:00',
            },
            'attempts': [
                {
                    'code_id': '7948e3a9-623c-4524-a390-9e4264d27b77',
                    'key_id': 'key_1',
                },
            ],
        }

    response = await taxi_bank_authorization.post(
        'v1/authorization/v1/verify_code',
        headers=common.get_headers('buid1'),
        json={
            'track_id': '7948e3a9-623c-4524-a390-9e4264d27a77',
            'code': '1234',
            'antifraud_context_id': 'antifraud_context_id',
        },
    )

    assert response.status_code == 200
    assert response.json()['verification_result'] == 'OK'


@pytest.mark.now('2021-06-13T14:00:00Z')
async def test_correct_code_500_in_ftc(
        taxi_bank_authorization, core_faster_payments_mock,
):
    core_faster_payments_mock.set_status(500)
    response = await taxi_bank_authorization.post(
        'v1/authorization/v1/verify_code',
        headers=common.get_headers(common.FPS_BANK_UID),
        json={'track_id': PG_TRACK_ID_FPS, 'code': '888888'},
    )

    assert response.status_code == 500


def get_headers_internal_version(idem_token=None, language='ru'):
    result = {}
    if idem_token is not None:
        result['X-Idempotency-Token'] = idem_token
    if language is not None:
        result['X-Request-Language'] = language
    return result


@pytest.mark.now('2021-06-13T14:00:00Z')
async def test_internal_404(taxi_bank_authorization):
    response = await taxi_bank_authorization.post(
        'authorization-internal/v1/verify_code',
        headers=get_headers_internal_version(),
        json={
            'track_id': '9948e3a9-623c-4524-a390-9e4264d27a77',
            'code': '1234',
            'buid': 'buid1',
        },
    )

    assert response.status_code == 404
    assert response.json()['code'] == 'NotFound'
    assert response.json()['message'] == 'Track_id is not found'


@pytest.mark.parametrize(
    'track_id, buid, code_id, code',
    [
        [
            '7948e3a9-623c-4524-a390-9e4264d27a77',
            'buid1',
            '7948e3a9-623c-4524-a390-9e4264d27b77',
            '1234',
        ],
    ],
)
@pytest.mark.now('2021-06-13T14:00:00Z')
async def test_internal_ok(
        taxi_bank_authorization,
        pgsql,
        risk_mock,
        core_faster_payments_mock,
        track_id,
        buid,
        code_id,
        code,
):
    response = await taxi_bank_authorization.post(
        'authorization-internal/v1/verify_code',
        headers=get_headers_internal_version(),
        json={'track_id': track_id, 'code': code, 'buid': 'buid1'},
    )

    assert response.status_code == 200
    assert response.json()['verification_result'] == 'OK'

    # same request
    response = await taxi_bank_authorization.post(
        'authorization-internal/v1/verify_code',
        headers=get_headers_internal_version(),
        json={'track_id': track_id, 'code': code, 'buid': 'buid1'},
    )

    assert response.status_code == 200
    assert response.json()['verification_result'] == 'OK'
    token = response.json()['ok_data']['verification_token']
    assert jwt.decode(token, key=PUBLIC_KEY, algorithms=['PS512']) == {
        'track_id': track_id,
        'verification_result': 'OK',
        'valid_to': '2021-06-13T14:15:00+00:00',
    }

    attempts = select_attempts(pgsql, code_id)
    assert len(attempts) == 1
    # attempted_hmac
    if track_id != PG_TRACK_ID_FPS:
        assert attempts[0][0] == '702a66ec4fd40d57920526e8a7958cc0bb960285'
        assert risk_mock.risk_calculation_handler.has_calls


@pytest.mark.parametrize(
    'track_id, buid, code_id, code',
    [
        [
            '7948e3a9-623c-4524-a390-9e4264d27a66',
            'buid2',
            '7948e3a9-623c-4524-a390-9e4264d27b66',
            1231,
        ],
    ],
)
@pytest.mark.now('2021-06-13T14:00:00Z')
async def test_internal_fail(
        taxi_bank_authorization,
        pgsql,
        risk_mock,
        core_faster_payments_mock,
        track_id,
        buid,
        code_id,
        code,
):
    response = await taxi_bank_authorization.post(
        'authorization-internal/v1/verify_code',
        headers=get_headers_internal_version(),
        json={'track_id': track_id, 'code': str(code), 'buid': buid},
    )

    assert response.status_code == 200
    assert response.json() == {
        'verification_result': 'FAIL',
        'fail_data': {'result_code': 'CODE_MISMATCH', 'attempts_left': 2},
    }

    # same request
    response = await taxi_bank_authorization.post(
        'authorization-internal/v1/verify_code',
        headers=get_headers_internal_version(),
        json={'track_id': track_id, 'code': str(code), 'buid': buid},
    )

    assert response.status_code == 200
    assert response.json() == {
        'verification_result': 'FAIL',
        'fail_data': {'result_code': 'CODE_MISMATCH', 'attempts_left': 2},
    }

    response = await taxi_bank_authorization.post(
        'authorization-internal/v1/verify_code',
        headers=get_headers_internal_version(),
        json={'track_id': track_id, 'code': str(code + 1), 'buid': buid},
    )

    assert response.status_code == 200
    assert response.json() == {
        'verification_result': 'FAIL',
        'fail_data': {'result_code': 'CODE_MISMATCH', 'attempts_left': 1},
    }

    response = await taxi_bank_authorization.post(
        'authorization-internal/v1/verify_code',
        headers=get_headers_internal_version(),
        json={'track_id': track_id, 'code': str(code + 2), 'buid': buid},
    )

    assert response.status_code == 200
    assert response.json() == {
        'verification_result': 'FAIL',
        'fail_data': {'result_code': 'CODE_MISMATCH', 'attempts_left': 0},
    }

    # try valid code with no attempts
    response = await taxi_bank_authorization.post(
        'authorization-internal/v1/verify_code',
        headers=get_headers_internal_version(),
        json={'track_id': track_id, 'code': str(code + 3), 'buid': buid},
    )

    assert response.status_code == 200
    assert response.json() == {
        'verification_result': 'FAIL',
        'fail_data': {'result_code': 'NO_ATTEMPTS_LEFT', 'attempts_left': 0},
    }

    attempts = select_attempts(pgsql, code_id)
    assert len(attempts) == 3
    assert not risk_mock.risk_calculation_handler.has_calls


@pytest.mark.now('2021-06-13T14:00:00Z')
async def test_internal_race1(
        taxi_bank_authorization, pgsql, testpoint, risk_mock,
):
    @testpoint('data_collected')
    def _data_collected(stats):
        cursor = pgsql['bank_authorization'].cursor()
        cursor.execute(
            (
                f'UPDATE bank_authorization.codes '
                f'SET attempts_left = 1 '
                f'WHERE id = \'7948e3a9-623c-4524-a390-9e4264d27b55\'::UUID;'
            ),
        )

    response = await taxi_bank_authorization.post(
        'authorization-internal/v1/verify_code',
        headers=get_headers_internal_version(),
        json={
            'track_id': '7948e3a9-623c-4524-a390-9e4264d27a55',
            'code': '1111',
            'buid': 'buid3',
        },
    )

    assert response.status_code == 500

    response = await taxi_bank_authorization.post(
        'authorization-internal/v1/verify_code',
        headers=get_headers_internal_version(),
        json={
            'track_id': '7948e3a9-623c-4524-a390-9e4264d27a55',
            'code': '1111',
            'buid': 'buid3',
        },
    )
    assert response.status_code == 200
    assert response.json()['verification_result'] == 'OK'
    assert response.json()['ok_data']['verification_token'] != ''


@pytest.mark.now('2021-06-13T14:00:00Z')
async def test_internal_race2(
        taxi_bank_authorization, pgsql, testpoint, risk_mock,
):
    @testpoint('data_collected')
    def _data_collected(stats):
        cursor = pgsql['bank_authorization'].cursor()
        cursor.execute(
            (
                f'INSERT INTO bank_authorization.attempts '
                f'(code_id, attempted_hmac, key_id, buid)'
                f'VALUES (\'7948e3a9-623c-4524-a390-9e4264d27b55\', '
                f'\'23a163139ee5d9dfba62adb61c1c6f61f0dbd4b0\', '
                f'\'key_id3\', \'buid3\') ON CONFLICT DO NOTHING;'
            ),
        )

    response = await taxi_bank_authorization.post(
        'authorization-internal/v1/verify_code',
        headers=get_headers_internal_version(),
        json={
            'track_id': '7948e3a9-623c-4524-a390-9e4264d27a55',
            'code': '1111',
            'buid': 'buid3',
        },
    )

    assert response.status_code == 500

    response = await taxi_bank_authorization.post(
        'authorization-internal/v1/verify_code',
        headers=get_headers_internal_version(),
        json={
            'track_id': '7948e3a9-623c-4524-a390-9e4264d27a55',
            'code': '1111',
            'buid': 'buid3',
        },
    )

    assert response.status_code == 200
    assert response.json()['verification_result'] == 'OK'
    assert response.json()['ok_data']['verification_token'] != ''


@pytest.mark.now('2021-06-13T14:00:00Z')
async def test_internal_key_not_found(taxi_bank_authorization, pgsql):
    response = await taxi_bank_authorization.post(
        'authorization-internal/v1/verify_code',
        headers=get_headers_internal_version(),
        json={
            'track_id': '7948e3a9-623c-4524-a390-9e4264d27a44',
            'code': '1234',
            'buid': 'buid4',
        },
    )

    assert response.status_code == 404


@pytest.mark.now('2021-06-13T14:00:00Z')
async def test_internal_old_key(taxi_bank_authorization, pgsql, risk_mock):
    response = await taxi_bank_authorization.post(
        'authorization-internal/v1/verify_code',
        headers=get_headers_internal_version(),
        json={
            'track_id': '7948e3a9-623c-4524-a390-9e4264d27a33',
            'code': '1234',
            'buid': 'buid5',
        },
    )

    assert response.status_code == 200
    assert response.json()['verification_result'] == 'OK'
    assert response.json()['ok_data']['verification_token'] != ''


@pytest.mark.parametrize(
    'track_id, buid', [['7948e3a9-623c-4524-a390-9e4264d27a22', 'buid6']],
)
@pytest.mark.now('2021-06-13T15:00:00Z')
async def test_internal_old_code(
        taxi_bank_authorization, pgsql, track_id, buid,
):
    response = await taxi_bank_authorization.post(
        'authorization-internal/v1/verify_code',
        headers=get_headers_internal_version(),
        json={'track_id': track_id, 'code': '1234', 'buid': buid},
    )

    assert response.status_code == 404
