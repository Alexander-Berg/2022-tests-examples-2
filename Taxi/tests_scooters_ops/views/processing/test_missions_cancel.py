import pytest

from tests_scooters_ops import db_utils
from tests_scooters_ops import utils


HANDLER = '/scooters-ops/v1/processing/missions/cancel'


def pickup_batteries_job(*, job_status='planned', accumulator_status='booked'):
    return {
        'type': 'pickup_batteries',
        'status': job_status,
        'typed_extra': {
            'accumulators': [
                {
                    'ui_status': accumulator_status,
                    'booking_id': 'booking_id_1',
                },
            ],
        },
    }


def return_batteries_job(*, job_status='planned', cell_status='booked'):
    return {
        'type': 'return_batteries',
        'status': job_status,
        'typed_extra': {
            'cells': [
                {'ui_status': cell_status, 'booking_id': 'booking_id_2'},
            ],
        },
    }


@pytest.mark.parametrize(
    [
        'pickup_job',
        'return_job',
        'scooter_accumulator_code',
        'expected_response',
        'calls',
    ],
    [
        pytest.param(
            pickup_batteries_job(accumulator_status='pickuped'),
            return_batteries_job(cell_status='returned'),
            200,
            {
                'status': 200,
                'json': {
                    'mission': {
                        'status': 'cancelling',
                        'points': [
                            {
                                'status': 'cancelled',
                                'revision': 2,
                                'jobs': [
                                    {
                                        'type': 'pickup_batteries',
                                        'status': 'cancelled',
                                        'revision': 2,
                                    },
                                ],
                            },
                            {
                                'status': 'cancelled',
                                'revision': 2,
                                'jobs': [
                                    {
                                        'type': 'return_batteries',
                                        'status': 'cancelled',
                                        'revision': 2,
                                    },
                                ],
                            },
                        ],
                    },
                },
            },
            {'booking_unbook': 2},
            id='all accs returned',
        ),
        pytest.param(
            pickup_batteries_job(
                job_status='completed', accumulator_status='pickuped',
            ),
            return_batteries_job(cell_status='returned'),
            200,
            {
                'status': 200,
                'json': {
                    'mission': {
                        'status': 'cancelling',
                        'points': [
                            {
                                'status': 'cancelled',
                                'revision': 2,
                                'jobs': [
                                    {
                                        'type': 'pickup_batteries',
                                        'status': 'completed',
                                        'revision': 1,
                                    },
                                ],
                            },
                            {
                                'status': 'cancelled',
                                'revision': 2,
                                'jobs': [
                                    {
                                        'type': 'return_batteries',
                                        'status': 'cancelled',
                                        'revision': 2,
                                    },
                                ],
                            },
                        ],
                    },
                },
            },
            {'booking_unbook': 1},
            id='partially done',
        ),
        pytest.param(
            pickup_batteries_job(accumulator_status='pickuped'),
            return_batteries_job(cell_status='booked'),
            200,
            {
                'status': 400,
                'json': {
                    'code': 'has_pickuped_accumulators',
                    'message': (
                        'Mission has 1 pickuped accumulators and 0 returned'
                    ),
                },
            },
            {'booking_unbook': 0},
            id='not all returned',
        ),
        pytest.param(
            pickup_batteries_job(accumulator_status='booked'),
            return_batteries_job(cell_status='booked'),
            500,
            {'status': 400, 'json': {'code': 'cannot_unbook_accumulator'}},
            {'booking_unbook': 1},
            id='scooter-accumulator can not unbook',
        ),
        pytest.param(
            pickup_batteries_job(accumulator_status='booked'),
            return_batteries_job(cell_status='booked'),
            404,
            {
                'status': 200,
                'json': {
                    'mission': {
                        'status': 'cancelling',
                        'points': [
                            {
                                'status': 'cancelled',
                                'revision': 2,
                                'jobs': [
                                    {
                                        'type': 'pickup_batteries',
                                        'status': 'cancelled',
                                        'revision': 2,
                                    },
                                ],
                            },
                            {
                                'status': 'cancelled',
                                'revision': 2,
                                'jobs': [
                                    {
                                        'type': 'return_batteries',
                                        'status': 'cancelled',
                                        'revision': 2,
                                    },
                                ],
                            },
                        ],
                    },
                },
            },
            {'booking_unbook': 2},
            id='scooter-accumulator returns 404 for booking',
        ),
    ],
)
async def test_ok(
        taxi_scooters_ops,
        pgsql,
        mockserver,
        pickup_job,
        return_job,
        scooter_accumulator_code,
        expected_response,
        calls,
):
    db_utils.add_mission(
        pgsql,
        {
            'mission_id': 'mission_stub_id',
            'status': 'cancelling',
            'points': [
                {
                    'type': 'depot',
                    'typed_extra': {'depot': {'id': 'depot_stub_id'}},
                    'jobs': [pickup_job],
                },
                {
                    'type': 'depot',
                    'typed_extra': {'depot': {'id': 'depot_stub_id'}},
                    'jobs': [return_job],
                },
            ],
        },
    )

    @mockserver.json_handler(
        '/scooter-accumulator/scooter-accumulator/v1/cabinet/booking/unbook',
    )
    def _mock_booking_unbook(request):
        return mockserver.make_response(
            status=scooter_accumulator_code,
            json={
                'code': '404',
                'message': 'cabinet by booking_id was not found',
            },
        )

    resp = await taxi_scooters_ops.post(
        HANDLER,
        params={'mission_id': 'mission_stub_id', 'mission_revision': 1},
    )

    assert resp.status == expected_response['status']
    utils.assert_partial_diff(resp.json(), expected_response['json'])

    assert _mock_booking_unbook.times_called == calls.get('booking_unbook', 0)


async def test_idempotent(taxi_scooters_ops, pgsql, mockserver):
    db_utils.add_mission(
        pgsql,
        {
            'mission_id': 'mission_stub_id',
            'status': 'cancelling',
            'points': [
                {
                    'type': 'depot',
                    'typed_extra': {'depot': {'id': 'depot_stub_id'}},
                    'jobs': [pickup_batteries_job()],
                },
                {
                    'type': 'depot',
                    'typed_extra': {'depot': {'id': 'depot_stub_id'}},
                    'jobs': [return_batteries_job()],
                },
            ],
        },
    )

    @mockserver.json_handler(
        '/scooter-accumulator/scooter-accumulator/v1/cabinet/booking/unbook',
    )
    def _mock_booking_unbook(request):
        return {}

    for _ in range(2):
        resp = await taxi_scooters_ops.post(
            HANDLER,
            params={'mission_id': 'mission_stub_id', 'mission_revision': 1},
        )
        assert resp.status == 200
        utils.assert_partial_diff(
            resp.json(),
            {
                'mission': {
                    'status': 'cancelling',
                    'points': [
                        {
                            'status': 'cancelled',
                            'revision': 2,
                            'jobs': [
                                {
                                    'type': 'pickup_batteries',
                                    'status': 'cancelled',
                                    'revision': 2,
                                },
                            ],
                        },
                        {
                            'status': 'cancelled',
                            'revision': 2,
                            'jobs': [
                                {
                                    'type': 'return_batteries',
                                    'status': 'cancelled',
                                    'revision': 2,
                                },
                            ],
                        },
                    ],
                },
            },
        )

    assert _mock_booking_unbook.times_called == 2


async def test_not_found(taxi_scooters_ops):
    resp = await taxi_scooters_ops.post(
        HANDLER,
        params={'mission_id': 'mission_stub_id', 'mission_revision': 1},
    )

    assert resp.status == 404
    assert resp.json() == {'code': 'not-found', 'message': 'Mission not found'}


async def test_conflict(taxi_scooters_ops, pgsql):
    db_utils.add_mission(
        pgsql,
        {
            'mission_id': 'mission_stub_id',
            'revision': 10,
            'points': [
                {
                    'type': 'depot',
                    'typed_extra': {'depot_id': 'depot_stub_id'},
                },
                {
                    'type': 'scooter',
                    'typed_extra': {
                        'scooter': {
                            'id': 'scooter_stub_id',
                            'number': 'scooter_stub_number',
                        },
                    },
                },
            ],
        },
    )

    resp = await taxi_scooters_ops.post(
        HANDLER,
        params={'mission_id': 'mission_stub_id', 'mission_revision': 1},
    )

    assert resp.status == 409
    assert resp.json() == {
        'code': 'conflict',
        'message': 'Mission has revision: 10 but 1 requested',
    }


@pytest.mark.parametrize(
    'job_status,expects_released',
    [
        pytest.param('planned', True, id='job undone -> release'),
        pytest.param('completed', False, id='job completed -> do not release'),
        pytest.param('cancelled', True, id='job cancelled -> release'),
    ],
)
async def test_release_draft_by_job(
        taxi_scooters_ops, pgsql, job_status, expects_released,
):
    mission = db_utils.add_mission(
        pgsql,
        {
            'mission_id': 'mission_stub_id',
            'status': 'cancelling',
            'points': [
                {
                    'type': 'scooter',
                    'location': (35.4, 42.1),
                    'typed_extra': {'scooter': {'id': 'stub_vehicle_id'}},
                    'jobs': [
                        {
                            'type': 'battery_exchange',
                            'status': job_status,
                            'typed_extra': {'vehicle_id': 'stub_vehicle_id'},
                        },
                    ],
                },
            ],
        },
    )
    db_utils.add_draft(
        pgsql,
        {
            'draft_id': 'stub_draft_id',
            'type': 'recharge',
            'typed_extra': {'vehicle_id': 'stub_vehicle_id'},
            'mission_id': 'mission_stub_id',
            'job_id': mission['points'][0]['jobs'][0]['job_id'],
        },
    )

    resp = await taxi_scooters_ops.post(
        HANDLER,
        params={'mission_id': 'mission_stub_id', 'mission_revision': 1},
    )
    assert resp.status == 200

    draft_released = db_utils.get_drafts(
        pgsql, ids=['stub_draft_id'], fields=['mission_id'], flatten=True,
    ) == [None]

    assert draft_released is expects_released


@pytest.mark.parametrize(
    'point_status,expects_released',
    [
        pytest.param('planned', True, id='point undone -> release'),
        pytest.param('visited', False, id='point visited -> do not release'),
        pytest.param('skipped', True, id='point skipped -> release'),
    ],
)
async def test_release_draft_by_point(
        taxi_scooters_ops, pgsql, point_status, expects_released,
):
    mission = db_utils.add_mission(
        pgsql,
        {
            'mission_id': 'mission_stub_id',
            'status': 'cancelling',
            'points': [
                {
                    'type': 'scooter',
                    'location': (35.4, 42.1),
                    'typed_extra': {'scooter': {'id': 'stub_vehicle_id'}},
                    'status': point_status,
                    'jobs': [
                        {
                            'type': 'battery_exchange',
                            'status': 'completed',
                            'typed_extra': {'vehicle_id': 'stub_vehicle_id'},
                        },
                    ],
                },
            ],
        },
    )
    db_utils.add_draft(
        pgsql,
        {
            'draft_id': 'stub_draft_id',
            'type': 'recharge',
            'typed_extra': {'vehicle_id': 'stub_vehicle_id'},
            'mission_id': 'mission_stub_id',
            'point_id': mission['points'][0]['point_id'],
        },
    )

    resp = await taxi_scooters_ops.post(
        HANDLER,
        params={'mission_id': 'mission_stub_id', 'mission_revision': 1},
    )
    assert resp.status == 200

    draft_released = db_utils.get_drafts(
        pgsql, ids=['stub_draft_id'], fields=['mission_id'], flatten=True,
    ) == [None]

    assert draft_released is expects_released


async def test_release_draft_by_mission(taxi_scooters_ops, pgsql):
    db_utils.add_mission(
        pgsql,
        {
            'mission_id': 'mission_stub_id',
            'status': 'cancelling',
            'points': [
                {
                    'type': 'scooter',
                    'location': (35.4, 42.1),
                    'typed_extra': {'scooter': {'id': 'stub_vehicle_id'}},
                    'jobs': [
                        {
                            'type': 'battery_exchange',
                            'typed_extra': {'vehicle_id': 'stub_vehicle_id'},
                        },
                    ],
                },
            ],
        },
    )
    db_utils.add_draft(
        pgsql,
        {
            'draft_id': 'stub_draft_id',
            'type': 'recharge',
            'typed_extra': {'vehicle_id': 'stub_vehicle_id'},
            'mission_id': 'mission_stub_id',
        },
    )

    resp = await taxi_scooters_ops.post(
        HANDLER,
        params={'mission_id': 'mission_stub_id', 'mission_revision': 1},
    )
    assert resp.status == 200

    draft_released = db_utils.get_drafts(
        pgsql, ids=['stub_draft_id'], fields=['mission_id'], flatten=True,
    ) == [None]

    assert draft_released is True
