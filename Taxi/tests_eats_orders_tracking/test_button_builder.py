# pylint: disable=unused-variable
import pytest

TRACKING_URL = '/eats/v1/eats-orders-tracking/v1/tracking'
MOCK_DATETIME = '2020-10-28T18:20:00.00+00:00'
PHONE_ROVER_SUPPORT = '+78006001234'
PHONE_CALL_CENTER = '+78006005678'

ORDER_DYNAMIC_SETTINGS = {
    'db_cache_ttl_seconds': 0,
    'is_db_cache_saving_enabled': True,
    'is_endpoint_claims_points_eta_enabled': True,
    'is_endpoint_claims_performer_position_enabled': True,
    'is_endpoint_eda_candidates_list_enabled': True,
    'endpoint_eats_eta_orders_estimate_using_strategy': 'disabled',
}


@pytest.fixture(name='mock_eda_candidates_list_by_ids')
def _mock_eda_candidates_list_by_ids(mockserver):
    @mockserver.json_handler('/eda-candidates/list-by-ids')
    def _handler_eda_candidates_list_by_ids(request):
        assert len(request.json['ids']) == 1
        mock_response = {'candidates': [{'position': [20.22, 10.11]}]}
        return mockserver.make_response(json=mock_response, status=200)


@pytest.mark.now(MOCK_DATETIME)
@pytest.mark.pgsql(
    'eats_orders_tracking', files=['fill_tracked_order_payload.sql'],
)
@pytest.mark.experiments3(
    is_config=True,
    name='eats_orders_tracking_order_dynamic_settings',
    consumers=['eats-orders-tracking/order-dynamic-settings'],
    default_value=ORDER_DYNAMIC_SETTINGS,
)
@pytest.mark.experiments3(filename='exp3_display_matching.json')
async def test_button_builder(
        taxi_eats_orders_tracking,
        make_tracking_headers,
        load_json,
        mock_eda_candidates_list_by_ids,
        mock_eats_personal,
):
    response = await taxi_eats_orders_tracking.get(
        path=TRACKING_URL, headers=make_tracking_headers(eater_id='eater1'),
    )
    expected_response = load_json('expected_response_for_button_builder.json')
    assert response.status_code == 200
    assert response.json() == expected_response


@pytest.mark.now(MOCK_DATETIME)
@pytest.mark.pgsql(
    'eats_orders_tracking', files=['fill_tracked_order_payload.sql'],
)
@pytest.mark.experiments3(
    filename='exp3_display_matching_for_repeat_order.json',
)
@pytest.mark.experiments3(
    is_config=True,
    name='eats_orders_tracking_order_dynamic_settings',
    consumers=['eats-orders-tracking/order-dynamic-settings'],
    default_value=ORDER_DYNAMIC_SETTINGS,
)
async def test_repeat_order_button(
        taxi_eats_orders_tracking,
        make_tracking_headers,
        load_json,
        mock_eda_candidates_list_by_ids,
        mock_eats_personal,
):
    response = await taxi_eats_orders_tracking.get(
        path=TRACKING_URL, headers=make_tracking_headers(eater_id='eater1'),
    )
    expected_response = load_json('expected_response_for_repeat_order.json')
    assert response.status_code == 200
    assert response.json() == expected_response


@pytest.fixture(name='mock_eats_cargo_claims')
def _mock_eats_cargo_claims(mockserver):
    @mockserver.json_handler(
        '/b2b-taxi/b2b/cargo/integration/v1/claims/points-eta',
    )
    def _handler_cargo_claims_info(request):
        return mockserver.make_response(json={}, status=200)

    @mockserver.json_handler(
        '/b2b-taxi/b2b/cargo/integration/v1/claims/performer-position',
    )
    def _handler_cargo_claims_performer_position(request):
        return mockserver.make_response(json={}, status=200)


@pytest.mark.now(MOCK_DATETIME)
@pytest.mark.config(
    EATS_ORDERS_TRACKING_CALL_CENTER_PHONE={
        'call_center_phone': PHONE_CALL_CENTER,
    },
)
@pytest.mark.pgsql(
    'eats_orders_tracking',
    files=['fill_tracked_order_payload.sql', 'fill_data_for_call_courier.sql'],
)
@pytest.mark.experiments3(
    filename='exp3_display_matching_for_call_courier.json',
)
async def test_call_courier_button_builder(
        taxi_eats_orders_tracking,
        make_tracking_headers,
        load_json,
        mock_eda_candidates_list_by_ids,
        mock_eats_personal,
        mock_eats_cargo_claims,
):
    response = await taxi_eats_orders_tracking.get(
        path=TRACKING_URL, headers=make_tracking_headers(eater_id='eater1'),
    )

    orders = response.json()['payload']['trackedOrders']
    assert response.status_code == 200
    assert len(orders) == 6

    # Personal courier phone number.
    assert orders[0]['order']['orderNr'] == '000000-000000'
    assert orders[0]['actions'] == [
        {
            'type': 'call',
            'title': 'button_title_1',
            'payload': {
                'contact_type': 'courier',
                'phone': '123',
                'alert_title': 'alert_title_key',
            },
            'actions': None,
        },
    ]
    assert orders[0]['contact'] == {'type': 'courier', 'phone': '123'}

    assert orders[1]['order']['orderNr'] == '000000-000001'
    assert orders[1]['actions'] == [
        {
            'type': 'contact_us',
            'title': 'buttons.default.contact_us',
            'payload': {'alert_title': 'alert_title_key'},
            'actions': None,
        },
    ]
    assert orders[1]['contact'] == {
        'type': 'call_center',
        'phone': PHONE_CALL_CENTER,
    }

    assert orders[2]['order']['orderNr'] == '000000-000002'
    assert orders[2]['actions'] == [
        {
            'type': 'contact_us',
            'title': 'buttons.default.contact_us',
            'payload': {'alert_title': 'alert_title_key'},
            'actions': None,
        },
    ]
    assert orders[2]['contact'] == {
        'type': 'call_center',
        'phone': PHONE_CALL_CENTER,
    }

    # Masked courier phone number.
    assert orders[3]['order']['orderNr'] == '000000-000003'
    assert orders[3]['actions'] == [
        {
            'type': 'call',
            'title': 'button_title_1',
            'payload': {
                'contact_type': 'courier',
                'phone': '000003,000003',
                'alert_title': 'alert_title_key',
            },
            'actions': None,
        },
    ]
    assert orders[3]['contact'] == {
        'type': 'courier',
        'phone': '000003,000003',
    }

    assert orders[4]['order']['orderNr'] == '000000-000004'
    assert orders[4]['actions'] == [
        {
            'type': 'contact_us',
            'title': 'buttons.default.contact_us',
            'payload': {'alert_title': 'alert_title_key'},
            'actions': None,
        },
    ]
    assert orders[4]['contact'] == {
        'type': 'call_center',
        'phone': PHONE_CALL_CENTER,
    }

    assert orders[5]['order']['orderNr'] == '000000-000005'
    assert orders[5]['actions'] == [
        {
            'type': 'contact_us',
            'title': 'buttons.default.contact_us',
            'payload': {'alert_title': 'alert_title_key'},
            'actions': None,
        },
    ]
    assert orders[5]['contact'] == {
        'type': 'call_center',
        'phone': PHONE_CALL_CENTER,
    }


@pytest.mark.config(
    EATS_ORDERS_TRACKING_ROVER={'support_phone_number': PHONE_ROVER_SUPPORT},
)
@pytest.mark.now(MOCK_DATETIME)
@pytest.mark.pgsql(
    'eats_orders_tracking',
    files=['fill_tracked_order_payload.sql', 'fill_data_for_call_courier.sql'],
)
@pytest.mark.experiments3(
    filename='exp3_display_matching_for_call_courier.json',
)
async def test_call_courier_button_builder_rover(
        taxi_eats_orders_tracking,
        make_tracking_headers,
        load_json,
        mock_eda_candidates_list_by_ids,
        mock_eats_personal,
        mock_eats_cargo_claims,
):
    response = await taxi_eats_orders_tracking.get(
        path=TRACKING_URL, headers=make_tracking_headers(eater_id='eater2'),
    )

    orders = response.json()['payload']['trackedOrders']
    assert response.status_code == 200
    assert orders[0]['actions'] == [
        {
            'type': 'call',
            'title': 'button_title_1',
            'payload': {
                'contact_type': 'courier',
                'phone': PHONE_ROVER_SUPPORT,
                'alert_title': 'alert_title_key',
            },
            'actions': None,
        },
    ]
    assert orders[0]['contact'] == {
        'type': 'courier',
        'phone': PHONE_ROVER_SUPPORT,
    }


@pytest.mark.now(MOCK_DATETIME)
@pytest.mark.pgsql(
    'eats_orders_tracking', files=['fill_data_for_call_place.sql'],
)
@pytest.mark.experiments3(filename='exp3_display_matching_for_call_place.json')
async def test_call_place_button_builder(
        taxi_eats_orders_tracking,
        make_tracking_headers,
        load_json,
        mock_eda_candidates_list_by_ids,
        mock_eats_personal,
):
    response = await taxi_eats_orders_tracking.get(
        path=TRACKING_URL, headers=make_tracking_headers(eater_id='eater1'),
    )

    orders = response.json()['payload']['trackedOrders']
    assert response.status_code == 200
    assert len(orders) == 5
    assert orders[0]['actions'] == [
        {
            'type': 'call',
            'title': 'button_title_1',
            'payload': {
                'contact_type': 'place',
                'phone': '111111111,123',
                'alert_title': 'alert_title_key',
            },
            'actions': None,
        },
    ]
    assert orders[1]['actions'] == [
        {
            'type': 'contact_us',
            'title': 'buttons.default.contact_us',
            'payload': {'alert_title': 'alert_title_key'},
            'actions': None,
        },
    ]
    assert orders[2]['actions'] == [
        {
            'type': 'contact_us',
            'title': 'buttons.default.contact_us',
            'payload': {'alert_title': 'alert_title_key'},
            'actions': None,
        },
    ]
    assert orders[3]['actions'] == [
        {
            'type': 'call',
            'title': 'button_title_1',
            'payload': {
                'alert_title': 'alert_title_key',
                'contact_type': 'place',
                'phone': '123,12345',
            },
            'actions': None,
        },
    ]
    assert orders[4]['actions'] == [
        {
            'type': 'contact_us',
            'title': 'buttons.default.contact_us',
            'payload': {'alert_title': 'alert_title_key'},
            'actions': None,
        },
    ]


@pytest.mark.now(MOCK_DATETIME)
@pytest.mark.pgsql(
    'eats_orders_tracking',
    files=['fill_data_for_call_place_building_strategy.sql'],
)
@pytest.mark.config(
    EATS_ORDERS_TRACKING_CALL_TO_PLACE_BUTTON_BUILDING_STRATEGIES_2={
        '__default__': {
            'success': 'show_not_masked',
            'disabled_for_region': 'show_not_masked',
            'disabled_globally': 'show_not_masked',
            'place_has_no_phone': 'show_contact_us',
            'has_extension': 'show_not_masked',
            'masking_error': 'show_not_masked',
            'unrecognized_error': 'show_contact_us',
        },
        'RU': {
            'success': 'show_masked',
            'disabled_for_region': 'show_not_masked',
            'disabled_globally': 'show_not_masked',
            'place_has_no_phone': 'show_contact_us',
            'has_extension': 'show_not_masked',
            'masking_error': 'show_not_masked',
            'unrecognized_error': 'show_contact_us',
        },
    },
)
@pytest.mark.experiments3(filename='exp3_display_matching_for_call_place.json')
async def test_call_place_building_strategy(
        taxi_eats_orders_tracking,
        make_tracking_headers,
        load_json,
        mock_eda_candidates_list_by_ids,
        mock_eats_personal,
):
    response = await taxi_eats_orders_tracking.get(
        path=TRACKING_URL, headers=make_tracking_headers(eater_id='eater1'),
    )

    orders = response.json()['payload']['trackedOrders']
    assert response.status_code == 200
    assert len(orders) == 2
    assert orders[0]['actions'] == [
        {
            'type': 'call',
            'title': 'button_title_1',
            'payload': {
                'contact_type': 'place',
                'phone': '111111111,123',
                'alert_title': 'alert_title_key',
            },
            'actions': None,
        },
    ]
    assert orders[1]['actions'] == [
        {
            'type': 'call',
            'title': 'button_title_1',
            'payload': {
                'contact_type': 'place',
                'phone': '123,12345',
                'alert_title': 'alert_title_key',
            },
            'actions': None,
        },
    ]


@pytest.mark.now(MOCK_DATETIME)
@pytest.mark.pgsql(
    'eats_orders_tracking', files=['fill_tracked_order_payload.sql'],
)
@pytest.mark.experiments3(
    filename='exp3_display_matching_for_cancel_order.json',
)
@pytest.mark.experiments3(filename='exp3_cancel_order_button_flag.json')
@pytest.mark.experiments3(
    is_config=True,
    name='eats_orders_tracking_order_dynamic_settings',
    consumers=['eats-orders-tracking/order-dynamic-settings'],
    default_value=ORDER_DYNAMIC_SETTINGS,
)
async def test_cancel_order_button(
        taxi_eats_orders_tracking,
        make_tracking_headers,
        load_json,
        mock_eda_candidates_list_by_ids,
        mock_eats_personal,
):
    response = await taxi_eats_orders_tracking.get(
        path=TRACKING_URL, headers=make_tracking_headers(eater_id='eater1'),
    )
    expected_response = load_json('expected_response_for_cancel_order.json')
    assert response.status_code == 200
    assert response.json() == expected_response
