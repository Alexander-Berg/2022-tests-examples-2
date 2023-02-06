import pytest

import test_dispatch_settings.web.mock_utils as mock_utils


@pytest.mark.config(
    ALL_CATEGORIES=['test_tariff_1'],
    DISPATCH_SETTINGS_BULK_EDIT_PROTECTION_ENABLED=False,
)
async def test_bulk_edit_defaults_1(
        taxi_dispatch_settings_web, tariffs, pgsql,
):
    tariffs.set_zones(['test_zone_1'])

    mock_utils.mock_parameters(
        pgsql=pgsql,
        zone_names={
            '__default__',
            'test_zone_1',
            'test_zone_2',
            'test_zone_3',
            'test_zone_4',
        },
        groups={'group1', 'group2'},
        tariffs=[
            mock_utils.Tariff('__default__group1__', 'group1'),
            mock_utils.Tariff('test_tariff_1', 'group1'),
            mock_utils.Tariff('test_tariff_2'),
            mock_utils.Tariff('test_tariff_3'),
            mock_utils.Tariff('test_tariff_4'),
        ],
        parameters=[
            mock_utils.ParameterDefinition(
                name='INTEGER_FIELD',
                schema={'type': 'integer', 'minimum': 0},
                actions={'set'},
            ),
            mock_utils.ParameterDefinition(
                name='STRING_FIELD',
                schema={'type': 'string'},
                actions={'set'},
            ),
        ],
        settings={
            '__default__': {
                '__default__group1__': [
                    mock_utils.Parameter('INTEGER_FIELD', 10),
                ],
                'test_tariff_1': [mock_utils.Parameter('INTEGER_FIELD', 2)],
            },
            'test_zone_1': {
                '__default__group1__': [
                    mock_utils.Parameter('INTEGER_FIELD', 11),
                ],
                'test_tariff_1': [
                    mock_utils.Parameter('INTEGER_FIELD', None),
                    mock_utils.Parameter('STRING_FIELD', None),
                ],
            },
        },
    )

    response = await taxi_dispatch_settings_web.post(
        '/v1/admin/bulk/edit',
        json={
            'location_query': {
                'tariffs': {'whitelist': ['test_tariff_1']},
                'zones': {'whitelist': ['test_zone_1']},
            },
            'actions': [
                {
                    'parameter': 'STRING_FIELD',
                    'action': 'set',
                    'action_data': {'value': 'str_val'},
                },
            ],
        },
    )

    assert response.status == 200
    assert (
        (
            await mock_utils.get_settings_for(
                client=taxi_dispatch_settings_web,
                zone_name='test_zone_1',
                tariff_name='test_tariff_1',
            )
        )
        == [
            {'name': 'INTEGER_FIELD', 'value': 11, 'version': 1},
            {'name': 'STRING_FIELD', 'value': 'str_val', 'version': 1},
        ]
    )


@pytest.mark.config(
    ALL_CATEGORIES=['test_tariff_1'],
    DISPATCH_SETTINGS_BULK_EDIT_PROTECTION_ENABLED=False,
)
async def test_bulk_edit_defaults_2(
        taxi_dispatch_settings_web, tariffs, pgsql,
):
    tariffs.set_zones(['test_zone_1'])

    mock_utils.mock_parameters(
        pgsql=pgsql,
        zone_names={
            '__default__',
            'test_zone_1',
            'test_zone_2',
            'test_zone_3',
            'test_zone_4',
        },
        groups={'group1', 'group2'},
        tariffs=[
            mock_utils.Tariff('__default__group1__', 'group1'),
            mock_utils.Tariff('test_tariff_1', 'group1'),
            mock_utils.Tariff('test_tariff_2'),
            mock_utils.Tariff('test_tariff_3'),
            mock_utils.Tariff('test_tariff_4'),
        ],
        parameters=[
            mock_utils.ParameterDefinition(
                name='INTEGER_FIELD',
                schema={'type': 'integer', 'minimum': 0},
                actions={'set'},
            ),
            mock_utils.ParameterDefinition(
                name='STRING_FIELD',
                schema={'type': 'string'},
                actions={'set'},
            ),
        ],
        settings={
            '__default__': {
                '__default__group1__': [
                    mock_utils.Parameter('INTEGER_FIELD', 10),
                ],
                'test_tariff_1': [mock_utils.Parameter('INTEGER_FIELD', 2)],
            },
            'test_zone_1': {
                '__default__group1__': [
                    mock_utils.Parameter('INTEGER_FIELD', None),
                ],
                'test_tariff_1': [
                    mock_utils.Parameter('INTEGER_FIELD', None),
                    mock_utils.Parameter('STRING_FIELD', None),
                ],
            },
        },
    )

    response = await taxi_dispatch_settings_web.post(
        '/v1/admin/bulk/edit',
        json={
            'location_query': {
                'tariffs': {'whitelist': ['test_tariff_1']},
                'zones': {'whitelist': ['test_zone_1']},
            },
            'actions': [
                {
                    'parameter': 'STRING_FIELD',
                    'action': 'set',
                    'action_data': {'value': 'str_val'},
                },
            ],
        },
    )

    assert response.status == 200
    assert (
        (
            await mock_utils.get_settings_for(
                client=taxi_dispatch_settings_web,
                zone_name='test_zone_1',
                tariff_name='test_tariff_1',
            )
        )
        == [
            {'name': 'INTEGER_FIELD', 'value': 2, 'version': 1},
            {'name': 'STRING_FIELD', 'value': 'str_val', 'version': 1},
        ]
    )


@pytest.mark.config(
    ALL_CATEGORIES=[
        'test_tariff_1',
        'test_tariff_2',
        'test_tariff_3',
        'test_tariff_4',
    ],
    DISPATCH_SETTINGS_BULK_EDIT_PROTECTION_ENABLED=True,
)
async def test_bulk_edit_safity_config(
        taxi_dispatch_settings_web, tariffs, pgsql,
):
    tariffs.set_zones(
        ['test_zone_1', 'test_zone_2', 'test_zone_3', 'test_zone_4'],
    )

    mock_utils.mock_parameters(
        pgsql=pgsql,
        zone_names={
            '__default__',
            'test_zone_1',
            'test_zone_2',
            'test_zone_3',
            'test_zone_4',
        },
        groups={'group1', 'group2'},
        tariffs=[
            mock_utils.Tariff('__default__group1__', 'group1'),
            mock_utils.Tariff('test_tariff_1', 'group1'),
            mock_utils.Tariff('test_tariff_2'),
            mock_utils.Tariff('test_tariff_3'),
            mock_utils.Tariff('test_tariff_4'),
        ],
        parameters=[
            mock_utils.ParameterDefinition(
                name='INTEGER_FIELD',
                schema={'type': 'integer', 'minimum': 0},
                actions={'set'},
            ),
            mock_utils.ParameterDefinition(
                name='STRING_FIELD',
                schema={'type': 'string'},
                actions={'set'},
            ),
        ],
        settings={
            '__default__': {
                'test_tariff_1': [mock_utils.Parameter('INTEGER_FIELD', 2)],
            },
            'test_zone_1': {
                'test_tariff_1': [
                    mock_utils.Parameter('INTEGER_FIELD', None),
                    mock_utils.Parameter('STRING_FIELD', None),
                ],
            },
        },
    )

    response = await taxi_dispatch_settings_web.post(
        '/v1/admin/bulk/edit',
        json={
            'location_query': {
                'tariffs': {'blacklist': []},
                'zones': {'blacklist': []},
            },
            'actions': [
                {
                    'parameter': 'STRING_FIELD',
                    'action': 'set',
                    'action_data': {'value': 'str_val'},
                },
            ],
        },
    )

    assert response.status == 200
    assert (
        await mock_utils.get_categories(client=taxi_dispatch_settings_web)
    ) == [{'zone_name': '__default__', 'tariff_names': ['test_tariff_1']}]
    assert (
        (
            await mock_utils.get_settings_for(
                client=taxi_dispatch_settings_web,
                zone_name='test_zone_1',
                tariff_name='test_tariff_1',
            )
        )
        == [
            {'name': 'INTEGER_FIELD', 'value': 2, 'version': 0},
            {'name': 'STRING_FIELD', 'value': 'str_val', 'version': 0},
        ]
    )
    assert (
        (
            await mock_utils.get_settings_for(
                client=taxi_dispatch_settings_web,
                zone_name='__default__',
                tariff_name='test_tariff_1',
            )
        )
        == [
            {'name': 'INTEGER_FIELD', 'value': 2, 'version': 0},
            {'name': 'STRING_FIELD', 'value': 'str_val', 'version': 0},
        ]
    )


@pytest.mark.config(
    ALL_CATEGORIES=[
        'test_tariff_1',
        'test_tariff_2',
        'test_tariff_3',
        'test_tariff_4',
    ],
    DISPATCH_SETTINGS_BULK_EDIT_PROTECTION_ENABLED=True,
)
async def test_bulk_default_zone_copy(
        taxi_dispatch_settings_web, tariffs, pgsql,
):
    tariffs.set_zones(
        ['test_zone_1', 'test_zone_2', 'test_zone_3', 'test_zone_4'],
    )

    mock_utils.mock_parameters(
        pgsql=pgsql,
        zone_names={
            '__default__',
            'test_zone_1',
            'test_zone_2',
            'test_zone_3',
            'test_zone_4',
        },
        groups={'group1', 'group2', 'group3', 'group4'},
        tariffs=[
            mock_utils.Tariff('__default__group1__', 'group1'),
            mock_utils.Tariff('__default__group2__', 'group2'),
            mock_utils.Tariff('__default__group3__', 'group3'),
            mock_utils.Tariff('__default__group4__', 'group4'),
            mock_utils.Tariff('test_tariff_1', 'group1'),
            mock_utils.Tariff('test_tariff_2', 'group2'),
            mock_utils.Tariff('test_tariff_3', 'group3'),
            mock_utils.Tariff('test_tariff_4'),
        ],
        parameters=[
            mock_utils.ParameterDefinition(
                name='INTEGER_FIELD',
                schema={'type': 'integer', 'minimum': 0},
                actions={'set'},
            ),
            mock_utils.ParameterDefinition(
                name='STRING_FIELD',
                schema={'type': 'string'},
                actions={'set'},
            ),
        ],
        settings={
            '__default__': {
                '__default__group1__': [
                    mock_utils.Parameter('INTEGER_FIELD', 11),
                ],
                '__default__group2__': [
                    mock_utils.Parameter('INTEGER_FIELD', 12),
                ],
                '__default__group3__': [
                    mock_utils.Parameter('INTEGER_FIELD', 13),
                ],
                '__default__group4__': [
                    mock_utils.Parameter('INTEGER_FIELD', 14),
                ],
                'test_tariff_1': [mock_utils.Parameter('INTEGER_FIELD', 1)],
                'test_tariff_2': [mock_utils.Parameter('INTEGER_FIELD', 2)],
                'test_tariff_3': [mock_utils.Parameter('INTEGER_FIELD', 3)],
                'test_tariff_4': [mock_utils.Parameter('INTEGER_FIELD', 4)],
            },
        },
    )

    response = await taxi_dispatch_settings_web.post(
        '/v1/admin/bulk/edit',
        json={
            'location_query': {
                'tariffs': {'whitelist': ['test_tariff_1', 'test_tariff_2']},
                'zones': {'whitelist': ['test_zone_1']},
            },
            'options': {'allow_new_categories': True},
            'actions': [
                {
                    'parameter': 'STRING_FIELD',
                    'action': 'set',
                    'action_data': {'value': 'str_val'},
                },
            ],
        },
    )

    assert response.status == 200
    assert (
        (await mock_utils.get_categories(client=taxi_dispatch_settings_web))
        == [
            {
                'zone_name': '__default__',
                'tariff_names': [
                    '__default__group1__',
                    '__default__group2__',
                    '__default__group3__',
                    '__default__group4__',
                    'test_tariff_1',
                    'test_tariff_2',
                    'test_tariff_3',
                    'test_tariff_4',
                ],
            },
            {
                'zone_name': 'test_zone_1',
                'tariff_names': [
                    '__default__group1__',
                    '__default__group2__',
                    'test_tariff_1',
                    'test_tariff_2',
                ],
            },
        ]
    )

    pg_cursor = pgsql['dispatch_settings'].cursor()
    assert mock_utils.current_settings(pg_cursor) == [
        ('__default__group1__', '__default__', 'INTEGER_FIELD', 0, 11),
        ('__default__group1__', 'test_zone_1', 'INTEGER_FIELD', 0, 11),
        ('__default__group2__', '__default__', 'INTEGER_FIELD', 0, 12),
        ('__default__group2__', 'test_zone_1', 'INTEGER_FIELD', 0, 12),
        ('__default__group3__', '__default__', 'INTEGER_FIELD', 0, 13),
        ('__default__group4__', '__default__', 'INTEGER_FIELD', 0, 14),
        ('test_tariff_1', '__default__', 'INTEGER_FIELD', 0, 1),
        ('test_tariff_1', 'test_zone_1', 'INTEGER_FIELD', 0, 1),
        ('test_tariff_1', 'test_zone_1', 'STRING_FIELD', 0, 'str_val'),
        ('test_tariff_2', '__default__', 'INTEGER_FIELD', 0, 2),
        ('test_tariff_2', 'test_zone_1', 'INTEGER_FIELD', 0, 2),
        ('test_tariff_2', 'test_zone_1', 'STRING_FIELD', 0, 'str_val'),
        ('test_tariff_3', '__default__', 'INTEGER_FIELD', 0, 3),
        ('test_tariff_4', '__default__', 'INTEGER_FIELD', 0, 4),
    ]
