# pylint: disable=redefined-outer-name
import collections
import copy
import datetime

import pytest

from . import cargo_dispatch_manager


@pytest.fixture
def mock_segment_dispatch_journal(
        mockserver, cargo_dispatch: cargo_dispatch_manager.CargoDispatch,
):
    @mockserver.json_handler('/cargo-dispatch/v1/segment/dispatch-journal')
    def mock_dispatch_journal(request):
        events, cursor = cargo_dispatch.segments.read_journal(
            request.json.get('cursor'),
        )
        return mockserver.make_response(
            headers={'X-Polling-Delay-Ms': '0'},
            json={'cursor': cursor, 'events': events},
        )

    return mock_dispatch_journal


@pytest.fixture
def mock_waybill_dispatch_journal(
        mockserver, cargo_dispatch: cargo_dispatch_manager.CargoDispatch,
):
    @mockserver.json_handler('/cargo-dispatch/v1/waybill/dispatch-journal')
    def mock_dispatch_journal(request):
        events, cursor = cargo_dispatch.waybills.read_journal(
            request.json.get('cursor'),
        )
        return mockserver.make_response(
            headers={'X-Polling-Delay-Ms': '0'},
            json={'cursor': cursor, 'events': events},
        )

    return mock_dispatch_journal


@pytest.fixture
def mock_dispatch_segment_info(
        mockserver,
        segment_builder,
        cargo_dispatch: cargo_dispatch_manager.CargoDispatch,
):
    @mockserver.json_handler('/cargo-dispatch/v1/segment/info')
    def mock_segment_info(request):
        segment_id = request.args['segment_id']
        segment = cargo_dispatch.get_segment(segment_id)
        if segment is None:
            return mockserver.make_response(
                status=404,
                json={'code': 'not found', 'message': 'segment not found'},
            )
        return segment_builder(segment)

    return mock_segment_info


@pytest.fixture
def mock_dispatch_waybill_info(
        mockserver,
        waybill_builder,
        cargo_dispatch: cargo_dispatch_manager.CargoDispatch,
):
    @mockserver.json_handler('/cargo-dispatch/v1/waybill/info')
    def mock(request):
        waybill_ref = request.args['waybill_external_ref']

        waybill = cargo_dispatch.get_waybill(waybill_ref=waybill_ref)
        if waybill is None:
            return mockserver.make_response(
                status=404,
                json={'code': 'not found', 'message': 'waybill not found'},
            )
        return waybill_builder(waybill)

    return mock


@pytest.fixture
def mock_cargo_dispatch_waybill_ref(
        mockserver, cargo_dispatch: cargo_dispatch_manager.CargoDispatch,
):
    @mockserver.json_handler('/cargo-dispatch/v1/waybill/find-ref')
    def _wrapper(request):
        waybill = cargo_dispatch.get_waybill(
            taxi_order_id=request.json['taxi_order_id'],
        )
        if waybill:
            return {'waybill_external_ref': waybill.id}
        return mockserver.make_response(
            status=404,
            json={
                'code': 'unknown_waybill',
                'message': 'no waybill with such taxi_order_id known yet',
            },
        )

    return _wrapper


@pytest.fixture
def cargo_dispatch_propose(
        cargo_dispatch: cargo_dispatch_manager.CargoDispatch,
):
    def _check_path_valid(path):
        visit_order = collections.defaultdict(int)
        for point in path:
            if visit_order[point['segment_id']] >= point['visit_order']:
                raise RuntimeError(
                    f'Incorrect visit order of point {point["point_id"]}',
                )
            visit_order[point['segment_id']] = point['visit_order']

    def proposition_checker(proposition):
        segment_points = set()
        for seg in proposition['segments']:
            segment_id = seg['segment_id']
            waybill_building_version = seg['waybill_building_version']
            segment = cargo_dispatch.get_segment(segment_id)
            if segment is None:
                raise RuntimeError(
                    f'Proposition reference to unknown segment {segment_id}',
                )
            if segment.waybill_building_version != waybill_building_version:
                raise RuntimeError(
                    f'waybill_building_version on proposition differs',
                )
            for point in segment.points:
                segment_points.add((segment_id, point.point_id))

        points = set()
        for point in proposition['points']:
            segment_id = point['segment_id']
            point_id = point['point_id']
            key = segment_id, point_id
            if key not in segment_points:
                raise RuntimeError(f'Reference to unknown point {key}')
            if key in points:
                raise RuntimeError(f'Multiple refrences to point {key}')
            points.add(key)

        _check_path_valid(proposition['points'])

        assert (
            segment_points == points
        ), 'Proposition points does not match segments'

    def register_proposition(proposition, *, initial_waybill_status):
        # build waybill/info by waybill/propose proposition
        segments = []
        for segment_record in proposition['segments']:
            segment = cargo_dispatch.get_segment(segment_record['segment_id'])
            assert segment is not None, 'Proposed unknown segment {}'.format(
                segment_record,
            )
            segments.append(segment)
        points = []
        for point in proposition['points']:
            point_added = False
            for segment in segments:
                if point['segment_id'] != segment.id:
                    continue
                for segment_point in segment.points:
                    if segment_point.point_id != point['point_id']:
                        continue
                    points.append(segment_point)
                    point_added = True
                    break
                break
            assert point_added, (
                f'point not found in proposed segments, '
                f'point: {point}, segments: {segments}'
            )

        taxi_order_requirements = copy.deepcopy(
            proposition['taxi_order_requirements'],
        )
        taxi_classes = taxi_order_requirements.pop('taxi_classes')

        waybill = cargo_dispatch_manager.Waybill(
            id=proposition['external_ref'],
            taxi_classes=taxi_classes,
            taxi_requirements=taxi_order_requirements,
            revision=1,
            special_requirements=proposition['special_requirements'],
            segments=segments,
            points=points,
        )
        if initial_waybill_status is not None:
            waybill.status = initial_waybill_status

        cargo_dispatch.add_waybill(waybill)

    def wrapper(proposition, initial_waybill_status=None):
        proposition_checker(proposition)
        register_proposition(
            proposition, initial_waybill_status=initial_waybill_status,
        )

    return wrapper


@pytest.fixture
def mock_waybill_propose(
        mockserver,
        propositions_manager: cargo_dispatch_manager.PropositionsManager,
        cargo_dispatch_propose,
):
    @mockserver.json_handler('/cargo-dispatch/v1/waybill/propose')
    def mock_propose(request):
        cargo_dispatch_propose(request.json)
        propositions_manager.add_propositon(request.json)

        return {}

    return mock_propose


@pytest.fixture
def mock_update_proposition(
        mockserver,
        propositions_manager: cargo_dispatch_manager.PropositionsManager,
        cargo_dispatch_propose,
):
    @mockserver.json_handler('/cargo-dispatch/v1/waybill/update-proposition')
    def mock(request):
        proposition = request.json['proposition']
        cargo_dispatch_propose(
            proposition, initial_waybill_status='driver_approval_awaited',
        )
        propositions_manager.add_live_proposition(
            request.json['updated_waybill_ref'], proposition,
        )

        return {}

    return mock


def _parse_datetime(date_string: str) -> datetime.datetime:
    try:
        return datetime.datetime.strptime(
            date_string, '%Y-%m-%dT%H:%M:%S.%f%z',
        )
    except ValueError:
        return datetime.datetime.strptime(date_string, '%Y-%m-%dT%H:%M:%S%z')


def _to_string(whatever):
    if whatever is None:
        return None
    if isinstance(whatever, datetime.datetime):
        return whatever.strftime('%Y-%m-%dT%H:%M:%S.%f%z')
    return str(whatever)


@pytest.fixture
def mock_eats_eta(mockserver, load_json_var):
    def wrapper(
            *,
            arrival_duration=200,
            arrival_distance=1000,
            delivery_duration=200,
            delivery_distance=1000,
            parking_duration=100,
            pickup_duration=100,
            dropoff_duration=100,
            return_duration=100,
    ):
        @mockserver.json_handler('/eats-eta/v1/eta/routes/estimate')
        def do_mock_eats_eta(request):
            route = request.json['routes'][0]
            action_points = route['action_points']
            initial_time = _parse_datetime(route['initial_time'])
            arrival_at = initial_time + datetime.timedelta(
                seconds=arrival_duration,
            )
            pickup_point_finish_parking_at = arrival_at + datetime.timedelta(
                seconds=parking_duration,
            )
            if 'executable_since' in action_points[0]:
                pickup_starts_at = max(
                    pickup_point_finish_parking_at,
                    _parse_datetime(action_points[0]['exeсutable_since']),
                )
            else:
                pickup_starts_at = pickup_point_finish_parking_at
            waiting_duration = (
                pickup_starts_at - pickup_point_finish_parking_at
            )
            delivery_starts_at = pickup_starts_at + datetime.timedelta(
                seconds=pickup_duration,
            )
            delivery_arrived_at = delivery_starts_at + datetime.timedelta(
                seconds=delivery_duration,
            )
            total_distance = arrival_distance + delivery_distance
            dropoff_finish_parking_at = (
                delivery_arrived_at
                + datetime.timedelta(seconds=parking_duration)
            )
            delivered_at = dropoff_finish_parking_at + datetime.timedelta(
                seconds=delivery_duration,
            )
            return_arrived_at = delivered_at + datetime.timedelta(
                seconds=delivery_duration,
            )
            distance_with_return = total_distance + delivery_distance
            return_finish_parking_at = return_arrived_at + datetime.timedelta(
                seconds=parking_duration,
            )
            returned_at = return_finish_parking_at + datetime.timedelta(
                seconds=return_duration,
            )
            variables = {
                'initial_time': _to_string(initial_time),
                'arrival_at': _to_string(arrival_at),
                'pickup_point_finish_parking_at': _to_string(
                    pickup_point_finish_parking_at,
                ),
                'pickup_starts_at': _to_string(pickup_starts_at),
                'delivery_starts_at': _to_string(delivery_starts_at),
                'delivery_arrived_at': _to_string(delivery_arrived_at),
                'dropoff_finish_parking_at': _to_string(
                    dropoff_finish_parking_at,
                ),
                'delivered_at': _to_string(delivered_at),
                'return_arrived_at': _to_string(return_arrived_at),
                'return_finish_parking_at': _to_string(
                    return_finish_parking_at,
                ),
                'returned_at': _to_string(returned_at),
                'initial_position': route['initial_courier_position'],
                'route_id': route['id'],
                'segment_id': action_points[0]['key']['segment_id'],
                'pickup_point_id': action_points[0]['key']['action_id'],
                'pickup_position': action_points[0]['position'],
                'dropoff_point_id': action_points[1]['key']['action_id'],
                'dropoff_position': action_points[1]['position'],
                'return_point_id': action_points[2]['key']['action_id'],
                'arrival_duration': arrival_duration,
                'arrival_distance': arrival_distance,
                'delivery_duration': delivery_duration,
                'delivery_distance': delivery_distance,
                'parking_duration': parking_duration,
                'pickup_duration': pickup_duration,
                'dropoff_duration': dropoff_duration,
                'return_duration': return_duration,
                'waiting_duration': waiting_duration.total_seconds(),
                'total_distance': total_distance,
                'distance_with_return': distance_with_return,
            }
            return {
                'routes_estimations': [
                    load_json_var(
                        'eats-eta/eats_eta_car_router_estimation.json',
                        **variables,
                    ),
                ],
            }

        return do_mock_eats_eta

    return wrapper
