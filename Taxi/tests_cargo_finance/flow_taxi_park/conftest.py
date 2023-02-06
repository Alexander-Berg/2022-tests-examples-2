import pytest


#  #############################
#  System states with injections


#  ##############################
#  Target handlers with shortcuts


@pytest.fixture(name='send_agent_ref')
def _send_agent_ref(taxi_cargo_finance, taxi_order_id, claim_id):
    url = '/internal/cargo-finance/flow/taxi-park/events/agent-ref'

    async def wrapper():
        params = {'taxi_order_id': taxi_order_id}
        data = {'flow': 'claims', 'entity_id': claim_id}
        response = await taxi_cargo_finance.post(url, params=params, json=data)
        assert response.status_code == 200

    return wrapper


@pytest.fixture(name='send_taxi_order_finished')
def _send_taxi_order_finished(taxi_cargo_finance, taxi_order_id):
    url = '/internal/cargo-finance/flow/taxi-park/events/taxi-order-finished'

    async def wrapper():
        params = {'taxi_order_id': taxi_order_id}
        response = await taxi_cargo_finance.post(url, params=params)
        assert response.status_code == 200

    return wrapper


@pytest.fixture(name='send_taxi_order_context')
def _send_taxi_order_context(taxi_cargo_finance, taxi_order_id):
    url = '/internal/cargo-finance/flow/taxi-park/events/taxi-order-context'

    async def wrapper(taxi_order_context):
        params = {'taxi_order_id': taxi_order_id}
        data = taxi_order_context
        response = await taxi_cargo_finance.post(url, params=params, json=data)
        assert response.status_code == 200

    return wrapper


@pytest.fixture(name='send_waybill_billing_context')
def _send_waybill_billing_context(taxi_cargo_finance, taxi_order_id):
    url = '/internal/cargo-finance/flow/taxi-park/events/waybill-billing-context'  # noqa: E501

    async def wrapper(taxi_order_context):
        params = {'taxi_order_id': taxi_order_id}
        data = taxi_order_context
        response = await taxi_cargo_finance.post(url, params=params, json=data)
        assert response.status_code == 200

    return wrapper


@pytest.fixture(name='build_waybill_billing_context')
def _build_waybill_billing_context(taxi_cargo_finance, taxi_order_id):
    url = '/internal/cargo-finance/flow/taxi-park/func/waybill-billing-context'  # noqa: E501

    async def wrapper():
        params = {'taxi_order_id': taxi_order_id}
        response = await taxi_cargo_finance.post(url, params=params)
        return response

    return wrapper


@pytest.fixture(name='build_taxi_order_context')
def _build_taxi_order_context(taxi_cargo_finance, taxi_order_id):
    url = '/internal/cargo-finance/flow/taxi-park/func/taxi-order-context'

    async def wrapper():
        params = {'taxi_order_id': taxi_order_id}
        response = await taxi_cargo_finance.post(url, params=params)
        assert response.status_code == 200
        return response.json()['context']

    return wrapper


@pytest.fixture(name='calc_sum2pay')
def _calc_sum2pay(taxi_cargo_finance, taxi_order_id):
    url = '/internal/cargo-finance/flow/taxi-park/func/sum2pay'

    async def wrapper(events):
        params = {'taxi_order_id': taxi_order_id}
        data = {'events': events}
        response = await taxi_cargo_finance.post(url, params=params, json=data)
        assert response.status_code == 200
        return response.json()

    return wrapper


#  #################
#  External handlers


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


@pytest.fixture(name='mock_waybill_find_ref')
def _mock_waybill_find_ref(mockserver):
    url = '/cargo-dispatch/v1/waybill/find-ref'

    @mockserver.json_handler(url)
    def handler(request):
        return mockserver.make_response(
            json={'waybill_external_ref': 'external_ref/123'},
        )

    return handler


@pytest.fixture(name='mock_waybill_info')
def _mock_waybill_info(mockserver, load_json):
    class WaybillInfoRequest:
        data = load_json('waybill_info_response.json')
        code = 200
        mock = None

    ctx = WaybillInfoRequest()
    url = '/cargo-dispatch/v1/waybill/info'

    @mockserver.json_handler(url)
    def handler(request):
        return mockserver.make_response(json=ctx.data, status=ctx.code)

    ctx.mock = handler

    return ctx


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


@pytest.fixture(name='flush_all')
def _flush_all(mock_py2_products):
    def wrapper():
        mock_py2_products.flush()

    return wrapper


@pytest.fixture(autouse=True)
def _setup_environment(mock_py2_products, order_proc):
    pass


#  #############################
#  etc


@pytest.fixture(name='get_event')
def _get_event(load_json):
    def wrapper(event_kind):
        for event in load_json('flow_taxi_park_events.json'):
            if event['payload']['kind'] == event_kind:
                return event
        template = 'event kind={} not found in flow_taxi_park_events.json'
        raise ValueError(template.format(event_kind))

    return wrapper
