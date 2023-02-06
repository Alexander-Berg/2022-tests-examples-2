import pytest


DB_TIMEOUTS = {'network_timeout': 100, 'statement_timeout': 100}
DISABLE_VALIDATION_SETTINGS = {
    'db_timeouts': {
        'retrieve': DB_TIMEOUTS,
        'update': DB_TIMEOUTS,
        'list': DB_TIMEOUTS,
    },
    'mod_validation': {
        'check_spec_template_exists': False,
        'check_service_exists': False,
        'check_host_exists': False,
        'check_domain_exists': False,
        'check_circuit_exists': False,
        'check_mod_data': False,
    },
}
ENABLE_VALIDATION_SETTINGS = {
    'db_timeouts': {
        'retrieve': DB_TIMEOUTS,
        'update': DB_TIMEOUTS,
        'list': DB_TIMEOUTS,
    },
    'mod_validation': {
        'check_spec_template_exists': True,
        'check_service_exists': True,
        'check_host_exists': True,
        'check_domain_exists': True,
        'check_circuit_exists': True,
        'check_mod_data': True,
    },
}


@pytest.mark.config(HEJMDAL_MOD_API_SETTINGS=DISABLE_VALIDATION_SETTINGS)
async def test_create_mods(taxi_hejmdal):
    await taxi_hejmdal.run_task('services_component/invalidate')
    await taxi_hejmdal.invalidate_caches(
        clean_update=True, cache_names=['spec-template-mod-cache'],
    )
    await taxi_hejmdal.run_task('tuner/initialize')

    for mod_id in [101, 102]:
        response = await taxi_hejmdal.post(
            '/v1/mod/retrieve', params={'mod_id': mod_id},
        )
        assert response.status_code == 404
        assert response.json() == {'code': '404', 'message': 'mod not found'}

    response = await taxi_hejmdal.put(
        '/v1/mod/create',
        headers={'X-Yandex-Login': 'login1'},
        json={
            'ticket': 'SOMETICKET',
            'spec_template_id': 'spec_template_id1',
            'apply_when': 'always',
            'service_id': 1,
            'service_name': 'test_service (nanny, test_project)',
            'env_type': 'stable',
            'mod_type': 'spec_disable',
            'mod_data': {'disable': True},
        },
    )
    assert response.status_code == 200
    response_json = response.json()
    assert 'mod_id' in response_json
    mod_id1 = response_json['mod_id']
    assert 'updated' in response_json
    updated1 = response_json['updated']

    response = await taxi_hejmdal.put(
        '/v1/mod/create',
        headers={'X-Yandex-Login': 'login2'},
        json={
            'ticket': 'OTHERTICKET',
            'spec_template_id': 'spec_template_id2',
            'apply_when': 'always',
            'service_id': 2,
            'service_name': 'test_service2 (nanny, test_project)',
            'domain': 'some_domain',
            'mod_type': 'spec_disable',
            'mod_data': {'disable': True},
        },
    )
    assert response.status_code == 200
    response_json = response.json()
    assert 'mod_id' in response_json
    mod_id2 = response_json['mod_id']
    assert 'updated' in response_json
    updated2 = response_json['updated']

    assert mod_id1 != mod_id2

    await taxi_hejmdal.invalidate_caches(
        clean_update=False, cache_names=['spec-template-mod-cache'],
    )

    response = await taxi_hejmdal.post(
        '/v1/mod/retrieve', params={'mod_id': mod_id1},
    )
    assert response.status_code == 200
    assert response.json() == {
        'mod_id': mod_id1,
        'login': 'login1',
        'updated': updated1,
        'ticket': 'SOMETICKET',
        'spec_template_id': 'spec_template_id1',
        'apply_when': 'always',
        'service_id': 1,
        'service_name': 'test_service (nanny, test_project)',
        'env_type': 'stable',
        'mod_type': 'spec_disable',
        'mod_data': {'disable': True},
        'usage_count': 0,
        'expired': False,
    }

    response = await taxi_hejmdal.post(
        '/v1/mod/retrieve', params={'mod_id': mod_id2},
    )
    assert response.status_code == 200
    assert response.json() == {
        'mod_id': mod_id2,
        'login': 'login2',
        'updated': updated2,
        'ticket': 'OTHERTICKET',
        'spec_template_id': 'spec_template_id2',
        'apply_when': 'always',
        'service_id': 2,
        'service_name': 'test_service2 (nanny, test_project)',
        'domain': 'some_domain',
        'mod_type': 'spec_disable',
        'mod_data': {'disable': True},
        'usage_count': 0,
        'expired': False,
    }

    response = await taxi_hejmdal.post('/v1/mod/list')
    assert response.status_code == 200
    assert response.json() == {
        'mods': [
            {
                'mod_id': mod_id1,
                'login': 'login1',
                'updated': updated1,
                'ticket': 'SOMETICKET',
                'spec_template_id': 'spec_template_id1',
                'apply_when': 'always',
                'service_id': 1,
                'service_name': 'test_service (nanny, test_project)',
                'env_type': 'stable',
                'mod_type': 'spec_disable',
                'usage_count': 0,
                'expired': False,
            },
            {
                'mod_id': mod_id2,
                'login': 'login2',
                'updated': updated2,
                'ticket': 'OTHERTICKET',
                'spec_template_id': 'spec_template_id2',
                'apply_when': 'always',
                'service_id': 2,
                'service_name': 'test_service2 (nanny, test_project)',
                'domain': 'some_domain',
                'mod_type': 'spec_disable',
                'usage_count': 0,
                'expired': False,
            },
        ],
    }

    response = await taxi_hejmdal.delete(
        '/v1/mod/delete',
        params={'mod_id': mod_id1},
        headers={'X-Yandex-Login': 'some-login'},
    )
    assert response.status_code == 200
    assert response.content == b''

    await taxi_hejmdal.invalidate_caches(
        clean_update=False, cache_names=['spec-template-mod-cache'],
    )

    response = await taxi_hejmdal.post(
        '/v1/mod/retrieve', params={'mod_id': mod_id1},
    )
    assert response.status_code == 404
    assert response.json() == {'code': '404', 'message': 'mod not found'}

    response = await taxi_hejmdal.post('/v1/mod/list')
    assert response.status_code == 200
    assert response.json() == {
        'mods': [
            {
                'mod_id': mod_id2,
                'login': 'login2',
                'updated': updated2,
                'ticket': 'OTHERTICKET',
                'spec_template_id': 'spec_template_id2',
                'apply_when': 'always',
                'service_id': 2,
                'service_name': 'test_service2 (nanny, test_project)',
                'domain': 'some_domain',
                'mod_type': 'spec_disable',
                'usage_count': 0,
                'expired': False,
            },
        ],
    }

    response = await taxi_hejmdal.put(
        '/v1/mod/create',
        headers={'X-Yandex-Login': 'login3'},
        json={
            'ticket': 'THIRDTICKET',
            'spec_template_id': 'spec_template_id1',
            'apply_when': 'always',
            'service_id': 1,
            'service_name': 'test_service (nanny, test_project)',
            'env_type': 'stable',
            'mod_type': 'schema_override',
            'mod_data': {'params': {'some_param': 'some_value'}},
        },
    )
    assert response.status_code == 200
    response_json = response.json()
    assert 'mod_id' in response_json
    mod_id3 = response_json['mod_id']
    assert 'updated' in response_json
    updated3 = response_json['updated']

    response = await taxi_hejmdal.post(
        '/v1/mod/retrieve', params={'mod_id': mod_id3},
    )
    assert response.status_code == 200
    assert response.json() == {
        'mod_id': mod_id3,
        'login': 'login3',
        'updated': updated3,
        'ticket': 'THIRDTICKET',
        'spec_template_id': 'spec_template_id1',
        'apply_when': 'always',
        'service_id': 1,
        'service_name': 'test_service (nanny, test_project)',
        'env_type': 'stable',
        'mod_type': 'schema_override',
        'mod_data': {'params': {'some_param': 'some_value'}},
        'expired': False,
    }


@pytest.mark.config(HEJMDAL_MOD_API_SETTINGS=DISABLE_VALIDATION_SETTINGS)
async def test_update_mod(taxi_hejmdal, pgsql):
    await taxi_hejmdal.invalidate_caches(
        clean_update=True, cache_names=['spec-template-mod-cache'],
    )
    await taxi_hejmdal.run_task('tuner/initialize')

    response = await taxi_hejmdal.put(
        '/v1/mod/create',
        headers={'X-Yandex-Login': 'login1'},
        json={
            'ticket': 'SOMETICKET',
            'spec_template_id': 'spec_template_id1',
            'apply_when': 'always',
            'service_id': 1,
            'service_name': 'test_service (nanny, test_project)',
            'env_type': 'stable',
            'mod_type': 'spec_disable',
            'mod_data': {'disable': True},
        },
    )
    assert response.status_code == 200
    response_json = response.json()
    assert 'mod_id' in response_json
    mod_id1 = response_json['mod_id']

    cursor = pgsql['hejmdal'].cursor()
    cursor.execute(
        f'select revision from spec_template_mods where id={mod_id1}',
    )
    query_result = cursor.fetchall()
    assert len(query_result) == 1
    assert len(query_result[0]) == 1
    revision1 = query_result[0][0]

    response = await taxi_hejmdal.put(
        '/v1/mod/update',
        headers={'X-Yandex-Login': 'login1'},
        params={'mod_id': mod_id1},
        json={'mod_type': 'spec_disable', 'mod_data': {'disable': False}},
    )
    assert response.status_code == 200
    response_json = response.json()
    assert 'mod_id' in response_json
    mod_id2 = response_json['mod_id']
    assert 'updated' in response_json
    updated2 = response_json['updated']

    assert mod_id1 == mod_id2

    response = await taxi_hejmdal.post(
        '/v1/mod/retrieve', params={'mod_id': mod_id1},
    )
    assert response.status_code == 200
    assert response.json() == {
        'mod_id': mod_id1,
        'login': 'login1',
        'updated': updated2,
        'ticket': 'SOMETICKET',
        'spec_template_id': 'spec_template_id1',
        'apply_when': 'always',
        'service_id': 1,
        'service_name': 'test_service (nanny, test_project)',
        'env_type': 'stable',
        'mod_type': 'spec_disable',
        'mod_data': {'disable': False},
        'expired': False,
    }

    cursor.execute(
        f'select revision from spec_template_mods where id={mod_id1}',
    )
    query_result = cursor.fetchall()
    assert len(query_result) == 1
    assert len(query_result[0]) == 1
    revision2 = query_result[0][0]

    assert revision2 > revision1


@pytest.mark.config(HEJMDAL_MOD_API_SETTINGS=DISABLE_VALIDATION_SETTINGS)
@pytest.mark.parametrize(
    'relation,response_code',
    [
        ({'domain': 'domain1'}, 200),
        ({'env_type': 'stable'}, 200),
        (
            {
                'service_id': 1,
                'service_name': 'test_service (nanny, test_project)',
            },
            200,
        ),
        ({'circuit_id': 'some_circuit'}, 200),
        (
            {
                'service_id': 1,
                'service_name': 'test_service (nanny, test_project)',
                'domain': 'domain1',
            },
            200,
        ),
        (
            {
                'service_id': 1,
                'service_name': 'test_service (nanny, test_project)',
                'env_type': 'testing',
            },
            200,
        ),
        (
            {
                'service_id': 1,
                'service_name': 'test_service (nanny, test_project)',
                'host': 'host1',
            },
            200,
        ),
        ({'env_type': 'stable', 'host': 'some_host'}, 400),
        (
            {
                'service_id': 1,
                'service_name': 'test_service (nanny, test_project)',
                'env_type': 'stable',
                'host': 'some_host',
            },
            200,
        ),
        ({'env_type': 'stable', 'domain': 'some_domain'}, 400),
        (
            {
                'service_id': 1,
                'service_name': 'test_service (nanny, test_project)',
                'env_type': 'stable',
                'domain': 'some_domain',
            },
            400,
        ),
    ],
)
async def test_correct_mod_relations(taxi_hejmdal, relation, response_code):
    await taxi_hejmdal.run_task('services_component/invalidate')
    await taxi_hejmdal.invalidate_caches(
        clean_update=True, cache_names=['spec-template-mod-cache'],
    )
    await taxi_hejmdal.run_task('tuner/initialize')

    response = await taxi_hejmdal.put(
        '/v1/mod/create',
        headers={'X-Yandex-Login': 'login1'},
        json={
            'ticket': 'SOMETICKET',
            'spec_template_id': 'spec_template_id1',
            'apply_when': 'always',
            **relation,
            'mod_type': 'spec_disable',
            'mod_data': {'disable': True},
        },
    )
    assert response.status_code == response_code
    response_json = response.json()
    if response_code == 200:
        assert 'mod_id' in response_json
        mod_id1 = response_json['mod_id']
        assert 'updated' in response_json
        updated1 = response_json['updated']

        response = await taxi_hejmdal.post(
            '/v1/mod/retrieve', params={'mod_id': mod_id1},
        )
        assert response.status_code == 200
        assert response.json() == {
            'mod_id': mod_id1,
            'login': 'login1',
            'updated': updated1,
            'ticket': 'SOMETICKET',
            'spec_template_id': 'spec_template_id1',
            'apply_when': 'always',
            **relation,
            'mod_type': 'spec_disable',
            'mod_data': {'disable': True},
            'expired': False,
        }
    elif response_code == 400:
        assert response_json == {
            'code': '400',
            'message': 'invalid mod relation',
        }


@pytest.mark.config(HEJMDAL_MOD_API_SETTINGS=DISABLE_VALIDATION_SETTINGS)
async def test_mod_usage_count(taxi_hejmdal):
    await taxi_hejmdal.run_task('services_component/invalidate')
    response = await taxi_hejmdal.put(
        '/v1/mod/create',
        headers={'X-Yandex-Login': 'login1'},
        json={
            'ticket': 'SOMETICKET',
            'spec_template_id': 'test_circuit_id',
            'apply_when': 'always',
            'host': 'test_host',
            'mod_type': 'spec_disable',
            'mod_data': {'disable': False},
        },
    )
    assert response.status_code == 200
    response_json = response.json()
    assert 'mod_id' in response_json
    mod_id1 = response_json['mod_id']
    assert 'updated' in response_json
    updated1 = response_json['updated']

    await taxi_hejmdal.invalidate_caches(
        clean_update=True,
        cache_names=['spec-template-mod-cache', 'schemas-cache'],
    )
    await taxi_hejmdal.run_task('tuner/initialize')

    response = await taxi_hejmdal.post(
        '/v1/mod/retrieve', params={'mod_id': mod_id1},
    )

    assert response.status_code == 200
    assert response.json() == {
        'mod_id': mod_id1,
        'login': 'login1',
        'updated': updated1,
        'ticket': 'SOMETICKET',
        'spec_template_id': 'test_circuit_id',
        'apply_when': 'always',
        'host': 'test_host',
        'mod_type': 'spec_disable',
        'mod_data': {'disable': False},
        'usage_count': 1,
        'expired': False,
    }


@pytest.mark.config(HEJMDAL_MOD_API_SETTINGS=DISABLE_VALIDATION_SETTINGS)
async def test_mod_conflict(taxi_hejmdal):
    await taxi_hejmdal.run_task('services_component/invalidate')
    await taxi_hejmdal.invalidate_caches(
        clean_update=True, cache_names=['spec-template-mod-cache'],
    )
    await taxi_hejmdal.run_task('tuner/initialize')
    response = await taxi_hejmdal.put(
        '/v1/mod/create',
        headers={'X-Yandex-Login': 'login1'},
        json={
            'ticket': 'SOMETICKET',
            'spec_template_id': 'spec_template_id1',
            'apply_when': 'always',
            'service_id': 1,
            'env_type': 'stable',
            'mod_type': 'spec_disable',
            'mod_data': {'disable': True},
        },
    )
    assert response.status_code == 200

    response = await taxi_hejmdal.put(
        '/v1/mod/create',
        headers={'X-Yandex-Login': 'login2'},
        json={
            'ticket': 'OTHERTICKET',
            'spec_template_id': 'spec_template_id1',
            'apply_when': 'always',
            'service_id': 1,
            'env_type': 'stable',
            'mod_type': 'spec_disable',
            'mod_data': {'disable': False},
        },
    )
    assert response.status_code == 409
    assert response.json() == {
        'code': '409',
        'message': 'mod with this relation already exists',
    }


@pytest.mark.config(HEJMDAL_MOD_API_SETTINGS=DISABLE_VALIDATION_SETTINGS)
async def test_create_mod_by_service_name(taxi_hejmdal):

    response = await taxi_hejmdal.put(
        '/v1/mod/create',
        headers={'X-Yandex-Login': 'login1'},
        json={
            'ticket': 'SOMETICKET',
            'spec_template_id': 'spec_template_id1',
            'apply_when': 'always',
            'service_name': 'test_service (nanny, test_project)',
            'env_type': 'stable',
            'mod_type': 'spec_disable',
            'mod_data': {'disable': True},
        },
    )

    assert response.status_code == 200
    response_json = response.json()
    assert 'mod_id' in response_json
    mod_id1 = response_json['mod_id']
    assert 'updated' in response_json
    updated1 = response_json['updated']

    await taxi_hejmdal.run_task('services_component/invalidate')
    await taxi_hejmdal.invalidate_caches(
        clean_update=True, cache_names=['spec-template-mod-cache'],
    )
    await taxi_hejmdal.run_task('tuner/initialize')

    response = await taxi_hejmdal.post(
        '/v1/mod/retrieve', params={'mod_id': mod_id1},
    )
    assert response.status_code == 200
    assert response.json() == {
        'mod_id': mod_id1,
        'login': 'login1',
        'updated': updated1,
        'ticket': 'SOMETICKET',
        'spec_template_id': 'spec_template_id1',
        'apply_when': 'always',
        'service_id': 1,
        'service_name': 'test_service (nanny, test_project)',
        'env_type': 'stable',
        'mod_type': 'spec_disable',
        'mod_data': {'disable': True},
        'usage_count': 0,
        'expired': False,
    }


@pytest.mark.config(HEJMDAL_MOD_API_SETTINGS=ENABLE_VALIDATION_SETTINGS)
async def test_validate_mod(taxi_hejmdal):
    await taxi_hejmdal.invalidate_caches(
        clean_update=True, cache_names=['schemas-cache'],
    )
    await taxi_hejmdal.run_task('services_component/invalidate')

    response = await taxi_hejmdal.put(
        '/v1/mod/create',
        headers={'X-Yandex-Login': 'login1'},
        json={
            'ticket': 'SOMETICKET',
            'spec_template_id': 'unknown_spec_template_id',
            'apply_when': 'always',
            'service_name': 'test_service (nanny, test_project)',
            'mod_type': 'spec_disable',
            'mod_data': {'disable': True},
        },
    )
    assert response.status_code == 404
    assert response.json() == {
        'code': '404',
        'message': 'invalid spec template id',
    }

    response = await taxi_hejmdal.put(
        '/v1/mod/create',
        headers={'X-Yandex-Login': 'login1'},
        json={
            'ticket': 'SOMETICKET',
            'spec_template_id': 'test_circuit_id',
            'apply_when': 'always',
            'service_name': 'unknown_service',
            'mod_type': 'spec_disable',
            'mod_data': {'disable': True},
        },
    )
    assert response.status_code == 404
    assert response.json() == {'code': '404', 'message': 'service not found'}

    response = await taxi_hejmdal.put(
        '/v1/mod/create',
        headers={'X-Yandex-Login': 'login1'},
        json={
            'ticket': 'SOMETICKET',
            'spec_template_id': 'test_circuit_id',
            'apply_when': 'always',
            'service_name': 'test_service (nanny, test_project)',
            'host': 'unknown_host',
            'mod_type': 'spec_disable',
            'mod_data': {'disable': True},
        },
    )
    assert response.status_code == 404
    assert response.json() == {'code': '404', 'message': 'host not found'}

    response = await taxi_hejmdal.put(
        '/v1/mod/create',
        headers={'X-Yandex-Login': 'login1'},
        json={
            'ticket': 'SOMETICKET',
            'spec_template_id': 'test_circuit_id',
            'apply_when': 'always',
            'service_name': 'test_service (nanny, test_project)',
            'host': 'test_service_stable_branch_host_name_1',
            'mod_type': 'spec_disable',
            'mod_data': {'disable': True},
        },
    )
    assert response.status_code == 200
    response_json = response.json()
    assert 'mod_id' in response_json
    mod_id = response_json['mod_id']

    response = await taxi_hejmdal.put(
        '/v1/mod/update',
        params={'mod_id': mod_id},
        headers={'X-Yandex-Login': 'login1'},
        json={
            'mod_type': 'schema_override',
            'mod_data': {'params': {'unknown_block_id': {'unknown_param': 1}}},
        },
    )
    assert response.status_code == 400
    assert response.json() == {'code': '400', 'message': 'invalid mod data'}

    response = await taxi_hejmdal.put(
        '/v1/mod/update',
        params={'mod_id': mod_id},
        headers={'X-Yandex-Login': 'login1'},
        json={
            'mod_type': 'schema_override',
            'mod_data': {
                'params': {'avg_usage': {'max_sample_size': 370}},
                'history_data_duration_sec': 60,
            },
        },
    )
    assert response.status_code == 200

    response = await taxi_hejmdal.put(
        '/v1/mod/update',
        params={'mod_id': mod_id},
        headers={'X-Yandex-Login': 'login1'},
        json={
            'mod_type': 'schema_override',
            'mod_data': {
                'params': {'avg_usage': {'max_sample_size': 370}},
                'invalid_field': 60,
            },
        },
    )
    assert response.status_code == 400

    response = await taxi_hejmdal.put(
        '/v1/mod/update',
        params={'mod_id': mod_id},
        headers={'X-Yandex-Login': 'login1'},
        json={'mod_type': 'spec_disable', 'mod_data': {'disable': False}},
    )
    assert response.status_code == 200

    response = await taxi_hejmdal.put(
        '/v1/mod/update',
        params={'mod_id': mod_id},
        headers={'X-Yandex-Login': 'login1'},
        json={'mod_type': 'spec_disable', 'mod_data': {'disable': True}},
    )
    assert response.status_code == 200

    response = await taxi_hejmdal.put(
        '/v1/mod/create',
        headers={'X-Yandex-Login': 'login1'},
        json={
            'ticket': 'SOMETICKET',
            'spec_template_id': 'test_circuit_id',
            'apply_when': 'always',
            'service_name': 'test_service (nanny, test_project)',
            'mod_type': 'spec_disable',
            'mod_data': {'disable': True},
        },
    )
    assert response.status_code == 200


@pytest.mark.config(HEJMDAL_MOD_API_SETTINGS=DISABLE_VALIDATION_SETTINGS)
async def test_flow_params_override(taxi_hejmdal):
    await taxi_hejmdal.invalidate_caches(
        clean_update=True, cache_names=['spec-template-mod-cache'],
    )
    await taxi_hejmdal.run_task('tuner/initialize')

    response = await taxi_hejmdal.put(
        '/v1/mod/create',
        headers={'X-Yandex-Login': 'login1'},
        json={
            'ticket': 'SOMETICKET',
            'spec_template_id': 'spec_template_id1',
            'apply_when': 'always',
            'service_id': 1,
            'service_name': 'test_service (nanny, test_project)',
            'env_type': 'stable',
            'mod_type': 'flow_params_override',
            'mod_data': {'flow_params': {'exclude_codes': '404_rps'}},
        },
    )
    assert response.status_code == 200
    response_json = response.json()
    assert 'mod_id' in response_json
    mod_id1 = response_json['mod_id']

    response = await taxi_hejmdal.put(
        '/v1/mod/update',
        headers={'X-Yandex-Login': 'login1'},
        params={'mod_id': mod_id1},
        json={
            'mod_type': 'flow_params_override',
            'mod_data': {'flow_params': {'exclude_codes': '403_rps'}},
        },
    )
    assert response.status_code == 200
    response_json = response.json()
    assert 'mod_id' in response_json
    mod_id2 = response_json['mod_id']
    assert 'updated' in response_json
    updated2 = response_json['updated']

    assert mod_id1 == mod_id2

    response = await taxi_hejmdal.post(
        '/v1/mod/retrieve', params={'mod_id': mod_id1},
    )
    assert response.status_code == 200
    assert response.json() == {
        'mod_id': mod_id1,
        'login': 'login1',
        'updated': updated2,
        'ticket': 'SOMETICKET',
        'spec_template_id': 'spec_template_id1',
        'apply_when': 'always',
        'service_id': 1,
        'service_name': 'test_service (nanny, test_project)',
        'env_type': 'stable',
        'mod_type': 'flow_params_override',
        'mod_data': {'flow_params': {'exclude_codes': '403_rps'}},
        'usage_count': 0,
        'expired': False,
    }


async def test_parameter_suggest(taxi_hejmdal):
    response = await taxi_hejmdal.get(
        '/v1/mod/suggest', params={'parameter_name': 'apply_when'},
    )
    assert response.status_code == 200
    assert response.json() == {
        'items': [
            {
                'name': 'apply_when',
                'value': 'always',
                'description': 'Применяется всегда',
            },
            {
                'name': 'apply_when',
                'value': 'drills',
                'description': 'Применяется при учениях',
            },
            {
                'name': 'apply_when',
                'value': 'deploy',
                'description': 'Применяется при выкатке',
            },
        ],
    }

    response = await taxi_hejmdal.get(
        '/v1/mod/suggest', params={'parameter_name': 'env_type'},
    )
    assert response.status_code == 200
    assert response.json() == {
        'items': [
            {'name': 'env_type', 'value': 'stable'},
            {'name': 'env_type', 'value': 'prestable'},
            {'name': 'env_type', 'value': 'testing'},
            {'name': 'env_type', 'value': 'unstable'},
        ],
    }

    response = await taxi_hejmdal.get(
        '/v1/mod/suggest', params={'parameter_name': 'mod_type'},
    )
    assert response.status_code == 200
    assert response.json() == {
        'items': [
            {
                'name': 'mod_type',
                'value': 'spec_disable',
                'description': 'Выключение проверки',
            },
            {
                'name': 'mod_type',
                'value': 'schema_override',
                'description': 'Изменение параметров проверки',
            },
            {
                'name': 'mod_type',
                'value': 'flow_params_override',
                'description': 'Изменение параметров получения входных данных',
            },
        ],
    }

    response = await taxi_hejmdal.get(
        '/v1/mod/suggest', params={'parameter_name': 'service_name'},
    )
    assert response.status_code == 200
    assert response.json() == {
        'items': [
            {
                'description': '1',
                'name': 'service_name',
                'value': 'test_service (nanny, test_project)',
            },
            {
                'description': '2',
                'name': 'service_name',
                'value': 'test_service2 (nanny, test_project)',
            },
        ],
    }

    response = await taxi_hejmdal.get(
        '/v1/mod/suggest', params={'parameter_name': 'spec_template_id'},
    )
    assert response.status_code == 200
    assert response.json() == {
        'items': [
            {'name': 'spec_template_id', 'value': '500_low_rps_aggregation'},
            {'name': 'spec_template_id', 'value': '500_rps_low'},
            {'name': 'spec_template_id', 'value': 'bad_rps'},
            {'name': 'spec_template_id', 'value': 'bad_rps_aggregation'},
            {
                'name': 'spec_template_id',
                'value': 'experimental_aggregation_circuit::139',
            },
            {'name': 'spec_template_id', 'value': 'mongo_cpu_usage'},
            {'name': 'spec_template_id', 'value': 'mongo_disk_usage'},
            {'name': 'spec_template_id', 'value': 'mongo_mdb_cpu_low_usage'},
            {'name': 'spec_template_id', 'value': 'mongo_mdb_cpu_usage'},
            {'name': 'spec_template_id', 'value': 'mongo_mdb_disk_usage'},
        ],
    }

    response = await taxi_hejmdal.get(
        '/v1/mod/suggest', params={'parameter_name': 'fake_param'},
    )
    assert response.status_code == 404
    assert response.json() == {
        'code': '404',
        'message': 'unknown parameter_name',
    }
