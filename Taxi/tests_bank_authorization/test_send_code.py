import pytest
import re

from tests_bank_authorization import common

PG_TRACK_ID1 = 'ccccb408-af20-4a4a-908b-e92cd5971794'
PG_TRACK_ID2 = 'ccccb408-af20-4a4a-908b-e92cd5971795'
PG_TRACK_ID_FPS = 'ccccb408-af20-4a4a-908b-e92cd5971796'
PG_TRACK_ID_FPS_2 = 'ccccb408-af20-4a4a-908b-e92cd5971797'
PG_TRACK_ID_NOT_CREATED = 'aaaab408-af20-4a4a-908b-e92cd5971797'
SUPPORT_URL = {'support_url': 'http://support.ya/'}


def select_last_code_by_track_id(pgsql, track_id):
    cursor = pgsql['bank_authorization'].cursor()
    cursor.execute(
        (
            'SELECT code_hmac, key_id, idempotency_token, '
            'attempts_left, track_id, buid, id, request_id '
            'FROM bank_authorization.codes '
            f'WHERE track_id = \'{track_id}\' '
            'ORDER BY cursor_key DESC '
            'LIMIT 1'
        ),
    )
    result = cursor.fetchall()
    assert len(result) == 1
    return result[0]


def select_all_codes_by_track_id(pgsql, track_id):
    cursor = pgsql['bank_authorization'].cursor()
    cursor.execute(
        (
            'SELECT code_hmac, key_id, idempotency_token, '
            'attempts_left, track_id, buid, id, request_id '
            'FROM bank_authorization.codes '
            f'WHERE track_id = \'{track_id}\' '
            'ORDER BY cursor_key DESC;'
        ),
    )
    results = cursor.fetchall()
    return results


def insert_code(pgsql, track_id, code_hmac, key_id, idempotency_token, buid):
    sql = (
        'INSERT INTO bank_authorization.codes '
        '(track_id, code_hmac, key_id, idempotency_token, buid) '
        'VALUES (%s, %s, %s, %s, %s) '
        'RETURNING id'
    )
    cursor = pgsql['bank_authorization'].cursor()
    cursor.execute(sql, (track_id, code_hmac, key_id, idempotency_token, buid))
    code_id = cursor.fetchone()[0]
    return code_id


@pytest.mark.now('2021-06-13T14:00:00Z')
async def test_simple(
        taxi_bank_authorization,
        pgsql,
        mockserver,
        testpoint,
        phone_number_mock,
):
    generated_code = None
    generated_code_hmac = None

    @mockserver.json_handler(
        '/bank-communications/communications-internal/v1/send',
    )
    def _mock_communications_send(request):
        assert request.json['locale'] != ''
        assert request.json['type'] == 'default_type'
        assert request.json['buid'] == common.BANK_UID1
        assert request.json['template_parameters'] == {'code': generated_code}
        assert request.headers['X-Idempotency-Token'] == 'idempotency-key'
        return mockserver.make_response('{}', 200)

    @mockserver.json_handler(
        '/bank-userinfo/userinfo-internal/v1/get_phone_number',
    )
    def _mock_phone_number():
        return {'phone': common.PHONE_NUMBER1}

    @testpoint('code_generated')
    def _code_generated(data):
        nonlocal generated_code
        nonlocal generated_code_hmac
        generated_code = data['code']
        generated_code_hmac = data['code_hmac']

    response = await taxi_bank_authorization.post(
        'v1/authorization/v1/send_code',
        headers=common.get_headers(common.BANK_UID1, 'idempotency-key'),
        json={'track_id': PG_TRACK_ID1},
    )

    assert response.json() == {
        'status': 'OK',
        'retry_interval': 30,
        'code_format': 'DIGIT_4',
        'phone': common.PHONE_NUMBER1_MASKED,
    }
    assert response.status_code == 200

    code = select_last_code_by_track_id(pgsql, PG_TRACK_ID1)

    # code hmac is not implemented, code is stored in plain text
    assert code[0] == generated_code_hmac
    # key_id is first in array
    assert code[1] == 'key_1'
    # idempotency token from request
    assert code[2] == 'idempotency-key'
    # default attempts_left is 3
    assert code[3] == 3
    # track_id from request
    assert code[4] == PG_TRACK_ID1
    # buid from request
    assert code[5] == common.BANK_UID1


@pytest.mark.config(BANK_AUTHORIZATION_TESTING={'disclose_sent_code': True})
@pytest.mark.now('2021-06-13T14:00:00Z')
async def test_simple_disclose_code(
        taxi_bank_authorization,
        pgsql,
        mockserver,
        testpoint,
        phone_number_mock,
):
    generated_code = None
    generated_code_hmac = None

    @mockserver.json_handler(
        '/bank-communications/communications-internal/v1/send',
    )
    def _mock_communications_send(request):
        assert request.json['locale'] != ''
        assert request.json['type'] == 'default_type'
        assert request.json['buid'] == common.BANK_UID1
        assert request.json['template_parameters'] == {'code': generated_code}
        assert request.headers['X-Idempotency-Token'] == 'idempotency-key'
        return mockserver.make_response('{}', 200)

    @testpoint('code_generated')
    def _code_generated(data):
        nonlocal generated_code
        nonlocal generated_code_hmac
        generated_code = data['code']
        generated_code_hmac = data['code_hmac']

    headers = common.get_headers(common.BANK_UID1, 'idempotency-key')
    headers['X-Testing'] = 'Disclose-Sent-Code'
    response = await taxi_bank_authorization.post(
        'v1/authorization/v1/send_code',
        headers=headers,
        json={'track_id': PG_TRACK_ID1},
    )

    assert response.status_code == 200
    testing_sent_code = response.json()['testing_sent_code']
    assert re.match(r'\d{4}', testing_sent_code)
    assert response.json() == {
        'status': 'OK',
        'retry_interval': 30,
        'code_format': 'DIGIT_4',
        'phone': common.PHONE_NUMBER1_MASKED,
        'testing_sent_code': testing_sent_code,
    }

    code = select_last_code_by_track_id(pgsql, PG_TRACK_ID1)

    # code hmac is not implemented, code is stored in plain text
    assert code[0] == generated_code_hmac
    # key_id is first in array
    assert code[1] == 'key_1'
    # idempotency token from request
    assert code[2] == 'idempotency-key'
    # default attempts_left is 3
    assert code[3] == 3
    # track_id from request
    assert code[4] == PG_TRACK_ID1
    # buid from request
    assert code[5] == common.BANK_UID1


@pytest.mark.now('2021-06-13T14:00:00Z')
async def test_simple_fps(
        taxi_bank_authorization,
        pgsql,
        mockserver,
        testpoint,
        core_faster_payments_mock,
):
    @mockserver.json_handler(
        '/bank-communications/communications-internal/v1/send',
    )
    def _mock_communications_send(request):
        return mockserver.make_response(status=500)

    @testpoint('code_generated')
    def _code_generated(data):
        assert data['request_id'] == common.FPS_REQUEST_ID

    response = await taxi_bank_authorization.post(
        'v1/authorization/v1/send_code',
        headers=common.get_headers(common.FPS_BANK_UID, 'idempotency-key'),
        json={'track_id': PG_TRACK_ID_FPS},
    )

    assert response.status_code == 200
    assert response.json() == {
        'status': 'OK',
        'retry_interval': 30,
        'code_format': 'DIGIT_6',
    }

    code = select_last_code_by_track_id(pgsql, PG_TRACK_ID_FPS)

    # default attempts_left is 3
    assert code[3] == 3
    # track_id from request
    assert code[4] == PG_TRACK_ID_FPS
    # buid from request
    assert code[5] == common.FPS_BANK_UID
    # request_id from bank-core-faster-payments
    assert code[7] == common.FPS_REQUEST_ID


@pytest.mark.parametrize(
    'track_id, buid, phone_masked, sent',
    [
        [PG_TRACK_ID1, common.BANK_UID1, common.PHONE_NUMBER1_MASKED, 1],
        [PG_TRACK_ID_FPS, common.FPS_BANK_UID, None, 0],
    ],
)
@pytest.mark.now('2021-06-13T14:00:00Z')
async def test_idempotency(
        taxi_bank_authorization,
        pgsql,
        mockserver,
        testpoint,
        core_faster_payments_mock,
        track_id,
        buid,
        phone_masked,
        sent,
        phone_number_mock,
):
    generated_code = None
    gen_code_hmac = None

    @mockserver.json_handler(
        '/bank-communications/communications-internal/v1/send',
    )
    def _mock_communications_send(request):
        assert request.json['locale'] != ''
        assert request.json['type'] == 'default_type'
        assert request.json['buid'] == common.BANK_UID1
        assert request.json['template_parameters'] == {'code': generated_code}
        assert request.headers['X-Idempotency-Token'] == 'idempotency-key'
        return mockserver.make_response('{}', 200)

    @testpoint('code_generated')
    def _code_generated(data):
        nonlocal generated_code
        nonlocal gen_code_hmac
        generated_code = data['code']
        gen_code_hmac = data['code_hmac']

    response = await taxi_bank_authorization.post(
        'v1/authorization/v1/send_code',
        headers=common.get_headers(buid, 'idempotency-key'),
        json={'track_id': track_id},
    )
    assert response.status_code == 200
    code_format = 'DIGIT_6' if buid == common.FPS_BANK_UID else 'DIGIT_4'
    if phone_masked is None:
        assert response.json() == {
            'status': 'OK',
            'retry_interval': 30,
            'code_format': code_format,
        }
    else:
        assert response.json() == {
            'status': 'OK',
            'retry_interval': 30,
            'code_format': code_format,
            'phone': phone_masked,
        }
    assert _mock_communications_send.times_called == sent

    code = select_last_code_by_track_id(pgsql, track_id)
    assert code[0] == gen_code_hmac
    assert code[1] == 'key_1'
    assert code[2] == 'idempotency-key'
    assert code[3] == 3
    assert code[4] == track_id
    assert code[5] == buid

    response = await taxi_bank_authorization.post(
        'v1/authorization/v1/send_code',
        headers=common.get_headers(buid, 'idempotency-key'),
        json={'track_id': track_id},
    )
    assert response.status_code == 200
    if phone_masked is None:
        assert response.json() == {
            'status': 'OK',
            'retry_interval': 30,
            'code_format': code_format,
        }
    else:
        assert response.json() == {
            'status': 'OK',
            'retry_interval': 30,
            'code_format': code_format,
            'phone': phone_masked,
        }
    assert _mock_communications_send.times_called == sent

    codes = select_all_codes_by_track_id(pgsql, track_id)
    assert len(codes) == 1
    assert codes[0][0] == gen_code_hmac
    assert codes[0][1] == 'key_1'
    assert codes[0][2] == 'idempotency-key'
    assert codes[0][3] == 3
    assert codes[0][4] == track_id
    assert codes[0][5] == buid
    assert code[6] == codes[0][6]


@pytest.mark.now('2021-06-13T14:00:00Z')
async def test_idempotency_race(
        taxi_bank_authorization,
        pgsql,
        mockserver,
        testpoint,
        core_faster_payments_mock,
        phone_number_mock,
):
    generated_code = None
    gen_code_hmac = None
    code_id = None

    @mockserver.json_handler(
        '/bank-communications/communications-internal/v1/send',
    )
    def _mock_communications_send(request):
        assert request.json['locale'] != ''
        assert request.json['type'] == 'default_type'
        assert request.json['buid'] == common.BANK_UID1
        assert request.json['template_parameters'] == {'code': generated_code}
        assert request.headers['X-Idempotency-Token'] == 'idempotency-key'
        return mockserver.make_response('{}', 200)

    @testpoint('code_generated')
    def _code_generated(data):
        nonlocal generated_code
        nonlocal gen_code_hmac
        generated_code = data['code']
        gen_code_hmac = data['code_hmac']

    @testpoint('create_other_code')
    def _create_other_track(data):
        nonlocal code_id
        code_id = insert_code(
            pgsql, PG_TRACK_ID1, '', '', 'idempotency-key', common.BANK_UID1,
        )

    response = await taxi_bank_authorization.post(
        'v1/authorization/v1/send_code',
        headers=common.get_headers(common.BANK_UID1, 'idempotency-key'),
        json={'track_id': PG_TRACK_ID1},
    )
    assert response.status_code == 500
    codes = select_all_codes_by_track_id(pgsql, PG_TRACK_ID1)
    assert not _mock_communications_send.has_calls
    assert len(codes) == 1
    assert codes[0] == (
        '',
        '',
        'idempotency-key',
        3,
        PG_TRACK_ID1,
        common.BANK_UID1,
        code_id,
        None,
    )


@pytest.mark.parametrize(
    'track_id, buid, phone_masked, sent',
    [
        [PG_TRACK_ID1, common.BANK_UID1, common.PHONE_NUMBER1_MASKED, 1],
        [PG_TRACK_ID_FPS, common.FPS_BANK_UID, None, 0],
    ],
)
@pytest.mark.now('2021-06-13T14:00:00Z')
async def test_idempotency_conflict(
        taxi_bank_authorization,
        pgsql,
        mockserver,
        testpoint,
        core_faster_payments_mock,
        track_id,
        buid,
        phone_masked,
        sent,
        phone_number_mock,
):
    generated_code = None
    gen_code_hmac = None

    @mockserver.json_handler(
        '/bank-communications/communications-internal/v1/send',
    )
    def _mock_communications_send(request):
        assert request.json['locale'] != ''
        assert request.json['type'] == 'default_type'
        assert request.json['buid'] == common.BANK_UID1
        assert request.json['template_parameters'] == {'code': generated_code}
        assert request.headers['X-Idempotency-Token'] == 'idempotency-key'
        return mockserver.make_response('{}', 200)

    @testpoint('code_generated')
    def _code_generated(data):
        nonlocal generated_code
        nonlocal gen_code_hmac
        generated_code = data['code']
        gen_code_hmac = data['code_hmac']

    response = await taxi_bank_authorization.post(
        'v1/authorization/v1/send_code',
        headers=common.get_headers(buid, 'idempotency_token1'),
        json={'track_id': track_id},
    )
    assert response.status_code == 409
    assert not _mock_communications_send.has_calls
    codes = select_all_codes_by_track_id(pgsql, track_id)
    assert not codes

    response = await taxi_bank_authorization.post(
        'v1/authorization/v1/send_code',
        headers=common.get_headers(buid, 'idempotency-key'),
        json={'track_id': track_id},
    )
    assert response.status_code == 200
    code_format = 'DIGIT_6' if buid == common.FPS_BANK_UID else 'DIGIT_4'
    if phone_masked is None:
        assert response.json() == {
            'status': 'OK',
            'retry_interval': 30,
            'code_format': code_format,
        }
    else:
        assert response.json() == {
            'status': 'OK',
            'retry_interval': 30,
            'code_format': code_format,
            'phone': phone_masked,
        }
    assert _mock_communications_send.times_called == sent

    codes = select_all_codes_by_track_id(pgsql, track_id)
    assert len(codes) == 1
    assert codes[0][0] == gen_code_hmac
    assert codes[0][1] == 'key_1'
    assert codes[0][2] == 'idempotency-key'
    assert codes[0][3] == 3
    assert codes[0][4] == track_id
    assert codes[0][5] == buid


@pytest.mark.parametrize(
    'track_id, buid',
    [[PG_TRACK_ID1, common.BANK_UID1], [PG_TRACK_ID_FPS, common.FPS_BANK_UID]],
)
@pytest.mark.now('2021-06-13T14:00:00Z')
async def test_500(
        taxi_bank_authorization, mockserver, track_id, buid, phone_number_mock,
):
    @mockserver.json_handler(
        '/bank-communications/communications-internal/v1/send',
    )
    def _mock_communications_send(request):
        return mockserver.make_response('{}', 500)

    @mockserver.json_handler(
        '/bank-core-faster-payments/v1/connect/setAsDefault',
    )
    def _mock_set_as_default(request):
        return mockserver.make_response(status=500)

    response = await taxi_bank_authorization.post(
        'v1/authorization/v1/send_code',
        headers=common.get_headers(buid, 'idempotency-key'),
        json={'track_id': track_id},
    )

    assert response.status_code == 500


@pytest.mark.now('2021-06-13T14:00:00Z')
async def test_429(taxi_bank_authorization, mockserver, phone_number_mock):
    @mockserver.json_handler(
        '/bank-communications/communications-internal/v1/send',
    )
    def _mock_communications_send(request):
        return mockserver.make_response(
            status=429,
            json={'code': 'TooManyRequests', 'message': 'TooManyRequests'},
        )

    response = await taxi_bank_authorization.post(
        'v1/authorization/v1/send_code',
        headers=common.get_headers(common.BANK_UID1, 'idempotency-key'),
        json={'track_id': PG_TRACK_ID1},
    )

    assert response.status_code == 429


@pytest.mark.config(
    BANK_AUTHORIZATION_AF_LIMITS=[{'offset': 1440, 'limit': 5}],
)
@pytest.mark.config(BANK_SUPPORT_URL=SUPPORT_URL)
@pytest.mark.now('2021-06-13T14:00:00Z')
async def test_af_limit_large(
        taxi_bank_authorization, mockserver, phone_number_mock,
):
    response = await taxi_bank_authorization.post(
        'v1/authorization/v1/send_code',
        headers=common.get_headers(common.BANK_UID2, 'idempotency-key'),
        json={'track_id': PG_TRACK_ID2},
    )

    assert response.status_code == 200
    assert response.json() == {
        'status': 'FAIL',
        'retry_interval': 30,
        'fail_data': {
            'result_code': 'NO_ATTEMPTS_LEFT',
            'support_url': 'http://support.ya/',
        },
    }


@pytest.mark.parametrize(
    'track_id, buid',
    [
        [PG_TRACK_ID2, common.BANK_UID2],
        [PG_TRACK_ID_FPS_2, common.FPS_BANK_UID],
    ],
)
@pytest.mark.config(BANK_AUTHORIZATION_AF_LIMITS=[{'offset': 10, 'limit': 2}])
@pytest.mark.now('2021-06-13T14:00:00Z')
@pytest.mark.config(BANK_SUPPORT_URL=SUPPORT_URL)
async def test_af_limit_small(
        taxi_bank_authorization,
        mockserver,
        core_faster_payments_mock,
        phone_number_mock,
        track_id,
        buid,
):
    response = await taxi_bank_authorization.post(
        'v1/authorization/v1/send_code',
        headers=common.get_headers(buid, 'idempotency-key'),
        json={'track_id': track_id},
    )

    assert response.status_code == 200
    assert response.json() == {
        'status': 'FAIL',
        'retry_interval': 30,
        'fail_data': {
            'result_code': 'NO_ATTEMPTS_LEFT',
            'support_url': 'http://support.ya/',
        },
    }


@pytest.mark.config(
    BANK_AUTHORIZATION_AF_LIMITS=[
        {'offset': 10, 'limit': 3},
        {'offset': 1440, 'limit': 5},
    ],
)
@pytest.mark.config(BANK_SUPPORT_URL=SUPPORT_URL)
@pytest.mark.now('2021-06-13T14:00:00Z')
async def test_af_limits_second_limit(
        taxi_bank_authorization, mockserver, phone_number_mock,
):
    response = await taxi_bank_authorization.post(
        'v1/authorization/v1/send_code',
        headers=common.get_headers(common.BANK_UID2, 'idempotency-key'),
        json={'track_id': PG_TRACK_ID2},
    )

    assert response.status_code == 200
    assert response.json() == {
        'status': 'FAIL',
        'retry_interval': 30,
        'fail_data': {
            'result_code': 'NO_ATTEMPTS_LEFT',
            'support_url': 'http://support.ya/',
        },
    }


@pytest.mark.config(
    BANK_AUTHORIZATION_AF_LIMITS=[
        {'offset': 10, 'limit': 2},
        {'offset': 1440, 'limit': 6},
    ],
)
@pytest.mark.config(BANK_SUPPORT_URL=SUPPORT_URL)
@pytest.mark.now('2021-06-13T14:00:00Z')
async def test_af_limits_first_limit(
        taxi_bank_authorization, mockserver, phone_number_mock,
):
    response = await taxi_bank_authorization.post(
        'v1/authorization/v1/send_code',
        headers=common.get_headers(common.BANK_UID2, 'idempotency-key'),
        json={'track_id': PG_TRACK_ID2},
    )

    assert response.status_code == 200
    assert response.json() == {
        'status': 'FAIL',
        'retry_interval': 30,
        'fail_data': {
            'result_code': 'NO_ATTEMPTS_LEFT',
            'support_url': 'http://support.ya/',
        },
    }


@pytest.mark.config(
    BANK_AUTHORIZATION_AF_LIMITS=[
        {'offset': 10, 'limit': 3},
        {'offset': 1440, 'limit': 6},
    ],
)
@pytest.mark.now('2021-06-13T14:00:00Z')
async def test_af_limits_allow(
        taxi_bank_authorization, mockserver, pgsql, phone_number_mock,
):
    @mockserver.json_handler(
        '/bank-communications/communications-internal/v1/send',
    )
    def _mock_communications_send(request):
        assert request.json['locale'] != ''
        assert request.json['antifraud_info']['device_id'] == '12345'
        assert (
            request.json['antifraud_info']['user_agent']
            == 'YandexBankSdk TestApp/0.15.0 bank-sdk/0.15.0 (android)'
        )
        assert request.json['antifraud_info']['client_ip'] == '127.0.0.13'
        return mockserver.make_response('{}', 200)

    response = await taxi_bank_authorization.post(
        'v1/authorization/v1/send_code',
        headers={
            'X-YaBank-SessionUUID': 'session_uuid',
            'X-YaBank-PhoneID': 'phone_id',
            'X-Yandex-BUID': common.BANK_UID2,
            'X-Yandex-UID': 'uid',
            'X-Ya-User-Ticket': 'user_ticket',
            'X-Idempotency-Token': 'idempotency-key',
            'X-Request-Language': 'ru',
            'User-Agent': (
                'YandexBankSdk TestApp/0.15.0 bank-sdk/0.15.0 (android)'
            ),
            'X-Remote-IP': '127.0.0.13',
        },
        json={'track_id': PG_TRACK_ID2, 'device_id': '12345'},
    )

    assert response.status_code == 200
    assert response.json() == {
        'status': 'OK',
        'retry_interval': 30,
        'code_format': 'DIGIT_4',
        'phone': common.PHONE_NUMBER2_MASKED,
    }


@pytest.mark.config(
    BANK_AUTHORIZATION_CODE_GENERATION_SETTINGS={
        '__default__': {
            'low_limit': 1234,
            'high_limit': 1234,
            'code_length': 6,
        },
    },
)
@pytest.mark.now('2021-06-13T14:00:00Z')
async def test_generation_config(
        taxi_bank_authorization, mockserver, testpoint, phone_number_mock,
):
    @mockserver.json_handler(
        '/bank-communications/communications-internal/v1/send',
    )
    def _mock_communications_send(request):
        assert request.json['locale'] != ''
        return mockserver.make_response('{}', 200)

    @testpoint('code_generated')
    def _code_generated(data):
        assert data['code'] == '001234'

    response = await taxi_bank_authorization.post(
        'v1/authorization/v1/send_code',
        headers=common.get_headers(common.BANK_UID1, 'idempotency-key'),
        json={'track_id': PG_TRACK_ID1},
    )

    assert response.status_code == 200
    assert response.json() == {
        'status': 'OK',
        'retry_interval': 30,
        'code_format': 'DIGIT_4',
        'phone': common.PHONE_NUMBER1_MASKED,
    }


async def test_empty_locale_header(taxi_bank_authorization):
    response = await taxi_bank_authorization.post(
        'v1/authorization/v1/send_code',
        headers=common.get_headers(common.BANK_UID1, 'idempotency-key', ''),
        json={'track_id': PG_TRACK_ID1},
    )

    assert response.status_code == 400


@pytest.mark.parametrize(
    'session_status',
    [
        'not_authorized',
        'pin_token_reissue',
        'pin_token_retry',
        'pin_token_registration',
    ],
)
async def test_send_not_full_session_allow(
        taxi_bank_authorization, mockserver, session_status, phone_number_mock,
):
    @mockserver.json_handler(
        '/bank-communications/communications-internal/v1/send',
    )
    def _mock_communications_send(request):
        return {}

    headers = common.get_headers(common.BANK_UID1, 'idempotency-key')
    headers['X-YaBank-AuthorizedByAuthproxy'] = 'no'
    headers['X-YaBank-SessionStatus'] = session_status
    response = await taxi_bank_authorization.post(
        'v1/authorization/v1/send_code',
        headers=headers,
        json={'track_id': PG_TRACK_ID1},
    )

    assert response.status_code == 200


async def test_send_not_full_session_not_allow(taxi_bank_authorization):
    headers = common.get_headers(common.BANK_UID1, 'idempotency-key')
    headers['X-YaBank-AuthorizedByAuthproxy'] = 'no'
    headers['X-YaBank-SessionStatus'] = 'not_registered'
    response = await taxi_bank_authorization.post(
        'v1/authorization/v1/send_code',
        headers=headers,
        json={'track_id': PG_TRACK_ID1},
    )

    assert response.status_code == 401


@pytest.mark.now('2021-06-13T14:00:00Z')
async def test_track_not_found(taxi_bank_authorization, mockserver, testpoint):
    response = await taxi_bank_authorization.post(
        'v1/authorization/v1/send_code',
        headers=common.get_headers(common.BANK_UID1, 'idempotency-key'),
        json={'track_id': PG_TRACK_ID_NOT_CREATED},
    )

    assert response.status_code == 404
