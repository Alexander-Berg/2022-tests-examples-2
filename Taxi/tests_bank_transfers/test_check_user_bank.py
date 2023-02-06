import uuid

import pytest

from tests_bank_transfers import common
from tests_bank_transfers import db_helpers

BUID_FPS_OFF = '7948e3a9-623c-4524-a390-9e4264d27a01'
TRANSFER_ID = 'e493fa8c-a742-4bfb-96e7-27126d0a9a15'

CHECK_BANK_REQUEST_V1 = '/v1/transfers/v1/faster/check_user_bank'
CHECK_BANK_REQUEST_V2 = '/v1/transfers/v2/faster/check_user_bank'


def build_params(transfer_id=TRANSFER_ID, bank_id=common.TINKOFF):
    return {'transfer_id': transfer_id, 'bank_id': bank_id}


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
@pytest.mark.parametrize(
    'request_str', [CHECK_BANK_REQUEST_V1, CHECK_BANK_REQUEST_V2],
)
async def test_not_authorized(taxi_bank_transfers, headers, request_str):
    if request_str == CHECK_BANK_REQUEST_V2:
        headers['X-Idempotency-Token'] = common.DEFAULT_IDEMPOTENCY_TOKEN
    response = await taxi_bank_transfers.post(
        request_str, headers=headers, json=build_params(),
    )
    assert response.status_code == 401


@pytest.mark.parametrize(
    'request_str', [CHECK_BANK_REQUEST_V1, CHECK_BANK_REQUEST_V2],
)
async def test_transfer_not_found(taxi_bank_transfers, request_str):
    response = await taxi_bank_transfers.post(
        request_str,
        headers=common.build_headers(
            idempotency_token=common.DEFAULT_IDEMPOTENCY_TOKEN,
        ),
        json=build_params(),
    )
    assert response.status_code == 404


@pytest.mark.parametrize(
    'request_str', [CHECK_BANK_REQUEST_V1, CHECK_BANK_REQUEST_V2],
)
async def test_wrong_transfer_id_format(taxi_bank_transfers, request_str):
    response = await taxi_bank_transfers.post(
        request_str,
        headers=common.build_headers(
            idempotency_token=common.DEFAULT_IDEMPOTENCY_TOKEN,
        ),
        json=build_params(transfer_id='e493fa8c'),
    )
    assert response.status_code == 400


@pytest.mark.parametrize(
    'request_str', [CHECK_BANK_REQUEST_V1, CHECK_BANK_REQUEST_V2],
)
async def test_buid_not_found(taxi_bank_transfers, pgsql, request_str):
    db_helpers.insert_transfer(pgsql)
    headers = common.build_headers(
        buid='e493fa8c-a742-4bfb-96e7-27126d0a9a15',
        idempotency_token=common.DEFAULT_IDEMPOTENCY_TOKEN,
    )
    response = await taxi_bank_transfers.post(
        request_str, headers=headers, json=build_params(),
    )
    assert response.status_code == 404


@pytest.mark.parametrize(
    'request_str', [CHECK_BANK_REQUEST_V1, CHECK_BANK_REQUEST_V2],
)
async def test_wrong_transfer_status(taxi_bank_transfers, pgsql, request_str):
    transfer_id = db_helpers.insert_transfer(pgsql, status='SUCCESS')
    params = build_params(transfer_id=transfer_id)
    response = await taxi_bank_transfers.post(
        request_str,
        headers=common.build_headers(
            idempotency_token=common.DEFAULT_IDEMPOTENCY_TOKEN,
        ),
        json=params,
    )
    assert response.status_code == 404


@pytest.mark.parametrize(
    'locale, note',
    [('ru', 'Не пользуется этим банком'), ('en', 'Doesn\'t use this bank')],
)
@pytest.mark.parametrize(
    'request_str', [CHECK_BANK_REQUEST_V1, CHECK_BANK_REQUEST_V2],
)
async def test_receiver_not_found(
        taxi_bank_transfers, pgsql, locale, note, request_str,
):
    transfer_id = db_helpers.insert_transfer(pgsql)
    params = build_params(transfer_id=transfer_id, bank_id=common.ROSDORBANK)
    response = await taxi_bank_transfers.post(
        request_str,
        headers=common.build_headers(
            language=locale,
            idempotency_token=common.DEFAULT_IDEMPOTENCY_TOKEN,
        ),
        json=params,
    )
    assert response.status_code == 200
    bank_check_response = {'error': note, 'status': 'NOT_FOUND'}
    assert (
        response.json()
        == {'status': 'SUCCESS', 'bank_check_result': bank_check_response}
        if request_str == CHECK_BANK_REQUEST_V2
        else bank_check_response
    )


@pytest.mark.parametrize(
    'amount, comment, request_id',
    [
        (None, None, None),
        ('123.45', None, common.CHECK_REQUEST_ID),
        ('123.45', 'Комментарий', common.CHECK_REQUEST_ID),
    ],
)
@pytest.mark.parametrize(
    'request_str', [CHECK_BANK_REQUEST_V1, CHECK_BANK_REQUEST_V2],
)
async def test_ok_not_to_yandex(
        taxi_bank_transfers, pgsql, amount, comment, request_id, request_str,
):
    transfer_id = db_helpers.insert_transfer(
        pgsql, amount=amount, comment=comment,
    )
    params = build_params(transfer_id=transfer_id)
    if amount:
        params['money'] = {'amount': '123.45', 'currency': 'RUB'}
    if comment:
        params['comment'] = comment

    response = await taxi_bank_transfers.post(
        request_str,
        headers=common.build_headers(
            idempotency_token=common.DEFAULT_IDEMPOTENCY_TOKEN,
        ),
        json=params,
    )
    assert response.status_code == 200
    bank_check_response = {
        'receiver_name': common.SHORT_RECEIVER_NAME_1,
        'status': 'FOUND',
        'header': common.get_default_response_header(),
    }
    assert (
        response.json()
        == {'status': 'SUCCESS', 'bank_check_result': bank_check_response}
        if request_str == CHECK_BANK_REQUEST_V2
        else bank_check_response
    )

    transfer = db_helpers.select_transfer(pgsql, transfer_id)
    assert transfer.receiver_bank_id == common.TINKOFF
    assert transfer.receiver_name == common.RECEIVER_NAME_1
    assert transfer.amount == amount
    assert transfer.comment == comment
    assert transfer.request_id == request_id


@pytest.mark.parametrize(
    'amount, error',
    [
        (1, 'Как минимум 10\xa0\u20BD'),
        (100, None),
        # balance < amount < transaction_limit < month_limit
        (1100, 'Недостаточно средств на счёте'),
        #  transaction_limit < amount < month_limit < balance
        (1400, 'Нельзя переводить более 1370\xa0\u20BD за одну операцию'),
        # month_limit < amount < balance = transaction_limit
        (90000, 'Больше возможного в этом месяце'),
    ],
)
@pytest.mark.parametrize(
    'request_str', [CHECK_BANK_REQUEST_V1, CHECK_BANK_REQUEST_V2],
)
async def test_limits_errors(
        taxi_bank_transfers,
        bank_core_statement_mock,
        pgsql,
        amount,
        error,
        request_str,
):
    if amount > 1100:
        bank_core_statement_mock.set_balance(100000)
    if amount > 1400:
        bank_core_statement_mock.set_transaction_limit(100000)
    transfer_id = db_helpers.insert_transfer(pgsql)
    params = {
        'transfer_id': transfer_id,
        'bank_id': common.TINKOFF,
        'money': {'amount': str(amount), 'currency': 'RUB'},
    }
    response = await taxi_bank_transfers.post(
        request_str,
        headers=common.build_headers(
            idempotency_token=common.DEFAULT_IDEMPOTENCY_TOKEN,
        ),
        json=params,
    )
    assert response.status_code == 200
    if error:
        if request_str == CHECK_BANK_REQUEST_V1:
            assert response.json()['error'] == error
        else:
            assert response.json()['bank_check_result']['error'] == error


@pytest.mark.parametrize(
    'amount, balance, transaction_limit',
    [
        #  balance = transaction_limit < amount < month_limit
        (2000, 1000, 1000),
        #  balance < transaction_limit < month_limit < amount
        (100000, 2000, 3000),
    ],
)
@pytest.mark.parametrize(
    'request_str', [CHECK_BANK_REQUEST_V1, CHECK_BANK_REQUEST_V2],
)
async def test_limits_errors_2(
        taxi_bank_transfers,
        bank_core_statement_mock,
        pgsql,
        amount,
        balance,
        transaction_limit,
        request_str,
):
    error = 'Нельзя переводить более {}\xa0\u20BD за одну операцию'.format(
        transaction_limit,
    )
    bank_core_statement_mock.set_balance(balance)
    bank_core_statement_mock.set_transaction_limit(transaction_limit)
    transfer_id = db_helpers.insert_transfer(pgsql)
    params = {
        'transfer_id': transfer_id,
        'bank_id': common.TINKOFF,
        'money': {'amount': str(amount), 'currency': 'RUB'},
    }
    response = await taxi_bank_transfers.post(
        request_str,
        headers=common.build_headers(
            idempotency_token=common.DEFAULT_IDEMPOTENCY_TOKEN,
        ),
        json=params,
    )
    assert response.status_code == 200

    if request_str == CHECK_BANK_REQUEST_V1:
        assert response.json()['error'] == error
    else:
        assert response.json()['bank_check_result']['error'] == error


@pytest.mark.parametrize(
    'amount, comment',
    [(None, None), ('123.45', None), ('123.45', 'Комментарий')],
)
@pytest.mark.parametrize(
    'request_str', [CHECK_BANK_REQUEST_V1, CHECK_BANK_REQUEST_V2],
)
@pytest.mark.parametrize('transfer_type', ['C2C', 'ME2ME'])
@pytest.mark.experiments3(
    filename='bank_transfer_inner_transfers_feature_experiments.json',
)
async def test_ok_to_yandex(
        taxi_bank_transfers,
        pgsql,
        amount,
        comment,
        request_str,
        transfer_type,
):
    transfer_id = db_helpers.insert_transfer(
        pgsql,
        amount=amount,
        comment=comment,
        receiver_bank_id=common.YANDEX_BANK,
        transfer_type=transfer_type,
    )
    params = {'transfer_id': transfer_id, 'bank_id': common.YANDEX_BANK}
    if amount:
        params['money'] = {'amount': '123.45', 'currency': 'RUB'}
    if comment:
        params['comment'] = comment
    headers = common.build_headers(
        idempotency_token=common.DEFAULT_IDEMPOTENCY_TOKEN,
    )
    response = await taxi_bank_transfers.post(
        request_str, headers=headers, json=params,
    )
    assert response.status_code == 200
    bank_check_response = {
        'receiver_name': common.SHORT_RECEIVER_NAME_1,
        'status': 'FOUND',
    }
    assert (
        response.json()
        == {'status': 'SUCCESS', 'bank_check_result': bank_check_response}
        if request_str == CHECK_BANK_REQUEST_V2
        else bank_check_response
    )

    transfer = db_helpers.select_transfer(pgsql, transfer_id)
    assert transfer.receiver_bank_id == common.YANDEX_BANK
    assert transfer.receiver_name == common.RECEIVER_NAME_1
    assert transfer.amount == amount
    assert transfer.comment == comment
    assert transfer.request_id is None


async def test_check_bank_pending_v2(
        taxi_bank_transfers, bank_core_faster_payments_mock, pgsql,
):
    bank_core_faster_payments_mock.set_bank_check_status('PENDING')

    transfer_id = db_helpers.insert_transfer(pgsql)
    params = build_params(transfer_id=transfer_id)
    response = await taxi_bank_transfers.post(
        CHECK_BANK_REQUEST_V2,
        headers=common.build_headers(
            idempotency_token=common.DEFAULT_IDEMPOTENCY_TOKEN,
        ),
        json=params,
    )
    assert response.status_code == 200
    assert response.json() == {'status': 'PENDING'}


@pytest.mark.parametrize(
    'request_str', [CHECK_BANK_REQUEST_V1, CHECK_BANK_REQUEST_V2],
)
@pytest.mark.experiments3(
    filename='bank_transfer_inner_transfers_feature_experiments.json',
)
async def test_to_yandex_not_inner_transfers(
        taxi_bank_transfers, pgsql, request_str,
):
    transfer_id = db_helpers.insert_transfer(
        pgsql, receiver_bank_id=common.YANDEX_BANK,
    )
    params = {'transfer_id': transfer_id, 'bank_id': common.YANDEX_BANK}
    headers = common.build_headers(
        idempotency_token=common.DEFAULT_IDEMPOTENCY_TOKEN,
        session_uuid=common.TEST_NOT_COMMON_SESSION_UUID,
    )
    response = await taxi_bank_transfers.post(
        request_str, headers=headers, json=params,
    )
    assert response.status_code == 200
    bank_check_response = {
        'error': 'Не пользуется этим банком',
        'status': 'NOT_FOUND',
    }
    assert (
        response.json()
        == {'status': 'SUCCESS', 'bank_check_result': bank_check_response}
        if request_str == CHECK_BANK_REQUEST_V2
        else bank_check_response
    )


@pytest.mark.parametrize(
    'request_str', [CHECK_BANK_REQUEST_V1, CHECK_BANK_REQUEST_V2],
)
async def test_security(taxi_bank_transfers, pgsql, request_str):
    transfer_id = db_helpers.insert_transfer(
        pgsql,
        receiver_phone=common.RECEIVER_PHONE_1,
        buid=common.TEST_BANK_UID,
    )
    params = {'transfer_id': transfer_id, 'bank_id': common.TINKOFF}
    # different buids in transfer and request
    response = await taxi_bank_transfers.post(
        request_str,
        headers=common.build_headers(
            buid=str(uuid.uuid4()),
            idempotency_token=common.DEFAULT_IDEMPOTENCY_TOKEN,
        ),
        json=params,
    )
    assert response.status_code == 404


@pytest.mark.parametrize(
    'request_str', [CHECK_BANK_REQUEST_V1, CHECK_BANK_REQUEST_V2],
)
@pytest.mark.experiments3(
    filename='bank_transfer_inner_transfers_feature_experiments.json',
)
async def test_second_check(taxi_bank_transfers, pgsql, request_str):
    transfer_id = db_helpers.insert_transfer(
        pgsql,
        amount='100',
        receiver_bank_id=common.TINKOFF,
        request_id=common.CHECK_REQUEST_ID,
    )
    # previous check has another bank_id!
    params = {
        'transfer_id': transfer_id,
        'bank_id': common.YANDEX_BANK,
        'money': {'amount': '100', 'currency': 'RUB'},
    }

    headers = common.build_headers(
        idempotency_token=common.DEFAULT_IDEMPOTENCY_TOKEN,
    )
    response = await taxi_bank_transfers.post(
        request_str, headers=headers, json=params,
    )
    assert response.status_code == 200
    bank_check_response = {
        'receiver_name': common.SHORT_RECEIVER_NAME_1,
        'status': 'FOUND',
    }
    assert (
        response.json()
        == {'status': 'SUCCESS', 'bank_check_result': bank_check_response}
        if request_str == CHECK_BANK_REQUEST_V2
        else bank_check_response
    )

    transfer = db_helpers.select_transfer(pgsql, transfer_id)
    assert transfer.receiver_bank_id == common.YANDEX_BANK
    assert transfer.receiver_name == common.RECEIVER_NAME_1
    assert transfer.amount == '100'
    assert transfer.request_id is None


@pytest.mark.parametrize('status_code', [400, 404, 500])
async def test_random_error_in_check_request(
        taxi_bank_transfers,
        pgsql,
        bank_core_faster_payments_mock,
        status_code,
):
    transfer_id = db_helpers.insert_transfer(pgsql)
    bank_core_faster_payments_mock.set_http_status_code(status_code)
    bank_core_faster_payments_mock.set_error_code('random_code')
    response = await taxi_bank_transfers.post(
        CHECK_BANK_REQUEST_V2,
        headers=common.build_headers(
            idempotency_token=common.DEFAULT_IDEMPOTENCY_TOKEN,
        ),
        json=build_params(transfer_id=transfer_id),
    )
    assert response.status_code == 500


@pytest.mark.parametrize(
    'error_code, error_message',
    [
        ('FCB-1037', 'Переводы СБП временно недоступны'),
        (
            'FCB-1038',
            'Перевод по выбранным реквизитам недоступен, уточните реквизиты у получателя',
        ),
        ('FCB-1039', 'Что-то пошло не так, попробуйте позже'),
        ('FCB-1040', 'Что-то пошло не так, попробуйте позже'),
    ],
)
async def test_fcb_error_in_check_request(
        taxi_bank_transfers,
        pgsql,
        bank_core_faster_payments_mock,
        error_code,
        error_message,
):
    transfer_id = db_helpers.insert_transfer(pgsql)
    bank_core_faster_payments_mock.set_http_status_code(400)
    bank_core_faster_payments_mock.set_error_code(error_code)
    response = await taxi_bank_transfers.post(
        CHECK_BANK_REQUEST_V2,
        headers=common.build_headers(
            idempotency_token=common.DEFAULT_IDEMPOTENCY_TOKEN,
        ),
        json=build_params(transfer_id=transfer_id),
    )
    assert response.status_code == 200
    assert response.json()['status'] == 'FAIL'
    assert response.json()['error'] == error_message

    transfer = db_helpers.select_transfer(pgsql, transfer_id)
    # user can change bank so status is not failed
    assert transfer.status == 'CREATED'
