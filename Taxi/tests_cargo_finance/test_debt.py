import pytest


MOCK_NOW = '2021-10-06T00:00:00+00:00'
REQUEST = {
    'revision': 0,
    'is_service_complete': False,
    'client': {
        'agent': {
            'sum': '300',
            'currency': 'RUB',
            'payment_methods': {
                'card': {
                    'cardstorage_id': 'card-xf8ffb28eab1eb323fb4c25d2',
                    'owner_yandex_uid': '123',
                },
            },
            'context': {
                'billing_product': {
                    'id': '100500_80781421_ride',
                    'name': 'ride',
                },
                'customer_ip': 'some_ip',
                'corp_client_id': '35bf617cf19348e9a4f4a7064774fb8e',
                'invoice_due': '2021-07-01T10:50:00+00:00',
                'taxi_order_id': 'taxi_order_id',
                'taxi_alias_id': 'taxi_alias_id',
                'park_clid': 'park_clid',
                'park_dbid': 'park_dbid',
                'contractor_profile_id': 'contractor_profile_id',
                'taxi_order_due': '2021-07-01T10:45:00+00:00',
                'tariff_class': 'express',
                'nearest_zone': 'moscow',
                'city': 'Москва',
                'taxi_order_source': 'yandex',
                'fiscal_receipt_info': {
                    'vat': 'nds_none',
                    'title': 'Услуги курьерской доставки',
                    'personal_tin_id': 'e7fc0c1b184a4a6bb56f8e0b3c344e8c',
                },
            },
        },
    },
    'taxi': {'taxi_order_id': 'test_order_id'},
}
UPSERT_URI = (
    '/internal/cargo-finance/pay/order/transactions/debt?'
    'flow=claims&entity_id=test_id'
)


@pytest.mark.now(MOCK_NOW)
async def test_debt_time_update(
        taxi_cargo_finance,
        load_json,
        mock_debt_collector_by_id_ctx,
        mock_debt_collector_by_id,
        mock_debt_collector_update_ctx,
        mock_debt_collector_update,
        mocked_time,
):
    mock_debt_collector_by_id_ctx.response = load_json(
        'debt_collector_by_id.json',
    )
    await taxi_cargo_finance.post(UPSERT_URI, json=REQUEST)
    request_old = mock_debt_collector_update.next_call()['request']
    await taxi_cargo_finance.post(UPSERT_URI, json=REQUEST)
    request_new = mock_debt_collector_update.next_call()['request']
    assert (
        request_old.headers['X-Idempotency-Token']
        == request_new.headers['X-Idempotency-Token']
    )
    mocked_time.sleep(1)
    await taxi_cargo_finance.post(UPSERT_URI, json=REQUEST)
    request_new = mock_debt_collector_update.next_call()['request']
    assert (
        request_old.headers['X-Idempotency-Token']
        != request_new.headers['X-Idempotency-Token']
    )


@pytest.mark.now(MOCK_NOW)
async def test_debt_upsert_update(
        taxi_cargo_finance,
        load_json,
        mock_transactions_ng_retrieve_ctx,
        mock_transactions_ng_retrieve,
        mock_debt_collector_by_id_ctx,
        mock_debt_collector_by_id,
        mock_debt_collector_update_ctx,
        mock_debt_collector_update,
):
    mock_transactions_ng_retrieve_ctx.response = load_json(
        'transactions_retrieve_response.json',
    )
    mock_debt_collector_by_id_ctx.response = load_json(
        'debt_collector_by_id.json',
    )
    response = await taxi_cargo_finance.post(UPSERT_URI, json=REQUEST)
    assert response.status == 200
    request = mock_transactions_ng_retrieve.next_call()['request'].json
    assert request['id'] == 'claims/agent/test_id'
    assert request['id_namespace'] == 'delivery'
    request = mock_debt_collector_by_id.next_call()['request'].json
    assert request == {'ids': ['claims/agent/test_id'], 'service': 'cargo'}
    request = mock_debt_collector_update.next_call()['request']
    assert request.json == load_json('expected_debt_update_request.json')
    assert response.json() == {
        'client': {'agent': {'is_finished': False, 'paid_sum': '0'}},
    }


@pytest.mark.now(MOCK_NOW)
async def test_debt_upsert_create(
        taxi_cargo_finance,
        load_json,
        mock_transactions_ng_retrieve_ctx,
        mock_transactions_ng_retrieve,
        mock_debt_collector_by_id_ctx,
        mock_debt_collector_by_id,
        mock_debt_collector_create_ctx,
        mock_debt_collector_create,
):
    mock_transactions_ng_retrieve_ctx.response = load_json(
        'transactions_retrieve_response.json',
    )
    mock_debt_collector_by_id_ctx.response = {'debts': []}
    response = await taxi_cargo_finance.post(UPSERT_URI, json=REQUEST)
    assert response.status == 200
    request = mock_transactions_ng_retrieve.next_call()['request'].json
    assert request['id'] == 'claims/agent/test_id'
    assert request['id_namespace'] == 'delivery'
    request = mock_debt_collector_by_id.next_call()['request'].json
    assert request == {'ids': ['claims/agent/test_id'], 'service': 'cargo'}
    request = mock_debt_collector_create.next_call()['request']
    assert request.headers['X-Idempotency-Token'] == 'create/0'
    assert request.json == load_json('expected_debt_create_request.json')


async def test_debt_retrieve(
        taxi_cargo_finance,
        mock_debt_collector_list_ctx,
        mock_debt_collector_list,
        load_json,
):
    mock_debt_collector_list_ctx.response = load_json(
        'debt_collector_by_id.json',
    )
    response = await taxi_cargo_finance.post(
        '/internal/cargo-finance/v1/debt/retrieve',
        json={
            'debtors': [
                {
                    'id': '35bf617cf19348e9a4f4a7064774fb8e',
                    'kind': 'corp_client_id',
                },
            ],
        },
    )
    assert response.status == 200
    assert response.json() == {
        'debts': [
            {
                'id': 'claims/agent/test_id',
                'currency': 'RUB',
                'debtor_id': (
                    'cargo/corp_client_id/35bf617cf19348e9a4f4a7064774fb8e'
                ),
                'sum_to_pay': '100',
            },
        ],
    }
    assert mock_debt_collector_list.next_call()['request'].json['limit'] == 20


@pytest.mark.now(MOCK_NOW)
async def test_debt_update_409(
        taxi_cargo_finance,
        load_json,
        mock_transactions_ng_retrieve_ctx,
        mock_transactions_ng_retrieve,
        mock_debt_collector_by_id_ctx,
        mock_debt_collector_by_id,
        mockserver,
):
    mock_transactions_ng_retrieve_ctx.response = load_json(
        'transactions_retrieve_response.json',
    )
    mock_debt_collector_by_id_ctx.response = load_json(
        'debt_collector_by_id.json',
    )

    @mockserver.json_handler('/debt-collector/v1/debt/update')
    def _handler(request):
        return mockserver.make_response(
            status=409, json={'code': 'code', 'message': 'message'},
        )

    response = await taxi_cargo_finance.post(UPSERT_URI, json=REQUEST)
    assert response.status == 200
