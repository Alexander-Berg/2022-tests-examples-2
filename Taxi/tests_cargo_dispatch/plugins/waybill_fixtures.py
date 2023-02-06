"""Fixtures to build and propose waybills.
"""

import itertools
import uuid

import pytest


@pytest.fixture(name='propose_from_segments')
def _propose_from_segments(waybill_from_segments, request_waybill_propose):
    async def _wrapper(
            router_id,
            waybill_external_ref,
            *segment_id_list,
            status_code=200,
            kind=None,
            reverse_destinations=False,
            segment_building_versions=None,
            taxi_requirements=None,
            lookup_extra=None,
    ):
        proposal = await waybill_from_segments(
            router_id,
            waybill_external_ref,
            *segment_id_list,
            kind=kind,
            reverse_destinations=reverse_destinations,
            segment_building_versions=segment_building_versions,
            taxi_requirements=taxi_requirements,
            lookup_extra=lookup_extra,
        )
        response = await request_waybill_propose(proposal)
        assert response.status_code == status_code
        return response.json()

    return _wrapper


@pytest.fixture(name='waybill_from_segments')
def _waybill_from_segments(get_segment_info):
    async def _wrapper(
            router_id,
            waybill_external_ref,
            *segment_id_list,
            kind=None,
            reverse_destinations: bool = False,
            segment_building_versions=None,
            taxi_requirements=None,
            lookup_extra=None,
    ):
        proposal = await _build_points_and_segments(
            segment_id_list,
            get_segment_info,
            reverse_destinations=reverse_destinations,
            segment_building_versions=segment_building_versions,
            taxi_requirements=taxi_requirements,
        )
        proposal['router_id'] = router_id
        proposal['external_ref'] = waybill_external_ref
        proposal['special_requirements'] = {
            'virtual_tariffs': [
                {
                    'class': 'cargo',
                    'special_requirements': [{'id': 'cargo_eds'}],
                },
            ],
        }
        if kind is not None:
            proposal['kind'] = kind
        if lookup_extra is not None:
            proposal['taxi_lookup_extra'] = lookup_extra
        return proposal

    return _wrapper


@pytest.fixture(name='waybill_from_segments_pull_dispatch')
def _waybill_from_segments_pull_dispatch(get_segment_info):
    async def _wrapper(
            router_id,
            waybill_external_ref,
            *segment_id_list,
            kind=None,
            segment_building_versions=None,
            taxi_requirements=None,
    ):
        proposal = await _build_points_and_segments_pull_dispatch(
            segment_id_list,
            get_segment_info,
            segment_building_versions=segment_building_versions,
            taxi_requirements=taxi_requirements,
        )
        proposal['router_id'] = router_id
        proposal['external_ref'] = waybill_external_ref
        proposal['special_requirements'] = {
            'virtual_tariffs': [
                {
                    'class': 'cargo',
                    'special_requirements': [{'id': 'cargo_eds'}],
                },
            ],
        }
        if kind is not None:
            proposal['kind'] = kind
        return proposal

    return _wrapper


async def _build_points_and_segments(
        segment_id_list,
        get_segment_info,
        *,
        reverse_destinations=False,
        segment_building_versions=None,
        taxi_requirements=None,
):
    if not segment_id_list:
        raise ValueError('no segment ids passed, cannot build waybill')
    if segment_building_versions is None:
        segment_building_versions = {}

    points = {'pickup': [], 'dropoff': [], 'return': []}
    segversions = {}
    for segment_id in segment_id_list:
        if segment_id in segversions:
            raise ValueError('segment %s passed twice' % segment_id)

        seginfo = await get_segment_info(segment_id)
        dispatch = seginfo['dispatch']
        segversions[segment_id] = segment_building_versions.get(
            segment_id, dispatch['waybill_building_version'],
        )
        for segpoint in seginfo['segment']['points']:
            obj = {'segment_id': segment_id, 'point_id': segpoint['point_id']}
            points[segpoint['type']].append(obj)

    proposal = {'segments': [], 'points': []}

    for segment_id, waybill_building_version in segversions.items():
        segment_info = {
            'segment_id': segment_id,
            'waybill_building_version': waybill_building_version,
        }
        proposal['segments'].append(segment_info)

    if reverse_destinations:
        points['dropoff'] = points['dropoff'][::-1]

    all_points = itertools.chain(
        points['pickup'], points['dropoff'], points['return'],
    )
    for (visit_order, obj) in enumerate(all_points, start=1):
        obj['visit_order'] = visit_order
        proposal['points'].append(obj)

    proposal['taxi_order_requirements'] = {
        'taxi_classes': ['express', 'courier'],
        'door_to_door': True,
    }

    if taxi_requirements:
        proposal['taxi_order_requirements'].update(taxi_requirements)

    return proposal


async def _build_points_and_segments_pull_dispatch(
        segment_id_list,
        get_segment_info,
        *,
        reverse_destinations=False,
        segment_building_versions=None,
        taxi_requirements=None,
):
    if not segment_id_list:
        raise ValueError('no segment ids passed, cannot build waybill')
    if segment_building_versions is None:
        segment_building_versions = {}

    all_points = []
    segversions = {}
    for segment_id in segment_id_list:
        if segment_id in segversions:
            raise ValueError('segment %s passed twice' % segment_id)

    for idx in range(4):
        for segment_id in segment_id_list:
            seginfo = await get_segment_info(segment_id)
            dispatch = seginfo['dispatch']
            segversions[segment_id] = segment_building_versions.get(
                segment_id, dispatch['waybill_building_version'],
            )
            segpoint = seginfo['segment']['points'][idx]
            obj = {'segment_id': segment_id, 'point_id': segpoint['point_id']}
            all_points.append(obj)

    proposal = {'segments': [], 'points': []}

    for segment_id, waybill_building_version in segversions.items():
        segment_info = {
            'segment_id': segment_id,
            'waybill_building_version': waybill_building_version,
        }
        proposal['segments'].append(segment_info)

    for (visit_order, obj) in enumerate(all_points, start=1):
        obj['visit_order'] = visit_order
        proposal['points'].append(obj)

    proposal['taxi_order_requirements'] = {
        'taxi_classes': ['express', 'courier'],
        'door_to_door': True,
    }

    if taxi_requirements:
        proposal['taxi_order_requirements'].update(taxi_requirements)

    return proposal


@pytest.fixture(name='get_point_execution_by_visit_order')
async def _get_point_execution_by_visit_order(
        taxi_cargo_dispatch, get_waybill_info,
):
    async def _wrapper(*, waybill_ref: str, visit_order: int):
        response = await get_waybill_info(waybill_ref)

        segment_point_id = next(
            p['point_id']
            for p in response.json()['waybill']['points']
            if p['visit_order'] == visit_order
        )

        point = next(
            p
            for p in response.json()['execution']['points']
            if p['point_id'] == segment_point_id
        )

        return point

    return _wrapper


@pytest.fixture(name='dispatch_return_point')
def _dispatch_return_point(
        taxi_cargo_dispatch,
        get_point_execution_by_visit_order,
        happy_path_claims_segment_db,
):
    async def _wrapper(
            waybill_external_ref: str,
            visit_order: int,
            comment: str = None,
            support: dict = None,
            driver_id: str = '789',
            async_timer_supported: bool = None,
            create_ticket: bool = False,
            **kwargs,
    ):
        point = await get_point_execution_by_visit_order(
            waybill_ref=waybill_external_ref, visit_order=visit_order,
        )
        claim_point_id = point['claim_point_id']
        segment_id = point['segment_id']

        request_body = {
            'last_known_status': 'pickup_confirmation',
            'point_id': claim_point_id,
            'performer_info': {
                'driver_id': driver_id,
                'park_id': 'park_id_1',
                'phone_pd_id': '+70000000000_id',
            },
            **kwargs,
        }
        if comment is not None:
            request_body['comment'] = comment
        if support:
            request_body['support'] = support
        if async_timer_supported:
            request_body[
                'async_timer_calculation_supported'
            ] = async_timer_supported
        request_body['need_create_ticket'] = create_ticket

        headers = {'Accept-Language': 'ru', 'X-Remote-Ip': '0.0.0.0'}
        if support:
            headers.pop('X-Remote-Ip')

        response = await taxi_cargo_dispatch.post(
            '/v1/waybill/return',
            params={'waybill_external_ref': waybill_external_ref},
            json=request_body,
            headers=headers,
        )

        if segment_id is not None:
            segment = happy_path_claims_segment_db.get_segment(segment_id)
            segment.set_point_visit_status(
                point['point_id'].split('_')[-1], 'skipped',
            )

        return response

    return _wrapper


@pytest.fixture(name='dispatch_confirm_point')
def _dispatch_confirm_point(
        taxi_cargo_dispatch,
        get_point_execution_by_visit_order,
        happy_path_claims_segment_db,
):
    async def _wrapper(
            waybill_external_ref: str,
            with_support: bool = False,
            visit_order: int = 1,
            *,
            driver_id: str = '789',
            async_timer_supported=None,
            last_known_status='pickup_confirmation',
    ):
        point = await get_point_execution_by_visit_order(
            waybill_ref=waybill_external_ref, visit_order=visit_order,
        )
        segment_id = point['segment_id']

        request_body = {
            'last_known_status': last_known_status,
            'confirmation_code': '123456',
            'point_id': point['claim_point_id'],
            'performer_info': {'driver_id': driver_id, 'park_id': 'park_id_1'},
        }
        if with_support:
            request_body['support'] = {
                'comment': 'some comment',
                'ticket': 'TICKET-100',
            }
        if async_timer_supported:
            request_body[
                'async_timer_calculation_supported'
            ] = async_timer_supported

        headers = {'Accept-Language': 'ru', 'X-Remote-Ip': '0.0.0.0'}
        if with_support:
            headers.pop('X-Remote-Ip')

        response = await taxi_cargo_dispatch.post(
            '/v1/waybill/exchange/confirm',
            params={'waybill_external_ref': waybill_external_ref},
            json=request_body,
            headers=headers,
        )

        segment = happy_path_claims_segment_db.get_segment(segment_id)
        segment.set_point_visit_status(
            point['point_id'].split('_')[-1], 'visited',
        )

        return response

    return _wrapper


@pytest.fixture
async def mark_performer_found(taxi_cargo_dispatch):
    async def _wrapper(
            waybill_ref,
            provider_order_id,
            *,
            chain_parent_cargo_order_id=None,
    ):
        request_body = {
            'waybill_id': waybill_ref,
            'order_id': str(uuid.uuid4()),
            'taxi_order_id': provider_order_id,
            'order_alias_id': '1234',
            'phone_pd_id': '+70000000000_id',
            'name': 'Kostya',
            'driver_id': '789',
            'park_id': 'park_id_1',
            'car_id': '123',
            'car_number': 'А001АА77',
            'car_model': 'KAMAZ',
            'lookup_version': 1,
        }
        if chain_parent_cargo_order_id is not None:
            request_body[
                'chain_parent_cargo_order_id'
            ] = chain_parent_cargo_order_id
        response = await taxi_cargo_dispatch.post(
            '/v1/waybill/mark/taxi-order-performer-found', json=request_body,
        )
        assert response.status_code == 200

    return _wrapper
