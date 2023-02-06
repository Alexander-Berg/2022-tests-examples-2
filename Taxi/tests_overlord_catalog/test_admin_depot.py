import collections

import pytest


def setup_gdepots(mockserver, depots, zones):
    @mockserver.json_handler('/grocery-depots/internal/v1/depots/v1/depots')
    def _handle_depots(_request):
        return depots

    @mockserver.json_handler('/grocery-depots/internal/v1/depots/v1/zones')
    def _handle_zones(_request):
        return zones


@pytest.mark.pgsql('overlord_catalog', files=['default.sql'])
async def test_not_found(taxi_overlord_catalog):
    response = await taxi_overlord_catalog.get(
        '/admin/catalog/v1/depot', params={'depot_id': '222'},
    )
    assert response.status_code == 404


@pytest.mark.parametrize(
    'depot_id', ['111', 'ddb8a6fbcee34b38b5281d8ea6ef749a000100010000'],
)
@pytest.mark.pgsql('overlord_catalog', files=['default.sql'])
@pytest.mark.parametrize('use_grocery_depots', [True])
async def test_basic_wms(
        taxi_overlord_catalog,
        depot_id,
        use_grocery_depots,
        mockserver,
        load_json,
        taxi_config,
):
    if use_grocery_depots:
        setup_gdepots(
            mockserver,
            load_json('g-depots-default.json'),
            load_json('g-depots-zones-default.json'),
        )
    taxi_config.set_values(
        {
            'OVERLORD_CATALOG_SWITCH_TO_GROCERY_DEPOTS_BACKEND': (
                'return_grocery_depots_agains_overlord_catalog'
                if use_grocery_depots
                else 'only_overlord_catalog'
            ),
        },
    )
    response = await taxi_overlord_catalog.get(
        '/admin/catalog/v1/depot', params={'depot_id': depot_id},
    )
    assert response.status_code == 200
    resp_json = response.json()

    def find_by_type(zone_type):
        for element in resp_json['detailed_zones']:
            if element['zoneType'] == zone_type:
                return element
        return None

    def sort_geozone(value):
        for item in value:
            item['geozone']['coordinates'][0][0].sort(
                key=lambda a: hash(a['lon']) + hash(a['lat']),
            )

    assert len(resp_json['detailed_zones']) == 2
    resp_json['detailed_zones'] = [
        find_by_type('yandex_taxi'),
        find_by_type('pedestrian'),
    ]
    sort_geozone(resp_json['detailed_zones'])
    expected = {
        'store_id': '111',
        'wms_id': 'ddb8a6fbcee34b38b5281d8ea6ef749a000100010000',
        'address': '',
        'location': {'lat': 55.840757, 'lon': 37.371618},
        'phone_number': '+79091234455',
        'directions': 'go to the right',
        'telegram': 'depot_telegram',
        'admin_enabled': True,
        'auto_enabled': True,
        'city_id': '213',
        'iso2': 'RU',
        'iso3': 'RUS',
        'currency': 'RUB',
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
                'geozone': {
                    'coordinates': [
                        [
                            [
                                {'lat': 3.0, 'lon': 3.0},
                                {'lat': 4.0, 'lon': 3.0},
                                {'lat': 4.0, 'lon': 4.0},
                                {'lat': 3.0, 'lon': 4.0},
                                {'lat': 3.0, 'lon': 3.0},
                            ],
                        ],
                    ],
                    'type': 'MultiPolygon',
                },
                'zoneType': 'yandex_taxi',
            },
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
                'geozone': {
                    'coordinates': [
                        [
                            [
                                {'lat': 1.0, 'lon': 1.0},
                                {'lat': 2.0, 'lon': 2.0},
                                {'lat': 3.1, 'lon': 3.1},
                                {'lat': 1.0, 'lon': 1.0},
                            ],
                        ],
                    ],
                    'type': 'MultiPolygon',
                },
                'zoneType': 'pedestrian',
            },
        ],
        'hidden': False,
        'name': 'Мир Дошиков',
        'slug': 'test_lavka_1',
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
        'timezone': 'Europe/Moscow',
        'allow_parcels': False,
    }
    sort_geozone(expected['detailed_zones'])
    assert resp_json == expected


@pytest.mark.parametrize(
    'depot_id, status, hidden',
    [('111', 'active', True), ('222', 'disabled', False)],
)
async def test_status_wms(
        taxi_overlord_catalog, depot_id, status, hidden, mock_grocery_depots,
):
    mock_grocery_depots.load_json(
        'gdepots-depots-status.json', 'gdepots-zones-status.json',
    )
    response = await taxi_overlord_catalog.get(
        '/admin/catalog/v1/depot', params={'depot_id': depot_id},
    )
    assert response.status_code == 200
    response_json = response.json()
    assert response_json['status'] == status
    assert response_json['hidden'] == hidden


async def test_depot_without_extended_zone(
        taxi_overlord_catalog, mock_grocery_depots, load_json,
):
    mock_grocery_depots.setup(
        load_json('gdepots_depot_without_extended_zone.json'), {'zones': []},
    )
    response = await taxi_overlord_catalog.get(
        '/admin/catalog/v1/depot',
        params={'depot_id': 'ddb8a6fbcee34b38b5281d8ea6ef749a000100010000'},
    )
    assert response.status_code == 200


@pytest.mark.skip('Fix will be applied later LAVKALOGDEV-1032')
@pytest.mark.now('2021-11-11T13:15+00:00')
async def test_gdepot_status_from_effective(
        mockserver, load_json, taxi_overlord_catalog,
):
    setup_gdepots(
        mockserver,
        load_json('gd-depots-effective_till.json'),
        load_json('gd-zones-effective_till.json'),
    )
    response = await taxi_overlord_catalog.get(
        '/admin/catalog/v1/depot', params={'depot_id': '402474'},
    )
    per_zones = collections.defaultdict(lambda: collections.defaultdict(int))
    for z in response.json()['detailed_zones']:
        per_zones[z['zoneType']][z['status']] += 1
    assert per_zones == {
        'pedestrian': {'active': 1, 'disabled': 3},
        'yandex_taxi': {'active': 1},
    }
