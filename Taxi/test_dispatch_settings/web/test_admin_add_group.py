import pytest

import test_dispatch_settings.web.mock_utils as mock_utils


@pytest.mark.pgsql('dispatch_settings', files=['admin_add_group.sql'])
async def test_admin_add_group(taxi_dispatch_settings_web, pgsql):
    resp = await taxi_dispatch_settings_web.post(
        '/v1/admin/add_group',
        json={'group_name': 'new_group_1', 'description': 'description'},
    )
    assert resp.status == 400
    r_json = await resp.json()
    assert r_json['code'] == 'invalid_group_name'

    resp = await taxi_dispatch_settings_web.post(
        '/v1/admin/add_group',
        json={
            'group_name': 'base_group',
            'description': 'description',
            'based_on_group_name': 'base_group',
        },
    )
    assert resp.status == 400
    r_json = await resp.json()
    assert r_json['code'] == 'same_group_names'

    resp = await taxi_dispatch_settings_web.post(
        '/v1/admin/add_group',
        json={
            'group_name': 'old',
            'description': 'description',
            'based_on_group_name': 'new_group',
        },
    )
    assert resp.status == 400
    r_json = await resp.json()
    assert r_json['code'] == 'already_exists'

    resp = await taxi_dispatch_settings_web.post(
        '/v1/admin/add_group',
        json={
            'group_name': 'base_group',
            'description': 'description',
            'based_on_group_name': 'unknown',
        },
    )
    assert resp.status == 400
    r_json = await resp.json()
    assert r_json['code'] == 'not_exists'

    resp = await taxi_dispatch_settings_web.post(
        '/v1/admin/add_group',
        json={
            'group_name': 'base_group',
            'description': 'description',
            'based_on_group_name': 'old',
        },
    )
    assert resp.status == 500
    r_json = await resp.json()
    assert r_json['code'] == 'consistence_error'

    pg_cursor = pgsql['dispatch_settings'].cursor()
    pg_cursor.execute(
        """
        INSERT INTO dispatch_settings.tariffs (tariff_name, group_id)
        VALUES ('__default__old__', (
          SELECT id FROM dispatch_settings.groups WHERE name = 'old')
        );
    """,
    )
    resp = await taxi_dispatch_settings_web.post(
        '/v1/admin/add_group',
        json={
            'group_name': 'base_group',
            'description': 'description',
            'based_on_group_name': 'old',
        },
    )
    assert resp.status == 500
    r_json = await resp.json()
    assert r_json['code'] == 'consistence_error'

    pg_cursor.execute(
        """
        INSERT INTO dispatch_settings.zones
        (zone_name) VALUES ('__default__');
    """,
    )
    resp = await taxi_dispatch_settings_web.post(
        '/v1/admin/add_group',
        json={
            'group_name': 'base_group',
            'description': 'description',
            'based_on_group_name': 'old',
        },
    )
    assert resp.status == 404
    r_json = await resp.json()
    assert r_json['code'] == 'settings_not_found'

    pg_cursor.execute(
        """INSERT INTO dispatch_settings.settings
      (tariff_id, zone_id, param_id, version, value)
      VALUES (
          (SELECT id FROM dispatch_settings.tariffs
            WHERE tariff_name = '__default__old__'),
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
        '/v1/admin/add_group',
        json={
            'group_name': 'base_group',
            'description': 'description',
            'based_on_group_name': 'old',
        },
    )
    assert resp.status == 404
    r_json = await resp.json()
    assert r_json['code'] == 'settings_not_found'

    resp = await taxi_dispatch_settings_web.post(
        '/v1/admin/add_group',
        json={'group_name': 'base_group', 'description': 'description'},
    )
    assert resp.status == 200
    r_json = await resp.json()
    assert r_json['code'] == 'OK'

    pg_cursor.execute(
        """SELECT id, name, description """
        """FROM dispatch_settings.groups ORDER BY name;""",
    )
    group_ids, group_descriptions = [], []
    for group in pg_cursor.fetchall():
        group_ids.append(group[0])
        group_descriptions.append((group[1], group[2]))
    assert group_descriptions == [
        ('base_group', 'description'),
        ('old', 'description'),
    ]

    pg_cursor.execute(
        """SELECT tariff_name, group_id """
        """FROM dispatch_settings.tariffs ORDER BY tariff_name;""",
    )
    tariffs = pg_cursor.fetchall()
    assert tariffs == [
        ('__default__base_group__', group_ids[0]),
        ('__default__old__', group_ids[1]),
    ]


@pytest.mark.pgsql(
    'dispatch_settings', files=['add_group_based_on_another.sql'],
)
async def test_admin_add_group_based_on_another(
        taxi_dispatch_settings_web, pgsql, taxi_config,
):
    pg_cursor = pgsql['dispatch_settings'].cursor()
    assert [
        ('__default__old__', '__default__', 'INTEGER_POSITIVE_FIELD', 10, 22),
        ('__default__old__', '__default__', 'NEW_INTEGER_FIELD', 11, 3),
    ] == mock_utils.current_settings(pg_cursor)

    resp = await taxi_dispatch_settings_web.post(
        '/v1/admin/add_group',
        json={
            'group_name': 'base',
            'description': 'description',
            'based_on_group_name': 'old',
        },
    )
    assert resp.status == 200
    r_json = await resp.json()
    assert r_json['code'] == 'OK'

    assert [
        ('__default__base__', '__default__', 'INTEGER_POSITIVE_FIELD', 0, 22),
        ('__default__base__', '__default__', 'NEW_INTEGER_FIELD', 0, 3),
        ('__default__old__', '__default__', 'INTEGER_POSITIVE_FIELD', 10, 22),
        ('__default__old__', '__default__', 'NEW_INTEGER_FIELD', 11, 3),
    ] == mock_utils.current_settings(pg_cursor)

    taxi_config.set_values({'DISPATCH_SETTINGS_MAINTENANCE_MODE': True})
    await taxi_dispatch_settings_web.invalidate_caches()
    resp = await taxi_dispatch_settings_web.post(
        '/v1/admin/add_group',
        json={
            'group_name': 'base',
            'description': 'description',
            'based_on_group_name': 'old',
        },
    )
    assert resp.status == 400
    r_json = await resp.json()
    assert r_json['code'] == 'maintenance_mode'
