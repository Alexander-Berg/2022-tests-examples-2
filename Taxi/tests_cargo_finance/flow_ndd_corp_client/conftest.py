import pytest


#  #############################
#  System states with injections


#  ##############################
#  Target handlers with shortcuts


@pytest.fixture(name='send_order_finalization_started')
def _send_order_finalization_started(taxi_cargo_finance, ndd_order_id):
    url = '/internal/cargo-finance/flow/ndd-corp-client/events/order-finalization-started'  # noqa: E501

    async def wrapper():
        params = {'ndd_order_id': ndd_order_id}
        response = await taxi_cargo_finance.post(url, params=params)
        assert response.status_code == 200

    return wrapper


@pytest.fixture(name='send_order_billing_context')
def _send_order_billing_context(taxi_cargo_finance, ndd_order_id):
    url = '/internal/cargo-finance/flow/ndd-corp-client/events/order-billing-context/delivery-client-b2b-logistics-payment'  # noqa: E501

    async def wrapper(order_billing_context):
        params = {'ndd_order_id': ndd_order_id}
        data = order_billing_context
        response = await taxi_cargo_finance.post(url, params=params, json=data)
        assert response.status_code == 200

    return wrapper


@pytest.fixture(name='build_order_billing_context_client_b2b')
def _build_order_billing_context_client_b2b(taxi_cargo_finance, ndd_order_id):
    url = '/internal/cargo-finance/flow/ndd-corp-client/func/order-billing-context/delivery-client-b2b-logistics-payment'  # noqa: E501

    async def wrapper():
        params = {'ndd_order_id': ndd_order_id}
        response = await taxi_cargo_finance.post(url, params=params)
        assert response.status_code == 200
        return response.json()

    return wrapper


@pytest.fixture(name='calc_sum2pay')
def _calc_sum2pay(taxi_cargo_finance, ndd_order_id):
    url = '/internal/cargo-finance/flow/ndd-corp-client/func/sum2pay'

    async def wrapper(events):
        params = {'ndd_order_id': ndd_order_id}
        data = {'events': events}
        response = await taxi_cargo_finance.post(url, params=params, json=data)
        assert response.status_code == 200
        return response.json()

    return wrapper


#  #################
#  External handlers


@pytest.fixture(name='mock_build_order_billing_context_client_b2b')
def _mock_build_order_billing_context_client_b2b(
        mockserver, build_order_context_client_b2b_response,
):
    url = '/logistic-platform-uservices/internal/logistic-platform/next-day-delivery/order/billing-context'  # noqa: E501

    @mockserver.json_handler(url)
    def handler(request):
        return build_order_context_client_b2b_response.make(request)

    return handler


@pytest.fixture(name='build_order_context_client_b2b_response')
def _build_order_billing_context_response(load_json):
    class NddOrderBillingContextResponse:
        def __init__(self):
            self.data = load_json(
                'flow_ndd_corp_client/order_billing_context_delivery_client_b2b_logistics_payment.json',  # noqa: E501
            )

        def make(self, request):
            return self.data

    return NddOrderBillingContextResponse()


@pytest.fixture(name='flush_all')
def _flush_all(mock_build_order_billing_context_client_b2b):
    def wrapper():
        mock_build_order_billing_context_client_b2b.flush()

    return wrapper


@pytest.fixture(autouse=True)
def _setup_environment(mock_build_order_billing_context_client_b2b):
    pass


#  #############################
#  etc


@pytest.fixture(name='get_event')
def _get_event(load_json):
    def wrapper(event_kind):
        for event in load_json('flow_ndd_corp_client_events.json'):
            if event['payload']['kind'] == event_kind:
                return event
        template = (
            'event kind={} not found in flow_ndd_corp_client_events.json'
        )
        raise ValueError(template.format(event_kind))

    return wrapper
