import copy

import pytest

from tests_eats_products import utils


PERIODIC_NAME = 'places-synchronizer'

DEFAULT_COUNTRY = {
    'id': 1,
    'name': 'Russia',
    'code': 'ru',
    'currency': {'sign': '₽', 'code': 'RUB'},
}

NEW_PLACES = [
    {
        'brand_id': 5,
        'place_id': 1,
        'place_slug': 'new_place1',
        'is_enabled': True,
        'business': 'shop',
        'country': DEFAULT_COUNTRY,
    },
    {
        'brand_id': 5,
        'place_id': 2,
        'place_slug': 'new_place2',
        'is_enabled': True,
        'business': 'shop',
        'country': DEFAULT_COUNTRY,
    },
    {
        'brand_id': 5,
        'place_id': 8,
        'place_slug': 'place_to_change_brand',
        'is_enabled': True,
        'business': 'shop',
        'country': DEFAULT_COUNTRY,
    },
    {
        'brand_id': 6,
        'place_id': 3,
        'place_slug': 'new_place3',
        'is_enabled': True,
        'business': 'shop',
        'country': DEFAULT_COUNTRY,
    },
    {
        'brand_id': 6,
        'place_id': 4,
        'place_slug': 'new_place4',
        'is_enabled': True,
        'business': 'shop',
        'country': DEFAULT_COUNTRY,
    },
]


def add_default_brands_and_places(sql_add_brand, sql_add_place):
    sql_add_brand(5, 'slug5', True)
    sql_add_brand(6, 'slug6', True)
    sql_add_brand(7, 'slug7', False)

    sql_add_place(1, 'place1', 5, True, 'KZT', '₸')
    sql_add_place(5, 'place5', 5, True)
    sql_add_place(6, 'place6', 6, False)
    sql_add_place(7, 'place7', 7, True)
    sql_add_place(8, 'place_to_change_brand', 7, True)


def mock_core_retail_brand_places(mockserver, new_places):
    @mockserver.json_handler(utils.Handlers.CORE_RETAIL_BRAND_PLACES)
    def _mock_core_retail_brand_places(request):
        places = [
            place
            for place in new_places
            if str(place['brand_id']) == request.query['brand_id']
        ]
        return {
            'places': [
                {
                    'id': str(place['place_id']),
                    'slug': place['place_slug'],
                    'enabled': place['is_enabled'],
                    'parser_enabled': True,
                }
                for place in places
            ],
            'meta': {'limit': len(places)},
        }


def mock_catalog_storage_places(mockserver, new_places):
    @mockserver.json_handler(utils.Handlers.PLACES_BY_PARAMS)
    def _mock_catalog_storage_places(request):
        assert set(request.json['projection']) == {
            'slug',
            'business',
            'enabled',
            'country',
        }
        return {
            'places': [
                {
                    'id': place['place_id'],
                    'revision_id': 0,
                    'updated_at': '2020-04-28T12:00:00+03:00',
                    'slug': place['place_slug'],
                    'enabled': place['is_enabled'],
                    'business': place['business'],
                    'country': place['country'],
                }
                for place in new_places
                if place['brand_id'] == request.json['brand_id']
            ],
        }


def sorted_places_by_id(places):
    return sorted(places, key=lambda item: item['id'])


def sql_get_places(pgsql, with_currency=False):
    cursor = pgsql['eats_products'].cursor()
    cursor.execute(
        f"""
        select
            place_id,
            slug,
            brand_id,
            is_enabled,
            currency_code,
            currency_sign
        from eats_products.place
        """,
    )
    result = []
    for place in cursor:
        item = {
            'id': place[0],
            'slug': place[1],
            'brand_id': place[2],
            'is_enabled': place[3],
        }
        if with_currency:
            item['currency_code'] = place[4]
            item['currency_sign'] = place[5]
        result.append(item)

    return result


@pytest.mark.pgsql('eats_products', files=['fill_data_disable_all.sql'])
async def test_places_disable_all(
        pgsql, testpoint, taxi_eats_products, load_json,
):
    @testpoint('eats_products::places-synchronizer-disable-all')
    def periodic_finished(arg):
        pass

    await taxi_eats_products.run_distlock_task(PERIODIC_NAME)
    periodic_finished.next_call()

    sql_places = sql_get_places(pgsql)
    expected_places = load_json('expected_places_disable_all.json')
    assert sorted_places_by_id(sql_places) == expected_places


@utils.PARAMETRIZE_BRAND_PLACES_SOURCE
@pytest.mark.pgsql('eats_products', files=['fill_data.sql'])
async def test_places_sync_handler(
        pgsql,
        mockserver,
        testpoint,
        taxi_eats_products,
        load_json,
        use_catalog_storage,
):
    """
    Тест проверяет ответ ручек /v1/brand/places/retrieve и
    /internal/eats-catalog-storage/v1/search/places-by-params
    """
    if use_catalog_storage:
        mock_catalog_storage_places(mockserver, NEW_PLACES)
    else:
        mock_core_retail_brand_places(mockserver, NEW_PLACES)

    @testpoint('eats_products::places-synchronizer-finished')
    def periodic_finished(arg):
        pass

    await taxi_eats_products.run_distlock_task(PERIODIC_NAME)
    periodic_finished.next_call()

    sql_places = sql_get_places(pgsql)
    assert sorted_places_by_id(sql_places) == load_json('expected_places.json')


@utils.PARAMETRIZE_BRAND_PLACES_SOURCE
@pytest.mark.pgsql('eats_products', files=['fill_data.sql'])
async def test_places_sync_handler_write_enabled_false(
        pgsql,
        mockserver,
        testpoint,
        taxi_eats_products,
        load_json,
        stq,
        use_catalog_storage,
):
    """
    Тест проверяет:
    1. Если в ответе у плейса стоит признак enabled=false,
    то он все равно запишется в БД, только с признаком is_enabled=false
    2. stq по обновлению маппингов запускается для новых плейсов,
    не важно включены они или нет.
    """
    new_places = copy.deepcopy(NEW_PLACES)
    new_places[0]['is_enabled'] = False
    new_places[1]['is_enabled'] = False
    if use_catalog_storage:
        mock_catalog_storage_places(mockserver, new_places)
    else:
        mock_core_retail_brand_places(mockserver, new_places)

    @testpoint('eats_products::places-synchronizer-finished')
    def periodic_finished(arg):
        pass

    await taxi_eats_products.run_distlock_task(PERIODIC_NAME)
    periodic_finished.next_call()

    sql_places = sql_get_places(pgsql)
    expected_places = load_json('expected_places.json')
    expected_places[0]['is_enabled'] = False
    expected_places[1]['is_enabled'] = False
    assert sorted_places_by_id(sql_places) == expected_places

    # для place_id которых нет в бд принудительно запускается stq
    # eats_products_update_nomenclature_product_mapping
    places = [4, 3, 2]
    assert (
        stq.eats_products_update_nomenclature_product_mapping.times_called
        == len(places)
    )
    for place_id in places:
        task_info = (
            stq.eats_products_update_nomenclature_product_mapping.next_call()
        )
        assert task_info['kwargs']['place_id'] == str(place_id)


@pytest.mark.parametrize(
    'batch_size, expected_call_times', [(1, 5), (2, 3), (3, 2), (10, 2)],
)
@pytest.mark.pgsql('eats_products', files=['fill_data.sql'])
async def test_places_sync_handler_batch_request(
        mockserver,
        testpoint,
        taxi_eats_products,
        taxi_config,
        batch_size,
        expected_call_times,
        pgsql,
        load_json,
):
    """
    Тест проверяет, что запросы в кору происходят батчами
    """
    settings = {'brand_places_retrieve_batch_size': batch_size}
    taxi_config.set(EATS_PRODUCTS_CORE_REQUEST_SETTINGS=settings)

    @mockserver.json_handler(utils.Handlers.CORE_RETAIL_BRAND_PLACES)
    def _mock_core_retail_brand_places(request):
        cursor = request.json.get('cursor')
        limit = request.json.get('limit')

        places = [
            place
            for place in NEW_PLACES
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

    @testpoint('eats_products::places-synchronizer-finished')
    def periodic_finished(arg):
        pass

    await taxi_eats_products.run_distlock_task(PERIODIC_NAME)
    periodic_finished.next_call()

    assert _mock_core_retail_brand_places.times_called == expected_call_times

    sql_places = sql_get_places(pgsql)
    expected_places = load_json('expected_places.json')

    assert sorted_places_by_id(sql_places) == expected_places


@pytest.mark.config(
    EATS_PRODUCTS_CORE_REQUEST_SETTINGS=(
        {'use_catalog_storage_for_retrieve_places': True}
    ),
)
@pytest.mark.parametrize(
    'wrong_value',
    ['none_slug', 'none_enabled', 'none_business', 'none_country', 'store'],
)
@pytest.mark.pgsql('eats_products', files=['fill_data.sql'])
async def test_places_sync_catalog_storage_handler(
        pgsql,
        mockserver,
        testpoint,
        taxi_eats_products,
        load_json,
        wrong_value,
):
    """
    Тест проверяет, что некорректные заведения из ответа ручки
    /internal/eats-catalog-storage/v1/search/places-by-params не будут
    сохранены в бд
    """
    new_places = copy.deepcopy(NEW_PLACES)
    new_places.append(
        {
            'brand_id': 6,
            'place_id': 5,
            'place_slug': None if wrong_value == 'none_slug' else 'new_place5',
            'is_enabled': None if wrong_value == 'none_enabled' else True,
            'country': (
                None if wrong_value == 'none_country' else DEFAULT_COUNTRY
            ),
            'business': (
                None
                if wrong_value == 'none_business'
                else ('store' if wrong_value == 'store' else 'shop')
            ),
        },
    )
    mock_catalog_storage_places(mockserver, new_places)

    @testpoint('eats_products::places-synchronizer-finished')
    def periodic_finished(arg):
        pass

    await taxi_eats_products.run_distlock_task(PERIODIC_NAME)
    periodic_finished.next_call()

    sql_places = sql_get_places(pgsql)
    assert sorted_places_by_id(sql_places) == load_json('expected_places.json')


@pytest.mark.config(
    EATS_PRODUCTS_CORE_REQUEST_SETTINGS=(
        {'use_catalog_storage_for_retrieve_places': True}
    ),
)
@pytest.mark.pgsql('eats_products', files=[])
async def test_places_sync_catalog_storage_bad_response(
        pgsql,
        mockserver,
        testpoint,
        taxi_eats_products,
        sql_add_place,
        sql_add_brand,
):
    """
    Тест проверяет, что при ошибки в ручке для какого-либо бренда, результат
    остальных будет сохранен корректно
    """
    add_default_brands_and_places(sql_add_brand, sql_add_place)

    @mockserver.json_handler(utils.Handlers.PLACES_BY_PARAMS)
    def _mock_catalog_storage_places(request):
        if request.json['brand_id'] == 6:
            raise mockserver.NetworkError()
        return {
            'places': [
                {
                    'id': place['place_id'],
                    'revision_id': 0,
                    'updated_at': '2020-04-28T12:00:00+03:00',
                    'slug': place['place_slug'],
                    'enabled': place['is_enabled'],
                    'business': place['business'],
                    'country': DEFAULT_COUNTRY,
                }
                for place in NEW_PLACES
                if place['brand_id'] == request.json['brand_id']
            ],
        }

    @testpoint('eats_products::places-synchronizer-finished')
    def periodic_finished(arg):
        pass

    await taxi_eats_products.run_distlock_task(PERIODIC_NAME)
    periodic_finished.next_call()

    assert {place['id'] for place in sql_get_places(pgsql)} == {
        1,
        2,
        5,
        6,
        7,
        8,
    }


@pytest.mark.config(
    EATS_PRODUCTS_CORE_REQUEST_SETTINGS=(
        {'use_catalog_storage_for_retrieve_places': True}
    ),
)
@pytest.mark.pgsql('eats_products', files=[])
async def test_places_sync_catalog_storage_currencies(
        pgsql,
        mockserver,
        testpoint,
        taxi_eats_products,
        sql_add_place,
        sql_add_brand,
):
    """
    Тест проверяет, что валюта корректно сохраняется в БД
    """

    new_places = copy.deepcopy(NEW_PLACES)
    country = copy.deepcopy(new_places[4]['country'])
    country['currency']['sign'] = 'руб.'
    country['currency']['code'] = 'BYN'
    new_places[4]['country'] = country

    mock_catalog_storage_places(mockserver, new_places)
    add_default_brands_and_places(sql_add_brand, sql_add_place)

    @testpoint('eats_products::places-synchronizer-finished')
    def periodic_finished(arg):
        pass

    await taxi_eats_products.run_distlock_task(PERIODIC_NAME)
    periodic_finished.next_call()

    places = {place['id']: place for place in sql_get_places(pgsql, True)}
    for id_ in (1, 2, 3, 8):
        assert places[id_]['currency_code'] == 'RUB'
        assert places[id_]['currency_sign'] == '₽'
    assert places[4]['currency_code'] == 'BYN'
    assert places[4]['currency_sign'] == 'руб.'
