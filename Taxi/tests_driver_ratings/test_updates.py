import pytest


@pytest.mark.now('2020-03-25T01:00:00+0000')
async def test_driver_ratings_updates(taxi_driver_ratings):
    response = await taxi_driver_ratings.get(
        'v1/driver/ratings/updates',
        params={
            'consumer': 'test',
            'last_known_revision': (
                '2020-01-01T10:00:00+0000|unique_driver_id1'
            ),
        },
    )
    assert response.status_code == 200
    assert response.json() == {
        'last_modified': '2020-03-25T01:00:00+0000',
        'last_revision': '2020-01-01T10:01:30+0000|unique_driver_id48',
        'ratings': [
            {
                'revision': '2020-01-01T10:00:00+0000|unique_driver_id4',
                'data': {'rating': 4.0, 'rating_count': 175, 'total': 0.75},
                'unique_driver_id': 'unique_driver_id4',
            },
            {
                'revision': '2020-01-01T10:01:01+0000|unique_driver_id_round1',
                'data': {'rating': 4.444, 'rating_count': 144, 'total': 0.861},
                'unique_driver_id': 'unique_driver_id_round1',
            },
            {
                'revision': '2020-01-01T10:01:02+0000|unique_driver_id_round2',
                'data': {
                    'rating': 4.999,
                    'rating_count': 156,
                    'total': 0.9997499999999999,
                },
                'unique_driver_id': 'unique_driver_id_round2',
            },
            {
                'revision': '2020-01-01T10:01:02+0000|unique_driver_id_round3',
                'data': {'rating': 4.0, 'rating_count': 0, 'total': 0.75},
                'unique_driver_id': 'unique_driver_id_round3',
            },
            {
                'revision': '2020-01-01T10:01:30+0000|unique_driver_id48',
                'data': {'rating': 5.0, 'rating_count': 175, 'total': 1.0},
                'unique_driver_id': 'unique_driver_id48',
            },
        ],
    }
    delay_header = response.headers.get('X-Polling-Delay-Ms')
    assert delay_header == '50'
    response = await taxi_driver_ratings.get(
        'v1/driver/ratings/updates',
        params={
            'consumer': 'test',
            'last_known_revision': (
                '2020-01-01T10:01:30+0000|unique_driver_id48'
            ),
        },
    )
    assert response.json() == {
        'last_modified': '2020-03-25T01:00:00+0000',
        'last_revision': '2020-01-01T10:01:30+0000|unique_driver_id48',
        'ratings': [],
    }


@pytest.mark.now('2020-03-25T01:00:00+0000')
async def test_driver_ratings_updates_empty_revision(taxi_driver_ratings):
    response = await taxi_driver_ratings.get(
        'v1/driver/ratings/updates', params={'consumer': 'test'},
    )
    assert response.status_code == 200
    assert response.json() == {
        'last_modified': '2020-03-25T01:00:00+0000',
        'last_revision': '2020-01-01T10:01:30+0000|unique_driver_id48',
        'ratings': [
            {
                'revision': '2019-01-01T10:00:00+0000|unique_driver_id1',
                'data': {'rating': 5.0, 'rating_count': 175, 'total': 1.0},
                'unique_driver_id': 'unique_driver_id1',
            },
            {
                'revision': '2020-01-01T10:00:00+0000|unique_driver_id4',
                'data': {'rating': 4.0, 'rating_count': 175, 'total': 0.75},
                'unique_driver_id': 'unique_driver_id4',
            },
            {
                'revision': '2020-01-01T10:01:01+0000|unique_driver_id_round1',
                'data': {'rating': 4.444, 'rating_count': 144, 'total': 0.861},
                'unique_driver_id': 'unique_driver_id_round1',
            },
            {
                'revision': '2020-01-01T10:01:02+0000|unique_driver_id_round2',
                'data': {
                    'rating': 4.999,
                    'rating_count': 156,
                    'total': 0.9997499999999999,
                },
                'unique_driver_id': 'unique_driver_id_round2',
            },
            {
                'revision': '2020-01-01T10:01:02+0000|unique_driver_id_round3',
                'data': {'rating': 4.0, 'rating_count': 0, 'total': 0.75},
                'unique_driver_id': 'unique_driver_id_round3',
            },
            {
                'revision': '2020-01-01T10:01:30+0000|unique_driver_id48',
                'data': {'rating': 5.0, 'rating_count': 175, 'total': 1.0},
                'unique_driver_id': 'unique_driver_id48',
            },
        ],
    }


@pytest.mark.now('2020-03-25T01:00:00+0000')
async def test_driver_ratings_updates_bad_cursor(taxi_driver_ratings):
    response = await taxi_driver_ratings.get(
        'v1/driver/ratings/updates',
        params={
            'consumer': 'test',
            'last_known_revision': (
                '2020-01-01xx10:00:00.000000|unique_driver_id1'
            ),
        },
    )
    assert response.status_code == 200
    assert response.json() == {
        'last_modified': '2020-03-25T01:00:00+0000',
        'last_revision': '2020-01-01T10:01:30+0000|unique_driver_id48',
        'ratings': [
            {
                'revision': '2019-01-01T10:00:00+0000|unique_driver_id1',
                'data': {'rating': 5.0, 'rating_count': 175, 'total': 1.0},
                'unique_driver_id': 'unique_driver_id1',
            },
            {
                'revision': '2020-01-01T10:00:00+0000|unique_driver_id4',
                'data': {'rating': 4.0, 'rating_count': 175, 'total': 0.75},
                'unique_driver_id': 'unique_driver_id4',
            },
            {
                'revision': '2020-01-01T10:01:01+0000|unique_driver_id_round1',
                'data': {'rating': 4.444, 'rating_count': 144, 'total': 0.861},
                'unique_driver_id': 'unique_driver_id_round1',
            },
            {
                'revision': '2020-01-01T10:01:02+0000|unique_driver_id_round2',
                'data': {
                    'rating': 4.999,
                    'rating_count': 156,
                    'total': 0.9997499999999999,
                },
                'unique_driver_id': 'unique_driver_id_round2',
            },
            {
                'revision': '2020-01-01T10:01:02+0000|unique_driver_id_round3',
                'data': {'rating': 4.0, 'rating_count': 0, 'total': 0.75},
                'unique_driver_id': 'unique_driver_id_round3',
            },
            {
                'revision': '2020-01-01T10:01:30+0000|unique_driver_id48',
                'data': {'rating': 5.0, 'rating_count': 175, 'total': 1.0},
                'unique_driver_id': 'unique_driver_id48',
            },
        ],
    }
