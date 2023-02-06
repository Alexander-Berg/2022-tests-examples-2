import pytest

MOCK_NOW = '2022-07-03T19:16:00.925246+00:00'
URL = '/internal/cargo-finance/flow/trucks/func/trucks-order-billing-context'


@pytest.mark.now(MOCK_NOW)
async def test_order_context(
        build_trucks_order_billing_context,
        get_event,
        mock_find_shipper_entity_context,
):
    order_context = await build_trucks_order_billing_context()

    expected_context = get_event('trucks_order_billing_context_3')['payload'][
        'data'
    ]
    assert order_context == expected_context


@pytest.mark.parametrize(
    'carrier_id, shipper_id',
    [
        ('existing_external_ref', 'non-existing_external_ref'),
        (
            'existing_external_ref',
            'non-single_existing_external_ref_dependence',
        ),
        ('non-existing_external_ref', 'existing_external_ref'),
        (
            'non-single_existing_external_ref_dependence',
            'existing_external_ref',
        ),
    ],
)
async def test_context_build_failure_due_to_cargo_trucks(
        taxi_cargo_finance,
        load_json,
        mock_find_shipper_entity_context,
        carrier_id,
        shipper_id,
):

    params = {'trucks_order_id': 'some_order_id'}
    events = load_json('flow_trucks_events_with_incorrect_entities.json')
    events[1]['payload']['data']['carrier_id'] = carrier_id
    events[1]['payload']['data']['shipper_id'] = shipper_id
    data = {'events': events}

    response = await taxi_cargo_finance.post(URL, params=params, json=data)
    assert response.status_code == 500
