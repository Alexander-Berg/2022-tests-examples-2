import datetime

import pytest
import pytz

from testsuite.utils import ordered_object


async def test_depots_bad_request(taxi_overlord_catalog):
    response = await taxi_overlord_catalog.get('/admin/catalog/v1/depots')
    assert response.status_code == 400
    assert response.json() == {
        'code': 'BAD_REQUEST',
        'message': 'Neither city_id nor country nor search provided',
    }


@pytest.mark.parametrize('city_id', ['bad', '100500', '55501'])
@pytest.mark.pgsql('overlord_catalog', files=['add_stocks.sql'])
async def test_depots_not_found_by_city(
        taxi_overlord_catalog, city_id, mock_grocery_depots,
):
    mock_grocery_depots.load_json(
        'gdepots-depots-default.json', 'gdepots-zones-default.json',
    )
    response = await taxi_overlord_catalog.get(
        '/admin/catalog/v1/depots',
        params={'city_id': city_id, 'search': 'never_gonna_find_me'},
    )
    if city_id != '55501':
        assert response.status_code == 404
        assert response.json() == {
            'code': 'CITY_NOT_FOUND',
            'message': 'No such city: ' + city_id,
        }
    else:
        assert response.status_code == 200
        assert response.json() == {'depots': []}


@pytest.mark.parametrize('country', ['bad', 'RUS'])
@pytest.mark.pgsql('overlord_catalog', files=['add_stocks.sql'])
async def test_depots_not_found_by_country(
        taxi_overlord_catalog, country, mock_grocery_depots,
):
    mock_grocery_depots.load_json(
        'gdepots-depots-default.json', 'gdepots-zones-default.json',
    )
    response = await taxi_overlord_catalog.get(
        '/admin/catalog/v1/depots',
        params={'country': country, 'search': 'never_gonna_find_me'},
    )
    if country == 'RUS':
        assert response.status_code == 200
        assert response.json() == {'depots': []}
    else:
        assert response.status_code == 404
        assert response.json() == {
            'code': 'COUNTRY_NOT_FOUND',
            'message': 'No such country: ' + country,
        }


def _update_depot_source(pgsql, source):
    db = pgsql['overlord_catalog']
    cursor = db.cursor()
    cursor.execute(
        f"""UPDATE catalog_wms.depots
            SET source = '{source}';""",
    )


def deep_sort(data):
    data['depots'].sort(key=lambda x: x['wms_id'])
    for depot in data['depots']:
        for zone in depot['detailed_zones']:
            for points in zone['geozone']['coordinates'][0]:
                points.sort(key=lambda coord: coord['lat'])
        depot['detailed_zones'].sort(
            key=lambda x: (
                x['status'],
                x['zoneType'],
                x['timetable'][0]['working_hours']['from']['hour'],
                x['geozone']['coordinates'][0][0][0]['lat'],
            ),
            reverse=True,
        )


@pytest.mark.config(
    OVERLORD_CATALOG_REGION_IDS_BY_COUNTRY_ID=[
        {
            'country_id': 225,
            'region_ids': [213, 1, 2, 47, 43, 54, 63, 35, 39, 65],
        },
        {'country_id': 181, 'region_ids': [131]},
        {'country_id': 124, 'region_ids': [10502]},
        {'country_id': 102, 'region_ids': [10393]},
    ],
)
@pytest.mark.parametrize(
    'params, expected_json_file',
    [({'country': 'RUS'}, 'oc_testing_expected.json')],
)
@pytest.mark.now('2021-11-11T13:15+00:00')
async def test_depots_in_testing(
        taxi_overlord_catalog,
        params,
        expected_json_file,
        mock_grocery_depots,
        load_json,
):
    mock_grocery_depots.load_json(
        'gdepots-depots-testing.json', 'gdepots-zones-testing.json',
    )
    response = await taxi_overlord_catalog.get(
        '/admin/catalog/v1/depots', params=params,
    )
    assert response.status_code == 200
    expected = load_json(expected_json_file)
    resp_json = response.json()
    deep_sort(resp_json)
    deep_sort(expected)
    assert resp_json == expected


@pytest.mark.parametrize(
    'params, expected_depots',
    [
        (
            {'city_id': '55501'},
            [
                {
                    'store_id': '99999901',
                    'wms_id': 'id-99999901',
                    'slug': 'test_lavka_1',
                    'name': '"Партвешок За Полтишок" на Никольской',
                    'city_id': '55501',
                    'stocks_count': 3,
                },
                {
                    'store_id': '99999902',
                    'wms_id': 'id-99999902',
                    'slug': 'test_lavka_2',
                    'name': '"Партвешок За Полтишок" на Скоробогадько 17',
                    'city_id': '55501',
                    'stocks_count': 0,
                },
            ],
        ),
        (
            {'search': 'test_lavka_1'},
            [
                {
                    'store_id': '99999901',
                    'wms_id': 'id-99999901',
                    'slug': 'test_lavka_1',
                    'name': '"Партвешок За Полтишок" на Никольской',
                    'city_id': '55501',
                    'stocks_count': 3,
                },
            ],
        ),
        (
            {'search': 'test_lavka'},
            [
                {
                    'store_id': '99999901',
                    'wms_id': 'id-99999901',
                    'slug': 'test_lavka_1',
                    'name': '"Партвешок За Полтишок" на Никольской',
                    'city_id': '55501',
                    'stocks_count': 3,
                },
                {
                    'store_id': '99999902',
                    'wms_id': 'id-99999902',
                    'slug': 'test_lavka_2',
                    'name': '"Партвешок За Полтишок" на Скоробогадько 17',
                    'city_id': '55501',
                    'stocks_count': 0,
                },
                {
                    'store_id': '99999903',
                    'wms_id': 'id-99999903',
                    'slug': 'test_lavka_3',
                    'name': '"Партвешок За Полтишок" на Внутреутробной',
                    'city_id': '55502',
                    'stocks_count': 0,
                },
                {
                    'store_id': '99999904',
                    'wms_id': 'id-99999904',
                    'slug': 'test_lavka_4',
                    'name': '"Партвешок За Полтишок" на Седьмой-Восьмой 9',
                    'city_id': '55502',
                    'stocks_count': 0,
                },
            ],
        ),
        (
            {'search': '99999901'},
            [
                {
                    'store_id': '99999901',
                    'wms_id': 'id-99999901',
                    'slug': 'test_lavka_1',
                    'name': '"Партвешок За Полтишок" на Никольской',
                    'city_id': '55501',
                    'stocks_count': 3,
                },
            ],
        ),
        (
            {'search': '999999'},
            [
                {
                    'store_id': '99999901',
                    'wms_id': 'id-99999901',
                    'slug': 'test_lavka_1',
                    'name': '"Партвешок За Полтишок" на Никольской',
                    'city_id': '55501',
                    'stocks_count': 3,
                },
                {
                    'store_id': '99999902',
                    'wms_id': 'id-99999902',
                    'slug': 'test_lavka_2',
                    'name': '"Партвешок За Полтишок" на Скоробогадько 17',
                    'city_id': '55501',
                    'stocks_count': 0,
                },
                {
                    'store_id': '99999903',
                    'wms_id': 'id-99999903',
                    'slug': 'test_lavka_3',
                    'name': '"Партвешок За Полтишок" на Внутреутробной',
                    'city_id': '55502',
                    'stocks_count': 0,
                },
                {
                    'store_id': '99999904',
                    'wms_id': 'id-99999904',
                    'slug': 'test_lavka_4',
                    'name': '"Партвешок За Полтишок" на Седьмой-Восьмой 9',
                    'city_id': '55502',
                    'stocks_count': 0,
                },
            ],
        ),
        (
            {'search': '5'},
            [
                {
                    'store_id': '5',
                    'wms_id': 'id-5',
                    'slug': 'mixed_lavka_6',
                    'name': '"Партвешок За Полтишок" на Большой Пятой',
                    'city_id': '5',
                    'stocks_count': 0,
                },
                {
                    'store_id': '6',
                    'wms_id': 'id-6',
                    'slug': 'mixed_lavka_5',
                    'name': '"Партвешок За Полтишок" на Малой Шестой',
                    'city_id': '6',
                    'stocks_count': 0,
                },
            ],
        ),
        ({'search': 'never_gonna_find_me'}, []),
        (
            {'city_id': '55501', 'search': 'test_lavka'},
            [
                {
                    'store_id': '99999901',
                    'wms_id': 'id-99999901',
                    'slug': 'test_lavka_1',
                    'name': '"Партвешок За Полтишок" на Никольской',
                    'city_id': '55501',
                    'stocks_count': 3,
                },
                {
                    'store_id': '99999902',
                    'wms_id': 'id-99999902',
                    'slug': 'test_lavka_2',
                    'name': '"Партвешок За Полтишок" на Скоробогадько 17',
                    'city_id': '55501',
                    'stocks_count': 0,
                },
            ],
        ),
        ({'city_id': '55501', 'search': 'test_lavka_3'}, []),
        (
            {'search': 'на Малой Шестой'},
            [
                {
                    'store_id': '6',
                    'wms_id': 'id-6',
                    'slug': 'mixed_lavka_5',
                    'name': '"Партвешок За Полтишок" на Малой Шестой',
                    'city_id': '6',
                    'stocks_count': 0,
                },
            ],
        ),
    ],
)
@pytest.mark.pgsql('overlord_catalog', files=['default.sql', 'add_stocks.sql'])
async def test_depots_base(
        taxi_overlord_catalog,
        pgsql,
        params,
        expected_depots,
        mock_grocery_depots,
):
    mock_grocery_depots.load_json(
        'gdepots-depots-default.json', 'gdepots-zones-default.json',
    )
    _update_depot_source(pgsql, 'WMS')

    def _only_base_fields(doc):
        depots = []
        for depot in doc['depots']:
            depots.append(
                {
                    key: value
                    for key, value in depot.items()
                    if key
                    in (
                        'store_id',
                        'wms_id',
                        'slug',
                        'name',
                        'city_id',
                        'stocks_count',
                    )
                },
            )
        return {'depots': depots}

    response = await taxi_overlord_catalog.get(
        '/admin/catalog/v1/depots', params=params,
    )
    assert response.status_code == 200
    ordered_object.assert_eq(
        _only_base_fields(response.json()),
        {'depots': expected_depots},
        ['depots'],
    )


@pytest.mark.parametrize(
    'params, expected_depots',
    [
        (
            {'city_id': '55501'},
            [
                {
                    'store_id': '99999901',
                    'root_category_id': 'root-99999901',
                    'assortment_id': '99999901ASTMNT',
                    'price_list_id': '99999901PRLIST',
                    'stocks_count': 3,
                },
                {
                    'store_id': '99999902',
                    'root_category_id': 'root-99999902',
                    'assortment_id': '99999902ASTMNT',
                    'price_list_id': '99999902PRLIST',
                    'stocks_count': 0,
                },
            ],
        ),
        (
            {'search': 'test_lavka_1'},
            [
                {
                    'store_id': '99999901',
                    'root_category_id': 'root-99999901',
                    'assortment_id': '99999901ASTMNT',
                    'price_list_id': '99999901PRLIST',
                    'stocks_count': 3,
                },
            ],
        ),
        (
            {'search': 'test_lavka'},
            [
                {
                    'store_id': '99999901',
                    'root_category_id': 'root-99999901',
                    'assortment_id': '99999901ASTMNT',
                    'price_list_id': '99999901PRLIST',
                    'stocks_count': 3,
                },
                {
                    'store_id': '99999902',
                    'root_category_id': 'root-99999902',
                    'assortment_id': '99999902ASTMNT',
                    'price_list_id': '99999902PRLIST',
                    'stocks_count': 0,
                },
                {
                    'store_id': '99999903',
                    'root_category_id': 'root-99999903',
                    'assortment_id': '99999903ASTMNT',
                    'price_list_id': '99999903PRLIST',
                    'stocks_count': 0,
                },
                {
                    'store_id': '99999904',
                    'root_category_id': 'root-99999904',
                    'assortment_id': '99999904ASTMNT',
                    'price_list_id': '99999904PRLIST',
                    'stocks_count': 0,
                },
            ],
        ),
        (
            {'search': '99999901'},
            [
                {
                    'store_id': '99999901',
                    'root_category_id': 'root-99999901',
                    'assortment_id': '99999901ASTMNT',
                    'price_list_id': '99999901PRLIST',
                    'stocks_count': 3,
                },
            ],
        ),
        (
            {'search': '999999'},
            [
                {
                    'store_id': '99999901',
                    'root_category_id': 'root-99999901',
                    'assortment_id': '99999901ASTMNT',
                    'price_list_id': '99999901PRLIST',
                    'stocks_count': 3,
                },
                {
                    'store_id': '99999902',
                    'root_category_id': 'root-99999902',
                    'assortment_id': '99999902ASTMNT',
                    'price_list_id': '99999902PRLIST',
                    'stocks_count': 0,
                },
                {
                    'store_id': '99999903',
                    'root_category_id': 'root-99999903',
                    'assortment_id': '99999903ASTMNT',
                    'price_list_id': '99999903PRLIST',
                    'stocks_count': 0,
                },
                {
                    'store_id': '99999904',
                    'root_category_id': 'root-99999904',
                    'assortment_id': '99999904ASTMNT',
                    'price_list_id': '99999904PRLIST',
                    'stocks_count': 0,
                },
            ],
        ),
        (
            {'search': '5'},
            [
                {
                    'store_id': '5',
                    'root_category_id': 'root-5',
                    'assortment_id': '5ASTMNT',
                    'price_list_id': '5PRLIST',
                    'stocks_count': 0,
                },
                {
                    'store_id': '6',
                    'root_category_id': 'root-6',
                    'assortment_id': '6ASTMNT',
                    'price_list_id': '6PRLIST',
                    'stocks_count': 0,
                },
            ],
        ),
        ({'search': 'never_gonna_find_me'}, []),
        (
            {'city_id': '55501', 'search': 'test_lavka'},
            [
                {
                    'store_id': '99999901',
                    'root_category_id': 'root-99999901',
                    'assortment_id': '99999901ASTMNT',
                    'price_list_id': '99999901PRLIST',
                    'stocks_count': 3,
                },
                {
                    'store_id': '99999902',
                    'root_category_id': 'root-99999902',
                    'assortment_id': '99999902ASTMNT',
                    'price_list_id': '99999902PRLIST',
                    'stocks_count': 0,
                },
            ],
        ),
        ({'city_id': '55501', 'search': 'test_lavka_3'}, []),
        (
            {'search': 'на Малой Шестой'},
            [
                {
                    'store_id': '6',
                    'root_category_id': 'root-6',
                    'assortment_id': '6ASTMNT',
                    'price_list_id': '6PRLIST',
                    'stocks_count': 0,
                },
            ],
        ),
    ],
)
@pytest.mark.pgsql(
    'overlord_catalog',
    files=['default.sql', 'set_wms_menu_data.sql', 'add_stocks.sql'],
)
async def test_depots_menu_fields(
        taxi_overlord_catalog,
        pgsql,
        params,
        expected_depots,
        mock_grocery_depots,
):
    mock_grocery_depots.load_json(
        'gdepots-depots-default.json', 'gdepots-zones-default.json',
    )
    _update_depot_source(pgsql, 'WMS')

    def _only_menu_fields(doc):
        depots = []
        for depot in doc['depots']:
            depots.append(
                {
                    key: value
                    for key, value in depot.items()
                    if key
                    in (
                        'store_id',
                        'root_category_id',
                        'assortment_id',
                        'price_list_id',
                        'stocks_count',
                    )
                },
            )
        return {'depots': depots}

    response = await taxi_overlord_catalog.get(
        '/admin/catalog/v1/depots', params=params,
    )
    assert response.status_code == 200
    ordered_object.assert_eq(
        _only_menu_fields(response.json()),
        {'depots': expected_depots},
        ['depots'],
    )


@pytest.mark.pgsql(
    'overlord_catalog', files=['default.sql', 'set_wms_menu_data.sql'],
)
async def test_retrive_depots_by_ids(
        mock_grocery_depots, taxi_overlord_catalog, pgsql, load_json,
):
    mock_grocery_depots.setup(
        load_json('gdepots-depots-default.json'),
        load_json('gdepots-zones-default.json'),
    )
    expected_depots = [
        {
            'store_id': '99999901',
            'wms_id': 'id-99999901',
            'slug': 'test_lavka_1',
            'name': '"Партвешок За Полтишок" на Никольской',
            'city_id': '55501',
            'root_category_id': 'root-99999901',
            'assortment_id': '99999901ASTMNT',
            'price_list_id': '99999901PRLIST',
            'status': 'enabled',
        },
        {
            'store_id': '99999902',
            'wms_id': 'id-99999902',
            'slug': 'test_lavka_2',
            'name': '"Партвешок За Полтишок" на Скоробогадько 17',
            'city_id': '55501',
            'root_category_id': 'root-99999902',
            'assortment_id': '99999902ASTMNT',
            'price_list_id': '99999902PRLIST',
            'status': 'enabled',
        },
        {
            'store_id': '5',
            'wms_id': 'id-5',
            'slug': 'mixed_lavka_6',
            'name': '"Партвешок За Полтишок" на Большой Пятой',
            'city_id': '5',
            'root_category_id': 'root-5',
            'assortment_id': '5ASTMNT',
            'price_list_id': '5PRLIST',
            'status': 'enabled',
        },
        {
            'store_id': 'id-not-found',
            'slug': '',
            'name': 'Depot not found',
            'city_id': '',
            'status': 'not_found',
        },
        {
            'store_id': '6',
            'wms_id': 'id-6',
            'slug': 'mixed_lavka_5',
            'name': '"Партвешок За Полтишок" на Малой Шестой',
            'city_id': '6',
            'root_category_id': 'root-6',
            'assortment_id': '6ASTMNT',
            'price_list_id': '6PRLIST',
            'status': 'enabled',
        },
    ]

    _update_depot_source(pgsql, 'WMS')

    def _filter_fields(doc):
        depots = []
        for depot in doc['depots']:
            depots.append(
                {
                    key: value
                    for key, value in depot.items()
                    if key
                    in (
                        'store_id',
                        'wms_id',
                        'slug',
                        'name',
                        'city_id',
                        'root_category_id',
                        'assortment_id',
                        'price_list_id',
                        'status',
                        'stocks_count',
                    )
                },
            )
        return {'depots': depots}

    depot_ids = ['id-99999901', '99999902', 'id-5', 'id-not-found', '6']

    response = await taxi_overlord_catalog.post(
        '/admin/catalog/v1/depots-by-ids', json={'depot_ids': depot_ids},
    )
    assert response.status_code == 200
    result = _filter_fields(response.json())
    ordered_object.assert_eq(result, {'depots': expected_depots}, ['wms_id'])


def setup_grocery_depots_mock(taxi_overlord_catalog, mockserver):
    @mockserver.json_handler('/grocery-depots/internal/v1/depots/v1/depots')
    def _handle_depots(_request):
        return {
            'depots': [
                {
                    'depot_id': 'id-99999901',
                    'legacy_depot_id': '99999901',
                    'country_iso3': 'RUS',
                    'country_iso2': 'RU',
                    'region_id': 55501,
                    'timezone': 'Europe/Moscow',
                    'location': {'lat': 37.371618, 'lon': 55.840757},
                    'phone_number': '',
                    'currency': 'RUB',
                    'company_type': 'yandex',
                    'status': 'active',
                    'hidden': False,
                    'short_address': '"Партвешок За Полтишок" на Никольской',
                    'name': 'test_lavka_1',
                    'price_list_id': '99999901PRLIST',
                    'root_category_id': 'root-99999901',
                    'assortment_id': '99999901ASTMNT',
                },
            ],
            'errors': [],
        }

    @mockserver.json_handler('/grocery-depots/internal/v1/depots/v1/zones')
    def _handle_zones(_request):
        return {
            'zones': [
                {
                    'zone_id': '000000010000a001',
                    'depot_id': 'id-99999901',
                    'legacy_depot_id': '99999901',
                    'zone_type': 'pedestrian',
                    'zone_status': 'active',
                    'timetable': [
                        {
                            'day_type': 'Everyday',
                            'working_hours': {
                                'from': {'hour': 0, 'minute': 0},
                                'to': {'hour': 24, 'minute': 0},
                            },
                        },
                    ],
                    'geozone': {
                        'type': 'MultiPolygon',
                        'coordinates': [
                            [
                                [
                                    {'lat': 2, 'lon': 1},
                                    {'lat': 6, 'lon': 5},
                                    {'lat': 4, 'lon': 3},
                                ],
                            ],
                        ],
                    },
                },
            ],
        }


@pytest.mark.pgsql(
    'overlord_catalog', files=['default.sql', 'set_wms_menu_data.sql'],
)
async def test_retrive_depots_by_ids_from_gd(
        taxi_overlord_catalog, pgsql, mockserver,
):
    setup_grocery_depots_mock(taxi_overlord_catalog, mockserver)
    expected_depots = [
        {
            'store_id': '99999901',
            'wms_id': 'id-99999901',
            'slug': 'test_lavka_1',
            'name': '"Партвешок За Полтишок" на Никольской',
            'city_id': '55501',
            'root_category_id': 'root-99999901',
            'assortment_id': '99999901ASTMNT',
            'price_list_id': '99999901PRLIST',
            'status': 'enabled',
        },
    ]

    _update_depot_source(pgsql, 'WMS')

    def _filter_fields(doc):
        depots = []
        for depot in doc['depots']:
            depots.append(
                {
                    key: value
                    for key, value in depot.items()
                    if key
                    in (
                        'store_id',
                        'wms_id',
                        'slug',
                        'name',
                        'city_id',
                        'root_category_id',
                        'assortment_id',
                        'price_list_id',
                        'status',
                        'stocks_count',
                    )
                },
            )
        return {'depots': depots}

    depot_ids = ['id-99999901']

    response = await taxi_overlord_catalog.post(
        '/admin/catalog/v1/depots-by-ids', json={'depot_ids': depot_ids},
    )
    assert response.status_code == 200
    assert _filter_fields(response.json()) == {'depots': expected_depots}


@pytest.mark.parametrize(
    'search',
    [
        'perfect_for_trim',
        'erfect_for_trim',
        'perfect_for_tri',
        ' erfect_for_trim',
        'perfect_for_tri ',
        ' erfect_for_tri ',
        '666666',
        '66666',
        ' 66666',
        '66666 ',
        ' 6666 ',
    ],
)
@pytest.mark.pgsql('overlord_catalog', files=['add_stocks.sql'])
async def test_depots_trim(taxi_overlord_catalog, search, mock_grocery_depots):
    mock_grocery_depots.load_json(
        'gdepots-depots-default.json', 'gdepots-zones-default.json',
    )
    response = await taxi_overlord_catalog.get(
        '/admin/catalog/v1/depots', params={'search': search},
    )
    assert response.status_code == 200
    assert len(response.json()['depots']) == 1
    assert response.json()['depots'][0]['store_id'] == '666666'


@pytest.mark.pgsql('overlord_catalog', files=['add_stocks.sql'])
async def test_depots_empty_search(taxi_overlord_catalog, mock_grocery_depots):
    mock_grocery_depots.load_json(
        'gdepots-depots-default.json', 'gdepots-zones-default.json',
    )
    response = await taxi_overlord_catalog.get(
        '/admin/catalog/v1/depots', params={'search': ' '},
    )
    assert response.status_code == 200
    assert len(response.json()['depots']) == 8


async def test_depots_empty_search_gd(taxi_overlord_catalog, mockserver):
    setup_grocery_depots_mock(taxi_overlord_catalog, mockserver)
    response = await taxi_overlord_catalog.get(
        '/admin/catalog/v1/depots', params={'search': ' '},
    )
    assert response.status_code == 200
    assert len(response.json()['depots']) == 1


@pytest.mark.parametrize(
    'search',
    ['lavka_1', '99999901', 'Никольской', ' Никольской ', 'Никольской '],
)
@pytest.mark.pgsql('overlord_catalog', files=['add_stocks.sql'])
async def test_depots_trim_gd(
        taxi_overlord_catalog, search, mock_grocery_depots,
):
    mock_grocery_depots.load_json(
        'gdepots-depots-default.json', 'gdepots-zones-default.json',
    )
    response = await taxi_overlord_catalog.get(
        '/admin/catalog/v1/depots', params={'search': search},
    )
    assert response.status_code == 200
    assert len(response.json()['depots']) == 1
    assert response.json()['depots'][0]['store_id'] == '99999901'


@pytest.mark.skip(reason='It will be fixed in LAVKALOGDEV-1137')
@pytest.mark.parametrize('grocery_depot_availability', [True, False])
@pytest.mark.parametrize('depot_status', ['admin_enabled', 'hidden'])
@pytest.mark.parametrize(
    'depot_id, external_id, depot_status_value, status_code, updated',
    [
        ('id-111', '111', True, 200, True),
        ('id-222', '222', False, 200, True),
        ('id-333', '333', True, 200, False),
        ('id-444', '444', True, 404, None),
    ],
)
@pytest.mark.pgsql('overlord_catalog', files=['set_status_wms.sql'])
@pytest.mark.suspend_periodic_tasks('nomenclature-sync')
async def test_depots_set_status_from_wms(
        taxi_overlord_catalog,
        pgsql,
        depot_status,
        depot_id,
        external_id,
        depot_status_value,
        status_code,
        updated,
        mockserver,
        grocery_depot_availability,
):
    orig_updated = datetime.datetime(2019, 12, 1, 1, 1, 1)

    @mockserver.json_handler(
        '/grocery-depots/admin/depots/v1/depots/set_status',
    )
    def _handle(request):
        assert request.json['hidden'] == depot_status_value
        status = 200 if grocery_depot_availability else 500
        return mockserver.make_response(status=status)

    for depot_to_send in (depot_id, external_id):
        response = await taxi_overlord_catalog.post(
            '/admin/catalog/v1/depots/set_status',
            params={'store_id': depot_to_send},
            json={depot_status: depot_status_value},
        )
        assert response.status_code == status_code

        if depot_status == 'admin_enabled':
            depot_status_field = 'status'
        elif depot_status == 'hidden':
            depot_status_field = 'hidden'
        else:
            assert False

        db = pgsql['overlord_catalog']
        cursor = db.cursor()
        cursor.execute(
            f'SELECT depot_id, {depot_status_field}, updated '
            f'FROM catalog_wms.depots '
            f'WHERE depot_id = \'{depot_id}\'',
        )
        result = {
            depot_id: [depot_status_value, updated]
            for depot_id, depot_status_value, updated in cursor.fetchall()
        }

        if status_code == 200:
            assert len(result) == 1
        elif status_code == 404:
            assert not result
            return
        else:
            assert False

        depot_info = result[depot_id]
        found_depot_status_value = depot_info[0]
        found_updated = depot_info[1].astimezone(pytz.UTC).replace(tzinfo=None)

        if depot_status == 'admin_enabled':
            if not depot_status_value:
                depot_status_value_string = 'disabled'
            else:
                depot_status_value_string = 'active'
        else:
            depot_status_value_string = depot_status_value

        assert found_depot_status_value == depot_status_value_string
        if updated:
            assert found_updated > orig_updated
        else:
            assert found_updated == orig_updated
