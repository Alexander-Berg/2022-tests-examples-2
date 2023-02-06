import pytest


def approx(vvvv: float):
    return pytest.approx(vvvv, abs=0.0001)


EXPECTED_RESPONSES = [
    {
        'ratings': [
            {
                'unique_driver_id': 'driver_id_1',
                'rating': approx(4.0),
                'previous_rating': approx(4.5),
                'calc_at': '2019-05-01T03:00:00+03:00',
                'used_scores_num': 25,
            },
            {
                'unique_driver_id': 'driver_id_2',
                'rating': approx(4.1),
                'previous_rating': approx(4.6),
                'calc_at': '2019-05-01T03:00:00+03:00',
                'used_scores_num': 15,
                'details': '[{"ts": 1599047171.819, "order": "f314d82912803505b0d3f77ba3912e77", "rating": 5, "weight": 1}]',  # noqa: E501 pylint: disable=line-too-long
            },
            {
                'unique_driver_id': 'driver_id_3',
                'rating': approx(4.2),
                'calc_at': '2019-05-01T03:01:00+03:00',
                'used_scores_num': 35,
                'details': '[{"ts": 1599047171.819, "order": "f314d82912803505b0d3f77ba3912e78", "rating": 4, "weight": 2}, {"count": 11, "rating": 5, "source": "padding", "artificial": true}]',  # noqa: E501 pylint: disable=line-too-long
            },
        ],
        'cursor': '2019-05-01T00:01:00|driver_id_3',
    },
    {
        'ratings': [
            {
                'unique_driver_id': 'driver_id_7',
                'rating': approx(4.6),
                'calc_at': '2019-05-01T03:02:00+03:00',
                'used_scores_num': 7,
            },
            {
                'unique_driver_id': 'driver_id_10',
                'rating': approx(4.9),
                'calc_at': '2019-05-02T03:00:00+03:00',
                'used_scores_num': 45,
            },
            {
                'unique_driver_id': 'driver_id_11',
                'rating': approx(4.91),
                'previous_rating': approx(4.7),
                'calc_at': '2019-05-02T03:00:00+03:00',
                'used_scores_num': 23,
            },
        ],
        'cursor': '2019-05-02T00:00:00|driver_id_11',
    },
    {'ratings': [], 'cursor': '2019-05-02T00:00:00|driver_id_13'},
]


@pytest.mark.parametrize(
    'cursor,limit,response_idx',
    [
        (None, 3, 0),
        ('2019-05-01T00:02:00|driver_id_6', 3, 1),
        ('2019-05-02T00:00:00|driver_id_13', 10, 2),
    ],
)
@pytest.mark.pgsql('driver_ratings_storage', files=['many_ratings.sql'])
@pytest.mark.config(FETCH_HISTORY_ON_RATING_UPDATES=True)
async def test_rating_updates(
        taxi_driver_ratings_storage_web, cursor, limit, response_idx,
):
    request = {'limit': limit}
    if cursor:
        request['cursor'] = cursor
    response = await taxi_driver_ratings_storage_web.post(
        f'/driver-ratings-storage/v1/ratings/updates/', json=request,
    )
    assert response.status == 200, await response.text()
    expected = EXPECTED_RESPONSES[response_idx]
    assert expected == await response.json()


async def test_empty_db(taxi_driver_ratings_storage_web):
    request = {'limit': 1000}
    response = await taxi_driver_ratings_storage_web.post(
        f'/driver-ratings-storage/v1/ratings/updates/', json=request,
    )
    assert response.status == 200, await response.text()
    assert {'ratings': []} == await response.json()


@pytest.mark.parametrize(
    'cursor',
    [
        'I am bad',
        '|2019-05-01T00:02:00|driver_id_6',
        '2019-05-01T00:02:00|',
        '|driver_id_6',
    ],
)
async def test_bad_cursor(taxi_driver_ratings_storage_web, cursor):
    request = {'limit': 1000, 'cursor': cursor}
    response = await taxi_driver_ratings_storage_web.post(
        f'/driver-ratings-storage/v1/ratings/updates/', json=request,
    )
    assert response.status == 400, await response.text()
