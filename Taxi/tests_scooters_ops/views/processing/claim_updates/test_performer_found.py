import copy

import pytest

from tests_scooters_ops import db_utils


@pytest.fixture(name='mock_scooter_accumulator_set_performer')
def _mock_scooter_accumulator_set_performer(mockserver):
    def wrapped(contractor='', bookings=None):
        @mockserver.json_handler(
            '/scooter-accumulator/scooter-accumulator/'
            'v1/cabinet/booking/contractor',
        )
        def set_performer(request):
            assert request.query['contractor_id'] == contractor
            assert request.query['booking_id'] in bookings
            bookings.remove(request.query['booking_id'])
            return {}

        return set_performer

    return wrapped


HANDLER = '/scooters-ops/v1/processing/claim-updates/performer_found'
SIMPLE_MISSION = {
    'mission_id': 'mission_id',
    'performer_id': 'performer_2',
    'cargo_claim_id': 'claim_1',
    'status': 'assigning',
    'revision': 1,
    'points': [
        {
            'point_id': 'point_1',
            'type': 'depot',
            'typed_extra': {'depot_id': 'depot1'},
            'status': 'prepared',
            'jobs': [
                {
                    'job_id': 'job_1',
                    'type': 'pickup_batteries',
                    'status': 'prepared',
                    'typed_extra': {
                        'accumulators': [
                            {'booking_id': 'book_1', 'ui_status': 'booked'},
                            {'booking_id': 'book_2', 'ui_status': 'booked'},
                        ],
                    },
                },
            ],
        },
        {
            'type': 'depot',
            'typed_extra': {'depot_id': 'depot1'},
            'status': 'prepared',
            'jobs': [
                {
                    'type': 'return_batteries',
                    'status': 'prepared',
                    'typed_extra': {
                        'cells': [
                            {'booking_id': 'book_3', 'ui_status': 'booked'},
                            {'booking_id': 'book_4', 'ui_status': 'booked'},
                        ],
                    },
                },
            ],
        },
    ],
}


async def test_ok(
        taxi_scooters_ops,
        pgsql,
        mockserver,
        mock_scooter_accumulator_set_performer,
):
    db_utils.add_mission(pgsql, copy.deepcopy(SIMPLE_MISSION))
    mock_scooter_accumulator_set_performer = (
        mock_scooter_accumulator_set_performer(
            'performer_2', ['book_1', 'book_2'],
        )
    )

    @mockserver.json_handler('/processing/v1/scooters/missions/create-event')
    def mock_processing_create_event(request):
        assert (
            request.headers['X-Idempotency-Token']
            == 'performing-mission_id-performer_2'
        )
        assert request.json['kind'] == 'performing'
        assert request.json['mission']['id'] == 'mission_id'
        assert request.json['mission']['revision'] == 2
        return {'event_id': 'idontcare'}

    response = await taxi_scooters_ops.post(
        HANDLER,
        {'performer_id': 'performer_2'},
        params={'cargo_claim_id': 'claim_1'},
    )

    assert response.status == 200
    assert mock_scooter_accumulator_set_performer.times_called == 2
    assert mock_processing_create_event.times_called == 1

    mission = db_utils.get_missions(
        pgsql, ids=['mission_id'], point_params={'job_params': {}},
    )[0]
    assert mission['performer_id'] == 'performer_2'
    assert mission['revision'] == 2
    assert [point['status'] for point in mission['points']] == [
        'planned',
        'planned',
    ]
    jobs = [job for point in mission['points'] for job in point['jobs']]
    assert [job['status'] for job in jobs] == ['planned', 'planned']


async def test_idempotency(
        taxi_scooters_ops,
        pgsql,
        mockserver,
        mock_scooter_accumulator_set_performer,
):
    db_utils.add_mission(pgsql, copy.deepcopy(SIMPLE_MISSION))
    mock_scooter_accumulator_set_performer = (
        mock_scooter_accumulator_set_performer(
            'performer_2', ['book_1', 'book_2'],
        )
    )

    @mockserver.json_handler('/processing/v1/scooters/missions/create-event')
    def mock_processing_create_event(request):
        assert (
            request.headers['X-Idempotency-Token']
            == 'performing-mission_id-performer_2'
        )
        assert request.json['kind'] == 'performing'
        assert request.json['mission']['id'] == 'mission_id'
        assert request.json['mission']['revision'] == 2
        return {'event_id': 'idontcare'}

    response1 = await taxi_scooters_ops.post(
        HANDLER,
        {'performer_id': 'performer_2'},
        params={'cargo_claim_id': 'claim_1'},
    )
    assert response1.status == 200

    response2 = await taxi_scooters_ops.post(
        HANDLER,
        {'performer_id': 'performer_2'},
        params={'cargo_claim_id': 'claim_1'},
    )
    assert response2.status == 200

    assert mock_scooter_accumulator_set_performer.times_called == 2
    assert mock_processing_create_event.times_called == 1
    assert db_utils.get_missions(
        pgsql, ids=['mission_id'], fields=['performer_id', 'revision'],
    ) == [{'performer_id': 'performer_2', 'revision': 2}]


async def test_not_found(taxi_scooters_ops):
    response = await taxi_scooters_ops.post(
        HANDLER,
        {'performer_id': 'performer_2'},
        params={'cargo_claim_id': 'absent_cargo_claim_id'},
    )

    assert response.status == 404
    assert response.json() == {
        'code': 'not-found',
        'message': (
            'Cannot find mission with cargo claim id: absent_cargo_claim_id'
        ),
    }


@pytest.mark.parametrize(
    ['incorrect_entity', 'expected_message'],
    [
        pytest.param(
            'job', 'Job: job_1 isnot prepared yet', id='Job isnot prepared',
        ),
        pytest.param(
            'point',
            'Point: point_1 isnot prepared yet',
            id='Point isnot prepared',
        ),
    ],
)
async def test_conflict(
        taxi_scooters_ops, pgsql, incorrect_entity, expected_message,
):
    mission = copy.deepcopy(SIMPLE_MISSION)
    if incorrect_entity == 'job':
        mission['points'][0]['jobs'][0]['status'] = 'created'
    elif incorrect_entity == 'point':
        mission['points'][0]['status'] = 'created'
    db_utils.add_mission(pgsql, mission)

    response = await taxi_scooters_ops.post(
        HANDLER,
        {'performer_id': 'performer_2'},
        params={'cargo_claim_id': 'claim_1'},
    )

    assert response.status == 409
    assert response.json() == {'code': 'conflict', 'message': expected_message}


async def test_another_performer(taxi_scooters_ops, pgsql):
    mission = copy.deepcopy(SIMPLE_MISSION)
    mission['performer_id'] = 'performer_1'
    db_utils.add_mission(pgsql, mission)

    response = await taxi_scooters_ops.post(
        HANDLER,
        {'performer_id': 'performer_2'},
        params={'cargo_claim_id': 'claim_1'},
    )

    assert response.status == 409
    assert response.json() == {
        'code': 'conflict',
        'message': (
            'Trying to set another performer(performer_2) for '
            'mission: mission_id; old performer: performer_1'
        ),
    }
