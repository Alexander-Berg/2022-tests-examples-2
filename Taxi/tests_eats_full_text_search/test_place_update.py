import datetime

import dateutil.parser
import pytest


def gen_place(place_id, business='shop'):
    return {
        'place_id': place_id,
        'place_slug': 'slug_{}'.format(place_id),
        'name': 'name_{}'.format(place_id),
        'business': business,
        'rating': 5.0,
        'updated_at': '2020-10-26T14:14:22Z',
        'launched_at': '2020-10-26T00:00:00Z',
        'region_id': 1,
        'enabled': place_id % 2 == 0,
    }


UPDATES_LIMIT = 2
UPDATES_CORRECTION = 10


@pytest.mark.config(
    EATS_FULL_TEXT_SEARCH_PLACE_UPDATE_SETTINGS={
        'full_update_interval': 7200,
        'incremental_update_interval': 3600,
        'enable': True,
        'enable_check_interval': 60,
    },
)
@pytest.mark.config(
    EATS_FULL_TEXT_SEARCH_CATALOG_STORAGE_REQUEST_SETTINGS={
        'updates_limit': UPDATES_LIMIT,
        'updates_correction': UPDATES_CORRECTION,
    },
)
async def test_catalog_storage_periodic(
        testpoint,
        taxi_eats_full_text_search,
        taxi_eats_full_text_search_monitor,
        mockserver,
        pgsql,
):
    """
    Проверяем, что периодик делает запрос в catalog-storage,
    в первый раз он отвечате вместе с first_updated_at.
    Проверяем, что периодик делает второй запрос с полученным
    first_updated_at с учетом коррекции из конфига
    Проверяем, что плейс с business=zapravki не попадает в базу
    а плейсы c business=shop и business=restaurant попадают
    Проверяем что last_updated_at остался в таблице catalog_state
    """

    @testpoint('components:place-update-periodic-finished')
    def catalog_periodic_finished(arg):
        pass

    places = list(gen_place(i) for i in range(3))
    non_shop_and_restaurant_place = gen_place(1000, business='zapravki')
    places.append(gen_place(1000, business='restaurant'))

    first_updated_at = dateutil.parser.parse('2020-10-26T10:00:00+03:00')
    corrected_first_updated_at = first_updated_at - datetime.timedelta(
        seconds=UPDATES_CORRECTION,
    )
    second_updated_at = dateutil.parser.parse('2020-10-26T11:00:00+03:00')
    corrected_second_updated_at = second_updated_at - datetime.timedelta(
        seconds=UPDATES_CORRECTION,
    )
    last_updated_at = dateutil.parser.parse('2020-10-26T12:00:00+03:00')

    # multiline path just to pass flake8
    @mockserver.json_handler(
        (
            '/eats-catalog-storage'
            '/internal/eats-catalog-storage/v1'
            '/search/places/updates'
        ),
    )
    def _catalog_storage(request):
        request_json = request.json
        assert request_json['limit'] == UPDATES_LIMIT
        # first request
        if 'updated_at' not in request_json:
            return {
                'last_updated_at': first_updated_at.isoformat(),
                'payload': {
                    'places': [places[0], non_shop_and_restaurant_place],
                },
            }
        # second request
        actual_first_updated_at = dateutil.parser.parse(
            request_json['updated_at'],
        )
        if actual_first_updated_at == corrected_first_updated_at:
            return {
                'last_updated_at': second_updated_at.isoformat(),
                'payload': {'places': places[1:4]},
            }
        # third request
        actual_last_updated_at = dateutil.parser.parse(
            request_json['updated_at'],
        )
        assert actual_last_updated_at == corrected_second_updated_at
        return {
            'last_updated_at': last_updated_at.isoformat(),
            'payload': {'places': []},
        }

    metric = await taxi_eats_full_text_search_monitor.get_metric(
        'place_update_statistics',
    )
    old_places_count = metric['got_places_count']
    expected_places_count = len(places)

    await taxi_eats_full_text_search.run_task('place-update-periodic')
    result = await catalog_periodic_finished.wait_call()
    assert result['arg'] == expected_places_count

    # Тестируем метрики
    metric = await taxi_eats_full_text_search_monitor.get_metric(
        'place_update_statistics',
    )
    new_places_count = metric['got_places_count']
    assert metric['has_error'] == 0
    assert new_places_count - old_places_count == expected_places_count

    cursor = pgsql['eats_full_text_search_indexer'].cursor()
    cursor.execute(
        """
        SELECT
            place_id,
            place_slug,
            enabled
        FROM
            fts.place
        ORDER BY place_id
    """,
    )
    place_state_data = list(
        {'place_id': row[0], 'place_slug': row[1], 'enabled': row[2]}
        for row in cursor
    )

    assert len(place_state_data) == len(places)

    for expected, actual in zip(places, place_state_data):
        for key, value in actual.items():
            assert value == expected[key]

    cursor.execute(
        """
        SELECT
            updated_at
        FROM
            fts.place_update_state
        ORDER BY id
        LIMIT 1""",
    )
    actual_updated_at = list(row[0] for row in cursor)[0]
    assert last_updated_at == actual_updated_at


@pytest.mark.config(
    EATS_FULL_TEXT_SEARCH_PLACE_UPDATE_SETTINGS={
        'full_update_interval': 7200,
        'incremental_update_interval': 3600,
        'enable': True,
        'enable_check_interval': 60,
    },
)
@pytest.mark.config(
    EATS_FULL_TEXT_SEARCH_CATALOG_STORAGE_REQUEST_SETTINGS={
        'updates_limit': UPDATES_LIMIT,
        'updates_correction': UPDATES_CORRECTION,
    },
)
async def test_catalog_storage_periodic_fail(
        testpoint,
        taxi_eats_full_text_search,
        taxi_eats_full_text_search_monitor,
        mockserver,
        pgsql,
):
    """
    Проверяем поведение при ошибке в запросе к catalog-storage
    """

    @testpoint('components:place-update-periodic-finished')
    def catalog_periodic_finished(arg):
        pass

    @mockserver.json_handler(
        (
            '/eats-catalog-storage'
            '/internal/eats-catalog-storage/v1'
            '/search/places/updates'
        ),
    )
    def _catalog_storage(request):
        return mockserver.make_response(status=500)

    expected_places_count = 0

    await taxi_eats_full_text_search.run_task('place-update-periodic')
    result = await catalog_periodic_finished.wait_call()
    assert result['arg'] == expected_places_count

    # Тестируем метрики
    metric = await taxi_eats_full_text_search_monitor.get_metric(
        'place_update_statistics',
    )
    places_count = metric['got_places_count']
    assert metric['has_error'] == 1
    assert places_count == expected_places_count

    cursor = pgsql['eats_full_text_search_indexer'].cursor()
    cursor.execute(
        """
        SELECT
            place_id,
            place_slug,
            enabled
        FROM
            fts.place
        ORDER BY place_id
    """,
    )
    place_state_data = list(
        {'place_id': row[0], 'place_slug': row[1], 'enabled': row[2]}
        for row in cursor
    )

    assert len(place_state_data) == expected_places_count
