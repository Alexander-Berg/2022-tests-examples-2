import json

import pytest

import tests_dispatch_airport_view.utils as utils

URL = '/driver/v1/dispatch-airport-view/v1/driver_pin_info'

DRIVER_META = {
    'dbid_uuid0': {'updated_ts': '1000', 'geobus_ts': '1000'},
    'dbid_uuid1': {'updated_ts': '1001', 'geobus_ts': '1001'},
    'dbid_uuid2': {'updated_ts': '1002', 'geobus_ts': '1002'},
    'dbid_uuid3': {'updated_ts': '1003', 'geobus_ts': '1003'},
    'dbid_uuid4': {
        'updated_ts': '1004',
        'geobus_ts': '1004',
        'is_hidden': 'false',
    },
    'dbid_uuid5': {
        'updated_ts': '1005',
        'geobus_ts': '1005',
        'is_hidden': 'true',
    },
    'dbid_uuid6': {'updated_ts': '1006', 'geobus_ts': '1006'},
}


def _make_headers(uuid):
    return {
        **utils.HEADERS,
        'X-YaTaxi-Park-Id': 'dbid',
        'X-YaTaxi-Driver-Profile-Id': uuid,
    }


@pytest.mark.translations(taximeter_messages=utils.TAXIMETER_MESSAGES)
async def test_v1_driver_pins_info_no_active_port(taxi_dispatch_airport_view):
    codes = {'unknown': 'no_port', 'ekb': 'no_active_port'}
    for zone_id, code in codes.items():
        response = await taxi_dispatch_airport_view.get(
            URL,
            headers=_make_headers('uuid0'),
            params={'airport_id': zone_id},
        )
        assert response.status_code == 404
        r_json = response.json()
        assert r_json == {'code': code, 'message': 'Вы уехали слишком далеко'}


@pytest.mark.translations(taximeter_messages=utils.TAXIMETER_MESSAGES)
@pytest.mark.config(DISPATCH_AIRPORT_ZONES_TANKER_KEYS={})
@pytest.mark.geoareas(filename='geoareas.json')
async def test_v1_driver_pins_info_wrong_configuration(
        taxi_dispatch_airport_view,
):
    response = await taxi_dispatch_airport_view.get(
        URL, headers=_make_headers('uuid0'), params={'airport_id': 'ekb'},
    )
    assert response.status_code == 404
    r_json = response.json()
    assert r_json == {
        'code': 'wrong_configuration',
        'message': 'Вы уехали слишком далеко',
    }


@pytest.mark.translations(taximeter_messages=utils.TAXIMETER_MESSAGES)
@pytest.mark.geoareas(filename='geoareas.json')
@pytest.mark.redis_store(
    [
        'hmset',
        utils.driver_info_key('dbid_uuid5'),
        {**DRIVER_META['dbid_uuid5'], 'pins': json.dumps([])},
    ],
)
async def test_v1_driver_pins_info_driver_not_found(
        taxi_dispatch_airport_view,
):
    for uuid in ('unknown', 'uuid5'):
        response = await taxi_dispatch_airport_view.get(
            URL, headers=_make_headers(uuid), params={'airport_id': 'ekb'},
        )
        assert response.status_code == 404
        r_json = response.json()
        assert r_json == {
            'code': 'driver_not_found',
            'message': 'Вы уехали слишком далеко',
        }


@pytest.mark.redis_store(
    # driver hashes
    [
        'hmset',
        utils.driver_info_key('dbid_uuid0'),
        {
            **DRIVER_META['dbid_uuid0'],
            'pins': json.dumps([utils.ekb_pin_point(True, 3600)]),
        },
    ],
)
@pytest.mark.translations(taximeter_messages=utils.TAXIMETER_MESSAGES)
@pytest.mark.geoareas(filename='geoareas.json')
async def test_v1_driver_pins_info_driver_without_pins(
        taxi_dispatch_airport_view,
):
    response = await taxi_dispatch_airport_view.get(
        URL,
        headers=_make_headers('uuid0'),
        params={'airport_id': 'kamenskuralsky'},
    )
    assert response.status_code == 404
    r_json = response.json()
    assert r_json == {
        'code': 'driver_without_pin',
        'message': 'Вы уехали слишком далеко',
    }


@pytest.mark.redis_store(
    # driver hashes
    [
        'hmset',
        utils.driver_info_key('dbid_uuid0'),
        {
            **DRIVER_META['dbid_uuid0'],
            'pins': json.dumps(
                [
                    utils.ekb_pin_point(
                        True,
                        3660,
                        class_wait_times={
                            'econom': 3660,
                            'comfortplus': 4560,
                            'vip': None,
                        },
                    ),
                ],
            ),
        },
    ],
    [
        'hmset',
        utils.driver_info_key('dbid_uuid1'),
        {
            **DRIVER_META['dbid_uuid1'],
            'pins': json.dumps([utils.ekb_pin_point(False, 3660)]),
        },
    ],
    [
        'hmset',
        utils.driver_info_key('dbid_uuid2'),
        {
            **DRIVER_META['dbid_uuid2'],
            'pins': json.dumps(
                [
                    {
                        'airport_id': 'ekb',
                        'pin_point': utils.AIRPORT_EKB_POSITION,
                        'state': int(utils.PinState.kAllowedOldMode),
                        'class_wait_times': {'econom': 300},
                    },
                ],
            ),
        },
    ],
    [
        'hmset',
        utils.driver_info_key('dbid_uuid3'),
        {
            **DRIVER_META['dbid_uuid3'],
            'pins': json.dumps(
                [
                    {
                        'airport_id': 'ekb',
                        'pin_point': utils.AIRPORT_EKB_POSITION,
                        'state': int(utils.PinState.kNotAllowed),
                        'class_wait_times': {'econom': 300},
                        'last_allowed': {
                            'state': 0,
                            'time': '2021-12-12T09:09:00.000',
                        },
                    },
                ],
            ),
        },
    ],
    [
        'hmset',
        utils.driver_info_key('dbid_uuid4'),
        {
            **DRIVER_META['dbid_uuid4'],
            'pins': json.dumps(
                [
                    {
                        'airport_id': 'ekb',
                        'pin_point': utils.AIRPORT_EKB_POSITION,
                        'state': int(utils.PinState.kNotAllowed),
                        'class_wait_times': {'econom': 300},
                        'not_allowed_reason': 'driver_cancel',
                    },
                ],
            ),
        },
    ],
    [
        'hmset',
        utils.driver_info_key('dbid_uuid6'),
        {
            **DRIVER_META['dbid_uuid6'],
            'pins': json.dumps(
                [
                    utils.ekb_pin_point(
                        True,
                        3660,
                        class_wait_times={
                            'econom': 3660,
                            'comfortplus': 4560,
                            'vip': None,
                        },
                    ),
                ],
            ),
        },
    ],
)
@pytest.mark.now('2021-12-12T09:09:09.000')
@pytest.mark.translations(taximeter_messages=utils.TAXIMETER_MESSAGES)
@pytest.mark.translations(tariff=utils.TARIFF)
@pytest.mark.geoareas(filename='geoareas.json')
@pytest.mark.parametrize(
    'uuid, pin_state',
    [
        ('uuid0', 0),
        ('uuid1', 2),
        ('uuid2', 1),
        ('uuid3', 2),
        ('uuid4', 2),
        ('uuid6', 0),
    ],
)
@pytest.mark.config(DISPATCH_AIRPORT_VIEW_DRIVER_PIN_INFO_MAX_AGE=30)
async def test_v1_driver_pins_info(
        taxi_dispatch_airport_view,
        uuid,
        pin_state,
        load_json,
        mode,
        mockserver,
):
    @mockserver.json_handler('/driver-status/v2/statuses')
    def _driver_status(http_request):
        for driver in http_request.json['driver_ids']:
            assert driver['park_id'] == 'dbid'
            status = 'offline' if driver['driver_id'] == 'uuid6' else 'online'
            return mockserver.make_response(
                json={
                    'statuses': [
                        {
                            'driver_id': driver['driver_id'],
                            'park_id': 'dbid',
                            'status': status,
                        },
                    ],
                },
            )

    # dbid_uuid0 - allowed_all
    # dbid_uuid1 - not_allowed
    # dbid_uuid2 - allowed_old_mode
    # dbid_uuid3 - not allowed, was allowed 9 seconds ago
    # dbid_uuid4 - not allowed, reason = driver_cancel
    # dbid_uuid6 - offline driver

    await taxi_dispatch_airport_view.invalidate_caches()

    response = await taxi_dispatch_airport_view.get(
        URL, headers=_make_headers(uuid), params={'airport_id': 'ekb'},
    )
    assert response.status_code == 200
    assert response.headers['Cache-Control'] == 'max-age=30'
    r_json = response.json()

    pin_info = r_json['pin_info']
    geoarea = pin_info.pop('geoarea')
    assert 'coordinates' in geoarea['geometry']
    assert geoarea['geometry']['type'] == 'Polygon'
    if pin_state != 2:
        assert geoarea['options'] == {
            'line_color': '#169CDC',
            'fill_color': '#48169CDC',
        }
    else:
        assert geoarea['options'] == {
            'line_color': '#FA3E2C',
            'fill_color': '#14FA3E2C',
        }

    etalons = load_json('etalons.json')
    rules = etalons['rules'][
        'old_mode' if mode in ['old', 'mixed_base_old'] else 'new_mode'
    ]

    driver_etalon = etalons[uuid]
    for etalon_item in driver_etalon['main_items']['items']:
        if etalon_item['id'] == 'airport_pin_message':
            etalon_item['payload'] = rules

    pin_info['main_items']['items'].sort(key=lambda x: x['id'])
    assert pin_info == driver_etalon
