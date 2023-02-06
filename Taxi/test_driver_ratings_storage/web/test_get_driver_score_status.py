import pytest

HEADERS = {'X-Yandex-Login': 'login', 'X-Yandex-UID': '1234567890'}


async def test_unknown_order(taxi_driver_ratings_storage_web):
    response = await taxi_driver_ratings_storage_web.get(
        '/driver-ratings-storage/v1/driver-score-status',
        params={'order_id': 'aabbccdd1234'},
        headers=HEADERS,
    )
    assert response.status == 200
    content = await response.json()
    assert content == {'was_edited': False}


@pytest.mark.pgsql('driver_ratings_storage', files=['first_record.sql'])
@pytest.mark.parametrize(
    'pgsql_files,expected_last_modification',
    [
        (
            ['first_record.sql'],
            {
                'is_ignored': True,
                'login': 'some_login',
                'type': 'support',
                'description': 'some_description',
            },
        ),
        (
            ['first_record_cancel.sql'],
            {
                'is_ignored': False,
                'login': 'another_login',
                'type': 'support',
                'description': 'another_description',
            },
        ),
        (
            ['no_description_record.sql'],
            {
                'is_ignored': True,
                'login': 'yet_another_login',
                'type': 'script',
                'description': 'Analytics script',
            },
        ),
    ],
)
async def test_known_order(
        taxi_driver_ratings_storage_web,
        pgsql,
        load,
        pgsql_files,
        expected_last_modification,
):
    with pgsql['driver_ratings_storage'].cursor() as cursor:
        for file in pgsql_files:
            cursor.execute(load(file))

    response = await taxi_driver_ratings_storage_web.get(
        '/driver-ratings-storage/v1/driver-score-status',
        params={'order_id': 'some_order_id'},
        headers=HEADERS,
    )

    assert response.status == 200
    content = await response.json()
    assert 'last_modification' in content
    content['last_modification'].pop('event_at', None)
    assert content == {
        'was_edited': True,
        'last_modification': expected_last_modification,
    }
