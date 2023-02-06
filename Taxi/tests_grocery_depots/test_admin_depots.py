import pytest

from testsuite.utils import ordered_object


@pytest.mark.pgsql('grocery_depots', files=['set_wms_closed_wms.sql'])
async def test_depots_get_closed_depots(taxi_grocery_depots):
    response = await taxi_grocery_depots.post(
        '/internal/v1/depots/v1/depots', json={'legacy_depot_ids': []},
    )

    response_depots = response.json()['depots']

    expected_depots = [
        {
            'allow_parcels': False,
            'company_id': '',
            'company_type': 'yandex',
            'country_iso2': 'RU',
            'country_iso3': 'RUS',
            'currency': 'RUB',
            'depot_id': 'id-333',
            'hidden': False,
            'legacy_depot_id': '333',
            'location': {'lat': 37.371618, 'lon': 55.840757},
            'name': 'test_lavka_3',
            'phone_number': '+78007700460',
            'region_id': 213,
            'status': 'closed',  # < closed возвращается
            'timetable': [
                {
                    'day_type': 'Everyday',
                    'working_hours': {
                        'from': {'hour': 8, 'minute': 0},
                        'to': {'hour': 23, 'minute': 0},
                    },
                },
            ],
            'timezone': 'Europe/Moscow',
        },
    ]

    assert len(response_depots) == 1
    assert response_depots == expected_depots


async def test_depots_bad_request(taxi_grocery_depots):
    response = await taxi_grocery_depots.get('/admin/depots/v1/depots')
    assert response.status_code == 400
    assert response.json() == {
        'code': 'BAD_REQUEST',
        'message': 'Neither region_id nor country nor search provided',
    }


@pytest.mark.pgsql(
    'grocery_depots',
    files=['gdepots-depots-default.sql', 'gdepots-zones-default.sql'],
)
@pytest.mark.parametrize('region_id', ['bad', '100500', '213'])
async def test_depots_not_found_by_city(taxi_grocery_depots, region_id):
    response = await taxi_grocery_depots.get(
        '/admin/depots/v1/depots',
        params={'region_id': region_id, 'search': 'never_gonna_find_me'},
    )
    if region_id != '213':
        if region_id != 'bad':
            assert response.status_code == 404
            assert response.json() == {
                'code': 'CITY_NOT_FOUND',
                'message': 'No such city: ' + region_id,
            }
        else:
            assert response.status_code == 400
    else:
        assert response.status_code == 200
        assert response.json() == {'depots_info': []}


@pytest.mark.parametrize('country', ['bad', 'RUS'])
@pytest.mark.pgsql(
    'grocery_depots',
    files=['gdepots-depots-default.sql', 'gdepots-zones-default.sql'],
)
async def test_depots_not_found_by_country(taxi_grocery_depots, country):
    response = await taxi_grocery_depots.get(
        '/admin/depots/v1/depots',
        params={'country': country, 'search': 'never_gonna_find_me'},
    )
    if country == 'RUS':
        assert response.status_code == 200
        assert response.json() == {'depots_info': []}
    else:
        assert response.status_code == 404
        assert response.json() == {
            'code': 'COUNTRY_NOT_FOUND',
            'message': 'No such country: ' + country,
        }


@pytest.mark.parametrize(
    'params, expected_depots',
    [
        (
            {'region_id': 213},
            [
                {
                    'legacy_depot_id': '99999901',
                    'depot_id': 'id-99999901',
                    'name': 'test_lavka_1',
                    'short_address': '"Партвешок За Полтишок" на Никольской',
                    'region_id': 213,
                },
                {
                    'legacy_depot_id': '99999902',
                    'depot_id': 'id-99999902',
                    'name': 'test_lavka_2',
                    'short_address': (
                        '"Партвешок За Полтишок" на Скоробогадько 17'
                    ),
                    'region_id': 213,
                },
            ],
        ),
        (
            {'search': 'test_lavka_1'},
            [
                {
                    'legacy_depot_id': '99999901',
                    'depot_id': 'id-99999901',
                    'name': 'test_lavka_1',
                    'short_address': '"Партвешок За Полтишок" на Никольской',
                    'region_id': 213,
                },
            ],
        ),
        (
            {'search': 'test_lavka'},
            [
                {
                    'legacy_depot_id': '99999901',
                    'depot_id': 'id-99999901',
                    'name': 'test_lavka_1',
                    'short_address': '"Партвешок За Полтишок" на Никольской',
                    'region_id': 213,
                },
                {
                    'legacy_depot_id': '99999902',
                    'depot_id': 'id-99999902',
                    'name': 'test_lavka_2',
                    'short_address': (
                        '"Партвешок За Полтишок" на Скоробогадько 17'
                    ),
                    'region_id': 213,
                },
                {
                    'legacy_depot_id': '99999903',
                    'depot_id': 'id-99999903',
                    'name': 'test_lavka_3',
                    'short_address': (
                        '"Партвешок За Полтишок" на Внутреутробной'
                    ),
                    'region_id': 2,
                },
                {
                    'legacy_depot_id': '99999904',
                    'depot_id': 'id-99999904',
                    'name': 'test_lavka_4',
                    'short_address': (
                        '"Партвешок За Полтишок" на Седьмой-Восьмой 9'
                    ),
                    'region_id': 2,
                },
            ],
        ),
        (
            {'search': '99999901'},
            [
                {
                    'legacy_depot_id': '99999901',
                    'depot_id': 'id-99999901',
                    'name': 'test_lavka_1',
                    'short_address': '"Партвешок За Полтишок" на Никольской',
                    'region_id': 213,
                },
            ],
        ),
        (
            {'search': '999999'},
            [
                {
                    'legacy_depot_id': '99999901',
                    'depot_id': 'id-99999901',
                    'name': 'test_lavka_1',
                    'short_address': '"Партвешок За Полтишок" на Никольской',
                    'region_id': 213,
                },
                {
                    'legacy_depot_id': '99999902',
                    'depot_id': 'id-99999902',
                    'name': 'test_lavka_2',
                    'short_address': (
                        '"Партвешок За Полтишок" на Скоробогадько 17'
                    ),
                    'region_id': 213,
                },
                {
                    'legacy_depot_id': '99999903',
                    'depot_id': 'id-99999903',
                    'name': 'test_lavka_3',
                    'short_address': (
                        '"Партвешок За Полтишок" на Внутреутробной'
                    ),
                    'region_id': 2,
                },
                {
                    'legacy_depot_id': '99999904',
                    'depot_id': 'id-99999904',
                    'name': 'test_lavka_4',
                    'short_address': (
                        '"Партвешок За Полтишок" на Седьмой-Восьмой 9'
                    ),
                    'region_id': 2,
                },
            ],
        ),
        (
            {'search': '5'},
            [
                {
                    'legacy_depot_id': '5',
                    'depot_id': 'id-5',
                    'name': 'mixed_lavka_6',
                    'short_address': (
                        '"Партвешок За Полтишок" на Большой Пятой'
                    ),
                    'region_id': 54,
                },
                {
                    'legacy_depot_id': '6',
                    'depot_id': 'id-6',
                    'name': 'mixed_lavka_5',
                    'short_address': '"Партвешок За Полтишок" на Малой Шестой',
                    'region_id': 63,
                },
            ],
        ),
        ({'search': 'never_gonna_find_me'}, []),
        (
            {'region_id': 213, 'search': 'test_lavka'},
            [
                {
                    'legacy_depot_id': '99999901',
                    'depot_id': 'id-99999901',
                    'name': 'test_lavka_1',
                    'short_address': '"Партвешок За Полтишок" на Никольской',
                    'region_id': 213,
                },
                {
                    'legacy_depot_id': '99999902',
                    'depot_id': 'id-99999902',
                    'name': 'test_lavka_2',
                    'short_address': (
                        '"Партвешок За Полтишок" на Скоробогадько 17'
                    ),
                    'region_id': 213,
                },
            ],
        ),
        ({'region_id': 213, 'search': 'test_lavka_3'}, []),
        (
            {'search': 'на Малой Шестой'},
            [
                {
                    'legacy_depot_id': '6',
                    'depot_id': 'id-6',
                    'name': 'mixed_lavka_5',
                    'short_address': '"Партвешок За Полтишок" на Малой Шестой',
                    'region_id': 63,
                },
            ],
        ),
    ],
)
@pytest.mark.pgsql(
    'grocery_depots',
    files=['gdepots-depots-default.sql', 'gdepots-zones-default.sql'],
)
async def test_depots_base(taxi_grocery_depots, params, expected_depots):
    def _only_base_fields(doc):
        depots = []
        for depot in doc['depots_info']:
            depots.append(
                {
                    key: value
                    for key, value in depot['depot'].items()
                    if key
                    in (
                        'depot_id',
                        'legacy_depot_id',
                        'name',
                        'short_address',
                        'region_id',
                    )
                },
            )
        return {'depots': depots}

    response = await taxi_grocery_depots.get(
        '/admin/depots/v1/depots', params=params,
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
            {'region_id': 213},
            [
                {
                    'legacy_depot_id': '99999901',
                    'root_category_id': 'root-99999901',
                    'assortment_id': '99999901ASTMNT',
                    'price_list_id': '99999901PRLIST',
                },
                {
                    'legacy_depot_id': '99999902',
                    'root_category_id': 'root-99999902',
                    'assortment_id': '99999902ASTMNT',
                    'price_list_id': '99999902PRLIST',
                },
            ],
        ),
        (
            {'search': 'test_lavka_1'},
            [
                {
                    'legacy_depot_id': '99999901',
                    'root_category_id': 'root-99999901',
                    'assortment_id': '99999901ASTMNT',
                    'price_list_id': '99999901PRLIST',
                },
            ],
        ),
        (
            {'search': 'test_lavka'},
            [
                {
                    'legacy_depot_id': '99999901',
                    'root_category_id': 'root-99999901',
                    'assortment_id': '99999901ASTMNT',
                    'price_list_id': '99999901PRLIST',
                },
                {
                    'legacy_depot_id': '99999902',
                    'root_category_id': 'root-99999902',
                    'assortment_id': '99999902ASTMNT',
                    'price_list_id': '99999902PRLIST',
                },
                {
                    'legacy_depot_id': '99999903',
                    'root_category_id': 'root-99999903',
                    'assortment_id': '99999903ASTMNT',
                    'price_list_id': '99999903PRLIST',
                },
                {
                    'legacy_depot_id': '99999904',
                    'root_category_id': 'root-99999904',
                    'assortment_id': '99999904ASTMNT',
                    'price_list_id': '99999904PRLIST',
                },
            ],
        ),
        (
            {'search': '99999901'},
            [
                {
                    'legacy_depot_id': '99999901',
                    'root_category_id': 'root-99999901',
                    'assortment_id': '99999901ASTMNT',
                    'price_list_id': '99999901PRLIST',
                },
            ],
        ),
        (
            {'search': '999999'},
            [
                {
                    'legacy_depot_id': '99999901',
                    'root_category_id': 'root-99999901',
                    'assortment_id': '99999901ASTMNT',
                    'price_list_id': '99999901PRLIST',
                },
                {
                    'legacy_depot_id': '99999902',
                    'root_category_id': 'root-99999902',
                    'assortment_id': '99999902ASTMNT',
                    'price_list_id': '99999902PRLIST',
                },
                {
                    'legacy_depot_id': '99999903',
                    'root_category_id': 'root-99999903',
                    'assortment_id': '99999903ASTMNT',
                    'price_list_id': '99999903PRLIST',
                },
                {
                    'legacy_depot_id': '99999904',
                    'root_category_id': 'root-99999904',
                    'assortment_id': '99999904ASTMNT',
                    'price_list_id': '99999904PRLIST',
                },
            ],
        ),
        (
            {'search': '5'},
            [
                {
                    'legacy_depot_id': '5',
                    'root_category_id': 'root-5',
                    'assortment_id': '5ASTMNT',
                    'price_list_id': '5PRLIST',
                },
                {
                    'legacy_depot_id': '6',
                    'root_category_id': 'root-6',
                    'assortment_id': '6ASTMNT',
                    'price_list_id': '6PRLIST',
                },
            ],
        ),
        ({'search': 'never_gonna_find_me'}, []),
        (
            {'region_id': 213, 'search': 'test_lavka'},
            [
                {
                    'legacy_depot_id': '99999901',
                    'root_category_id': 'root-99999901',
                    'assortment_id': '99999901ASTMNT',
                    'price_list_id': '99999901PRLIST',
                },
                {
                    'legacy_depot_id': '99999902',
                    'root_category_id': 'root-99999902',
                    'assortment_id': '99999902ASTMNT',
                    'price_list_id': '99999902PRLIST',
                },
            ],
        ),
        ({'region_id': 213, 'search': 'test_lavka_3'}, []),
        (
            {'search': 'на Малой Шестой'},
            [
                {
                    'legacy_depot_id': '6',
                    'root_category_id': 'root-6',
                    'assortment_id': '6ASTMNT',
                    'price_list_id': '6PRLIST',
                },
            ],
        ),
    ],
)
@pytest.mark.pgsql(
    'grocery_depots',
    files=['gdepots-depots-default.sql', 'gdepots-zones-default.sql'],
)
async def test_depots_menu_fields(
        taxi_grocery_depots, pgsql, params, expected_depots,
):
    def _only_menu_fields(doc):
        depots = []
        for depot in doc['depots_info']:
            depots.append(
                {
                    key: value
                    for key, value in depot['depot'].items()
                    if key
                    in (
                        'legacy_depot_id',
                        'root_category_id',
                        'assortment_id',
                        'price_list_id',
                    )
                },
            )
        return {'depots': depots}

    response = await taxi_grocery_depots.get(
        '/admin/depots/v1/depots', params=params,
    )
    assert response.status_code == 200
    ordered_object.assert_eq(
        _only_menu_fields(response.json()),
        {'depots': expected_depots},
        ['depots'],
    )


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
@pytest.mark.pgsql(
    'grocery_depots',
    files=['gdepots-depots-default.sql', 'gdepots-zones-default.sql'],
)
async def test_depots_trim(taxi_grocery_depots, search):
    response = await taxi_grocery_depots.get(
        '/admin/depots/v1/depots', params={'search': search},
    )
    assert response.status_code == 200
    assert len(response.json()['depots_info']) == 1
    assert (
        response.json()['depots_info'][0]['depot']['legacy_depot_id']
        == '666666'
    )


@pytest.mark.pgsql(
    'grocery_depots',
    files=['gdepots-depots-default.sql', 'gdepots-zones-default.sql'],
)
async def test_depots_empty_search(taxi_grocery_depots):
    response = await taxi_grocery_depots.get(
        '/admin/depots/v1/depots', params={'search': ' '},
    )
    assert response.status_code == 200
    assert len(response.json()['depots_info']) == 8


@pytest.mark.pgsql(
    'grocery_depots',
    files=[
        'from_setup_grocery_depots_mock_depots.sql',
        'from_setup_grocery_depots_mock_zones.sql',
    ],
)
async def test_depots_empty_search_gd(taxi_grocery_depots):
    response = await taxi_grocery_depots.get(
        '/admin/depots/v1/depots', params={'search': ' '},
    )
    assert response.status_code == 200
    assert len(response.json()['depots_info']) == 1


@pytest.mark.parametrize(
    'search',
    ['lavka_1', '99999901', 'Никольской', ' Никольской ', 'Никольской '],
)
@pytest.mark.pgsql(
    'grocery_depots',
    files=[
        'from_setup_grocery_depots_mock_depots.sql',
        'from_setup_grocery_depots_mock_zones.sql',
    ],
)
async def test_depots_trim_gd(taxi_grocery_depots, search):
    response = await taxi_grocery_depots.get(
        '/admin/depots/v1/depots', params={'search': search},
    )
    assert response.status_code == 200
    assert len(response.json()['depots_info']) == 1
    assert (
        response.json()['depots_info'][0]['depot']['legacy_depot_id']
        == '99999901'
    )
