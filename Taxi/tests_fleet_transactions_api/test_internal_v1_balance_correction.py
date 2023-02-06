import json

import pytest


ENDPOINT_URL = '/internal/v1/balance-correction'
MOCK_URL = '/billing-orders/v2/process/async'


@pytest.mark.parametrize(
    'body_patch, transaction_patch',
    [
        ({'park_id': 'no_park'}, {}),
        ({'driver_profile_id': 'no_driver'}, {}),
        ({}, {'currency_code': 'EUR'}),
        ({}, {'amount': 'trash'}),
        ({}, {'transaction_id': ''}),
        ({}, {'agreement_id': 'taxi/something_else'}),
        ({}, {'sub_account': 'payment/something_else'}),
        ({}, {'agreement_id': 'taxi/yandex_ride', 'sub_account': 'park_only'}),
    ],
)
async def test_bad(
        taxi_fleet_transactions_api,
        load_json,
        mock_fleet_parks_list,
        driver_profiles,
        body_patch,
        transaction_patch,
):
    request_json = load_json('service_request.json')
    request_json.update(body_patch)
    request_json['transactions'][0].update(transaction_patch)

    response = await taxi_fleet_transactions_api.post(
        ENDPOINT_URL, json=request_json,
    )

    assert response.status_code == 400, response.text


@pytest.mark.now('2021-02-03T13:33:17+00:00')
async def test_ok(
        taxi_fleet_transactions_api,
        load_json,
        mockserver,
        mock_fleet_parks_list,
        driver_profiles,
):
    @mockserver.json_handler(MOCK_URL)
    async def mock_billing_orders(request):
        request_topics = [
            order['topic']
            for order in json.loads(request.get_data())['orders']
        ]
        response_json = load_json('orders_response.json')
        response_json['orders'] = [
            order
            for order in response_json['orders']
            if order['topic'] in request_topics
        ]
        return response_json

    response = await taxi_fleet_transactions_api.post(
        ENDPOINT_URL, json=load_json('service_request.json'),
    )

    assert response.status_code == 200, response.text
    assert response.json() == load_json('service_response.json')

    assert mock_fleet_parks_list.mock_parks_list.has_calls

    full_orders_request_json = {'orders': []}

    while mock_billing_orders.has_calls:
        orders_request = mock_billing_orders.next_call()['request']
        assert orders_request.method == 'POST'
        orders_request_json = json.loads(orders_request.get_data())
        full_orders_request_json['orders'] += orders_request_json['orders']

    assert full_orders_request_json == load_json('orders_request.json')


async def test_skip_account_validation(
        taxi_fleet_transactions_api,
        load_json,
        mock_fleet_parks_list,
        driver_profiles,
        billing_orders,
):
    request_json = load_json('service_request.json')
    request_json['skip_account_validation'] = True
    request_json['transactions'][0].update(
        {
            'agreement_id': 'taxi/something_else',
            'sub_account': 'payment/something_else',
        },
    )

    response = await taxi_fleet_transactions_api.post(
        ENDPOINT_URL, json=request_json,
    )

    assert response.status_code == 200


@pytest.mark.now('2021-02-03T13:33:17+00:00')
async def test_many(
        taxi_fleet_transactions_api,
        load_json,
        mockserver,
        mock_fleet_parks_list,
        driver_profiles,
):
    def _make_transaction_id(index):
        return f'index_{index}'

    def _make_transaction(index):
        return {
            'transaction_id': _make_transaction_id(index),
            'source_event_at': '2021-02-03T16:46:00+03:00',
            'agreement_id': 'taxi/park_services',
            'sub_account': 'arbitrary/other',
            'currency_code': 'RUB',
            'amount': f'{-99 + index}.00',
            'details': {'index': f'{index}'},
        }

    def _make_request(count):
        return {
            'park_id': '7ad35b',
            'driver_profile_id': '9c5e35',
            'transactions': [_make_transaction(i) for i in range(0, count)],
        }

    def _make_topic(transaction_index):
        return (
            'taxi/taximeter/payment/correction/7ad35b/9c5e35/'
            + _make_transaction_id(transaction_index)
        )

    def _make_doc(transaction_index):
        return {
            'topic': _make_topic(transaction_index),
            'doc_id': 111 + 3 * transaction_index,
        }

    def _make_order(transaction_index):
        return {'external_ref': '0', **_make_doc(transaction_index)}

    @mockserver.json_handler(MOCK_URL)
    async def mock_billing_orders(request):
        indices = [
            int(order['data']['entries'][0]['details']['index'])
            for order in request.json['orders']
        ]
        assert len(indices) <= 5, 'too many orders'
        return {'orders': [_make_order(i) for i in indices]}

    transactions_count = 42

    response = await taxi_fleet_transactions_api.post(
        ENDPOINT_URL, json=_make_request(transactions_count),
    )

    assert response.status_code == 200, response.text
    assert response.json() == {
        'docs': [_make_doc(i) for i in range(0, transactions_count)],
    }

    assert mock_fleet_parks_list.mock_parks_list.has_calls
    assert mock_billing_orders.has_calls


async def test_status_code_429(
        taxi_fleet_transactions_api,
        load_json,
        mockserver,
        mock_fleet_parks_list,
        driver_profiles,
):
    @mockserver.json_handler(MOCK_URL)
    async def mock_billing_orders(request):
        return mockserver.make_response(status=429)

    response = await taxi_fleet_transactions_api.post(
        ENDPOINT_URL, json=load_json('service_request.json'),
    )

    assert response.status_code == 429, response.text
    assert mock_billing_orders.has_calls


async def test_use_source_event_at(
        taxi_fleet_transactions_api,
        load_json,
        mockserver,
        mock_fleet_parks_list,
        driver_profiles,
        billing_orders,
):
    request = load_json('service_request.json')
    request['use_source_event_at'] = True
    response = await taxi_fleet_transactions_api.post(
        ENDPOINT_URL, json=request,
    )

    assert response.status_code == 200
    assert billing_orders.get_event_ats() == {
        t['source_event_at'] for t in request['transactions']
    }
