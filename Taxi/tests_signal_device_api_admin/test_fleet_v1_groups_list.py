import copy
import typing

import pytest

from tests_signal_device_api_admin import utils
from tests_signal_device_api_admin import web_common

ENDPOINT = 'fleet/signal-device-api-admin/v1/groups/list'


P1_RESPONSE: typing.Dict[str, typing.List[typing.Dict]] = {'groups': []}

P2_RESPONSE = {
    'groups': [
        {
            'group_id': '29a168a6-2fe3-401d-9959-ba1b14fd4862',
            'group_name': 'South',
            'has_subgroups': True,
            'devices_count': 3,
        },
        {
            'group_id': '09a1d1ab-6e60-4d7b-9144-dfad7fcf9000',
            'group_name': 'Some',
            'has_subgroups': False,
            'devices_count': 1,
        },
        {
            'group_id': '4552f39f-e868-46c1-8139-b5bf2dcda760',
            'group_name': 'Body',
            'has_subgroups': False,
            'devices_count': 0,
        },
    ],
}

P3_RESPONSE = {
    'groups': [
        {
            'group_id': '12bb68a6-aae3-421d-9119-ca1c14fd4862',
            'group_name': 'North',
            'has_subgroups': False,
            'devices_count': 0,
        },
        {
            'group_id': '2480430f-8dc2-4217-b2d4-1e9806c3bd2a',
            'group_name': 'SouthWest',
            'has_subgroups': False,
            'devices_count': 1,
        },
    ],
}

P2_RESPONSE_WITH_PARENT = {
    'groups': [
        {
            'group_id': '1db9bcc6-982c-46ff-a161-78fa1817be01',
            'group_name': 'SouthWestHam',
            'has_subgroups': False,
            'devices_count': 2,
        },
        {
            'group_id': '51035bca-2011-4306-b148-8ff08c6f7a31',
            'group_name': 'SouthEast',
            'has_subgroups': False,
            'devices_count': 0,
        },
    ],
}

EMPTY_RESPONSE: typing.Dict[str, typing.List[typing.Dict]] = {'groups': []}


@pytest.mark.pgsql(
    'signal_device_api_meta_db', files=['pg_signal_device_api_meta_db.sql'],
)
@pytest.mark.parametrize(
    'park_id, parent_group_id, expected_code, expected_response',
    [
        ('p1', None, 200, P1_RESPONSE),
        ('p2', None, 200, P2_RESPONSE),
        ('p3', None, 200, P3_RESPONSE),
        (
            'p2',
            '29a168a6-2fe3-401d-9959-ba1b14fd4862',
            200,
            P2_RESPONSE_WITH_PARENT,
        ),
        ('p1252', None, 200, EMPTY_RESPONSE),
        ('p1252', '29a168a6-2fe3-401d-9959-ba1b14fd4862', 200, EMPTY_RESPONSE),
    ],
)
async def test_groups_list_without_cursor(
        taxi_signal_device_api_admin,
        park_id,
        parent_group_id,
        expected_code,
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

    headers = {**web_common.PARTNER_HEADERS_1, 'X-Park-Id': park_id}

    body = (
        {'parent_group_id': parent_group_id}
        if parent_group_id is not None
        else {}
    )

    response = await taxi_signal_device_api_admin.post(
        ENDPOINT, json=body, headers=headers,
    )

    assert response.status_code == expected_code, response.text
    assert response.json() == expected_response


P2_RESPONSE_WITH_CURSOR1 = {
    'groups': P2_RESPONSE['groups'][:2],
    'cursor': utils.get_encoded_groups_list_cursor(
        created_at='2021-07-11T00:00:00.123456+00:00',
        group_id='09a1d1ab-6e60-4d7b-9144-dfad7fcf9000',
    ),
}
P2_RESPONSE_WITH_CURSOR2 = {'groups': [P2_RESPONSE['groups'][2]]}

P2_RESPONSE_WITH_PARENT_WITH_CURSOR1 = {
    'groups': [P2_RESPONSE_WITH_PARENT['groups'][0]],
    'cursor': utils.get_encoded_groups_list_cursor(
        created_at='2021-06-30T00:00:00.000001+00:00',
        group_id='1db9bcc6-982c-46ff-a161-78fa1817be01',
    ),
}
P2_RESPONSE_WITH_PARENT_WITH_CURSOR2 = {
    'groups': [P2_RESPONSE_WITH_PARENT['groups'][1]],
    'cursor': utils.get_encoded_groups_list_cursor(
        created_at='2021-06-30T00:00:00.000001+00:00',
        group_id='51035bca-2011-4306-b148-8ff08c6f7a31',
    ),
}

P3_RESPONSE_WITH_CURSOR1 = copy.deepcopy(P3_RESPONSE)
P3_RESPONSE_WITH_CURSOR1['cursor'] = utils.get_encoded_groups_list_cursor(
    created_at='2021-06-30T00:00:00.000001+00:00',
    group_id='2480430f-8dc2-4217-b2d4-1e9806c3bd2a',
)
P3_RESPONSE_WITH_CURSOR2: typing.Dict[str, typing.List[typing.Dict]] = {
    'groups': [],
}


@pytest.mark.pgsql(
    'signal_device_api_meta_db', files=['pg_signal_device_api_meta_db.sql'],
)
@pytest.mark.config(
    SIGNAL_DEVICE_API_ADMIN_DEVICE_GROUPS_LIMITS_V2={
        'groups_list_limit': 2,
        'group_devices_list_limit': 20,
        'ungrouped_devices_list_limit': 1,
    },
)
@pytest.mark.parametrize(
    'park_id, parent_group_id, expected_response1, expected_response2',
    [
        ('p1', None, P1_RESPONSE, None),
        ('p2', None, P2_RESPONSE_WITH_CURSOR1, P2_RESPONSE_WITH_CURSOR2),
        ('p3', None, P3_RESPONSE_WITH_CURSOR1, P3_RESPONSE_WITH_CURSOR2),
        pytest.param(
            'p2',
            '29a168a6-2fe3-401d-9959-ba1b14fd4862',
            P2_RESPONSE_WITH_PARENT_WITH_CURSOR1,
            P2_RESPONSE_WITH_PARENT_WITH_CURSOR2,
            marks=pytest.mark.config(
                SIGNAL_DEVICE_API_ADMIN_DEVICE_GROUPS_LIMITS_V2={
                    'groups_list_limit': 1,
                    'group_devices_list_limit': 20,
                    'ungrouped_devices_list_limit': 1,
                },
            ),
        ),
    ],
)
async def test_groups_list_with_cursor(
        taxi_signal_device_api_admin,
        park_id,
        parent_group_id,
        expected_response1,
        expected_response2,
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

    headers = {**web_common.PARTNER_HEADERS_1, 'X-Park-Id': park_id}

    body = (
        {'parent_group_id': parent_group_id}
        if parent_group_id is not None
        else {}
    )

    response = await taxi_signal_device_api_admin.post(
        ENDPOINT, json=body, headers=headers,
    )

    assert response.status_code == 200, response.text
    response_json = response.json()
    assert response_json == expected_response1

    if expected_response2 is None:
        return

    body['cursor'] = response_json.pop('cursor')
    response = await taxi_signal_device_api_admin.post(
        ENDPOINT, json=body, headers=headers,
    )
    assert response.status_code == 200, response.text
    assert response.json() == expected_response2


ALL_GROUPS_RESPONSE = [
    {
        'group_id': 'g1',
        'group_name': 'SuperWeb',
        'has_subgroups': True,
        'devices_count': 1,
    },
    {
        'group_id': 'sg1',
        'group_name': 'SignalQ',
        'has_subgroups': False,
        'devices_count': 1,
    },
    {
        'group_id': 'g2',
        'group_name': 'Scooters',
        'has_subgroups': False,
        'devices_count': 1,
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
        'events': [],
        'vehicles': [],
        'groups': web_common.DEMO_GROUPS,
        'drivers': [],
    },
    SIGNAL_DEVICE_API_ADMIN_DEVICE_GROUPS_LIMITS_V2={
        'groups_list_limit': 2,
        'group_devices_list_limit': 2,
        'ungrouped_devices_list_limit': 2,
    },
)
@pytest.mark.parametrize(
    'parent_group_id, expected_response',
    [
        pytest.param(
            None, [ALL_GROUPS_RESPONSE[0], ALL_GROUPS_RESPONSE[2]], id='all',
        ),
        pytest.param('g1', ALL_GROUPS_RESPONSE[1:2], id='subgroups'),
    ],
)
async def test_demo_groups_list(
        taxi_signal_device_api_admin,
        parent_group_id,
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

    json = {}
    if parent_group_id:
        json = {'parent_group_id': parent_group_id}
    response = await taxi_signal_device_api_admin.post(
        ENDPOINT,
        json=json,
        headers={**web_common.PARTNER_HEADERS_1, 'X-Park-Id': 'no such park'},
    )
    assert response.status_code == 200, response.text
    assert response.json()['groups'] == expected_response


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
        'events': [],
        'vehicles': [],
        'groups': web_common.DEMO_GROUPS,
        'drivers': [],
    },
    SIGNAL_DEVICE_API_ADMIN_DEVICE_GROUPS_LIMITS_V2={
        'groups_list_limit': 2,
        'group_devices_list_limit': 2,
        'ungrouped_devices_list_limit': 2,
    },
)
async def test_demo_groups_list_cursor(
        taxi_signal_device_api_admin, mockserver,
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

    response = await taxi_signal_device_api_admin.post(
        ENDPOINT,
        json={},
        headers={**web_common.PARTNER_HEADERS_1, 'X-Park-Id': 'no such park'},
    )
    assert response.status_code == 200, response.text
    response_json = response.json()
    assert response_json['groups'] == [
        ALL_GROUPS_RESPONSE[0],
        ALL_GROUPS_RESPONSE[2],
    ]

    response = await taxi_signal_device_api_admin.post(
        ENDPOINT,
        json={'cursor': response_json['cursor']},
        headers={**web_common.PARTNER_HEADERS_1, 'X-Park-Id': 'no such park'},
    )
    assert response.status_code == 200, response.text
    assert response.json()['groups'] == ALL_GROUPS_RESPONSE[1:2]
