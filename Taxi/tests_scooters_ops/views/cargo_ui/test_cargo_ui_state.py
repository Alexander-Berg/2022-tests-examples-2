import pytest


from tests_scooters_ops import common
from tests_scooters_ops import db_utils


HANDLER = '/driver/v1/scooters-ops/v1/cargo-ui/state'


def _create_mission(
        point_status=None,
        first_job_status=None,
        first_job_type=None,
        first_job_extra=None,
        second_job_status=None,
        second_job_type=None,
        second_job_extra=None,
):
    return {
        'mission_id': 'mission_id_1',
        'cargo_claim_id': 'claim_uuid_1',
        'performer_id': 'performer_1',
        'created_at': '2022-02-14T6:30:00+03',
        'points': [
            {
                'point_id': 'point_id1',
                'cargo_point_id': '2',
                'type': 'depot',
                'typed_extra': {'depot': {'id': 'depot1'}},
                'status': point_status or 'arrived',
                'eta': '2022-04-01T07:00:00+00:00',
                'address': 'Вот сюда надо приехать',
                'jobs': [
                    {
                        'job_id': 'job_id1',
                        'status': first_job_status or 'completed',
                        'type': first_job_type or 'do_nothing',
                        'expected_execution_time': '60 seconds',
                        'started_at': '2022-04-01T07:05:00+00:00',
                        'typed_extra': first_job_extra or {},
                    },
                    {
                        'job_id': 'job_id2',
                        'status': second_job_status or 'completed',
                        'type': second_job_type or 'do_nothing',
                        'expected_execution_time': '60 seconds',
                        'typed_extra': second_job_extra or {},
                    },
                ],
            },
        ],
    }


@common.DEEPLINKS_CONFIG
@common.TRANSLATIONS
@common.SCOOTERS_PROBLEMS_CONFIG
@pytest.mark.now('2022-02-14T12:00:00+03:00')
@pytest.mark.parametrize(
    'points_resolved_number, point_status, first_job_status, '
    'first_job_type, first_job_extra, response_json',
    [
        pytest.param(
            0,
            'planned',
            None,
            None,
            None,
            'to_point_screen.json',
            id='state_to_point_screen',
        ),
        pytest.param(
            0,
            'arrived',
            'performing',
            'pickup_vehicles',
            {
                'vehicles': [
                    {
                        'id': 'scooter_stub_id',
                        'number': '0001',
                        'status': 'problems',
                        'problems': ['not_found', 'discharged'],
                    },
                    {
                        'id': 'scooter_stub_id_1',
                        'number': '0002',
                        'status': 'processed',
                    },
                    {
                        'id': 'scooter_stub_id_2',
                        'number': '0003',
                        'status': 'pending',
                    },
                    {
                        'id': 'scooter_stub_id_3',
                        'number': '0004',
                        'status': 'problems',
                        'problems': ['didnt_open'],
                    },
                    {
                        'id': 'scooter_stub_id_4',
                        'number': '0005',
                        'status': 'problems',
                        'problems': ['discharged'],
                    },
                ],
            },
            'items_to_pickup_screen.json',
            id='state_pickup_items_screen',
        ),
        pytest.param(
            0,
            'arrived',
            'performing',
            'dropoff_vehicles',
            {
                'quantity': 4,
                'vehicles': [
                    {'id': 'veh_1', 'number': 'num_1', 'status': 'processed'},
                    {'id': 'veh_2', 'number': 'num_2', 'status': 'processed'},
                ],
                'vehicle_with_problems_ids': ['vehicle3'],
            },
            'items_to_dropoff_screen.json',
            id='state_dropoff_items_screen',
        ),
        pytest.param(
            2,
            'visited',
            None,
            None,
            None,
            'final_screen.json',
            id='state_final_screen',
        ),
    ],
)
async def test_cargo_ui_state_ok(
        taxi_scooters_ops,
        cargo_orders,
        load_json,
        pgsql,
        points_resolved_number,
        point_status,
        first_job_status,
        first_job_type,
        first_job_extra,
        response_json,
):
    for _ in range(points_resolved_number):
        cargo_orders.resolve_current_point_and_move()

    db_utils.add_mission(
        pgsql,
        _create_mission(
            point_status, first_job_status, first_job_type, first_job_extra,
        ),
    )

    response = await taxi_scooters_ops.post(
        HANDLER,
        headers=common.DAP_HEADERS,
        json={'cargo_ref_id': 'unique_cargo_ref_id'},
    )

    assert response.status == 200
    assert response.json() == load_json(response_json)


@common.DEEPLINKS_CONFIG
@common.TRANSLATIONS
async def test_cargo_ui_state_errors(taxi_scooters_ops, cargo_orders, pgsql):
    for _ in range(2):
        cargo_orders.resolve_current_point_and_move()

    db_utils.add_mission(pgsql, _create_mission('arrived'))

    response = await taxi_scooters_ops.post(
        HANDLER,
        headers=common.DAP_HEADERS,
        json={'cargo_ref_id': 'unique_cargo_ref_id'},
    )

    assert response.status == 500
