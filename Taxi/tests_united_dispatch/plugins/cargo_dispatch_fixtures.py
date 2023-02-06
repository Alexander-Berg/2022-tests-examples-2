"""
    Describe here cargo-dispatch service specific fixtures.
"""
# pylint: disable=redefined-outer-name
# flake8: noqa: E501
import dataclasses

import pytest

from . import cargo_dispatch_manager


@pytest.fixture
def cargo_dispatch():
    return cargo_dispatch_manager.CargoDispatch()


@pytest.fixture
def propositions_manager():
    return cargo_dispatch_manager.PropositionsManager()


@pytest.fixture(name='make_point')
async def _make_point():
    def wrapper(**kwargs):
        return cargo_dispatch_manager.Point(**kwargs)

    return wrapper


@pytest.fixture(name='segment_point_builder')
async def _segment_point_builder(load_json_var):
    def wrapper(*, visit_order: int, point: cargo_dispatch_manager.Point):
        result = load_json_var(
            'cargo-dispatch/segment_point.json',
            location_id=point.location_id,
            point_id=point.point_id,
            point_type=point.point_type,
            visit_order=visit_order,
            due=point.due,
            external_order_id=point.external_order_id,
        )

        if point.time_intervals is not None:
            result['time_intervals'] = point.time_intervals

        return result

    return wrapper


@pytest.fixture(name='location_builder')
async def _location_builder(load_json_var):
    def wrapper(*, point: cargo_dispatch_manager.Point):
        return load_json_var(
            'cargo-dispatch/location.json',
            id=point.location_id,
            coordinates=point.coordinates,
        )

    return wrapper


@pytest.fixture(name='waybill_builder')
async def _waybill_builder(load_json_var, segment_point_builder):
    def wrapper(waybill: cargo_dispatch_manager.Waybill):
        execution_points = []
        waybill_points = []
        for i, point in enumerate(waybill.points):
            visit_order = i + 1
            execution_points.append(
                load_json_var(
                    'cargo-dispatch/waybill/execution_point.json',
                    coordinates=point.coordinates,
                    location_id=point.location_id,
                    point_id=point.point_id,
                    is_resolved=point.is_resolved,
                    resolution=point.resolution,
                    segment_id=point.segment_id,
                    point_type=point.point_type,
                    visit_order=visit_order,
                    visit_status=point.visit_status,
                ),
            )
            waybill_points.append(
                load_json_var(
                    'cargo-dispatch/waybill/waybill_point.json',
                    point_id=point.point_id,
                    segment_id=point.segment_id,
                    visit_order=visit_order,
                ),
            )

        execution_segments = []
        segments = []
        for seg in waybill.segments:
            execution_segments.append(
                load_json_var(
                    'cargo-dispatch/waybill/execution_segment.json',
                    id=seg.id,
                    allow_alive_batch_v1=seg.allow_alive_batch_v1,
                    allow_alive_batch_v2=seg.allow_alive_batch_v2,
                    allow_batch=seg.allow_batch,
                    status=seg.status,
                ),
            )

            points = []
            locations = []
            for i, point in enumerate(waybill.points):
                if point.segment_id != seg.id:
                    continue
                points.append(
                    segment_point_builder(point=point, visit_order=i + 1),
                )
                locations.append(
                    load_json_var(
                        'cargo-dispatch/waybill/location.json',
                        id=point.location_id,
                        coordinates=point.coordinates,
                    ),
                )
            segments.append(
                load_json_var(
                    'cargo-dispatch/waybill/segment.json',
                    id=seg.id,
                    waybill_building_version=seg.waybill_building_version,
                    corp_client_id=seg.corp_client_id,
                    zone_id=seg.zone_id,
                    locations=locations,
                    points=points,
                    special_requirements=cargo_dispatch_manager.serialize_special_requirements(
                        seg.special_requirements,
                    ),
                    taxi_classes=list(seg.taxi_classes),
                    allow_alive_batch_v1=seg.allow_alive_batch_v1,
                    allow_alive_batch_v2=seg.allow_alive_batch_v2,
                    allow_batch=seg.allow_batch,
                    status=seg.status,
                    waybill_building_awaited=seg.waybill_building_awaited,
                ),
            )

        taxi_order_info = None  # filled on taxi order created
        cargo_order_info = None  # filled on taxi order created
        if waybill.taxi_order_id or waybill.cargo_order_id:
            cargo_order_info = load_json_var(
                'cargo-dispatch/waybill/cargo_order_info.json',
                taxi_order_id=waybill.taxi_order_id,
                cargo_order_id=waybill.cargo_order_id,
            )
        if waybill.taxi_order_id:
            performer_info = None
            if waybill.performer_id:
                assert waybill.performer_tariff
                park_id, driver_id = waybill.performer_id.split('_')
                performer_info = load_json_var(
                    'cargo-dispatch/waybill/performer_info.json',
                    park_id=park_id,
                    driver_id=driver_id,
                    tariff_class=waybill.performer_tariff,
                )

            taxi_order_info = load_json_var(
                'cargo-dispatch/waybill/taxi_order_info.json',
                taxi_order_id=waybill.taxi_order_id,
                performer_found_ts=waybill.performer_found_ts,
                performer_info=performer_info,
            )

        return load_json_var(
            'cargo-dispatch/waybill.json',
            waybill_ref=waybill.id,
            revision=waybill.revision,
            status=waybill.status,
            is_performer_assigned=waybill.performer_id is not None,
            cargo_order_info=cargo_order_info,
            execution_points=execution_points,
            execution_segments=execution_segments,
            taxi_order_info=taxi_order_info,
            segments=segments,
            waybill_points=waybill_points,
            special_requirements=waybill.special_requirements,
            taxi_classes=waybill.taxi_classes,
            resolution=waybill.resolution,
            is_waybill_accepted=waybill.is_accepted,
            is_waybill_declined=waybill.is_declined,
        )

    return wrapper


@pytest.fixture(name='internal_waybill_builder')
async def _internal_waybill_builder(load_json_var, segment_builder):
    def wrapper(waybill: cargo_dispatch_manager.Waybill):
        path = []
        for point in waybill.points:
            path.append(
                load_json_var(
                    'united-dispatch/waybill/path_item.json',
                    point_id=point.point_id,
                    resolution=point.resolution and point.visit_status,
                    segment_id=point.segment_id,
                ),
            )

        segments = []
        for seg in waybill.segments:
            segment = segment_builder(seg)
            segments.append(
                load_json_var(
                    'united-dispatch/waybill/segment.json', segment=segment,
                ),
            )

        performer = None
        if waybill.performer_id:
            performer = load_json_var(
                'united-dispatch/waybill/performer.json',
                id=waybill.performer_id,
                found_ts=waybill.performer_found_ts,
                tariff_class=waybill.performer_tariff,
            )

        return load_json_var(
            'united-dispatch/waybill.json',
            path_items=path,
            segments=segments,
            taxi_order_id=waybill.taxi_order_id,
            performer=performer,
            taxi_order_requirements={'forced_soon': True},
            update_proposition=None,
        )

    return wrapper


@pytest.fixture(name='segment_builder')
async def _segment_builder(
        load_json_var, segment_point_builder, location_builder,
):
    def wrapper(segment: cargo_dispatch_manager.Segment):
        performer_requirements = segment.taxi_requirements
        performer_requirements['special_requirements'] = (
            cargo_dispatch_manager.serialize_special_requirements(
                segment.special_requirements,
            )
        )
        performer_requirements['taxi_classes'] = list(segment.taxi_classes)

        points = []
        locations = []
        for i, point in enumerate(segment.points):
            points.append(
                segment_point_builder(point=point, visit_order=i + 1),
            )
            locations.append(location_builder(point=point))

        response = load_json_var(
            'cargo-dispatch/segment.json',
            id=segment.id,
            waybill_building_version=segment.waybill_building_version,
            waybill_building_awaited=segment.waybill_building_awaited,
            waybill_building_deadline=segment.waybill_building_deadline,
            corp_client_id=segment.corp_client_id,
            zone_id=segment.zone_id,
            modified_classes=segment.modified_classes,
            tariffs_substitution=segment.tariffs_substitution,
            performer_requirements=performer_requirements,
            custom_context=segment.custom_context,
            points=points,
            locations=locations,
            claim_comment=segment.build_comment(),
            allow_batch=segment.allow_batch,
            allow_alive_batch_v1=segment.allow_alive_batch_v1,
            allow_alive_batch_v2=segment.allow_alive_batch_v2,
            resolution=segment.resolution,
            resolved=bool(segment.resolution),
            chosen_waybill=segment.chosen_waybill,
            estimations=segment.estimations,
            routers=segment.routers,
            items=list(map(dataclasses.asdict, segment.items)),
            claim_features=segment.claim_features,
            claim_origin=segment.claim_origin,
        )

        return response

    return wrapper


@pytest.fixture(name='create_segment')
def _create_segment(
        mock_segment_dispatch_journal,
        mock_dispatch_segment_info,
        cargo_dispatch: cargo_dispatch_manager.CargoDispatch,
):
    def wrapper(**kwargs):
        segment = cargo_dispatch_manager.make_segment(**kwargs)
        cargo_dispatch.add_segment(segment)
        return segment

    return wrapper


@pytest.fixture(name='make_eats_custom_context')
async def _make_eats_custom_context():
    def wrapper(
            zone_type=None,
            order_confirmed_at=None,
            is_fast_food=None,
            delivery_flags=None,
            place_id=None,
            **kwargs,
    ):
        ctx = {
            'cooking_time': 480,
            'delivery_cost': {
                'value': 400,
                'currency': 'RUB',
                'decimal_places': 2,
            },
            'delivery_flags': {
                'assign_rover': False,
                'is_forbidden_to_be_in_batch': False,
                'is_forbidden_to_be_in_taxi_batch': False,
                'is_forbidden_to_be_second_in_batch': False,
            },
            'delivery_flow_type': 'courier',
            'has_slot': False,
            'is_asap': True,
            'is_fast_food': False,
            'items_cost': {
                'value': 1800,
                'currency': 'RUB',
                'decimal_places': 2,
            },
            'order_cancel_at': '2021-12-14T16:10:00.425521+00:00',
            'order_confirmed_at': '2021-12-14T15:15:00.425521+00:00',
            'order_flow_type': 'native',
            'order_id': 110000,
            'brand_id': 1,
            'place_id': 10,
            'promise_max_at': '2021-12-14T15:50:00.425521+00:00',
            'promise_min_at': '2021-12-14T15:40:00.425521+00:00',
            'region_id': 1,
            'route_to_client': {
                'pedestrian': {
                    'distance': 600,
                    'time': 120,
                    'is_precise': True,
                },
                'transit': {'distance': 800, 'time': 300, 'is_precise': True},
                'auto': {'distance': 1200, 'time': 260, 'is_precise': True},
            },
            'surge_data': {'currency_code': 'RUB', 'price': '30'},
            'send_to_place_at': '2021-12-14T15:20:00.425521+00:00',
            'user_device_id': '___??',
            'weight': 234,
        }

        if zone_type:
            ctx['zone_type'] = zone_type

        if order_confirmed_at:
            ctx['order_confirmed_at'] = order_confirmed_at

        if is_fast_food:
            ctx['is_fast_food'] = is_fast_food

        if delivery_flags:
            ctx['delivery_flags'].update(delivery_flags)

        if place_id:
            ctx['place_id'] = place_id
        return ctx

    return wrapper
