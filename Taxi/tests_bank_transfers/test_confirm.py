import uuid

import pytest

from tests_bank_transfers import common
from tests_bank_transfers import db_helpers

CONFIRM_V1 = '/v1/transfers/v1/transfer/confirm'
CONFIRM_V2 = '/v1/transfers/v2/transfer/confirm'


def build_params(
        transfer_id='e493fa8c-a742-4bfb-96e7-27126d0a9a15',
        amount=str(common.DEFAULT_OFFER_AMOUNT),
        transfer_type='C2C',
        currency='RUB',
        offer_id='6282d918-f31e-424d-be10-aca0cae92117',
        comment=None,
):
    if transfer_type == 'ME2ME':
        offer_id = None

    params = {
        'transfer_id': transfer_id,
        'money': {'amount': amount, 'currency': currency},
        'offer_id': offer_id,
    }
    if comment is not None:
        params['comment'] = comment
    return params


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
@pytest.mark.experiments3(filename='bank_transfer_feature_experiments.json')
@pytest.mark.parametrize('request_string', [CONFIRM_V1, CONFIRM_V2])
async def test_not_authorized(taxi_bank_transfers, headers, request_string):
    response = await taxi_bank_transfers.post(
        request_string, headers=headers, json=build_params(),
    )
    assert response.status_code == 401


@pytest.mark.experiments3(filename='bank_transfer_feature_experiments.json')
@pytest.mark.parametrize('request_string', [CONFIRM_V1, CONFIRM_V2])
async def test_wrong_transfer_id_format(taxi_bank_transfers, request_string):
    response = await taxi_bank_transfers.post(
        request_string,
        headers=common.build_headers(verification_token=common.GOOD_TOKEN),
        json=build_params(transfer_id='e493fa8c'),
    )
    assert response.status_code == 400


@pytest.mark.experiments3(filename='bank_transfer_feature_experiments.json')
@pytest.mark.config(BANK_AUTHORIZATION_JWT_PUBLIC_KEYS=common.JWT_PUBLIC_KEYS)
@pytest.mark.parametrize('request_string', [CONFIRM_V1, CONFIRM_V2])
async def test_transfer_not_found(taxi_bank_transfers, request_string):
    response = await taxi_bank_transfers.post(
        request_string,
        headers=common.build_headers(verification_token=common.GOOD_TOKEN),
        json=build_params(),
    )
    assert response.status_code == 404


@pytest.mark.experiments3(filename='bank_transfer_feature_experiments.json')
@pytest.mark.parametrize('transfer_type', ['C2C', 'ME2ME'])
@pytest.mark.config(BANK_AUTHORIZATION_JWT_PUBLIC_KEYS=common.JWT_PUBLIC_KEYS)
@pytest.mark.parametrize('request_string', [CONFIRM_V1, CONFIRM_V2])
async def test_buid_not_found(
        taxi_bank_transfers, pgsql, request_string, transfer_type,
):
    transfer_id = db_helpers.insert_transfer(
        pgsql, amount=common.DEFAULT_OFFER_AMOUNT, transfer_type=transfer_type,
    )
    if transfer_type == 'C2C':
        db_helpers.create_offer(pgsql, transfer_id)
    db_helpers.insert_2fa(pgsql, transfer_id)
    response = await taxi_bank_transfers.post(
        request_string,
        headers=common.build_headers(
            buid='e493fa8c-a742-4bfb-96e7-27126d0a9a15',
            verification_token=common.GOOD_TOKEN,
        ),
        json=build_params(transfer_id, transfer_type=transfer_type),
    )
    assert response.status_code == 404


@pytest.mark.experiments3(filename='bank_transfer_feature_experiments.json')
@pytest.mark.config(BANK_AUTHORIZATION_JWT_PUBLIC_KEYS=common.JWT_PUBLIC_KEYS)
@pytest.mark.parametrize('request_string', [CONFIRM_V1, CONFIRM_V2])
async def test_wrong_currency(taxi_bank_transfers, pgsql, request_string):
    transfer_id = db_helpers.insert_transfer(
        pgsql, amount=common.DEFAULT_OFFER_AMOUNT, currency='USD',
    )
    db_helpers.create_offer(pgsql, transfer_id)
    db_helpers.insert_2fa(pgsql, transfer_id)
    params = build_params(transfer_id, currency='USD')
    response = await taxi_bank_transfers.post(
        request_string,
        headers=common.build_headers(verification_token=common.GOOD_TOKEN),
        json=params,
    )
    assert response.status_code == 404


@pytest.mark.experiments3(filename='bank_transfer_feature_experiments.json')
@pytest.mark.config(BANK_AUTHORIZATION_JWT_PUBLIC_KEYS=common.JWT_PUBLIC_KEYS)
@pytest.mark.parametrize('request_string', [CONFIRM_V1, CONFIRM_V2])
async def test_me2me_use_params_from_request(
        taxi_bank_transfers, pgsql, request_string,
):
    transfer_id = db_helpers.insert_transfer(
        pgsql, amount=common.DEFAULT_OFFER_AMOUNT, transfer_type='ME2ME',
    )
    new_amount = '99'
    db_helpers.insert_2fa(pgsql, transfer_id, amount=new_amount)
    params = build_params(transfer_id, amount=new_amount, offer_id=None)
    response = await taxi_bank_transfers.post(
        request_string,
        headers=common.build_headers(verification_token=common.GOOD_TOKEN),
        json=params,
    )
    assert response.status_code == 200
    transfer = db_helpers.select_transfer(pgsql, transfer_id)
    assert transfer.currency == common.DEFAULT_CURRENCY
    assert transfer.amount == new_amount


@pytest.mark.experiments3(filename='bank_transfer_feature_experiments.json')
async def test_offer_not_found_for_c2c(taxi_bank_transfers, pgsql):
    transfer_id = db_helpers.insert_transfer(pgsql, transfer_type='C2C')
    response = await taxi_bank_transfers.post(
        '/v1/transfers/v1/transfer/confirm',
        headers=common.build_headers(),
        json=build_params(transfer_id),
    )
    assert response.status_code == 404


@pytest.mark.experiments3(filename='bank_transfer_feature_experiments.json')
async def test_wrong_offer_amount(taxi_bank_transfers, pgsql):
    transfer_id = db_helpers.insert_transfer(pgsql, transfer_type='C2C')
    offer_id = db_helpers.create_offer(pgsql, transfer_id, amount=150)
    response = await taxi_bank_transfers.post(
        '/v1/transfers/v1/transfer/confirm',
        headers=common.build_headers(),
        json=build_params(transfer_id, offer_id=offer_id),
    )
    assert response.status_code == 404


@pytest.mark.experiments3(filename='bank_transfer_feature_experiments.json')
@pytest.mark.config(BANK_AUTHORIZATION_JWT_PUBLIC_KEYS=common.JWT_PUBLIC_KEYS)
@pytest.mark.parametrize('request_string', [CONFIRM_V1, CONFIRM_V2])
@pytest.mark.parametrize(
    'receiver_phone, status, request_id, comment',
    [
        (common.RECEIVER_PHONE_1, 'PROCESSING', 'aa1235', None),
        (common.RECEIVER_PHONE_1, 'PROCESSING', 'aa1235', 'комментарий'),
        (common.RECEIVER_PHONE_2, 'FAILED', 'aa1234', None),
    ],
)
@pytest.mark.parametrize('transfer_type', ['C2C', 'ME2ME'])
async def test_ok(
        taxi_bank_transfers,
        bank_core_faster_payments_mock,
        pgsql,
        stq,
        receiver_phone,
        status,
        request_id,
        comment,
        transfer_type,
        request_string,
):
    transfer_id = db_helpers.insert_transfer(
        pgsql,
        receiver_phone=receiver_phone,
        amount=common.DEFAULT_OFFER_AMOUNT,
        transfer_type=transfer_type,
        comment=comment,
    )
    offer_id = (
        db_helpers.create_offer(pgsql, transfer_id)
        if transfer_type == 'C2C'
        else None
    )
    if transfer_type == 'ME2ME':
        bank_core_faster_payments_mock.set_me2me_pull_response_status(status)
    db_helpers.insert_2fa(pgsql, transfer_id)

    response = await taxi_bank_transfers.post(
        request_string,
        headers=common.build_headers(verification_token=common.GOOD_TOKEN),
        json=build_params(
            transfer_id,
            transfer_type=transfer_type,
            offer_id=offer_id,
            comment=comment,
        ),
    )
    assert response.status_code == 200
    transfer = db_helpers.select_transfer(pgsql, transfer_id)
    assert transfer.status == status
    assert transfer.request_id == request_id
    if comment is not None:
        assert transfer.comment == comment
    if status == 'PROCESSING':
        assert stq.bank_transfers_statuses.times_called == 1
        next_stq_call = stq.bank_transfers_statuses.next_call()
        assert next_stq_call['queue'] == 'bank_transfers_statuses'
        assert next_stq_call['id'] == f'poll_{transfer_id}'
        assert next_stq_call['kwargs']['transfer_id'] == transfer_id
    else:
        assert stq.bank_transfers_statuses.times_called == 0

    if transfer_type == 'ME2ME':
        assert (
            bank_core_faster_payments_mock.me2me_pull_perform_handler.times_called
            == 1
        )
    else:
        assert bank_core_faster_payments_mock.perform_handler.times_called == 1


@pytest.mark.experiments3(filename='bank_transfer_feature_experiments.json')
@pytest.mark.config(BANK_AUTHORIZATION_JWT_PUBLIC_KEYS=common.JWT_PUBLIC_KEYS)
@pytest.mark.parametrize('request_string', [CONFIRM_V1, CONFIRM_V2])
@pytest.mark.parametrize(
    'amount, comment, offer_amount, confirm_comment, final_request_id',
    [
        ('123.45', 'Комментарий', '123.45', 'Комментарий', 'aa1236'),
        ('123.45', 'Комментарий', '123.45', 'Новый комментарий', 'aa1235'),
        ('123.45', 'Комментарий', '234.56', 'Комментарий', 'aa1235'),
        ('123.45', 'Комментарий', '234.56', 'Новый комментарий', 'aa1235'),
    ],
)
async def test_continue(
        taxi_bank_transfers,
        bank_core_faster_payments_mock,
        pgsql,
        stq,
        amount,
        comment,
        offer_amount,
        confirm_comment,
        final_request_id,
        request_string,
):
    transfer_id = db_helpers.insert_transfer(
        pgsql,
        amount=amount,
        request_id=common.CHECK_REQUEST_ID,
        comment=comment,
    )
    offer_id = db_helpers.create_offer(pgsql, transfer_id, amount=offer_amount)
    db_helpers.insert_2fa(
        pgsql, transfer_id, comment=confirm_comment, amount=offer_amount,
    )

    response = await taxi_bank_transfers.post(
        request_string,
        headers=common.build_headers(verification_token=common.GOOD_TOKEN),
        json=build_params(
            transfer_id=transfer_id,
            offer_id=offer_id,
            comment=confirm_comment,
            amount=offer_amount,
        ),
    )
    assert response.status_code == 200

    transfer = db_helpers.select_transfer(pgsql, transfer_id=transfer_id)
    assert transfer.amount == offer_amount
    assert transfer.status == 'PROCESSING'
    assert transfer.request_id == final_request_id
    assert transfer.comment == confirm_comment

    assert stq.bank_transfers_statuses.times_called == 1
    next_stq_call = stq.bank_transfers_statuses.next_call()
    assert next_stq_call['queue'] == 'bank_transfers_statuses'
    assert next_stq_call['id'] == f'poll_{transfer_id}'
    assert next_stq_call['kwargs']['transfer_id'] == transfer_id
    assert (
        bank_core_faster_payments_mock.me2me_pull_perform_handler.times_called
        == 0
    )
    if amount != offer_amount or comment != confirm_comment:
        assert (
            bank_core_faster_payments_mock.continue_handler.times_called == 0
        )
        assert bank_core_faster_payments_mock.perform_handler.times_called == 1
    else:
        assert (
            bank_core_faster_payments_mock.continue_handler.times_called == 1
        )
        assert bank_core_faster_payments_mock.perform_handler.times_called == 0


@pytest.mark.experiments3(filename='bank_transfer_feature_experiments.json')
@pytest.mark.parametrize('transfer_type', ['C2C', 'ME2ME'])
@pytest.mark.config(BANK_AUTHORIZATION_JWT_PUBLIC_KEYS=common.JWT_PUBLIC_KEYS)
@pytest.mark.parametrize('request_string', [CONFIRM_V1, CONFIRM_V2])
async def test_called_twice(
        taxi_bank_transfers,
        bank_core_faster_payments_mock,
        pgsql,
        stq,
        transfer_type,
        request_string,
):
    transfer_id = db_helpers.insert_transfer(
        pgsql, amount=common.DEFAULT_OFFER_AMOUNT, transfer_type=transfer_type,
    )
    offer_id = (
        db_helpers.create_offer(pgsql, transfer_id)
        if transfer_type == 'C2C'
        else None
    )
    db_helpers.insert_2fa(pgsql, transfer_id)

    for _ in range(2):
        response = await taxi_bank_transfers.post(
            request_string,
            headers=common.build_headers(verification_token=common.GOOD_TOKEN),
            json=build_params(transfer_id, offer_id=offer_id),
        )
        assert response.status_code == 200
        status = (
            response.json()['result']['status']
            if request_string == CONFIRM_V1
            else response.json()['success_data']['status']
        )
        assert status == 'PROCESSING'

    bank_core_faster_payments_mock.set_http_status_code(409)
    if transfer_type == 'ME2ME':
        assert (
            bank_core_faster_payments_mock.me2me_pull_perform_handler.times_called
            == 1
        )
    else:
        assert bank_core_faster_payments_mock.perform_handler.times_called == 1

    new_amount = '99'
    response = await taxi_bank_transfers.post(
        request_string,
        headers=common.build_headers(verification_token=common.GOOD_TOKEN),
        json=build_params(
            transfer_id, amount=new_amount, transfer_type=transfer_type,
        ),
    )
    if request_string == CONFIRM_V2:
        assert response.status_code == 409
    else:
        assert response.status_code == 404
        assert 'already confirmed with ' in response.json()['message']

    status = db_helpers.select_transfer_status(pgsql, transfer_id)
    assert status == 'PROCESSING'
    assert stq.bank_transfers_statuses.times_called == 1
    next_stq_call = stq.bank_transfers_statuses.next_call()
    assert next_stq_call['queue'] == 'bank_transfers_statuses'
    assert next_stq_call['id'] == f'poll_{transfer_id}'
    assert next_stq_call['kwargs']['transfer_id'] == transfer_id
    if transfer_type == 'ME2ME':
        assert (
            bank_core_faster_payments_mock.me2me_pull_perform_handler.times_called
            == 1
        )
    else:
        assert bank_core_faster_payments_mock.perform_handler.times_called == 1


@pytest.mark.experiments3(filename='bank_transfer_feature_experiments.json')
@pytest.mark.config(BANK_AUTHORIZATION_JWT_PUBLIC_KEYS=common.JWT_PUBLIC_KEYS)
@pytest.mark.parametrize('request_string', [CONFIRM_V1, CONFIRM_V2])
@pytest.mark.parametrize('status', ['PROCESSING', 'FAILED', 'SUCCESS'])
async def test_security(
        taxi_bank_transfers, pgsql, stq, status, request_string,
):
    transfer_id = db_helpers.insert_transfer(
        pgsql,
        receiver_phone=common.RECEIVER_PHONE_1,
        status=status,
        buid=common.TEST_BANK_UID,
        amount=common.DEFAULT_OFFER_AMOUNT,
    )
    offer_id = db_helpers.create_offer(pgsql, transfer_id)
    db_helpers.insert_2fa(pgsql, transfer_id)

    # different buids in transfer and request
    response = await taxi_bank_transfers.post(
        request_string,
        headers=common.build_headers(
            buid=str(uuid.uuid4()), verification_token=common.GOOD_TOKEN,
        ),
        json=build_params(transfer_id, offer_id=offer_id),
    )
    assert stq.bank_transfers_statuses.times_called == 0
    assert response.status_code == 404


async def test_confrim_v2_not_enable(taxi_bank_transfers):
    response = await taxi_bank_transfers.post(
        '/v1/transfers/v2/transfer/confirm',
        headers=common.build_headers(verification_token=common.GOOD_TOKEN),
        json=build_params(),
    )

    assert response.status_code == 404
    assert response.json() == {
        'code': 'NotFound',
        'message': 'Confirm_v2 is not enable for user',
    }


@pytest.mark.experiments3(filename='bank_transfer_feature_experiments.json')
@pytest.mark.config(BANK_AUTHORIZATION_JWT_PUBLIC_KEYS=common.JWT_PUBLIC_KEYS)
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
        ('another_code', 'Не получилось перевести деньги'),
    ],
)
@pytest.mark.parametrize('request_string', [CONFIRM_V1, CONFIRM_V2])
async def test_fcb_errors(
        taxi_bank_transfers,
        bank_core_faster_payments_mock,
        pgsql,
        error_code,
        error_message,
        request_string,
):
    bank_core_faster_payments_mock.set_error_code(error_code)
    # bad_receiver_phone
    transfer_id = db_helpers.insert_transfer(
        pgsql,
        receiver_phone=common.RECEIVER_PHONE_2,
        amount=common.DEFAULT_OFFER_AMOUNT,
        transfer_type='C2C',
    )
    offer_id = db_helpers.create_offer(pgsql, transfer_id)

    db_helpers.insert_2fa(pgsql, transfer_id)

    response = await taxi_bank_transfers.post(
        request_string,
        headers=common.build_headers(verification_token=common.GOOD_TOKEN),
        json=build_params(transfer_id, offer_id=offer_id),
    )
    assert response.status_code == 200
    message = (
        response.json()['result']['message']
        if request_string == CONFIRM_V1
        else response.json()['success_data']['message']
    )
    assert message == error_message

    transfer = db_helpers.select_transfer(pgsql, transfer_id)
    assert transfer.status == 'FAILED'
