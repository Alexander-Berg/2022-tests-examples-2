import json

import jwt
import pytest

from tests_bank_h2h import common

HANDLE_URL = '/h2h/v1/process_document'
MOCK_NOW = '2021-09-28T19:31:00.1+0000'
MOCK_DATE_NOW = '2021-09-28'
DOCUMENT_TYPE = 'yandex.pro.001'


def get_broken_invalid_format():
    body = common.get_document_body()
    body['instructions'][0]['money']['amount'] = '-12.3'
    return body


def get_broken_type_mismatch():
    body = common.get_document_body()
    body['instructions'][0]['money']['amount'] = 12.3
    return body


def get_broken_no_required_field():
    body = common.get_document_body()
    del body['instructions'][0]['money']['amount']
    return body


def get_other_document_body():
    body = common.get_document_body()
    body['instructions'][0]['money']['amount'] = '123'
    return body


def get_document_wrong_accessor_type():
    body = common.get_document_body()
    body['instructions'][0]['payment_type'] = 'PAYMENT_REQUIREMENT'
    return body


def default_stq_kwargs(sender, document_id):
    return {'sender': sender, 'document_id': document_id}


GOOD_TOKEN = jwt.encode(
    common.get_document_body(),
    common.JWT_VERIFIER_PRIVATE_KEY_ES256,
    algorithm='ES256',
)


@pytest.mark.now(MOCK_NOW)
async def test_handle_ok(taxi_bank_h2h, pgsql, stq):
    response = await taxi_bank_h2h.post(
        HANDLE_URL,
        headers=common.get_headers(),
        json={'document_jwt': GOOD_TOKEN},
    )
    assert response.status_code == 200
    response = response.json()
    expected_status_info = common.get_status_info()
    assert jwt.decode(
        response['response_jwt'],
        common.JWT_SIGNER_PUBLIC_KEY_RS256,
        algorithms=['RS256'],
    ) == {'status_info': expected_status_info}
    assert response['response']['status_info'] == expected_status_info
    document_pg = common.select_document(
        pgsql, common.SENDER, common.DOCUMENT_ID,
    )
    assert document_pg.sender == common.SENDER
    assert document_pg.id == common.DOCUMENT_ID
    assert document_pg.document == common.get_document_body()
    assert document_pg.document_jwt == GOOD_TOKEN
    assert document_pg.status_info == expected_status_info

    assert stq.bank_h2h_process_document_in_bank_core.times_called == 1


@pytest.mark.now(MOCK_NOW)
@pytest.mark.parametrize(
    'body',
    [
        get_broken_type_mismatch(),
        get_broken_no_required_field(),
        get_broken_invalid_format(),
    ],
)
async def test_handle_broken_body(taxi_bank_h2h, stq, body):
    token = jwt.encode(
        body, common.JWT_VERIFIER_PRIVATE_KEY_ES256, algorithm='ES256',
    )
    response = await taxi_bank_h2h.post(
        HANDLE_URL, headers=common.get_headers(), json={'document_jwt': token},
    )
    assert response.status_code == 400

    assert stq.bank_h2h_process_document_in_bank_core.times_called == 0


@pytest.mark.now(MOCK_NOW)
async def test_handle_no_public_key(taxi_bank_h2h, stq):
    token = jwt.encode(
        common.get_document_body(),
        common.JWT_VERIFIER_PRIVATE_KEY_RS256,
        algorithm='RS256',
    )
    response = await taxi_bank_h2h.post(
        HANDLE_URL, headers=common.get_headers(), json={'document_jwt': token},
    )
    assert response.status_code == 500

    assert stq.bank_h2h_process_document_in_bank_core.times_called == 0


# keys up to 2021-09-29
@pytest.mark.now('2021-09-28T23:59:59.999+0000')
async def test_handle_all_public_key_expired(taxi_bank_h2h, stq, mocked_time):
    response = await taxi_bank_h2h.post(
        HANDLE_URL,
        headers=common.get_headers(),
        json={'document_jwt': GOOD_TOKEN},
    )
    assert response.status_code == 200
    assert stq.bank_h2h_process_document_in_bank_core.times_called == 1

    mocked_time.sleep(1)

    response = await taxi_bank_h2h.post(
        HANDLE_URL,
        headers=common.get_headers(),
        json={'document_jwt': GOOD_TOKEN},
    )
    assert response.status_code == 400
    assert stq.bank_h2h_process_document_in_bank_core.times_called == 1


@pytest.mark.now(MOCK_NOW)
async def test_handle_unknown_sender(taxi_bank_h2h, stq):
    response = await taxi_bank_h2h.post(
        HANDLE_URL,
        headers=common.get_headers(sender='YANDEX_BANK'),
        json={'document_jwt': GOOD_TOKEN},
    )
    assert response.status_code == 400

    assert stq.bank_h2h_process_document_in_bank_core.times_called == 0


@pytest.mark.now(MOCK_NOW)
async def test_handle_idempotency_conflict(
        taxi_bank_h2h, stq, testpoint, pgsql,
):
    @testpoint('create_other_document')
    def _code_generated(data):
        common.insert_document(pgsql)

    response = await taxi_bank_h2h.post(
        HANDLE_URL,
        headers=common.get_headers(),
        json={'document_jwt': GOOD_TOKEN},
    )
    assert response.status_code == 500

    assert stq.bank_h2h_process_document_in_bank_core.times_called == 0


@pytest.mark.now(MOCK_NOW)
async def test_handle_idempotency_409(taxi_bank_h2h, stq, pgsql):
    common.insert_document(
        pgsql,
        document=json.dumps(get_other_document_body()),
        status_info=json.dumps(common.get_status_info()),
    )

    response = await taxi_bank_h2h.post(
        HANDLE_URL,
        headers=common.get_headers(),
        json={'document_jwt': GOOD_TOKEN},
    )
    assert response.status_code == 409

    assert stq.bank_h2h_process_document_in_bank_core.times_called == 0


@pytest.mark.now(MOCK_NOW)
async def test_handle_idempotency_200(taxi_bank_h2h, stq, pgsql):
    document_body = common.get_document_body()
    common.insert_document(
        pgsql,
        document=json.dumps(document_body),
        status_info=json.dumps(common.get_status_info()),
    )

    response = await taxi_bank_h2h.post(
        HANDLE_URL,
        headers=common.get_headers(),
        json={'document_jwt': GOOD_TOKEN},
    )
    assert response.status_code == 200

    assert stq.bank_h2h_process_document_in_bank_core.times_called == 1


@pytest.mark.now(MOCK_NOW)
@pytest.mark.parametrize(
    'inn', ['1234567890', '123456789012', '123456789a', '0000000000'],
)
async def test_handle_bad_inn(taxi_bank_h2h, stq, pgsql, inn):
    document_body = common.get_document_body()
    document_body['instructions'][0]['creditor']['person']['tin'] = inn
    token = jwt.encode(
        document_body,
        common.JWT_VERIFIER_PRIVATE_KEY_ES256,
        algorithm='ES256',
    )

    response = await taxi_bank_h2h.post(
        HANDLE_URL, headers=common.get_headers(), json={'document_jwt': token},
    )
    assert response.status_code == 400

    assert stq.bank_h2h_process_document_in_bank_core.times_called == 0


def repair_enum_accessor_type(instruction_list):
    def cast(accessor_type):
        if accessor_type == 'EXTERNAL_WALLET_ID':
            return 'ELECTRONIC_PAYMENT_ACCESSOR'
        if accessor_type == 'ACCOUNT_NUMBER':
            return 'ACCOUNT'
        return None

    for instruction in instruction_list:
        if instruction.get('debtor', None) is not None:
            instruction['debtor']['accessor']['type'] = cast(
                instruction['debtor']['accessor']['type'],
            )
        if instruction.get('creditor', None) is not None:
            instruction['creditor']['accessor']['type'] = cast(
                instruction['creditor']['accessor']['type'],
            )

    return instruction_list


@pytest.mark.now(MOCK_NOW)
async def test_stq_ok(pgsql, stq_runner, bank_core_tps):
    sender = common.SENDER
    document_id = common.DOCUMENT_ID
    body = common.get_document_body()
    common.insert_document(
        pgsql,
        document=json.dumps(body),
        status_info=json.dumps(common.get_status_info()),
    )
    await stq_runner.bank_h2h_process_document_in_bank_core.call(
        task_id=f'process_document_in_bank_core_{sender}_{document_id}',
        kwargs=default_stq_kwargs(sender, document_id),
        expect_fail=False,
    )
    document_pg = common.select_document(pgsql, sender, document_id)
    assert document_pg.status_info == {
        'instruction_statuses': [
            {
                'instruction_id': '1',
                'original_money': {'amount': '1234.56', 'currency': 'RUB'},
                'status': common.STATUS_NEW,
                'status_history': [
                    {
                        'date': MOCK_DATE_NOW,
                        'new_status': common.STATUS_ACCEPTED,
                    },
                    {
                        'date': MOCK_DATE_NOW,
                        'new_status': common.STATUS_NEW,
                        'old_status': common.STATUS_ACCEPTED,
                    },
                ],
            },
            {
                'instruction_id': '2',
                'original_money': {'amount': '234.56', 'currency': 'USD'},
                'status': common.STATUS_FAILED,
                'status_history': [
                    {
                        'date': MOCK_DATE_NOW,
                        'new_status': common.STATUS_ACCEPTED,
                    },
                    {
                        'date': MOCK_DATE_NOW,
                        'new_status': common.STATUS_FAILED,
                        'old_status': common.STATUS_ACCEPTED,
                    },
                ],
            },
        ],
    }

    assert bank_core_tps.document_execute_handler.times_called == 1
    core_request = bank_core_tps.document_execute_request
    assert core_request == {
        'type': DOCUMENT_TYPE,
        'sender': sender,
        'sender_reference': document_id,
        'notification_channels': [
            {
                'channel': 'stq',
                'destination': (
                    'bank_h2h_update_document_status_from_bank_core'
                ),
                'params': {
                    'task_id': (
                        f'update_document_status_{sender}_{document_id}'
                    ),
                },
            },
        ],
        'instructions': repair_enum_accessor_type(body['instructions']),
    }


@pytest.mark.now(MOCK_NOW)
async def test_stq_core_tps_failed(mockserver, pgsql, stq_runner):
    @mockserver.json_handler('/bank-core-tps/v2/document/internal')
    def document_execute(request):
        return mockserver.make_response(status=500)

    sender = common.SENDER
    document_id = common.DOCUMENT_ID
    body = common.get_document_body()
    common.insert_document(
        pgsql,
        document=json.dumps(body),
        status_info=json.dumps(common.get_status_info()),
    )
    await stq_runner.bank_h2h_process_document_in_bank_core.call(
        task_id=f'process_document_in_bank_core_{sender}_{document_id}',
        kwargs=default_stq_kwargs(sender, document_id),
        expect_fail=True,
    )
    document_pg = common.select_document(pgsql, sender, document_id)
    assert document_pg.status_info == common.get_status_info()

    assert document_execute.times_called == 2


@pytest.mark.now(MOCK_NOW)
async def test_stq_document_not_found(stq_runner, bank_core_tps):
    sender = common.SENDER
    document_id = 'other_document_id'
    await stq_runner.bank_h2h_process_document_in_bank_core.call(
        task_id=f'process_document_in_bank_core_{sender}_{document_id}',
        kwargs=default_stq_kwargs(sender, document_id),
        expect_fail=True,
    )

    assert bank_core_tps.document_execute_handler.times_called == 0


@pytest.mark.now(MOCK_NOW)
@pytest.mark.config(BANK_H2H_CLIENT_TO_ACCOUNT_NUMBERS={})
async def test_handle_unknown_client(taxi_bank_h2h, pgsql, stq):
    response = await taxi_bank_h2h.post(
        HANDLE_URL,
        headers=common.get_headers(),
        json={'document_jwt': GOOD_TOKEN},
    )
    assert response.status_code == 400


@pytest.mark.now(MOCK_NOW)
@pytest.mark.config(BANK_H2H_CLIENT_TO_ACCOUNT_NUMBERS={'YANDEX_PRO': []})
async def test_handle_account_not_in_config(taxi_bank_h2h, pgsql, stq):
    response = await taxi_bank_h2h.post(
        HANDLE_URL,
        headers=common.get_headers(),
        json={'document_jwt': GOOD_TOKEN},
    )
    assert response.status_code == 400


@pytest.mark.now(MOCK_NOW)
async def test_handle_account_wrong_type(taxi_bank_h2h, pgsql, stq):
    body = get_document_wrong_accessor_type()
    token = jwt.encode(
        body, common.JWT_VERIFIER_PRIVATE_KEY_ES256, algorithm='ES256',
    )
    response = await taxi_bank_h2h.post(
        HANDLE_URL, headers=common.get_headers(), json={'document_jwt': token},
    )
    assert response.status_code == 400
    assert response.json()['message'] == 'accessor should be ACCOUNT_NUMBER'
