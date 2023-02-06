import pytest

HEADERS = {'X-Yandex-Login': 'login', 'X-Yandex-UID': '1234567890'}
ENDPOINT = (
    '/driver-ratings-storage/v1/driver-score-status/'
    'history/statistics/retrieve'
)


@pytest.mark.now('2020-05-08T18:00:00+03:00')
@pytest.mark.parametrize(
    'request_type,request_value', [('days', 3), ('scores', 5)],
)
@pytest.mark.parametrize(
    'scores_sql,history_sql,expected',
    [
        (None, None, {'ignored': 0, 'restored': 0, 'total_scores': 0}),
        (
            'scores.sql',
            'history_ignored_only.sql',
            {'ignored': 2, 'restored': 0, 'total_scores': 5},
        ),
        (
            'scores.sql',
            'history.sql',
            {'ignored': 3, 'restored': 1, 'total_scores': 5},
        ),
    ],
)
async def test_ok(
        taxi_driver_ratings_storage_web,
        pgsql,
        load,
        request_type,
        request_value,
        scores_sql,
        history_sql,
        expected,
):
    with pgsql['driver_ratings_storage'].cursor() as cursor:
        if scores_sql:
            cursor.execute(load(scores_sql))
        if history_sql:
            cursor.execute(load(history_sql))

    response = await taxi_driver_ratings_storage_web.get(
        ENDPOINT,
        params={
            'unique_driver_id': 'driver_1',
            'type': request_type,
            'value': request_value,
        },
        headers=HEADERS,
    )
    assert response.status == 200
    content = await response.json()
    assert content == expected
