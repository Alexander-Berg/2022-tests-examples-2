import json

import pytest

from tests_dispatcher_access_control import utils

ENDPOINT = 'v1/parks/users/permissions/list'
PARK_ID = 'park_valid1'
PERMISSION_ID_2 = 'permission_2'


def build_headers(
        user_ticket='ticket_valid1',
        user_ticket_provider='yandex',
        service_ticket=utils.MOCK_SERVICE_TICKET,
):
    return {
        'X-Ya-User-Ticket': user_ticket,
        'X-Ya-User-Ticket-Provider': user_ticket_provider,
        'X-Ya-Service-Ticket': service_ticket,
    }


async def _make_request(
        taxi_dispatcher_access_control,
        headers_params=None,
        expected_permissions=None,
):
    headers = (
        build_headers()
        if headers_params is None
        else build_headers(**headers_params)
    )
    permissions = [] if expected_permissions is None else expected_permissions
    response = await taxi_dispatcher_access_control.get(
        ENDPOINT, params={'park_id': PARK_ID}, headers=headers,
    )

    assert response.status_code == 200, response.text
    assert sorted(response.json()['permissions']) == sorted(permissions)


def build_filter_park(
        countries=None,
        countries_exclude=None,
        cities=None,
        cities_exclude=None,
        park_ids=None,
        park_ids_exclude=None,
        park_types=None,
        brands=None,
        demo_mode=None,
        uber=None,
        has_clid=None,
        ui_mode=None,
        relationship=None,
        specifications=None,
        required_specifications=None,
        fleet_version=None,
):
    filter_park = dict()
    if countries is not None:
        filter_park['countries'] = countries
    if countries_exclude is not None:
        filter_park['countries_exclude'] = countries_exclude
    if cities is not None:
        filter_park['cities'] = cities
    if cities_exclude is not None:
        filter_park['cities_exclude'] = cities_exclude
    if park_ids is not None:
        filter_park['park_ids'] = park_ids
    if park_ids_exclude is not None:
        filter_park['park_ids_exclude'] = park_ids_exclude
    if park_types is not None:
        filter_park['park_types'] = park_types
    if brands is not None:
        filter_park['brands'] = brands
    if demo_mode is not None:
        filter_park['demo_mode'] = demo_mode
    if uber is not None:
        filter_park['uber'] = uber
    if ui_mode is not None:
        filter_park['ui_mode'] = ui_mode
    if has_clid is not None:
        filter_park['has_clid'] = has_clid
    if relationship is not None:
        filter_park['relationship'] = relationship
    if specifications is not None:
        filter_park['specifications'] = specifications
    if required_specifications is not None:
        filter_park['required_specifications'] = required_specifications
    if fleet_version is not None:
        filter_park['fleet_version'] = fleet_version

    return filter_park or None


def build_filter_user(superuser=None, grant=None, role=None, provider=None):
    filter_user = dict()
    if superuser is not None:
        filter_user['superuser'] = superuser
    if grant is not None:
        filter_user['grant'] = grant
    if role is not None:
        filter_user['role'] = role
    if provider is not None:
        filter_user['provider'] = provider

    return filter_user or None


def build_filter(
        countries=None,
        countries_exclude=None,
        cities=None,
        cities_exclude=None,
        park_ids=None,
        park_ids_exclude=None,
        park_types=None,
        brands=None,
        demo_mode=None,
        uber=None,
        ui_mode=None,
        has_clid=None,
        relationship=None,
        specifications=None,
        required_specifications=None,
        fleet_version=None,
        superuser=None,
        grant=None,
        role=None,
        provider=None,
):
    permission_filter = dict()
    filter_park = build_filter_park(
        countries=countries,
        countries_exclude=countries_exclude,
        cities=cities,
        cities_exclude=cities_exclude,
        park_ids=park_ids,
        park_ids_exclude=park_ids_exclude,
        park_types=park_types,
        brands=brands,
        demo_mode=demo_mode,
        uber=uber,
        has_clid=has_clid,
        ui_mode=ui_mode,
        relationship=relationship,
        specifications=specifications,
        required_specifications=required_specifications,
        fleet_version=fleet_version,
    )
    if filter_park is not None:
        permission_filter['park'] = filter_park
    filter_user = build_filter_user(superuser, grant, role, provider)
    if filter_user is not None:
        permission_filter['user'] = filter_user

    return permission_filter


ENABLED_FOR_PARAMS = [
    ('all', 'yandex', [utils.PERMISSION_ID]),
    ('all', 'yandex_team', [utils.PERMISSION_ID]),
    ('yandex', 'yandex', [utils.PERMISSION_ID]),
    ('yandex', 'yandex_team', []),
    ('yandex_team', 'yandex', []),
    ('yandex_team', 'yandex_team', [utils.PERMISSION_ID]),
    ('none', 'yandex', []),
    ('none', 'yandex_team', []),
]


@pytest.mark.redis_store(
    [
        'hmset',
        'User:Items:park_valid1',
        {
            'user_valid1': json.dumps(
                {
                    'Enable': True,
                    'Group': 'group_valid1',
                    'Name': 'Admin',
                    'Email': 'admin@yandex.ru',
                    'Phones': '',
                    'YandexConfirmed': True,
                    'IsSuperUser': False,
                    'YandexLogin': 'admin',
                    'YandexUid': '100',
                },
            ),
        },
    ],
)
@pytest.mark.parametrize(
    'enabled_for, ticket_provider, expected_permissions', ENABLED_FOR_PARAMS,
)
async def test_ok_enabled_for(
        taxi_dispatcher_access_control,
        mock_fleet_parks_list,
        mock_fleet_payouts,
        blackbox_service,
        taxi_config,
        enabled_for,
        ticket_provider,
        expected_permissions,
):
    blackbox_service.set_user_ticket_info(
        'ticket_valid1', '100', 'admin@yandex.ru',
    )

    taxi_config.set_values(
        dict(
            FLEET_ACCESS_CONTROL_PERMISSIONS=utils.build_config_permission(
                enabled_for=enabled_for,
            ),
        ),
    )
    await taxi_dispatcher_access_control.invalidate_caches()
    await _make_request(
        taxi_dispatcher_access_control,
        headers_params={'user_ticket_provider': ticket_provider},
        expected_permissions=expected_permissions,
    )


IS_INTERNAL_PARAMS = [(False, [utils.PERMISSION_ID]), (True, [])]


@pytest.mark.redis_store(
    [
        'hmset',
        'User:Items:park_valid1',
        {
            'user_valid1': json.dumps(
                {
                    'Enable': True,
                    'Group': 'group_valid1',
                    'Name': 'Admin',
                    'Email': 'admin@yandex.ru',
                    'Phones': '',
                    'YandexConfirmed': True,
                    'IsSuperUser': False,
                    'YandexLogin': 'admin',
                    'YandexUid': '100',
                },
            ),
        },
    ],
)
@pytest.mark.parametrize(
    'is_internal, expected_permissions', IS_INTERNAL_PARAMS,
)
async def test_is_internal(
        taxi_dispatcher_access_control,
        mock_fleet_parks_list,
        mock_fleet_payouts,
        blackbox_service,
        taxi_config,
        is_internal,
        expected_permissions,
):
    blackbox_service.set_user_ticket_info(
        'ticket_valid1', '100', 'admin@yandex.ru',
    )

    taxi_config.set_values(
        dict(
            FLEET_ACCESS_CONTROL_PERMISSIONS=utils.build_config_permission(
                is_internal=is_internal,
            ),
        ),
    )
    await taxi_dispatcher_access_control.invalidate_caches()
    await _make_request(
        taxi_dispatcher_access_control,
        expected_permissions=expected_permissions,
    )


REQUIRED_PERMISSION_PARAMS = [
    (
        'all',
        [
            utils.PERMISSION_ID,
            'required_permission_1',
            'required_permission_2',
        ],
    ),
    ('none', ['required_permission_1']),
]


@pytest.mark.redis_store(
    [
        'hmset',
        'User:Items:park_valid1',
        {
            'user_valid1': json.dumps(
                {
                    'Enable': True,
                    'Group': 'group_valid1',
                    'Name': 'Admin',
                    'Email': 'admin@yandex.ru',
                    'Phones': '',
                    'YandexConfirmed': True,
                    'IsSuperUser': False,
                    'YandexLogin': 'admin',
                    'YandexUid': '100',
                },
            ),
        },
    ],
)
@pytest.mark.parametrize(
    'required_enabled_for, expected_permissions', REQUIRED_PERMISSION_PARAMS,
)
async def test_required_permission(
        taxi_dispatcher_access_control,
        blackbox_service,
        mock_fleet_parks_list,
        mock_fleet_payouts,
        taxi_config,
        required_enabled_for,
        expected_permissions,
):
    blackbox_service.set_user_ticket_info(
        'ticket_valid1', '100', 'admin@yandex.ru',
    )

    config_permissions = utils.build_config_permission(
        required_permissions=[
            'required_permission_1',
            'required_permission_2',
        ],
    )
    config_permissions.update(
        utils.build_config_permission(
            permission_id='required_permission_1', enabled_for='all',
        ),
    )
    config_permissions.update(
        utils.build_config_permission(
            permission_id='required_permission_2',
            enabled_for=required_enabled_for,
        ),
    )

    taxi_config.set_values(
        dict(FLEET_ACCESS_CONTROL_PERMISSIONS=config_permissions),
    )
    await taxi_dispatcher_access_control.invalidate_caches()
    await _make_request(
        taxi_dispatcher_access_control,
        expected_permissions=expected_permissions,
    )


@pytest.mark.redis_store(
    [
        'hmset',
        'User:Items:park_valid1',
        {
            'user_valid1': json.dumps(
                {
                    'Enable': True,
                    'Group': 'group_valid1',
                    'Name': 'Admin',
                    'Email': 'admin@yandex.ru',
                    'Phones': '',
                    'YandexConfirmed': True,
                    'IsSuperUser': False,
                    'YandexLogin': 'admin',
                    'YandexUid': '100',
                },
            ),
        },
    ],
)
async def test_required_permission_loop(
        taxi_dispatcher_access_control,
        blackbox_service,
        mock_fleet_parks_list,
        mock_fleet_payouts,
        taxi_config,
):
    blackbox_service.set_user_ticket_info(
        'ticket_valid1', '100', 'admin@yandex.ru',
    )

    config_permissions = utils.build_config_permission(
        permission_id='permission_1', required_permissions=['permission_2'],
    )
    config_permissions.update(
        utils.build_config_permission(
            permission_id='permission_2',
            required_permissions=['permission_1'],
        ),
    )

    taxi_config.set_values(
        dict(FLEET_ACCESS_CONTROL_PERMISSIONS=config_permissions),
    )
    await taxi_dispatcher_access_control.invalidate_caches()
    await _make_request(taxi_dispatcher_access_control)


@pytest.mark.redis_store(
    [
        'hmset',
        'User:Items:park_valid1',
        {
            'user_valid1': json.dumps(
                {
                    'Enable': True,
                    'Group': 'group_valid1',
                    'Name': 'Admin',
                    'Email': 'admin@yandex.ru',
                    'Phones': '',
                    'YandexConfirmed': True,
                    'IsSuperUser': False,
                    'YandexLogin': 'admin',
                    'YandexUid': '100',
                },
            ),
        },
    ],
)
async def test_required_undefined_permission(
        taxi_dispatcher_access_control,
        blackbox_service,
        mock_fleet_parks_list,
        mock_fleet_payouts,
        taxi_config,
):
    blackbox_service.set_user_ticket_info(
        'ticket_valid1', '100', 'admin@yandex.ru',
    )

    config_permissions = utils.build_config_permission(
        permission_id='permission_1',
        required_permissions=['undefined_permission'],
    )

    taxi_config.set_values(
        dict(FLEET_ACCESS_CONTROL_PERMISSIONS=config_permissions),
    )
    await taxi_dispatcher_access_control.invalidate_caches()
    await _make_request(taxi_dispatcher_access_control)


FILTER_PARAMS = [
    (build_filter(countries=['cid1']), [utils.PERMISSION_ID]),
    (build_filter(countries_exclude=['cid1']), []),
    (build_filter(cities=['city1']), [utils.PERMISSION_ID]),
    (build_filter(cities_exclude=['city1']), []),
    (build_filter(park_ids=['park_valid1']), [utils.PERMISSION_ID]),
    (build_filter(park_ids_exclude=['park_valid1']), []),
    (build_filter(park_types=['taxi-company']), []),
    (build_filter(park_types=['self-employed-fns']), []),
    (build_filter(park_types=['self-employed-ie']), [utils.PERMISSION_ID]),
    (build_filter(brands=['yandex', 'uber']), []),
    (build_filter(brands=['uber-driver']), [utils.PERMISSION_ID]),
    (build_filter(demo_mode=False), [utils.PERMISSION_ID]),
    (build_filter(demo_mode=True), []),
    (build_filter(uber=False), []),
    (build_filter(uber=True), [utils.PERMISSION_ID]),
    (build_filter(ui_mode='default'), [utils.PERMISSION_ID]),
    (build_filter(ui_mode='small'), []),
    (build_filter(relationship='direct-contract'), [utils.PERMISSION_ID]),
    (build_filter(relationship='sub-contract'), []),
    (build_filter(superuser=True), []),
    (build_filter(superuser=False), [utils.PERMISSION_ID]),
    (build_filter(required_specifications=['spec1']), [utils.PERMISSION_ID]),
    (build_filter(required_specifications=['spec999']), []),
    (
        build_filter(specifications={'include': ['spec1']}),
        [utils.PERMISSION_ID],
    ),
    (build_filter(specifications={'include': ['spec999']}), []),
    (
        build_filter(specifications={'exclude': ['spec999']}),
        [utils.PERMISSION_ID],
    ),
    (build_filter(specifications={'exclude': ['spec1']}), []),
    (
        build_filter(specifications={'equal': ['spec1', 'spec2']}),
        [utils.PERMISSION_ID],
    ),
    (build_filter(specifications={'equal': ['spec1']}), []),
    (build_filter(provider='yandex'), [utils.PERMISSION_ID]),
    (build_filter(provider='yandex_team'), []),
    (build_filter(has_clid=True), [utils.PERMISSION_ID]),
    (build_filter(has_clid=False), []),
    (build_filter(fleet_version='basic'), [utils.PERMISSION_ID]),
    (build_filter(fleet_version='simple'), []),
]


@pytest.mark.redis_store(
    [
        'hmset',
        'User:Items:park_valid1',
        {
            'user_valid1': json.dumps(
                {
                    'Enable': True,
                    'Group': 'group_valid1',
                    'Name': 'Admin',
                    'Email': 'admin@yandex.ru',
                    'Phones': '',
                    'YandexConfirmed': True,
                    'IsSuperUser': False,
                    'YandexLogin': 'admin',
                    'YandexUid': '100',
                },
            ),
        },
    ],
    [
        'hmset',
        'UserGroup:Items:park_valid1',
        {'group_valid1': json.dumps({'Name': 'Group1'})},
    ],
)
@pytest.mark.parametrize(
    'permission_filter, expected_permissions', FILTER_PARAMS,
)
async def test_filter(
        taxi_dispatcher_access_control,
        blackbox_service,
        mock_fleet_parks_list,
        mock_fleet_payouts,
        taxi_config,
        permission_filter,
        expected_permissions,
):
    blackbox_service.set_user_ticket_info(
        'ticket_valid1', '100', 'admin@yandex.ru',
    )

    taxi_config.set_values(
        dict(
            FLEET_ACCESS_CONTROL_PERMISSIONS=utils.build_config_permission(
                filters=[permission_filter],
            ),
        ),
    )
    await taxi_dispatcher_access_control.invalidate_caches()
    await _make_request(
        taxi_dispatcher_access_control,
        expected_permissions=expected_permissions,
    )


@pytest.mark.redis_store(
    [
        'hmset',
        'User:Items:park_valid1',
        {
            'user_valid1': json.dumps(
                {
                    'Enable': True,
                    'Group': 'group_valid1',
                    'Name': 'Admin',
                    'Email': 'admin@yandex.ru',
                    'Phones': '',
                    'YandexConfirmed': True,
                    'IsSuperUser': False,
                    'YandexLogin': 'admin',
                    'YandexUid': '100',
                },
            ),
        },
    ],
    [
        'hmset',
        'UserGroup:Items:park_valid1',
        {'group_valid1': json.dumps({'Name': 'Group1'})},
    ],
)
@pytest.mark.parametrize(
    'park_fleet_version, filter_fleet_version, expected_permissions',
    (
        ['simple', 'simple', [utils.PERMISSION_ID]],
        ['basic', 'basic', [utils.PERMISSION_ID]],
        ['simple', 'basic', []],
        ['basic', 'simple', []],
    ),
)
async def test_fleet_version_cache(
        taxi_dispatcher_access_control,
        blackbox_service,
        mock_fleet_parks_list,
        mock_fleet_payouts,
        taxi_config,
        park_fleet_version,
        filter_fleet_version,
        expected_permissions,
):
    blackbox_service.set_user_ticket_info(
        'ticket_valid1', '100', 'admin@yandex.ru',
    )
    mock_fleet_payouts.set_data(fleet_version=park_fleet_version)

    taxi_config.set_values(
        dict(
            FLEET_ACCESS_CONTROL_PERMISSIONS=utils.build_config_permission(
                filters=[build_filter(fleet_version=filter_fleet_version)],
            ),
        ),
    )
    await taxi_dispatcher_access_control.invalidate_caches()
    await _make_request(
        taxi_dispatcher_access_control,
        expected_permissions=expected_permissions,
    )
    assert mock_fleet_payouts.call_mock_fleet_payouts_calls == 1

    await _make_request(
        taxi_dispatcher_access_control,
        expected_permissions=expected_permissions,
    )
    assert mock_fleet_payouts.call_mock_fleet_payouts_calls == 1


YANDEX_TEAM_FILTER_PARAMS = [
    (build_filter(role='Basic'), [utils.PERMISSION_ID]),
    (build_filter(role='Admin'), []),
    (build_filter(provider='yandex_team'), [utils.PERMISSION_ID]),
    (build_filter(provider='yandex'), []),
    (build_filter(provider='yandex_team', fleet_version='simple'), []),
    (
        build_filter(provider='yandex_team', fleet_version='basic'),
        [utils.PERMISSION_ID],
    ),
]


@pytest.mark.redis_store(['sadd', 'admin:rolemembers:Basic', 'user'])
@pytest.mark.parametrize(
    'permission_filter, expected_permissions', YANDEX_TEAM_FILTER_PARAMS,
)
async def test_yandex_team_filter(
        taxi_dispatcher_access_control,
        mock_fleet_parks_list,
        mock_fleet_payouts,
        blackbox_service,
        taxi_config,
        permission_filter,
        expected_permissions,
):
    blackbox_service.set_user_ticket_info('ticket_valid1', '100', 'user')

    taxi_config.set_values(
        dict(
            FLEET_ACCESS_CONTROL_PERMISSIONS=utils.build_config_permission(
                filters=[permission_filter],
            ),
        ),
    )
    await taxi_dispatcher_access_control.invalidate_caches()
    await _make_request(
        taxi_dispatcher_access_control,
        headers_params={'user_ticket_provider': 'yandex_team'},
        expected_permissions=expected_permissions,
    )


@pytest.mark.redis_store(
    [
        'hmset',
        'User:Items:park_valid1',
        {
            'user_valid1': json.dumps(
                {
                    'Enable': True,
                    'Group': 'group_valid1',
                    'Name': 'Admin',
                    'Email': 'admin@yandex.ru',
                    'Phones': '',
                    'YandexConfirmed': True,
                    'IsSuperUser': False,
                    'YandexLogin': 'admin',
                    'YandexUid': '100',
                },
            ),
        },
    ],
)
async def test_many_filters(
        taxi_dispatcher_access_control,
        blackbox_service,
        mock_fleet_parks_list,
        mock_fleet_payouts,
        taxi_config,
):
    blackbox_service.set_user_ticket_info(
        'ticket_valid1', '100', 'admin@yandex.ru',
    )

    taxi_config.set_values(
        dict(
            FLEET_ACCESS_CONTROL_PERMISSIONS=utils.build_config_permission(
                filters=[
                    build_filter(countries_exclude=['cid1']),
                    build_filter(cities=['city1']),
                ],
            ),
        ),
    )
    await taxi_dispatcher_access_control.invalidate_caches()

    response = await taxi_dispatcher_access_control.get(
        ENDPOINT, params={'park_id': PARK_ID}, headers=build_headers(),
    )

    assert response.status_code == 200, response.text
    assert response.json() == {'permissions': [utils.PERMISSION_ID]}
    await _make_request(
        taxi_dispatcher_access_control,
        expected_permissions=[utils.PERMISSION_ID],
    )


GRANTS_PARAMS = [
    ('_grant_driver_read_common', ['_grant_driver_read_common']),
    ('_grant_driver_write_common', []),
]


@pytest.mark.redis_store(
    [
        'hmset',
        'User:Items:park_valid1',
        {
            'user_valid1': json.dumps(
                {
                    'Enable': True,
                    'Group': 'group_valid1',
                    'Name': 'Admin',
                    'Email': 'admin@yandex.ru',
                    'Phones': '',
                    'YandexConfirmed': True,
                    'IsSuperUser': False,
                    'YandexLogin': 'admin',
                    'YandexUid': '100',
                },
            ),
        },
    ],
    [
        'hmset',
        'UserGroup:Items:park_valid1',
        {'group_valid1': json.dumps({'Name': 'Group1'})},
    ],
    [
        'hmset',
        'Grants:park_valid1:group_valid1',
        {'driver_read_common': str(True), 'driver_write_common': str(False)},
    ],
)
@pytest.mark.parametrize('permission_id, expected_permissions', GRANTS_PARAMS)
async def test_grants(
        taxi_dispatcher_access_control,
        blackbox_service,
        mock_fleet_parks_list,
        mock_fleet_payouts,
        taxi_config,
        permission_id,
        expected_permissions,
):
    blackbox_service.set_user_ticket_info('ticket_valid1', '100', 'user')

    taxi_config.set_values(
        dict(
            FLEET_ACCESS_CONTROL_PERMISSIONS=utils.build_config_permission(
                permission_id=permission_id,
            ),
        ),
    )
    await taxi_dispatcher_access_control.invalidate_caches()
    await _make_request(
        taxi_dispatcher_access_control,
        expected_permissions=expected_permissions,
    )


async def test_park_not_found(
        taxi_dispatcher_access_control,
        mock_fleet_parks_list,
        mock_fleet_payouts,
        taxi_config,
):
    response = await taxi_dispatcher_access_control.get(
        ENDPOINT, params={'park_id': 'invalid'}, headers=build_headers(),
    )

    assert response.status_code == 404, response.text
    assert response.json() == {
        'code': 'park_not_found',
        'message': 'Park not found',
    }


@pytest.mark.redis_store(
    [
        'hmset',
        'User:Items:park_valid1',
        {
            'user_valid1': json.dumps(
                {
                    'Enable': False,
                    'Group': 'group_valid1',
                    'Name': 'Admin',
                    'Email': 'admin@yandex.ru',
                    'Phones': '',
                    'YandexConfirmed': True,
                    'IsSuperUser': False,
                    'YandexLogin': 'admin',
                    'YandexUid': '100',
                },
            ),
        },
    ],
)
async def test_user_not_found(
        taxi_dispatcher_access_control,
        blackbox_service,
        mock_fleet_parks_list,
        mock_fleet_payouts,
        taxi_config,
):
    blackbox_service.set_user_ticket_info(
        'ticket_valid1', '100', 'admin@yandex.ru',
    )

    response = await taxi_dispatcher_access_control.get(
        ENDPOINT, params={'park_id': PARK_ID}, headers=build_headers(),
    )

    assert response.status_code == 403, response.text
    assert response.json() == {
        'code': 'user_not_found',
        'message': 'No such active user in park',
    }


async def test_invalid_ticket(
        taxi_dispatcher_access_control,
        mock_fleet_parks_list,
        mock_fleet_payouts,
        blackbox_service,
        taxi_config,
):
    response = await taxi_dispatcher_access_control.get(
        ENDPOINT,
        params={'park_id': PARK_ID},
        headers=build_headers(user_ticket_provider='yandex_team'),
    )

    assert response.status_code == 403, response.text
    assert response.json() == {
        'code': 'invalid_user_ticket',
        'message': 'Invalid user ticket',
    }
