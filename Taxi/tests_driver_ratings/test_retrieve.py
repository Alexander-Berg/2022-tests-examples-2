import pytest


@pytest.mark.now('2020-05-15T10:01:00+0000')
async def test_driver_ratings_retrieve(taxi_driver_ratings):
    response = await taxi_driver_ratings.post(
        'v1/driver/ratings/retrieve',
        json={
            'id_in_set': [
                'unique_driver_id_round3',
                'unique_driver_id1',
                'unique_driver_id5',
                'unique_driver_id6',
            ],
        },
        params={'consumer': 'test'},
    )
    assert response.status_code == 200
    assert 'application/json' in response.headers['Content-Type']
    assert response.json() == {
        'ratings': [
            {
                'revision': '2020-05-14T10:01:00+0000|unique_driver_id_round3',
                'data': {'rating': 4.0, 'rating_count': 0, 'total': 0.75},
                'unique_driver_id': 'unique_driver_id_round3',
            },
            {
                'revision': '2019-01-01T10:00:00+0000|unique_driver_id1',
                'data': {'rating': 5.0, 'rating_count': 175, 'total': 1.0},
                'unique_driver_id': 'unique_driver_id1',
            },
            {
                'revision': '2020-05-14T10:01:00+0000|unique_driver_id5',
                'data': {'rating': 4.0, 'rating_count': 0, 'total': 0.75},
                'unique_driver_id': 'unique_driver_id5',
            },
            {
                'revision': '2020-05-14T10:01:00+0000|unique_driver_id6',
                'data': {'rating': 4.0, 'rating_count': 0, 'total': 0.75},
                'unique_driver_id': 'unique_driver_id6',
            },
        ],
    }
