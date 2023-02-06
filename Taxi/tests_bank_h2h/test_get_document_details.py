import json

import jwt
import pytest

from tests_bank_h2h import common

HANDLE_URL = '/h2h/v1/get_document_details'


def get_request():
    return {'document_id': common.DOCUMENT_ID}


def get_broken_no_required_field():
    return {'document': common.DOCUMENT_ID}


def get_broken_type_mismatch():
    return {'document_id': 123}


GOOD_TOKEN = jwt.encode(
    get_request(), common.JWT_VERIFIER_PRIVATE_KEY_ES256, algorithm='ES256',
)


@pytest.mark.now(common.MOCK_NOW)
async def test_get_document_details_ok(taxi_bank_h2h, pgsql):
    common.insert_document(
        pgsql, status_info=json.dumps(common.get_status_info()),
    )

    response = await taxi_bank_h2h.post(
        HANDLE_URL,
        headers=common.get_headers(),
        json={'request_jwt': GOOD_TOKEN},
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


@pytest.mark.now(common.MOCK_NOW)
async def test_get_document_details_not_found(taxi_bank_h2h):
    response = await taxi_bank_h2h.post(
        HANDLE_URL,
        headers=common.get_headers(),
        json={'request_jwt': GOOD_TOKEN},
    )
    assert response.status_code == 404


@pytest.mark.now(common.MOCK_NOW)
@pytest.mark.parametrize(
    'body', [get_broken_no_required_field(), get_broken_type_mismatch()],
)
async def test_handle_broken_body(taxi_bank_h2h, body):
    token = jwt.encode(
        body, common.JWT_VERIFIER_PRIVATE_KEY_ES256, algorithm='ES256',
    )
    response = await taxi_bank_h2h.post(
        HANDLE_URL, headers=common.get_headers(), json={'request_jwt': token},
    )
    assert response.status_code == 400


@pytest.mark.now(common.MOCK_NOW)
async def test_handle_no_public_key(taxi_bank_h2h):
    token = jwt.encode(
        get_request(),
        common.JWT_VERIFIER_PRIVATE_KEY_RS256,
        algorithm='RS256',
    )
    response = await taxi_bank_h2h.post(
        HANDLE_URL, headers=common.get_headers(), json={'request_jwt': token},
    )
    assert response.status_code == 500


# keys up to 2021-09-29
@pytest.mark.now('2021-09-28T23:59:59.999+0000')
async def test_handle_all_public_key_expired(
        taxi_bank_h2h, pgsql, mocked_time,
):
    common.insert_document(
        pgsql, status_info=json.dumps(common.get_status_info()),
    )

    response = await taxi_bank_h2h.post(
        HANDLE_URL,
        headers=common.get_headers(),
        json={'request_jwt': GOOD_TOKEN},
    )
    assert response.status_code == 200

    mocked_time.sleep(1)

    response = await taxi_bank_h2h.post(
        HANDLE_URL,
        headers=common.get_headers(),
        json={'request_jwt': GOOD_TOKEN},
    )
    assert response.status_code == 400


@pytest.mark.now(common.MOCK_NOW)
async def test_handle_unknown_sender(taxi_bank_h2h):
    response = await taxi_bank_h2h.post(
        HANDLE_URL,
        headers=common.get_headers(sender='YANDEX_BANK'),
        json={'document_jwt': GOOD_TOKEN},
    )
    assert response.status_code == 400
