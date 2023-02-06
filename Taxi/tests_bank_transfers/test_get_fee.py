import uuid

import pytest

from tests_bank_transfers import common
from tests_bank_transfers import db_helpers


def build_params(
        transfer_id='e493fa8c-a742-4bfb-96e7-27126d0a9a15', amount='100.05',
):
    return {
        'transfer_id': transfer_id,
        'money': {'amount': amount, 'currency': 'RUB'},
    }


@pytest.mark.parametrize(
    'headers',
    [
        ({}),
        (
            {
                'X-YaBank-SessionUUID': common.TEST_SESSION_UUID,
                'X-Yandex-UID': common.TEST_YANDEX_UID,
                'X-YaBank-PhoneID': common.TEST_PHONE_ID,
                'X-Request-Language': common.TEST_LOCALE,
            }
        ),
    ],
)
async def test_not_authorized(taxi_bank_transfers, headers):
    response = await taxi_bank_transfers.post(
        '/v1/transfers/v1/transfer/get_fee',
        headers=headers,
        json=build_params(),
    )
    assert response.status_code == 401


async def test_wrong_transfer_id_format(taxi_bank_transfers):
    response = await taxi_bank_transfers.post(
        '/v1/transfers/v1/transfer/get_fee',
        headers=common.build_headers(),
        json=build_params(transfer_id='e493fa8c'),
    )
    assert response.status_code == 400


async def test_wrong_amount_format(taxi_bank_transfers):
    response = await taxi_bank_transfers.post(
        '/v1/transfers/v1/transfer/get_fee',
        headers=common.build_headers(),
        json=build_params(amount='100.001'),
    )
    assert response.status_code == 400


async def test_not_found(taxi_bank_transfers):
    response = await taxi_bank_transfers.post(
        '/v1/transfers/v1/transfer/get_fee',
        headers=common.build_headers(),
        json=build_params(),
    )
    assert response.status_code == 404


async def test_buid_not_found(
        taxi_bank_transfers, bank_core_faster_payments_mock, pgsql,
):
    transfer_id = db_helpers.insert_transfer(pgsql)
    response = await taxi_bank_transfers.post(
        '/v1/transfers/v1/transfer/get_fee',
        headers=common.build_headers(
            buid='e493fa8c-a742-4bfb-96e7-27126d0a9a15',
        ),
        json=build_params(transfer_id),
    )
    assert response.status_code == 404


async def test_wrong_transfer_status(
        taxi_bank_transfers, bank_core_faster_payments_mock, pgsql,
):
    transfer_id = db_helpers.insert_transfer(pgsql, status='SUCCESS')
    response = await taxi_bank_transfers.post(
        '/v1/transfers/v1/transfer/get_fee',
        headers=common.build_headers(),
        json=build_params(transfer_id),
    )
    assert response.status_code == 404


async def test_wrong_currency(
        taxi_bank_transfers, bank_core_faster_payments_mock, pgsql,
):
    transfer_id = db_helpers.insert_transfer(pgsql)
    params = build_params(transfer_id)
    params['money']['currency'] = 'USD'
    response = await taxi_bank_transfers.post(
        '/v1/transfers/v1/transfer/get_fee',
        headers=common.build_headers(),
        json=params,
    )
    assert response.status_code == 404


@pytest.mark.parametrize(
    'amount, error',
    [
        (1, 'Как минимум 10\xa0\u20BD'),
        (100, None),
        # amount < balance < transaction_limit < month_limit
        (1100, 'Недостаточно средств на счёте'),
        # amount < transaction_limit < month_limit < balance
        (1400, 'Нельзя переводить более 1370\xa0\u20BD за одну операцию'),
        # amount < month_limit < balance = transaction_limit
        (90000, 'Больше возможного в этом месяце'),
    ],
)
async def test_ok(
        taxi_bank_transfers,
        bank_core_faster_payments_mock,
        bank_core_statement_mock,
        pgsql,
        amount,
        error,
):
    if amount > 1100:
        bank_core_statement_mock.set_balance('100000')
    if amount > 1400:
        bank_core_statement_mock.set_transaction_limit('100000')
    transfer_id = db_helpers.insert_transfer(pgsql)
    response = await taxi_bank_transfers.post(
        '/v1/transfers/v1/transfer/get_fee',
        headers=common.build_headers(),
        json=build_params(transfer_id, amount=str(amount)),
    )
    assert response.status_code == 200
    if error:
        assert response.json()['error'] == error
    else:
        offer_id = response.json()['offer_id']
        offer = db_helpers.select_offer(pgsql, offer_id, transfer_id)
        assert offer.amount == str(amount)
        assert offer.fee == '0'


async def test_security(taxi_bank_transfers, pgsql):
    transfer_id = db_helpers.insert_transfer(
        pgsql,
        receiver_phone=common.RECEIVER_PHONE_1,
        buid=common.TEST_BANK_UID,
    )
    # different buids in transfer and request
    response = await taxi_bank_transfers.post(
        '/v1/transfers/v1/transfer/get_fee',
        headers=common.build_headers(buid=str(uuid.uuid4())),
        json=build_params(transfer_id, amount='150'),
    )
    assert response.status_code == 404
