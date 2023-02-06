import json

import pytest


@pytest.mark.redis_store(
    ['hset', 'Driver:Photos:2128506', 'vodilo', '{}'],
    [
        'hset',
        'Driver:Photos:2128506',
        'pilot',
        json.dumps(
            {
                'Large': {
                    'Driver': (
                        'https://storage.mds.yandex.net/get-taximeter/'
                        'https://storage.mds.yandex.net/get-taximeter/'
                        'https://storage.mds.yandex.net/get-taximeter/'
                        '3325/6a255a958d234fa497d99c21b4a1f166_small.jpg'
                    ),
                },
                'Original': {
                    'Driver': 'original/driver.jpg',
                    'Front': 'front.jpg',
                    'Left': 'left.jpg',
                    'Salon': 'salon.jpg',
                },
            },
        ),
    ],
)
@pytest.mark.parametrize(
    'params, body, expected_response',
    [
        (
            {'park_id': '2128506', 'driver_profile_id': 'vodilo'},
            {'photos': ['driver', 'left']},
            {'photos': []},
        ),
        (
            {'park_id': '2128506', 'driver_profile_id': 'pilot'},
            {'photos': ['driver', 'front', 'left']},
            {
                'photos': [
                    {
                        'href': (
                            'https://storage.mds.yandex.net/get-taximeter/'
                            'salon.jpg'
                        ),
                        'scale': 'original',
                        'type': 'salon',
                    },
                ],
            },
        ),
        (
            {'park_id': '2128506', 'driver_profile_id': 'pilot'},
            {'photos': ['front', 'left', 'salon']},
            {
                'photos': [
                    {
                        'href': (
                            'https://storage.mds.yandex.net/get-taximeter/'
                            '3325/6a255a958d234fa497d99c21b4a1f166_small.jpg'
                        ),
                        'scale': 'large',
                        'type': 'driver',
                    },
                    {
                        'href': (
                            'https://storage.mds.yandex.net/get-taximeter/'
                            'original/driver.jpg'
                        ),
                        'scale': 'original',
                        'type': 'driver',
                    },
                ],
            },
        ),
    ],
)
def test_ok(taxi_parks, params, body, expected_response):
    response = taxi_parks.post(
        '/driver-profiles/photo-remove', params=params, data=json.dumps(body),
    )

    assert response.status_code == 200, response.text
    assert response.json() == expected_response


def test_no_such_driver(taxi_parks, redis_store):
    park = '2128506'
    driver = 'pilot'
    response = taxi_parks.post(
        '/driver-profiles/photo-remove',
        params={'park_id': park, 'driver_profile_id': driver},
        data=json.dumps({'photos': []}),
    )

    assert response.status_code == 200, response.text
    assert redis_store.hget('Driver:Photos:' + park, driver) is None
    assert response.json() == {'photos': []}
