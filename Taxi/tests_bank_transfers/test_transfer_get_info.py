import uuid

import pytest

from tests_bank_transfers import common
from tests_bank_transfers import db_helpers


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
        '/v1/transfers/v1/transfer/get_info',
        headers=headers,
        json={'transfer_id': 'e493fa8c-a742-4bfb-96e7-27126d0a9a15'},
    )
    assert response.status_code == 401


async def test_wrong_transfer_id_format(taxi_bank_transfers):
    response = await taxi_bank_transfers.post(
        '/v1/transfers/v1/transfer/get_info',
        headers=common.build_headers(),
        json={'transfer_id': 'e493fa8c'},
    )
    assert response.status_code == 400


async def test_transfer_not_found(taxi_bank_transfers):
    response = await taxi_bank_transfers.post(
        '/v1/transfers/v1/transfer/get_info',
        headers=common.build_headers(),
        json={'transfer_id': 'e493fa8c-a742-4bfb-96e7-27126d0a9a15'},
    )
    assert response.status_code == 404


async def test_buid_not_found(taxi_bank_transfers, pgsql):
    transfer_id = db_helpers.insert_transfer(pgsql)
    response = await taxi_bank_transfers.post(
        '/v1/transfers/v1/transfer/get_info',
        headers=common.build_headers(
            buid='e493fa8c-a742-4bfb-96e7-27126d0a9a15',
        ),
        json={'transfer_id': transfer_id},
    )
    assert response.status_code == 404


@pytest.mark.parametrize(
    'transfer_status, response_status',
    (
        ('CREATED', 'PROCESSING'),
        ('PROCESSING', 'PROCESSING'),
        ('FAILED', 'FAILED'),
        ('SUCCESS', 'SUCCESS'),
    ),
)
async def test_ok(
        taxi_bank_transfers,
        bank_core_faster_payments_mock,
        pgsql,
        transfer_status,
        response_status,
):
    transfer_id = db_helpers.insert_transfer(
        pgsql, amount='1000', status=transfer_status, comment='Комментарий',
    )
    response = await taxi_bank_transfers.post(
        '/v1/transfers/v1/transfer/get_info',
        headers=common.build_headers(),
        json={'transfer_id': transfer_id},
    )
    assert response.status_code == 200
    assert response.json()['info']['transfer_id'] == transfer_id
    assert response.json()['info']['agreement_id'] == common.TEST_AGREEMENT_ID
    assert response.json()['info']['bank_info']['bank_id'] == common.TINKOFF
    assert response.json()['info']['bank_info']['title'] == 'Тинькофф'
    assert (
        response.json()['info']['receiver']['phone'] == common.RECEIVER_PHONE_1
    )
    assert (
        response.json()['info']['receiver']['name'] == common.RECEIVER_NAME_1
    )
    assert response.json()['info']['money']['amount'] == '1000'
    assert response.json()['info']['money']['currency'] == 'RUB'
    assert 'fee' not in response.json()['info']
    assert response.json()['info']['comment'] == 'Комментарий'
    assert response.json()['info']['result']['status'] == response_status


@pytest.mark.parametrize('status', ['PROCESSING', 'FAILED', 'SUCCESS'])
async def test_security(taxi_bank_transfers, pgsql, status):
    transfer_id = db_helpers.insert_transfer(
        pgsql,
        receiver_phone=common.RECEIVER_PHONE_1,
        status=status,
        buid=common.TEST_BANK_UID,
        amount='150',
    )

    # different buids in transfer and request
    params = {
        'transfer_id': transfer_id,
        'receiver_phone': common.RECEIVER_PHONE_1,
    }
    response = await taxi_bank_transfers.post(
        '/v1/transfers/v1/transfer/get_info',
        headers=common.build_headers(buid=str(uuid.uuid4())),
        json=params,
    )
    assert response.status_code == 404
