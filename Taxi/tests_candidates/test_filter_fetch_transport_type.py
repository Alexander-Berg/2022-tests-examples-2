import json

import pytest


@pytest.mark.contractors_transport(
    {
        'contractors_transport': [
            {
                'contractor_id': 'dbid0_uuid0',
                'is_deleted': False,
                'revision': '1234567_2',
                'transport_active': {'type': 'bicycle'},
            },
            {
                'contractor_id': 'dbid0_uuid1',
                'is_deleted': True,
                'revision': '1234567_2',
                'transport_active': {'type': 'bicycle'},
            },
        ],
        'cursor': '0|1234567_4',
    },
)
async def test_sample(taxi_candidates, mockserver):
    @mockserver.json_handler(
        '/contractor-transport/v1/transport-active/retrieve-by-contractor-id',
    )
    def _mock_retrieve_by_contractor_id(request):
        return mockserver.make_response(
            response=json.dumps(
                {
                    'contractors_transport': [
                        {
                            'contractor_id': 'dbid0_uuid1',
                            'is_deleted': False,
                            'revision': '1234567_2',
                            'transport_active': {'type': 'pedestrian'},
                        },
                    ],
                },
            ),
        )

    request_body = {
        'driver_ids': ['dbid0_uuid0', 'dbid0_uuid1'],
        'zone_id': 'moscow',
        'data_keys': ['transport'],
    }

    response = await taxi_candidates.post('profiles', json=request_body)
    assert response.status_code == 200
    assert 'drivers' in response.json()
    drivers = response.json()['drivers']
    assert len(drivers) == 2
    result = {driver['id']: driver['transport']['type'] for driver in drivers}
    assert result == {'dbid0_uuid0': 'bicycle', 'dbid0_uuid1': 'pedestrian'}


@pytest.mark.parametrize(
    'exp_value, transport_type',
    [
        ({}, None),
        ({'transport_type': 'pedestrian'}, 'pedestrian'),
        ({'transport_type': 'invalid'}, None),
        (None, 'car'),
    ],
)
@pytest.mark.contractors_transport(
    {'contractors_transport': [], 'cursor': '0|1234567_4'},
)
async def test_fallback_transport_type(
        taxi_candidates, exp_value, transport_type, experiments3, mockserver,
):
    if exp_value is not None:
        experiments3.add_config(
            match={'predicate': {'type': 'true'}, 'enabled': True},
            name='candidates_contractor_transport_fallback_settings',
            consumers=['candidates/user'],
            clauses=[
                {
                    'value': exp_value,
                    'predicate': {'type': 'true'},
                    'enabled': True,
                },
            ],
            default_value={},
        )

    @mockserver.json_handler(
        '/contractor-transport/v1/transport-active/retrieve-by-contractor-id',
    )
    def _mock_retrieve_by_contractor_id(request):
        return mockserver.make_response(
            response=json.dumps({'contractors_transport': []}),
        )

    request_body = {
        'driver_ids': ['dbid0_uuid0'],
        'zone_id': 'moscow',
        'data_keys': ['transport'],
    }

    response = await taxi_candidates.post('profiles', json=request_body)
    assert response.status_code == 200
    assert 'drivers' in response.json()
    drivers = response.json()['drivers']

    if transport_type:
        assert len(drivers) == 1
        assert drivers[0]['transport']['type'] == transport_type
    else:
        assert not drivers
