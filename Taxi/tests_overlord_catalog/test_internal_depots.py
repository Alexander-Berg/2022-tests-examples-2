import pytest

from .plugins import mock_personal

YANDEX_COMPANIES = pytest.mark.config(
    OVERLORD_CATALOG_YANDEX_COMPANY_TITLES=['Yandex'],
)


def deep_sort_without_geo(data):
    data['depots'].sort(key=lambda x: x['depot_id'])
    for depot in data['depots']:
        depot['detailed_zones'].sort(
            key=lambda x: (
                x['status'],
                x['zoneType'],
                x['timetable'][0]['working_hours']['from']['hour'],
            ),
            reverse=True,
        )


@pytest.mark.now('2021-11-11T13:15+00:00')
async def test_gdepot_in_tesing(
        load_json, mock_grocery_depots, taxi_overlord_catalog,
):
    mock_grocery_depots.load_json(
        'gdepots-depots-testing.json', 'gdepots-zones-testing.json',
    )
    response = await taxi_overlord_catalog.post(
        '/internal/v1/catalog/v1/depots', json={'legacy_depot_ids': []},
    )
    assert response.status_code == 200
    response_json = response.json()
    for depot in response_json['depots']:
        depot.pop('tin', None)  # gdepots provides tin without personal_tin
    expected = load_json('gdepots_testing_expected.json')
    expected['errors'] = []  # no errors about country inside gdepots repons
    deep_sort_without_geo(response_json)
    deep_sort_without_geo(expected)
    # for 0997625d53b24eaf9c26c8e115e6e195000300020000
    # company type comes from gdepots
    expected['depots'][1]['company_type'] = 'franchise'
    assert response_json == expected


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
                    'location': {'lat': 55.840757, 'lon': 37.371618},
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
                    'company_id': 'company-id-franchise',
                    'tin': 'tin-for-franchise',
                    'address': '"Партвешок За Полтишок" на Никольской',
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


async def test_basic_grocery_depots(
        taxi_overlord_catalog, personal, mockserver,
):
    # Tins from pg_overlord_catalog.sql
    personal.add_tins(['tin-for-franchise', 'tin-11111111'])
    setup_grocery_depots_mock(taxi_overlord_catalog, mockserver)
    await taxi_overlord_catalog.invalidate_caches()
    response = await taxi_overlord_catalog.post(
        '/internal/v1/catalog/v1/depots',
        json={'legacy_depot_ids': ['99999901']},
    )
    assert response.json() == {
        'depots': [
            {
                'depot_id': 'id-99999901',
                'country_iso3': 'RUS',
                'country_iso2': 'RU',
                'legacy_depot_id': '99999901',
                'region_id': 55501,
                'timezone': 'Europe/Moscow',
                'position': {'location': [37.371618, 55.840757]},
                'address': '"Партвешок За Полтишок" на Никольской',
                'phone_number': '',
                'currency': 'RUB',
                'company_type': 'yandex',
                'company_id': 'company-id-franchise',
                'tin': 'tin-for-franchise',
                'name': 'test_lavka_1',
                'short_address': '"Партвешок За Полтишок" на Никольской',
                'personal_tin_id': mock_personal.PERSONAL_TIN_ID,
                'detailed_zones': [
                    {
                        'status': 'active',
                        'timetable': [
                            {
                                'day_type': 'Everyday',
                                'working_hours': {
                                    'from': {'hour': 0, 'minute': 0},
                                    'to': {'hour': 0, 'minute': 0},
                                },
                            },
                        ],
                        'zoneType': 'pedestrian',
                    },
                ],
            },
        ],
        'errors': [],
    }


@pytest.mark.parametrize(
    'zones_mode', ['nothing', 'with_geozones', 'without_geozones', None],
)
@YANDEX_COMPANIES
async def test_all_depots(
        taxi_overlord_catalog, personal, zones_mode, mock_grocery_depots,
):
    mock_grocery_depots.load_json(
        'gdepots-depots-pg_overlord_catalog.json',
        'gdepots-zones-pg_overlord_catalog.json',
    )
    # Tins from pg_overlord_catalog.sql
    personal.add_tins(['tin-for-franchise', 'tin-11111111'])

    await taxi_overlord_catalog.invalidate_caches()

    request = {'legacy_depot_ids': []}
    if zones_mode is not None:
        request['zones_mode'] = zones_mode

    response = await taxi_overlord_catalog.post(
        '/internal/v1/catalog/v1/depots', json=request,
    )

    if zones_mode is None:
        # It's a default value
        zones_mode = 'without_geozones'

    assert not response.json()['errors']
    depots = response.json()['depots']
    expected_depots = [
        {
            'depot_id': 'aab8a6fbcee34b38b5281d8ea6ef749a000100010000',
            'country_iso2': 'RU',
            'country_iso3': 'RUS',
            'legacy_depot_id': '3',
            'position': {'location': [37.371618, 55.840757]},
            'region_id': 1,
            'timezone': 'Europe/Moscow',
            'tin': 'tin-11111111',
            'phone_number': '+78007700460',
            'currency': 'RUB',
            'company_id': 'company-id-yandex',
            'company_type': 'yandex',
            'name': 'lavka_2',
            'personal_tin_id': mock_personal.PERSONAL_TIN_ID,
        },
        {
            'depot_id': 'ddb8a6fbcee34b38b5281d8ea6ef749a000100010000',
            'country_iso2': 'RU',
            'country_iso3': 'RUS',
            'legacy_depot_id': '2',
            'position': {'location': [37.371618, 55.840757]},
            'region_id': 1,
            'timezone': 'Europe/Moscow',
            'address': (
                '140015, Московская обл, Люберцы г, Инициативная ул, дом № 50'
            ),
            'phone_number': '8(999)7777777',
            'currency': 'RUB',
            'company_type': 'franchise',
            'tin': 'tin-for-franchise',
            'company_id': 'company-id-franchise',
            'name': 'lavka_1',
            'short_address': 'Инициативная, 50',
            'personal_tin_id': mock_personal.PERSONAL_TIN_ID,
            'oebs_depot_id': 'oebs-depot-id-for-lavka_1',
        },
    ]

    if zones_mode in ('without_geozones', 'with_geozones'):
        for depot in expected_depots:
            depot['detailed_zones'] = [
                {
                    'status': 'active',
                    'timetable': [
                        {
                            'day_type': 'Everyday',
                            'working_hours': {
                                'from': {'hour': 0, 'minute': 0},
                                'to': {'hour': 0, 'minute': 0},
                            },
                        },
                    ],
                    'zoneType': 'pedestrian',
                },
            ]

        if zones_mode == 'with_geozones':
            detailed_zone = expected_depots[0]['detailed_zones'][0]
            detailed_zone['geozone'] = {'type': 'MultiPolygon'}
            detailed_zone['geozone']['coordinates'] = [
                [
                    [
                        {'lat': 0.0, 'lon': 0.0},
                        {'lat': 1.0, 'lon': 0.0},
                        {'lat': 1.0, 'lon': 1.0},
                        {'lat': 0.0, 'lon': 1.0},
                        {'lat': 0.0, 'lon': 0.0},
                    ],
                ],
            ]

            detailed_zone = expected_depots[1]['detailed_zones'][0]
            detailed_zone['geozone'] = {'type': 'MultiPolygon'}
            detailed_zone['geozone']['coordinates'] = [
                [
                    [
                        {'lat': 55.0, 'lon': 37.0},
                        {'lat': 56.0, 'lon': 37.0},
                        {'lat': 56.0, 'lon': 38.0},
                        {'lat': 55.0, 'lon': 38.0},
                        {'lat': 55.0, 'lon': 37.0},
                    ],
                ],
            ]
    depots.sort(key=lambda d: d['depot_id'])
    expected_depots.sort(key=lambda d: d['depot_id'])
    assert depots == expected_depots


@pytest.mark.pgsql('overlord_catalog', files=['default_empty.sql'])
@pytest.mark.parametrize(
    'request_filter,expected_ids',
    ([None, ['2', '3']], ['allow_parcels', ['2']]),
)
async def test_with_filter(
        taxi_overlord_catalog,
        request_filter,
        expected_ids,
        mock_grocery_depots,
):
    """ Checks optional filter field for /internal/v1/catalog/v1/depots
    should return depots with corresponding features """
    mock_grocery_depots.load_json(
        'gdepots-depots-pg_overlord_catalog.json',
        'gdepots-zones-pg_overlord_catalog.json',
        replace_at_depots=[[['2'], {'allow_parcels': True}]],
    )
    request = {'legacy_depot_ids': []}
    if request_filter:
        request['filter'] = request_filter
    response = await taxi_overlord_catalog.post(
        '/internal/v1/catalog/v1/depots', json=request,
    )

    assert not response.json()['errors']
    legacy_depot_ids = [
        depot['legacy_depot_id'] for depot in response.json()['depots']
    ]
    assert sorted(legacy_depot_ids) == sorted(expected_ids)


@pytest.mark.pgsql('overlord_catalog', files=['default_empty.sql'])
async def test_depot_without_tin(taxi_overlord_catalog, mock_grocery_depots):
    mock_grocery_depots.load_json(
        'gdepots-depots-pg_overlord_catalog.json',
        'gdepots-zones-pg_overlord_catalog.json',
    )
    response = await taxi_overlord_catalog.post(
        '/internal/v1/catalog/v1/depots', json={'legacy_depot_ids': []},
    )
    assert not response.json()['errors']
    assert response.json()['depots']


@pytest.mark.now('2021-04-01T04:00:00+00:00')
async def test_depots_in_effect(taxi_overlord_catalog, mock_grocery_depots):
    mock_grocery_depots.load_json(
        'gdepots-depots-in_effect_zones.json',
        'gdepots-zones-in_effect_zones.json',
    )
    expected_zones_in_effect = 1
    await taxi_overlord_catalog.invalidate_caches()

    response = await taxi_overlord_catalog.post(
        '/internal/v1/catalog/v1/depots', json={'legacy_depot_ids': []},
    )

    zones_in_effect = 0
    for depot in response.json()['depots']:
        zones_in_effect += len(depot['detailed_zones'])

    assert not response.json()['errors']
    assert zones_in_effect == expected_zones_in_effect


@pytest.mark.config(OVERLORD_CATALOG_YANDEX_COMPANY_TITLES=[])
async def test_ownership_column(
        taxi_overlord_catalog, personal, mock_grocery_depots,
):
    mock_grocery_depots.load_json(
        'gdepots-depots-pg_overlord_catalog.json',
        'gdepots-zones-pg_overlord_catalog.json',
    )
    # Tins from pg_overlord_catalog.sql
    personal.add_tins(['tin-for-franchise', 'tin-11111111'])

    await taxi_overlord_catalog.invalidate_caches()

    response = await taxi_overlord_catalog.post(
        '/internal/v1/catalog/v1/depots', json={'legacy_depot_ids': ['3']},
    )

    assert response.json()['depots'][0]['company_type'] == 'yandex'
