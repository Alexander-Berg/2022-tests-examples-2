# flake8: noqa
# pylint: disable=import-error,wildcard-import,too-many-lines
import datetime
import pytest


STATIC_COURIER_ON_ORDERS = 6
STATIC_COURIER_POSITIONS = 32
STATIC_COURIER_ANALYZES = 1

DETECTORS_CONFIG = {
    'courier': {
        'events_settings': [
            {'enabled': True, 'delay_sec': 0, 'order_event': 'created'},
        ],
    },
}

MAP_CARGO_ALIAS_TO_CLIENT_ID = {
    'claim_alias_123': {'client_id': 'corp_client_id_123'},
}

DETECTOR_EXPERIMENT_ENABLED = pytest.mark.experiments3(
    name='eats_proactive_support_courier_detector',
    consumers=['eats_proactive_support/courier_detector'],
    is_config=True,
    default_value={'enabled': True, 'config': {'reschedule_delay_sec': 10}},
    clauses=[],
)

AUTOSTATUS_FILTER_EXPERIMENT_ENABLED = pytest.mark.experiments3(
    name='eats_proactive_support_courier_autostatus_filter',
    consumers=['eats_proactive_support/courier_autostatus_filter'],
    is_config=True,
    default_value={'enabled': True, 'config': {'stq_delay_sec': 17}},
    clauses=[],
)

CATALOG_STORAGE_RESPONSE = {
    'places': [
        {
            'place_id': 40,
            'created_at': '2021-01-01T09:00:00+06:00',
            'updated_at': '2021-01-01T09:00:00+06:00',
            'place': {
                'slug': 'some_slug',
                'enabled': True,
                'name': 'some_name',
                'revision': 1,
                'type': 'native',
                'business': 'restaurant',
                'launched_at': '2021-01-01T09:00:00+06:00',
                'payment_methods': ['cash', 'payture', 'taxi'],
                'gallery': [{'type': 'image', 'url': 'some_url', 'weight': 1}],
                'brand': {
                    'id': 100,
                    'slug': 'some_slug',
                    'name': 'some_brand',
                    'picture_scale_type': 'aspect_fit',
                },
                'address': {'city': 'Moscow', 'short': 'some_address'},
                'country': {
                    'id': 1,
                    'name': 'Russia',
                    'code': 'RU',
                    'currency': {'sign': 'RUB', 'code': 'RUB'},
                },
                'categories': [{'id': 1, 'name': 'some_name'}],
                'quick_filters': {
                    'general': [{'id': 1, 'slug': 'some_slug'}],
                    'wizard': [{'id': 1, 'slug': 'some_slug'}],
                },
                'region': {'id': 1, 'geobase_ids': [1], 'time_zone': 'UTC'},
                'location': {'geo_point': [30.1, 50.1]},
                'rating': {'users': 5.0, 'admin': 5.0, 'count': 1},
                'price_category': {'id': 1, 'name': 'some_name', 'value': 5.0},
                'extra_info': {},
                'features': {
                    'ignore_surge': False,
                    'supports_preordering': False,
                    'fast_food': False,
                },
                'timing': {
                    'preparation': 60.0,
                    'extra_preparation': 60.0,
                    'average_preparation': 60.0,
                },
                'sorting': {'weight': 5, 'popular': 5},
                'assembly_cost': 1,
            },
        },
    ],
}


@pytest.fixture(name='exp_courier_autostatus')
async def _exp_courier_autostatus(taxi_eats_proactive_support, experiments3):
    async def wrapper(
            *,
            minimal_period_near_point_sec=180,
            slow_polling_interval_sec=None,
            high_courier_speed=None,
            min_good_pos_at_high_speed=None,
            no_gps_anomaly_distance_meters=None,
            very_far_from_point_distance=None,
            max_speed_very_far=None,
    ):
        config = {
            'courier_info_polling_interval_sec': 10,
            'mode': 'change_status',
            'admin_ticket': 'ticket_1',
            'admin_comment': 'comment',
            'minimal_number_of_good_gps_positions': 5,
            'maximal_gps_time_in_advance_sec': 5,
            'minimal_time_delta_of_good_gps_positions_sec': 5,
            'maximal_time_delta_of_good_gps_positions_sec': 20,
            'far_from_point_distance_meters': 150.0,
            'near_point_distance_meters': 50.0,
            'minimal_period_near_point_sec': minimal_period_near_point_sec,
            'maximal_courier_speed_meters_per_sec': 6.0,
        }

        if slow_polling_interval_sec is not None:
            config[
                'courier_info_slow_polling_interval_sec'
            ] = slow_polling_interval_sec

        if high_courier_speed is not None:
            config['high_courier_speed_meters_per_sec'] = high_courier_speed

        if min_good_pos_at_high_speed is not None:
            config[
                'minimal_number_of_good_gps_positions_at_high_speed'
            ] = min_good_pos_at_high_speed

        if no_gps_anomaly_distance_meters is not None:
            config[
                'no_gps_anomaly_distance_meters'
            ] = no_gps_anomaly_distance_meters

        if very_far_from_point_distance is not None:
            config[
                'very_far_from_point_distance_meters'
            ] = very_far_from_point_distance

        if max_speed_very_far is not None:
            config[
                'maximal_courier_speed_very_far_meters_per_sec'
            ] = max_speed_very_far

        experiments3.add_config(
            match={'predicate': {'type': 'true'}, 'enabled': True},
            name='eats_proactive_support_courier_autostatus',
            consumers=['eats_proactive_support/courier_autostatus'],
            clauses=[],
            default_value={'enabled': True, 'config': config},
        )
        await taxi_eats_proactive_support.invalidate_caches()

    await wrapper()
    return wrapper


def assert_db_expected_count(psql, expected_count, table_name):
    cursor = psql.cursor()
    cursor.execute('SELECT * FROM eats_proactive_support.' + table_name + ';')
    records = cursor.fetchall()
    assert len(records) == expected_count


def assert_db_problems(psql, expected_count):
    assert_db_expected_count(psql, expected_count, 'problems')


def assert_db_actions(psql, expected_count):
    assert_db_expected_count(psql, expected_count, 'actions')


def assert_db_courier_on_orders(psql, expected_count):
    assert_db_expected_count(psql, expected_count, 'courier_on_orders')


def assert_db_courier_positions(psql, expected_count):
    assert_db_expected_count(psql, expected_count, 'courier_positions')


def assert_db_courier_analyzes(psql, expected_count):
    assert_db_expected_count(psql, expected_count, 'courier_analyzes')


@pytest.fixture(name='mock_eats_orders_tracking')
def _mock_eats_orders_tracking(mockserver):
    @mockserver.json_handler(
        '/eats-orders-tracking/internal/'
        'eats-orders-tracking/v1/get-claim-by-order-nr',
    )
    def mock(request):
        return mockserver.make_response(
            status=200,
            json={
                'order_nr': '123',
                'claim_id': 'claim_id_123',
                'claim_alias': 'claim_alias_123',
            },
        )

    return mock


@pytest.fixture(name='mock_cargo_claims_external_performer')
def _mock_cargo_claims_external_performer(mockserver):
    @mockserver.json_handler('/cargo-claims/internal/external-performer')
    def mock(request):
        return mockserver.make_response(
            status=200,
            json={
                'car_info': {'model': 'car_model_1', 'number': 'car_number_1'},
                'eats_profile_id': '123',
                'name': 'Kostya',
                'first_name': 'some first name',
                'legal_name': 'park_name_1',
                'driver_id': 'driver_profile_id_1',
                'park_id': 'park_id_1',
                'taxi_alias_id': 'taxi_alias_id_1',
            },
        )

    return mock


@pytest.fixture(name='mock_eats_tags')
def _mock_eats_tags(mockserver):
    @mockserver.json_handler('/eats-tags/v2/match_single')
    def mock(request):
        personal_phone_id = request.json['match'][0]['value']
        if personal_phone_id == 'phone_id_1':
            return mockserver.make_response(
                status=200, json={'tags': ['vip_eater']},
            )

        return mockserver.make_response(
            status=500, json={'code': 'code_500', 'message': 'message_500'},
        )

    return mock


@pytest.fixture(name='mock_eats_catalog_storage')
def _mock_eats_catalog_storage(mockserver):
    @mockserver.json_handler(
        '/eats-catalog-storage/internal/eats-catalog-storage/v1/search/places/list',
    )
    def mock(request):
        place_id = request.json['place_ids'][0]
        if place_id == 40:
            return mockserver.make_response(
                status=200, json=CATALOG_STORAGE_RESPONSE,
            )

        return mockserver.make_response(
            status=500, json={'code': 'code_500', 'message': 'message_500'},
        )

    return mock


@pytest.fixture(name='mock_cargo_claims_full')
def _mock_cargo_claims_full(mockserver):
    @mockserver.json_handler('/cargo-claims/v2/claims/full')
    def mock(request):
        return mockserver.make_response(
            status=200,
            json={
                'created_ts': '2020-01-01T00:00:00+00:00',
                'updated_ts': '2020-01-01T00:00:00+00:00',
                'id': 'claim_id_123',
                'items': [],
                'route_points': [],
                'status': 'pickup_arrived',
                'user_request_revision': '1',
                'version': 1,
                'taxi_order_id': 'taxi_order_id_123',
                'segments': [{'id': 'segment_id_1', 'revision': 1}],
            },
        )

    return mock


def build_claim_info(claim_id, claim_status, current_point_id, lat, lon):
    default_point_id = 1000
    if current_point_id is not None:
        default_point_id = current_point_id

    claim_info = {
        'created_ts': '2020-01-01T00:00:00+00:00',
        'updated_ts': '2020-01-01T00:00:00+00:00',
        'id': claim_id,
        'items': [
            {
                'pickup_point': default_point_id,
                'droppof_point': default_point_id,
                'title': 'title_1',
                'cost_value': '10.0',
                'cost_currency': 'RUB',
                'quantity': 1,
            },
        ],
        'route_points': [
            {
                'id': default_point_id,
                'address': {
                    'fullname': 'fullname_1',
                    'coordinates': [lon, lat],
                },
                'contact': {'phone': 'phone_1', 'name': 'name_1'},
                'type': 'source',
                'visit_order': 1,
                'visit_status': 'pending',
                'visited_at': {},
            },
            {
                'id': default_point_id + 1,
                'address': {
                    'fullname': 'fullname_1',
                    'coordinates': [lon, lat],
                },
                'contact': {'phone': 'phone_1', 'name': 'name_1'},
                'type': 'destination',
                'visit_order': 1,
                'visit_status': 'pending',
                'visited_at': {},
            },
        ],
        'status': claim_status,
        'user_request_revision': '1',
        'version': 1,
        'revision': 1,
        'performer_info': {
            'courier_name': 'courier_name_1',
            'legal_name': 'legal_name_1',
            'transport_type': 'pedestrian',
            'driver_id': 'driver_profile_id_1',
        },
    }

    if current_point_id is not None:
        claim_info['current_point_id'] = current_point_id

    return claim_info


@pytest.fixture(name='mock_cargo_claims_info')
def _mock_cargo_claims_info(mockserver):
    @mockserver.json_handler('/cargo-claims/api/integration/v2/claims/info')
    def mock(request):
        return mockserver.make_response(
            status=200,
            json=build_claim_info(
                'claim_id_123', 'pickup_arrived', 1000, 30.1, 50.1,
            ),
        )

    return mock


@pytest.fixture(name='mock_cargo_claims_bulk_info')
def _mock_cargo_claims_bulk_info(mockserver):
    @mockserver.json_handler(
        '/cargo-claims/api/integration/v2/claims/bulk_info',
    )
    def mock(request):
        return mockserver.make_response(
            status=200,
            json={
                'claims': [
                    build_claim_info(
                        'claim_id_123', 'pickup_arrived', 1000, 30.1, 50.1,
                    ),
                    build_claim_info(
                        'claim_id_125', 'performer_found', None, 30.1, 50.1,
                    ),
                ],
            },
        )

    return mock


@pytest.fixture(name='mock_cargo_dispatch_segment_info')
def _mock_cargo_dispatch_segment_info(mockserver):
    @mockserver.json_handler('/cargo-dispatch/v1/segment/info')
    def mock(request):
        return mockserver.make_response(
            status=200,
            json={
                'segment': {
                    'id': 'segment_id_1',
                    'items': [],
                    'locations': [],
                    'points': [],
                    'performer_requirements': {
                        'taxi_classes': [],
                        'special_requirements': {'virtual_tariffs': []},
                    },
                    'allow_batch': True,
                    'allow_alive_batch_v1': True,
                    'allow_alive_batch_v2': True,
                    'client_info': {'payment_info': {'type': 'type_1'}},
                    'zone_id': 'zone_id_1',
                },
                'dispatch': {
                    'revision': 1,
                    'waybill_building_version': 1,
                    'waybill_building_awaited': False,
                    'waybill_chosen': True,
                    'resolved': False,
                    'status': 'new',
                    'chosen_waybill': {
                        'router_id': 'router_id_1',
                        'external_ref': 'waybill_ref_1',
                    },
                },
                'diagnostics': {
                    'claim_id': 'claim_id_1',
                    'claims_segment_created_ts': '2020-01-01T00:00:00+00:00',
                    'claims_segment_revision': 1,
                    'created_ts': '2020-01-01T00:00:00+00:00',
                    'current_revision_ts': '2020-01-01T00:00:00+00:00',
                },
            },
        )

    return mock


@pytest.fixture(name='mock_cargo_claims_performer_position')
def _mock_cargo_claims_performer_position(mockserver):
    @mockserver.json_handler(
        '/cargo-claims/api/integration/v1/claims/performer-position',
    )
    def mock(request):
        return mockserver.make_response(
            status=200,
            json={'position': {'lat': 30.1018, 'lon': 50.1, 'timestamp': 210}},
        )

    return mock


@pytest.fixture(name='mock_cargo_dispatch_exchange_confirm')
def _mock_cargo_dispatch_exchange_confirm(mockserver):
    @mockserver.json_handler('cargo-dispatch/v1/waybill/exchange/confirm')
    def mock(request):
        return mockserver.make_response(
            status=200,
            json={
                'result': 'abc',
                'new_status': 'new_status_1',
                'new_route': [],
                'waybill_info': {
                    'waybill': {
                        'router_id': 'router_id_1',
                        'external_ref': 'waybill_ref_1',
                        'points': [],
                        'taxi_order_requirements': {},
                        'special_requirements': {'virtual_tariffs': []},
                        'optional_return': True,
                        'items': [],
                    },
                    'dispatch': {
                        'revision': 1,
                        'created_ts': '2020-01-01T00:00:00+00:00',
                        'updated_ts': '2020-01-01T00:00:00+00:00',
                        'is_waybill_accepted': True,
                        'is_waybill_declined': False,
                        'is_performer_assigned': True,
                        'status': 'processing',
                    },
                    'execution': {
                        'points': [],
                        'paper_flow': False,
                        'segments': [],
                    },
                    'diagnostics': {
                        'order_id': 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa',
                    },
                    'segments': [],
                },
            },
        )

    return mock


@pytest.mark.config(EATS_PROACTIVE_SUPPORT_DETECTORS_SETTINGS=DETECTORS_CONFIG)
@pytest.mark.pgsql('eats_proactive_support', files=['fill_orders.sql'])
@pytest.mark.parametrize(
    """order_nr""",
    [
        pytest.param('123', marks=[], id='disabled_config'),
        pytest.param(
            '124', marks=[DETECTOR_EXPERIMENT_ENABLED], id='finished_order',
        ),
    ],
)
async def test_no_action(
        pgsql,
        stq_runner,
        stq,
        mock_eats_orders_tracking,
        mock_cargo_claims_external_performer,
        mock_eats_catalog_storage,
        mock_eats_tags,
        order_nr,
):
    await stq_runner.eats_proactive_support_detections.call(
        task_id='123',
        kwargs={
            'order_nr': order_nr,
            'event_name': 'created',
            'detector_name': 'courier',
        },
    )

    assert_db_problems(pgsql['eats_proactive_support'], 0)
    assert_db_actions(pgsql['eats_proactive_support'], 0)

    assert mock_eats_orders_tracking.times_called == 0
    assert mock_cargo_claims_external_performer.times_called == 0
    assert mock_eats_catalog_storage.times_called == 0
    assert mock_eats_tags.times_called == 0
    assert stq.eats_proactive_support_actions.times_called == 0
    assert stq.eats_proactive_support_detections.times_called == 0
    assert stq.eats_proactive_support_couriers.times_called == 0


@pytest.mark.config(EATS_PROACTIVE_SUPPORT_DETECTORS_SETTINGS=DETECTORS_CONFIG)
@pytest.mark.config(
    EATS_MAP_CARGO_ALIAS_TO_CLIENT_ID=MAP_CARGO_ALIAS_TO_CLIENT_ID,
)
@pytest.mark.pgsql('eats_proactive_support', files=['fill_orders.sql'])
@DETECTOR_EXPERIMENT_ENABLED
async def test_courier_disabled(
        pgsql,
        stq_runner,
        stq,
        mock_eats_orders_tracking,
        mock_cargo_claims_external_performer,
        mock_eats_catalog_storage,
        mock_eats_tags,
        order_nr='123',
):
    await stq_runner.eats_proactive_support_detections.call(
        task_id='123',
        kwargs={
            'order_nr': order_nr,
            'event_name': 'created',
            'detector_name': 'courier',
        },
    )

    assert_db_problems(pgsql['eats_proactive_support'], 0)
    assert_db_actions(pgsql['eats_proactive_support'], 0)
    assert_db_courier_on_orders(pgsql['eats_proactive_support'], 0)

    assert mock_eats_orders_tracking.times_called == 1
    assert mock_cargo_claims_external_performer.times_called == 1
    assert mock_eats_catalog_storage.times_called == 1
    assert mock_eats_tags.times_called == 1
    assert stq.eats_proactive_support_actions.times_called == 0
    assert stq.eats_proactive_support_detections.times_called == 0
    assert stq.eats_proactive_support_couriers.times_called == 0


@pytest.mark.now('1970-01-01T00:00:00+00:00')
@pytest.mark.config(EATS_PROACTIVE_SUPPORT_DETECTORS_SETTINGS=DETECTORS_CONFIG)
@pytest.mark.config(
    EATS_MAP_CARGO_ALIAS_TO_CLIENT_ID=MAP_CARGO_ALIAS_TO_CLIENT_ID,
)
@pytest.mark.pgsql('eats_proactive_support', files=['fill_orders.sql'])
@DETECTOR_EXPERIMENT_ENABLED
@AUTOSTATUS_FILTER_EXPERIMENT_ENABLED
async def test_start_watching(
        pgsql,
        stq_runner,
        stq,
        mock_eats_orders_tracking,
        mock_cargo_claims_external_performer,
        mock_eats_catalog_storage,
        mock_eats_tags,
        mock_cargo_claims_full,
        mock_cargo_dispatch_segment_info,
        order_nr='123',
):
    await stq_runner.eats_proactive_support_detections.call(
        task_id='123',
        kwargs={
            'order_nr': order_nr,
            'event_name': 'created',
            'detector_name': 'courier',
        },
    )

    assert_db_problems(pgsql['eats_proactive_support'], 0)
    assert_db_actions(pgsql['eats_proactive_support'], 0)
    assert_db_courier_on_orders(pgsql['eats_proactive_support'], 1)

    assert mock_eats_orders_tracking.times_called == 1
    assert mock_cargo_claims_external_performer.times_called == 1
    assert mock_eats_catalog_storage.times_called == 1
    assert mock_eats_tags.times_called == 1
    assert mock_cargo_claims_full.times_called == 1
    assert mock_cargo_dispatch_segment_info.times_called == 1
    assert stq.eats_proactive_support_actions.times_called == 0
    assert stq.eats_proactive_support_detections.times_called == 0

    assert stq.eats_proactive_support_couriers.times_called == 1
    task = stq.eats_proactive_support_couriers.next_call()

    assert task['kwargs']['driver_profile_id'] == 'driver_profile_id_1'
    expected_eta = datetime.datetime.fromisoformat('1970-01-01T00:00:17+00:00')
    assert task['eta'] == expected_eta.replace(tzinfo=None)


@pytest.mark.pgsql(
    'eats_proactive_support', files=['fill_orders.sql', 'fill_couriers.sql'],
)
async def test_finished_order(
        pgsql,
        stq_runner,
        stq,
        mock_cargo_claims_info,
        mock_cargo_claims_bulk_info,
):
    await stq_runner.eats_proactive_support_couriers.call(
        task_id='driver_profile_id_2',
        kwargs={'driver_profile_id': 'driver_profile_id_2'},
    )

    assert_db_courier_on_orders(
        pgsql['eats_proactive_support'], STATIC_COURIER_ON_ORDERS,
    )
    assert_db_courier_positions(
        pgsql['eats_proactive_support'], STATIC_COURIER_POSITIONS,
    )
    assert_db_courier_analyzes(
        pgsql['eats_proactive_support'], STATIC_COURIER_ANALYZES,
    )

    assert mock_cargo_claims_info.times_called == 0
    assert mock_cargo_claims_bulk_info.times_called == 0
    assert stq.eats_proactive_support_couriers.times_called == 0


@pytest.mark.now('1970-01-01T00:03:35+00:00')
@pytest.mark.pgsql(
    'eats_proactive_support', files=['fill_orders.sql', 'fill_couriers.sql'],
)
@pytest.mark.parametrize(
    ['polling_interval_sec'],
    [
        pytest.param(None, id='default_slow_interval'),
        pytest.param(20, id='specified_slow_interval'),
    ],
)
async def test_change_status_single(
        pgsql,
        stq_runner,
        stq,
        mock_cargo_claims_info,
        mock_cargo_claims_bulk_info,
        mock_cargo_claims_performer_position,
        mock_cargo_dispatch_exchange_confirm,
        exp_courier_autostatus,
        polling_interval_sec,
):
    await exp_courier_autostatus(
        slow_polling_interval_sec=polling_interval_sec,
    )

    await stq_runner.eats_proactive_support_couriers.call(
        task_id='driver_profile_id_1',
        kwargs={'driver_profile_id': 'driver_profile_id_1'},
    )

    assert_db_courier_on_orders(
        pgsql['eats_proactive_support'], STATIC_COURIER_ON_ORDERS,
    )
    assert_db_courier_positions(
        pgsql['eats_proactive_support'], STATIC_COURIER_POSITIONS + 1,
    )
    assert_db_courier_analyzes(
        pgsql['eats_proactive_support'], STATIC_COURIER_ANALYZES + 1,
    )

    assert mock_cargo_claims_info.times_called == 0
    assert mock_cargo_claims_bulk_info.times_called == 1
    assert mock_cargo_claims_performer_position.times_called == 1
    assert mock_cargo_dispatch_exchange_confirm.times_called == 1

    assert stq.eats_proactive_support_couriers.times_called == 1
    task = stq.eats_proactive_support_couriers.next_call()

    expected_eta = datetime.datetime.fromisoformat('1970-01-01T00:03:45+00:00')
    assert task['eta'] == expected_eta.replace(tzinfo=None)


@pytest.mark.now('1970-01-01T00:03:35+00:00')
@pytest.mark.pgsql(
    'eats_proactive_support', files=['fill_orders.sql', 'fill_couriers.sql'],
)
@pytest.mark.parametrize(
    ['high_speed', 'min_positions_at_high_speed', 'expected_num_analyzes'],
    [
        pytest.param(None, None, 2, id='high_speed_not_specified'),
        pytest.param(5.0, 6, 2, id='high_speed_specified'),
        pytest.param(5.0, 7, 1, id='high_speed_specified_needs_points'),
    ],
)
async def test_high_speed(
        pgsql,
        stq_runner,
        stq,
        mock_cargo_claims_info,
        mock_cargo_claims_bulk_info,
        mock_cargo_claims_performer_position,
        mock_cargo_dispatch_exchange_confirm,
        exp_courier_autostatus,
        high_speed,
        min_positions_at_high_speed,
        expected_num_analyzes,
):
    await exp_courier_autostatus(
        high_courier_speed=high_speed,
        min_good_pos_at_high_speed=min_positions_at_high_speed,
    )

    await stq_runner.eats_proactive_support_couriers.call(
        task_id='driver_profile_id_1',
        kwargs={'driver_profile_id': 'driver_profile_id_1'},
    )

    assert_db_courier_on_orders(
        pgsql['eats_proactive_support'], STATIC_COURIER_ON_ORDERS,
    )
    assert_db_courier_positions(
        pgsql['eats_proactive_support'], STATIC_COURIER_POSITIONS + 1,
    )
    assert_db_courier_analyzes(
        pgsql['eats_proactive_support'], expected_num_analyzes,
    )

    assert stq.eats_proactive_support_couriers.times_called == 1
    task = stq.eats_proactive_support_couriers.next_call()

    expected_eta = datetime.datetime.fromisoformat('1970-01-01T00:03:45+00:00')
    assert task['eta'] == expected_eta.replace(tzinfo=None)


@pytest.mark.now('1970-01-01T00:03:35+00:00')
@pytest.mark.pgsql(
    'eats_proactive_support', files=['fill_orders.sql', 'fill_couriers.sql'],
)
@pytest.mark.parametrize(
    ['no_gps_anomaly_distance_meters', 'expected_num_analyzes'],
    [
        pytest.param(
            None, STATIC_COURIER_ANALYZES + 1, id='distance_not_specified',
        ),
        pytest.param(
            111, STATIC_COURIER_ANALYZES + 1, id='distance_no_anomaly',
        ),
        pytest.param(200, STATIC_COURIER_ANALYZES, id='distance_with_anomaly'),
    ],
)
async def test_gps_jump(
        pgsql,
        stq_runner,
        stq,
        mock_cargo_claims_info,
        mock_cargo_claims_bulk_info,
        mock_cargo_claims_performer_position,
        mock_cargo_dispatch_exchange_confirm,
        exp_courier_autostatus,
        no_gps_anomaly_distance_meters,
        expected_num_analyzes,
):
    await exp_courier_autostatus(
        minimal_period_near_point_sec=120,
        no_gps_anomaly_distance_meters=no_gps_anomaly_distance_meters,
    )

    await stq_runner.eats_proactive_support_couriers.call(
        task_id='driver_profile_id_4',
        kwargs={'driver_profile_id': 'driver_profile_id_4'},
    )

    assert_db_courier_on_orders(
        pgsql['eats_proactive_support'], STATIC_COURIER_ON_ORDERS,
    )
    assert_db_courier_positions(
        pgsql['eats_proactive_support'], STATIC_COURIER_POSITIONS + 1,
    )
    assert_db_courier_analyzes(
        pgsql['eats_proactive_support'], expected_num_analyzes,
    )

    assert stq.eats_proactive_support_couriers.times_called == 1
    task = stq.eats_proactive_support_couriers.next_call()

    expected_eta = datetime.datetime.fromisoformat('1970-01-01T00:03:45+00:00')
    assert task['eta'] == expected_eta.replace(tzinfo=None)


@pytest.mark.now('1970-01-01T00:03:35+00:00')
@pytest.mark.pgsql(
    'eats_proactive_support', files=['fill_orders.sql', 'fill_couriers.sql'],
)
@pytest.mark.parametrize(
    [
        'very_far_from_point_distance',
        'max_speed_very_far',
        'expected_num_analyzes',
    ],
    [
        pytest.param(
            None, None, STATIC_COURIER_ANALYZES, id='very_far_not_specified',
        ),
        pytest.param(
            400, 20, STATIC_COURIER_ANALYZES, id='very_far_specified_slow',
        ),
        pytest.param(
            400, 25, STATIC_COURIER_ANALYZES + 1, id='very_far_specified_fast',
        ),
    ],
)
async def test_very_far(
        pgsql,
        mockserver,
        stq_runner,
        stq,
        mock_cargo_claims_info,
        mock_cargo_claims_bulk_info,
        mock_cargo_dispatch_exchange_confirm,
        exp_courier_autostatus,
        very_far_from_point_distance,
        max_speed_very_far,
        expected_num_analyzes,
):
    await exp_courier_autostatus(
        very_far_from_point_distance=very_far_from_point_distance,
        max_speed_very_far=max_speed_very_far,
    )

    @mockserver.json_handler(
        '/cargo-claims/api/integration/v1/claims/performer-position',
    )
    def _mock_cargo_claims_performer_position(request):
        return mockserver.make_response(
            status=200,
            json={'position': {'lat': 30.1042, 'lon': 50.1, 'timestamp': 210}},
        )

    await stq_runner.eats_proactive_support_couriers.call(
        task_id='driver_profile_id_5',
        kwargs={'driver_profile_id': 'driver_profile_id_5'},
    )

    assert_db_courier_on_orders(
        pgsql['eats_proactive_support'], STATIC_COURIER_ON_ORDERS,
    )
    assert_db_courier_positions(
        pgsql['eats_proactive_support'], STATIC_COURIER_POSITIONS + 1,
    )
    assert_db_courier_analyzes(
        pgsql['eats_proactive_support'], expected_num_analyzes,
    )

    assert stq.eats_proactive_support_couriers.times_called == 1
    task = stq.eats_proactive_support_couriers.next_call()

    expected_eta = datetime.datetime.fromisoformat('1970-01-01T00:03:45+00:00')
    assert task['eta'] == expected_eta.replace(tzinfo=None)


@pytest.mark.now('1970-01-01T00:00:00+00:00')
@pytest.mark.pgsql(
    'eats_proactive_support', files=['fill_orders.sql', 'fill_couriers.sql'],
)
@pytest.mark.parametrize(
    ['polling_interval_sec', 'expected_eta'],
    [
        pytest.param(
            None, '1970-01-01T00:00:10+00:00', id='default_slow_interval',
        ),
        pytest.param(
            20, '1970-01-01T00:00:20+00:00', id='specified_slow_interval',
        ),
    ],
)
async def test_reschedule_stq(
        pgsql,
        mockserver,
        stq_runner,
        stq,
        mock_cargo_claims_bulk_info,
        mock_cargo_claims_performer_position,
        mock_cargo_dispatch_exchange_confirm,
        exp_courier_autostatus,
        polling_interval_sec,
        expected_eta,
):
    await exp_courier_autostatus(
        slow_polling_interval_sec=polling_interval_sec,
    )

    @mockserver.json_handler('/cargo-claims/api/integration/v2/claims/info')
    def mock_cargo_claims_info(request):
        return mockserver.make_response(
            status=200,
            json=build_claim_info(
                'claim_id_123', 'pickuped', 1000, 30.1, 50.1,
            ),
        )

    await stq_runner.eats_proactive_support_couriers.call(
        task_id='driver_profile_id_3',
        kwargs={'driver_profile_id': 'driver_profile_id_3'},
    )

    assert_db_courier_on_orders(
        pgsql['eats_proactive_support'], STATIC_COURIER_ON_ORDERS,
    )
    assert_db_courier_positions(
        pgsql['eats_proactive_support'], STATIC_COURIER_POSITIONS,
    )
    assert_db_courier_analyzes(
        pgsql['eats_proactive_support'], STATIC_COURIER_ANALYZES,
    )

    assert mock_cargo_claims_info.times_called == 1
    assert mock_cargo_claims_bulk_info.times_called == 0
    assert mock_cargo_claims_performer_position.times_called == 0
    assert mock_cargo_dispatch_exchange_confirm.times_called == 0

    assert stq.eats_proactive_support_couriers.times_called == 1
    task = stq.eats_proactive_support_couriers.next_call()

    expected_eta_datetime = datetime.datetime.fromisoformat(expected_eta)
    assert task['eta'] == expected_eta_datetime.replace(tzinfo=None)


@pytest.mark.now('1970-01-01T00:03:35+00:00')
@pytest.mark.pgsql(
    'eats_proactive_support', files=['fill_orders.sql', 'fill_couriers.sql'],
)
async def test_change_status_multi(
        pgsql,
        mockserver,
        stq_runner,
        stq,
        mock_cargo_claims_info,
        mock_cargo_claims_performer_position,
        mock_cargo_dispatch_exchange_confirm,
        exp_courier_autostatus,
):
    await exp_courier_autostatus()

    @mockserver.json_handler(
        '/cargo-claims/api/integration/v2/claims/bulk_info',
    )
    def mock_cargo_claims_bulk_info(request):
        return mockserver.make_response(
            status=200,
            json={
                'claims': [
                    build_claim_info(
                        'claim_id_123', 'pickup_arrived', 1000, 30.1, 50.1,
                    ),
                    build_claim_info(
                        'claim_id_125', 'pickup_arrived', 1010, 30.1, 50.1,
                    ),
                ],
            },
        )

    await stq_runner.eats_proactive_support_couriers.call(
        task_id='driver_profile_id_1',
        kwargs={'driver_profile_id': 'driver_profile_id_1'},
    )

    assert_db_courier_on_orders(
        pgsql['eats_proactive_support'], STATIC_COURIER_ON_ORDERS,
    )
    assert_db_courier_positions(
        pgsql['eats_proactive_support'], STATIC_COURIER_POSITIONS + 2,
    )
    assert_db_courier_analyzes(
        pgsql['eats_proactive_support'], STATIC_COURIER_ANALYZES + 2,
    )

    assert mock_cargo_claims_info.times_called == 0
    assert mock_cargo_claims_bulk_info.times_called == 1
    assert mock_cargo_claims_performer_position.times_called == 2
    assert mock_cargo_dispatch_exchange_confirm.times_called == 2

    assert stq.eats_proactive_support_couriers.times_called == 1
