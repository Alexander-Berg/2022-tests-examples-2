async def test_admin_delete_group(taxi_dispatch_settings_web, taxi_config):
    resp = await taxi_dispatch_settings_web.post(
        '/v1/admin/delete_group', json={'group_name': 'unknown'},
    )
    assert resp.status == 404
    r_json = await resp.json()
    assert r_json['code'] == 'not_found'

    for group_id in ('group1', 'group4'):
        resp = await taxi_dispatch_settings_web.post(
            '/v1/admin/delete_group', json={'group_name': group_id},
        )
        assert resp.status == 500
        r_json = await resp.json()
        assert r_json['code'] == 'consistence_error'

    resp = await taxi_dispatch_settings_web.post(
        '/v1/admin/delete_group', json={'group_name': 'group2'},
    )
    assert resp.status == 400
    r_json = await resp.json()
    assert r_json['code'] == 'not_empty'

    resp = await taxi_dispatch_settings_web.post(
        '/v1/admin/delete_group', json={'group_name': 'group3'},
    )
    assert resp.status == 200
    r_json = await resp.json()
    assert r_json['code'] == 'OK'

    taxi_config.set_values({'DISPATCH_SETTINGS_MAINTENANCE_MODE': True})
    await taxi_dispatch_settings_web.invalidate_caches()
    response = await taxi_dispatch_settings_web.post(
        '/v1/admin/delete_group', json={'group_name': 'group3'},
    )
    assert response.status == 400
    r_json = await response.json()
    assert r_json['code'] == 'maintenance_mode'
