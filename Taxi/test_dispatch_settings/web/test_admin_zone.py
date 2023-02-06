import test_dispatch_settings.web.mock_utils as mock_utils


def fetch_zones(cursor):
    cursor.execute(
        """
      SELECT zone_name
      FROM dispatch_settings.zones zones;
    """,
    )
    result = cursor.fetchall()
    return sorted([row[0] for row in result])


async def test_admin_zone_delete(
        taxi_dispatch_settings_web, pgsql, tariffs, taxi_config,
):
    tariffs.set_zones(['test_zone_1'])
    pg_cursor = pgsql['dispatch_settings'].cursor()
    assert [
        ('test_tariff_1', 'test_zone_1', 'MAX_ROBOT_DISTANCE', 1, 1),
        ('test_tariff_1', 'test_zone_2', 'MAX_ROBOT_DISTANCE', 2, 2),
    ] == mock_utils.current_settings(pg_cursor)

    resp = await taxi_dispatch_settings_web.delete(
        '/v1/admin/zone', params={'zone_name': 'test_zone_1'},
    )
    assert resp.status == 400
    r_json = await resp.json()
    assert r_json['code'] == 'valid_zone'

    for zone_name in ('test_zone_2', 'test_zone_3'):
        resp = await taxi_dispatch_settings_web.delete(
            '/v1/admin/zone', params={'zone_name': zone_name},
        )
        assert resp.status == 200
        r_json = await resp.json()
        assert r_json['code'] == 'OK'
        assert [
            ('test_tariff_1', 'test_zone_1', 'MAX_ROBOT_DISTANCE', 1, 1),
        ] == mock_utils.current_settings(pg_cursor)

    taxi_config.set_values({'DISPATCH_SETTINGS_MAINTENANCE_MODE': True})
    await taxi_dispatch_settings_web.invalidate_caches()
    resp = await taxi_dispatch_settings_web.delete(
        '/v1/admin/zone', params={'zone_name': 'test_zone_1'},
    )
    assert resp.status == 400
    r_json = await resp.json()
    assert r_json['code'] == 'maintenance_mode'


async def test_admin_zone_create(
        taxi_dispatch_settings_web, pgsql, tariffs, taxi_config,
):
    pg_cursor = pgsql['dispatch_settings'].cursor()
    assert ['__default__', 'test_zone_1', 'test_zone_2'] == fetch_zones(
        pg_cursor,
    )

    tariffs.set_zones(['test_zone_3'])
    resp = await taxi_dispatch_settings_web.post(
        '/v1/admin/zone', json={'zone_name': 'test_zone_4'},
    )
    assert resp.status == 400
    r_json = await resp.json()
    assert r_json['code'] == 'invalid_zone'

    resp = await taxi_dispatch_settings_web.post(
        '/v1/admin/zone', json={'zone_name': 'test_zone_3'},
    )
    assert resp.status == 200
    r_json = await resp.json()
    assert r_json['code'] == 'OK'
    assert [
        '__default__',
        'test_zone_1',
        'test_zone_2',
        'test_zone_3',
    ] == fetch_zones(pg_cursor)

    taxi_config.set_values({'DISPATCH_SETTINGS_MAINTENANCE_MODE': True})
    await taxi_dispatch_settings_web.invalidate_caches()
    resp = await taxi_dispatch_settings_web.post(
        '/v1/admin/zone', json={'zone_name': 'test_zone_3'},
    )
    assert resp.status == 400
    r_json = await resp.json()
    assert r_json['code'] == 'maintenance_mode'
