import pytest


@pytest.fixture(name='assert_correct_scope_queue')
def _assert_correct_scope_queue():
    def wrapper(request):
        scope_queue = 'cargo/finance_flow_trucks'
        assert request.path.count(scope_queue)

    return wrapper


@pytest.fixture(name='send_pay_shipping_contract')
def _send_pay_shipping_contract(taxi_cargo_finance, trucks_order_id):
    url = '/internal/cargo-finance/flow/trucks/events/pay-shipping-contract'  # noqa: E501

    async def wrapper(trucks_order_doc):
        params = {'trucks_order_id': trucks_order_id}
        data = trucks_order_doc
        response = await taxi_cargo_finance.post(url, params=params, json=data)
        assert response.status_code == 200

    return wrapper


@pytest.fixture(name='send_trucks_order_billing_context')
def _send_trucks_order_billing_context(taxi_cargo_finance, trucks_order_id):
    url = '/internal/cargo-finance/flow/trucks/events/trucks-order-billing-context'  # noqa: E501

    async def wrapper(trucks_order_billing_context):
        params = {'trucks_order_id': trucks_order_id}
        data = trucks_order_billing_context
        response = await taxi_cargo_finance.post(url, params=params, json=data)
        assert response.status_code == 200

    return wrapper


@pytest.fixture(name='build_trucks_order_billing_context')
def _build_trucks_order_billing_context(
        taxi_cargo_finance, load_json, trucks_order_id,
):
    url = '/internal/cargo-finance/flow/trucks/func/trucks-order-billing-context'  # noqa: E501

    async def wrapper():
        params = {'trucks_order_id': trucks_order_id}
        data = {'events': load_json('flow_trucks_events.json')}
        response = await taxi_cargo_finance.post(url, params=params, json=data)
        assert response.status_code == 200
        return response.json()['context']

    return wrapper


@pytest.fixture(name='get_event')
def _get_event(load_json):
    def wrapper(event_kind):
        for event in load_json('flow_trucks_events.json'):
            if event['event_id'] == event_kind:
                return event
        template = 'event event_id={} not found in flow_trucks_events.json'
        raise ValueError(template.format(event_kind))

    return wrapper


@pytest.fixture(name='mock_find_shipper_entity_context')
def _mock_find_shipper_entity_context(mockserver):
    url = r'/cargo-trucks/internal/cargo-trucks/(?P<shipper_entity>\w+)/find'

    @mockserver.json_handler(url, regex=True)
    def handler(request, shipper_entity):
        external_ref = request.query['external_ref']
        if external_ref == 'existing_external_ref':
            return {
                shipper_entity: [
                    {
                        'external_ref': 'existing_external_ref',
                        'billing': {
                            'client_id': shipper_entity + '/1000',
                            'person_id': shipper_entity + '/2000',
                            'contract_id': shipper_entity + '/3000',
                            'external_id': shipper_entity + '/4000',
                        },
                    },
                ],
            }
        if external_ref == 'non-single_existing_external_ref_dependence':
            return {
                shipper_entity: [
                    {
                        'external_ref': 'existing_external_ref_1',
                        'billing': {
                            'client_id': '0',
                            'person_id': '1',
                            'contract_id': '2',
                            'external_id': '3',
                        },
                    },
                    {
                        'external_ref': 'existing_external_ref_2',
                        'billing': {
                            'client_id': '4',
                            'person_id': '5',
                            'contract_id': '6',
                            'external_id': '7',
                        },
                    },
                ],
            }
        return {shipper_entity: []}

    return handler
