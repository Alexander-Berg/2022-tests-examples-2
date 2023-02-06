import pytest

from tests_scooters_ops import common
from tests_scooters_ops import db_utils
from tests_scooters_ops import utils
import tests_scooters_ops.views.cargo_ui.common as ui_common


HANDLER = '/driver/v1/scooters-ops/v1/cargo-ui/arrive_at_point'


def _create_mission(jobs):
    return {
        'mission_id': 'mission_id_1',
        'cargo_claim_id': 'claim_uuid_1',
        'performer_id': 'performer_1',
        'points': [
            {
                'point_id': 'point_id1',
                'cargo_point_id': '2',
                'type': 'depot',
                'typed_extra': {'depot': {'id': 'depot1'}},
                'status': 'planned',
                'jobs': jobs,
            },
        ],
    }


def _get_job_started_history(job_extra, job_type):
    return {
        'extra': {'job_extra': job_extra, 'job_type': job_type},
        'type': 'job_started',
    }


POINT_ARRIVED_HISTORY = {
    'extra': {'point_extra': {'depot': {'id': 'depot1'}}},
    'type': 'point_arrived',
}

REQUEST_BODY = {
    'cargo_ref_id': 'unique_cargo_ref_id',
    'last_known_status': 'pickup_confirmation',
    'point_id': 1,
    'location_data': {'a': []},
}


@common.DEEPLINKS_CONFIG
@common.TAGS_WITH_LOCK_CONFIG
@common.TRANSLATIONS
@common.SCOOTERS_PROBLEMS_CONFIG
@pytest.mark.now('2022-04-01T07:05:00+00:00')
@pytest.mark.parametrize(
    'job_type, typed_extra, response_json, new_typed_extra',
    [
        pytest.param(
            'pickup_vehicles',
            {
                'vehicles': [
                    {'id': 'vehicle_id1', 'number': '0001'},
                    {'id': 'vehicle_id2', 'number': '0002'},
                ],
            },
            'items_to_pickup_screen.json',
            {'vehicles': [{'status': 'pending'}, {'status': 'pending'}]},
            id='arrive_at_point_pickup_vehicles',
        ),
        pytest.param(
            'dropoff_vehicles',
            {'quantity': 2, 'vehicles': []},
            'items_to_dropoff_screen.json',
            {'quantity': 2, 'vehicles': []},
            id='arrive_at_point_dropoff_vehicles_no_problems',
        ),
        pytest.param(
            'dropoff_vehicles',
            {
                'quantity': 3,
                'vehicles': [],
                'vehicle_with_problems_ids': ['vehicle_id1'],
            },
            'items_to_dropoff_screen.json',
            {
                'quantity': 3,
                'vehicles': [],
                'vehicle_with_problems_ids': ['vehicle_id1'],
            },
            id='arrive_at_point_dropoff_vehicles_with_problems',
        ),
    ],
)
async def test_cargo_ui_arrive_at_point_ok(
        taxi_scooters_ops,
        cargo_orders,
        driver_trackstory,
        job_type,
        typed_extra,
        response_json,
        new_typed_extra,
        load_json,
        pgsql,
):
    jobs = [
        {
            'job_id': 'job_id1',
            'status': 'planned',
            'type': job_type,
            'expected_execution_time': '60 seconds',
            'typed_extra': typed_extra,
        },
    ]

    db_utils.add_mission(pgsql, _create_mission(jobs))

    response = await taxi_scooters_ops.post(
        HANDLER, headers=common.DAP_HEADERS, json=REQUEST_BODY,
    )

    assert response.status == 200
    assert ui_common.stabilize_response(response.json()) == load_json(
        response_json,
    )

    point = db_utils.get_points(pgsql, ids=['point_id1'], job_params={})[0]
    utils.assert_partial_diff(
        point,
        {
            'status': 'arrived',
            'arrival_time': utils.parse_timestring_aware(
                '2022-04-01T07:05:00+00:00',
            ),
            'jobs': [{'status': 'performing', 'typed_extra': new_typed_extra}],
        },
    )

    history = db_utils.get_history(pgsql, fields=['type', 'extra'])
    expected_history = [
        POINT_ARRIVED_HISTORY,
        _get_job_started_history(new_typed_extra, job_type),
    ]
    utils.assert_partial_diff(history, expected_history)

    assert driver_trackstory.driver_position.times_called == 1
    assert cargo_orders.get_order_info.times_called == 1
    assert cargo_orders.arrive_at_point.times_called == 1


@common.DEEPLINKS_CONFIG
@common.TAGS_WITH_LOCK_CONFIG
@common.TRANSLATIONS
@pytest.mark.now('2022-04-01T07:05:00+00:00')
@common.SCOOTERS_PROBLEMS_CONFIG
async def test_cargo_ui_arrive_at_point_idempotency(
        taxi_scooters_ops, load_json, cargo_orders, driver_trackstory, pgsql,
):
    jobs = [
        {
            'job_id': 'job_id1',
            'status': 'planned',
            'type': 'dropoff_vehicles',
            'expected_execution_time': '60 seconds',
            'typed_extra': {'quantity': 2, 'vehicles': []},
        },
    ]

    db_utils.add_mission(pgsql, _create_mission(jobs))

    response = await taxi_scooters_ops.post(
        HANDLER, headers=common.DAP_HEADERS, json=REQUEST_BODY,
    )

    assert response.status == 200

    response = await taxi_scooters_ops.post(
        HANDLER, headers=common.DAP_HEADERS, json=REQUEST_BODY,
    )

    assert response.status == 200
    assert ui_common.stabilize_response(response.json()) == load_json(
        'items_to_dropoff_screen.json',
    )

    point = db_utils.get_points(pgsql, ids=['point_id1'], job_params={})[0]
    utils.assert_partial_diff(
        point,
        {
            'status': 'arrived',
            'arrival_time': utils.parse_timestring_aware(
                '2022-04-01T07:05:00+00:00',
            ),
            'jobs': [
                {
                    'status': 'performing',
                    'typed_extra': {'quantity': 2, 'vehicles': []},
                },
            ],
        },
    )

    expected_history = [
        POINT_ARRIVED_HISTORY,
        _get_job_started_history(
            {'quantity': 2, 'vehicles': []}, 'dropoff_vehicles',
        ),
    ]
    history = db_utils.get_history(pgsql, fields=['type', 'extra'])
    utils.assert_partial_diff(history, expected_history)

    assert driver_trackstory.driver_position.times_called == 1
    assert cargo_orders.get_order_info.times_called == 2
    assert cargo_orders.arrive_at_point.times_called == 1


@common.DEEPLINKS_CONFIG
@common.TRANSLATIONS
@pytest.mark.now('2022-02-14T12:00:00+03')
@pytest.mark.parametrize(
    'points_resolved_number, job_statuses, error_code, expected_json',
    [
        pytest.param(
            2,
            [],
            400,
            {'code': 'BAD_REQUEST', 'message': 'No unresolved points'},
            id='no_unresolved_points',
        ),
        pytest.param(
            0,
            ['completed'],
            400,
            {
                'code': 'BAD_REQUEST',
                'message': (
                    'The first job job_id0 at the point '
                    'point_id1 has already been finished'
                ),
            },
            id='the_only_job_is_already_completed',
        ),
        pytest.param(
            0,
            ['completed', 'planned'],
            400,
            {
                'code': 'BAD_REQUEST',
                'message': (
                    'The first job job_id0 at the point '
                    'point_id1 has already been finished'
                ),
            },
            id='some_jobs_are_already_completed',
        ),
        pytest.param(
            1,
            [],
            500,
            {'code': '500', 'message': 'Internal Server Error'},
            id='no_point_for_cargo_point_id',
        ),
    ],
)
async def test_cargo_ui_arrive_at_point_errors(
        taxi_scooters_ops,
        pgsql,
        cargo_orders,
        driver_trackstory,
        points_resolved_number,
        job_statuses,
        error_code,
        expected_json,
):
    for _ in range(points_resolved_number):
        cargo_orders.resolve_current_point_and_move()

    jobs = [
        {
            'job_id': f'job_id{id}',
            'status': job_status,
            'type': 'dropoff_vehicles',
            'expected_execution_time': '60 seconds',
            'typed_extra': {'quantity': 1, 'vehicles': []},
        }
        for id, job_status in enumerate(job_statuses)
    ]

    db_utils.add_mission(pgsql, _create_mission(jobs))

    response = await taxi_scooters_ops.post(
        HANDLER, headers=common.DAP_HEADERS, json=REQUEST_BODY,
    )

    assert response.status == error_code
    assert response.json() == expected_json
