import datetime

import pytest

TRACKING_URL = '/eats/v1/eats-orders-tracking/v1/tracking'
MOCK_DATETIME = '2020-10-28T18:20:00.00+00:00'
ORDER_NR = '000000-000000'


@pytest.fixture(name='mock_claims_points_eta')
def _mock_claims_points_eta(mockserver, load_json):
    @mockserver.json_handler(
        '/b2b-taxi/b2b/cargo/integration/v1/claims/points-eta',
    )
    def _handler(request):
        mock_response = {
            'id': 'temp_id',
            'route_points': [
                {
                    'id': 1,
                    'address': {
                        'fullname': '1',
                        'coordinates': [35.8, 55.4],
                        'country': '1',
                        'city': '1',
                        'street': '1',
                        'building': '1',
                    },
                    'type': 'source',
                    'visit_order': 1,
                    'visit_status': 'pending',
                    'visited_at': {},
                },
                {
                    'id': 2,
                    'address': {
                        'fullname': '2',
                        'coordinates': [37.8, 55.4],
                        'country': '2',
                        'city': '2',
                        'street': '2',
                        'building': '2',
                    },
                    'type': 'destination',
                    'visit_order': 2,
                    'visit_status': 'pending',
                    'visited_at': {'expected': '2020-10-28T18:28:00.00+00:00'},
                },
                {
                    'id': 3,
                    'address': {
                        'fullname': '3',
                        'coordinates': [40.8, 50.4],
                        'country': '3',
                        'city': '3',
                        'street': '3',
                        'building': '3',
                    },
                    'type': 'destination',
                    'visit_order': 3,
                    'visit_status': 'pending',
                    'visited_at': {'expected': '2020-10-28T19:00:00.00+00:00'},
                },
            ],
            'performer_position': [37.8, 55.4],
        }
        return mockserver.make_response(json=mock_response, status=200)


@pytest.fixture(name='mock_claims_points_eta_arrived_to_place')
def _mock_claims_points_eta_arrived_to_place(mockserver, load_json):
    @mockserver.json_handler(
        '/b2b-taxi/b2b/cargo/integration/v1/claims/points-eta',
    )
    def _handler(request):
        mock_response = {
            'id': 'temp_id',
            'route_points': [
                {
                    'id': 1,
                    'address': {
                        'fullname': '1',
                        'coordinates': [35.8, 55.4],
                        'country': '1',
                        'city': '1',
                        'street': '1',
                        'building': '1',
                    },
                    'type': 'source',
                    'visit_order': 1,
                    'visit_status': 'arrived',
                    'visited_at': {},
                },
                {
                    'id': 2,
                    'address': {
                        'fullname': '2',
                        'coordinates': [37.8, 55.4],
                        'country': '2',
                        'city': '2',
                        'street': '2',
                        'building': '2',
                    },
                    'type': 'destination',
                    'visit_order': 2,
                    'visit_status': 'pending',
                    'visited_at': {'expected': '2020-10-28T18:28:00.00+00:00'},
                },
                {
                    'id': 3,
                    'address': {
                        'fullname': '3',
                        'coordinates': [40.8, 50.4],
                        'country': '3',
                        'city': '3',
                        'street': '3',
                        'building': '3',
                    },
                    'type': 'destination',
                    'visit_order': 3,
                    'visit_status': 'pending',
                    'visited_at': {'expected': '2020-10-28T19:00:00.00+00:00'},
                },
            ],
            'performer_position': [37.8, 55.4],
        }
        return mockserver.make_response(json=mock_response, status=200)


@pytest.fixture(name='mock_eats_eta_orders_estimate')
def _mock_eats_eta_orders_estimate(mockserver, load_json):
    @mockserver.json_handler('/eats-eta/v1/eta/orders/estimate')
    def _handler(request):
        mock_response = {
            'orders': [
                {
                    'order_nr': ORDER_NR,
                    'estimations': [
                        {
                            'name': 'courier_arrival_at',
                            'calculated_at': MOCK_DATETIME,
                            'status': 'in_progress',
                        },
                        {
                            'name': 'delivery_at',
                            'calculated_at': MOCK_DATETIME,
                            'expected_at': '2020-10-28T18:32:00.00+00:00',
                        },
                    ],
                },
            ],
            'not_found_orders': [],
        }
        return mockserver.make_response(json=mock_response, status=200)


@pytest.fixture(name='mock_claims_performer_position')
def _mock_performer_position(mockserver, load_json):
    @mockserver.json_handler(
        '/b2b-taxi/b2b/cargo/integration/v1/claims/performer-position',
    )
    def _handler_b2b_location(request):
        mock_response = {
            'position': {'lat': 1.0, 'lon': 2.0, 'timestamp': 1234},
        }
        return mockserver.make_response(json=mock_response, status=200)


@pytest.fixture(name='mock_claims_points_eta_404')
def _mock_points_eta_404(mockserver):
    @mockserver.json_handler(
        '/b2b-taxi/b2b/cargo/integration/v1/claims/points-eta',
    )
    def _handler_b2b_location(request):
        return mockserver.make_response(status=404)


@pytest.fixture(name='mock_claims_performer_position_404')
def _mock_performer_position_404(mockserver):
    @mockserver.json_handler(
        '/b2b-taxi/b2b/cargo/integration/v1/claims/performer-position',
    )
    def _handler_b2b_location(request):
        return mockserver.make_response(status=404)


@pytest.fixture(name='mock_eda_candidates_list')
def _mock_eda_candidates_list(mockserver, load_json):
    @mockserver.json_handler('/eda-candidates/list-by-ids')
    def _handler_b2b_location(request):
        mock_response = {'candidates': [{'position': [4.0, 3.0]}]}
        return mockserver.make_response(json=mock_response, status=200)


@pytest.fixture(name='mock_eda_candidates_list_404')
def _mock_eda_candidates_list_404(mockserver):
    @mockserver.json_handler('/eda-candidates/list-by-ids')
    def _handler_b2b_location(request):
        return mockserver.make_response(status=404)


@pytest.mark.experiments3(
    is_config=True,
    name='eats_orders_tracking_order_dynamic_settings',
    consumers=['eats-orders-tracking/order-dynamic-settings'],
    default_value={
        'db_cache_ttl_seconds': 10,
        'is_db_cache_saving_enabled': True,
        'is_endpoint_claims_points_eta_enabled': True,
        'is_endpoint_claims_performer_position_enabled': True,
        'is_endpoint_eda_candidates_list_enabled': True,
        'endpoint_eats_eta_orders_estimate_using_strategy': 'use_to_show',
    },
)
@pytest.mark.now(MOCK_DATETIME)
@pytest.mark.pgsql(
    'eats_orders_tracking',
    files=['fill_tracked_order_payload.sql', 'fill_courier_with_claim.sql'],
    queries=[
        """INSERT INTO eats_orders_tracking.orders_dynamic_data
        (order_nr, payload, created_at, updated_at)
        VALUES (
            '000000-000000',
            $${
                "estimates": {
                    "courier_arriving_to_client": {
                        "expected_at": "2020-10-28T18:25:00.00+00:00",
                        "calculation_source": "some_source"
                    }
                },
                "courier_position": {
                    "latitude": 11.11,
                    "longitude": 12.12
                }
            }$$,
            '2020-10-28T18:19:59.00+00:00',
            '2020-10-28T18:19:59.00+00:00'
        )""",
    ],
)
@pytest.mark.experiments3(filename='exp3_display_matching.json')
async def test_fresh_cached_data(
        taxi_eats_orders_tracking, make_tracking_headers, mock_eats_personal,
):
    response = await taxi_eats_orders_tracking.get(
        path=TRACKING_URL, headers=make_tracking_headers(eater_id='eater1'),
    )

    order = response.json()['payload']['trackedOrders'][0]
    assert response.status_code == 200
    assert order['courier']['location']['latitude'] == 11.11
    assert order['courier']['location']['longitude'] == 12.12
    assert order['eta'] == 5


@pytest.mark.experiments3(
    is_config=True,
    name='eats_orders_tracking_order_dynamic_settings',
    consumers=['eats-orders-tracking/order-dynamic-settings'],
    default_value={
        'db_cache_ttl_seconds': 10,
        'is_db_cache_saving_enabled': True,
        'is_endpoint_claims_points_eta_enabled': False,
        'is_endpoint_claims_performer_position_enabled': False,
        'is_endpoint_eda_candidates_list_enabled': False,
        'endpoint_eats_eta_orders_estimate_using_strategy': 'disabled',
    },
)
@pytest.mark.now(MOCK_DATETIME)
@pytest.mark.pgsql(
    'eats_orders_tracking',
    files=['fill_tracked_order_payload.sql', 'fill_courier_with_claim.sql'],
)
@pytest.mark.experiments3(filename='exp3_display_matching.json')
async def test_no_db_data_all_disabled(
        taxi_eats_orders_tracking, make_tracking_headers, mock_eats_personal,
):
    response = await taxi_eats_orders_tracking.get(
        path=TRACKING_URL, headers=make_tracking_headers(eater_id='eater1'),
    )

    order = response.json()['payload']['trackedOrders'][0]
    assert response.status_code == 200
    assert order['courier']['location']['latitude'] == 59.999102
    assert order['courier']['location']['longitude'] == 30.220117
    assert order['eta'] == 10


@pytest.mark.experiments3(
    is_config=True,
    name='eats_orders_tracking_order_dynamic_settings',
    consumers=['eats-orders-tracking/order-dynamic-settings'],
    default_value={
        'db_cache_ttl_seconds': 10,
        'is_db_cache_saving_enabled': True,
        'is_endpoint_claims_points_eta_enabled': True,
        'is_endpoint_claims_performer_position_enabled': True,
        'is_endpoint_eda_candidates_list_enabled': False,
        'endpoint_eats_eta_orders_estimate_using_strategy': 'disabled',
    },
)
@pytest.mark.now(MOCK_DATETIME)
@pytest.mark.pgsql(
    'eats_orders_tracking',
    files=['fill_tracked_order_payload.sql', 'fill_courier_with_claim.sql'],
)
@pytest.mark.experiments3(filename='exp3_display_matching.json')
async def test_claims_enabled(
        taxi_eats_orders_tracking,
        make_tracking_headers,
        mock_claims_points_eta,
        mock_claims_performer_position,
        mock_eats_personal,
):
    response = await taxi_eats_orders_tracking.get(
        path=TRACKING_URL, headers=make_tracking_headers(eater_id='eater1'),
    )

    order = response.json()['payload']['trackedOrders'][0]
    assert response.status_code == 200
    assert order['courier']['location']['latitude'] == 55.4
    assert order['courier']['location']['longitude'] == 37.8
    assert order['eta'] == 8


@pytest.mark.experiments3(
    is_config=True,
    name='eats_orders_tracking_order_dynamic_settings',
    consumers=['eats-orders-tracking/order-dynamic-settings'],
    default_value={
        'db_cache_ttl_seconds': 0,
        'is_db_cache_saving_enabled': True,
        'is_endpoint_claims_points_eta_enabled': True,
        'is_endpoint_claims_performer_position_enabled': True,
        'is_endpoint_eda_candidates_list_enabled': True,
        'endpoint_eats_eta_orders_estimate_using_strategy': 'disabled',
    },
)
@pytest.mark.now(MOCK_DATETIME)
@pytest.mark.pgsql(
    'eats_orders_tracking',
    files=['fill_tracked_order_payload.sql', 'fill_courier_without_claim.sql'],
)
@pytest.mark.experiments3(filename='exp3_display_matching.json')
async def test_eda_candidates_enabled(
        taxi_eats_orders_tracking,
        make_tracking_headers,
        mock_eda_candidates_list,
        mock_eats_personal,
):
    response = await taxi_eats_orders_tracking.get(
        path=TRACKING_URL, headers=make_tracking_headers(eater_id='eater1'),
    )

    order = response.json()['payload']['trackedOrders'][0]
    assert response.status_code == 200
    assert order['courier']['location']['latitude'] == 3.0
    assert order['courier']['location']['longitude'] == 4.0
    assert order['eta'] == 10


@pytest.mark.experiments3(
    is_config=True,
    name='eats_orders_tracking_order_dynamic_settings',
    consumers=['eats-orders-tracking/order-dynamic-settings'],
    default_value={
        'db_cache_ttl_seconds': 10,
        'is_db_cache_saving_enabled': True,
        'is_endpoint_claims_points_eta_enabled': True,
        'is_endpoint_claims_performer_position_enabled': False,
        'is_endpoint_eda_candidates_list_enabled': False,
        'endpoint_eats_eta_orders_estimate_using_strategy': 'disabled',
    },
)
@pytest.mark.now(MOCK_DATETIME)
@pytest.mark.pgsql(
    'eats_orders_tracking',
    files=['fill_tracked_order_payload.sql', 'fill_courier_with_claim.sql'],
)
@pytest.mark.experiments3(filename='exp3_display_matching.json')
async def test_enabled_only_claims_points_eta(
        taxi_eats_orders_tracking,
        make_tracking_headers,
        mock_claims_points_eta,
        mock_eats_personal,
):
    response = await taxi_eats_orders_tracking.get(
        path=TRACKING_URL, headers=make_tracking_headers(eater_id='eater1'),
    )

    order = response.json()['payload']['trackedOrders'][0]
    assert response.status_code == 200
    assert order['courier']['location']['longitude'] == 37.8
    assert order['courier']['location']['latitude'] == 55.4
    assert order['eta'] == 8


@pytest.mark.experiments3(
    is_config=True,
    name='eats_orders_tracking_order_dynamic_settings',
    consumers=['eats-orders-tracking/order-dynamic-settings'],
    default_value={
        'db_cache_ttl_seconds': 10,
        'is_db_cache_saving_enabled': True,
        'is_endpoint_claims_points_eta_enabled': True,
        'is_endpoint_claims_performer_position_enabled': False,
        'is_endpoint_eda_candidates_list_enabled': False,
        'endpoint_eats_eta_orders_estimate_using_strategy': (
            'request_without_using'
        ),
    },
)
@pytest.mark.now(MOCK_DATETIME)
@pytest.mark.pgsql(
    'eats_orders_tracking',
    files=['fill_tracked_order_payload.sql', 'fill_courier_with_claim.sql'],
)
@pytest.mark.experiments3(filename='exp3_display_matching.json')
async def test_eats_eta_enabled_without_using(
        taxi_eats_orders_tracking,
        make_tracking_headers,
        mock_claims_points_eta,
        mock_eats_eta_orders_estimate,
        mock_eats_personal,
):
    response = await taxi_eats_orders_tracking.get(
        path=TRACKING_URL, headers=make_tracking_headers(eater_id='eater1'),
    )

    order = response.json()['payload']['trackedOrders'][0]
    assert response.status_code == 200
    assert order['courier']['location']['longitude'] == 37.8
    assert order['courier']['location']['latitude'] == 55.4
    assert order['eta'] == 8


@pytest.mark.experiments3(
    is_config=True,
    name='eats_orders_tracking_order_dynamic_settings',
    consumers=['eats-orders-tracking/order-dynamic-settings'],
    default_value={
        'db_cache_ttl_seconds': 0,
        'is_db_cache_saving_enabled': True,
        'is_endpoint_claims_points_eta_enabled': False,
        'is_endpoint_claims_performer_position_enabled': True,
        'is_endpoint_eda_candidates_list_enabled': False,
        'endpoint_eats_eta_orders_estimate_using_strategy': 'disabled',
    },
)
@pytest.mark.now(MOCK_DATETIME)
@pytest.mark.pgsql(
    'eats_orders_tracking',
    files=['fill_tracked_order_payload.sql', 'fill_courier_with_claim.sql'],
)
@pytest.mark.experiments3(filename='exp3_display_matching.json')
async def test_enabled_only_claims_performer_position(
        taxi_eats_orders_tracking,
        make_tracking_headers,
        mock_claims_performer_position,
        mock_eats_personal,
):
    response = await taxi_eats_orders_tracking.get(
        path=TRACKING_URL, headers=make_tracking_headers(eater_id='eater1'),
    )

    order = response.json()['payload']['trackedOrders'][0]
    assert response.status_code == 200
    assert order['courier']['location']['latitude'] == 1.0
    assert order['courier']['location']['longitude'] == 2.0
    assert order['eta'] == 10


@pytest.mark.experiments3(
    is_config=True,
    name='eats_orders_tracking_order_dynamic_settings',
    consumers=['eats-orders-tracking/order-dynamic-settings'],
    default_value={
        'db_cache_ttl_seconds': 10,
        'is_db_cache_saving_enabled': True,
        'is_endpoint_claims_points_eta_enabled': False,
        'is_endpoint_claims_performer_position_enabled': False,
        'is_endpoint_eda_candidates_list_enabled': False,
        'endpoint_eats_eta_orders_estimate_using_strategy': 'disabled',
    },
)
@pytest.mark.now(MOCK_DATETIME)
@pytest.mark.pgsql(
    'eats_orders_tracking',
    files=['fill_tracked_order_payload.sql', 'fill_courier_with_claim.sql'],
    queries=[
        """INSERT INTO eats_orders_tracking.orders_dynamic_data
        (order_nr, payload, created_at, updated_at)
        VALUES (
            '000000-000000',
            $${
                "estimates": {
                    "courier_arriving_to_client": {
                        "expected_at": "2020-10-28T18:25:00.00+00:00",
                        "calculation_source": "some_source"
                    }
                },
                "courier_position": {
                    "latitude": 11.11,
                    "longitude": 12.12
                }
            }$$,
            '2020-10-28T18:10:00.00+00:00',
            '2020-10-28T18:10:00.00+00:00'
        )""",
    ],
)
@pytest.mark.experiments3(filename='exp3_display_matching.json')
# fallback to outdated order dynamic data cache
async def test_cached_outdated_data_all_disabled_building_via_cache(
        taxi_eats_orders_tracking,
        make_tracking_headers,
        pgsql,
        mock_eats_personal,
):
    response = await taxi_eats_orders_tracking.get(
        path=TRACKING_URL, headers=make_tracking_headers(eater_id='eater1'),
    )

    order = response.json()['payload']['trackedOrders'][0]
    assert response.status_code == 200
    assert order['courier']['location']['latitude'] == 11.11
    assert order['courier']['location']['longitude'] == 12.12
    assert order['eta'] == 5

    cursor = pgsql['eats_orders_tracking'].cursor()
    cursor.execute(
        """SELECT updated_at
        FROM eats_orders_tracking.orders_dynamic_data
        where order_nr = '000000-000000';""",
    )
    courier_dynamic = cursor.fetchone()
    # check that outdated data not rewritten
    assert courier_dynamic[0] == datetime.datetime.fromisoformat(
        '2020-10-28T18:10:00+00:00',
    )


@pytest.mark.experiments3(
    is_config=True,
    name='eats_orders_tracking_order_dynamic_settings',
    consumers=['eats-orders-tracking/order-dynamic-settings'],
    default_value={
        'db_cache_ttl_seconds': 10,
        'is_db_cache_saving_enabled': True,
        'is_endpoint_claims_points_eta_enabled': False,
        'is_endpoint_claims_performer_position_enabled': False,
        'is_endpoint_eda_candidates_list_enabled': False,
        'endpoint_eats_eta_orders_estimate_using_strategy': 'disabled',
    },
)
@pytest.mark.now(MOCK_DATETIME)
@pytest.mark.pgsql(
    'eats_orders_tracking',
    files=['fill_tracked_order_payload.sql', 'fill_courier_with_claim.sql'],
)
@pytest.mark.experiments3(filename='exp3_display_matching.json')
# fallback to place location
async def test_no_cache_data_all_disabled_building_via_place(
        taxi_eats_orders_tracking,
        make_tracking_headers,
        pgsql,
        mock_eats_personal,
):
    response = await taxi_eats_orders_tracking.get(
        path=TRACKING_URL, headers=make_tracking_headers(eater_id='eater1'),
    )

    order = response.json()['payload']['trackedOrders'][0]
    assert response.status_code == 200
    assert order['courier']['location']['latitude'] == 59.999102
    assert order['courier']['location']['longitude'] == 30.220117
    assert order['eta'] == 10  # ETA is building from promise

    cursor = pgsql['eats_orders_tracking'].cursor()
    cursor.execute(
        f"""SELECT order_nr
        FROM eats_orders_tracking.orders_dynamic_data
        where order_nr = '000000-000000';""",
    )

    order_dynamic = cursor.fetchone()
    assert order_dynamic is None


@pytest.mark.experiments3(
    is_config=True,
    name='eats_orders_tracking_order_dynamic_settings',
    consumers=['eats-orders-tracking/order-dynamic-settings'],
    default_value={
        'db_cache_ttl_seconds': 10,
        'is_db_cache_saving_enabled': True,
        'is_endpoint_claims_points_eta_enabled': True,
        'is_endpoint_claims_performer_position_enabled': True,
        'is_endpoint_eda_candidates_list_enabled': True,
        'endpoint_eats_eta_orders_estimate_using_strategy': 'use_to_show',
    },
)
@pytest.mark.now(MOCK_DATETIME)
@pytest.mark.pgsql(
    'eats_orders_tracking',
    files=['fill_tracked_order_payload.sql', 'fill_courier_with_claim.sql'],
    queries=[
        """INSERT INTO eats_orders_tracking.orders_dynamic_data
        (order_nr, payload, created_at, updated_at)
        VALUES (
            '000000-000000',
            $${
                "estimates": {
                    "courier_arriving_to_client": {
                        "expected_at": "2020-10-28T18:25:00.00+00:00",
                        "calculation_source": "some_source"
                    }
                },
                "courier_position": {
                    "latitude": 11.11,
                    "longitude": 12.12
                }
            }$$,
            '2020-10-28T18:10:00.00+00:00',
            '2020-10-28T18:10:00.00+00:00'
        )""",
    ],
)
@pytest.mark.experiments3(filename='exp3_display_matching.json')
@pytest.mark.experiments3(
    is_config=True,
    name='eats_orders_tracking_eats_eta_settings',
    consumers=['eats-orders-tracking/eats-eta-settings'],
    default_value={'enabled': True},
)
async def test_not_fresh_data_all_enabled(
        taxi_eats_orders_tracking,
        make_tracking_headers,
        pgsql,
        mock_claims_performer_position,
        mock_claims_points_eta,
        mock_eats_personal,
        mock_eats_eta_orders_estimate,
        testpoint,
):
    @testpoint('update_order_dynamic_data_detached')
    def detached_coro_task(data):
        return data

    response = await taxi_eats_orders_tracking.get(
        path=TRACKING_URL, headers=make_tracking_headers(eater_id='eater1'),
    )

    await detached_coro_task.wait_call()

    order = response.json()['payload']['trackedOrders'][0]
    assert response.status_code == 200
    assert order['courier']['location']['latitude'] == 55.4
    assert order['courier']['location']['longitude'] == 37.8
    assert order['eta'] == 12  # ETA is building from eats-eta

    cursor = pgsql['eats_orders_tracking'].cursor()
    cursor.execute(
        """SELECT payload
        FROM eats_orders_tracking.orders_dynamic_data
        where order_nr = '000000-000000';""",
    )

    courier_dynamic = cursor.fetchone()
    assert courier_dynamic[0] == {
        'estimates': {
            'courier_arriving_to_client': {
                'expected_at': '2020-10-28T18:32:00+00:00',
                'calculation_source': 'eats_eta',
            },
            'courier_arriving_to_place': {'status': 'in_progress'},
        },
        'courier_position': {'latitude': 55.4, 'longitude': 37.8},
    }


@pytest.mark.experiments3(
    is_config=True,
    name='eats_orders_tracking_order_dynamic_settings',
    consumers=['eats-orders-tracking/order-dynamic-settings'],
    default_value={
        'db_cache_ttl_seconds': 10,
        'is_db_cache_saving_enabled': False,
        'is_endpoint_claims_points_eta_enabled': True,
        'is_endpoint_claims_performer_position_enabled': True,
        'is_endpoint_eda_candidates_list_enabled': True,
        'endpoint_eats_eta_orders_estimate_using_strategy': 'use_to_show',
    },
)
@pytest.mark.now(MOCK_DATETIME)
@pytest.mark.pgsql(
    'eats_orders_tracking',
    files=['fill_tracked_order_payload.sql', 'fill_courier_with_claim.sql'],
    queries=[
        """INSERT INTO eats_orders_tracking.orders_dynamic_data
        (order_nr, payload, created_at, updated_at)
        VALUES (
            '000000-000000',
            $${
                "estimates": {
                    "courier_arriving_to_client": {
                        "expected_at": "2020-10-28T18:25:00.00+00:00",
                        "calculation_source": "some_source"
                    }
                },
                "courier_position": {
                    "latitude": 11.11,
                    "longitude": 12.12
                }
            }$$,
            '2020-10-28T18:10:00.00+00:00',
            '2020-10-28T18:10:00.00+00:00'
        )""",
    ],
)
@pytest.mark.experiments3(filename='exp3_display_matching.json')
@pytest.mark.experiments3(
    is_config=True,
    name='eats_orders_tracking_eats_eta_settings',
    consumers=['eats-orders-tracking/eats-eta-settings'],
    default_value={'enabled': True},
)
async def test_not_fresh_data_saving_disabled(
        taxi_eats_orders_tracking,
        make_tracking_headers,
        pgsql,
        mock_claims_performer_position,
        mock_claims_points_eta,
        mock_eats_personal,
        mock_eats_eta_orders_estimate,
        testpoint,
):
    response = await taxi_eats_orders_tracking.get(
        path=TRACKING_URL, headers=make_tracking_headers(eater_id='eater1'),
    )

    order = response.json()['payload']['trackedOrders'][0]
    assert response.status_code == 200
    assert order['courier']['location']['latitude'] == 55.4
    assert order['courier']['location']['longitude'] == 37.8
    assert order['eta'] == 12  # ETA is building from eats-eta

    cursor = pgsql['eats_orders_tracking'].cursor()
    cursor.execute(
        """SELECT payload
        FROM eats_orders_tracking.orders_dynamic_data
        where order_nr = '000000-000000';""",
    )

    courier_dynamic = cursor.fetchone()
    assert courier_dynamic[0] == {
        'estimates': {
            'courier_arriving_to_client': {
                'expected_at': '2020-10-28T18:25:00.00+00:00',
                'calculation_source': 'some_source',
            },
        },
        'courier_position': {'latitude': 11.11, 'longitude': 12.12},
    }


@pytest.mark.experiments3(
    is_config=True,
    name='eats_orders_tracking_order_dynamic_settings',
    consumers=['eats-orders-tracking/order-dynamic-settings'],
    default_value={
        'db_cache_ttl_seconds': 10,
        'is_db_cache_saving_enabled': True,
        'is_endpoint_claims_points_eta_enabled': True,
        'is_endpoint_claims_performer_position_enabled': True,
        'is_endpoint_eda_candidates_list_enabled': False,
        'endpoint_eats_eta_orders_estimate_using_strategy': 'disabled',
    },
)
@pytest.mark.now(MOCK_DATETIME)
@pytest.mark.pgsql(
    'eats_orders_tracking',
    files=['fill_tracked_order_payload.sql', 'fill_courier_with_claim.sql'],
)
@pytest.mark.experiments3(filename='exp3_display_matching.json')
async def test_claims_enabled_but_not_found(
        taxi_eats_orders_tracking,
        make_tracking_headers,
        mock_claims_points_eta_404,
        mock_claims_performer_position_404,
        mock_eats_personal,
):
    response = await taxi_eats_orders_tracking.get(
        path=TRACKING_URL, headers=make_tracking_headers(eater_id='eater1'),
    )

    order = response.json()['payload']['trackedOrders'][0]
    assert response.status_code == 200
    assert order['courier']['location']['latitude'] == 59.999102
    assert order['courier']['location']['longitude'] == 30.220117
    assert order['eta'] == 10


@pytest.mark.experiments3(
    is_config=True,
    name='eats_orders_tracking_order_dynamic_settings',
    consumers=['eats-orders-tracking/order-dynamic-settings'],
    default_value={
        'db_cache_ttl_seconds': 0,
        'is_db_cache_saving_enabled': True,
        'is_endpoint_claims_points_eta_enabled': True,
        'is_endpoint_claims_performer_position_enabled': True,
        'is_endpoint_eda_candidates_list_enabled': True,
        'endpoint_eats_eta_orders_estimate_using_strategy': 'disabled',
    },
)
@pytest.mark.now(MOCK_DATETIME)
@pytest.mark.pgsql(
    'eats_orders_tracking',
    files=['fill_tracked_order_payload.sql', 'fill_courier_without_claim.sql'],
)
@pytest.mark.experiments3(filename='exp3_display_matching.json')
async def test_eda_candidates_enabled_but_not_found(
        taxi_eats_orders_tracking,
        make_tracking_headers,
        mock_eda_candidates_list_404,
        mock_eats_personal,
):
    response = await taxi_eats_orders_tracking.get(
        path=TRACKING_URL, headers=make_tracking_headers(eater_id='eater1'),
    )

    order = response.json()['payload']['trackedOrders'][0]
    assert response.status_code == 200
    assert order['courier']['location']['latitude'] == 59.999102
    assert order['courier']['location']['longitude'] == 30.220117
    assert order['eta'] == 10


@pytest.mark.experiments3(
    is_config=True,
    name='eats_orders_tracking_order_dynamic_settings',
    consumers=['eats-orders-tracking/order-dynamic-settings'],
    default_value={
        'db_cache_ttl_seconds': 0,
        'is_db_cache_saving_enabled': True,
        'is_endpoint_claims_points_eta_enabled': True,
        'is_endpoint_claims_performer_position_enabled': True,
        'is_endpoint_eda_candidates_list_enabled': False,
        'endpoint_eats_eta_orders_estimate_using_strategy': 'disabled',
    },
)
@pytest.mark.now(MOCK_DATETIME)
@pytest.mark.pgsql(
    'eats_orders_tracking',
    files=[
        'fill_tracked_order_payload_ready_for_delivery.sql',
        'fill_courier_with_claim.sql',
    ],
)
@pytest.mark.experiments3(filename='exp3_display_matching.json')
async def test_courier_arrived_to_place(
        taxi_eats_orders_tracking,
        make_tracking_headers,
        mock_claims_points_eta_arrived_to_place,
        mock_claims_performer_position,
        mock_eats_personal,
):
    response = await taxi_eats_orders_tracking.get(
        path=TRACKING_URL, headers=make_tracking_headers(eater_id='eater1'),
    )

    order = response.json()['payload']['trackedOrders'][0]
    assert response.status_code == 200
    # courier location must be same with place's even if got another from cargo
    assert order['courier']['location']['latitude'] == 59.999102
    assert order['courier']['location']['longitude'] == 30.220117


@pytest.mark.experiments3(
    is_config=True,
    name='eats_orders_tracking_order_dynamic_settings',
    consumers=['eats-orders-tracking/order-dynamic-settings'],
    default_value={
        'db_cache_ttl_seconds': 0,
        'is_db_cache_saving_enabled': True,
        'is_endpoint_claims_points_eta_enabled': True,
        'is_endpoint_claims_performer_position_enabled': True,
        'is_endpoint_eda_candidates_list_enabled': False,
        'endpoint_eats_eta_orders_estimate_using_strategy': 'disabled',
    },
)
@pytest.mark.now(MOCK_DATETIME)
@pytest.mark.pgsql(
    'eats_orders_tracking',
    files=['fill_tracked_order_payload.sql', 'fill_courier_with_claim.sql'],
)
@pytest.mark.experiments3(filename='exp3_display_matching.json')
async def test_courier_arrived_to_place_order_taken(
        taxi_eats_orders_tracking,
        make_tracking_headers,
        mock_claims_points_eta_arrived_to_place,
        mock_claims_performer_position,
        mock_eats_personal,
):
    response = await taxi_eats_orders_tracking.get(
        path=TRACKING_URL, headers=make_tracking_headers(eater_id='eater1'),
    )

    order = response.json()['payload']['trackedOrders'][0]
    assert response.status_code == 200
    # courier location must be actual for already taken order
    # even if source point has status "arrived"
    assert order['courier']['location']['longitude'] == 37.8
    assert order['courier']['location']['latitude'] == 55.4
