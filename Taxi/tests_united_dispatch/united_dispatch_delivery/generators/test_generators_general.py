import collections
import dataclasses
import datetime
import uuid

import pytest

from testsuite.utils import matching


# TODO(CARGODEV-9676): use builder
@pytest.fixture(name='create_multipoint_segment')
def _create_multipoint_segment(create_segment):
    def wrapper(*args, **kwargs):
        segment_multipoint = create_segment(*args, **kwargs)
        dropoff_point = [
            dataclasses.replace(p)
            for p in segment_multipoint.points
            if p.point_type == 'dropoff'
        ][0]
        dropoff_point.point_id = str(uuid.uuid4())
        segment_multipoint.add_point(dropoff_point)
        return segment_multipoint

    return wrapper


async def test_generators_config(
        exp_delivery_configs,
        create_segment,
        testpoint,
        state_waybill_proposed,
):
    create_segment(zone_id='test_zone_id', corp_client_id='test_corp_id')
    create_segment(zone_id='wrong_zone_id', corp_client_id='test_corp_id')
    create_segment(zone_id='test_zone_id', corp_client_id='wrong_corp_id')
    create_segment(zone_id='wrong_zone_id', corp_client_id='wrong_corp_id')
    create_segment(zone_id='test_zone_id', corp_client_id='')
    expected_values = {
        'test_zone_id.test_corp_id': {
            'batch_size2_goodness_diff_threshold': 1,
            'batch_size2_goodness_ratio_threshold': 1.9,
            'max_segment_duration_increase': 2.1,
            'distance_of_arrival': 10,
        },
        'wrong_zone_id.test_corp_id': {
            'batch_size2_goodness_diff_threshold': 4,
            'batch_size2_goodness_ratio_threshold': 0,
            'max_segment_duration_increase': 4,
            'distance_of_arrival': 10,
        },
        'test_zone_id.wrong_corp_id': {
            'batch_size2_goodness_diff_threshold': 3,
            'batch_size2_goodness_ratio_threshold': 0,
            'max_segment_duration_increase': 2.1,
            'distance_of_arrival': 10,
        },
        'wrong_zone_id.wrong_corp_id': {
            'batch_size2_goodness_diff_threshold': -5000,
            'batch_size2_goodness_ratio_threshold': 0,
            'max_segment_duration_increase': 4,
            'distance_of_arrival': 10,
        },
        'test_zone_id.': {
            'batch_size2_goodness_diff_threshold': 3,
            'batch_size2_goodness_ratio_threshold': 0,
            'max_segment_duration_increase': 2.1,
            'distance_of_arrival': 10,
        },
    }

    @testpoint('delivery_planner::generators_settings')
    def check_config_correctness(data):
        zone_id = data['zone_id']
        corp_client_id = (
            data['corp_client_id'] if 'corp_client_id' in data else ''
        )
        full_id = zone_id + '.' + corp_client_id
        values = expected_values[full_id]
        assert (
            data['batch_size2_goodness_diff_threshold']
            == values['batch_size2_goodness_diff_threshold']
        )
        assert (
            data['batch_size2_goodness_ratio_threshold']
            == values['batch_size2_goodness_ratio_threshold']
        )
        assert (
            data['max_segment_duration_increase']
            == values['max_segment_duration_increase']
        )
        assert data['distance_of_arrival'] == values['distance_of_arrival']

    # Флаг, чтобы параллельно посмотреть, не упало ли что-то
    await exp_delivery_configs()
    await state_waybill_proposed()
    assert check_config_correctness.times_called


async def test_segments_splitter(
        exp_delivery_configs,
        testpoint,
        create_segment,
        create_multipoint_segment,
        state_waybill_proposed,
        cargo_dispatch,
        exp_delivery_gamble_settings,
        mocked_time,
):
    segments_can_batch = set()
    segments_can_batch.add(create_segment().id)
    segments_can_batch.add(create_segment().id)
    segments_can_batch.add(create_segment(allow_alive_batch_v1=False).id)
    segments_can_batch.add(create_segment(allow_alive_batch_v2=False).id)
    create_multipoint_segment()
    create_segment(taxi_classes={'express'})
    create_segment(allow_batch=False)
    create_segment(planner='delivery', corp_client_id='eats_corp_id1')
    create_segment(planner='delivery', corp_client_id='food_retail_corp_id1')
    create_segment(planner='delivery', corp_client_id='grocery_corp_id1')
    # do not batch if allow_batch=False, see CARGODEV-12505
    create_segment(
        allow_batch=False,
        allow_alive_batch_v1=True,
        allow_alive_batch_v2=False,
    )
    create_segment(
        allow_batch=False,
        allow_alive_batch_v1=False,
        allow_alive_batch_v2=True,
    )
    create_segment(
        allow_batch=False,
        allow_alive_batch_v1=True,
        allow_alive_batch_v2=True,
    )

    # force batches by claim_origin if certain cargo_finance features are set
    # (see CARGODEV-9115)

    # features are empty, don't force batch
    create_segment(
        allow_batch=False,
        allow_alive_batch_v1=False,
        allow_alive_batch_v2=False,
        claim_features=[],
        claim_origin='webcorp',
    )
    # feature is set, force batch
    segments_can_batch.add(
        create_segment(
            allow_batch=False,
            allow_alive_batch_v1=False,
            allow_alive_batch_v2=False,
            claim_features=[{'id': 'cargo_finance_use_cargo_pipeline'}],
            claim_origin='webcorp',
        ).id,
    )
    # cargo_finance_dry_cargo_events is set, don't force
    create_segment(
        allow_batch=False,
        allow_alive_batch_v1=False,
        allow_alive_batch_v2=False,
        claim_features=[
            {'id': 'cargo_finance_use_cargo_pipeline'},
            {'id': 'cargo_finance_dry_cargo_events'},
        ],
        claim_origin='webcorp',
    )
    # wrong claim_origin, don't force
    create_segment(
        allow_batch=False,
        allow_alive_batch_v1=False,
        allow_alive_batch_v2=False,
        claim_features=[{'id': 'cargo_finance_use_cargo_pipeline'}],
        claim_origin='yandexgo',
    )

    # CARGODEV-12910 don't batch segments
    # if strict interval on return is too close
    now = datetime.datetime(2022, 7, 15, 12)
    one_hour_later = now + datetime.timedelta(hours=1)
    two_hours_later = now + datetime.timedelta(hours=2)
    mocked_time.set(now)

    create_segment(
        allow_batch=True,
        return_time_intervals=[
            {
                'type': 'strict_match',
                'from': now.strftime(format='%Y-%m-%dT%H:%M:%SZ'),
                'to': one_hour_later.strftime(format='%Y-%m-%dT%H:%M:%SZ'),
            },
        ],
    )
    segments_can_batch.add(
        create_segment(
            allow_batch=True,
            return_time_intervals=[
                {
                    'type': 'strict_match',
                    'from': now.strftime(format='%Y-%m-%dT%H:%M:%SZ'),
                    'to': two_hours_later.strftime(
                        format='%Y-%m-%dT%H:%M:%SZ',
                    ),
                },
            ],
        ).id,
    )

    @testpoint('delivery_planner::check_segment_predicate')
    def check_can_batch_segment(data):
        if data['route_generator_tag'] not in (
                'two-circles-batch',
                'live-batch',
        ):
            return
        for segment in data['segments']:
            assert (segment['segment_id'] in segments_can_batch) == segment[
                'can_batch'
            ], f'failed check of segment_id={segment["segment_id"]}'

    await exp_delivery_gamble_settings(
        generators=['single-segment', 'two-circles-batch', 'live-batch'],
        forcedly_batched_origins=['webcorp'],
        return_time_left=90 * 60,  # 1h30m
    )
    await exp_delivery_configs(delivery_gamble_settings=False)
    await state_waybill_proposed()
    assert check_can_batch_segment.times_called
    # verify that all segments are checked
    checked_segment_ids = set()
    for _ in range(check_can_batch_segment.times_called):
        data = check_can_batch_segment.next_call()['data']
        if data['route_generator_tag'] in ('two-circles-batch', 'live-batch'):
            checked_segment_ids |= {
                segment['segment_id'] for segment in data['segments']
            }
    assert checked_segment_ids == set(cargo_dispatch.segments.segments.keys())


async def test_p2p_batches_contain_all_segments(
        exp_delivery_gamble_settings,
        exp_delivery_configs,
        testpoint,
        create_segment,
        create_multipoint_segment,
        state_waybill_proposed,
        cargo_dispatch,
):
    segments_can_batch = set()
    segments_can_batch.add(create_segment().id)
    segments_can_batch.add(create_segment().id)
    create_segment(taxi_classes={'express'})
    create_multipoint_segment()
    create_segment(allow_batch=False)
    create_segment(allow_alive_batch_v1=False)
    create_segment(allow_alive_batch_v2=False)
    create_segment(planner='delivery', corp_client_id='eats_corp_id1')
    create_segment(planner='delivery', corp_client_id='food_retail_corp_id1')
    create_segment(planner='delivery', corp_client_id='grocery_corp_id1')

    @testpoint('delivery_planner::pre_routes')
    def check_p2p_batches_contain_all(data):
        segments_in_pre_routes = collections.defaultdict(
            set,
        )  # segments by generator
        for batch in data['routes']:
            segments = {p['segment_id'] for p in batch['points']}
            segments_in_pre_routes[batch['generator']] |= segments

        assert (
            segments_in_pre_routes['single-segment']
            == cargo_dispatch.segments.segments.keys()
        )

    await exp_delivery_gamble_settings(generators=['single-segment'])
    await exp_delivery_configs(delivery_gamble_settings=False)
    await state_waybill_proposed()
    assert check_p2p_batches_contain_all.times_called


async def test_classes_filtration(
        exp_delivery_configs,
        create_segment,
        state_waybill_proposed,
        cargo_dispatch,
):
    segment_1 = create_segment(taxi_classes=['eda', 'courier', 'express'])

    await exp_delivery_configs()
    await state_waybill_proposed()

    waybill = cargo_dispatch.waybills.get_single_waybill()
    assert waybill.taxi_classes == ['express', 'courier']
    assert {segment_1.id} == {s.id for s in waybill.segments}


async def test_router_stats(
        exp_delivery_gamble_settings,
        exp_delivery_configs,
        create_segment,
        state_waybill_proposed,
        mock_maps,
        taxi_united_dispatch_delivery,
        taxi_united_dispatch_delivery_monitor,
):
    await taxi_united_dispatch_delivery.tests_control(reset_metrics=True)

    mock_maps.add_route(
        points=[[37.400000, 55.700000], [37.400000, 55.700000]],
        car_time=0,
        car_distance=0,
        pedestrian_time=0,
        pedestrian_distance=0,
    )
    create_segment()
    create_segment()

    await exp_delivery_gamble_settings(disable_maps_router=False)
    await exp_delivery_configs(delivery_gamble_settings=False)
    await state_waybill_proposed()

    stats = await taxi_united_dispatch_delivery_monitor.get_metric(
        'delivery-planner-router',
    )
    assert stats == {
        'client_routing_linear_router': {
            '$meta': {'solomon_children_labels': 'router_type'},
        },
        'client_routing_router': {
            'CarRouter': 1,
            'PedestrianRouter': 1,
            '$meta': {'solomon_children_labels': 'router_type'},
        },
        'custom_ud_linear_fallback': {
            '$meta': {'solomon_children_labels': 'router_type'},
        },
    }


async def test_pre_routes_collision(
        exp_delivery_gamble_settings,
        exp_delivery_generators_settings,
        exp_delivery_configs,
        create_segment,
        testpoint,
        state_waybill_proposed,
):
    pickup_coordinates = [
        [37.611330, 55.748982],
        [37.611330, 55.748982],
        [37.611330, 55.748982],
        [37.611330, 55.748982],
    ]
    dropoff_coordinates = [
        [37.614541, 55.750974],
        [37.619760, 55.752468],
        [37.625059, 55.752423],
        [37.631482, 55.751216],
    ]
    for i, coordinates in enumerate(
            zip(pickup_coordinates, dropoff_coordinates),
    ):
        pickup, dropoff = coordinates
        create_segment(
            pickup_coordinates=pickup,
            dropoff_coordinates=dropoff,
            segment_id=str(i),
            corp_client_id='b010d898a6ef4a3ea75d0e12e6ea51ef',
            zone_id='himki',
        )

    @testpoint('route_generator::segments_packs_collision_num')
    def check_batched_routes(data):
        assert data['segments_packs_size'] >= 1
        assert data['segments_packs_collision_num'] >= 1

    await exp_delivery_gamble_settings(
        generators=['two-circles-batch', 'two-circles-batch'],
    )
    await exp_delivery_generators_settings(
        pickup_radius_mult=10,
        pickup_radius_bias=0,
        dropoff_radius_mult=10,
        dropoff_radius_bias=0,
        min_batch_size=3,
        max_batch_size=6,
    )
    await exp_delivery_configs(
        delivery_gamble_settings=False, delivery_generators_settings=False,
    )
    await state_waybill_proposed()
    assert check_batched_routes.times_called


async def test_batch_properties(
        exp_delivery_configs,
        testpoint,
        create_segment,
        state_waybill_proposed,
        mock_maps,
):
    pickup_coordinates = (82.929395, 55.056471)
    dropoff_coordinates = (82.910909, 55.055010)
    mock_maps.add_route(
        points=[pickup_coordinates, dropoff_coordinates],
        car_time=360,
        car_distance=2500,
        pedestrian_time=960,
        pedestrian_distance=1370,
    )
    due = '2022-03-21T10:45:21Z'
    due_timestamp_s = 1647859521.0

    estimations = [
        {'offer_price': '300.0000', 'tariff_class': 'courier'},
        {'offer_price': '200.0000', 'tariff_class': 'express'},
    ]

    segment_with_due = create_segment(
        pickup_coordinates=pickup_coordinates,
        dropoff_coordinates=dropoff_coordinates,
        due=due,
        estimations=estimations,
    )

    corp_client_id = 'test-corp-client-id'
    segment_with_corp = create_segment(
        pickup_coordinates=pickup_coordinates,
        dropoff_coordinates=dropoff_coordinates,
        corp_client_id=corp_client_id,
        estimations=estimations,
    )

    @testpoint('delivery_planner::batch_properties')
    def batch_properties(data):
        batch_aggregates = data['batch_properties']['batch_aggregates']
        assert len(data['segment_ids']) == batch_aggregates['num_segments']
        assert 'route_id' in batch_aggregates
        assert 'gamble_id' in batch_aggregates
        assert 'waybill_ref' in batch_aggregates
        tariff_offers_prices = sorted(
            batch_aggregates['tariff_offers_prices'],
            key=lambda el: el['class_name'],
        )
        assert tariff_offers_prices == [
            {
                'class_name': 'courier',
                'price': 300.0 * batch_aggregates['num_segments'],
            },
            {
                'class_name': 'express',
                'price': 200.0 * batch_aggregates['num_segments'],
            },
        ]
        for routers_data_name in [
                'routers_data',
                'total_segment_routers_data',
        ]:
            for router_type in ['car', 'pedestrian']:
                assert routers_data_name in batch_aggregates
                router_data = batch_aggregates[routers_data_name]
                assert router_type in router_data
                assert router_data[router_type]['distance'] > 0
                assert router_data[router_type]['time'] > 0

        batch_segments = data['batch_properties']['segments']

        total_segment_routers_distance = collections.defaultdict(int)
        total_segment_routers_time = collections.defaultdict(int)

        for batch_segment in batch_segments:
            total_segment_routers_distance['car'] += batch_segment[
                'routers_data'
            ]['car']['distance']
            total_segment_routers_time['car'] += batch_segment['routers_data'][
                'car'
            ]['time']

            total_segment_routers_distance['pedestrian'] += batch_segment[
                'routers_data'
            ]['pedestrian']['distance']
            total_segment_routers_time['pedestrian'] += batch_segment[
                'routers_data'
            ]['pedestrian']['time']

        assert (
            batch_aggregates['total_segment_routers_data']['car']['distance']
            == total_segment_routers_distance['car']
        )
        assert (
            batch_aggregates['total_segment_routers_data']['car']['time']
            == total_segment_routers_time['car']
        )
        assert (
            batch_aggregates['total_segment_routers_data']['pedestrian'][
                'distance'
            ]
            == total_segment_routers_distance['pedestrian']
        )
        assert (
            batch_aggregates['total_segment_routers_data']['pedestrian'][
                'time'
            ]
            == total_segment_routers_time['pedestrian']
        )

        batch_points = data['batch_properties']['points']

        points_router_distance = collections.defaultdict(int)
        points_router_time = collections.defaultdict(int)

        for batch_point in batch_points:
            batch_segment = batch_segments[batch_point['segment_index']]
            if batch_segment['id'] == segment_with_due.id:
                assert batch_segment['due_timestamp_s'] == due_timestamp_s
                if batch_point['type'] == 'pickup':
                    assert batch_point['due_timestamp_s'] == due_timestamp_s
                else:
                    assert 'due_timestamp_s' not in batch_point

            assert batch_point['geopoint']

            if (
                    'car' in batch_point['from_start_routers_data']
                    or 'pedestrian' in batch_point['from_start_routers_data']
            ):
                assert (
                    'car' in batch_point['from_start_routers_data']
                    and 'pedestrian' in batch_point['from_start_routers_data']
                )

                points_router_distance['car'] = batch_point[
                    'from_start_routers_data'
                ]['car']['distance']
                points_router_time['car'] = batch_point[
                    'from_start_routers_data'
                ]['car']['time']

                points_router_distance['pedestrian'] = batch_point[
                    'from_start_routers_data'
                ]['pedestrian']['distance']
                points_router_time['pedestrian'] = batch_point[
                    'from_start_routers_data'
                ]['pedestrian']['time']

            assert batch_segment['num_dropoff_points'] == 1
            assert batch_segment['ud_created_s'] == matching.any_float
            if batch_segment['id'] == segment_with_corp.id:
                assert batch_segment['corp_client_id'] == corp_client_id
            tariff_offers_prices = sorted(
                batch_segment['tariff_offers_prices'],
                key=lambda el: el['class_name'],
            )
            assert tariff_offers_prices == [
                {'class_name': 'courier', 'price': 300.0},
                {'class_name': 'express', 'price': 200.0},
            ]

        assert (
            batch_aggregates['routers_data']['car']['distance']
            == points_router_distance['car']
        )
        assert (
            batch_aggregates['routers_data']['car']['time']
            == points_router_time['car']
        )

        assert (
            batch_aggregates['routers_data']['pedestrian']['distance']
            == points_router_distance['pedestrian']
        )
        assert (
            batch_aggregates['routers_data']['pedestrian']['time']
            == points_router_time['pedestrian']
        )

    await exp_delivery_configs()
    await state_waybill_proposed()
    assert batch_properties.times_called == 4


@pytest.mark.parametrize(
    """is_forbidden_to_be_in_batch,
    is_forbidden_to_be_in_taxi_batch,
    num_batches""",
    [(True, True, 3), (True, False, 5), (False, True, 5), (False, False, 10)],
)
async def test_delivery_assign_rover_param(
        state_waybill_proposed,
        testpoint,
        exp_delivery_configs,
        create_segment,
        is_forbidden_to_be_in_batch,
        is_forbidden_to_be_in_taxi_batch,
        num_batches,
):
    custom_context_1 = {
        'delivery_flags': {
            'is_forbidden_to_be_in_batch': is_forbidden_to_be_in_batch,
        },
    }
    custom_context_2 = {
        'delivery_flags': {
            'is_forbidden_to_be_in_taxi_batch': (
                is_forbidden_to_be_in_taxi_batch
            ),
        },
    }

    create_segment()
    create_segment(custom_context=custom_context_1)
    create_segment(custom_context=custom_context_2)

    @testpoint('delivery_planner::dead_routes')
    def check_num_batches(data):
        assert len(data['routes']) >= num_batches

    await exp_delivery_configs()
    await state_waybill_proposed()

    assert check_num_batches.times_called
