import pytest


@pytest.mark.now('2021-09-16T12:00:00+03:00')
async def test_expiration_point_validation(taxi_hejmdal, pgsql):
    await taxi_hejmdal.run_task('circuit_states_cache/invalidate')
    await taxi_hejmdal.run_task('services_component/invalidate')

    response = await taxi_hejmdal.put(
        '/v1/mod/create',
        headers={'X-Yandex-Login': 'login1'},
        json={
            'ticket': 'SOMETICKET',
            'spec_template_id': 'rtc_memory_usage',
            'apply_when': 'always',
            'expiration_point': '2021-09-16T11:50:00+03:00',
            'service_id': 1,
            'service_name': 'test_service (nanny, test_project)',
            'env_type': 'stable',
            'mod_type': 'spec_disable',
            'mod_data': {'disable': True},
        },
    )
    assert response.status_code == 400

    cursor = pgsql['hejmdal'].cursor()
    query = 'select * from spec_template_mods;'
    cursor.execute(query)
    db_res = cursor.fetchall()
    assert db_res == []

    response = await taxi_hejmdal.put(
        '/v1/mod/create',
        headers={'X-Yandex-Login': 'login1'},
        json={
            'ticket': 'SOMETICKET',
            'spec_template_id': 'rtc_memory_usage',
            'apply_when': 'always',
            'service_id': 1,
            'service_name': 'test_service (nanny, test_project)',
            'env_type': 'stable',
            'mod_type': 'spec_disable',
            'mod_data': {'disable': True},
        },
    )
    assert response.status_code == 200

    cursor = pgsql['hejmdal'].cursor()
    query = 'select * from spec_template_mods;'
    cursor.execute(query)
    db_res = cursor.fetchall()
    assert len(db_res) == 1

    response = await taxi_hejmdal.put(
        '/v1/mod/update?mod_id=1',
        headers={'X-Yandex-Login': 'login1'},
        json={
            'mod_type': 'spec_disable',
            'mod_data': {'disable': True},
            'expiration_point': '2021-09-16T11:50:00+03:00',
        },
    )
    assert response.status_code == 400

    response = await taxi_hejmdal.put(
        '/v1/mod/update?mod_id=1',
        headers={'X-Yandex-Login': 'login1'},
        json={
            'mod_type': 'spec_disable',
            'mod_data': {'disable': True},
            'expiration_point': '2021-09-16T12:10:00+03:00',
        },
    )
    assert response.status_code == 200

    cursor = pgsql['hejmdal'].cursor()
    query = (
        'select ticket, spec_template_id, apply_when, expiration_point, '
        'service_id, env, deleted, expired, type, mod_data '
        'from spec_template_mods'
    )
    cursor.execute(query)
    db_res = cursor.fetchall()
    assert len(db_res) == 1
    assert db_res[0][0] == 'SOMETICKET'
    assert db_res[0][1] == 'rtc_memory_usage'
    assert db_res[0][2] == 'always'
    assert db_res[0][3].isoformat() == '2021-09-16T12:10:00+03:00'
    assert db_res[0][4] == 1
    assert db_res[0][5] == 'stable'
    assert db_res[0][6] is False
    assert db_res[0][7] is False
    assert db_res[0][8] == 'spec_disable'
    assert db_res[0][9] == {'disable': True}


@pytest.mark.now('2021-09-16T12:00:00+03')
async def test_update_expiration_point(taxi_hejmdal, pgsql):
    response = await taxi_hejmdal.put(
        '/v1/mod/create',
        headers={'X-Yandex-Login': 'login1'},
        json={
            'ticket': 'SOMETICKET',
            'spec_template_id': 'rtc_memory_usage',
            'apply_when': 'always',
            'service_id': 1,
            'service_name': 'test_service (nanny, test_project)',
            'env_type': 'stable',
            'mod_type': 'spec_disable',
            'mod_data': {'disable': True},
        },
    )
    assert response.status_code == 200

    response = await taxi_hejmdal.put(
        '/v1/mod/update?mod_id=1',
        headers={'X-Yandex-Login': 'login1'},
        json={
            'mod_type': 'spec_disable',
            'mod_data': {'disable': True},
            'expiration_point': '2021-09-16T12:15:00+02:00',
        },
    )
    assert response.status_code == 200
    cursor = pgsql['hejmdal'].cursor()
    query = 'select expiration_point from spec_template_mods;'
    cursor.execute(query)
    db_res = cursor.fetchall()
    assert len(db_res) == 1
    assert db_res[0][0].isoformat() == '2021-09-16T13:15:00+03:00'

    response = await taxi_hejmdal.put(
        '/v1/mod/update?mod_id=1',
        headers={'X-Yandex-Login': 'login1'},
        json={'mod_type': 'spec_disable', 'mod_data': {'disable': True}},
    )
    assert response.status_code == 200
    cursor = pgsql['hejmdal'].cursor()
    query = 'select expiration_point from spec_template_mods;'
    cursor.execute(query)
    db_res = cursor.fetchall()
    assert len(db_res) == 1
    assert db_res[0][0] is None


@pytest.mark.now('2021-09-16T12:00:00+03')
async def test_delete_expired_mods(taxi_hejmdal, pgsql, mocked_time):
    response = await taxi_hejmdal.put(
        '/v1/mod/create',
        headers={'X-Yandex-Login': 'login1'},
        json={
            'ticket': 'SOMETICKET',
            'spec_template_id': 'rtc_memory_usage',
            'apply_when': 'always',
            'expiration_point': '2021-09-16T12:10:00+03',
            'service_id': 1,
            'service_name': 'test_service (nanny, test_project)',
            'env_type': 'stable',
            'mod_type': 'spec_disable',
            'mod_data': {'disable': True},
        },
    )
    assert response.status_code == 200

    await taxi_hejmdal.run_task('distlock/db_cleanup')

    cursor = pgsql['hejmdal'].cursor()
    query = (
        'select ticket, spec_template_id, apply_when, expiration_point, '
        'service_id, env, deleted, expired, type, mod_data '
        'from spec_template_mods'
    )
    cursor.execute(query)
    db_res = cursor.fetchall()
    assert len(db_res) == 1
    assert db_res[0][0] == 'SOMETICKET'
    assert db_res[0][1] == 'rtc_memory_usage'
    assert db_res[0][2] == 'always'
    assert db_res[0][3].isoformat() == '2021-09-16T12:10:00+03:00'
    assert db_res[0][4] == 1
    assert db_res[0][5] == 'stable'
    assert db_res[0][6] is False
    assert db_res[0][7] is False
    assert db_res[0][8] == 'spec_disable'
    assert db_res[0][9] == {'disable': True}

    mocked_time.sleep(500)
    await taxi_hejmdal.run_task('distlock/db_cleanup')

    cursor = pgsql['hejmdal'].cursor()
    query = 'select expired from spec_template_mods'
    cursor.execute(query)
    db_res = cursor.fetchall()
    assert len(db_res) == 1
    assert db_res[0][0] is False

    mocked_time.sleep(150)
    await taxi_hejmdal.run_task('distlock/db_cleanup')

    cursor = pgsql['hejmdal'].cursor()
    query = 'select expired from spec_template_mods'
    cursor.execute(query)
    db_res = cursor.fetchall()
    assert len(db_res) == 1
    assert db_res[0][0] is True
