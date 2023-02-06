import pytest


@pytest.fixture(name='assert_correct_scope_queue')
def _assert_correct_scope_queue():
    def wrapper(request):
        scope_queue = 'cargo/finance_flow_claims'
        assert request.path.count(scope_queue)

    return wrapper


@pytest.fixture(name='send_taxi_order_billing_context')
def _send_taxi_order_billing_context(
        taxi_cargo_finance, mock_claims_full, claim_id,
):
    url = '/internal/cargo-finance/flow/claims/events/taxi-order-billing-context'  # noqa: E501

    async def wrapper(taxi_order_billing_context):
        params = {'claim_id': claim_id}
        data = taxi_order_billing_context
        response = await taxi_cargo_finance.post(url, params=params, json=data)
        assert response.status_code == 200

    return wrapper


@pytest.fixture(name='build_taxi_order_billing_context')
def _build_taxi_order_billing_context(
        taxi_cargo_finance, mock_claims_full, claim_id,
):
    url = '/internal/cargo-finance/flow/claims/func/taxi-order-billing-context'  # noqa: E501

    async def wrapper():
        params = {'claim_id': claim_id}
        response = await taxi_cargo_finance.post(url, params=params)
        return response

    return wrapper


@pytest.fixture(name='build_pricing_billing_context')
def _build_pricing_billing_context(
        taxi_cargo_finance, mock_v1_taxi_calc_retrieve, claim_id, calc_id,
):
    url = '/internal/cargo-finance/flow/claims/func/pricing-billing-context'

    async def wrapper():
        params = {'claim_id': claim_id, 'calc_id': calc_id}
        response = await taxi_cargo_finance.post(url, params=params)
        return response

    return wrapper


@pytest.fixture(name='mock_py2_taxi_order_context')
def _mock_py2_taxi_order_context(mockserver, load_json):
    class Py2TaxiOrderContextRequest:
        data = load_json('py2_taxi_order_context.json')
        code = 200
        mock = None

    ctx = Py2TaxiOrderContextRequest()
    url = '/py2-delivery/order-event-context'

    @mockserver.json_handler(url)
    def handler(request):
        return mockserver.make_response(json=ctx.data, status=ctx.code)

    ctx.mock = handler

    return ctx


@pytest.fixture(name='get_event')
def _get_event(load_json):
    def wrapper(event_kind):
        for event in load_json('flow_claims_events.json'):
            if event['payload']['kind'] == event_kind:
                return event
        template = 'event kind={} not found in flow_claims_events.json'
        raise ValueError(template.format(event_kind))

    return wrapper


@pytest.fixture(name='mock_phoenix_traits')
def _mock_phoenix_traits(mockserver):
    url = 'cargo-orders/v1/phoenix/traits'

    @mockserver.json_handler(url)
    def handler(request):
        return {
            'cargo_ref_id': 'order/order_id',
            'claim_id': 'claim_id',
            'is_phoenix_flow': True,
            'is_cargo_finance_billing_event': True,
        }

    return handler


@pytest.fixture(name='mock_v1_taxi_calc_retrieve')
def _mock_v1_taxi_calc_retrieve(mockserver, load_json):
    url = 'cargo-pricing/v1/taxi/calc/retrieve'

    @mockserver.json_handler(url)
    def handler(request):
        return load_json('taxi_calc_retrieve_response.json')

    return handler


@pytest.fixture(name='mock_v1_parks_retrieve')
def _mock_v1_parks_retrieve(mockserver):
    url = 'parks-replica/v1/parks/retrieve'

    @mockserver.json_handler(url)
    def handler(request):
        return {
            'parks': [
                {'park_id': 'foobar_123456', 'data': {'city': 'Москва'}},
            ],
        }

    return handler
