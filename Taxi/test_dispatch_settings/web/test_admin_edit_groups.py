import itertools

import pytest


def current_groups(cursor):
    cursor.execute(
        """
      SELECT groups.name, COALESCE(array_agg(DISTINCT tariff_name)
      FILTER (WHERE tariff_name IS NOT NULL), '{}'), groups.description
      FROM dispatch_settings.groups
      LEFT JOIN dispatch_settings.tariffs
      ON groups.id = tariffs.group_id
      GROUP BY groups.id, groups.name, groups.description;

    """,
    )
    result = cursor.fetchall()
    for row in result:
        row[1].sort()
    return sorted(result)


def current_tariffs(cursor):
    cursor.execute(
        """
      SELECT tariff_name FROM dispatch_settings.tariffs;

    """,
    )
    result = cursor.fetchall()
    return sorted(itertools.chain.from_iterable(result))


@pytest.mark.pgsql(
    'dispatch_settings', files=['admin_edit_groups_negative.sql'],
)
@pytest.mark.config(
    ALL_CATEGORIES=[
        'new_tariff_1',
        'new_tariff_2',
        'new_tariff_3',
        'new_tariff_4',
    ],
)
async def test_admin_edit_group_negative(
        taxi_dispatch_settings_web, pgsql, taxi_config,
):
    pg_cursor = pgsql['dispatch_settings'].cursor()
    assert current_groups(pg_cursor) == [
        ('group1', [], 'description_1'),
        (
            'group2',
            ['__default__group2__', 'new_tariff_1', 'new_tariff_2'],
            'description_2',
        ),
        (
            'group3',
            ['__default__group3__', 'new_tariff_3', 'new_tariff_4'],
            'description_3',
        ),
    ]

    for tariff_names in ([], ['test_tariff_1']):
        resp = await taxi_dispatch_settings_web.post(
            '/v1/admin/edit_groups',
            json={
                'groups': [
                    {
                        'group_name': 'unknown',
                        'description': 'description',
                        'tariff_names': tariff_names,
                    },
                ],
            },
        )
        assert resp.status == 400
        r_json = await resp.json()
        assert r_json['code'] == 'default_missing'

    resp = await taxi_dispatch_settings_web.post(
        '/v1/admin/edit_groups',
        json={
            'groups': [
                {
                    'group_name': 'unknown',
                    'description': 'description',
                    'tariff_names': ['__default__unknown__', 'test_tariff_1'],
                },
            ],
        },
    )
    assert resp.status == 404
    r_json = await resp.json()
    assert r_json['code'] == 'group_not_found'

    resp = await taxi_dispatch_settings_web.post(
        '/v1/admin/edit_groups',
        json={
            'groups': [
                {
                    'group_name': 'group1',
                    'description': 'new_description',
                    'tariff_names': [
                        '__default__group1__',
                        'new_tariff_1',
                        'new_tariff_non_exists',
                    ],
                },
            ],
        },
    )
    assert resp.status == 500
    r_json = await resp.json()
    assert r_json['code'] == 'consistence_error'

    resp = await taxi_dispatch_settings_web.post(
        '/v1/admin/edit_groups',
        json={
            'groups': [
                {
                    'group_name': 'group2',
                    'description': 'new_description',
                    'tariff_names': ['__default__group2__', 'new_tariff_3'],
                },
            ],
        },
    )
    assert resp.status == 500
    r_json = await resp.json()
    assert r_json['code'] == 'consistence_error'

    pg_cursor.execute(
        """
        INSERT INTO dispatch_settings.zones (zone_name) VALUES ('__default__')
    """,
    )
    resp = await taxi_dispatch_settings_web.post(
        '/v1/admin/edit_groups',
        json={
            'groups': [
                {
                    'group_name': 'group2',
                    'description': 'new_description',
                    'tariff_names': ['__default__group2__', 'new_tariff_3'],
                },
            ],
        },
    )
    assert resp.status == 400
    r_json = await resp.json()
    assert r_json['code'] == 'settings_not_found'

    pg_cursor.execute(
        """INSERT INTO dispatch_settings.settings
      (tariff_id, zone_id, param_id, version, value)
      VALUES (
          (SELECT id FROM dispatch_settings.tariffs
            WHERE tariff_name = '__default__group2__'),
          (SELECT id FROM dispatch_settings.zones
            WHERE zone_name = '__default__'),
          (SELECT id FROM dispatch_settings.parameters
            WHERE field_name = 'INTEGER_POSITIVE_FIELD'),
          10,
          NULL
      )
      """,
    )
    resp = await taxi_dispatch_settings_web.post(
        '/v1/admin/edit_groups',
        json={
            'groups': [
                {
                    'group_name': 'group2',
                    'description': 'new_description',
                    'tariff_names': ['__default__group2__', 'new_tariff_3'],
                },
            ],
        },
    )
    assert resp.status == 400
    r_json = await resp.json()
    assert r_json['code'] == 'settings_not_found'

    pg_cursor.execute(
        """INSERT INTO dispatch_settings.settings
      (tariff_id, zone_id, param_id, version, value)
      VALUES (
          (SELECT id FROM dispatch_settings.tariffs
            WHERE tariff_name = '__default__group2__'),
          (SELECT id FROM dispatch_settings.zones
            WHERE zone_name = '__default__'),
          (SELECT id FROM dispatch_settings.parameters
            WHERE field_name = 'NEW_INTEGER_FIELD'),
          10,
          '1'
      )
      """,
    )

    resp = await taxi_dispatch_settings_web.post(
        '/v1/admin/edit_groups',
        json={
            'groups': [
                {
                    'group_name': 'group2',
                    'description': 'new_description',
                    'tariff_names': ['__default__group2__', 'new_tariff_3'],
                },
            ],
        },
    )
    assert resp.status == 400
    r_json = await resp.json()
    assert r_json['code'] == 'tariff_reset_error'

    resp = await taxi_dispatch_settings_web.post(
        '/v1/admin/edit_groups',
        json={
            'groups': [
                {
                    'group_name': 'group2',
                    'description': 'new_description',
                    'tariff_names': [
                        '__default__group1__',
                        '__default__group2__',
                        'new_tariff_1',
                        'new_tariff_2',
                        'new_tariff_3',
                        'new_tariff_non_exists',
                    ],
                },
            ],
        },
    )
    assert resp.status == 400
    r_json = await resp.json()
    assert r_json['code'] == 'wrong_default_tariff_error'

    resp = await taxi_dispatch_settings_web.post(
        '/v1/admin/edit_groups',
        json={
            'groups': [
                {
                    'group_name': 'group2',
                    'description': 'new_description',
                    'tariff_names': [
                        '__default__group2__',
                        'new_tariff_1',
                        'new_tariff_2',
                        'new_tariff_3',
                        'new_tariff_non_exists',
                    ],
                },
            ],
        },
    )
    assert resp.status == 400
    r_json = await resp.json()
    assert r_json['code'] == 'wrong_requested_tariff_error'

    assert current_groups(pg_cursor) == [
        ('group1', [], 'description_1'),
        (
            'group2',
            ['__default__group2__', 'new_tariff_1', 'new_tariff_2'],
            'description_2',
        ),
        (
            'group3',
            ['__default__group3__', 'new_tariff_3', 'new_tariff_4'],
            'description_3',
        ),
    ]

    taxi_config.set_values({'DISPATCH_SETTINGS_MAINTENANCE_MODE': True})
    await taxi_dispatch_settings_web.invalidate_caches()
    response = await taxi_dispatch_settings_web.post(
        '/v1/admin/edit_groups',
        json={
            'groups': [
                {
                    'group_name': 'group2',
                    'description': 'new_description',
                    'tariff_names': [
                        '__default__group2__',
                        'new_tariff_1',
                        'new_tariff_2',
                        'new_tariff_3',
                        'new_tariff_non_exists',
                    ],
                },
            ],
        },
    )
    assert response.status == 400
    r_json = await response.json()
    assert r_json['code'] == 'maintenance_mode'


@pytest.mark.config(
    ALL_CATEGORIES=[
        'new_tariff_1',
        'new_tariff_2',
        'new_tariff_3',
        'new_tariff_4',
        'not_exist_in_local_db_tariff',
    ],
)
@pytest.mark.pgsql('dispatch_settings', files=['admin_edit_groups.sql'])
async def test_admin_edit_group_positive(taxi_dispatch_settings_web, pgsql):
    pg_cursor = pgsql['dispatch_settings'].cursor()
    assert current_groups(pg_cursor) == [
        (
            'group2',
            ['__default__group2__', 'new_tariff_1', 'new_tariff_2'],
            'description_2',
        ),
        (
            'group3',
            ['__default__group3__', 'new_tariff_3', 'new_tariff_4'],
            'description_3',
        ),
    ]

    resp = await taxi_dispatch_settings_web.post(
        '/v1/admin/edit_groups',
        json={
            'groups': [
                {
                    'group_name': 'group2',
                    'description': 'second_description',
                    'tariff_names': [
                        '__default__group2__',
                        'new_tariff_1',
                        'new_tariff_2',
                        'new_tariff_3',
                    ],
                },
            ],
        },
    )
    assert resp.status == 200
    r_json = await resp.json()
    assert r_json['code'] == 'OK'

    assert current_groups(pg_cursor) == [
        (
            'group2',
            [
                '__default__group2__',
                'new_tariff_1',
                'new_tariff_2',
                'new_tariff_3',
            ],
            'second_description',
        ),
        ('group3', ['__default__group3__', 'new_tariff_4'], 'description_3'),
    ]

    resp = await taxi_dispatch_settings_web.post(
        '/v1/admin/edit_groups',
        json={
            'groups': [
                {
                    'group_name': 'group2',
                    'description': 'second_description_new',
                    'tariff_names': ['__default__group2__', 'new_tariff_1'],
                },
                {
                    'group_name': 'group3',
                    'description': 'third_description',
                    'tariff_names': [
                        '__default__group3__',
                        'new_tariff_2',
                        'new_tariff_3',
                        'new_tariff_4',
                    ],
                },
            ],
        },
    )
    assert resp.status == 200
    r_json = await resp.json()
    assert r_json['code'] == 'OK'

    assert current_groups(pg_cursor) == [
        (
            'group2',
            ['__default__group2__', 'new_tariff_1'],
            'second_description_new',
        ),
        (
            'group3',
            [
                '__default__group3__',
                'new_tariff_2',
                'new_tariff_3',
                'new_tariff_4',
            ],
            'third_description',
        ),
    ]

    # Checkng the addition of a new tariff via edit_groups
    assert current_tariffs(pg_cursor) == [
        '__default__group2__',
        '__default__group3__',
        'new_tariff_1',
        'new_tariff_2',
        'new_tariff_3',
        'new_tariff_4',
    ]

    resp = await taxi_dispatch_settings_web.post(
        '/v1/admin/edit_groups',
        json={
            'groups': [
                {
                    'group_name': 'group2',
                    'description': 'second_description_new',
                    'tariff_names': [
                        '__default__group2__',
                        'new_tariff_1',
                        'not_exist_in_local_db_tariff',
                    ],
                },
            ],
        },
    )
    assert resp.status == 200
    r_json = await resp.json()
    assert r_json['code'] == 'OK'

    assert current_groups(pg_cursor) == [
        (
            'group2',
            [
                '__default__group2__',
                'new_tariff_1',
                'not_exist_in_local_db_tariff',
            ],
            'second_description_new',
        ),
        (
            'group3',
            [
                '__default__group3__',
                'new_tariff_2',
                'new_tariff_3',
                'new_tariff_4',
            ],
            'third_description',
        ),
    ]

    assert current_tariffs(pg_cursor) == [
        '__default__group2__',
        '__default__group3__',
        'new_tariff_1',
        'new_tariff_2',
        'new_tariff_3',
        'new_tariff_4',
        'not_exist_in_local_db_tariff',
    ]
