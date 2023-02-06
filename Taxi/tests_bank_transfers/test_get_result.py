import uuid

import pytest

from tests_bank_transfers import common
from tests_bank_transfers import db_helpers


def buid_params(transfer_id='e493fa8c-a742-4bfb-96e7-27126d0a9a15'):
    return {'transfer_id': transfer_id}


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
        '/v1/transfers/v1/transfer/get_result',
        headers=headers,
        json=buid_params(),
    )
    assert response.status_code == 401


async def test_wrong_transfer_id_format(taxi_bank_transfers):
    response = await taxi_bank_transfers.post(
        '/v1/transfers/v1/transfer/get_result',
        headers=common.build_headers(),
        json=buid_params(transfer_id='e493fa8c'),
    )
    assert response.status_code == 400


async def test_not_found(taxi_bank_transfers):
    response = await taxi_bank_transfers.post(
        '/v1/transfers/v1/transfer/get_result',
        headers=common.build_headers(),
        json=buid_params(),
    )
    assert response.status_code == 404


async def test_buid_not_found(taxi_bank_transfers, pgsql):
    transfer_id = db_helpers.insert_transfer(pgsql)
    response = await taxi_bank_transfers.post(
        '/v1/transfers/v1/transfer/get_result',
        headers=common.build_headers(
            buid='e493fa8c-a742-4bfb-96e7-27126d0a9a15',
        ),
        json=buid_params(transfer_id),
    )
    assert response.status_code == 404


@pytest.mark.parametrize(
    'transfer_type, db_status, status, errors, locale, message, description',
    [
        (
            'C2C',
            'CREATED',
            'PROCESSING',
            [],
            'ru',
            'Перевод в обработке',
            f'105,51\xa0\u20BD на {common.RECEIVER_PHONE_1_F}\n'
            f'{common.SHORT_RECEIVER_NAME_1} в Тинькофф',
        ),
        (
            'C2C',
            'PROCESSING',
            'PROCESSING',
            [],
            'ru',
            'Перевод в обработке',
            f'105,51\xa0\u20BD на {common.RECEIVER_PHONE_1_F}\n'
            f'{common.SHORT_RECEIVER_NAME_1} в Тинькофф',
        ),
        (
            'C2C',
            'PROCESSING',
            'PROCESSING',
            [],
            'en',
            'Transfer in processing',
            f'\u20BD\xa0105.51 to {common.RECEIVER_PHONE_1_F}\n'
            f'{common.SHORT_RECEIVER_NAME_1} in Tinkoff',
        ),
        (
            'C2C',
            'SUCCESS',
            'SUCCESS',
            [],
            'ru',
            '−105,51\xa0\u20BD',
            f'{common.RECEIVER_PHONE_1_F}\n'
            f'{common.SHORT_RECEIVER_NAME_1} в Тинькофф',
        ),
        (
            'C2C',
            'SUCCESS',
            'SUCCESS',
            [],
            'en',
            '−\u20BD\xa0105.51',
            f'{common.RECEIVER_PHONE_1_F}\n'
            f'{common.SHORT_RECEIVER_NAME_1} in Tinkoff',
        ),
        (
            'C2C',
            'FAILED',
            'FAILED',
            ['500', 'FCB-1000'],
            'ru',
            'Не получилось перевести деньги',
            f'105,51\xa0\u20BD на {common.RECEIVER_PHONE_1_F}\n'
            f'{common.SHORT_RECEIVER_NAME_1} в Тинькофф',
        ),
        (
            'C2C',
            'FAILED',
            'FAILED',
            ['500', 'FCB-1000'],
            'en',
            'Failed to transfer money',
            f'\u20BD\xa0105.51 to {common.RECEIVER_PHONE_1_F}\n'
            f'{common.SHORT_RECEIVER_NAME_1} in Tinkoff',
        ),
        (
            'ME2ME',
            'CREATED',
            'PROCESSING',
            [],
            'ru',
            'Перевод в обработке',
            f'105,51\xa0\u20BD на {common.RECEIVER_PHONE_1_F}\n'
            f'{common.SHORT_RECEIVER_NAME_1} в Тинькофф',
        ),
        (
            'ME2ME',
            'PROCESSING',
            'PROCESSING',
            [],
            'ru',
            'Перевод в обработке',
            f'105,51\xa0\u20BD на {common.RECEIVER_PHONE_1_F}\n'
            f'{common.SHORT_RECEIVER_NAME_1} в Тинькофф',
        ),
        (
            'ME2ME',
            'PROCESSING',
            'PROCESSING',
            [],
            'en',
            'Transfer in processing',
            f'\u20BD\xa0105.51 to {common.RECEIVER_PHONE_1_F}\n'
            f'{common.SHORT_RECEIVER_NAME_1} in Tinkoff',
        ),
        (
            'ME2ME',
            'SUCCESS',
            'SUCCESS',
            [],
            'ru',
            '105,51\xa0\u20BD',
            'Поступят после подтверждения в приложении вашего банка',
        ),
        (
            'ME2ME',
            'SUCCESS',
            'SUCCESS',
            [],
            'en',
            '\u20BD\xa0105.51',
            'Will be received after confirmation in your bank\'s application',
        ),
        (
            'ME2ME',
            'FAILED',
            'FAILED',
            ['500', 'FCB-1000'],
            'ru',
            'Не получилось пополнить счет',
            f'105,51\xa0\u20BD из Тинькофф',
        ),
        (
            'ME2ME',
            'FAILED',
            'FAILED',
            ['500', 'FCB-1000'],
            'en',
            'Some error when adding funds to the account',
            f'\u20BD\xa0105.51 from Tinkoff',
        ),
    ],
)
async def test_ok(
        taxi_bank_transfers,
        pgsql,
        db_status,
        status,
        errors,
        locale,
        message,
        description,
        transfer_type,
):
    transfer_id = db_helpers.insert_transfer(
        pgsql,
        status=db_status,
        errors=errors,
        amount='105.51',
        transfer_type=transfer_type,
    )
    response = await taxi_bank_transfers.post(
        '/v1/transfers/v1/transfer/get_result',
        headers=common.build_headers(language=locale),
        json=buid_params(transfer_id),
    )
    assert response.status_code == 200
    assert response.json()['result'] == {
        'status': status,
        'message': message,
        'description': description,
    }


@pytest.mark.parametrize('status', ['PROCESSING', 'FAILED', 'SUCCESS'])
async def test_security(taxi_bank_transfers, pgsql, status):
    transfer_id = db_helpers.insert_transfer(
        pgsql,
        receiver_phone=common.RECEIVER_PHONE_1,
        buid=common.TEST_BANK_UID,
        amount='105.51',
    )
    # different buids in transfer and request
    response = await taxi_bank_transfers.post(
        '/v1/transfers/v1/transfer/get_result',
        headers=common.build_headers(buid=str(uuid.uuid4())),
        json=buid_params(transfer_id),
    )
    assert response.status_code == 404


@pytest.mark.parametrize('transfer_type', ['ME2ME', 'C2C'])
@pytest.mark.parametrize(
    'errors, error_message',
    [
        (['FCB-1037'], 'Переводы СБП временно недоступны'),
        (
            ['FCB-1038'],
            'Перевод по выбранным реквизитам недоступен, уточните реквизиты у получателя',
        ),
        (['FCB-1039'], 'Что-то пошло не так, попробуйте позже'),
        (['FCB-1040'], 'Что-то пошло не так, попробуйте позже'),
        (['500'], 'Не получилось перевести деньги'),
    ],
)
async def test_fcb_errors(
        taxi_bank_transfers, pgsql, error_message, errors, transfer_type,
):

    transfer_id = db_helpers.insert_transfer(
        pgsql,
        status='FAILED',
        errors=errors,
        amount='105.51',
        transfer_type=transfer_type,
    )
    response = await taxi_bank_transfers.post(
        '/v1/transfers/v1/transfer/get_result',
        headers=common.build_headers(),
        json=buid_params(transfer_id),
    )
    assert response.status_code == 200
    description = f'105,51\xa0\u20BD на {common.RECEIVER_PHONE_1_F}\n{common.SHORT_RECEIVER_NAME_1} в Тинькофф'
    if transfer_type == 'ME2ME':
        if errors == ['500']:
            error_message = 'Не получилось пополнить счет'
        description = f'105,51\xa0\u20BD из Тинькофф'
    assert response.json()['result'] == {
        'status': 'FAILED',
        'message': error_message,
        'description': description,
    }
    transfer = db_helpers.select_transfer(pgsql, transfer_id)
    assert transfer.status == 'FAILED'
