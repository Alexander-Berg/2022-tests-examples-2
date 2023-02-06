import copy

import pytest

from tests_scooters_ops import db_utils
from tests_scooters_ops import utils


HANDLER = '/scooters-ops/v1/processing/claim-updates/delivered_finish'

SIMPLE_MISSION = {
    'mission_id': 'mission_id',
    'cargo_claim_id': 'claim_1',
    'performer_id': 'performer_1',
    'status': 'performing',
    'revision': 1,
    'points': [
        {
            'point_id': 'point_1',
            'type': 'depot',
            'typed_extra': {'depot_id': 'depot1'},
            'status': 'visited',
            'jobs': [
                {
                    'job_id': 'job_1',
                    'type': 'pickup_batteries',
                    'status': 'completed',
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
            'point_id': 'point_2',
            'type': 'depot',
            'typed_extra': {'depot_id': 'depot1'},
            'status': 'visited',
            'jobs': [
                {
                    'job_id': 'job_2',
                    'type': 'return_batteries',
                    'status': 'completed',
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
    ['mission_status'],
    [
        pytest.param('performing', id='Mission completion'),
        pytest.param('completed', id='Mission already completed'),
    ],
)
async def test_ok(taxi_scooters_ops, pgsql, mockserver, mission_status):
    mission = copy.deepcopy(SIMPLE_MISSION)
    mission['status'] = mission_status

    db_utils.add_mission(pgsql, mission)

    @mockserver.json_handler('/processing/v1/scooters/missions/create-event')
    def mock_processing_create_event(request):
        assert request.headers['X-Idempotency-Token'] == 'completed-mission_id'
        assert request.json['kind'] == 'completed'
        assert request.json['mission']['id'] == 'mission_id'
        assert request.json['mission']['revision'] == 1
        return {'event_id': 'idontcare'}

    response = await taxi_scooters_ops.post(
        HANDLER, {}, params={'cargo_claim_id': 'claim_1'},
    )

    assert response.status == 200
    assert mock_processing_create_event.times_called == 1


async def test_idempotency(taxi_scooters_ops, pgsql, mockserver):
    db_utils.add_mission(pgsql, SIMPLE_MISSION)

    @mockserver.json_handler('/processing/v1/scooters/missions/create-event')
    def mock_processing_create_event(request):
        assert request.headers['X-Idempotency-Token'] == 'completed-mission_id'
        assert request.json['kind'] == 'completed'
        assert request.json['mission']['id'] == 'mission_id'
        assert request.json['mission']['revision'] == 1
        return {'event_id': 'idontcare'}

    response1 = await taxi_scooters_ops.post(
        HANDLER, {}, params={'cargo_claim_id': 'claim_1'},
    )
    response2 = await taxi_scooters_ops.post(
        HANDLER, {}, params={'cargo_claim_id': 'claim_1'},
    )

    assert response1.status == 200
    assert response2.status == 200

    # called twice, but its idempotent
    assert mock_processing_create_event.times_called == 2


async def test_not_found(taxi_scooters_ops):
    response = await taxi_scooters_ops.post(
        HANDLER,
        {'performer_id': 'performer_2'},
        params={'cargo_claim_id': 'absent_claim_id'},
    )

    assert response.status == 404
    assert response.json() == {
        'code': 'not-found',
        'message': 'Cannot find mission with cargo claim id: absent_claim_id',
    }


@pytest.mark.config(
    SCOOTERS_OPS_DRAFTS_SETTINGS_BY_TYPE={
        'recharge': {'unlock_tags': ['battery_low']},
    },
)
async def test_process_drafts(taxi_scooters_ops, pgsql, mockserver):
    mission = db_utils.add_mission(pgsql, SIMPLE_MISSION)
    db_utils.add_draft(
        pgsql,
        {
            'draft_id': 'mission_draft',
            'type': 'recharge',
            'typed_extra': {'vehicle_id': 'vehicle_id'},
            'mission_id': mission['mission_id'],
        },
    )
    db_utils.add_draft(
        pgsql,
        {
            'draft_id': 'point_draft',
            'type': 'recharge',
            'status': 'processed',
            'revision': 1,
            'typed_extra': {'vehicle_id': 'vehicle_id'},
            'mission_id': mission['mission_id'],
            'point_id': mission['points'][0]['point_id'],
        },
    )

    @mockserver.json_handler('/scooter-backend/api/taxi/car/tag_remove')
    def mock_tag_remove(request):
        assert request.json == {
            'object_ids': ['vehicle_id'],
            'tag_names': ['battery_low'],
        }
        return {}

    @mockserver.json_handler('/processing/v1/scooters/missions/create-event')
    def mock_processing_create_event(request):
        return {'event_id': 'idontcare'}

    response = await taxi_scooters_ops.post(
        HANDLER, {}, params={'cargo_claim_id': 'claim_1'},
    )

    assert response.status == 200
    assert mock_processing_create_event.times_called == 1
    assert mock_tag_remove.times_called == 1

    assert db_utils.get_draft(pgsql, 'mission_draft', fields=['status']) == {
        'status': 'processed',
    }
    assert db_utils.get_draft(
        pgsql, 'point_draft', fields=['status', 'revision'],
    ) == {'status': 'processed', 'revision': 1}


async def test_manually_finished(taxi_scooters_ops, pgsql, mockserver):
    mission = copy.deepcopy(SIMPLE_MISSION)
    mission['points'][0]['jobs'][0]['status'] = 'performing'
    mission['points'][1]['jobs'][0]['status'] = 'planned'
    mission['status'] = 'completed'

    db_utils.add_mission(pgsql, mission)

    @mockserver.json_handler('/processing/v1/scooters/missions/create-event')
    def mock_processing_create_event(request):
        assert request.headers['X-Idempotency-Token'] == 'completed-mission_id'
        assert request.json['kind'] == 'completed'
        assert request.json['mission']['id'] == 'mission_id'
        assert request.json['mission']['revision'] == 1
        return {'event_id': 'idontcare'}

    @mockserver.json_handler(
        '/scooter-accumulator/scooter-accumulator/v1/bookings',
    )
    def _mock_bookings(request):
        return {
            'bookings': [
                {
                    'booking_id': request.query['booking_ids'][0],
                    'status': 'REVOKED',
                    'cell_id': 'cell_id',
                    'cabinet_id': 'cabinet_id',
                    'cells_count': 1,
                    'cabinet_type': 'charge_station',
                },
                {
                    'booking_id': request.query['booking_ids'][1],
                    'status': 'IN_PROCESS',
                    'cell_id': 'cell_id2',
                    'cabinet_id': 'cabinet_id',
                    'cells_count': 1,
                    'cabinet_type': 'charge_station',
                },
            ],
        }

    @mockserver.json_handler(
        '/scooter-accumulator/scooter-accumulator/v1/cabinet/booking/unbook',
    )
    def _mock_booking_unbook(request):
        return {}

    response = await taxi_scooters_ops.post(
        HANDLER, {}, params={'cargo_claim_id': 'claim_1'},
    )

    assert response.status == 500
    assert mock_processing_create_event.times_called == 0

    notifications = db_utils.get_notifications(
        pgsql, mission_ids=['mission_id'],
    )
    assert notifications == [
        {
            'idempotency_token': 'mission_id___mission_completed_manually',
            'mission_id': 'mission_id',
            'point_id': '',
            'job_id': '',
            'type': 'mission_completed_manually',
            'completed': False,
            'recipients': {},
            'created_at': utils.AnyValue(),
            'updated_at': utils.AnyValue(),
        },
    ]
