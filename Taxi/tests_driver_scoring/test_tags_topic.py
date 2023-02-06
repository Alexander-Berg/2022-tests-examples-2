import pytest

import tests_driver_scoring.tvm_tickets as tvm_tickets


HEADERS = {'X-Ya-Service-Ticket': tvm_tickets.MOCK_SERVICE_TICKET}
BODY = {
    'request': {
        'search': {
            'order': {
                'request': {'source': {'geopoint': [39.60258, 52.569089]}},
                'nearest_zone': 'lipetsk',
            },
            'allowed_classes': ['econom'],
        },
        'candidates': [
            {  # bonus: 10
                'id': 'dbid0_uuid0',
                'route_info': {
                    'time': 500,
                    'distance': 3200,
                    'approximate': False,
                },
                'position': [39.59568, 52.568001],
                'classes': ['econom', 'business'],
                'unique_driver_id': 'udid0',
            },
        ],
    },
    'intent': 'dispatch-buffer',
}


@pytest.mark.experiments3(filename='driver_bonuses.json')
@pytest.mark.experiments3(filename='default_postprocessors.json')
@pytest.mark.tags_v2_index(
    tags_list=[
        ('dbid_uuid', 'dbid0_uuid0', 'silver'),  # bonus: 10
        ('dbid_uuid', 'dbid0_uuid0', 'private_car'),  # bonus: 20
        ('udid', 'udid0', 'reposition_super_surge'),  # bonus: 50
    ],
    topic_relations=[('driver_scoring', 'silver')],
)
async def test_tags_without_topic(taxi_driver_scoring):
    await taxi_driver_scoring.invalidate_caches()

    response = await taxi_driver_scoring.post(
        'v2/score-candidates', headers=HEADERS, json=BODY,
    )
    assert response.status_code == 200
    assert response.json() == {
        'search': {},
        'candidates': [
            {'id': 'dbid0_uuid0', 'score': 490.0},  # 500 - 10 = 490
        ],
    }


@pytest.mark.experiments3(filename='driver_bonuses.json')
@pytest.mark.experiments3(filename='default_postprocessors.json')
@pytest.mark.tags_v2_index(
    tags_list=[
        ('dbid_uuid', 'dbid0_uuid0', 'silver'),  # bonus: 10
        ('dbid_uuid', 'dbid0_uuid0', 'private_car'),  # bonus: 20
        ('udid', 'udid0', 'reposition_super_surge'),  # bonus: 50
    ],
)
async def test_tags_with_topic(taxi_driver_scoring):
    await taxi_driver_scoring.invalidate_caches()

    response = await taxi_driver_scoring.post(
        'v2/score-candidates', headers=HEADERS, json=BODY,
    )
    assert response.status_code == 200
    assert response.json() == {
        'search': {},
        'candidates': [
            {'id': 'dbid0_uuid0', 'score': 420.0},  # 500 - 10 - 20 - 50 = 420
        ],
    }


@pytest.mark.experiments3(filename='driver_bonuses.json')
@pytest.mark.experiments3(filename='default_postprocessors.json')
@pytest.mark.tags_v2_index(
    tags_list=[
        ('dbid_uuid', 'dbid0_uuid0', 'silver'),  # bonus: 10
        ('dbid_uuid', 'dbid1_uuid1', 'silver'),  # bonus: 10
        ('dbid_uuid', 'dbid2_uuid2', 'silver'),  # bonus: 10
        ('dbid_uuid', 'dbid3_uuid3', 'silver'),  # bonus: 10
        ('park_car_id', 'dbid0_car0', 'park_car_id_tag'),  # bonus: 60
        ('park_car_id', 'dbid1_car1', 'park_car_id_tag'),  # bonus: 60
        ('park_car_id', 'dbid3_car3', 'park_car_id_tag'),  # bonus: 60
    ],
)
async def test_tag_park_car_id(taxi_driver_scoring):
    await taxi_driver_scoring.invalidate_caches()

    body = BODY
    body['request']['candidates'].append(
        {
            'id': 'dbid1_uuid1',
            'route_info': {
                'time': 500,
                'distance': 3200,
                'approximate': False,
            },
            'position': [39.59568, 52.568001],
            'classes': ['econom', 'business'],
            'unique_driver_id': 'udid1',
        },
    )
    body['request']['candidates'].append(
        {
            'id': 'dbid2_uuid2',
            'route_info': {
                'time': 500,
                'distance': 3200,
                'approximate': False,
            },
            'position': [39.59568, 52.568001],
            'classes': ['econom', 'business'],
            'unique_driver_id': 'udid2',
        },
    )

    response = await taxi_driver_scoring.post(
        'v2/score-candidates', headers=HEADERS, json=body,
    )
    assert response.status_code == 200
    assert response.json() == {
        'search': {},
        'candidates': [
            {'id': 'dbid0_uuid0', 'score': 430.0},  # 500 - 10 - 60 = 430
            {
                'id': 'dbid1_uuid1',
                'score': 490.0,
            },  # 500 - 10 = 490, no car_id in response candidates/profiles
            {
                'id': 'dbid2_uuid2',
                'score': 490.0,
            },  # 500 - 10 = 490, car_id exists in in response
            # candidates/profiles, but no bonuses
        ],
    }
