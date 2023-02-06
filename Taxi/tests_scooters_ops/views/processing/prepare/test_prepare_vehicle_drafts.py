import pytest

from tests_scooters_ops import db_utils


HANDLER = '/scooters-ops/v1/processing/missions/prepare'


@pytest.mark.config(
    SCOOTERS_OPS_DRAFTS_SETTINGS_BY_TYPE={
        'pickup_vehicle': {
            'lock_tags': ['lockme'],
            'lock_on': 'mission_preparing',
        },
        'dropoff_vehicles': {},
    },
)
async def test_ok(taxi_scooters_ops, pgsql, mockserver, load_json, yamaps):
    db_utils.add_mission(
        pgsql,
        {
            'status': 'preparing',
            'mission_id': 'mission_stub_id',
            'revision': 2,
            'points': [
                {
                    'type': 'depot',
                    'typed_extra': {'depot': {'id': 'depot_stub_id'}},
                    'jobs': [{'type': 'do_nothing', 'typed_extra': {}}],
                },
                {
                    'type': 'scooter',
                    'typed_extra': {'scooter': {'id': 'scooter_stub_id_1'}},
                    'jobs': [{'type': 'do_nothing', 'typed_extra': {}}],
                },
            ],
        },
    )

    db_utils.add_draft(
        pgsql,
        {
            'draft_id': 'draft_01',
            'type': 'pickup_vehicle',
            'typed_extra': {'vehicle_id': 'scooter_stub_id_1', 'score': 1},
            'mission_id': 'mission_stub_id',
        },
    )

    db_utils.add_draft(
        pgsql,
        {
            'draft_id': 'draft_02',
            'type': 'dropoff_vehicles',
            'typed_extra': {
                'point_id': 'lala',
                'point_type': 'parking_place',
                'location': (37, 55),
                'dropoff': 1,
                'score': 1,
            },
            'mission_id': 'mission_stub_id',
            # This draft will be prepared first because GetMissionDrafts
            # order drafts by created_at ASC
            'created_at': '2000-01-01T14:00:00.00000+00:00',
        },
    )

    @mockserver.json_handler('/scooters-misc/scooters-misc/v1/areas')
    async def _areas(request):
        return {'areas': []}

    @mockserver.json_handler('/scooter-backend/api/taxi/car/details')
    async def mock_car_details(request):
        assert request.args['car_id'] == 'scooter_stub_id_1'
        return load_json('car_details.json')

    @mockserver.json_handler('/scooter-backend/api/taxi/car/tag_add')
    def mock_tag_add(request):
        assert request.json == {
            'object_ids': ['scooter_stub_id_1'],
            'tag_name': 'lockme',
        }
        return {
            'tagged_objects': [
                {'object_id': 'scooter_stub_id_1', 'tag_id': ['tag_id1']},
            ],
        }

    resp = await taxi_scooters_ops.post(
        HANDLER,
        params={'mission_id': 'mission_stub_id', 'mission_revision': 2},
    )

    assert resp.status == 200

    assert mock_car_details.times_called == 3
    assert mock_tag_add.times_called == 1
