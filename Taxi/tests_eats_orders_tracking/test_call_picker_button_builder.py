import pytest

TRACKING_URL = '/eats/v1/eats-orders-tracking/v1/tracking'


@pytest.mark.config(
    EATS_ORDERS_TRACKING_CALL_TO_PICKER_BUTTON_BUILDING_STRATEGIES={
        '__default__': {
            'has_masked_phone': 'show_masked',
            'has_not_masked_phone': 'show_contact_us',
            'has_no_phone': 'show_contact_us',
            'unrecognized_error': 'show_contact_us',
        },
        'RU': {
            'has_masked_phone': 'show_masked',
            'has_not_masked_phone': 'show_not_masked',
            'has_no_phone': 'show_contact_us',
            'unrecognized_error': 'show_contact_us',
        },
    },
)
@pytest.mark.pgsql(
    'eats_orders_tracking', files=['fill_tracked_order_payload.sql'],
)
@pytest.mark.experiments3(
    filename='exp3_display_matching_for_call_picker.json',
)
async def test_call_picker_button(
        taxi_eats_orders_tracking, make_tracking_headers, mock_eats_personal,
):
    # Checking building "Call picker button"
    # according to building strategies from config
    response = await taxi_eats_orders_tracking.get(
        path=TRACKING_URL, headers=make_tracking_headers(eater_id='eater1'),
    )
    orders = response.json()['payload']['trackedOrders']
    assert response.status_code == 200
    assert len(orders) == 4

    # masked
    assert orders[0]['order']['orderNr'] == '000000-000000'
    assert orders[0]['actions'] == [
        {
            'type': 'call',
            'title': 'Call picker',
            'payload': {
                'contact_type': 'picker',
                'phone': '124,456',
                'alert_title': 'alert_title_key',
            },
            'actions': None,
        },
    ]
    # not masked
    assert orders[1]['order']['orderNr'] == '000000-000001'
    assert orders[1]['actions'] == [
        {
            'type': 'call',
            'title': 'Call picker',
            'payload': {
                'contact_type': 'picker',
                'phone': '124',
                'alert_title': 'alert_title_key',
            },
            'actions': None,
        },
    ]
    # call us
    assert orders[2]['order']['orderNr'] == '000000-000002'
    assert orders[2]['actions'] == [
        {
            'type': 'contact_us',
            'title': 'buttons.default.contact_us',
            'payload': {'alert_title': 'alert_title_key'},
            'actions': None,
        },
    ]
    # picker has phone, but BY config strategy: call us
    assert orders[3]['order']['orderNr'] == '000000-000003'
    assert orders[3]['actions'] == [
        {
            'type': 'contact_us',
            'title': 'buttons.default.contact_us',
            'payload': {'alert_title': 'alert_title_key'},
            'actions': None,
        },
    ]
