import pytest

from tests_bank_transfers import common
from tests_bank_transfers import db_helpers

CHECK_BANK_REQUEST_V1 = '/v1/transfers/v1/faster/check_user_bank'
CHECK_BANK_REQUEST_V2 = '/v1/transfers/v2/faster/check_user_bank'

CONFIRM_V1 = '/v1/transfers/v1/transfer/confirm'
CONFIRM_V2 = '/v1/transfers/v2/transfer/confirm'


@pytest.mark.experiments3(
    filename='bank_transfer_me2me_feature_experiments.json',
)
@pytest.mark.parametrize('confirm_version', [CONFIRM_V1, CONFIRM_V2])
@pytest.mark.parametrize(
    'check_user_bank_version', [CHECK_BANK_REQUEST_V1, CHECK_BANK_REQUEST_V2],
)
@pytest.mark.experiments3(filename='bank_transfer_feature_experiments.json')
async def test_me2me_flow_happy_path(
        taxi_bank_transfers,
        pgsql,
        stq,
        bank_core_faster_payments_mock,
        confirm_version,
        check_user_bank_version,
):
    # me2me handlers flow :
    # 1. /v1/transfers/v1/phone/get_transfer_info
    # 2. /v1/transfers/v1/faster/get_all_banks
    # 3. /v1/transfers/v{1|2}/faster/check_user_bank
    # 4. /v1/transfers/v{1|2}/transfer/confirm

    # 1. /v1/transfers/v1/phone/get_transfer_info
    response = await taxi_bank_transfers.post(
        '/v1/transfers/v1/phone/get_transfer_info',
        headers=common.build_headers(),
        json={
            'agreement_id': common.TEST_AGREEMENT_ID,
            'transfer_type': 'ME2ME',
        },
    )

    assert response.status_code == 200
    test_max_limit = str(min(common.AGREEMENT_BALANCE, *common.DEBIT_LIMITS))
    assert response.json()['max_limit']['money']['amount'] == test_max_limit
    transfer_id = response.json()['transfer_id']
    transfer = db_helpers.select_transfer(pgsql, transfer_id)
    assert transfer.bank_uid == common.TEST_BANK_UID
    assert transfer.agreement_id == common.TEST_AGREEMENT_ID
    assert transfer.status == 'CREATED'
    assert transfer.max_limit == test_max_limit
    assert transfer.transfer_type == 'ME2ME'
    transfer_history = db_helpers.select_transfer_history(pgsql, transfer_id)
    assert len(transfer_history) == 1
    assert transfer_history[0].transfer_type == 'ME2ME'

    # 2. /v1/transfers/v1/faster/get_all_banks
    response = await taxi_bank_transfers.post(
        '/v1/transfers/v1/faster/get_all_banks',
        headers=common.build_headers(),
        json={'transfer_id': transfer_id},
    )
    assert response.status_code == 200
    assert response.json() == {'banks': common.BANKS_WITH_M2M}

    # 3. /v1/transfers/v{1|2}/faster/check_user_bank
    amount = '123.45'
    currency = 'RUB'
    comment = 'very cool comment'
    params = {
        'transfer_id': transfer_id,
        'bank_id': common.TINKOFF,
        'money': {'amount': amount, 'currency': currency},
        'comment': comment,
    }
    headers = common.build_headers(
        idempotency_token=common.DEFAULT_IDEMPOTENCY_TOKEN,
    )
    response = await taxi_bank_transfers.post(
        check_user_bank_version, headers=headers, json=params,
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
        if check_user_bank_version == CHECK_BANK_REQUEST_V2
        else bank_check_response
    )

    transfer = db_helpers.select_transfer(pgsql, transfer_id)
    assert transfer.receiver_bank_id == common.TINKOFF
    assert transfer.receiver_name == common.RECEIVER_NAME_1
    assert transfer.amount == amount
    assert transfer.comment == comment
    assert transfer.request_id == common.CHECK_REQUEST_ID
    assert transfer.receiver_phone == common.RECEIVER_PHONE_1

    # 4. /v1/transfers/v{1|2}/transfer/confirm
    new_comment = 'new very cool comment'
    response = await taxi_bank_transfers.post(
        confirm_version,
        headers=common.build_headers(),
        json={
            'transfer_id': transfer_id,
            'money': {'amount': amount, 'currency': currency},
            'comment': new_comment,
        },
    )
    assert response.status_code == 200
    transfer = db_helpers.select_transfer(pgsql, transfer_id)
    assert transfer.status == 'PROCESSING'
    assert transfer.comment == new_comment
    assert stq.bank_transfers_statuses.times_called == 1
    next_stq_call = stq.bank_transfers_statuses.next_call()
    assert next_stq_call['queue'] == 'bank_transfers_statuses'
    assert next_stq_call['id'] == f'poll_{transfer_id}'
    assert next_stq_call['kwargs']['transfer_id'] == transfer_id
    assert (
        bank_core_faster_payments_mock.me2me_pull_perform_handler.times_called
        == 1
    )
    # assert transfer.request_id == request_id
