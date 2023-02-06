import pytest

from tests_bank_topup import common

HANDLE_URL = '/topup-support/v1/payment/get_info'
BUID = '52f542ed-5813-4c96-9775-3a40e4f8b490'


def get_body():
    return {'buid': BUID, 'payment_id': common.TEST_PAYMENT_ID}


@pytest.mark.parametrize(
    'payment_status, info_status',
    [
        ('CREATED', 'CREATED'),
        ('FAILED', 'FAILED'),
        ('REFUNDED', 'FAILED'),
        ('FAILED_SAVED', 'FAILED'),
        ('REFUNDED_SAVED', 'FAILED'),
        ('SUCCESS_SAVED', 'SUCCESS'),
        ('CLEARING', 'SUCCESS'),
        ('CLEARED', 'SUCCESS'),
        ('SUCCESS_SAVING', 'PROCESSING'),
        ('REFUNDED_SAVING', 'PROCESSING'),
        ('FAILED_SAVING', 'PROCESSING'),
        ('REFUNDING', 'PROCESSING'),
        ('PAYMENT_RECEIVED', 'PROCESSING'),
    ],
)
async def test_ok(
        pgsql,
        taxi_bank_topup,
        access_control_mock,
        payment_status,
        info_status,
):
    body = get_body()
    headers = common.get_support_headers()

    common.set_payment_status(pgsql, status=payment_status)

    response = await taxi_bank_topup.post(
        HANDLE_URL, json=body, headers=headers,
    )
    assert response.status_code == 200
    json = response.json()
    assert json['payment_info']['payment_id'] == common.TEST_PAYMENT_ID
    assert json['status'] == info_status
    assert json['payment_info']['image'] == 'image_url'
    assert json['payment_info']['money'] == {
        'amount': '100',
        'currency': 'RUB',
    }
    assert (
        json['payment_info']['creation_timestamp']
        == '2021-10-31T00:34:00.0+00:00'
    )
    assert access_control_mock.handler_path == HANDLE_URL


async def test_access_deny(
        taxi_bank_topup, bank_core_statement_mock, access_control_mock,
):
    body = get_body()
    headers = {'X-Bank-Token': 'deny'}

    response = await taxi_bank_topup.post(
        HANDLE_URL, headers=headers, json=body,
    )

    assert response.status_code == 401


async def test_not_found(taxi_bank_topup, access_control_mock):
    body = {
        'payment_id': 'd9abbfb7-84d4-44be-94b3-8f8ea7eb31d0',
        'buid': '52f542ed-5813-4c96-9775-3a40e4f8b491',
    }
    headers = common.get_support_headers()
    response = await taxi_bank_topup.post(
        HANDLE_URL, json=body, headers=headers,
    )
    assert response.status_code == 404


@pytest.mark.parametrize(
    'locale, topup',
    [('en', 'Top up'), ('ru', 'Пополнение'), ('unknown', 'Пополнение')],
)
async def test_tanker_locales(
        taxi_bank_topup,
        locale,
        topup,
        pgsql,
        taxi_config,
        access_control_mock,
):

    body = get_body()
    headers = common.get_support_headers()
    headers.update({'X-Request-Language': locale})
    response = await taxi_bank_topup.post(
        HANDLE_URL, json=body, headers=headers,
    )

    assert response.status_code == 200
    assert response.json()['payment_info']['name'] == topup


@pytest.mark.parametrize(
    'db_rrn, response_rrn', [(None, None), ('12345', '12345')],
)
async def test_rrn(
        taxi_bank_topup,
        pgsql,
        taxi_config,
        access_control_mock,
        db_rrn,
        response_rrn,
):
    common.set_rrn(pgsql, rrn=db_rrn)
    response = await taxi_bank_topup.post(
        HANDLE_URL, json=get_body(), headers=common.get_support_headers(),
    )
    assert response.status_code == 200
    if response_rrn:
        assert response.json()['rrn'] == response_rrn
    else:
        assert 'rrn' not in response.json()
