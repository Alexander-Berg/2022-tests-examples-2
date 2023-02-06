# pylint: disable=unused-variable
import pytest

TRACKING_URL = '/eats/v1/eats-orders-tracking/v1/tracking'
MOCK_DATETIME = '2020-10-28T18:20:00.00+00:00'

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


@pytest.fixture(name='mock_claims_performer_position')
async def _mock_performer_position(mockserver, load_json):
    @mockserver.json_handler(
        '/b2b-taxi/b2b/cargo/integration/v1/claims/performer-position',
    )
    async def _handler_b2b_location(request):
        assert (
            request.headers.get('Authorization') == 'Bearer corp_client_id_111'
        )
        mock_response = {
            'position': {'lat': 10.11, 'lon': 20.22, 'timestamp': 1234},
        }
        return mockserver.make_response(json=mock_response, status=200)

    return _handler_b2b_location


@pytest.fixture(name='mock_eats_personal_500')
def _mock_eats_personal_500(mockserver):
    @mockserver.json_handler('/personal/v1/phones/bulk_retrieve')
    def _handler_eats_personal_500(request):
        return mockserver.make_response(json={}, status=500)


@pytest.mark.now(MOCK_DATETIME)
@pytest.mark.pgsql(
    'eats_orders_tracking', files=['fill_tracked_order_payload.sql'],
)
@pytest.mark.experiments3(filename='exp3_display_matching.json')
@pytest.mark.parametrize(
    'param_headers',
    [
        pytest.param({'X-YaTaxi-User': 'eats_user_id=eater1'}, id='superapp'),
        pytest.param({'X-Eats-User': 'user_id=eater1'}, id='native'),
        pytest.param({'X-Eats-User': 'partner_user_id=eater1'}, id='partner'),
    ],
)
@pytest.mark.experiments3(
    is_config=True,
    name='eats_orders_tracking_order_dynamic_settings',
    consumers=['eats-orders-tracking/order-dynamic-settings'],
    default_value=ORDER_DYNAMIC_SETTINGS,
)
async def test_green_flow_with_different_auths(
        taxi_eats_orders_tracking,
        load_json,
        mock_eda_candidates_list_by_ids,
        mock_eats_personal,
        param_headers,
):
    response = await taxi_eats_orders_tracking.get(
        path=TRACKING_URL, headers=param_headers,
    )
    expected_response = load_json('expected_response.json')
    assert response.status_code == 200
    assert response.json() == expected_response


@pytest.mark.now(MOCK_DATETIME)
@pytest.mark.pgsql(
    'eats_orders_tracking', files=['fill_tracked_order_payload.sql'],
)
async def test_green_flow_no_auth(taxi_eats_orders_tracking):
    response = await taxi_eats_orders_tracking.get(path=TRACKING_URL)
    assert response.status_code == 200
    assert response.json() == {
        'payload': {'trackedOrders': []},
        'meta': {'checkAfter': 15, 'count': 0},
    }


@pytest.mark.now(MOCK_DATETIME)
@pytest.mark.pgsql(
    'eats_orders_tracking', files=['fill_tracked_order_payload.sql'],
)
@pytest.mark.experiments3(
    filename='exp3_display_matching_without_courier.json',
)
async def test_hide_courier(
        taxi_eats_orders_tracking,
        make_tracking_headers,
        load_json,
        mock_eda_candidates_list_by_ids,
        mock_eats_personal,
):
    # Remove courier info from the default expected response.
    expected_response = load_json('expected_response.json')
    courier_is_found = False
    for tracked_order in expected_response['payload']['trackedOrders']:
        if tracked_order['courier'] is not None:
            courier_is_found = True
            tracked_order['courier'] = None
    assert courier_is_found

    response = await taxi_eats_orders_tracking.get(
        path=TRACKING_URL, headers=make_tracking_headers(eater_id='eater1'),
    )
    assert response.status_code == 200
    assert response.json() == expected_response


@pytest.mark.now(MOCK_DATETIME)
@pytest.mark.pgsql(
    'eats_orders_tracking', files=['fill_tracked_order_payload.sql'],
)
@pytest.mark.parametrize(
    'param_application,param_expected_link',
    [
        pytest.param(
            None,
            'https://yandex.ru/maps/?'
            + 'll=30.220117,59.999102&pt=30.220117,59.999102&z=19&l=map',
            id='default',
        ),
        pytest.param(
            'app_name=web',
            'https://yandex.ru/maps/?'
            + 'll=30.220117,59.999102&pt=30.220117,59.999102&z=19&l=map',
            id='desktop',
        ),
        pytest.param(
            'app_name=android',
            'yandexmaps://maps.yandex.com/?'
            + 'll=30.220117,59.999102&pt=30.220117,59.999102&z=19&l=map',
            id='mobile',
        ),
    ],
)
@pytest.mark.experiments3(filename='exp3_display_matching.json')
@pytest.mark.experiments3(
    is_config=True,
    name='eats_orders_tracking_order_dynamic_settings',
    consumers=['eats-orders-tracking/order-dynamic-settings'],
    default_value=ORDER_DYNAMIC_SETTINGS,
)
async def test_location_link(
        taxi_eats_orders_tracking,
        make_tracking_headers,
        load_json,
        mock_eda_candidates_list_by_ids,
        param_application,
        param_expected_link,
        mock_eats_personal,
):
    # Prepare headers.
    headers_value = make_tracking_headers(eater_id='eater1')
    if param_application is None:
        headers_value.pop('X-Request-Application', None)
    else:
        headers_value['X-Request-Application'] = param_application

    # Call the handler.
    response = await taxi_eats_orders_tracking.get(
        path=TRACKING_URL, headers=headers_value,
    )
    assert response.status_code == 200

    # Check expected response.
    expected_response = load_json('expected_response.json')
    for order in expected_response['payload']['trackedOrders']:
        order['place']['locationLink'] = param_expected_link

    assert response.json() == expected_response


@pytest.mark.now(MOCK_DATETIME)
@pytest.mark.pgsql(
    'eats_orders_tracking', files=['fill_tracked_order_payload.sql'],
)
@pytest.mark.experiments3(filename='exp3_display_matching.json')
@pytest.mark.parametrize(
    'param_app_version',
    [
        pytest.param('1', id='one_part'),
        pytest.param('2.22', id='two_parts'),
        pytest.param('3.33.333', id='three_parts'),
        pytest.param('4.44.444.4444', id='four_parts'),
        pytest.param('some_text', id='invalid_version'),
    ],
)
@pytest.mark.experiments3(
    is_config=True,
    name='eats_orders_tracking_order_dynamic_settings',
    consumers=['eats-orders-tracking/order-dynamic-settings'],
    default_value=ORDER_DYNAMIC_SETTINGS,
)
async def test_unusual_app_versions(
        taxi_eats_orders_tracking,
        make_tracking_headers,
        load_json,
        mock_eda_candidates_list_by_ids,
        param_app_version,
        mock_eats_personal,
):
    headers = make_tracking_headers(eater_id='eater1')
    headers['X-App-Version'] = param_app_version
    response = await taxi_eats_orders_tracking.get(
        path=TRACKING_URL, headers=headers,
    )
    expected_response = load_json('expected_response.json')
    assert response.status_code == 200
    assert response.json() == expected_response


@pytest.mark.now(MOCK_DATETIME)
@pytest.mark.experiments3(
    is_config=True,
    name='eats_orders_tracking_order_dynamic_settings',
    consumers=['eats-orders-tracking/order-dynamic-settings'],
    default_value=ORDER_DYNAMIC_SETTINGS,
)
@pytest.mark.pgsql(
    'eats_orders_tracking', files=['fill_tracked_order_payload.sql'],
)
@pytest.mark.experiments3(filename='exp3_display_matching.json')
async def test_green_flow_with_personal_error(
        taxi_eats_orders_tracking,
        load_json,
        mock_eda_candidates_list_by_ids,
        mock_eats_personal_500,
        make_tracking_headers,
):
    response = await taxi_eats_orders_tracking.get(
        path=TRACKING_URL, headers=make_tracking_headers(eater_id='eater1'),
    )
    expected_response = load_json('expected_response.json')
    assert response.status_code == 200
    assert response.json() == expected_response


@pytest.mark.now(MOCK_DATETIME)
@pytest.mark.experiments3(
    is_config=True,
    name='eats_orders_tracking_order_dynamic_settings',
    consumers=['eats-orders-tracking/order-dynamic-settings'],
    default_value=ORDER_DYNAMIC_SETTINGS,
)
@pytest.mark.pgsql(
    'eats_orders_tracking', files=['fill_tracked_order_payload.sql'],
)
@pytest.mark.experiments3(filename='exp3_display_matching_hidden_icons.json')
async def test_hidden_icons(
        taxi_eats_orders_tracking,
        load_json,
        mock_eda_candidates_list_by_ids,
        mock_eats_personal,
        make_tracking_headers,
):
    response = await taxi_eats_orders_tracking.get(
        path=TRACKING_URL, headers=make_tracking_headers(eater_id='eater1'),
    )
    expected_response = load_json('expected_response_hidden_icons.json')
    assert response.status_code == 200
    assert response.json() == expected_response


@pytest.mark.now(MOCK_DATETIME)
@pytest.mark.pgsql(
    'eats_orders_tracking', files=['fill_tracked_order_payload.sql'],
)
@pytest.mark.experiments3(filename='exp3_display_matching.json')
@pytest.mark.experiments3(
    is_config=True,
    name='eats_orders_tracking_order_dynamic_settings',
    consumers=['eats-orders-tracking/order-dynamic-settings'],
    default_value=ORDER_DYNAMIC_SETTINGS,
)
@pytest.mark.config(
    EATS_ORDERS_TRACKING_EATERS_WITH_TRACKED_ORDERS_CACHE_SETTINGS={
        'cache_full_update_enabled': True,
        'cache_incremental_update_enabled': True,
        'cache_using_enabled': True,
        'caching_after_order_finished_seconds': 3600,
    },
)
async def test_cache(
        taxi_eats_orders_tracking,
        make_tracking_headers,
        load_json,
        mock_eda_candidates_list_by_ids,
        mock_eats_personal,
):
    headers = make_tracking_headers(eater_id='eater1')
    response = await taxi_eats_orders_tracking.get(
        path=TRACKING_URL, headers=headers,
    )
    expected_response = load_json('expected_response.json')
    assert response.status_code == 200
    assert response.json() == expected_response


@pytest.mark.now(MOCK_DATETIME)
@pytest.mark.config(
    EATS_ORDERS_TRACKING_SELECT_WAYBILL_ENABLED={
        'is_allowed_select_waybill_info': True,
    },
)
@pytest.mark.pgsql(
    'eats_orders_tracking',
    files=['fill_tracked_order_payload.sql', 'waybills.sql'],
)
@pytest.mark.experiments3(filename='exp3_display_matching.json')
@pytest.mark.experiments3(filename='exp3_use_cargo_waybills.json')
@pytest.mark.experiments3(
    is_config=True,
    name='eats_orders_tracking_order_dynamic_settings',
    consumers=['eats-orders-tracking/order-dynamic-settings'],
    default_value={
        'db_cache_ttl_seconds': 0,
        'is_db_cache_saving_enabled': True,
        'is_endpoint_claims_points_eta_enabled': False,
        'is_endpoint_claims_performer_position_enabled': True,
        'is_endpoint_eda_candidates_list_enabled': True,
        'endpoint_eats_eta_orders_estimate_using_strategy': 'disabled',
    },
)
async def test_waybill_performer_info(
        taxi_eats_orders_tracking,
        load_json,
        make_tracking_headers,
        mock_eda_candidates_list_by_ids,
        mock_eats_personal,
        mock_claims_performer_position,
):
    response = await taxi_eats_orders_tracking.get(
        path=TRACKING_URL, headers=make_tracking_headers(eater_id='eater1'),
    )
    expected_response = load_json('expected_response_by_waybill.json')
    assert response.status_code == 200
    assert response.json() == expected_response


@pytest.mark.now(MOCK_DATETIME)
@pytest.mark.config(
    EATS_ORDERS_TRACKING_SELECT_WAYBILL_ENABLED={
        'is_allowed_select_waybill_info': True,
    },
)
@pytest.mark.pgsql(
    'eats_orders_tracking',
    files=['fill_tracked_order_payload.sql', 'few_waybills_for_one_order.sql'],
)
@pytest.mark.experiments3(filename='exp3_display_matching.json')
@pytest.mark.experiments3(filename='exp3_use_cargo_waybills.json')
@pytest.mark.experiments3(
    is_config=True,
    name='eats_orders_tracking_order_dynamic_settings',
    consumers=['eats-orders-tracking/order-dynamic-settings'],
    default_value={
        'db_cache_ttl_seconds': 0,
        'is_db_cache_saving_enabled': True,
        'is_endpoint_claims_points_eta_enabled': False,
        'is_endpoint_claims_performer_position_enabled': True,
        'is_endpoint_eda_candidates_list_enabled': True,
        'endpoint_eats_eta_orders_estimate_using_strategy': 'disabled',
    },
)
async def test_few_waybill_performer_info(
        taxi_eats_orders_tracking,
        load_json,
        make_tracking_headers,
        mock_eda_candidates_list_by_ids,
        mock_eats_personal,
        mock_claims_performer_position,
):
    response = await taxi_eats_orders_tracking.get(
        path=TRACKING_URL, headers=make_tracking_headers(eater_id='eater1'),
    )
    expected_response = load_json('expected_response_by_waybill.json')
    assert response.status_code == 200
    assert response.json() == expected_response
