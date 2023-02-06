import json

import pytest

from tests_dispatcher_access_control import utils


ENDPOINT = '/fleet/dac/v1/parks/groups/grants-by-sections/'


def build_headers(park_id='park_valid1', accept_language='ru'):
    return {
        'X-Ya-User-Ticket': 'ticket_valid1',
        'X-Ya-User-Ticket-Provider': 'yandex',
        'X-Park-ID': park_id,
        'X-Ya-Service-Ticket': utils.MOCK_SERVICE_TICKET,
        'X-Yandex-UID': '100',
        'Accept-Language': accept_language,
    }


def build_params(group_id='group_valid1', section_id=None):
    params = {'group_id': group_id}
    if section_id is not None:
        params['section_id'] = section_id
    return params


OK_PARAMS = [
    (
        'en',
        None,
        {
            'grants_by_sections': [
                {
                    'grants': [
                        {
                            'hint': 'Access to the section',
                            'id': 'driver_read_common',
                            'is_enabled': True,
                            'name': 'Drivers',
                            'requires_confirm': False,
                            'sub_grants': [
                                {
                                    'id': 'driver_write_common',
                                    'is_enabled': True,
                                    'name': 'adding_a_driver',
                                    'requires_confirm': False,
                                },
                                {
                                    'id': 'driver_add_money',
                                    'is_enabled': True,
                                    'name': 'Пополнение баланса водителя',
                                    'requires_confirm': True,
                                },
                            ],
                        },
                    ],
                    'section': {
                        'grants_count': {'active': 3, 'all': 3},
                        'id': 'staff',
                        'name': 'Staff',
                    },
                },
                {
                    'grants': [
                        {
                            'hint': 'Access to the section',
                            'id': 'car_read_common',
                            'is_enabled': True,
                            'name': 'cars',
                            'requires_confirm': False,
                        },
                    ],
                    'section': {
                        'grants_count': {'active': 1, 'all': 1},
                        'id': 'car_park',
                        'name': 'car_park',
                    },
                },
            ],
        },
    ),
    (
        'ru',
        'staff',
        {
            'grants_by_sections': [
                {
                    'grants': [
                        {
                            'hint': 'Доступ к разделу',
                            'id': 'driver_read_common',
                            'is_enabled': True,
                            'name': 'Водители',
                            'requires_confirm': False,
                            'sub_grants': [
                                {
                                    'id': 'driver_write_common',
                                    'is_enabled': True,
                                    'name': 'adding_a_driver',
                                    'requires_confirm': False,
                                },
                                {
                                    'id': 'driver_add_money',
                                    'is_enabled': True,
                                    'name': 'Пополнение баланса водителя',
                                    'requires_confirm': True,
                                },
                            ],
                        },
                    ],
                    'section': {
                        'grants_count': {'active': 3, 'all': 3},
                        'id': 'staff',
                        'name': 'Персонал',
                    },
                },
            ],
        },
    ),
]


@pytest.mark.redis_store(
    [
        'hmset',
        'UserGroup:Items:park_valid1',
        {'group_valid1': json.dumps({'Name': 'Group1'})},
    ],
)
@pytest.mark.parametrize(
    'accept_language, section, expected_response', OK_PARAMS,
)
async def test_ok(
        taxi_dispatcher_access_control,
        taxi_config,
        mock_fleet_parks_list,
        mock_fleet_payouts,
        accept_language,
        section,
        expected_response,
):
    config_permissions = utils.build_config_permission(
        permission_id='_grant_driver_read_common',
    )
    config_permissions.update(
        utils.build_config_permission(
            permission_id='_grant_driver_write_common',
        ),
    )
    config_permissions.update(
        utils.build_config_permission(permission_id='_grant_car_read_common'),
    )
    config_permissions.update(
        utils.build_config_permission(permission_id='_grant_driver_add_money'),
    )

    taxi_config.set_values(
        dict(FLEET_ACCESS_CONTROL_PERMISSIONS=config_permissions),
    )
    await taxi_dispatcher_access_control.invalidate_caches()

    response = await taxi_dispatcher_access_control.get(
        ENDPOINT,
        params=build_params(section_id=section),
        headers=build_headers(accept_language=accept_language),
    )

    assert response.status_code == 200
    assert response.json() == expected_response


BAD_PARAMS = [
    (
        build_headers(park_id='park_invalid'),
        build_params(),
        {'code': 'park_not_found', 'message': 'Park not found'},
    ),
    (
        build_headers(),
        build_params(group_id='group_invalid'),
        {'code': 'group_not_found', 'message': 'Group not found'},
    ),
    (
        build_headers(),
        build_params(section_id='invalid'),
        {'code': 'section_not_found', 'message': 'Section not found'},
    ),
]


@pytest.mark.redis_store(
    [
        'hmset',
        'UserGroup:Items:park_valid1',
        {'group_valid1': json.dumps({'Name': 'Group1'})},
    ],
)
@pytest.mark.parametrize('headers, params, expected_response', BAD_PARAMS)
async def test_fail(
        taxi_dispatcher_access_control,
        taxi_config,
        mock_fleet_parks_list,
        mock_fleet_payouts,
        headers,
        params,
        expected_response,
):
    response = await taxi_dispatcher_access_control.get(
        ENDPOINT, params=params, headers=headers,
    )

    assert response.status_code == 404
    assert response.json() == expected_response
