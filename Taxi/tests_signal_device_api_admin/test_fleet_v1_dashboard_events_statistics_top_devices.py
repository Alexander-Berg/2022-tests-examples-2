# flake8: noqa
import typing

import pytest

from testsuite.utils import ordered_object

from tests_signal_device_api_admin import utils
from tests_signal_device_api_admin import web_common

ENDPOINT = (
    'fleet/signal-device-api-admin/v1/dashboard/events/statistics/top/devices'
)

FLEET_VEHICLE_C3 = {
    'data': {'car_id': 'c3', 'number': 'О122КХ777'},
    'park_id_car_id': 'p1_c3',
    'revision': '0_1574328384_71',
}
FLEET_VEHICLE_C4 = {
    'data': {'car_id': 'c4', 'number': 'E777КХ777'},
    'park_id_car_id': 'p1_c4',
    'revision': '0_1574328384_71',
}

DEVICE1 = {'id': 'pd1', 'serial_number': 'AB1'}
DEVICE2 = {'id': 'pd2', 'serial_number': 'AB12FE45DD'}
DEVICE3 = {'id': 'pd3', 'serial_number': 'FFEE33'}
DEVICE4 = {'id': 'pd4', 'serial_number': 'FFFDEAD4'}

THREAD_ID_DEVICE1 = utils.to_base64('||pd1').rstrip('=')
THREAD_ID_DEVICE2 = utils.to_base64('||pd2').rstrip('=')
THREAD_ID_DEVICE3 = utils.to_base64('||pd3').rstrip('=')
THREAD_ID_DEVICE4 = utils.to_base64('||pd4').rstrip('=')

VEHICLE1 = {'id': 'c3', 'plate_number': 'О122КХ777'}
VEHICLE2 = {'id': 'c4', 'plate_number': 'E777КХ777'}

RESPONSE1 = {
    'top_total': [
        {
            'device': DEVICE1,
            'thread_id': THREAD_ID_DEVICE1,
            'critical_amount': 4,
            'non_critical_amount': 0,
        },
        {
            'device': DEVICE2,
            'thread_id': THREAD_ID_DEVICE2,
            'critical_amount': 1,
            'non_critical_amount': 1,
            'vehicle': VEHICLE1,
        },
        {
            'device': DEVICE3,
            'thread_id': THREAD_ID_DEVICE3,
            'critical_amount': 1,
            'non_critical_amount': 0,
            'vehicle': VEHICLE2,
        },
        {
            'device': DEVICE4,
            'thread_id': THREAD_ID_DEVICE4,
            'critical_amount': 0,
            'non_critical_amount': 2,
        },
    ],
    'rest_total': {
        'devices_amount': 0,
        'critical_amount': 0,
        'non_critical_amount': 0,
    },
}

RESPONSE2 = {
    'top_total': [
        {
            'device': DEVICE1,
            'thread_id': THREAD_ID_DEVICE1,
            'critical_amount': 4,
            'non_critical_amount': 0,
        },
        {
            'device': DEVICE2,
            'thread_id': THREAD_ID_DEVICE2,
            'critical_amount': 1,
            'non_critical_amount': 1,
            'vehicle': VEHICLE1,
        },
    ],
    'rest_total': {
        'devices_amount': 2,
        'critical_amount': 1,
        'non_critical_amount': 2,
    },
}

RESPONSE3 = {
    'top_total': [
        {
            'device': DEVICE1,
            'thread_id': THREAD_ID_DEVICE1,
            'critical_amount': 1,
            'non_critical_amount': 3,
        },
        {
            'device': DEVICE3,
            'thread_id': THREAD_ID_DEVICE3,
            'critical_amount': 1,
            'non_critical_amount': 0,
            'vehicle': VEHICLE2,
        },
        {
            'device': DEVICE2,
            'thread_id': THREAD_ID_DEVICE2,
            'critical_amount': 0,
            'non_critical_amount': 1,
            'vehicle': VEHICLE1,
        },
    ],
    'rest_total': {
        'devices_amount': 0,
        'critical_amount': 0,
        'non_critical_amount': 0,
    },
}

RESPONSE4 = {
    'top_total': [
        {
            'device': DEVICE2,
            'thread_id': THREAD_ID_DEVICE2,
            'critical_amount': 0,
            'non_critical_amount': 1,
            'vehicle': VEHICLE1,
        },
    ],
    'rest_total': {
        'devices_amount': 0,
        'critical_amount': 0,
        'non_critical_amount': 0,
    },
}

RESPONSE5 = {
    'top_total': [
        {
            'device': DEVICE4,
            'thread_id': THREAD_ID_DEVICE4,
            'critical_amount': 0,
            'non_critical_amount': 2,
        },
        {
            'device': DEVICE3,
            'thread_id': THREAD_ID_DEVICE3,
            'critical_amount': 1,
            'non_critical_amount': 0,
            'vehicle': VEHICLE2,
        },
    ],
    'rest_total': {
        'devices_amount': 2,
        'critical_amount': 5,
        'non_critical_amount': 1,
    },
}


@pytest.mark.pgsql(
    'signal_device_api_meta_db', files=['pg_signal_device_api_meta_db.sql'],
)
@pytest.mark.parametrize(
    'park_id, period_from, period_to, critical_types, whitelist, '
    'top_amount, sort_order_direction, vehicles_response, expected_response',
    [
        (
            'p1',
            '2020-02-25T00:00:00+03:00',
            '2020-02-28T00:00:00+03:00',
            ['distraction', 'sleep'],
            None,
            None,
            'desc',
            {'vehicles': [FLEET_VEHICLE_C3, FLEET_VEHICLE_C4]},
            RESPONSE1,
        ),
        (
            'p1',
            '2020-02-25T00:00:00+03:00',
            '2020-02-28T00:00:00+03:00',
            ['distraction', 'sleep'],
            None,
            2,
            'desc',
            {'vehicles': [FLEET_VEHICLE_C3]},
            RESPONSE2,
        ),
        (
            'p1',
            '2020-02-25T00:00:00+03:00',
            '2020-02-28T00:00:00+03:00',
            ['distraction'],
            ['distraction', 'sleep'],
            None,
            None,
            {'vehicles': [FLEET_VEHICLE_C3, FLEET_VEHICLE_C4]},
            RESPONSE3,
        ),
        (
            'p1',
            '2020-02-27T23:00:00+03:00',
            '2020-02-28T00:00:00+03:00',
            ['distraction', 'sleep'],
            None,
            None,
            None,
            {'vehicles': [FLEET_VEHICLE_C3]},
            RESPONSE4,
        ),
        (
            'p1',
            '2020-02-25T00:00:00+03:00',
            '2020-02-28T00:00:00+03:00',
            ['distraction', 'sleep'],
            None,
            2,
            'asc',
            {'vehicles': [FLEET_VEHICLE_C4]},
            RESPONSE5,
        ),
    ],
)
async def test_v1_dashboard_events_statistics_top_devices(
        taxi_signal_device_api_admin,
        fleet_vehicles,
        pgsql,
        park_id,
        period_from,
        period_to,
        critical_types,
        whitelist,
        sort_order_direction,
        top_amount,
        vehicles_response,
        expected_response,
        mockserver,
):
    @mockserver.json_handler('/fleet-parks/v1/parks/list')
    def _mock_fleet_parks(request):
        return {
            'parks': [
                {
                    **web_common.get_fleet_parks_info(park_id),
                    'specifications': ['signalq'],
                },
            ],
        }

    if vehicles_response is not None:
        fleet_vehicles.set_fleet_vehicles_response(vehicles_response)

    body = {'period': {'from': period_from, 'to': period_to}}
    if sort_order_direction is not None:
        body['sort_order_direction'] = sort_order_direction
    if whitelist is not None:
        body['whitelist'] = whitelist
    if critical_types is not None:
        utils.add_park_critical_types_in_db(
            pgsql, park_id=park_id, critical_types=critical_types,
        )
    if top_amount is not None:
        body['top_amount'] = top_amount

    headers = {**web_common.YA_TEAM_HEADERS, 'X-Park-Id': park_id}
    response = await taxi_signal_device_api_admin.post(
        ENDPOINT, json=body, headers=headers,
    )
    assert response.status_code == 200, response.text
    ordered_object.assert_eq(response.json(), expected_response, paths='')


TOP_DEVICES = [
    {
        'device': {'id': 'dev2', 'serial_number': '77777'},
        'thread_id': utils.to_base64('||dev2').rstrip('='),
        'critical_amount': 2,
        'non_critical_amount': 6,
    },
    {
        'device': {'id': 'dev1', 'serial_number': '11111'},
        'thread_id': utils.to_base64('|v2|dev1').rstrip('='),
        'critical_amount': 2,
        'non_critical_amount': 4,
        'vehicle': {'id': 'v2', 'plate_number': 'Y777GD'},
    },
]


@pytest.mark.config(
    SIGNAL_DEVICE_API_ADMIN_DEMO_SETTINGS_V2={
        'timings': {
            'working_day_start': 8,
            'working_day_end': 20,
            'working_days_amount': 7,
        },
        'comments': ['Комментарий 1', 'Комментарий 2', 'Комментарий 3'],
        'media': {'__default__': {}},
        'devices': web_common.DEMO_DEVICES,
        'events': web_common.DEMO_EVENTS,
        'vehicles': web_common.DEMO_VEHICLES,
        'groups': [],
        'drivers': [],
    },
    SIGNAL_DEVICE_API_ADMIN_EVENTS_WEB_WHITELIST_V2=web_common.get_demo_whitelist(
        ['tired', 'seatbelt'],
    ),
)
@pytest.mark.parametrize(
    'period_from, period_to, top_amount, expected_response',
    [
        pytest.param(
            '2020-02-10T00:00:00+03:00',
            '2020-02-24T00:00:00+03:00',
            1,
            {
                'top_total': TOP_DEVICES[0:1],
                'rest_total': {
                    'devices_amount': 1,
                    'critical_amount': 2,
                    'non_critical_amount': 4,
                },
            },
            id='both top and res',
        ),
        pytest.param(
            '2020-02-10T00:00:00+03:00',
            '2020-02-24T00:00:00+03:00',
            30,
            {
                'top_total': TOP_DEVICES,
                'rest_total': {
                    'devices_amount': 0,
                    'critical_amount': 0,
                    'non_critical_amount': 0,
                },
            },
            id='all in top',
        ),
    ],
)
async def test_demo_v1_dashboard_events_statistics_top_devices(
        taxi_signal_device_api_admin,
        period_from,
        period_to,
        top_amount,
        expected_response,
        mockserver,
):
    @mockserver.json_handler('/fleet-parks/v1/parks/list')
    def _mock_fleet_parks(request):
        return {
            'parks': [
                {
                    **web_common.get_fleet_parks_info('no such park'),
                    'specifications': ['taxi'],
                },
            ],
        }

    body = {'period': {'from': period_from, 'to': period_to}}
    if top_amount is not None:
        body['top_amount'] = top_amount

    headers = {**web_common.YA_TEAM_HEADERS, 'X-Park-Id': 'no such park'}
    response = await taxi_signal_device_api_admin.post(
        ENDPOINT, json=body, headers=headers,
    )
    assert response.status_code == 200, response.text
    ordered_object.assert_eq(response.json(), expected_response, paths='')
