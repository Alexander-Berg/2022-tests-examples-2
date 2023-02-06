# flake8: noqa
import pytest

from testsuite.utils import ordered_object

from tests_signal_device_api_admin import utils
from tests_signal_device_api_admin import web_common

ENDPOINT = (
    'fleet/signal-device-api-admin/v1/dashboard/events/statistics/top/drivers'
)

DRIVER_PROFILE_1 = {
    'car': {'id': 'car1', 'normalized_number': 'О122КХ777'},
    'driver_profile': {
        'first_name': 'Petr',
        'middle_name': 'D`',
        'last_name': 'Ivanov',
        'driver_license': {
            'expiration_date': '2025-08-07T00:00:00+0000',
            'issue_date': '2015-08-07T00:00:00+0000',
            'normalized_number': '7723306794',
            'number': '7723306794',
        },
        'id': 'd1',
        'phones': ['+79265975310'],
    },
}

DRIVER_PROFILE_2 = {
    'car': {'id': 'car1', 'normalized_number': 'О122КХ777'},
    'driver_profile': {
        'first_name': 'Vtoroi',
        'last_name': 'Voditel',
        'driver_license': {
            'expiration_date': '2025-08-07T00:00:00+0000',
            'issue_date': '2015-08-07T00:00:00+0000',
            'normalized_number': '7723306794',
            'number': '7723306794',
        },
        'id': 'd2',
        'phones': ['+79265975310'],
    },
}

DRIVER_PROFILES_LIST_SECOND_RESPONSE = {
    'driver_profiles': [DRIVER_PROFILE_2],
    'offset': 0,
    'parks': [{'id': 'p1'}],
    'total': 1,
    'limit': 300,
}

DRIVER_PROFILES_LIST_BOTH_RESPONSE = {
    'driver_profiles': [DRIVER_PROFILE_1, DRIVER_PROFILE_2],
    'offset': 0,
    'parks': [{'id': 'p1'}],
    'total': 2,
    'limit': 300,
}

THREAD_ID_DEVICE1_DRIVER1 = utils.to_base64('d1||pd1').rstrip('=')
THREAD_ID_DEVICE1_DRIVER2 = utils.to_base64('d2||pd1').rstrip('=')
THREAD_ID_DEVICE3_DRIVER3 = utils.to_base64('d3||pd3').rstrip('=')
THREAD_ID_DEVICE4_DRIVER4 = utils.to_base64('d4||pd4').rstrip('=')

DRIVER1 = {
    'id': 'd1',
    'first_name': 'Petr',
    'middle_name': 'D`',
    'last_name': 'Ivanov',
}
DRIVER2 = {'id': 'd2', 'first_name': 'Vtoroi', 'last_name': 'Voditel'}
DRIVER3 = {'id': 'd3'}
DRIVER4 = {'id': 'd4'}

RESPONSE1 = {
    'top_total': [
        {
            'driver': DRIVER1,
            'thread_id': THREAD_ID_DEVICE1_DRIVER1,
            'critical_amount': 4,
            'non_critical_amount': 0,
        },
        {
            'driver': DRIVER2,
            'thread_id': THREAD_ID_DEVICE1_DRIVER2,
            'critical_amount': 1,
            'non_critical_amount': 1,
        },
        {
            'driver': DRIVER3,
            'thread_id': THREAD_ID_DEVICE3_DRIVER3,
            'critical_amount': 1,
            'non_critical_amount': 0,
        },
        {
            'driver': DRIVER4,
            'thread_id': THREAD_ID_DEVICE4_DRIVER4,
            'critical_amount': 0,
            'non_critical_amount': 2,
        },
    ],
    'rest_total': {
        'drivers_amount': 0,
        'critical_amount': 0,
        'non_critical_amount': 0,
    },
}

RESPONSE2 = {
    'top_total': [
        {
            'driver': DRIVER1,
            'thread_id': THREAD_ID_DEVICE1_DRIVER1,
            'critical_amount': 4,
            'non_critical_amount': 0,
        },
        {
            'driver': DRIVER2,
            'thread_id': THREAD_ID_DEVICE1_DRIVER2,
            'critical_amount': 1,
            'non_critical_amount': 1,
        },
    ],
    'rest_total': {
        'drivers_amount': 2,
        'critical_amount': 1,
        'non_critical_amount': 2,
    },
}

RESPONSE3 = {
    'top_total': [
        {
            'driver': DRIVER1,
            'thread_id': THREAD_ID_DEVICE1_DRIVER1,
            'critical_amount': 1,
            'non_critical_amount': 3,
        },
        {
            'driver': DRIVER3,
            'thread_id': THREAD_ID_DEVICE3_DRIVER3,
            'critical_amount': 1,
            'non_critical_amount': 0,
        },
        {
            'driver': DRIVER2,
            'thread_id': THREAD_ID_DEVICE1_DRIVER2,
            'critical_amount': 0,
            'non_critical_amount': 1,
        },
    ],
    'rest_total': {
        'drivers_amount': 0,
        'critical_amount': 0,
        'non_critical_amount': 0,
    },
}

RESPONSE4 = {
    'top_total': [
        {
            'driver': DRIVER2,
            'thread_id': THREAD_ID_DEVICE1_DRIVER2,
            'critical_amount': 0,
            'non_critical_amount': 1,
        },
    ],
    'rest_total': {
        'drivers_amount': 0,
        'critical_amount': 0,
        'non_critical_amount': 0,
    },
}

RESPONSE5 = {
    'top_total': [
        {
            'driver': DRIVER4,
            'thread_id': THREAD_ID_DEVICE4_DRIVER4,
            'critical_amount': 0,
            'non_critical_amount': 2,
        },
        {
            'driver': DRIVER3,
            'thread_id': THREAD_ID_DEVICE3_DRIVER3,
            'critical_amount': 1,
            'non_critical_amount': 0,
        },
    ],
    'rest_total': {
        'drivers_amount': 2,
        'critical_amount': 5,
        'non_critical_amount': 1,
    },
}

RESPONSE6 = {
    'top_total': [
        {
            'driver': DRIVER1,
            'thread_id': THREAD_ID_DEVICE1_DRIVER1,
            'critical_amount': 4,
            'non_critical_amount': 0,
        },
        {
            'driver': DRIVER2,
            'thread_id': THREAD_ID_DEVICE1_DRIVER2,
            'critical_amount': 1,
            'non_critical_amount': 1,
        },
        {
            'driver': DRIVER4,
            'thread_id': THREAD_ID_DEVICE4_DRIVER4,
            'critical_amount': 0,
            'non_critical_amount': 1,
        },
    ],
    'rest_total': {
        'drivers_amount': 0,
        'critical_amount': 0,
        'non_critical_amount': 0,
    },
}


@pytest.mark.pgsql(
    'signal_device_api_meta_db', files=['pg_signal_device_api_meta_db.sql'],
)
@pytest.mark.parametrize(
    'park_id, period_from, period_to, critical_types, whitelist, '
    'top_amount, sort_order_direction, group, driver_profiles_response, expected_response',
    [
        (
            'p1',
            '2020-02-25T00:00:00+03:00',
            '2020-02-28T00:00:00+03:00',
            ['distraction', 'sleep'],
            None,
            None,
            'desc',
            None,
            [DRIVER_PROFILES_LIST_BOTH_RESPONSE],
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
            None,
            [DRIVER_PROFILES_LIST_BOTH_RESPONSE],
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
            None,
            [DRIVER_PROFILES_LIST_BOTH_RESPONSE],
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
            None,
            [DRIVER_PROFILES_LIST_SECOND_RESPONSE],
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
            None,
            [DRIVER_PROFILES_LIST_BOTH_RESPONSE],
            RESPONSE5,
        ),
        (
            'p1',
            '2020-02-25T00:00:00+03:00',
            '2020-02-28T00:00:00+03:00',
            ['distraction', 'sleep'],
            None,
            None,
            'desc',
            'g1',
            [DRIVER_PROFILES_LIST_BOTH_RESPONSE],
            RESPONSE6,
        ),
    ],
)
async def test_v1_dashboard_events_statistics_top_drivers(
        taxi_signal_device_api_admin,
        parks,
        pgsql,
        park_id,
        period_from,
        period_to,
        critical_types,
        whitelist,
        top_amount,
        sort_order_direction,
        group,
        driver_profiles_response,
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

    if driver_profiles_response is not None:
        parks.set_driver_profiles_response(driver_profiles_response)

    body = {'period': {'from': period_from, 'to': period_to}}
    if group is not None:
        body['filter'] = {'group_id': 'g1'}
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


TOP_DRIVERS = [
    {
        'driver': {
            'id': 'dr2',
            'first_name': 'Grisha',
            'last_name': 'Dergachev',
        },
        'thread_id': utils.to_base64('dr2||dev2').rstrip('='),
        'critical_amount': 2,
        'non_critical_amount': 2,
    },
    {
        'driver': {'id': 'dr1', 'first_name': 'Roman', 'last_name': 'Maresov'},
        'thread_id': utils.to_base64('dr1||dev1').rstrip('='),
        'critical_amount': 0,
        'non_critical_amount': 4,
    },
]


@pytest.mark.now('2021-12-31T16:00:00+03:00')
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
        'drivers': web_common.DEMO_DRIVERS,
    },
    SIGNAL_DEVICE_API_ADMIN_EVENTS_WEB_WHITELIST_V2=web_common.get_demo_whitelist(
        ['ushel v edu'],
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
                'top_total': TOP_DRIVERS[0:1],
                'rest_total': {
                    'drivers_amount': 1,
                    'critical_amount': 0,
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
                'top_total': TOP_DRIVERS,
                'rest_total': {
                    'drivers_amount': 0,
                    'critical_amount': 0,
                    'non_critical_amount': 0,
                },
            },
            id='all in top',
        ),
    ],
)
async def test_demo_v1_dashboard_events_statistics_top_drivers(
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
