import pytest

from tests_scooters_ops import common
from tests_scooters_ops import db_utils
from tests_scooters_ops import utils


@common.TRANSLATIONS
@common.DEEPLINKS_CONFIG
@pytest.mark.parametrize(
    ['job_type', 'src_booking_status', 'dst_booking_status', 'cell_broken'],
    [
        pytest.param(
            'pickup_batteries',
            'booked',
            'failed',
            {
                'response': {
                    'status_code': 200,
                    'body': {'cell_id': 'cell_id123'},
                },
                'times_called': 1,
            },
        ),
        pytest.param(
            'pickup_batteries',
            'booked',
            'failed',
            {
                'response': {
                    'status_code': 400,
                    'body': {'message': 'cell has another error_code'},
                },
                'times_called': 1,
            },
        ),
        pytest.param(
            'pickup_batteries',
            'failed',
            'failed',
            {
                'response': {
                    'status_code': 200,
                    'body': {'cell_id': 'cell_id123'},
                },
                'times_called': 0,
            },
            id='pickup/test idempotency',
        ),
        pytest.param(
            'return_batteries',
            'returned',
            'failed',
            {
                'response': {
                    'status_code': 200,
                    'body': {'cell_id': 'cell_id123'},
                },
                'times_called': 1,
            },
        ),
        pytest.param(
            'return_batteries',
            'returned',
            'failed',
            {
                'response': {
                    'status_code': 404,
                    'body': {'message': 'no booking_id'},
                },
                'times_called': 1,
            },
        ),
        pytest.param(
            'return_batteries',
            'returned',
            'failed',
            {
                'response': {
                    'status_code': 500,
                    'body': {'message': 'internal service error'},
                },
                'times_called': 1,
            },
        ),
        pytest.param(
            'return_batteries',
            'failed',
            'failed',
            {
                'response': {
                    'status_code': 200,
                    'body': {'cell_id': 'cell_id123'},
                },
                'times_called': 0,
            },
            id='return/test idempotency',
        ),
    ],
)
async def test_handler(
        taxi_scooters_ops,
        pgsql,
        load_json,
        mockserver,
        job_type,
        src_booking_status,
        dst_booking_status,
        cell_broken,
):
    item_type = utils.extra_item_type_by_job_type(job_type)
    db_utils.add_job(
        pgsql,
        {
            'job_id': 'job_id',
            'type': job_type,
            'status': 'performing',
            'point_id': 'point_id',
            'order_at_point': 1,
            'typed_extra': {
                'quantity': 1,
                item_type: [
                    {
                        'booking_id': 'booking_id',
                        'cabinet_id': 'cabinet_id',
                        'cabinet_type': 'cabinet',
                        'cell_id': 'cell_id',
                        'ui_status': src_booking_status,
                    },
                ],
            },
        },
    )

    db_utils.add_point(
        pgsql,
        {
            'point_id': 'point_id',
            'cargo_point_id': 'cargo_point_id',
            'type': 'depot',
            'status': 'arrived',
            'location': (37, 55),
            'mission_id': 'mission_id',
            'order_in_mission': 1,
            'typed_extra': {'depot': {'id': 'depot_id'}},
        },
    )

    db_utils.add_mission(
        pgsql,
        {
            'mission_id': 'mission_id',
            'performer_id': 'performer_id',
            'status': 'performing',
        },
    )

    @mockserver.json_handler(
        '/scooter-accumulator/scooter-accumulator/v1'
        '/bookings/cell/set-error-code',
    )
    def mock_accumulator_cell_broken(request):
        return mockserver.make_response(
            status=cell_broken['response']['status_code'],
            json=cell_broken['response']['body'],
        )

    resp = await taxi_scooters_ops.post(
        '/driver/v1/scooters/v1/old-flow/screens/battery-exchange/broken',
        headers=common.DAP_HEADERS,
        params={
            'mission_id': 'mission_id',
            'cargo_point_id': 'cargo_point_id',
            'booking_id': 'booking_id',
            'job_type': job_type,
        },
    )

    assert resp.status == 200
    assert resp.json() == {
        'ui_items': load_json(f'job_type_{job_type}/response_ui.json'),
    }

    assert (
        mock_accumulator_cell_broken.times_called
        == cell_broken['times_called']
    )

    assert (
        db_utils.get_jobs(
            pgsql, ids=['job_id'], fields=['typed_extra'], flatten=True,
        )[0][item_type][0]['ui_status']
        == dst_booking_status
    )


@pytest.mark.parametrize(
    ['job_type', 'mission', 'error_message'],
    [
        pytest.param(
            'pickup_batteries',
            {
                'mission_id': 'mission_id',
                'status': 'assigning',
                'points': [
                    {
                        'point_id': 'point_id',
                        'cargo_point_id': 'cargo_point_id',
                        'type': 'depot',
                        'typed_extra': {'depot': {'id': 'depot_id'}},
                        'jobs': [
                            {
                                'job_id': 'job_id',
                                'type': 'pickup_batteries',
                                'typed_extra': {
                                    'quantity': 1,
                                    'accumulators': [
                                        {
                                            'booking_id': 'booking_id',
                                            'cabinet_type': 'cabinet',
                                            'cell_id': 'cell_id',
                                            'ui_status': 'failed',
                                        },
                                    ],
                                },
                            },
                        ],
                    },
                ],
            },
            'Mission is in incorrect state',
        ),
        pytest.param(
            'return_batteries',
            {
                'mission_id': 'mission_id',
                'status': 'performing',
                'points': [
                    {
                        'point_id': 'point_id',
                        'cargo_point_id': 'cargo_point_id',
                        'type': 'depot',
                        'typed_extra': {'depot': {'id': 'depot_id'}},
                        'jobs': [
                            {
                                'type': 'return_batteries',
                                'job_id': 'job_id',
                                'typed_extra': {
                                    'quantity': 1,
                                    'cells': [
                                        {
                                            'booking_id': 'booking_id',
                                            'cabinet_type': 'cabinet',
                                            'cell_id': 'cell_id',
                                            'ui_status': 'failed',
                                        },
                                    ],
                                },
                            },
                        ],
                    },
                ],
            },
            'Mission has no performer',
        ),
        pytest.param(
            'pickup_batteries',
            {
                'mission_id': 'mission_id',
                'status': 'performing',
                'performer_id': 'performer_id',
                'points': [
                    {
                        'point_id': 'point_id',
                        'cargo_point_id': 'cargo_point_id',
                        'type': 'depot',
                        'typed_extra': {'depot': {'id': 'depot_id'}},
                        'status': 'cancelled',
                        'jobs': [
                            {
                                'job_id': 'job_id',
                                'type': 'pickup_batteries',
                                'typed_extra': {
                                    'quantity': 1,
                                    'accumulators': [
                                        {
                                            'booking_id': 'booking_id',
                                            'cabinet_type': 'cabinet',
                                            'cell_id': 'cell_id',
                                            'ui_status': 'failed',
                                        },
                                    ],
                                },
                            },
                        ],
                    },
                ],
            },
            'Point is in incorrect state',
        ),
        pytest.param(
            'return_batteries',
            {
                'mission_id': 'mission_id',
                'status': 'performing',
                'performer_id': 'performer_id',
                'points': [
                    {
                        'point_id': 'point_id',
                        'cargo_point_id': 'cargo_point_id',
                        'type': 'depot',
                        'typed_extra': {'depot': {'id': 'depot_id'}},
                        'status': 'arrived',
                        'jobs': [
                            {
                                'status': 'completed',
                                'job_id': 'job_id',
                                'type': 'return_batteries',
                                'typed_extra': {
                                    'quantity': 1,
                                    'cells': [
                                        {
                                            'booking_id': 'booking_id',
                                            'cabinet_type': 'cabinet',
                                            'cell_id': 'cell_id',
                                            'ui_status': 'failed',
                                        },
                                    ],
                                },
                            },
                        ],
                    },
                ],
            },
            'Job is in incorrect state',
        ),
        pytest.param(
            'return_batteries',
            {
                'mission_id': 'mission_id',
                'status': 'performing',
                'performer_id': 'performer_id',
                'points': [
                    {
                        'point_id': 'point_id',
                        'cargo_point_id': 'cargo_point_id',
                        'type': 'depot',
                        'typed_extra': {'depot': {'id': 'depot_id'}},
                        'status': 'arrived',
                        'jobs': [
                            {
                                'status': 'performing',
                                'job_id': 'job_id',
                                'type': 'return_batteries',
                                'typed_extra': {
                                    'quantity': 1,
                                    'cells': [
                                        {
                                            'booking_id': 'booking_id',
                                            'cabinet_type': 'cabinet',
                                            'cell_id': 'cell_id',
                                            'ui_status': 'failed',
                                        },
                                    ],
                                },
                            },
                        ],
                    },
                ],
            },
            'Booking has no cabinet id',
        ),
    ],
)
async def test_validation(
        pgsql, taxi_scooters_ops, job_type, mission, error_message,
):
    db_utils.add_mission(pgsql, mission)

    resp = await taxi_scooters_ops.post(
        '/driver/v1/scooters/v1/old-flow/screens/battery-exchange/broken',
        headers=common.DAP_HEADERS,
        params={
            'mission_id': 'mission_id',
            'cargo_point_id': 'cargo_point_id',
            'booking_id': 'booking_id',
            'job_type': job_type,
        },
    )

    assert resp.status_code == 400
    assert resp.json() == {'code': '400', 'message': error_message}
