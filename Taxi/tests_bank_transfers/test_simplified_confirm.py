import pytest

from tests_bank_transfers import common
from tests_bank_transfers import db_helpers


@pytest.mark.experiments3(filename='bank_transfer_feature_experiments.json')
@pytest.mark.experiments3(
    filename='bank_transfer_me2me_feature_experiments.json',
)
async def test_simplified_confirm_ok(
        taxi_bank_transfers, pgsql, stq, bank_core_faster_payments_mock,
):
    amount = str(common.DEFAULT_OFFER_AMOUNT)
    currency = 'RUB'
    response = await taxi_bank_transfers.post(
        '/v1/transfers/v1/transfer/simplified_confirm',
        headers=common.build_headers(
            idempotency_token=common.DEFAULT_IDEMPOTENCY_TOKEN,
        ),
        json=common.build_simplified_confirm_params(
            amount=amount, currency=currency,
        ),
    )

    assert response.status_code == 200
    response_success_data = response.json()['success_data']
    transfer_id = response_success_data['transfer_id']
    transfer = db_helpers.select_transfer(pgsql, transfer_id)
    assert transfer.bank_uid == common.TEST_BANK_UID
    assert transfer.agreement_id == common.TEST_AGREEMENT_ID
    assert transfer.status == 'PROCESSING'
    assert transfer.amount == amount
    assert transfer.currency == currency
    assert not transfer.max_limit
    assert not transfer.comment
    assert transfer.transfer_type == 'ME2ME'
    transfer_history = db_helpers.select_transfer_history(pgsql, transfer_id)
    assert len(transfer_history) == 2
    assert transfer_history[0].transfer_type == 'ME2ME'

    assert stq.bank_transfers_statuses.times_called == 1
    next_stq_call = stq.bank_transfers_statuses.next_call()
    assert next_stq_call['queue'] == 'bank_transfers_statuses'
    assert next_stq_call['id'] == f'poll_{transfer_id}'
    assert next_stq_call['kwargs']['transfer_id'] == transfer_id
    assert (
        bank_core_faster_payments_mock.me2me_pull_perform_handler.times_called
        == 1
    )


@pytest.mark.experiments3(
    filename='bank_transfer_me2me_feature_experiments.json',
)
async def test_not_in_bank_transfer_feature_exp(taxi_bank_transfers):
    response = await taxi_bank_transfers.post(
        '/v1/transfers/v1/transfer/simplified_confirm',
        headers=common.build_headers(
            idempotency_token=common.DEFAULT_IDEMPOTENCY_TOKEN,
        ),
        json=common.build_simplified_confirm_params(),
    )
    assert response.status_code == 404


@pytest.mark.experiments3(filename='bank_transfer_feature_experiments.json')
async def test_not_in_bank_transfer_me2me_feature_exp(taxi_bank_transfers):
    response = await taxi_bank_transfers.post(
        '/v1/transfers/v1/transfer/simplified_confirm',
        headers=common.build_headers(
            idempotency_token=common.DEFAULT_IDEMPOTENCY_TOKEN,
        ),
        json=common.build_simplified_confirm_params(),
    )
    assert response.status_code == 404


@pytest.mark.experiments3(filename='bank_transfer_feature_experiments.json')
@pytest.mark.experiments3(
    filename='bank_transfer_me2me_feature_experiments.json',
)
async def test_simplified_confirm_anonymous(
        taxi_bank_transfers, bank_core_client_mock,
):
    bank_core_client_mock.set_auth_level('ANONYMOUS')
    response = await taxi_bank_transfers.post(
        '/v1/transfers/v1/transfer/simplified_confirm',
        headers=common.build_headers(
            idempotency_token=common.DEFAULT_IDEMPOTENCY_TOKEN,
        ),
        json=common.build_simplified_confirm_params(),
    )
    assert response.status_code == 404


@pytest.mark.experiments3(filename='bank_transfer_feature_experiments.json')
@pytest.mark.experiments3(
    filename='bank_transfer_me2me_feature_experiments.json',
)
async def test_bad_core_client_response(
        taxi_bank_transfers, bank_core_client_mock,
):
    bank_core_client_mock.set_http_status_code(500)
    response = await taxi_bank_transfers.post(
        '/v1/transfers/v1/transfer/simplified_confirm',
        headers=common.build_headers(
            idempotency_token=common.DEFAULT_IDEMPOTENCY_TOKEN,
        ),
        json=common.build_simplified_confirm_params(),
    )
    assert response.status_code == 500


@pytest.mark.experiments3(filename='bank_transfer_feature_experiments.json')
@pytest.mark.experiments3(
    filename='bank_transfer_me2me_feature_experiments.json',
)
async def test_core_faster_payments_409(
        taxi_bank_transfers, bank_core_faster_payments_mock,
):
    bank_core_faster_payments_mock.set_http_status_code(409)
    response = await taxi_bank_transfers.post(
        '/v1/transfers/v1/transfer/simplified_confirm',
        headers=common.build_headers(
            idempotency_token=common.DEFAULT_IDEMPOTENCY_TOKEN,
        ),
        json=common.build_simplified_confirm_params(),
    )
    assert response.status_code == 409


@pytest.mark.experiments3(filename='bank_transfer_feature_experiments.json')
@pytest.mark.experiments3(
    filename='bank_transfer_me2me_feature_experiments.json',
)
async def test_insert_by_idempotency_token(
        taxi_bank_transfers, pgsql, testpoint,
):
    @testpoint('transfer_insert_data_race')
    async def _transfer_insert_data_race(data):
        pass

    @testpoint('select_after_insert_error')
    async def _select_after_insert_error(data):
        pass

    response = await taxi_bank_transfers.post(
        '/v1/transfers/v1/transfer/simplified_confirm',
        headers=common.build_headers(
            idempotency_token=common.DEFAULT_IDEMPOTENCY_TOKEN,
        ),
        json=common.build_simplified_confirm_params(),
    )
    assert response.status_code == 200
    assert _transfer_insert_data_race.times_called == 1
    assert _select_after_insert_error.times_called == 0


@pytest.mark.experiments3(filename='bank_transfer_feature_experiments.json')
@pytest.mark.experiments3(
    filename='bank_transfer_me2me_feature_experiments.json',
)
async def test_select_by_idempotency_token(
        taxi_bank_transfers, pgsql, testpoint,
):
    transfer_id = ''

    @testpoint('transfer_insert_data_race')
    async def _transfer_insert_data_race(data):
        nonlocal transfer_id
        transfer_id = db_helpers.insert_transfer(
            pgsql,
            transfer_type='ME2ME',
            idempotency_token=common.DEFAULT_IDEMPOTENCY_TOKEN,
            amount=str(common.DEFAULT_OFFER_AMOUNT),
        )

    @testpoint('select_after_insert_error')
    async def _select_after_insert_error(data):
        assert data == transfer_id

    response = await taxi_bank_transfers.post(
        '/v1/transfers/v1/transfer/simplified_confirm',
        headers=common.build_headers(
            idempotency_token=common.DEFAULT_IDEMPOTENCY_TOKEN,
        ),
        json=common.build_simplified_confirm_params(),
    )
    assert response.status_code == 200
    assert _transfer_insert_data_race.times_called == 1
    assert _select_after_insert_error.times_called == 1
