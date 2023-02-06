import pytest

from tests_bank_topup import common

HANDLE_URL = '/topup-support/v1/get_pending_payments'
BUID = '52f542ed-5813-4c96-9775-3a40e4f8b490'


def get_body():
    return {'buid': BUID, 'limit': 100}


EXPECTED_PAYMENTS_STATUS = [
    ['aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaa12', 'PROCESSING'],
    ['aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaa11', 'PROCESSING'],
    ['aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaa10', 'PROCESSING'],
    ['aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaa04', 'PROCESSING'],
    ['aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaa03', 'PROCESSING'],
    ['aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaa02', 'PROCESSING'],
    ['aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaa01', 'PROCESSING'],
]


async def test_ok(taxi_bank_topup, access_control_mock):
    response = await taxi_bank_topup.post(
        HANDLE_URL, headers=common.get_support_headers(), json=get_body(),
    )
    json = response.json()
    assert response.status_code == 200
    assert 'cursor' not in json
    assert access_control_mock.handler_path == HANDLE_URL
    assert (
        common.get_pending_payments_status(json['payments'])
        == EXPECTED_PAYMENTS_STATUS
    )
    assert all(
        payment['payment_info']['image'] == 'image_url'
        for payment in json['payments']
    )


async def test_limit(taxi_bank_topup, access_control_mock):
    body = get_body()
    body['limit'] = 5
    response = await taxi_bank_topup.post(
        HANDLE_URL, headers=common.get_support_headers(), json=body,
    )
    json = response.json()
    assert response.status_code == 200
    assert (
        common.get_pending_payments_status(json['payments'])
        == EXPECTED_PAYMENTS_STATUS[:5]
    )


async def test_access_deny(
        taxi_bank_topup, bank_core_statement_mock, access_control_mock,
):
    body = get_body()
    headers = {'X-Bank-Token': 'deny'}

    response = await taxi_bank_topup.post(
        HANDLE_URL, headers=headers, json=body,
    )

    assert response.status_code == 401


@pytest.mark.parametrize(
    'locale, expected_name',
    [('en', 'Top up'), ('ru', 'Пополнение'), ('unknown', 'Пополнение')],
)
async def test_locale(
        taxi_bank_topup, access_control_mock, locale, expected_name,
):
    headers = common.get_support_headers()
    headers['X-Request-Language'] = locale

    response = await taxi_bank_topup.post(
        HANDLE_URL, headers=headers, json=get_body(),
    )
    json = response.json()

    assert response.status_code == 200
    assert json['payments'][0]['payment_info']['name'] == expected_name
