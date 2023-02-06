import uuid

import jwt
import pytest

from tests_bank_h2h import common

HANDLE_URL = '/h2h/v1/get_statement_file'
MOCK_NOW = '2021-09-28T19:31:00.100+00:00'


def get_body(file_id):
    result = {}
    if file_id is not None:
        result['file_id'] = file_id
    return result


def good_token(file_id):
    return jwt.encode(
        get_body(file_id),
        common.JWT_VERIFIER_PRIVATE_KEY_ES256,
        algorithm='ES256',
    )


@pytest.mark.now(MOCK_NOW)
async def test_get_statement_file(taxi_bank_h2h, s3_mock, pgsql):
    file_id = '9782839d-8b85-44fc-9b80-bd7a1201ca25'
    common.insert_statement(
        pgsql,
        str(uuid.uuid4()),
        status='SUCCESS',
        sender=common.SENDER,
        account='1234',
        date_from='2022-05-01',
        date_to='2022-05-31',
        file_name='file_name',
        file_name_id=file_id,
    )

    response = await taxi_bank_h2h.post(
        HANDLE_URL,
        headers=common.get_headers(),
        json={'request_jwt': good_token(file_id)},
    )
    assert response.status_code == 200
    assert response.content == b'file_content'
    assert s3_mock.s3_handle.times_called == 1


@pytest.mark.now(MOCK_NOW)
async def test_get_statement_file_not_found(taxi_bank_h2h):
    response = await taxi_bank_h2h.post(
        HANDLE_URL,
        headers=common.get_headers(),
        json={
            'request_jwt': good_token('e38c0309-2ce1-4054-8f6c-05fa19ede9cd'),
        },
    )
    assert response.status_code == 404


@pytest.mark.now(MOCK_NOW)
async def test_get_statement_file_no_file_name(taxi_bank_h2h, pgsql):
    file_id = '9782839d-8b85-44fc-9b80-bd7a1201ca25'
    common.insert_statement(
        pgsql,
        str(uuid.uuid4()),
        status='SUCCESS',
        sender=common.SENDER,
        account='1234',
        date_from='2022-05-01',
        date_to='2022-05-31',
        file_name_id=file_id,
    )

    response = await taxi_bank_h2h.post(
        HANDLE_URL,
        headers=common.get_headers(),
        json={'request_jwt': good_token(file_id)},
    )
    assert response.status_code == 500


@pytest.mark.now(MOCK_NOW)
@pytest.mark.parametrize(
    'type_of_broke', ['type_mismatch', 'no_required_field', 'invalid_format'],
)
async def test_get_statement_file_non_uuid_id(taxi_bank_h2h, type_of_broke):
    if type_of_broke == 'type_mismatch':
        file_id = 1234
    elif type_of_broke == 'no_required_field':
        file_id = None
    elif type_of_broke == 'invalid_format':
        file_id = '123'
    response = await taxi_bank_h2h.post(
        HANDLE_URL,
        headers=common.get_headers(),
        json={'request_jwt': good_token(file_id)},
    )
    assert response.status_code == 400


@pytest.mark.now(MOCK_NOW)
async def test_get_statement_file_no_public_key(taxi_bank_h2h):
    token = jwt.encode(
        get_body(''), common.JWT_VERIFIER_PRIVATE_KEY_RS256, algorithm='RS256',
    )
    response = await taxi_bank_h2h.post(
        HANDLE_URL, headers=common.get_headers(), json={'request_jwt': token},
    )
    assert response.status_code == 500


# keys up to 2021-09-29
@pytest.mark.now('2021-09-28T23:59:59.999+00:00')
async def test_get_statement_file_all_public_key_expired(
        taxi_bank_h2h, pgsql, mocked_time, s3_mock,
):
    file_id = '9782839d-8b85-44fc-9b80-bd7a1201ca25'
    common.insert_statement(
        pgsql,
        str(uuid.uuid4()),
        status='SUCCESS',
        sender=common.SENDER,
        account='1234',
        date_from='2022-05-01',
        date_to='2022-05-31',
        file_name='file_name',
        file_name_id=file_id,
    )

    response = await taxi_bank_h2h.post(
        HANDLE_URL,
        headers=common.get_headers(),
        json={'request_jwt': good_token(file_id)},
    )
    assert response.status_code == 200
    assert s3_mock.s3_handle.times_called == 1

    mocked_time.sleep(1)

    response = await taxi_bank_h2h.post(
        HANDLE_URL,
        headers=common.get_headers(),
        json={'request_jwt': good_token(file_id)},
    )
    assert response.status_code == 400
    assert s3_mock.s3_handle.times_called == 1


@pytest.mark.now(MOCK_NOW)
async def test_get_statement_file_unknown_sender(taxi_bank_h2h):
    response = await taxi_bank_h2h.post(
        HANDLE_URL,
        headers=common.get_headers(sender='YANDEX_BANK'),
        json={'request_jwt': good_token('')},
    )
    assert response.status_code == 400
