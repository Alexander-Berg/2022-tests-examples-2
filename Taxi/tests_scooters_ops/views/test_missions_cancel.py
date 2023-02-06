import copy

import pytest

from tests_scooters_ops import db_utils


HANDLER = '/scooters-ops/v1/missions/cancel'
SIMPLE_MISSION = {
    'mission_id': 'mission_id',
    'cargo_claim_id': 'claim_1',
    'performer_id': 'performer_2',
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


@pytest.mark.parametrize(
    'params,expected_response,calls',
    [
        pytest.param(
            {'cargo_claim_id': 'claim_1', 'intent': 'processing'},
            {'status': 200, 'json': None},
            {'processing_create_event': 1},
            id='processing intent, ok',
        ),
        pytest.param(
            {'mission_id': 'mission_id', 'intent': 'processing'},
            {'status': 200, 'json': None},
            {'processing_create_event': 1},
            id='processing intent by mission_id',
        ),
        pytest.param(
            {'mission_id': 'absent', 'intent': 'processing'},
            {
                'status': 404,
                'json': {
                    'code': 'not-found',
                    'message': 'Cannot find mission',
                },
            },
            {},
            id='processing intent mission not found',
        ),
        pytest.param(
            {'mission_id': 'absent', 'intent': 'admin'},
            {
                'status': 400,
                'json': {
                    'code': 'bad-request',
                    'message': (
                        'Cancelling is disabled for intent: '
                        'admin. See: SCOOTERDEV-808'
                    ),
                },
            },
            {},
            id='disabled for admin intent',
        ),
        pytest.param(
            {'intent': 'processing'},
            {
                'status': 400,
                'json': {
                    'code': 'bad-request',
                    'message': (
                        'One of: mission_id, cargo_claim_id required. '
                        'Got nothing'
                    ),
                },
            },
            {},
            id='without params',
        ),
        pytest.param(
            {
                'intent': 'processing',
                'mission_id': 'absent',
                'cargo_claim_id': 'claim_1',
            },
            {
                'status': 400,
                'json': {
                    'code': 'bad-request',
                    'message': (
                        'One of: mission_id, cargo_claim_id allowed. Got both'
                    ),
                },
            },
            {},
            id='without params',
        ),
    ],
)
async def test_handler(
        taxi_scooters_ops, pgsql, mockserver, params, expected_response, calls,
):
    db_utils.add_mission(pgsql, copy.deepcopy(SIMPLE_MISSION))

    @mockserver.json_handler('/processing/v1/scooters/missions/create-event')
    def mock_processing_create_event(request):
        assert (
            request.headers['X-Idempotency-Token'] == 'cancelling-mission_id'
        )
        assert request.json['mission']['id'] == 'mission_id'
        return {'event_id': 'idontcare'}

    response = await taxi_scooters_ops.post(HANDLER, {}, params=params)

    assert response.status == expected_response['status']
    if expected_response['json']:
        assert response.json() == expected_response['json']

    assert mock_processing_create_event.times_called == calls.get(
        'processing_create_event', 0,
    )


async def test_idempotency(taxi_scooters_ops, pgsql, mockserver):
    db_utils.add_mission(pgsql, copy.deepcopy(SIMPLE_MISSION))

    @mockserver.json_handler('/processing/v1/scooters/missions/create-event')
    def mock_processing_create_event(request):
        assert (
            request.headers['X-Idempotency-Token'] == 'cancelling-mission_id'
        )
        assert request.json['mission']['id'] == 'mission_id'
        return {'event_id': 'idontcare'}

    request_params = {'cargo_claim_id': 'claim_1', 'intent': 'processing'}

    for _ in range(2):
        resp = await taxi_scooters_ops.post(HANDLER, {}, params=request_params)
        assert resp.status == 200

    assert (
        mock_processing_create_event.times_called == 2
    )  # called twice, but its idempotent by itself
