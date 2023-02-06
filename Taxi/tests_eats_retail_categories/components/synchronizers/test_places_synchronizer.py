import copy
import datetime

import pytest

from tests_eats_retail_categories import utils

BRAND_IDS = [1, 2]
PLACE_IDS = [1, 2, 3, 4, 5]
PLACE_SLUGS = ['place_1', 'place_2', 'place_3', 'place_4', 'place_5']

PERIODIC_NAME = 'places-synchronizer'

NEW_PLACES = [
    {
        'brand_id': BRAND_IDS[0],
        'place_id': PLACE_IDS[0],
        'place_slug': PLACE_SLUGS[0],
        'is_enabled': True,
    },
    {
        'brand_id': BRAND_IDS[1],
        'place_id': PLACE_IDS[1],
        'place_slug': PLACE_SLUGS[1],
        'is_enabled': True,
    },
    {
        'brand_id': BRAND_IDS[1],
        'place_id': PLACE_IDS[2],
        'place_slug': PLACE_SLUGS[2],
        'is_enabled': True,
    },
]


def mock_core_retail_brand_places(mockserver, new_places):
    @mockserver.json_handler(utils.Handlers.CORE_RETAIL_BRAND_PLACES)
    def _mock_core_retail_brand_places(request):
        cursor = request.json.get('cursor')
        limit = request.json.get('limit')

        places = [
            place
            for place in new_places
            if str(place['brand_id']) == request.query['brand_id']
        ]
        places_ids = [str(place['place_id']) for place in places]
        if cursor:
            places = places[places_ids.index(cursor) :]
            places_ids = places_ids[places_ids.index(cursor) :]

        result = places[:limit]
        cursor = None if len(places_ids) <= limit else str(places_ids[limit])

        return {
            'places': [
                {
                    'id': str(place['place_id']),
                    'slug': place['place_slug'],
                    'enabled': place['is_enabled'],
                    'parser_enabled': True,
                }
                for place in result
            ],
            'meta': {'limit': limit, 'cursor': cursor},
        }

    return _mock_core_retail_brand_places


def sorted_places_by_id(places):
    return sorted(places, key=lambda item: item['id'])


def make_place_info(_id, slug, brand_id, is_enabled):
    return {
        'id': _id,
        'slug': slug,
        'brand_id': brand_id,
        'is_enabled': is_enabled,
    }


def sql_get_places(get_cursor):
    cursor = get_cursor()
    cursor.execute(
        f"""
        SELECT id, slug, brand_id, is_enabled
        FROM eats_retail_categories.places
        """,
    )
    return [
        make_place_info(place[0], place[1], place[2], place[3])
        for place in cursor
    ]


def sql_get_places_updated_at(get_cursor):
    cursor = get_cursor()
    cursor.execute(
        f"""
            SELECT id, updated_at
            FROM eats_retail_categories.places
            """,
    )
    return [{'id': place[0], 'updated_at': place[1]} for place in cursor]


async def test_places_synchronizer_disable_all(
        get_cursor,
        testpoint,
        taxi_eats_retail_categories,
        pg_add_place,
        pg_add_brand,
):
    # Проверяется, что в тестпоинте places-synchronizer-disable-all
    # все магазины становяется выключенными
    for brand_id in BRAND_IDS:
        pg_add_brand(brand_id, 'brand_slug', is_enabled=False)
    pg_add_place(PLACE_IDS[0], PLACE_SLUGS[0], BRAND_IDS[0], is_enabled=True)
    pg_add_place(PLACE_IDS[1], PLACE_SLUGS[1], BRAND_IDS[1], is_enabled=False)
    pg_add_place(PLACE_IDS[2], PLACE_SLUGS[2], BRAND_IDS[1], is_enabled=True)

    @testpoint('eats_retail_categories::places-synchronizer-disable-all')
    def periodic_finished(arg):
        pass

    await taxi_eats_retail_categories.run_distlock_task(PERIODIC_NAME)
    periodic_finished.next_call()

    sql_places = sql_get_places(get_cursor)
    expected_places = [
        make_place_info(
            PLACE_IDS[0], PLACE_SLUGS[0], BRAND_IDS[0], is_enabled=False,
        ),
        make_place_info(
            PLACE_IDS[1], PLACE_SLUGS[1], BRAND_IDS[1], is_enabled=False,
        ),
        make_place_info(
            PLACE_IDS[2], PLACE_SLUGS[2], BRAND_IDS[1], is_enabled=False,
        ),
    ]
    assert sorted_places_by_id(sql_places) == expected_places


async def test_places_synchronizer_new_places_upserted(
        get_cursor,
        mockserver,
        testpoint,
        taxi_eats_retail_categories,
        pg_add_brand,
        pg_add_place,
):
    # Проверяется, что новые магазины будут добавлены в БД, а старые обновлены
    for brand_id in BRAND_IDS:
        pg_add_brand(brand_id, 'brand_slug')
    pg_add_place(PLACE_IDS[0], PLACE_SLUGS[0], BRAND_IDS[0], is_enabled=True)
    pg_add_place(PLACE_IDS[1], PLACE_SLUGS[1], BRAND_IDS[1], is_enabled=False)

    mock_core_retail_brand_places(mockserver, NEW_PLACES)

    @testpoint('eats_retail_categories::places-synchronizer-finished')
    def periodic_finished(arg):
        pass

    await taxi_eats_retail_categories.run_distlock_task(PERIODIC_NAME)
    periodic_finished.next_call()

    sql_places = sql_get_places(get_cursor)
    expected_places = [
        make_place_info(
            PLACE_IDS[0], PLACE_SLUGS[0], BRAND_IDS[0], is_enabled=True,
        ),
        make_place_info(
            PLACE_IDS[1], PLACE_SLUGS[1], BRAND_IDS[1], is_enabled=True,
        ),
        make_place_info(
            PLACE_IDS[2], PLACE_SLUGS[2], BRAND_IDS[1], is_enabled=True,
        ),
    ]
    assert sorted_places_by_id(sql_places) == expected_places


async def test_places_synchronizer_disabled_by_core(
        get_cursor,
        mockserver,
        testpoint,
        taxi_eats_retail_categories,
        pg_add_brand,
        pg_add_place,
):
    """
    Проверяется:
    1. если в ответе коры у плейса стоит признак enabled=false,
    то он все равно запишется в БД, только с признаком is_enabled=false
    2. если в ответе коры нет плейса, который есть в БД,
    то у него is_enabled будет false
    """
    for brand_id in BRAND_IDS:
        pg_add_brand(brand_id, 'brand_slug')
    pg_add_place(PLACE_IDS[0], PLACE_SLUGS[0], BRAND_IDS[0], is_enabled=True)
    pg_add_place(PLACE_IDS[1], PLACE_SLUGS[1], BRAND_IDS[1], is_enabled=False)
    pg_add_place(PLACE_IDS[2], PLACE_SLUGS[2], BRAND_IDS[1], is_enabled=True)

    new_places = copy.deepcopy(NEW_PLACES[:2])
    new_places[0]['is_enabled'] = False

    mock_core_retail_brand_places(mockserver, new_places)

    @testpoint('eats_retail_categories::places-synchronizer-finished')
    def periodic_finished(arg):
        pass

    await taxi_eats_retail_categories.run_distlock_task(PERIODIC_NAME)
    periodic_finished.next_call()

    sql_places = sql_get_places(get_cursor)
    expected_places = [
        make_place_info(
            PLACE_IDS[0], PLACE_SLUGS[0], BRAND_IDS[0], is_enabled=False,
        ),
        make_place_info(
            PLACE_IDS[1], PLACE_SLUGS[1], BRAND_IDS[1], is_enabled=True,
        ),
        make_place_info(
            PLACE_IDS[2], PLACE_SLUGS[2], BRAND_IDS[1], is_enabled=False,
        ),
    ]
    assert sorted_places_by_id(sql_places) == expected_places


@pytest.mark.parametrize(
    'batch_size, expected_call_times', [(1, 5), (2, 3), (3, 2), (10, 1)],
)
async def test_places_synchronizer_handler_batch_request(
        mockserver,
        testpoint,
        taxi_eats_retail_categories,
        taxi_config,
        get_cursor,
        pg_add_brand,
        pg_add_place,
        batch_size,
        expected_call_times,
):
    """
    Тест проверяет, что запросы в кору происходят батчами
    """
    pg_add_brand(BRAND_IDS[0], 'brand_slug')
    pg_add_place(PLACE_IDS[0], PLACE_SLUGS[0], BRAND_IDS[0], is_enabled=True)
    pg_add_place(PLACE_IDS[1], PLACE_SLUGS[1], BRAND_IDS[0], is_enabled=False)

    settings = {'places_retrieve_batch_size': batch_size}
    taxi_config.set(EATS_RETAIL_CATEGORIES_CORE_REQUESTS_SETTINGS=settings)
    new_places = []
    expected_places = []
    for i in range(5):
        new_places.append(
            {
                'brand_id': BRAND_IDS[0],
                'place_id': PLACE_IDS[i],
                'place_slug': PLACE_SLUGS[i],
                'is_enabled': True,
            },
        )
        expected_places.append(
            make_place_info(
                PLACE_IDS[i], PLACE_SLUGS[i], BRAND_IDS[0], is_enabled=True,
            ),
        )
    mock = mock_core_retail_brand_places(mockserver, new_places)

    @testpoint('eats_retail_categories::places-synchronizer-finished')
    def periodic_finished(arg):
        pass

    await taxi_eats_retail_categories.run_distlock_task(PERIODIC_NAME)
    periodic_finished.next_call()

    assert mock.times_called == expected_call_times

    sql_places = sql_get_places(get_cursor)

    assert sorted_places_by_id(sql_places) == expected_places


async def test_places_synchronizer_updated_at(
        get_cursor,
        mockserver,
        testpoint,
        taxi_eats_retail_categories,
        pg_add_brand,
        pg_add_place,
):
    """
    Проверяется поле updated_at при обновлении магазинов:
    1. новый магазин: updated_at = now()
    2. обновленный магазин: updated_at = now()
    3. удаленный магазин: поле updated_at не изменяется
    """
    updated_at = '2021-01-01T00:00:00+00:00'
    updated_timestamp = datetime.datetime.fromisoformat(updated_at).timestamp()
    now = datetime.datetime.now().timestamp()

    for brand_id in BRAND_IDS:
        pg_add_brand(brand_id, 'brand_slug')
    pg_add_place(
        PLACE_IDS[0],
        PLACE_SLUGS[0],
        BRAND_IDS[0],
        is_enabled=True,
        updated_at=updated_at,
    )
    pg_add_place(
        PLACE_IDS[1],
        PLACE_SLUGS[1],
        BRAND_IDS[0],
        is_enabled=False,
        updated_at=updated_at,
    )
    pg_add_place(
        PLACE_IDS[2],
        PLACE_SLUGS[2],
        BRAND_IDS[0],
        is_enabled=False,
        updated_at=updated_at,
    )

    new_places = copy.deepcopy(NEW_PLACES[:2])
    new_places.append(
        {
            'brand_id': BRAND_IDS[0],
            'place_id': PLACE_IDS[3],
            'place_slug': PLACE_SLUGS[3],
            'is_enabled': True,
        },
    )

    mock_core_retail_brand_places(mockserver, new_places)

    @testpoint('eats_retail_categories::places-synchronizer-finished')
    def periodic_finished(arg):
        pass

    await taxi_eats_retail_categories.run_distlock_task(PERIODIC_NAME)
    periodic_finished.next_call()

    places = sorted_places_by_id(sql_get_places_updated_at(get_cursor))
    # точно такой же, как в БД
    assert places[0]['updated_at'].timestamp() >= now
    # измененный в БД
    assert places[1]['updated_at'].timestamp() >= now
    # удаленный из БД
    assert places[2]['updated_at'].timestamp() == updated_timestamp
    # новый магазин
    assert places[3]['updated_at'].timestamp() >= now
