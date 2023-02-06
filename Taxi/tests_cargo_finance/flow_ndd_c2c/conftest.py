import pytest


@pytest.fixture(name='mock_cargo_finance_dummy_init')
def _mock_cargo_finance_dummy_init(mockserver):
    url = 'cargo-finance/internal/cargo-finance/events/dummy-init'

    @mockserver.json_handler(url)
    def handler(request):
        return {}

    return handler


@pytest.fixture(name='mock_logistic_platform_c2c_payment_context')
def _mock_logistic_platform_c2c_payment_context(
        mockserver, build_c2c_payment_context_response,
):
    url = '/logistic-platform-uservices/api/c2c/platform/payment/context'

    @mockserver.json_handler(url)
    def handler(request):
        return build_c2c_payment_context_response.make(request)

    return handler


@pytest.fixture(name='build_c2c_payment_context_response')
def _build_c2c_payment_context_response(load_json):
    class NddOrderBillingContextResponse:
        def __init__(self):
            self.data = load_json('c2c_logistic_payment_context.json')

        def make(self, request):
            return self.data

    return NddOrderBillingContextResponse()


@pytest.fixture(name='build_billing_context')
def _build_billing_context(taxi_cargo_finance):
    url = '/internal/cargo-finance/flow/ndd-c2c/func/billing-context'

    async def wrapper(ndd_order_id):
        params = {'ndd_order_id': ndd_order_id}
        response = await taxi_cargo_finance.post(url, params=params)
        assert response.status_code == 200
        return response.json()['context']

    return wrapper


@pytest.fixture(name='calc_sum2pay')
def _calc_sum2pay(taxi_cargo_finance):
    url = '/internal/cargo-finance/flow/ndd-c2c/func/sum2pay'

    async def wrapper(events, ndd_order_id):
        params = {'taxi_order_id': ndd_order_id}
        data = {'events': events}
        response = await taxi_cargo_finance.post(url, params=params, json=data)
        assert response.status_code == 200
        return response.json()

    return wrapper


@pytest.fixture(name='assert_correct_scope_queue')
def _assert_correct_scope_queue():
    def wrapper(request):
        scope_queue = 'cargo/finance_flow_ndd_c2c'
        assert request.path.count(scope_queue)

    return wrapper


@pytest.fixture(name='get_event')
def _get_event(load_json):
    def wrapper(event_kind):
        for event in load_json('flow_ndd_c2c_events.json'):
            if event['payload']['kind'] == event_kind:
                return event
        template = 'event kind={} not found in ndd_c2c_events.json'
        raise ValueError(template.format(event_kind))

    return wrapper
