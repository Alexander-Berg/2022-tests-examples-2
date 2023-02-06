import pytest

from tests_bank_authorization import common


def select_code(pgsql, code_id):
    cursor = pgsql['bank_authorization'].cursor()
    cursor.execute(
        (
            f'SELECT code_hmac, key_id, '
            'idempotency_token, attempts_left, buid '
            f'FROM bank_authorization.codes '
            f'WHERE id = \'{code_id}\'::UUID'
        ),
    )
    return list(cursor)


@pytest.mark.now('2021-06-13T14:00:00Z')
async def test_generate_and_verify(
        taxi_bank_authorization,
        pgsql,
        mockserver,
        testpoint,
        risk_mock,
        phone_number_mock,
):
    generated_code = None

    @mockserver.json_handler(
        '/bank-communications/communications-internal/v1/send',
    )
    def _mock_communications_send(request):
        assert request.json['locale'] != ''
        assert request.json['template_parameters'] == {'code': generated_code}
        return mockserver.make_response('{}', 200)

    @testpoint('code_generated')
    def _code_generated(data):
        nonlocal generated_code
        generated_code = data['code']

    response = await taxi_bank_authorization.post(
        'authorization-internal/v1/create_track',
        json={'buid': common.BANK_UID1, 'operation_type': 'operation'},
        headers={'X-Idempotency-Token': 'idempotency-key'},
    )

    assert response.status_code == 200
    track_id = response.json()['track_id']

    response = await taxi_bank_authorization.post(
        'v1/authorization/v1/send_code',
        headers=common.get_headers(common.BANK_UID1, 'idempotency-key2'),
        json={'track_id': track_id},
    )

    assert response.status_code == 200
    assert response.json() == {
        'status': 'OK',
        'retry_interval': 30,
        'code_format': 'DIGIT_4',
        'phone': common.PHONE_NUMBER1_MASKED,
    }
    assert _mock_communications_send.times_called == 1

    response = await taxi_bank_authorization.post(
        'v1/authorization/v1/verify_code',
        headers=common.get_headers(common.BANK_UID1),
        json={'track_id': track_id, 'code': generated_code},
    )
    assert response.status_code == 200
    assert response.json()['verification_result'] == 'OK'
    assert response.json()['ok_data']['verification_token'] != ''


@pytest.mark.now('2021-06-13T14:00:00Z')
async def test_generate_and_verify_double_send(
        taxi_bank_authorization,
        pgsql,
        mockserver,
        testpoint,
        risk_mock,
        phone_number_mock,
):
    generated_code_1 = None
    generated_code_2 = None

    @mockserver.json_handler(
        '/bank-communications/communications-internal/v1/send',
    )
    def _mock_communications_send(request):
        assert request.json['locale'] != ''
        template_parameters = request.json['template_parameters']
        assert template_parameters in [
            {'code': generated_code_1},
            {'code': generated_code_2},
        ]
        return mockserver.make_response('{}', 200)

    @testpoint('code_generated')
    def _code_generated(data):
        nonlocal generated_code_1
        nonlocal generated_code_2
        if generated_code_1 is None:
            generated_code_1 = data['code']
        else:
            generated_code_2 = data['code']
            assert generated_code_1 != generated_code_2

    response = await taxi_bank_authorization.post(
        'authorization-internal/v1/create_track',
        json={'buid': common.BANK_UID1, 'operation_type': 'operation'},
        headers={'X-Idempotency-Token': 'idempotency-key'},
    )

    assert response.status_code == 200
    track_id = response.json()['track_id']

    response = await taxi_bank_authorization.post(
        'v1/authorization/v1/send_code',
        headers=common.get_headers(common.BANK_UID1, 'idempotency-key2'),
        json={'track_id': track_id},
    )
    assert response.status_code == 200
    assert response.json() == {
        'status': 'OK',
        'retry_interval': 30,
        'code_format': 'DIGIT_4',
        'phone': common.PHONE_NUMBER1_MASKED,
    }
    assert _mock_communications_send.times_called == 1

    response = await taxi_bank_authorization.post(
        'v1/authorization/v1/send_code',
        headers=common.get_headers(common.BANK_UID1, 'idempotency-key3'),
        json={'track_id': track_id},
    )
    assert response.status_code == 200
    assert response.json() == {
        'status': 'OK',
        'retry_interval': 30,
        'code_format': 'DIGIT_4',
        'phone': common.PHONE_NUMBER1_MASKED,
    }
    assert _mock_communications_send.times_called == 2

    response = await taxi_bank_authorization.post(
        'v1/authorization/v1/verify_code',
        headers=common.get_headers(common.BANK_UID1),
        json={'track_id': track_id, 'code': generated_code_1},
    )
    assert response.status_code == 200
    assert response.json()['verification_result'] == 'FAIL'
    assert response.json()['fail_data']['result_code'] == 'CODE_MISMATCH'
    assert response.json()['fail_data']['attempts_left'] == 2

    response = await taxi_bank_authorization.post(
        'v1/authorization/v1/verify_code',
        headers=common.get_headers(common.BANK_UID1),
        json={'track_id': track_id, 'code': generated_code_2},
    )
    assert response.status_code == 200
    assert response.json()['verification_result'] == 'OK'
    assert response.json()['ok_data']['verification_token'] != ''
