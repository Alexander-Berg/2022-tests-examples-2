import pytest


@pytest.mark.config(
    DRIVER_OPTIONS_BUILDER_SETTINGS=[
        {
            'title_key': 'taxi_options.title',
            'options': [
                {
                    'blocking_tags': [],
                    'exams': [],
                    'name': 'own_chair',
                    'prefix': 'other',
                    'title_key': 'own_chair_title',
                    'version': '1.12',
                },
            ],
        },
    ],
    EXTRA_EXAMS_BY_ZONE={},
    TAGS_INDEX={
        'enabled': True,
        'request_interval': 100,
        'request_size': 8192,
    },
)
@pytest.mark.tags_v2_index(
    tags_list=[
        # dbid0_uuid0 -- booster + own_chair
        ('dbid_uuid', 'dbid0_uuid0', 'own_chair'),
        # dbid0_uuid1 -- booster
    ],
)
@pytest.mark.parametrize(
    'requirements, expected_drivers',
    [
        ({'childchair': 7}, ['uuid0', 'uuid1']),
        ({'childchair': 7, 'own_chair': True}, ['uuid0']),
        ({'own_chair': True}, ['uuid0']),
        ({'childchair': 10}, ['uuid0']),
        ({'childchair': [7, 10]}, ['uuid0']),
        ({'childchair': [10, 10]}, ['uuid0']),
        ({'childchair': [1, 10]}, []),
    ],
)
async def test_sample(
        taxi_candidates, driver_positions, requirements, expected_drivers,
):
    await driver_positions(
        [
            {'dbid_uuid': 'dbid0_uuid0', 'position': [37.680517, 55.787963]},
            {'dbid_uuid': 'dbid0_uuid1', 'position': [37.559667, 55.685688]},
        ],
    )

    request_body = {
        'geoindex': 'kdtree',
        'max_distance': 10000,
        'limit': 2,
        'filters': ['partners/childchairs', 'infra/requirements_v2'],
        'point': [37.611254, 55.752533],
        'zone_id': 'moscow',
        'requirements': requirements,
    }
    response = await taxi_candidates.post('search', json=request_body)
    assert response.status_code == 200
    json = response.json()
    assert 'drivers' in json
    drivers = json['drivers']
    assert len(drivers) == len(expected_drivers)
    for driver in json['drivers']:
        assert driver['uuid'] in expected_drivers
