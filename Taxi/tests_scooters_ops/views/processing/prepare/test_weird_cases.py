HANDLER = '/scooters-ops/v1/processing/missions/prepare'


async def test_dropoff_vehicles_job_parse_json(
        taxi_scooters_ops, mockserver, yamaps,
):
    @mockserver.json_handler('/processing/v1/scooters/missions/create-event')
    def _mock_processing_create_event(request):
        return {'event_id': 'idontcare'}

    mission = {
        'performer_id': 'performer',
        'related_drafts': [],
        'points': [
            {
                'type': 'depot',
                'location': [35.2, 42.6],
                'typed_extra': {'depot': {'id': 'depot_stub_id'}},
                'jobs': [{'type': 'do_nothing', 'typed_extra': {}}],
            },
            {
                'type': 'parking_place',
                'location': [35.2, 42.6],
                'typed_extra': {'parking_place': {'id': 'pp1'}},
                'jobs': [
                    {
                        'type': 'dropoff_vehicles',
                        'typed_extra': {'quantity': 1},
                    },
                ],
            },
        ],
    }

    mission_create_response = await taxi_scooters_ops.post(
        '/scooters-ops/v1/missions/create',
        mission,
        params={'mission_id': 'mission_stub_id'},
    )

    assert mission_create_response.status == 200

    @mockserver.json_handler('/scooters-misc/scooters-misc/v1/areas')
    async def _areas(request):
        return {'areas': []}

    resp = await taxi_scooters_ops.post(
        HANDLER,
        params={'mission_id': 'mission_stub_id', 'mission_revision': 1},
    )

    assert resp.status == 200
