import pytest


CLID = 'clid1'


async def test_order_context(
        build_order_billing_context,
        get_event,
        order_proc,
        mock_v1_parks_retrieve,
        mock_agglomerations_context,
        mock_v1_billing_client_id,
):
    order_context = await build_order_billing_context()

    expected_context = get_event('order_billing_context')['payload']['data']
    assert order_context == expected_context


@pytest.fixture(name='build_order_billing_context')
def _build_order_billing_context(taxi_cargo_finance, load_json):
    url = '/internal/cargo-finance/flow/performer/fines/func/order-billing-context'  # noqa: E501

    async def wrapper():
        data = {'events': load_json('processing_events.json')}
        update_request = data['events'][-1]
        alias_id = update_request['payload']['data']['order_info'][
            'taxi_alias_id'
        ]
        operation_id = update_request['payload']['data']['operation_id']
        data['operation_id'] = operation_id
        params = {'taxi_alias_id': alias_id}
        response = await taxi_cargo_finance.post(url, params=params, json=data)
        assert response.status_code == 200
        return response.json()

    return wrapper


@pytest.fixture(name='mock_v1_parks_retrieve')
def _mock_v1_parks_retrieve(mockserver):
    url = 'parks-replica/v1/parks/retrieve'

    @mockserver.json_handler(url)
    def handler(request):
        return {'parks': [{'park_id': CLID, 'data': {'city': 'Москва'}}]}

    return handler


@pytest.fixture(name='mock_agglomerations_context')
def _mock_agglomerations_context(mockserver):
    @mockserver.json_handler(
        '/taxi-agglomerations/v1/geo_nodes/get_mvp_oebs_id',
    )
    def handler(request):
        return {'oebs_mvp_id': 'some_id'}

    return handler


@pytest.fixture(name='mock_v1_billing_client_id')
def _mock_v1_billing_client_id(mockserver):
    url = '/parks-replica/v1/parks/billing_client_id/retrieve'

    @mockserver.json_handler(url)
    def handler(request):
        return {'billing_client_id': 'some_id'}

    return handler
