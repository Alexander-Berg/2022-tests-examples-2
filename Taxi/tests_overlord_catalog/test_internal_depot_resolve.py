# pylint: disable=too-many-lines
import datetime

import pytest

from . import experiments

MARKERS = [
    [37.64169216156006, 55.73626835571061],  # Inside smallest zone (foot)
    [37.64164924621582, 55.74030311233403],  # Inside taxi zone
    [37.64817237854004, 55.744844734490414],  # Inside remote zone
    [37.63688564300537, 55.73764553509855],  # Outside any zone
    [37.638559341430664, 55.74424082584503],  # Inside taxi night zone
    [38.64169216156006, 56.73626835571061],  # Inside tristero foot zone
    [38.64817237854004, 56.744844734490414],  # Inside tristero remote zone
    [37.64199256896973, 55.734969655191975],  # Inside rover zone
    [39.64169216156006, 57.73626835571061],  # Inside disabled foot zone
    [38.64164924621582, 56.74030311233403],  # Inside tristero taxi zone
    [38.638559341430664, 56.74424082584503],  # Inside tristero taxi night zone
]

ENABLED_MOSCOW = {'region_id': 213, 'enabled': True}
ENABLED_RUSSIA = {'region_id': 225, 'enabled': True}
DISABLED_MOSCOW = {'region_id': 213, 'enabled': False}


def setup_gdepots(mockserver, depots, zones):
    @mockserver.json_handler('/grocery-depots/internal/v1/depots/v1/depots')
    def _handle_depots(_request):
        return depots

    @mockserver.json_handler('/grocery-depots/internal/v1/depots/v1/zones')
    def _handle_zones(_request):
        return zones


def _geo_onboarding_experiment(experiments3, *, locations):
    experiments3.add_experiment(
        name='grocery_geo_onboarding',
        consumers=['overlord-catalog/availability'],
        clauses=[
            {
                'title': 'Москва',
                'value': {'enabled': location['enabled']},
                'predicate': {
                    'type': 'eq',
                    'init': {
                        'value': location['region_id'],
                        'arg_name': 'region_id',
                        'arg_type': 'int',
                    },
                },
            }
            for location in locations
        ],
    )


@pytest.mark.now('2021-11-11T13:15+00:00')
async def test_gdepot_resolve_overlap(
        mockserver, load_json, taxi_overlord_catalog,
):
    setup_gdepots(
        mockserver,
        load_json('gdepots_overlap_zones_depots.json'),
        load_json('gdepots_overlap_zones.json'),
    )
    request = {
        'get_next_depot': True,
        'position': {'location': [30.413101747718123, 59.84979457479827]},
    }
    response = await taxi_overlord_catalog.post(
        '/internal/v1/catalog/v1/depot-resolve', json=request,
    )
    assert response.status_code == 200
    assert response.json() == load_json('gdepots_overlap_zones_expected.json')


@pytest.mark.parametrize('depot_reverse', [True, False])
@pytest.mark.parametrize('position', [{'lat': 55.944548, 'lon': 37.346442}])
@pytest.mark.now('2021-11-22T14:10+03:00')
async def test_gdepot_lld_955_availability(
        mockserver, load_json, taxi_overlord_catalog, position, depot_reverse,
):
    depots = load_json('gd-depots-955.json')
    if depot_reverse:
        depots['depots'].reverse()
    setup_gdepots(mockserver, depots, load_json('gd-zones-955.json'))
    response = await taxi_overlord_catalog.post(
        (
            '/internal/v1/catalog/v1/availability'
            '?longitude={lon}&latitude={lat}'
        ).format(**position),
    )
    assert response.status_code == 200
    resp_json = response.json()
    assert resp_json['exists']
    assert resp_json['available']


@pytest.mark.now('2021-11-19T01:04+03:00')
async def test_gdepot_in_testing(mockserver, load_json, taxi_overlord_catalog):
    setup_gdepots(
        mockserver,
        load_json('gdepots-depots-testing.json'),
        load_json('gdepots-zones-testing.json'),
    )
    request = {
        'get_next_depot': True,
        'position': {'location': [37.548145897811864, 55.759832453266256]},
    }
    response = await taxi_overlord_catalog.post(
        '/internal/v1/catalog/v1/depot-resolve', json=request,
    )
    assert response.status_code == 200
    assert response.json() == {
        'depot_id': 'f2cf987af49f4644b82c593256a3053a000300010000',
        'depot_external_id': '120345',
        'zone_type': 'pedestrian',
        'state': 'closed',
        'switch_time': '2021-11-19T04:00:00+00:00',
        'next_depot': {
            'depot_id': 'f2cf987af49f4644b82c593256a3053a000300010000',
            'depot_external_id': '120345',
            'zone': {
                'zone_type': 'pedestrian',
                'state': 'closed',
                'switch_time': '2021-11-19T04:00:00+00:00',
                'working_hours': {
                    'from': {'hour': 7, 'minute': 0},
                    'to': {'hour': 0, 'minute': 0},
                },
            },
        },
        'next_depot_time': '2021-11-19T04:00:00+00:00',
    }


# zones and markers are here
# https://gist.github.com/zmij/7ff63c8b9227bf72ad161098bae9d96c
@pytest.mark.parametrize(
    'location, timeofday, expected_code, expected_zone, expected_state, '
    'allow_parcels, external_id, working_hours_idx, only_overlord_catalog',
    [
        pytest.param(
            # marker no 1
            MARKERS[0],
            '10:00',
            200,
            'pedestrian',
            'open',
            False,
            '111',
            0,
            False,  # only_overlord_catalog
            id='foot zone',
        ),
        pytest.param(
            # marker no 1
            MARKERS[0],
            '09:00',
            200,
            'pedestrian',
            'open',
            False,
            '111',
            0,
            False,  # only_overlord_catalog
            id='foot zone schedule start',
        ),
        pytest.param(
            # marker no 1
            MARKERS[0],
            '01:00',
            200,
            'yandex_taxi_night',
            'open',
            False,
            '111',
            2,
            False,  # only_overlord_catalog
            id='night zone',
        ),
        pytest.param(
            # marker no 2
            MARKERS[1],
            '10:00',
            200,
            'yandex_taxi',
            'open',
            False,
            '111',
            1,
            False,  # only_overlord_catalog
            id='taxi zone',
        ),
        pytest.param(
            # marker no 2
            MARKERS[1],
            '01:00',
            200,
            'yandex_taxi_night',
            'open',
            False,
            '111',
            2,
            False,  # only_overlord_catalog
            id='taxi zone at night',
        ),
        pytest.param(
            # marker no 2
            MARKERS[1],
            '01:00',
            404,
            'yandex_taxi_night',
            'open',
            True,
            '111',
            2,
            False,  # only_overlord_catalog
            id='taxi zone at night 1',
        ),
        pytest.param(
            # marker no 5
            MARKERS[4],
            '10:00',
            200,
            'yandex_taxi_night',
            'closed',
            False,
            '111',
            None,
            False,  # only_overlord_catalog
            id='night zone at day',
        ),
        pytest.param(
            # marker no 3
            MARKERS[2],
            '10:00',
            200,
            'yandex_taxi_remote',
            'open',
            False,
            '111',
            3,
            False,  # only_overlord_catalog
            id='remote zone at day',
        ),
        pytest.param(
            # marker no 3
            MARKERS[2],
            '01:00',
            200,
            'yandex_taxi_remote',
            'closed',
            False,
            '111',
            None,
            False,  # only_overlord_catalog
            id='remote zone at night',
        ),
        pytest.param(
            # marker no 4
            MARKERS[3],
            '10:00',
            404,
            None,
            None,
            False,
            '111',
            None,
            False,  # only_overlord_catalog
            id='no zone at day',
        ),
        pytest.param(
            # marker no 4
            MARKERS[3],
            '01:00',
            404,
            None,
            None,
            False,
            '111',
            2,
            False,  # only_overlord_catalog
            id='no zone at night',
        ),
        pytest.param(
            # marker no 6
            MARKERS[5],
            '09:00',
            200,
            'pedestrian',
            'open',
            False,
            '112',
            0,
            False,  # only_overlord_catalog
            id='foot zone with parcels schedule start',
        ),
        pytest.param(
            # marker no 7
            MARKERS[6],
            '01:00',
            200,
            'yandex_taxi_remote',
            'closed',
            False,
            '112',
            None,
            False,  # only_overlord_catalog
            id='remote tristero zone at night',
        ),
        pytest.param(
            # marker no 7
            MARKERS[6],
            '01:00',
            200,
            'yandex_taxi_remote',
            'closed',
            False,
            '112',
            None,
            False,  # only_overlord_catalog
            id='remote zone at night',
        ),
        pytest.param(
            # marker no 8
            MARKERS[7],
            '09:00',
            200,
            'pedestrian',
            'open',
            False,
            '111',
            0,
            False,  # only_overlord_catalog
            id='rover zone lower priority',
        ),
        pytest.param(
            # marker no 6
            MARKERS[5],
            '09:00',
            200,
            'pedestrian',
            'open',
            True,
            '112',
            0,
            False,  # only_overlord_catalog
            id='pedestrian allow_parcels flag',
        ),
        # ToDo: fix after https://st.yandex-team.ru/LAVKABACKEND-5428
        pytest.param(
            # marker no 7
            MARKERS[6],
            '10:00',
            404,  # 200 after fix
            None,
            None,
            True,
            '112',
            None,
            True,  # only_overlord_catalog
            id='yandex_taxi_remote allow_parcels flag',
        ),
        # ToDo: fix after https://st.yandex-team.ru/LAVKABACKEND-5428
        pytest.param(
            # marker no 10
            MARKERS[9],
            '10:00',
            404,  # 200 after fix
            None,
            None,
            True,
            '112',
            None,
            True,  # only_overlord_catalog
            id='yandex_taxi  allow_parcels flag',
        ),
        # ToDo: fix after https://st.yandex-team.ru/LAVKABACKEND-5428
        pytest.param(
            # marker no 11
            MARKERS[10],
            '01:00',
            404,  # 200 after fix
            None,
            None,
            True,
            '112',
            None,
            True,  # only_overlord_catalog
            id='yandex_taxi_night allow_parcels flag',
        ),
    ],
)
@experiments.zone_priority_config_default
async def test_depot_resolve_ok(
        only_overlord_catalog,
        mockserver,
        load_json,
        taxi_overlord_catalog,
        location,
        timeofday,
        expected_code,
        expected_zone,
        expected_state,
        allow_parcels,
        external_id,
        working_hours_idx,
):
    """
    There is a single depot in the database with 4 zones:
    * foot zone is available 09:00-20:00
    * rover zone is available 09:00-20:00
    * taxi zone is available 07:00-24:00
    * night zone is available 00:00-07:00
    * remote zone is available 07:00-23:00
    The zones and markers used in tests can be viewed here
    https://gist.github.com/zmij/7ff63c8b9227bf72ad161098bae9d96c
    """
    if only_overlord_catalog:
        return
    setup_gdepots(
        mockserver,
        load_json('g-depots-as-default-sql.json'),
        load_json('g-depots-zones-as-default-sql.json'),
    )
    working_hours_arr = [
        {'from': {'hour': 9, 'minute': 0}, 'to': {'hour': 20, 'minute': 0}},
        {'from': {'hour': 7, 'minute': 0}, 'to': {'hour': 0, 'minute': 0}},
        {'from': {'hour': 0, 'minute': 0}, 'to': {'hour': 7, 'minute': 0}},
        {'from': {'hour': 7, 'minute': 0}, 'to': {'hour': 23, 'minute': 0}},
    ]
    await taxi_overlord_catalog.invalidate_caches()

    request = {
        'position': {'location': location},
        'time': '2020-09-09T{}:00+00:00'.format(timeofday),
    }
    if allow_parcels:
        request['filter'] = 'allow_parcels'

    response = await taxi_overlord_catalog.post(
        '/internal/v1/catalog/v1/depot-resolve', json=request,
    )

    if external_id == '111':
        depot_id = 'ddb8a6fbcee34b38b5281d8ea6ef749a000100010000'
    else:
        depot_id = 'ddb8a6fbcee34b38b5281d8ea6ef749a000100010011'

    working_hours = None
    if working_hours_idx is not None:
        working_hours = working_hours_arr[working_hours_idx]

    assert response.status_code == expected_code
    if expected_code == 200:
        resp_json = response.json()
        assert resp_json['depot_id'] == depot_id
        assert resp_json['depot_external_id'] == external_id
        assert 'zone_type' in resp_json.keys()
        assert resp_json['zone_type'] == expected_zone
        assert 'state' in resp_json.keys()
        assert resp_json['state'] == expected_state
        assert 'switch_time' in resp_json.keys()
        assert resp_json.get('working_hours', None) == working_hours


def setup_grocery_depots_mock(mockserver):
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


async def test_grocery_depot_not_availability(
        taxi_overlord_catalog, mockserver,
):
    setup_grocery_depots_mock(mockserver)
    response = await taxi_overlord_catalog.post(
        '/internal/v1/catalog/v1/availability?latitude=55&longitude=37',
    )
    assert response.status_code == 200
    resp_json = response.json()
    assert not resp_json['exists']
    assert not resp_json['available']


# zones and markers are here
# https://gist.github.com/zmij/7ff63c8b9227bf72ad161098bae9d96c
@pytest.mark.parametrize(
    'location, timeofday, expected_exists, expected_available',
    [
        pytest.param(
            # marker no 1
            MARKERS[0],
            '10:00',
            True,
            True,
            id='foot zone',
        ),
        pytest.param(
            # marker no 1
            MARKERS[0],
            '09:00',
            True,
            True,
            id='foot zone schedule start',
        ),
        pytest.param(
            # marker no 1
            MARKERS[0],
            '01:00',
            True,
            True,
            id='night zone',
        ),
        pytest.param(
            # marker no 2
            MARKERS[1],
            '10:00',
            True,
            True,
            id='taxi zone',
        ),
        pytest.param(
            # marker no 2
            MARKERS[1],
            '01:00',
            True,
            True,
            id='taxi zone at night',
        ),
        pytest.param(
            # marker no 5
            MARKERS[4],
            '10:00',
            True,
            False,
            id='night zone at day',
        ),
        pytest.param(
            # marker no 3
            MARKERS[2],
            '10:00',
            True,
            True,
            id='remote zone at day',
        ),
        pytest.param(
            # marker no 3
            MARKERS[2],
            '01:00',
            True,
            False,
            id='remote zone at night',
        ),
        pytest.param(
            # marker no 4
            MARKERS[3],
            '10:00',
            False,
            False,
            id='no zone at day',
        ),
        pytest.param(
            # marker no 4
            MARKERS[3],
            '01:00',
            False,
            False,
            id='no zone at night',
        ),
    ],
)
async def test_depot_availability(
        taxi_overlord_catalog,
        mocked_time,
        location,
        timeofday,
        expected_exists,
        expected_available,
        mock_grocery_depots,
):
    """
    There is a single depot in the database with 4 zones:
    * foot zone is available 09:00-20:00
    * rover zone is available 09:00-20:00
    * taxi zone is available 07:00-24:00
    * night zone is available 00:00-07:00
    * remote zone is available 07:00-23:00
    The zones and markers used in tests can be viewed here
    https://gist.github.com/zmij/7ff63c8b9227bf72ad161098bae9d96c
    """
    mock_grocery_depots.load_json(
        'g-depots-as-default-sql.json', 'g-depots-zones-as-default-sql.json',
    )
    mocked_time.set(
        datetime.datetime.fromisoformat(
            '2020-09-09T{}:00+00:00'.format(timeofday),
        ),
    )

    response = await taxi_overlord_catalog.post(
        '/internal/v1/catalog/v1/availability?latitude={}&longitude={}'.format(
            location[1], location[0],
        ),
    )

    assert response.status_code == 200
    resp_json = response.json()
    assert resp_json['exists'] == expected_exists
    assert resp_json['available'] == expected_available


# zones and markers are here
# https://gist.github.com/zmij/7ff63c8b9227bf72ad161098bae9d96c
@pytest.mark.parametrize(
    'location, expected_exists, expected_available, locations',
    [
        pytest.param(
            # marker no 1
            MARKERS[0],
            True,
            True,
            [ENABLED_MOSCOW],
            id='closed depot, coming soon zone, city enabled',
        ),
        pytest.param(
            # marker no 1
            MARKERS[0],
            True,
            True,
            [ENABLED_RUSSIA],
            id='closed depot, coming soon zone, country enabled',
        ),
        pytest.param(
            # marker no 1
            MARKERS[0],
            False,
            False,
            [ENABLED_RUSSIA, DISABLED_MOSCOW],
            id='closed depot, coming soon zone, city disabled',
        ),
        pytest.param(
            # marker no 1
            MARKERS[0],
            False,
            False,
            None,
            id='closed depot, coming soon zone, no exp',
        ),
        pytest.param(
            # marker no 6
            MARKERS[5],
            False,
            False,
            None,
            id='already opened disabled depot',
        ),
        pytest.param(
            # marker no 9
            MARKERS[8],
            False,
            False,
            None,
            id='closed depot, disabled zone',
        ),
    ],
)
@pytest.mark.now('2021-06-01T10:00:00+00:00')
async def test_closed_depot_with_active_zone(
        taxi_overlord_catalog,
        location,
        expected_exists,
        expected_available,
        locations,
        experiments3,
        mock_grocery_depots,
):
    """ Should return exists == true and available == true
    for closed depot if open_ts is Null and grocery_geo_onboarding
    experiment matched """

    mock_grocery_depots.load_json(
        'gdepots-depots-closed_depots_with_active_zone.json',
        'gdepots-zones-closed_depots_with_active_zone.json',
    )

    if locations is not None:
        _geo_onboarding_experiment(experiments3, locations=locations)

    response = await taxi_overlord_catalog.post(
        '/internal/v1/catalog/v1/availability?latitude={}&longitude={}'.format(
            location[1], location[0],
        ),
    )

    assert response.status_code == 200
    resp_json = response.json()
    assert resp_json['exists'] == expected_exists
    assert resp_json['available'] == expected_available


# zones and markers are here
# https://gist.github.com/zmij/7ff63c8b9227bf72ad161098bae9d96c
@pytest.mark.parametrize(
    'location, timeofday, delta_days, expected_code, expected_zone, '
    'expected_state',
    [
        pytest.param(
            # marker no 1
            MARKERS[0],
            '10:00',
            0,
            200,
            'pedestrian',
            'open',
            id='old foot zone',
        ),
        pytest.param(
            # marker no 1
            MARKERS[0],
            '21:00',
            0,
            200,
            'pedestrian',
            'closed',
            id='old foot zone out of working time',
        ),
        pytest.param(
            # marker no 2
            MARKERS[1],
            '10:00',
            0,
            404,
            None,
            None,
            id='outside old foot zone',
        ),
        pytest.param(
            # marker no 3
            MARKERS[2],
            '10:00',
            0,
            200,
            'yandex_taxi_remote',
            'open',
            id='old remote zone',
        ),
        pytest.param(
            # marker no 1
            MARKERS[0],
            '10:00',
            2,  # plus two days
            200,
            'pedestrian',
            'open',
            id='new foot zone',
        ),
        pytest.param(
            # marker no 2
            MARKERS[1],
            '10:00',
            2,  # plus two days
            200,
            'pedestrian',
            'open',
            id='new foot zone - marker 2 ',
        ),
        pytest.param(
            # marker no 3
            MARKERS[2],
            '10:00',
            2,  # plus two days
            404,
            None,
            None,
            id='retired remote zone',
        ),
    ],
)
async def test_zone_retiring(
        taxi_overlord_catalog,
        location,
        timeofday,
        delta_days,
        expected_code,
        expected_zone,
        expected_state,
        mock_grocery_depots,
):
    """
    There is a single depot in the database:
    * 2 foot zones, both available 07:00-20:00, first one is available till
      test time + 24h, the other one is bigger and is available
      since time + 24h
    * 1 remote zone available 07:00-23:00, retiring in test time + 24h

    The zones and markers used in tests can be viewed here
    https://gist.github.com/zmij/7ff63c8b9227bf72ad161098bae9d96c
    """
    mock_grocery_depots.parse_json(
        'gdepots-depots-zone_retiring.json',
        'gdepots-zones-zone_retiring.json',
    )
    await taxi_overlord_catalog.invalidate_caches()
    request_date = datetime.date.today() + datetime.timedelta(days=delta_days)
    request = {
        'position': {'location': location},
        'time': (
            f'{request_date.year}-{request_date.month:02d}-'
            f'{request_date.day:02d}'
            f'T{timeofday}:00+00:00'
        ),
    }

    response = await taxi_overlord_catalog.post(
        '/internal/v1/catalog/v1/depot-resolve', json=request,
    )
    assert response.status_code == expected_code
    if expected_code == 200:
        resp_json = response.json()
        assert 'zone_type' in resp_json.keys()
        assert resp_json['zone_type'] == expected_zone
        assert 'state' in resp_json.keys()
        assert resp_json['state'] == expected_state


# zones and markers are here
# https://gist.github.com/zmij/7ff63c8b9227bf72ad161098bae9d96c
@pytest.mark.parametrize(
    'location, timeofday, delta_days, expected_code, expected_zone, '
    'expected_state',
    [
        pytest.param(
            # marker no 1
            MARKERS[0],
            '10:00',
            0,
            200,
            'pedestrian',
            'open',
            id='old foot zone',
        ),
        pytest.param(
            # marker no 1
            MARKERS[0],
            '21:00',
            0,
            200,
            'pedestrian',
            'closed',
            id='old foot zone out of working time',
        ),
        pytest.param(
            # marker no 2
            MARKERS[1],
            '10:00',
            0,
            404,
            None,
            None,
            id='outside old foot zone',
        ),
        pytest.param(
            # marker no 3
            MARKERS[2],
            '10:00',
            0,
            200,
            'yandex_taxi_remote',
            'open',
            id='old remote zone',
        ),
        pytest.param(
            # marker no 1
            MARKERS[0],
            '10:00',
            2,  # plus two days
            200,
            'pedestrian',
            'open',
            id='new foot zone',
        ),
        pytest.param(
            # marker no 2
            MARKERS[1],
            '10:00',
            2,  # plus two days
            200,
            'pedestrian',
            'open',
            id='new foot zone - marker 2 ',
        ),
        pytest.param(
            # marker no 3
            MARKERS[2],
            '10:00',
            2,  # plus two days
            404,
            None,
            None,
            id='retired remote zone',
        ),
    ],
)
async def test_zone_retiring_separate_table(
        taxi_overlord_catalog,
        location,
        timeofday,
        delta_days,
        expected_code,
        expected_zone,
        expected_state,
        mock_grocery_depots,
):
    """
    There is a single depot in the database:
    * 2 foot zones, both available 07:00-20:00, first one is available till
      test time + 24h, the other one is bigger and is available
      since time + 24h
    * 1 remote zone available 07:00-23:00, retiring in test time + 24h

    The zones and markers used in tests can be viewed here
    https://gist.github.com/zmij/7ff63c8b9227bf72ad161098bae9d96c
    """
    mock_grocery_depots.parse_json(
        'gdepots-depots-zone_retiring_separate_table.json',
        'gdepots-zones-zone_retiring_separate_table.json',
    )

    await taxi_overlord_catalog.invalidate_caches()
    request_date = datetime.date.today() + datetime.timedelta(days=delta_days)
    request = {
        'position': {'location': location},
        'time': (
            f'{request_date.year}-{request_date.month:02d}-'
            f'{request_date.day:02d}'
            f'T{timeofday}:00+00:00'
        ),
    }

    response = await taxi_overlord_catalog.post(
        '/internal/v1/catalog/v1/depot-resolve', json=request,
    )
    assert response.status_code == expected_code
    if expected_code == 200:
        resp_json = response.json()
        assert 'zone_type' in resp_json.keys()
        assert resp_json['zone_type'] == expected_zone
        assert 'state' in resp_json.keys()
        assert resp_json['state'] == expected_state


@pytest.mark.parametrize(
    'location, timeofday, expected_code, excluded_zones, expected_zone',
    [
        pytest.param(
            # marker no 1
            MARKERS[0],
            '10:00',
            200,
            [],
            'pedestrian',
            id='Allowed pedestrian zone',
        ),
        pytest.param(
            # marker no 1
            MARKERS[0],
            '10:00',
            200,
            ['pedestrian'],
            'yandex_taxi',
            id='Disallowed pedestrian zone',
        ),
    ],
)
async def test_exclude_zone_from_depot_resolve(
        taxi_overlord_catalog,
        location,
        timeofday,
        expected_code,
        excluded_zones,
        expected_zone,
        taxi_config,
        mock_grocery_depots,
):
    """
    There is a single depot in the database with 4 zones:
    * foot zone is available 09:00-20:00
    * rover zone is available 09:00-20:00
    * taxi zone is available 07:00-24:00
    * night zone is available 00:00-07:00
    * remote zone is available 07:00-23:00
    The zones and markers used in tests can be viewed here
    https://gist.github.com/zmij/7ff63c8b9227bf72ad161098bae9d96c
    """
    mock_grocery_depots.load_json(
        'g-depots-as-default-sql.json', 'g-depots-zones-as-default-sql.json',
    )
    taxi_config.set_values(
        {'GROCERY_DEPOTS_CLIENT_EXCLUDED_DELIVERY_TYPES': excluded_zones},
    )
    await taxi_overlord_catalog.invalidate_caches()

    request = {
        'position': {'location': location},
        'time': '2020-09-09T{}:00+00:00'.format(timeofday),
    }

    response = await taxi_overlord_catalog.post(
        '/internal/v1/catalog/v1/depot-resolve', json=request,
    )

    assert response.status_code == 200
    assert 'zone_type' in response.json().keys()
    assert response.json()['zone_type'] == expected_zone


# zones and markers are here
# https://gist.github.com/zmij/7ff63c8b9227bf72ad161098bae9d96c
@pytest.mark.parametrize(
    'location, expected_code, expected_state',
    [
        pytest.param(
            # marker no 1
            MARKERS[0],
            200,
            'coming_soon',
            id='closed depot, coming soon zone',
        ),
        pytest.param(
            # marker no 6
            MARKERS[5],
            200,
            'disabled',
            id='already opened disabled depot',
        ),
        pytest.param(
            # marker no 9
            MARKERS[8],
            404,
            None,
            id='closed depot, disabled zone',
        ),
    ],
)
@pytest.mark.now('2021-06-01T10:00:00+00:00')
async def test_resolve_closed_depot_with_active_zone(
        taxi_overlord_catalog,
        location,
        expected_code,
        expected_state,
        mock_grocery_depots,
):
    """ Should return depot state == coming_soon for closed
    depot if open_ts is Null """
    mock_grocery_depots.load_json(
        'gdepots-depots-closed_depots_with_active_zone.json',
        'gdepots-zones-closed_depots_with_active_zone.json',
    )

    request = {'position': {'location': location}}

    response = await taxi_overlord_catalog.post(
        '/internal/v1/catalog/v1/depot-resolve', json=request,
    )

    assert response.status_code == expected_code
    response_json = response.json()
    assert ('state' in response_json) == (expected_state is not None)
    if expected_state is not None:
        assert response_json['state'] == expected_state


# zones and markers are here
# https://gist.github.com/zmij/7ff63c8b9227bf72ad161098bae9d96c
@pytest.mark.parametrize(
    'location, timeofday, external_id, expected_zone, expected_state, '
    'working_hours_idx, next_external_id, next_zone, next_state, '
    'next_depot_time',
    [
        pytest.param(
            # marker no 3
            MARKERS[2],
            '04:00',
            '111',
            'yandex_taxi_remote',
            'open',
            3,
            None,
            None,
            None,
            None,
            id='remote',
        ),
        pytest.param(
            # marker no 3
            MARKERS[2],
            '01:00',
            '111',
            'yandex_taxi_remote',
            'closed',
            None,
            '111',
            'yandex_taxi_remote',
            'closed',
            '04:00',
            id='remote at night',
        ),
        pytest.param(
            # marker no 1
            MARKERS[0],
            '04:30',
            '111',
            'yandex_taxi',
            'open',
            1,
            '112',
            'pedestrian',
            'closed',
            '06:00',
            id='taxi -> ped',
        ),
        pytest.param(
            # marker no 1
            MARKERS[0],
            '06:00',
            '112',
            'pedestrian',
            'open',
            0,
            '111',
            'yandex_taxi',
            'open',
            '17:00',
            id='ped -> taxi',
        ),
        pytest.param(
            # marker no 1
            MARKERS[0],
            '00:00',
            '111',
            'yandex_taxi_night',
            'open',
            2,
            '111',
            'yandex_taxi',
            'closed',
            '04:00',
            id='taxi_n -> taxi',
        ),
    ],
)
async def test_next_depot(
        taxi_overlord_catalog,
        location,
        timeofday,
        external_id,
        expected_zone,
        expected_state,
        working_hours_idx,
        next_external_id,
        next_zone,
        next_state,
        next_depot_time,
        load_json,
        mockserver,
):
    """
    Test for next_depot data in response.

    2 depots: 111, 112
    depot 111
    * taxi zone is available 07:00-24:00
    * night zone is available 00:00-08:00
    * remote zone is available 07:00-23:00
    depot 112
    * foot zone is available 09:00-20:00
    """
    setup_gdepots(
        mockserver,
        load_json('gdepots-depots-next_depot.json'),
        load_json('gdepots-zones-next_depot.json'),
    )
    working_hours_arr = [
        # ped
        {'from': {'hour': 9, 'minute': 0}, 'to': {'hour': 20, 'minute': 0}},
        # taxi
        {'from': {'hour': 7, 'minute': 0}, 'to': {'hour': 0, 'minute': 0}},
        # taxi-night
        {'from': {'hour': 0, 'minute': 0}, 'to': {'hour': 8, 'minute': 0}},
        # taxi-remote
        {'from': {'hour': 7, 'minute': 0}, 'to': {'hour': 23, 'minute': 0}},
    ]
    await taxi_overlord_catalog.invalidate_caches()

    request = {
        'position': {'location': location},
        'time': '2020-09-09T{}:00+00:00'.format(timeofday),
        'get_next_depot': True,
    }

    response = await taxi_overlord_catalog.post(
        '/internal/v1/catalog/v1/depot-resolve', json=request,
    )

    working_hours = None
    if working_hours_idx is not None:
        working_hours = working_hours_arr[working_hours_idx]

    resp_json = response.json()

    assert resp_json['depot_external_id'] == external_id
    assert 'zone_type' in resp_json.keys()
    assert resp_json['zone_type'] == expected_zone
    assert 'state' in resp_json.keys()
    assert resp_json['state'] == expected_state
    assert 'switch_time' in resp_json.keys()
    assert resp_json.get('working_hours', None) == working_hours

    if next_external_id is not None:
        assert resp_json['next_depot_time'] == '2020-09-09T{}:00+00:00'.format(
            next_depot_time,
        )
        next_depot = resp_json['next_depot']
        assert next_depot['depot_external_id'] == next_external_id
        next_depot_zone = next_depot['zone']
        assert next_depot_zone['zone_type'] == next_zone
        assert next_depot_zone['state'] == next_state
        assert 'switch_time' in next_depot_zone.keys()


# zones and markers are here
# https://gist.github.com/zmij/7ff63c8b9227bf72ad161098bae9d96c
@pytest.mark.parametrize(
    'location, timeofday, external_id, expected_zone, expected_state, '
    'working_hours_idx, availability_time_idx',
    [
        pytest.param(
            # marker no 1
            MARKERS[0],
            '00:00',
            '111',
            'yandex_taxi',
            'open',
            1,
            1,
            id='taxi 1',
        ),
        pytest.param(
            # marker no 1
            MARKERS[0],
            '20:59',
            '111',
            'yandex_taxi',
            'open',
            1,
            2,
            id='taxi 2',
        ),
        pytest.param(
            # marker no 1
            MARKERS[0],
            '4:00',
            '111',
            'pedestrian',
            'open',
            0,
            0,
            id='ped',
        ),
    ],
)
async def test_zones_24h(
        taxi_overlord_catalog,
        location,
        timeofday,
        external_id,
        expected_zone,
        expected_state,
        working_hours_idx,
        availability_time_idx,
        load_json,
        mockserver,
):
    """
    Test that for 2 zones available 24 hours.
    In all cases availability period must be exactly 24 hours.

    depot 111
    * foot zone is available 07:00-22:00
    * taxi zone is available 22:00-7:00
    """
    setup_gdepots(
        mockserver,
        load_json('gdepots-depots-24h.json'),
        load_json('gdepots-zones-24h.json'),
    )

    working_hours_arr = [
        # ped
        {'from': {'hour': 7, 'minute': 0}, 'to': {'hour': 22, 'minute': 0}},
        # taxi
        {'from': {'hour': 22, 'minute': 0}, 'to': {'hour': 7, 'minute': 0}},
    ]

    availability_time_arr = [
        # for time == '2020-09-09T04:00+00:00'
        {
            'from': '2020-09-09T04:00:00+00:00',
            'to': '2020-09-10T04:00:00+00:00',
        },
        # for time == '2020-09-09T00:00+00:00'
        {
            'from': '2020-09-08T19:00:00+00:00',
            'to': '2020-09-09T19:00:00+00:00',
        },
        # for time == '2020-09-09T20:59+00:00'
        {
            'from': '2020-09-09T19:00:00+00:00',
            'to': '2020-09-10T19:00:00+00:00',
        },
    ]
    await taxi_overlord_catalog.invalidate_caches()

    request = {
        'position': {'location': location},
        'time': '2020-09-09T{}:00+00:00'.format(timeofday),
        'get_next_depot': True,
        'get_availability_time': True,
    }

    response = await taxi_overlord_catalog.post(
        '/internal/v1/catalog/v1/depot-resolve', json=request,
    )

    resp_json = response.json()

    availability_time = resp_json['availability_time']
    assert (
        availability_time['from']
        == availability_time_arr[availability_time_idx]['from']
    )
    assert (
        availability_time['to']
        == availability_time_arr[availability_time_idx]['to']
    )

    assert resp_json['depot_external_id'] == external_id
    assert resp_json['zone_type'] == expected_zone
    assert resp_json['state'] == expected_state
    assert (
        resp_json.get('working_hours', None)
        == working_hours_arr[working_hours_idx]
    )


# zones and markers are here
# https://gist.github.com/zmij/7ff63c8b9227bf72ad161098bae9d96c
@pytest.mark.parametrize(
    'location, timeofday, external_id, expected_zone, expected_state, '
    'working_hours_idx',
    [
        pytest.param(
            # marker no 1
            MARKERS[0],
            '7:00',
            '111',
            'pedestrian',
            'open',
            0,
            id='24-hour ped',
        ),
    ],
)
async def test_zone_all_day(
        taxi_overlord_catalog,
        location,
        timeofday,
        external_id,
        expected_zone,
        expected_state,
        working_hours_idx,
        load_json,
        mockserver,
):
    """
    Test that for a 24 hour zone the all_day flag is returned.

    depot 111
    * foot zone is available 00:00-24:00
    """
    setup_gdepots(
        mockserver,
        load_json('gdepots-depots-zone_all_day.json'),
        load_json('gdepots-zones-zone_all_day.json'),
    )

    working_hours_arr = [
        # ped
        {'from': {'hour': 0, 'minute': 0}, 'to': {'hour': 0, 'minute': 0}},
    ]
    await taxi_overlord_catalog.invalidate_caches()

    request = {
        'position': {'location': location},
        'time': '2020-09-09T{}:00+00:00'.format(timeofday),
        'get_next_depot': True,
        'get_availability_time': True,
    }

    response = await taxi_overlord_catalog.post(
        '/internal/v1/catalog/v1/depot-resolve', json=request,
    )

    working_hours = None
    if working_hours_idx is not None:
        working_hours = working_hours_arr[working_hours_idx]

    resp_json = response.json()

    assert resp_json['all_day'] is True

    availability_time = resp_json['availability_time']
    assert availability_time['from'] == '2020-09-08T21:00:00+00:00'
    assert availability_time['to'] == '2020-09-09T21:00:00+00:00'

    assert resp_json['depot_external_id'] == external_id
    assert resp_json['zone_type'] == expected_zone
    assert resp_json['state'] == expected_state
    assert 'switch_time' in resp_json.keys()
    assert resp_json.get('working_hours', None) == working_hours

    assert 'next_depot_time' not in resp_json.keys()
    assert 'next_depot' not in resp_json.keys()


# zones and markers are here
# https://gist.github.com/zmij/7ff63c8b9227bf72ad161098bae9d96c
@pytest.mark.parametrize(
    'location, timeofday, external_id, expected_zone, expected_state, '
    'working_hours_idx, next_external_id, next_zone, next_state, '
    'next_working_hours_idx, next_depot_time',
    [
        pytest.param(
            # marker no 1
            MARKERS[0],
            '06:00',
            '111',
            'pedestrian',
            'open',
            0,
            None,
            None,
            None,
            None,
            '06:00',
            id='ped -> none',
        ),
        pytest.param(
            # marker no 1
            MARKERS[0],
            '00:00',
            '111',
            'pedestrian',
            'closed',
            None,
            '111',
            'pedestrian',
            'closed',
            0,
            '06:00',
            id='ped closed -> ped',
        ),
    ],
)
async def test_zone_working_hours_from_to_simple(
        taxi_overlord_catalog,
        location,
        timeofday,
        external_id,
        expected_zone,
        expected_state,
        working_hours_idx,
        next_external_id,
        next_zone,
        next_state,
        next_working_hours_idx,
        next_depot_time,
        load_json,
        mock_grocery_depots,
):
    """
    Простейший случай - одна некруглосуточная зона, провереятся наличие
    working_hours в текущей или следующей зоне.

    depot 111
    * foot zone is available 09:00-20:00
    """
    mock_grocery_depots.load_json(
        'gdepots-depots-zone_all_day.json', 'gdepots-zones-zone-from-to.json',
    )

    working_hours_arr = [
        # ped
        {'from': {'hour': 9, 'minute': 0}, 'to': {'hour': 20, 'minute': 0}},
        # taxi
        {'from': {'hour': 7, 'minute': 0}, 'to': {'hour': 0, 'minute': 0}},
        # taxi-night
        {'from': {'hour': 0, 'minute': 0}, 'to': {'hour': 8, 'minute': 0}},
        # taxi-remote
        {'from': {'hour': 7, 'minute': 0}, 'to': {'hour': 23, 'minute': 0}},
    ]
    await taxi_overlord_catalog.invalidate_caches()

    request = {
        'position': {'location': location},
        'time': '2020-09-09T{}:00+00:00'.format(timeofday),
        'get_next_depot': True,
        'get_availability_time': True,
    }

    response = await taxi_overlord_catalog.post(
        '/internal/v1/catalog/v1/depot-resolve', json=request,
    )

    working_hours = None
    if working_hours_idx is not None:
        working_hours = working_hours_arr[working_hours_idx]

    resp_json = response.json()

    assert resp_json['depot_external_id'] == external_id
    assert 'zone_type' in resp_json.keys()
    assert resp_json['zone_type'] == expected_zone
    assert 'state' in resp_json.keys()
    assert resp_json['state'] == expected_state
    assert 'switch_time' in resp_json.keys()
    assert resp_json.get('working_hours', None) == working_hours

    availability_time = resp_json['availability_time']
    assert availability_time['from'] == '2020-09-09T06:00:00+00:00'
    assert availability_time['to'] == '2020-09-09T17:00:00+00:00'

    if next_external_id is not None:
        assert resp_json['next_depot_time'] == '2020-09-09T{}:00+00:00'.format(
            next_depot_time,
        )
        next_depot = resp_json['next_depot']
        assert next_depot['depot_external_id'] == next_external_id
        next_depot_zone = next_depot['zone']
        assert next_depot_zone['zone_type'] == next_zone
        assert next_depot_zone['state'] == next_state
        assert 'switch_time' in next_depot_zone.keys()

        next_working_hours = None
        if next_working_hours_idx is not None:
            next_working_hours = working_hours_arr[next_working_hours_idx]

        assert next_depot_zone.get('working_hours', None) == next_working_hours


@pytest.mark.experiments3(
    name='region_hidings',
    consumers=['grocery-depots-internal/region_hidings'],
    clauses=[
        {
            'title': 'Hide market in Moscow',
            'predicate': {
                'init': {
                    'arg_name': 'application.brand',
                    'arg_type': 'string',
                    'value': 'market',
                },
                'type': 'eq',
            },
            'value': {'hidden_regions': [213]},
        },
    ],
    default_value={},
    is_config=True,
)
@pytest.mark.parametrize(
    'brand, status_code', [('lavka', 200), ('market', 404)],
)
async def test_depots_can_be_hidden_by_brands(
        taxi_overlord_catalog, brand, status_code, mock_grocery_depots,
):
    """
    Лавка может быть скрыта в определённом регионе для определённого
    бренда-потребителя.
    """
    mock_grocery_depots.load_json(
        'g-depots-as-default-sql.json', 'g-depots-zones-as-default-sql.json',
    )

    location = MARKERS[0]
    timeofday = '10:00'

    await taxi_overlord_catalog.invalidate_caches()

    request = {
        'position': {'location': location},
        'time': '2020-09-09T{}:00+00:00'.format(timeofday),
    }
    headers = {
        'X-Request-Application': (
            f'app_name=mobileweb_market_lavka_iphone,app_brand={brand}'
        ),
    }
    response = await taxi_overlord_catalog.post(
        '/internal/v1/catalog/v1/depot-resolve', json=request, headers=headers,
    )

    assert response.status_code == status_code
