import copy

import pytest


REQUEST = {
    'revision': 0,
    'is_service_complete': False,
    'client': {
        'agent': {
            'sum': '300',
            'currency': 'RUB',
            'payment_methods': {
                'card': {
                    'cardstorage_id': 'card-123456789',
                    'owner_yandex_uid': '123',
                },
            },
            'context': {
                'billing_product': {'id': 'park_clid_product', 'name': 'ride'},
                'customer_ip': 'some_ip',
                'corp_client_id': '0400ddf6026511e8653a6f0023263aca',
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
                    'personal_tin_id': '1514a5c7d59247afa82489b273e45303',
                    'title': 'Услуги курьерской доставки',
                    'vat': 'nds_none',
                },
            },
        },
    },
    'taxi': {'taxi_order_id': 'test_order_id'},
}
PERFORMER_CALLBACK = {
    'payload': {
        'alias_id': 'taxi_alias_id',
        'city': 'Москва',
        'driver': {
            'clid': 'park_clid',
            'driver_profile_id': 'contractor_profile_id',
            'park_id': 'park_dbid',
        },
        'due': '2021-07-01T10:45:00+00:00',
        'is_roaming_user': False,
        'nearest_zone': 'moscow',
        'order_id': 'taxi_order_id',
        'payment_type': 'card',
        'source': 'yandex',
        'tariff_class': 'express',
    },
    'queue': 'taxi_send_to_orders_callback',
}
UPSERT_URI = (
    '/internal/cargo-finance/pay/order/transactions/upsert?'
    'flow=claims&entity_id=claim_id'
)
RETRIEVE_URI = (
    '/internal/cargo-finance/pay/order/transactions/retrieve?'
    'flow=claims&entity_id=claim_id'
)


@pytest.fixture(name='transactions_ng_ctx')
def _transactions_ng_ctx(mockserver):
    class Ctx:
        def __init__(self):
            self.retrieve_response = (
                404,
                {'code': 'NOT_FOUND', 'message': 'Not found'},
            )
            self.additional_data = {}

    return Ctx()


@pytest.fixture(name='mock_transactions_ng')
def _mock_transactions_ng(mockserver, transactions_ng_ctx):
    @mockserver.json_handler('/transactions-ng/v2/invoice/retrieve')
    async def _invoice_retrieve(request):
        return mockserver.make_response(
            status=transactions_ng_ctx.retrieve_response[0],
            json=transactions_ng_ctx.retrieve_response[1],
        )

    @mockserver.json_handler('/transactions-ng/v2/invoice/create')
    async def _invoice_create(request):
        if transactions_ng_ctx.retrieve_response[0] == 200:
            return mockserver.make_response(
                status=409,
                json={'code': 'already_exists', 'message': 'already exists'},
            )
        transactions_ng_ctx.retrieve_response = (
            200,
            {
                **transactions_ng_ctx.retrieve_response[1],
                'cleared': [],
                'currency': request.json['currency'],
                'created': '2021-07-01T11:00:00+0000',
                'debt': [],
                'held': [],
                'id': request.json['id'],
                'invoice_due': request.json['invoice_due'],
                'operation_info': {'version': 1},
                'operations': [],
                'payment_types': [request.json['payments'][0]['type']],
                'status': 'init',
                'sum_to_pay': [],
                'transactions': [],
                'yandex_uid': request.json['yandex_uid'],
            },
        )
        return mockserver.make_response(status=200, json={})

    @mockserver.json_handler('/transactions-ng/v2/invoice/update')
    async def _invoice_update(request):
        assert (
            request.json['id']
            == transactions_ng_ctx.retrieve_response[1]['id']
        )
        item = request.json['items_by_payment_type'][0]['items'][0]
        assert item['fiscal_receipt_info'] == {
            'personal_tin_id': '1514a5c7d59247afa82489b273e45303',
            'title': 'Услуги курьерской доставки',
            'vat': 'nds_none',
        }
        payment_list = {
            'items': [{'amount': item['amount'], 'item_id': item['item_id']}],
            'payment_type': request.json['items_by_payment_type'][0][
                'payment_type'
            ],
        }
        new_state = {
            **transactions_ng_ctx.retrieve_response[1],
            'yandex_uid': request.json['yandex_uid'],
            'operation_info': {'version': 2},
            'status': 'holding',
            'sum_to_pay': [payment_list],
        }
        new_state['operations'].append(
            {
                'created': '2021-07-01T11:10:00+0000',
                'id': request.json['operation_id'],
                'status': 'processing',
                'sum_to_pay': [payment_list],
            },
        )
        # new_state['held'] = [copy.deepcopy(payment_list)]
        new_state['transactions'].append(
            {
                'created': '2021-07-01T11:11:00+0000',
                'external_payment_id': '0400ddf6026511e8653a6f0023263aca',
                'held': '2021-07-01T11:12:00+0000',
                'initial_sum': [
                    {'amount': item['amount'], 'item_id': item['item_id']},
                ],
                'operation_id': request.json['operation_id'],
                'payment_method_id': request.json['payments'][0]['method'],
                'payment_type': 'card',
                'refunds': [],
                'status': 'hold_pending',
                'sum': [
                    {'amount': item['amount'], 'item_id': item['item_id']},
                ],
                'technical_error': False,
                'updated': '2021-07-01T11:15:00+0000',
            },
        )
        transactions_ng_ctx.additional_data['callbacks'] = request.json[
            'callbacks'
        ]
        transactions_ng_ctx.additional_data['held'] = [
            copy.deepcopy(payment_list),
        ]

        transactions_ng_ctx.retrieve_response = (200, new_state)
        return mockserver.make_response(status=200, json={})

    @mockserver.json_handler('/transactions-ng/invoice/clear')
    async def _invoice_clear(request):
        assert (
            request.json['id']
            == transactions_ng_ctx.retrieve_response[1]['id']
        )
        new_state = transactions_ng_ctx.retrieve_response[1]
        new_state['cleared'] = new_state['sum_to_pay']
        new_state['held'] = []
        new_state['status'] = 'cleared'
        for operation in new_state['operations']:
            operation['status'] = 'done'
        transactions_ng_ctx.retrieve_response = (200, new_state)
        return {}


def _make_operations_done(transactions_ng_ctx):
    for operation in transactions_ng_ctx.retrieve_response[1]['operations']:
        operation['status'] = 'done'
    transactions_ng_ctx.retrieve_response[1][
        'held'
    ] = transactions_ng_ctx.additional_data['held']


def _assert_performer_callback(transactions_ng_ctx):
    assert (
        PERFORMER_CALLBACK in transactions_ng_ctx.additional_data['callbacks']
    )


async def test_pay_upsert_corpcard(
        taxi_cargo_finance, transactions_ng_ctx, mock_transactions_ng,
):
    request = copy.deepcopy(REQUEST)
    response = await taxi_cargo_finance.post(UPSERT_URI, json=request)
    assert response.status == 200
    assert response.json() == {
        'client': {'agent': {'is_finished': False, 'paid_sum': '0'}},
    }
    _assert_performer_callback(transactions_ng_ctx)
    request['client']['agent']['sum'] = '400'
    request['revision'] = 5
    _make_operations_done(transactions_ng_ctx)
    response = await taxi_cargo_finance.post(UPSERT_URI, json=request)
    assert response.json() == {
        'client': {'agent': {'is_finished': False, 'paid_sum': '300'}},
    }
    _assert_performer_callback(transactions_ng_ctx)
    request['client']['agent']['sum'] = '200'
    request['revision'] = 13
    request['is_service_complete'] = True
    _make_operations_done(transactions_ng_ctx)
    response = await taxi_cargo_finance.post(UPSERT_URI, json=request)
    assert response.json() == {
        'client': {'agent': {'is_finished': True, 'paid_sum': '200'}},
    }
    _assert_performer_callback(transactions_ng_ctx)


async def test_pay_retrieve_corpcard(
        taxi_cargo_finance, transactions_ng_ctx, mock_transactions_ng,
):
    request = copy.deepcopy(REQUEST)
    request['is_service_complete'] = True
    response = await taxi_cargo_finance.post(UPSERT_URI, json=request)
    assert response.status == 200
    assert response.json() == {
        'client': {'agent': {'is_finished': True, 'paid_sum': '300'}},
    }
    response = await taxi_cargo_finance.post(RETRIEVE_URI, json=request)
    assert response.status == 200
    assert response.json() == {
        'client': {'agent': {'is_finished': True, 'paid_sum': '300'}},
    }


async def test_pay_retrieve_corpcard_not_exist(
        taxi_cargo_finance, transactions_ng_ctx, mock_transactions_ng,
):
    response = await taxi_cargo_finance.post(RETRIEVE_URI, json=REQUEST)
    assert response.status == 200
    assert response.json() == {
        'client': {'agent': {'is_finished': True, 'paid_sum': '0'}},
    }


async def test_pay_upsert_no_update_needed(
        taxi_cargo_finance, transactions_ng_ctx, mock_transactions_ng,
):
    request = copy.deepcopy(REQUEST)
    response = await taxi_cargo_finance.post(UPSERT_URI, json=request)
    assert response.status == 200
    assert response.json() == {
        'client': {'agent': {'is_finished': False, 'paid_sum': '0'}},
    }
    assert len(transactions_ng_ctx.retrieve_response[1]['operations']) == 1
    assert (
        transactions_ng_ctx.retrieve_response[1]['operations'][-1]['id']
        == '0:0'
    )
    _make_operations_done(transactions_ng_ctx)
    # retry: same revision, same sum
    response = await taxi_cargo_finance.post(UPSERT_URI, json=request)
    assert response.status == 200
    assert response.json() == {
        'client': {'agent': {'is_finished': True, 'paid_sum': '300'}},
    }
    assert len(transactions_ng_ctx.retrieve_response[1]['operations']) == 1
    assert (
        transactions_ng_ctx.retrieve_response[1]['operations'][-1]['id']
        == '0:0'
    )
    # different sum, same revision,
    # like last operation failed with same revision
    request['client']['agent']['sum'] = '400'
    _make_operations_done(transactions_ng_ctx)
    response = await taxi_cargo_finance.post(UPSERT_URI, json=request)
    assert response.status == 200
    assert response.json() == {
        'client': {'agent': {'is_finished': False, 'paid_sum': '300'}},
    }
    assert len(transactions_ng_ctx.retrieve_response[1]['operations']) == 2
    assert (
        transactions_ng_ctx.retrieve_response[1]['operations'][-1]['id']
        == '0:1'
    )
    # same sum, same revision, last operation is not finished, like retry
    response = await taxi_cargo_finance.post(UPSERT_URI, json=request)
    assert response.status == 200
    assert response.json() == {
        'client': {'agent': {'is_finished': False, 'paid_sum': '300'}},
    }
    assert len(transactions_ng_ctx.retrieve_response[1]['operations']) == 2
    assert (
        transactions_ng_ctx.retrieve_response[1]['operations'][-1]['id']
        == '0:1'
    )
    # different sum, same revision, last operation is not finished
    request['client']['agent']['sum'] = '410'
    response = await taxi_cargo_finance.post(UPSERT_URI, json=request)
    assert response.status == 200
    assert response.json() == {
        'client': {'agent': {'is_finished': False, 'paid_sum': '300'}},
    }
    assert len(transactions_ng_ctx.retrieve_response[1]['operations']) == 2
    assert (
        transactions_ng_ctx.retrieve_response[1]['operations'][-1]['id']
        == '0:1'
    )
    # different sum, different revision
    request['revision'] = 1
    request['client']['agent']['sum'] = '405'
    _make_operations_done(transactions_ng_ctx)
    response = await taxi_cargo_finance.post(UPSERT_URI, json=request)
    assert response.status == 200
    assert response.json() == {
        'client': {'agent': {'is_finished': False, 'paid_sum': '400'}},
    }
    assert len(transactions_ng_ctx.retrieve_response[1]['operations']) == 3
    assert (
        transactions_ng_ctx.retrieve_response[1]['operations'][-1]['id']
        == '1:2'
    )
    # different sum, different revision, last operation is not finished
    request['revision'] = 2
    request['client']['agent']['sum'] = '410'
    response = await taxi_cargo_finance.post(UPSERT_URI, json=request)
    assert response.status == 500
    assert len(transactions_ng_ctx.retrieve_response[1]['operations']) == 3
    assert (
        transactions_ng_ctx.retrieve_response[1]['operations'][-1]['id']
        == '1:2'
    )
    # same sum, different revision
    request['client']['agent']['sum'] = '405'
    _make_operations_done(transactions_ng_ctx)
    response = await taxi_cargo_finance.post(UPSERT_URI, json=request)
    assert response.status == 200
    assert response.json() == {
        'client': {'agent': {'is_finished': True, 'paid_sum': '405'}},
    }
    assert len(transactions_ng_ctx.retrieve_response[1]['operations']) == 3
    assert (
        transactions_ng_ctx.retrieve_response[1]['operations'][-1]['id']
        == '1:2'
    )
