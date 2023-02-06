import pytest


async def search_places_updates(taxi_eats_catalog_storage, data):
    path = '/internal/eats-catalog-storage/v1/search/places/updates'
    response = await taxi_eats_catalog_storage.post(path, data)
    return response


def get_test_records_number(pgsql):
    cursor = pgsql['eats_catalog_storage'].cursor()
    cursor.execute('SELECT count(*) FROM storage.places')
    return cursor.fetchone()[0]


async def select_and_check_empty(taxi_eats_catalog_storage, data):
    response = await search_places_updates(taxi_eats_catalog_storage, data)
    assert response.status_code == 200

    response_data = response.json()
    assert 'last_updated_at' not in response_data
    assert not response_data['payload']['places']


async def select_and_check_number(
        taxi_eats_catalog_storage, data, expected_number,
):
    response = await search_places_updates(taxi_eats_catalog_storage, data)
    assert response.status_code == 200

    response_data = response.json()
    places = response_data['payload']['places']
    assert len(places) == expected_number

    last_updated_at = response_data['last_updated_at']
    assert last_updated_at is not None


@pytest.mark.pgsql('eats_catalog_storage', files=['insert_places.sql'])
async def test_search_with_invalid_limit(taxi_eats_catalog_storage):
    # the function must not crash on invalid input
    data = {'limit': 0}
    await select_and_check_empty(taxi_eats_catalog_storage, data)


@pytest.mark.pgsql('eats_catalog_storage', files=['insert_places.sql'])
async def test_search_with_no_timestamp_truncated(
        taxi_eats_catalog_storage, pgsql,
):
    # let's select a half of records
    test_records_number = get_test_records_number(pgsql)
    assert test_records_number > 1
    select_records_number = test_records_number // 2

    data = {'limit': select_records_number}
    await select_and_check_number(
        taxi_eats_catalog_storage, data, select_records_number,
    )


@pytest.mark.pgsql('eats_catalog_storage', files=['insert_places.sql'])
async def test_search_with_no_timestamp_all(taxi_eats_catalog_storage, pgsql):
    # let's select all test records by using exceeding limit
    test_records_number = get_test_records_number(pgsql)
    select_records_number = test_records_number * 2

    data = {'limit': select_records_number}
    await select_and_check_number(
        taxi_eats_catalog_storage, data, test_records_number,
    )


@pytest.mark.pgsql('eats_catalog_storage', files=['insert_places.sql'])
async def test_search_with_timestamp(taxi_eats_catalog_storage):
    # the last 3 records are:
    # '2018-12-14T00:00:03+03:00'
    # '2018-12-14T00:00:04+03:00'
    # '2018-12-14T00:00:04+03:00'
    # the last 2 records have identical value in updated_at

    date_time_3_sec = '2018-12-14T00:00:03+03:00'
    date_time_4_sec = '2018-12-14T00:00:04+03:00'

    # select all records filtered by time
    data = {'updated_at': date_time_3_sec, 'limit': 1000}
    await select_and_check_number(taxi_eats_catalog_storage, data, 3)

    data = {'updated_at': date_time_4_sec, 'limit': 1000}
    await select_and_check_number(taxi_eats_catalog_storage, data, 2)

    # select limited number of records filtered by time
    data = {'updated_at': date_time_3_sec, 'limit': 1}
    await select_and_check_number(taxi_eats_catalog_storage, data, 1)

    data = {'updated_at': date_time_4_sec, 'limit': 1}
    await select_and_check_number(taxi_eats_catalog_storage, data, 1)


@pytest.mark.pgsql('eats_catalog_storage', files=['insert_places.sql'])
async def test_search_with_timestamp_no_result(taxi_eats_catalog_storage):
    data = {'updated_at': '2018-12-14T00:00:05+03:00', 'limit': 4}
    await select_and_check_empty(taxi_eats_catalog_storage, data)


@pytest.mark.pgsql(
    'eats_catalog_storage', files=['insert_place_with_new_rating.sql'],
)
async def test_search_with_new_rating(taxi_eats_catalog_storage):

    response = await search_places_updates(
        taxi_eats_catalog_storage, {'limit': 1},
    )
    assert response.status_code == 200

    assert response.json() == {
        'last_updated_at': '2020-10-10T02:05:05+00:00',
        'payload': {
            'places': [
                {
                    'business': 'zapravki',
                    'enabled': True,
                    'launched_at': '2020-10-10T02:05:05+00:00',
                    'name': 'Название10',
                    'new_rating': {'rating': 5.0, 'show': True, 'count': 0},
                    'place_id': 10,
                    'place_slug': 'slug10',
                    'rating': 1.0,
                    'region_id': 1,
                    'updated_at': '2020-10-10T02:05:05+00:00',
                },
            ],
        },
    }
