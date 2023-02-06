import datetime

import pytest

REQUEST = {
    'uniques_events': [
        {
            'unique_driver': {
                'id': 'driver_1',
                'park_driver_profile_ids': [{'id': '123'}],
            },
            'merged_unique_driver': {
                'id': 'driver_2',
                'park_driver_profile_ids': [{'id': '456'}],
            },
        },
    ],
}

COPY_SCORES_RESPONSE = [
    ('order_1_1', 'driver_1', 1, datetime.datetime(2019, 5, 1, 0, 0), None),
    ('order_1_2', 'driver_1', 1, datetime.datetime(2019, 5, 2, 0, 0), None),
    ('order_2_1', 'driver_2', 2, datetime.datetime(2019, 5, 3, 0, 0), None),
    ('order_2_2', 'driver_2', 2, datetime.datetime(2019, 5, 4, 0, 0), None),
    ('order_3_1', 'driver_3', 3, datetime.datetime(2019, 5, 5, 0, 0), None),
    ('order_3_2', 'driver_3', 3, datetime.datetime(2019, 5, 6, 0, 0), None),
    ('order_4_1', 'driver_4', 4, datetime.datetime(2019, 5, 7, 0, 0), None),
    ('order_4_2', 'driver_4', 4, datetime.datetime(2019, 5, 8, 0, 0), None),
    (
        'order_2_1driver_1',
        'driver_1',
        2,
        datetime.datetime(2019, 5, 3, 0, 0),
        None,
    ),
    (
        'order_2_2driver_1',
        'driver_1',
        2,
        datetime.datetime(2019, 5, 4, 0, 0),
        None,
    ),
]

COPY_RATING_RESPONSE = [
    (
        'driver_2',
        2.0,
        datetime.datetime(2019, 5, 1, 0, 0),
        datetime.datetime(2019, 5, 1, 0, 0),
        None,
        None,
        None,
        None,
        None,
    ),
    (
        'driver_4',
        4.0,
        datetime.datetime(2019, 5, 1, 0, 0),
        datetime.datetime(2019, 5, 1, 0, 0),
        None,
        None,
        None,
        None,
        None,
    ),
]


@pytest.mark.config(
    DRIVER_RATINGS_STORAGE_PROCESS_UNIQUES_EVENTS={
        '__default__': False,
        'MergeEvents': True,
    },
)
async def test_uniques_events_bulk(
        taxi_driver_ratings_storage_web, pgsql, load,
):
    with pgsql['driver_ratings_storage'].cursor() as cursor:
        cursor.execute(load('tables.sql'))

    response = await taxi_driver_ratings_storage_web.post(
        '/internal/v1/ratings/process/uniques-events/bulk/', json=REQUEST,
    )

    with pgsql['driver_ratings_storage'].cursor() as cursor:
        cursor.execute(load('check_driver_scores.sql'))
        assert cursor.fetchall() == COPY_SCORES_RESPONSE

    with pgsql['driver_ratings_storage'].cursor() as cursor:
        cursor.execute(load('check_driver_ratings.sql'))
        table_data = cursor.fetchall()
        updated_row = table_data.pop(2)
        assert updated_row[7]
        assert table_data == COPY_RATING_RESPONSE

    assert response.status == 200
