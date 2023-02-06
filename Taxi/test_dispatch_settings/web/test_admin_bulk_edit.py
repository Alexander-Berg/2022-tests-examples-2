import typing as tp

import pytest

ALL_LOCATION_QUERY: tp.Any = {
    'tariffs': {'blacklist': []},
    'zones': {'blacklist': []},
}


@pytest.mark.config(
    ALL_CATEGORIES=[
        'test_tariff_1',
        'test_tariff_2',
        'test_tariff_3',
        'test_tariff_4',
    ],
)
async def test_bulk_edit_sequential_actions(
        taxi_dispatch_settings_web, mockserver,
):
    @mockserver.json_handler('/individual-tariffs/internal/v1/tariffs/summary')
    def _individual_tariffs_mock(request):
        return {
            'tariffs': [
                {
                    'id': '1',
                    'home_zone': 'test_zone_1',
                    'activation_zone': 'test',
                    'related_zones': [],
                    'categories': [],
                    'city_id': 'Moscow',
                    'country': 'rus',
                    'timezone': 'Europe/Moscow',
                },
                {
                    'id': '2',
                    'home_zone': 'test_zone_2',
                    'activation_zone': 'test',
                    'related_zones': [],
                    'categories': [],
                    'city_id': 'Moscow',
                    'country': 'rus',
                    'timezone': 'Europe/Moscow',
                },
                {
                    'id': '3',
                    'home_zone': 'test_zone_3',
                    'activation_zone': 'test',
                    'related_zones': [],
                    'categories': [],
                    'city_id': 'Moscow',
                    'country': 'rus',
                    'timezone': 'Europe/Moscow',
                },
                {
                    'id': '4',
                    'home_zone': 'test_zone_4',
                    'activation_zone': 'test',
                    'related_zones': [],
                    'categories': [],
                    'city_id': 'Moscow',
                    'country': 'rus',
                    'timezone': 'Europe/Moscow',
                },
            ],
        }

    response = await taxi_dispatch_settings_web.post(
        '/v1/admin/bulk/edit',
        json={
            'location_query': {
                'tariffs': {'whitelist': ['test_tariff_1']},
                'zones': {'whitelist': ['test_zone_1']},
            },
            'actions': [
                {
                    'parameter': 'INTEGER_POSITIVE_FIELD',
                    'action': 'set',
                    'action_data': {'value': 55},
                },
                {
                    'parameter': 'DICT_FIELD',
                    'action': 'add_kv',
                    'action_data': {
                        'key': 'key_value',
                        'value': 66,
                        'not_exist_ok': True,
                    },
                },
                {
                    'parameter': 'DICT_FIELD',
                    'action': 'remove_kvs',
                    'action_data': {'keys': ['key_value']},
                },
                {
                    'parameter': 'LIST_FIELD',
                    'action': 'add_items',
                    'action_data': {'values': ['a_new']},
                },
                {
                    'parameter': 'LIST_FIELD',
                    'action': 'add_items',
                    'action_data': {'values': ['b_new']},
                },
                {
                    'parameter': 'LIST_FIELD',
                    'action': 'remove_items',
                    'action_data': {'values': ['b_new']},
                },
                {
                    'parameter': 'REMOVABLE_FIELD',
                    'action': 'remove',
                    'action_data': {},
                },
            ],
        },
    )
    assert response.status == 200

    response = await taxi_dispatch_settings_web.get(
        '/v2/admin/fetch',
        params={'zone_name': 'test_zone_1', 'tariff_name': 'test_tariff_1'},
    )
    assert response.status == 200
    content = await response.json()
    content['settings'].sort(key=lambda x: x['name'])
    assert content == {
        'are_default_settings': False,
        'settings': [
            {
                'name': 'DICT_FIELD',
                'value': {'key1': 44, '__default__': 33},
                'version': 1,
            },
            {'name': 'INTEGER_POSITIVE_FIELD', 'value': 55, 'version': 1},
            {
                'name': 'LIST_FIELD',
                'value': ['a1', 'a2', 'a3', 'a_new'],
                'version': 1,
            },
            {'name': 'REMOVABLE_FIELD', 'version': 1},
        ],
    }


@pytest.mark.parametrize(
    'location_query,'
    'action,'
    'parameter_name,'
    'action_data,'
    'group_name,'
    'expected_status',
    [
        (
            # Wrong request forming
            {'tariffs': {'blacklist': [], 'whitelist': []}},
            'set',
            'INTEGER_POSITIVE_FIELD',
            {'value': 0xDEAD},
            None,
            400,
        ),
        (
            # Wrong request forming
            {'tariffs': {}},
            'set',
            'INTEGER_POSITIVE_FIELD',
            {'value': 0xDEAD},
            None,
            400,
        ),
        (  # Wrong action data type
            ALL_LOCATION_QUERY,
            'set',
            'INTEGER_POSITIVE_FIELD',
            0xDEAD,
            None,
            400,
        ),
        (  # Value validation at apply stage
            {
                'tariffs': {'whitelist': ['test_tariff_1']},
                'zones': {'whitelist': ['test_zone_3']},
            },
            'set',
            'INTEGER_POSITIVE_FIELD',
            {'value': 'some_str'},
            None,
            400,
        ),
        (  # Wrong action data internal format
            ALL_LOCATION_QUERY,
            'set',
            'INTEGER_POSITIVE_FIELD',
            {'volue': 0xDEAD},
            None,
            400,
        ),
        (
            # Not allowed, tariffs in different groups (existing groups)
            {
                'tariffs': {'whitelist': ['test_tariff_1', 'test_tariff_2']},
                'zones': {'whitelist': ['test_zone_3']},
            },
            'set',
            'INTEGER_POSITIVE_FIELD',
            {'value': 0xDEAD},
            'group1',
            403,
        ),
        (
            # Not allowed, tariffs in different groups (non existing groups)
            {
                'tariffs': {'whitelist': ['test_tariff_1', 'test_tariff_4']},
                'zones': {'whitelist': ['test_zone_3']},
            },
            'set',
            'INTEGER_POSITIVE_FIELD',
            {'value': 0xDEAD},
            'non_existent_group',
            403,
        ),
        (
            # tariff without group (group_name passed)
            {
                'tariffs': {'whitelist': ['test_tariff_1', 'test_tariff_3']},
                'zones': {'whitelist': ['test_zone_3']},
            },
            'set',
            'INTEGER_POSITIVE_FIELD',
            {'value': 0xDEAD},
            'group1',
            404,
        ),
        (
            # tariff without group (superuser)
            ALL_LOCATION_QUERY,
            'set',
            'INTEGER_POSITIVE_FIELD',
            {'value': 0xDEAD},
            None,
            404,
        ),
    ],
)
@pytest.mark.config(
    ALL_CATEGORIES=[
        'test_tariff_1',
        'test_tariff_2',
        'test_tariff_3',
        'test_tariff_4',
    ],
)
async def test_bulk_edit_errors(
        taxi_dispatch_settings_web,
        location_query,
        parameter_name,
        action,
        action_data,
        group_name,
        expected_status,
        mockserver,
):
    @mockserver.json_handler('/individual-tariffs/internal/v1/tariffs/summary')
    def _individual_tariffs_mock(request):
        return {
            'tariffs': [
                {
                    'id': '1',
                    'home_zone': 'test_zone_1',
                    'activation_zone': 'test',
                    'related_zones': [],
                    'categories': [],
                    'city_id': 'Moscow',
                    'country': 'rus',
                    'timezone': 'Europe/Moscow',
                },
                {
                    'id': '2',
                    'home_zone': 'test_zone_2',
                    'activation_zone': 'test',
                    'related_zones': [],
                    'categories': [],
                    'city_id': 'Moscow',
                    'country': 'rus',
                    'timezone': 'Europe/Moscow',
                },
                {
                    'id': '3',
                    'home_zone': 'test_zone_3',
                    'activation_zone': 'test',
                    'related_zones': [],
                    'categories': [],
                    'city_id': 'Moscow',
                    'country': 'rus',
                    'timezone': 'Europe/Moscow',
                },
                {
                    'id': '4',
                    'home_zone': 'test_zone_4',
                    'activation_zone': 'test',
                    'related_zones': [],
                    'categories': [],
                    'city_id': 'Moscow',
                    'country': 'rus',
                    'timezone': 'Europe/Moscow',
                },
            ],
        }

    request = {
        'location_query': location_query,
        'actions': [
            {
                'parameter': parameter_name,
                'action': action,
                'action_data': action_data,
            },
        ],
    }
    if group_name is not None:
        request['group_name'] = group_name

    response = await taxi_dispatch_settings_web.post(
        '/v1/admin/bulk/edit', json=request,
    )

    assert response.status == expected_status


@pytest.mark.parametrize(
    'action,' 'parameter_name,' 'action_data,' 'expected_value',
    [
        ('set', 'INTEGER_POSITIVE_FIELD', {'value': 0xDEAD}, 0xDEAD),
        (
            'add_kv',
            'DICT_FIELD',
            {'key': 'new_key', 'value': 0xBEEF},
            {'__default__': 33, 'key1': 44, 'new_key': 0xBEEF},
        ),
        (
            'edit_kv',
            'DICT_FIELD',
            {'key': '__default__', 'value': 0xEFBE},
            {'__default__': 0xEFBE, 'key1': 44},
        ),
        (
            'add_items',
            'LIST_FIELD',
            {'values': ['new_item']},
            ['a1', 'a2', 'a3', 'new_item'],
        ),
        ('remove_items', 'LIST_FIELD', {'values': ['a2']}, ['a1', 'a3']),
        ('remove', 'INTEGER_POSITIVE_FIELD', {}, None),
        (
            'update_dict',
            'DICT_FIELD',
            {'value': {'__default__': 22, 'new_key': 99}},
            {'__default__': 22, 'key1': 44, 'new_key': 99},
        ),
        ('remove_kvs', 'DICT_FIELD', {'keys': ['key1']}, {'__default__': 33}),
    ],
)
@pytest.mark.config(
    ALL_CATEGORIES=[
        'test_tariff_1',
        'test_tariff_2',
        'test_tariff_3',
        'test_tariff_4',
    ],
)
async def test_bulk_edit_actions(
        taxi_dispatch_settings_web,
        action,
        action_data,
        parameter_name,
        expected_value,
        mockserver,
):
    @mockserver.json_handler('/individual-tariffs/internal/v1/tariffs/summary')
    def _individual_tariffs_mock(request):
        return {
            'tariffs': [
                {
                    'id': '1',
                    'home_zone': 'test_zone_1',
                    'activation_zone': 'test',
                    'related_zones': [],
                    'categories': [],
                    'city_id': 'Moscow',
                    'country': 'rus',
                    'timezone': 'Europe/Moscow',
                },
                {
                    'id': '2',
                    'home_zone': 'test_zone_2',
                    'activation_zone': 'test',
                    'related_zones': [],
                    'categories': [],
                    'city_id': 'Moscow',
                    'country': 'rus',
                    'timezone': 'Europe/Moscow',
                },
                {
                    'id': '3',
                    'home_zone': 'test_zone_3',
                    'activation_zone': 'test',
                    'related_zones': [],
                    'categories': [],
                    'city_id': 'Moscow',
                    'country': 'rus',
                    'timezone': 'Europe/Moscow',
                },
                {
                    'id': '4',
                    'home_zone': 'test_zone_4',
                    'activation_zone': 'test',
                    'related_zones': [],
                    'categories': [],
                    'city_id': 'Moscow',
                    'country': 'rus',
                    'timezone': 'Europe/Moscow',
                },
            ],
        }

    response = await taxi_dispatch_settings_web.post(
        '/v1/admin/bulk/edit',
        json={
            'location_query': {
                'tariffs': {'whitelist': ['test_tariff_1']},
                'zones': {'whitelist': ['test_zone_1']},
            },
            'actions': [
                {
                    'parameter': parameter_name,
                    'action': action,
                    'action_data': action_data,
                },
            ],
        },
    )
    assert response.status == 200

    response = await taxi_dispatch_settings_web.get(
        '/v2/admin/fetch',
        params={'zone_name': 'test_zone_1', 'tariff_name': 'test_tariff_1'},
    )
    assert response.status == 200
    content = await response.json()

    found = False
    for param in content['settings']:
        if param['name'] == parameter_name:
            found = True
            assert param.get('value', None) == expected_value

    if not found:
        assert False, 'Can\'t find desired setting'


@pytest.mark.config(
    ALL_CATEGORIES=[
        'test_tariff_1',
        'test_tariff_2',
        'test_tariff_3',
        'test_tariff_4',
    ],
)
async def test_bulk_edit_add_parameter(
        taxi_dispatch_settings_web, mockserver, taxi_config,
):
    @mockserver.json_handler('/individual-tariffs/internal/v1/tariffs/summary')
    def _individual_tariffs_mock(request):
        return {
            'tariffs': [
                {
                    'id': '1',
                    'home_zone': 'test_zone_1',
                    'activation_zone': 'test',
                    'related_zones': [],
                    'categories': [],
                    'city_id': 'Moscow',
                    'country': 'rus',
                    'timezone': 'Europe/Moscow',
                },
                {
                    'id': '2',
                    'home_zone': 'test_zone_2',
                    'activation_zone': 'test',
                    'related_zones': [],
                    'categories': [],
                    'city_id': 'Moscow',
                    'country': 'rus',
                    'timezone': 'Europe/Moscow',
                },
                {
                    'id': '3',
                    'home_zone': 'test_zone_3',
                    'activation_zone': 'test',
                    'related_zones': [],
                    'categories': [],
                    'city_id': 'Moscow',
                    'country': 'rus',
                    'timezone': 'Europe/Moscow',
                },
                {
                    'id': '4',
                    'home_zone': 'test_zone_4',
                    'activation_zone': 'test',
                    'related_zones': [],
                    'categories': [],
                    'city_id': 'Moscow',
                    'country': 'rus',
                    'timezone': 'Europe/Moscow',
                },
            ],
        }

    response = await taxi_dispatch_settings_web.post(
        '/v1/admin/bulk/edit',
        json={
            'location_query': {
                'tariffs': {'whitelist': ['test_tariff_1']},
                'zones': {'whitelist': ['test_zone_1']},
            },
            'actions': [
                {
                    'parameter': 'NEW_INTEGER_FIELD',
                    'action': 'set',
                    'action_data': {'value': 4},
                },
            ],
        },
    )
    assert response.status == 200

    response = await taxi_dispatch_settings_web.get(
        '/v2/admin/fetch',
        params={'zone_name': 'test_zone_1', 'tariff_name': 'test_tariff_1'},
    )
    assert response.status == 200
    content = await response.json()
    content['settings'].sort(key=lambda x: x['name'])
    assert content == {
        'are_default_settings': False,
        'settings': [
            {
                'name': 'DICT_FIELD',
                'value': {'key1': 44, '__default__': 33},
                'version': 0,
            },
            {'name': 'INTEGER_POSITIVE_FIELD', 'value': 22, 'version': 0},
            {'name': 'LIST_FIELD', 'value': ['a1', 'a2', 'a3'], 'version': 0},
            {'name': 'NEW_INTEGER_FIELD', 'value': 4, 'version': 0},
            {'name': 'REMOVABLE_FIELD', 'value': 44, 'version': 0},
        ],
    }

    taxi_config.set_values({'DISPATCH_SETTINGS_MAINTENANCE_MODE': True})
    await taxi_dispatch_settings_web.invalidate_caches()
    response = await taxi_dispatch_settings_web.post(
        '/v1/admin/bulk/edit',
        json={
            'location_query': {
                'tariffs': {'whitelist': ['test_tariff_1']},
                'zones': {'whitelist': ['test_zone_1']},
            },
            'actions': [
                {
                    'parameter': 'NEW_INTEGER_FIELD',
                    'action': 'set',
                    'action_data': {'value': 4},
                },
            ],
        },
    )
    assert response.status == 400
    r_json = await response.json()
    assert r_json['code'] == 'maintenance_mode'


@pytest.mark.config(
    ALL_CATEGORIES=[
        'test_tariff_1',
        'test_tariff_2',
        'test_tariff_3',
        'test_tariff_4',
        'test_tariff_5',
        'test_tariff_6',
    ],
    DISPATCH_SETTINGS_BULK_EDIT_PROTECTION_ENABLED=False,
)
async def test_bulk_edit_default_on_non_existing(
        taxi_dispatch_settings_web, mockserver, pgsql,
):
    pg_cursor = pgsql['dispatch_settings'].cursor()
    statement = (
        """UPDATE dispatch_settings.tariffs SET group_id = ("""
        """SELECT id FROM dispatch_settings.groups WHERE name = 'group1')"""
        """WHERE tariff_name = 'test_tariff_6'"""
    )
    pg_cursor.execute(statement)

    @mockserver.json_handler('/individual-tariffs/internal/v1/tariffs/summary')
    def _individual_tariffs_mock(request):
        return {
            'tariffs': [
                {
                    'id': '1',
                    'home_zone': 'test_zone_1',
                    'activation_zone': 'test',
                    'related_zones': [],
                    'categories': [],
                    'city_id': 'Moscow',
                    'country': 'rus',
                    'timezone': 'Europe/Moscow',
                },
                {
                    'id': '2',
                    'home_zone': 'test_zone_2',
                    'activation_zone': 'test',
                    'related_zones': [],
                    'categories': [],
                    'city_id': 'Moscow',
                    'country': 'rus',
                    'timezone': 'Europe/Moscow',
                },
                {
                    'id': '3',
                    'home_zone': 'test_zone_3',
                    'activation_zone': 'test',
                    'related_zones': [],
                    'categories': [],
                    'city_id': 'Moscow',
                    'country': 'rus',
                    'timezone': 'Europe/Moscow',
                },
                {
                    'id': '4',
                    'home_zone': 'test_zone_4',
                    'activation_zone': 'test',
                    'related_zones': [],
                    'categories': [],
                    'city_id': 'Moscow',
                    'country': 'rus',
                    'timezone': 'Europe/Moscow',
                },
            ],
        }

    response = await taxi_dispatch_settings_web.post(
        '/v1/admin/bulk/edit',
        json={
            'location_query': {
                'tariffs': {'whitelist': ['test_tariff_6']},
                'zones': {'whitelist': ['test_zone_3']},
            },
            'actions': [
                {
                    'parameter': 'LIST_FIELD',
                    'action': 'set',
                    'action_data': {'value': ['test_value']},
                },
            ],
        },
    )

    assert response.status == 200

    response = await taxi_dispatch_settings_web.get(
        '/v2/admin/fetch',
        params={'zone_name': 'test_zone_3', 'tariff_name': 'test_tariff_6'},
    )
    assert response.status == 200
    content = await response.json()
    content['settings'].sort(key=lambda x: x['name'])
    assert content == {
        'are_default_settings': False,
        'settings': [
            {'name': 'INTEGER_POSITIVE_FIELD', 'value': 222, 'version': 0},
            {'name': 'LIST_FIELD', 'value': ['test_value'], 'version': 0},
        ],
    }


@pytest.mark.config(
    ALL_CATEGORIES=[
        'test_tariff_1',
        'test_tariff_2',
        'test_tariff_3',
        'test_tariff_4',
        'test_tariff_5',
    ],
)
async def test_bulk_edit_blacklist_without_group(
        taxi_dispatch_settings_web, mockserver, pgsql,
):
    pg_cursor = pgsql['dispatch_settings'].cursor()
    statement = (
        """UPDATE dispatch_settings.tariffs SET group_id = ("""
        """SELECT id FROM dispatch_settings.groups WHERE name = 'group1')"""
        """WHERE tariff_name = 'test_tariff_3'"""
    )
    pg_cursor.execute(statement)

    @mockserver.json_handler('/individual-tariffs/internal/v1/tariffs/summary')
    def _individual_tariffs_mock(request):
        return {
            'tariffs': [
                {
                    'id': '1',
                    'home_zone': 'test_zone_1',
                    'activation_zone': 'test',
                    'related_zones': [],
                    'categories': [],
                    'city_id': 'Moscow',
                    'country': 'rus',
                    'timezone': 'Europe/Moscow',
                },
                {
                    'id': '2',
                    'home_zone': 'test_zone_2',
                    'activation_zone': 'test',
                    'related_zones': [],
                    'categories': [],
                    'city_id': 'Moscow',
                    'country': 'rus',
                    'timezone': 'Europe/Moscow',
                },
                {
                    'id': '3',
                    'home_zone': 'test_zone_3',
                    'activation_zone': 'test',
                    'related_zones': [],
                    'categories': [],
                    'city_id': 'Moscow',
                    'country': 'rus',
                    'timezone': 'Europe/Moscow',
                },
                {
                    'id': '4',
                    'home_zone': 'test_zone_4',
                    'activation_zone': 'test',
                    'related_zones': [],
                    'categories': [],
                    'city_id': 'Moscow',
                    'country': 'rus',
                    'timezone': 'Europe/Moscow',
                },
            ],
        }

    location_query = {
        'zones': {'whitelist': ['test_zone_3']},
        'tariffs': {'blacklist': ['test_tariff_5']},
    }

    request = {
        'location_query': location_query,
        'actions': [
            {
                'parameter': 'INTEGER_POSITIVE_FIELD',
                'action': 'set',
                'action_data': {'value': 1001},
            },
        ],
    }
    response = await taxi_dispatch_settings_web.post(
        '/v1/admin/bulk/edit', json=request,
    )
    assert response.status == 200

    etalon = {
        '__default__group1__': {'value': 1001, 'version': 1},
        'test_tariff_1': {'value': 1001, 'version': 1},
        'test_tariff_2': {'value': 1001, 'version': 1},
        'test_tariff_3': {'value': 1001, 'version': 1},
        'test_tariff_4': {'value': 1001, 'version': 1},
        'test_tariff_5': {'value': 5, 'version': 0},
    }
    for tariff_name, compare in etalon.items():
        response = await taxi_dispatch_settings_web.get(
            '/v2/admin/fetch',
            params={'zone_name': 'test_zone_3', 'tariff_name': tariff_name},
        )
        assert response.status == 200
        content = await response.json()
        assert content['settings'] == [
            {
                'name': 'INTEGER_POSITIVE_FIELD',
                'value': compare['value'],
                'version': compare['version'],
            },
        ]


@pytest.mark.config(
    ALL_CATEGORIES=[
        'test_tariff_1',
        'test_tariff_2',
        'test_tariff_3',
        'test_tariff_4',
        'test_tariff_5',
    ],
)
@pytest.mark.parametrize(
    'location_part,etalon',
    [
        (
            {'whitelist': ['test_tariff_5']},
            {
                '__default__group1__': {'value': 222, 'version': 0},
                'test_tariff_1': {'value': 1, 'version': 0},
                'test_tariff_2': {'value': 2, 'version': 0},
                'test_tariff_3': {'value': 3, 'version': 0},
                'test_tariff_4': {'value': 4, 'version': 0},
                'test_tariff_5': {'value': 1001, 'version': 1},
            },
        ),
        (
            {'blacklist': ['test_tariff_5']},
            {
                '__default__group1__': {'value': 1001, 'version': 1},
                'test_tariff_1': {'value': 1001, 'version': 1},
                'test_tariff_2': {'value': 2, 'version': 0},
                'test_tariff_3': {'value': 3, 'version': 0},
                'test_tariff_4': {'value': 1001, 'version': 1},
                'test_tariff_5': {'value': 5, 'version': 0},
            },
        ),
        (
            {'blacklist': []},
            {
                '__default__group1__': {'value': 1001, 'version': 1},
                'test_tariff_1': {'value': 1001, 'version': 1},
                'test_tariff_2': {'value': 2, 'version': 0},
                'test_tariff_3': {'value': 3, 'version': 0},
                'test_tariff_4': {'value': 1001, 'version': 1},
                'test_tariff_5': {'value': 1001, 'version': 1},
            },
        ),
        # empty whitelist doesn't have sence
    ],
)
async def test_bulk_edit_inside_group(
        taxi_dispatch_settings_web, location_part, etalon, mockserver,
):
    @mockserver.json_handler('/individual-tariffs/internal/v1/tariffs/summary')
    def _individual_tariffs_mock(request):
        return {
            'tariffs': [
                {
                    'id': '1',
                    'home_zone': 'test_zone_1',
                    'activation_zone': 'test',
                    'related_zones': [],
                    'categories': [],
                    'city_id': 'Moscow',
                    'country': 'rus',
                    'timezone': 'Europe/Moscow',
                },
                {
                    'id': '2',
                    'home_zone': 'test_zone_2',
                    'activation_zone': 'test',
                    'related_zones': [],
                    'categories': [],
                    'city_id': 'Moscow',
                    'country': 'rus',
                    'timezone': 'Europe/Moscow',
                },
                {
                    'id': '3',
                    'home_zone': 'test_zone_3',
                    'activation_zone': 'test',
                    'related_zones': [],
                    'categories': [],
                    'city_id': 'Moscow',
                    'country': 'rus',
                    'timezone': 'Europe/Moscow',
                },
                {
                    'id': '4',
                    'home_zone': 'test_zone_4',
                    'activation_zone': 'test',
                    'related_zones': [],
                    'categories': [],
                    'city_id': 'Moscow',
                    'country': 'rus',
                    'timezone': 'Europe/Moscow',
                },
            ],
        }

    location_query = {
        'zones': {'whitelist': ['test_zone_3']},
        'tariffs': location_part,
    }
    request = {
        'location_query': location_query,
        'actions': [
            {
                'parameter': 'INTEGER_POSITIVE_FIELD',
                'action': 'set',
                'action_data': {'value': 1001},
            },
        ],
        'group_name': 'group1',
    }
    response = await taxi_dispatch_settings_web.post(
        '/v1/admin/bulk/edit', json=request,
    )
    assert response.status == 200

    for tariff_name, compare in etalon.items():
        response = await taxi_dispatch_settings_web.get(
            '/v2/admin/fetch',
            params={'zone_name': 'test_zone_3', 'tariff_name': tariff_name},
        )
        assert response.status == 200
        content = await response.json()
        assert content['settings'] == [
            {
                'name': 'INTEGER_POSITIVE_FIELD',
                'value': compare['value'],
                'version': compare['version'],
            },
        ]
