import uuid

import jwt
import pytest

from tests_bank_h2h import common

HANDLE_URL = '/h2h/v1/get_statement_status'
MOCK_NOW = '2021-09-28T19:31:00.100+00:00'


def get_body(statement_id):
    result = {}
    if statement_id is not None:
        result['statement_id'] = statement_id
    return result


def good_token(statement_id):
    return jwt.encode(
        get_body(statement_id),
        common.JWT_VERIFIER_PRIVATE_KEY_ES256,
        algorithm='ES256',
    )


@pytest.mark.now(MOCK_NOW)
async def test_get_statement_status(taxi_bank_h2h, pgsql):
    statement_id = common.insert_statement(
        pgsql,
        str(uuid.uuid4()),
        status='SUCCESS',
        sender=common.SENDER,
        account='1234',
        date_from='2022-05-01',
        date_to='2022-05-31',
        file_name='file_name',
        file_name_id='9782839d-8b85-44fc-9b80-bd7a1201ca25',
    )

    response = await taxi_bank_h2h.post(
        HANDLE_URL,
        headers=common.get_headers(),
        json={'request_jwt': good_token(statement_id)},
    )
    assert response.status_code == 200
    expected_response = {
        'status': 'SUCCESS',
        'info': {
            'statement_id': statement_id,
            'account': '1234',
            'date_from': '2022-05-01',
            'date_to': '2022-05-31',
        },
        'success_response': {
            'file_id': '9782839d-8b85-44fc-9b80-bd7a1201ca25',
        },
    }
    response = response.json()
    assert response['response'] == expected_response
    assert (
        jwt.decode(
            response['response_jwt'],
            common.JWT_SIGNER_PUBLIC_KEY_RS256,
            algorithms=['RS256'],
        )
        == expected_response
    )


@pytest.mark.now(MOCK_NOW)
async def test_get_statement_status_not_found(taxi_bank_h2h):
    response = await taxi_bank_h2h.post(
        HANDLE_URL,
        headers=common.get_headers(),
        json={
            'request_jwt': good_token('e38c0309-2ce1-4054-8f6c-05fa19ede9cd'),
        },
    )
    assert response.status_code == 404


@pytest.mark.now(MOCK_NOW)
@pytest.mark.parametrize(
    'type_of_broke', ['type_mismatch', 'no_required_field', 'invalid_format'],
)
async def test_get_statement_status_broken_body(taxi_bank_h2h, type_of_broke):
    if type_of_broke == 'type_mismatch':
        statement_id = 1234
    elif type_of_broke == 'no_required_field':
        statement_id = None
    elif type_of_broke == 'invalid_format':
        statement_id = '123'
    response = await taxi_bank_h2h.post(
        HANDLE_URL,
        headers=common.get_headers(),
        json={'request_jwt': good_token(statement_id)},
    )
    assert response.status_code == 400


@pytest.mark.now(MOCK_NOW)
async def test_get_statement_no_public_key(taxi_bank_h2h):
    token = jwt.encode(
        get_body(''), common.JWT_VERIFIER_PRIVATE_KEY_RS256, algorithm='RS256',
    )
    response = await taxi_bank_h2h.post(
        HANDLE_URL, headers=common.get_headers(), json={'request_jwt': token},
    )
    assert response.status_code == 500


# keys up to 2021-09-29
@pytest.mark.now('2021-09-28T23:59:59.999+00:00')
async def test_get_statement_all_public_key_expired(
        taxi_bank_h2h, pgsql, mocked_time,
):
    statement_id = common.insert_statement(
        pgsql,
        str(uuid.uuid4()),
        status='SUCCESS',
        sender=common.SENDER,
        account='1234',
        date_from='2022-05-01',
        date_to='2022-05-31',
        file_name='file_name',
        file_name_id='9782839d-8b85-44fc-9b80-bd7a1201ca25',
    )

    response = await taxi_bank_h2h.post(
        HANDLE_URL,
        headers=common.get_headers(),
        json={'request_jwt': good_token(statement_id)},
    )
    assert response.status_code == 200

    mocked_time.sleep(1)

    response = await taxi_bank_h2h.post(
        HANDLE_URL,
        headers=common.get_headers(),
        json={'request_jwt': good_token(statement_id)},
    )
    assert response.status_code == 400


@pytest.mark.now(MOCK_NOW)
async def test_get_statement_unknown_sender(taxi_bank_h2h):
    response = await taxi_bank_h2h.post(
        HANDLE_URL,
        headers=common.get_headers(sender='YANDEX_BANK'),
        json={'request_jwt': good_token('')},
    )
    assert response.status_code == 400
