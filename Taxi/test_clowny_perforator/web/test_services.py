# pylint: disable=C0302
import pytest


CREATE_SERVICE_DATA = [
    (
        'tvm_service',
        [{'tvm_id': 100, 'env_type': 'production'}],
        None,
        None,
        200,
        None,
    ),
    (
        'tvm_service',
        [
            {'tvm_id': 100, 'env_type': 'production'},
            {'tvm_id': 120, 'env_type': 'testing'},
        ],
        5,
        1,
        200,
        None,
    ),
    ('tvm_service', [], 5, 1, 200, None),
    (
        'tvm_service',
        [{'tvm_id': 100, 'env_type': 'undefined'}],
        None,
        None,
        400,
        'REQUEST_VALIDATION_ERROR',
    ),
    # existed tvm name
    (
        'existed_tvm_service',
        [{'tvm_id': 1000000, 'env_type': 'production'}],
        None,
        None,
        409,
        'service_already_exists',
    ),
]


def _make_post_tvm_services(tvm_name, environments, get_tvm_services):
    async def _post_tvm_services(body, env_type):
        tvm_services = get_tvm_services(env_type)['value']
        new_id = None
        for env in environments:
            if env['env_type'] == env_type:
                new_id = env['tvm_id']
        if new_id is not None:
            tvm_services[tvm_name] = new_id
        assert body['new_value'] == tvm_services
        assert body['old_value'] == get_tvm_services(env_type)['value']
        assert set(body.keys()) == {'new_value', 'old_value', 'reason'}

    return _post_tvm_services


def _make_delete_tvm_services(tvm_name, get_tvm_services):
    async def _post_tvm_services(body, env_type):
        tvm_services = get_tvm_services(env_type)['value']
        if tvm_name in tvm_services:
            del tvm_services[tvm_name]

        assert body['new_value'] == tvm_services
        assert body['old_value'] == get_tvm_services(env_type)['value']
        assert set(body.keys()) == {'new_value', 'old_value', 'reason'}

    return _post_tvm_services


def _make_post_tvm_rules(appended_rules, get_tvm_rules):
    async def _post_tvm_rules(body, env_type):
        tvm_rules = get_tvm_rules(env_type)['value']
        new_tvm_rules = tvm_rules + appended_rules[env_type]

        assert body['new_value'] == new_tvm_rules
        assert body['old_value'] == tvm_rules
        assert set(body.keys()) == {'new_value', 'old_value', 'reason'}

    return _post_tvm_rules


def _make_delete_tvm_rules(deleted_rules, get_tvm_rules):
    async def _post_tvm_rules(body, env_type):
        tvm_rules = get_tvm_rules(env_type)['value']
        new_tvm_rules = []
        for rule in tvm_rules:
            cache_item = (rule['src'], rule['dst'])
            if cache_item not in deleted_rules[env_type]:
                new_tvm_rules.append(rule)

        assert body['new_value'] == new_tvm_rules
        assert body['old_value'] == tvm_rules
        assert set(body.keys()) == {'new_value', 'old_value', 'reason'}

    return _post_tvm_rules


@pytest.mark.pgsql('clowny_perforator', files=['service_data.sql'])
@pytest.mark.parametrize(
    'tvm_name,environments,clown_id,project_id,status,error_code',
    CREATE_SERVICE_DATA,
)
async def test_service_create(
        web_app_client,
        tvm_name,
        environments,
        clown_id,
        project_id,
        status,
        error_code,
        cte_configs_mockserver,
        get_tvm_services,
):
    config_mock = cte_configs_mockserver(
        post_tvm_services=_make_post_tvm_services(
            tvm_name, environments, get_tvm_services,
        ),
    )

    body = {'tvm_name': tvm_name}
    if environments:
        body['environments'] = environments
    if clown_id is not None:
        body['clown_service'] = {
            'clown_id': clown_id,
            'project_id': project_id,
        }
    response = await web_app_client.post('/v1.0/services/create', json=body)
    content = await response.json()
    assert response.status == status, content
    if status != 200:
        assert content['code'] == error_code
    else:
        assert content.pop('id') > 0
        for item in content['environments']:
            assert item.pop('id') > 0
        expected = {
            'is_internal': bool(clown_id),
            'tvm_name': tvm_name,
            'environments': [
                environments[index] for index in range(len(environments))
            ],
        }
        if clown_id is not None:
            expected['clown_service'] = {
                'clown_id': clown_id,
                'project_id': project_id,
            }
        assert content == expected
        assert config_mock.times_called == len(environments) * 2


@pytest.mark.pgsql('clowny_perforator', files=['service_data.sql'])
@pytest.mark.parametrize(
    'tvm_name,environments,clown_id,project_id,status,error_code',
    CREATE_SERVICE_DATA,
)
async def test_service_create_validate(
        web_app_client,
        tvm_name,
        environments,
        clown_id,
        project_id,
        status,
        error_code,
):
    body = {'tvm_name': tvm_name}
    if environments:
        body['environments'] = environments
    if clown_id is not None:
        body['clown_service'] = {
            'clown_id': clown_id,
            'project_id': project_id,
        }
    response = await web_app_client.post(
        '/v1.0/services/create/validate', json=body,
    )
    content = await response.json()
    assert response.status == status, content
    if status != 200:
        assert content['code'] == error_code
    else:
        expected = {'data': body, 'change_doc_id': f'service_{tvm_name}'}
        assert content == expected


@pytest.mark.pgsql('clowny_perforator', files=['service_data.sql'])
@pytest.mark.parametrize(
    'tvm_name,service_id,status,error_code,times_called',
    [
        ('existed_tvm_service_3', 3, 200, None, 4),
        ('existed_tvm_service_4', 4, 200, None, 4),
        ('existed_tvm_service', 1, 400, 'linked_rules', None),
        ('existed_tvm_service_2', 2, 400, 'linked_rules', None),
        ('empty_service', 5, 200, None, 0),
        (None, 6, 404, 'not_found', None),
    ],
)
async def test_service_delete(
        web_app_client,
        tvm_name,
        service_id,
        status,
        error_code,
        times_called,
        cte_configs_mockserver,
        get_tvm_services,
):
    config_mock = cte_configs_mockserver(
        post_tvm_services=_make_delete_tvm_services(
            tvm_name, get_tvm_services,
        ),
    )

    response = await web_app_client.post(
        '/v1.0/services/delete', json={'service_id': service_id},
    )
    content = await response.json()
    assert response.status == status, content
    if status != 200:
        assert content['code'] == error_code
    else:
        assert content == {}
        assert config_mock.times_called == times_called


@pytest.mark.pgsql('clowny_perforator', files=['service_data.sql'])
@pytest.mark.parametrize(
    'tvm_name,service_id,status,clown_id,error_code',
    [
        ('existed_tvm_service_3', 3, 200, 124, None),
        ('existed_tvm_service', 1, 400, 124, 'linked_rules'),
        (None, 6, 404, 124, 'not_found'),
    ],
)
async def test_service_delete_validate(
        web_app_client, tvm_name, service_id, status, clown_id, error_code,
):
    response = await web_app_client.post(
        '/v1.0/services/delete/validate', json={'service_id': service_id},
    )
    content = await response.json()
    assert response.status == status, content
    if status != 200:
        assert content['code'] == error_code
    else:
        assert content == {
            'data': {
                'clown_id': clown_id,
                'service_id': service_id,
                'tvm_name': tvm_name,
            },
            'change_doc_id': f'service_{tvm_name}',
        }


@pytest.mark.pgsql('clowny_perforator', files=['service_data.sql'])
@pytest.mark.parametrize(
    'service_id,status,expected,error_code',
    [
        (
            1,
            200,
            {
                'id': 1,
                'is_internal': True,
                'tvm_name': 'existed_tvm_service',
                'clown_service': {'clown_id': 123, 'project_id': 1},
                'environments': [
                    {'env_type': 'production', 'tvm_id': 1002},
                    {'env_type': 'testing', 'tvm_id': 1000},
                    {'env_type': 'unstable', 'tvm_id': 1000},
                ],
            },
            None,
        ),
        (
            2,
            200,
            {
                'id': 2,
                'is_internal': False,
                'tvm_name': 'existed_tvm_service_2',
                'environments': [
                    {'env_type': 'production', 'tvm_id': 2000},
                    {'env_type': 'testing', 'tvm_id': 2002},
                ],
            },
            None,
        ),
        (
            5,
            200,
            {
                'environments': [],
                'id': 5,
                'is_internal': False,
                'tvm_name': 'empty_service',
            },
            None,
        ),
        (6, 404, {}, 'not_found'),
    ],
)
async def test_service_get(
        web_app_client, service_id, expected, status, error_code,
):
    response = await web_app_client.get(
        '/v1.0/services', params={'id': service_id},
    )
    content = await response.json()
    assert response.status == status, content
    if status != 200:
        assert content['code'] == error_code
    else:
        for item in content['environments']:
            assert item.pop('id') > 0
        assert content == expected


@pytest.mark.pgsql('clowny_perforator', files=['many_services.sql'])
@pytest.mark.parametrize(
    'data,expected_len,expected_ids',
    [
        (
            {},
            25,
            [
                1002,
                1003,
                1004,
                1005,
                1006,
                1,
                10,
                100,
                1000,
                1001,
                101,
                102,
                103,
                104,
                105,
                106,
                107,
                108,
                109,
                11,
                110,
                111,
                112,
                113,
                114,
            ],
        ),
        (
            {'search': 'isted_tvm_service_50'},
            11,
            [50, 500, 501, 502, 503, 504, 505, 506, 507, 508, 509],
        ),
        ({'clown_ids': [1, 2, 14, 15, 3, 5]}, 4, [1, 15, 3, 5]),
        (
            {
                'tvm_names': [
                    'existed_tvm_service_1',
                    'existed_tvm_service_700',
                    'existed_tvm_service_123',
                    'existed_tvm_service_5',
                    'existed_tvm_service_-1',
                ],
            },
            4,
            [1, 123, 5, 700],
        ),
        (
            {'service_ids': [500, 1500, 499, 498, 497, 496]},
            5,
            [496, 497, 498, 499, 500],
        ),
        ({'limit': 6}, 6, [1002, 1003, 1004, 1005, 1006, 1]),
        (
            {
                'service_ids': [1, 2, 3, 4, 5, 501, 502, 503, 504, 505],
                'clown_ids': [1, 2, 3, 4, 501, 502, 503, 504, 505],
                'tvm_names': [
                    'existed_tvm_service_1',
                    'existed_tvm_service_2',
                    'existed_tvm_service_3',
                    'existed_tvm_service_501',
                    'existed_tvm_service_502',
                    'existed_tvm_service_503',
                ],
                'offset': 1,
                'limit': 3,
            },
            3,
            [3, 501, 503],
        ),
        ({'search': '1001'}, 2, [1, 1001]),
    ],
)
async def test_service_retrieve(
        web_app_client, data, expected_len, expected_ids,
):
    response = await web_app_client.post('/v1.0/services/retrieve', json=data)
    content = await response.json()
    assert response.status == 200, content
    assert set(content.keys()) == {'services'}
    assert len(content['services']) == expected_len
    for index in range(expected_len):
        assert content['services'][index]['id'] == expected_ids[index]


@pytest.mark.pgsql('clowny_perforator', files=['service_data.sql'])
@pytest.mark.parametrize(
    'service_id,tvm_id,env_type,tvm_name,status,error_code',
    [
        (
            2,
            2002,
            'testing',
            'existed_tvm_service_2',
            409,
            'environment_already_exists',
        ),
        (6, 2002, 'testing', 'existed_tvm_service_2', 404, 'not_found'),
        (5, 5002, 'testing', 'empty_service', 200, None),
        (5, 5001, 'testing', 'empty_service', 400, 'configs_error'),
    ],
)
async def test_environment_create(
        web_app_client,
        service_id,
        tvm_id,
        env_type,
        tvm_name,
        status,
        error_code,
        cte_configs_mockserver,
        get_tvm_services,
):
    config_mock = cte_configs_mockserver(
        post_tvm_services=_make_post_tvm_services(
            tvm_name,
            [{'tvm_id': tvm_id, 'env_type': env_type}],
            get_tvm_services,
        ),
    )

    response = await web_app_client.post(
        '/v1.0/services/environments/create',
        json={
            'service_id': service_id,
            'env_type': env_type,
            'tvm_id': tvm_id,
        },
    )
    content = await response.json()
    assert response.status == status, content
    if status != 200:
        assert content['code'] == error_code
    else:
        assert content.pop('id') > 0
        expected = {'env_type': env_type, 'tvm_id': tvm_id}
        assert content == expected
        assert config_mock.times_called == 1


@pytest.mark.pgsql('clowny_perforator', files=['service_data.sql'])
@pytest.mark.parametrize(
    'service_id,tvm_id,env_type,tvm_name,status,error_code',
    [
        (2, 2002, 'unstable', 'existed_tvm_service_2', 200, None),
        (6, 2002, 'unstable', 'existed_tvm_service_2', 404, 'not_found'),
    ],
)
async def test_environment_create_validate(
        web_app_client,
        service_id,
        tvm_id,
        env_type,
        tvm_name,
        status,
        error_code,
):
    body = {'service_id': service_id, 'env_type': env_type, 'tvm_id': tvm_id}
    response = await web_app_client.post(
        '/v1.0/services/environments/create/validate', json=body,
    )
    content = await response.json()
    assert response.status == status, content
    if status != 200:
        assert content['code'] == error_code
    else:
        expected = {'data': body, 'change_doc_id': f'service_{tvm_name}'}
        assert content == expected


@pytest.mark.pgsql('clowny_perforator', files=['service_data.sql'])
@pytest.mark.parametrize(
    'tvm_name,env_id,status,error_code, times_called',
    [
        ('existed_tvm_service', 1, 200, None, 0),
        ('existed_tvm_service_2', 4, 200, None, 2),
        ('existed_tvm_service', 3, 400, 'linked_rules', 0),
        (None, 30, 404, 'not_found', 0),
    ],
)
async def test_environment_delete(
        web_app_client,
        tvm_name,
        env_id,
        status,
        error_code,
        cte_configs_mockserver,
        get_tvm_services,
        times_called,
):
    config_mock = cte_configs_mockserver(
        post_tvm_services=_make_delete_tvm_services(
            tvm_name, get_tvm_services,
        ),
    )

    response = await web_app_client.post(
        '/v1.0/services/environments/delete', json={'environment_id': env_id},
    )
    content = await response.json()
    assert response.status == status, content
    if status != 200:
        assert content['code'] == error_code
    else:
        assert content == {}
        assert config_mock.times_called == times_called


@pytest.mark.pgsql('clowny_perforator', files=['service_data.sql'])
@pytest.mark.parametrize(
    'tvm_name,env_id,status,error_code,doc_id,clown_id',
    [
        (
            'existed_tvm_service',
            1,
            200,
            None,
            'service_existed_tvm_service',
            123,
        ),
        ('existed_tvm_service', 3, 400, 'linked_rules', None, None),
        (None, 30, 404, 'not_found', None, None),
    ],
)
async def test_environment_delete_validate(
        web_app_client, tvm_name, env_id, status, error_code, doc_id, clown_id,
):
    body = {'clown_id': clown_id, 'environment_id': env_id}
    response = await web_app_client.post(
        '/v1.0/services/environments/delete/validate', json=body,
    )
    content = await response.json()
    assert response.status == status, content
    if status != 200:
        assert content['code'] == error_code
    else:
        assert content == {'data': body, 'change_doc_id': doc_id}


@pytest.mark.pgsql('clowny_perforator', files=['service_data.sql'])
@pytest.mark.parametrize(
    'tvm_name,env_id,env_type,tvm_id,status,error_code',
    [
        ('existed_tvm_service', 1, 'unstable', 54321, 400, 'configs_error'),
        ('existed_tvm_service_2', 4, 'production', 54321, 200, None),
        (None, 30, 'production', 54321, 404, 'not_found'),
    ],
)
async def test_environment_edit(
        web_app_client,
        tvm_name,
        env_id,
        env_type,
        tvm_id,
        status,
        error_code,
        cte_configs_mockserver,
        get_tvm_services,
):
    config_mock = cte_configs_mockserver(
        post_tvm_services=_make_post_tvm_services(
            tvm_name,
            [{'tvm_id': tvm_id, 'env_type': env_type}],
            get_tvm_services,
        ),
    )

    response = await web_app_client.post(
        '/v1.0/services/environments/edit',
        json={'environment_id': env_id, 'tvm_id': tvm_id},
    )
    content = await response.json()
    assert response.status == status, content
    if status != 200:
        assert content['code'] == error_code
    else:
        assert content == {
            'id': env_id,
            'tvm_id': tvm_id,
            'env_type': env_type,
        }
        assert config_mock.times_called == 2


@pytest.mark.pgsql('clowny_perforator', files=['service_data.sql'])
@pytest.mark.parametrize(
    'tvm_name,env_id,env_type,tvm_id,status,error_code,doc_id,clown_id',
    [
        (
            'existed_tvm_service',
            1,
            'unstable',
            54321,
            200,
            None,
            'service_existed_tvm_service',
            123,
        ),
        (None, 30, 'production', 54321, 404, 'not_found', None, None),
        pytest.param(
            None,
            1,
            'unstable',
            1000,
            409,
            'tvm_id_already_exists_in_this_environment',
            None,
            None,
            id='tvm_id exists in this environment',
        ),
        pytest.param(
            None,
            3,
            'production',
            1000,
            200,
            None,
            'service_existed_tvm_service',
            123,
            id='tvm_id exists in other environment',
        ),
    ],
)
async def test_environment_edit_validate(
        web_app_client,
        tvm_name,
        env_id,
        env_type,
        tvm_id,
        status,
        error_code,
        doc_id,
        clown_id,
):
    body = {'clown_id': clown_id, 'environment_id': env_id, 'tvm_id': tvm_id}
    response = await web_app_client.post(
        '/v1.0/services/environments/edit/validate', json=body,
    )
    content = await response.json()
    assert response.status == status, content
    if status != 200:
        assert content['code'] == error_code
    else:
        assert content == {'data': body, 'change_doc_id': doc_id}


@pytest.mark.pgsql('clowny_perforator', files=['service_data.sql'])
@pytest.mark.parametrize('is_validate', [True, False])
@pytest.mark.parametrize(
    'env_type,source,destinations,appended_rules,'
    'expected,status,error_code,is_reversed',
    [
        (
            'testing',
            'existed_tvm_service_2',
            ['existed_tvm_service', 'existed_tvm_service_2'],
            [
                ('existed_tvm_service_2', 'existed_tvm_service'),
                ('existed_tvm_service_2', 'existed_tvm_service_2'),
            ],
            [
                {
                    'destination_tvm_name': 'existed_tvm_service',
                    'source_tvm_name': 'existed_tvm_service_2',
                },
                {
                    'destination_tvm_name': 'existed_tvm_service_2',
                    'source_tvm_name': 'existed_tvm_service_2',
                },
            ],
            200,
            None,
            False,
        ),
        (
            'production',
            'existed_tvm_service_2',
            ['existed_tvm_service', 'existed_tvm_service_2'],
            [
                ('existed_tvm_service_2', 'existed_tvm_service'),
                ('existed_tvm_service_2', 'existed_tvm_service_2'),
            ],
            [
                {
                    'destination_tvm_name': 'existed_tvm_service',
                    'source_tvm_name': 'existed_tvm_service_2',
                },
                {
                    'destination_tvm_name': 'existed_tvm_service_2',
                    'source_tvm_name': 'existed_tvm_service_2',
                },
            ],
            200,
            None,
            False,
        ),
        (
            'unstable',
            'existed_tvm_service_2',
            ['existed_tvm_service_2', 'existed_tvm_service'],
            [],
            [],
            404,
            'not_found',
            False,
        ),
        (
            'production',
            'non_existed_tvm_service_2',
            ['non_existed_tvm_service'],
            [],
            [],
            404,
            'not_found',
            False,
        ),
        (
            'testing',
            'existed_tvm_service_2',
            ['existed_tvm_service', 'existed_tvm_service_2'],
            [('existed_tvm_service_2', 'existed_tvm_service_2')],
            [
                {
                    'destination_tvm_name': 'existed_tvm_service_2',
                    'source_tvm_name': 'existed_tvm_service_2',
                },
            ],
            200,
            None,
            True,
        ),
        (
            'production',
            'non_existed_tvm_service_2',
            ['non_existed_tvm_service'],
            [],
            [],
            404,
            'not_found',
            True,
        ),
    ],
)
async def test_environments_rules_create(
        web_app_client,
        env_type,
        source,
        destinations,
        appended_rules,
        expected,
        status,
        error_code,
        is_validate,
        cte_configs_mockserver,
        get_tvm_rules,
        is_reversed,
):
    if is_validate:
        await _test_environments_rules_create(
            source,
            destinations,
            appended_rules,
            cte_configs_mockserver,
            env_type,
            web_app_client,
            status,
            expected,
            error_code,
            get_tvm_rules,
            is_reversed,
        )
    else:
        await _test_environments_rules_create_validate(
            source,
            destinations,
            env_type,
            web_app_client,
            status,
            error_code,
            is_reversed,
        )


async def _test_environments_rules_create(
        source,
        destinations,
        appended_rules,
        cte_configs_mockserver,
        env_type,
        web_app_client,
        status,
        expected,
        error_code,
        get_tvm_rules,
        is_reversed,
):
    appended_rules_formatted = [
        {'src': rule[0], 'dst': rule[1]} for rule in appended_rules
    ]
    config_mock = cte_configs_mockserver(
        post_tvm_rules=_make_post_tvm_rules(
            {env_type: appended_rules_formatted}, get_tvm_rules,
        ),
    )

    body = {
        'source': source,
        'destinations': destinations,
        'env_type': env_type,
    }
    handler_name = '/v1.0/services/environments/rules/create'
    if is_reversed:
        body = {
            'destination': source,
            'sources': destinations,
            'env_type': env_type,
        }
        handler_name = '/v1.0/services/environments/rules/destination/create'
    response = await web_app_client.post(handler_name, json=body)
    content = await response.json()
    assert response.status == status, content
    if status != 200:
        assert content['code'] == error_code
    else:
        created_rules = content['created_rules']
        _assert_environments_rules(created_rules, expected, env_type)
        assert config_mock.times_called == 2


async def _test_environments_rules_create_validate(
        source,
        destinations,
        env_type,
        web_app_client,
        status,
        error_code,
        is_reversed,
):
    handler_name = '/v1.0/services/environments/rules/create/validate'
    body = {
        'source': source,
        'destinations': destinations,
        'env_type': env_type,
    }
    if is_reversed:
        handler_name = (
            '/v1.0/services/environments/rules/destination/create/validate'
        )
        body = {
            'destination': source,
            'sources': destinations,
            'env_type': env_type,
        }
    response = await web_app_client.post(handler_name, json=body)
    content = await response.json()
    assert response.status == status, content
    if status != 200:
        assert content['code'] == error_code
    else:
        assert content == {'data': body, 'change_doc_id': f'service_{source}'}


@pytest.mark.pgsql('clowny_perforator', files=['service_data.sql'])
@pytest.mark.parametrize('is_validate', [True, False])
@pytest.mark.parametrize(
    'source,destinations,appended_rules,'
    'expected,status,error_code,is_reversed,clown_id',
    [
        (
            'existed_tvm_service_3',
            ['existed_tvm_service'],
            {
                'production': [
                    {
                        'src': 'existed_tvm_service_3',
                        'dst': 'existed_tvm_service',
                    },
                ],
                'testing': [
                    {
                        'src': 'existed_tvm_service_3',
                        'dst': 'existed_tvm_service',
                    },
                ],
            },
            [
                {
                    'destination_tvm_name': 'existed_tvm_service',
                    'source_tvm_name': 'existed_tvm_service_3',
                    'env_type': 'production',
                },
                {
                    'destination_tvm_name': 'existed_tvm_service',
                    'source_tvm_name': 'existed_tvm_service_3',
                    'env_type': 'testing',
                },
            ],
            200,
            None,
            False,
            124,
        ),
        (
            'non_existed_tvm_service_2',
            ['non_existed_tvm_service'],
            [],
            [],
            404,
            'not_found',
            False,
            None,
        ),
        (
            'existed_tvm_service_3',
            ['existed_tvm_service'],
            {
                'production': [
                    {
                        'src': 'existed_tvm_service',
                        'dst': 'existed_tvm_service_3',
                    },
                ],
                'testing': [
                    {
                        'src': 'existed_tvm_service',
                        'dst': 'existed_tvm_service_3',
                    },
                ],
            },
            [
                {
                    'destination_tvm_name': 'existed_tvm_service_3',
                    'source_tvm_name': 'existed_tvm_service',
                    'env_type': 'production',
                },
                {
                    'destination_tvm_name': 'existed_tvm_service_3',
                    'source_tvm_name': 'existed_tvm_service',
                    'env_type': 'testing',
                },
            ],
            200,
            None,
            True,
            124,
        ),
        (
            'non_existed_tvm_service_2',
            ['non_existed_tvm_service'],
            [],
            [],
            404,
            'not_found',
            True,
            None,
        ),
    ],
)
async def test_rules_create(
        web_app_client,
        source,
        destinations,
        appended_rules,
        expected,
        status,
        error_code,
        is_validate,
        cte_configs_mockserver,
        get_tvm_rules,
        is_reversed,
        clown_id,
):
    if is_validate:
        await _test_rules_create(
            cte_configs_mockserver,
            web_app_client,
            source,
            destinations,
            appended_rules,
            status,
            error_code,
            expected,
            get_tvm_rules,
            is_reversed,
        )
    else:
        await _test_rules_create_validate(
            web_app_client,
            source,
            destinations,
            status,
            error_code,
            is_reversed,
            clown_id,
        )


async def _test_rules_create(
        cte_configs_mockserver,
        web_app_client,
        source,
        destinations,
        appended_rules,
        status,
        error_code,
        expected,
        get_tvm_rules,
        is_reversed,
):
    config_mock = cte_configs_mockserver(
        post_tvm_rules=_make_post_tvm_rules(appended_rules, get_tvm_rules),
    )
    body = {'source': source, 'destinations': destinations}
    handler_name = '/v1.0/services/rules/create'
    if is_reversed:
        body = {'destination': source, 'sources': destinations}
        handler_name = '/v1.0/services/rules/destination/create'
    response = await web_app_client.post(handler_name, json=body)
    content = await response.json()
    assert response.status == status, content
    if status != 200:
        assert content['code'] == error_code
    else:
        created_rules = content['created_rules']
        _assert_services_rules(
            created_rules, config_mock, appended_rules, expected,
        )


async def _test_rules_create_validate(
        web_app_client,
        source,
        destinations,
        status,
        error_code,
        is_reversed,
        clown_id,
):
    body = {
        'source': source,
        'destinations': destinations,
        'clown_id': clown_id,
    }
    handler_name = '/v1.0/services/rules/create/validate'
    if is_reversed:
        body = {
            'destination': source,
            'sources': destinations,
            'clown_id': clown_id,
        }
        handler_name = '/v1.0/services/rules/destination/create/validate'
    response = await web_app_client.post(handler_name, json=body)
    content = await response.json()
    assert response.status == status, content
    if status != 200:
        assert content['code'] == error_code
    else:
        assert content == {'data': body, 'change_doc_id': f'service_{source}'}


@pytest.mark.pgsql('clowny_perforator', files=['service_data.sql'])
@pytest.mark.parametrize('is_validate', [True, False])
@pytest.mark.parametrize(
    'env_type,source,destinations,expected,status,error_code,'
    'is_reversed,clown_id',
    [
        (
            'testing',
            'existed_tvm_service',
            ['existed_tvm_service', 'existed_tvm_service_2'],
            [
                {
                    'destination_tvm_name': 'existed_tvm_service_2',
                    'source_tvm_name': 'existed_tvm_service',
                },
            ],
            200,
            None,
            False,
            123,
        ),
        (
            'production',
            'existed_tvm_service',
            ['existed_tvm_service', 'existed_tvm_service_2'],
            [
                {
                    'destination_tvm_name': 'existed_tvm_service',
                    'source_tvm_name': 'existed_tvm_service',
                },
            ],
            200,
            None,
            False,
            123,
        ),
        (
            'production',
            'non_existed_tvm_service_2',
            ['non_existed_tvm_service'],
            [],
            404,
            'not_found',
            False,
            None,
        ),
        (
            'unstable',
            'existed_tvm_service_2',
            ['existed_tvm_service', 'existed_tvm_service_2'],
            [],
            404,
            'not_found',
            False,
            None,
        ),
        (
            'production',
            'existed_tvm_service',
            ['existed_tvm_service', 'existed_tvm_service_2'],
            [
                {
                    'destination_tvm_name': 'existed_tvm_service',
                    'source_tvm_name': 'existed_tvm_service',
                },
            ],
            200,
            None,
            True,
            123,
        ),
        (
            'production',
            'non_existed_tvm_service_2',
            ['non_existed_tvm_service'],
            [],
            404,
            'not_found',
            True,
            None,
        ),
    ],
)
async def test_environments_rules_delete(
        web_app_client,
        env_type,
        source,
        destinations,
        expected,
        status,
        error_code,
        is_validate,
        cte_configs_mockserver,
        get_tvm_rules,
        is_reversed,
        clown_id,
):
    if is_validate:
        await _test_environments_rules_delete(
            source,
            destinations,
            cte_configs_mockserver,
            web_app_client,
            env_type,
            expected,
            status,
            error_code,
            get_tvm_rules,
            is_reversed,
        )
    else:
        await _test_environments_rules_delete_validate(
            source,
            destinations,
            web_app_client,
            env_type,
            status,
            error_code,
            is_reversed,
            clown_id,
        )


async def _test_environments_rules_delete(
        source,
        destinations,
        cte_configs_mockserver,
        web_app_client,
        env_type,
        expected,
        status,
        error_code,
        get_tvm_rules,
        is_reversed,
):
    deleted_rules = [
        (rule['source_tvm_name'], rule['destination_tvm_name'])
        for rule in expected
    ]
    config_mock = cte_configs_mockserver(
        post_tvm_rules=_make_delete_tvm_rules(
            {env_type: deleted_rules}, get_tvm_rules,
        ),
    )
    body = {
        'source': source,
        'destinations': destinations,
        'env_type': env_type,
    }
    handler_name = '/v1.0/services/environments/rules/delete'
    if is_reversed:
        body = {
            'destination': source,
            'sources': destinations,
            'env_type': env_type,
        }
        handler_name = '/v1.0/services/environments/rules/destination/delete'
    response = await web_app_client.post(handler_name, json=body)
    content = await response.json()
    assert response.status == status, content
    if status != 200:
        assert content['code'] == error_code
    else:
        deleted_rules = content['deleted_rules']
        _assert_environments_rules(deleted_rules, expected, env_type)
        assert config_mock.times_called == 2


async def _test_environments_rules_delete_validate(
        source,
        destinations,
        web_app_client,
        env_type,
        status,
        error_code,
        is_reversed,
        clown_id,
):
    body = {
        'source': source,
        'destinations': destinations,
        'env_type': env_type,
        'clown_id': clown_id,
    }
    handler_name = '/v1.0/services/environments/rules/delete/validate'
    if is_reversed:
        body = {
            'destination': source,
            'sources': destinations,
            'env_type': env_type,
            'clown_id': clown_id,
        }
        handler_name = (
            '/v1.0/services/environments/rules/destination/delete/validate'
        )
    response = await web_app_client.post(handler_name, json=body)
    content = await response.json()
    assert response.status == status, content
    if status != 200:
        assert content['code'] == error_code
    else:
        assert content == {'data': body, 'change_doc_id': f'service_{source}'}


@pytest.mark.pgsql('clowny_perforator', files=['service_data.sql'])
@pytest.mark.parametrize('is_validate', [True, False])
@pytest.mark.parametrize(
    'source,destinations,expected,status,error_code,is_reversed,clown_id',
    [
        (
            'existed_tvm_service',
            ['existed_tvm_service', 'existed_tvm_service_2'],
            [
                {
                    'destination_tvm_name': 'existed_tvm_service',
                    'source_tvm_name': 'existed_tvm_service',
                    'env_type': 'production',
                },
                {
                    'destination_tvm_name': 'existed_tvm_service_2',
                    'source_tvm_name': 'existed_tvm_service',
                    'env_type': 'testing',
                },
            ],
            200,
            None,
            False,
            123,
        ),
        (
            'non_existed_tvm_service_2',
            ['non_existed_tvm_service_2', 'non_existed_tvm_service'],
            [],
            404,
            'not_found',
            False,
            None,
        ),
        (
            'existed_tvm_service',
            ['existed_tvm_service', 'existed_tvm_service_2'],
            [
                {
                    'destination_tvm_name': 'existed_tvm_service',
                    'source_tvm_name': 'existed_tvm_service',
                    'env_type': 'production',
                },
            ],
            200,
            None,
            True,
            123,
        ),
        (
            'non_existed_tvm_service_2',
            ['non_existed_tvm_service_2', 'non_existed_tvm_service'],
            [],
            404,
            'not_found',
            True,
            None,
        ),
    ],
)
async def test_rules_delete(
        web_app_client,
        source,
        destinations,
        expected,
        status,
        error_code,
        is_validate,
        cte_configs_mockserver,
        get_tvm_rules,
        is_reversed,
        clown_id,
):
    if is_validate:
        await _test_rules_delete(
            cte_configs_mockserver,
            web_app_client,
            source,
            destinations,
            expected,
            status,
            error_code,
            get_tvm_rules,
            is_reversed,
        )
    else:
        await _test_rules_delete_validate(
            web_app_client,
            source,
            destinations,
            status,
            error_code,
            is_reversed,
            clown_id,
        )


async def _test_rules_delete(
        cte_configs_mockserver,
        web_app_client,
        source,
        destinations,
        expected,
        status,
        error_code,
        get_tvm_rules,
        is_reversed,
):
    rules_to_delete = {}
    for rule in expected:
        cache_rule = (rule['source_tvm_name'], rule['destination_tvm_name'])
        rules_to_delete.setdefault(rule['env_type'], []).append(cache_rule)

    config_mock = cte_configs_mockserver(
        post_tvm_rules=_make_delete_tvm_rules(rules_to_delete, get_tvm_rules),
    )

    handler_name = '/v1.0/services/rules/delete'
    body = {'source': source, 'destinations': destinations}
    if is_reversed:
        handler_name = '/v1.0/services/rules/destination/delete'
        body = {'destination': source, 'sources': destinations}
    response = await web_app_client.post(handler_name, json=body)
    content = await response.json()
    assert response.status == status, content
    if status != 200:
        assert content['code'] == error_code
    else:
        deleted_rules = content['deleted_rules']
        _assert_services_rules(
            deleted_rules, config_mock, rules_to_delete, expected,
        )


async def _test_rules_delete_validate(
        web_app_client,
        source,
        destinations,
        status,
        error_code,
        is_reversed,
        clown_id,
):
    body = {
        'source': source,
        'destinations': destinations,
        'clown_id': clown_id,
    }
    handler_name = '/v1.0/services/rules/delete/validate'
    if is_reversed:
        body = {
            'destination': source,
            'sources': destinations,
            'clown_id': clown_id,
        }
        handler_name = '/v1.0/services/rules/destination/delete/validate'
    response = await web_app_client.post(handler_name, json=body)
    content = await response.json()
    assert response.status == status, content
    if status != 200:
        assert content['code'] == error_code
    else:
        assert content == {'data': body, 'change_doc_id': f'service_{source}'}


@pytest.mark.pgsql('clowny_perforator', files=['many_services.sql'])
@pytest.mark.parametrize(
    'data,expected_len',
    [
        ({}, 25),
        ({'rule_ids': [-1, 5, 10]}, 2),
        ({'source_tvm_name': 'existed_tvm_service_10'}, 3),
        ({'source_tvm_name': 'existed_tvm_service_-1'}, 0),
        ({'destination_tvm_name': 'existed_tvm_service_10'}, 3),
        ({'env_type': 'production', 'limit': 50}, 50),
        (
            {
                'env_type': 'production',
                'limit': 50,
                'destination_tvm_name': 'existed_tvm_service_10',
            },
            1,
        ),
        (
            {
                'env_type': 'production',
                'limit': 50,
                'source_tvm_name': 'existed_tvm_service_7',
                'destination_tvm_name': 'existed_tvm_service_10',
            },
            1,
        ),
        (
            {
                'env_type': 'production',
                'limit': 50,
                'source_tvm_name': 'existed_tvm_service_6',
                'destination_tvm_name': 'existed_tvm_service_10',
            },
            0,
        ),
        ({'offset': 0}, 25),
    ],
)
async def test_rules_retrieve(web_app_client, data, expected_len):
    response = await web_app_client.post(
        '/v1.0/services/rules/retrieve', json=data,
    )
    content = await response.json()
    assert response.status == 200, content
    assert set(content.keys()) == {'rules'}
    assert len(content['rules']) == expected_len


def _assert_environments_rules(rules, expected, env_type):
    for item in rules:
        assert item.pop('rule_id') > 0
        assert item.pop('env_type') == env_type
    assert len(rules) == len(expected)
    for item, expected_item in zip(rules, expected):
        assert item['source']['tvm_name'] == expected_item['source_tvm_name']
        assert (
            item['destination']['tvm_name']
            == expected_item['destination_tvm_name']
        )


def _assert_services_rules(rules, config_mock, changed_rules, expected):
    for item in rules:
        assert item.pop('rule_id') > 0
    assert len(rules) == len(expected)
    for item, expected_item in zip(rules, expected):
        assert item['env_type'] == expected_item['env_type']
        assert item['source']['tvm_name'] == expected_item['source_tvm_name']
        assert (
            item['destination']['tvm_name']
            == expected_item['destination_tvm_name']
        )
    assert config_mock.times_called == 2 * len(changed_rules.keys())
