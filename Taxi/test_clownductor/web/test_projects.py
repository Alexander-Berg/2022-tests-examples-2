import pytest


@pytest.mark.pgsql('clownductor')
async def test_projects_add(web_app_client, login_mockserver, add_namespace):
    login_mockserver()
    namespace = await add_namespace('taxi')
    response = await web_app_client.post(
        '/api/projects',
        json={
            'name': 'taxi',
            'network_testing': '_TEST_NET_',
            'network_stable': '_STABLE_NET_',
            'service_abc': 'someserviceabcslug',
            'yp_quota_abc': 'slugwithqouta',
            'tvm_root_abc': 'tvmtvmtvm',
            'owners': {'logins': ['karachevda'], 'groups': []},
            'approving_devs': {'logins': ['damsker'], 'cgroups': [123, 456]},
            'env_params': {
                'stable': {
                    'domain': 'taxi.yandex.net',
                    'juggler_folder': 'taxi.prod',
                },
                'testing': {
                    'domain': 'taxi.tst.yandex.net',
                    'juggler_folder': 'taxi.test',
                },
                'unstable': {
                    'domain': 'taxi.dev.yandex.net',
                    'juggler_folder': 'taxi.unst',
                },
                'general': {
                    'project_prefix': 'taxi',
                    'docker_image_tpl': 'taxi/{{ service }}/$',
                },
            },
            'responsible_team': {
                'ops': ['yandex_distproducts_browserdev_mobile_taxi_mnt'],
                'developers': [],
                'managers': [],
                'superusers': ['isharov', 'nikslim'],
            },
            'yt_topic': {
                'path': 'taxi/taxi-access-log',
                'permissions': ['WriteTopic'],
            },
            'pgaas_root_abc': 'pgaassomeserviceabcslug',
            'namespace_id': namespace['id'],
        },
        headers={'Authorization': 'OAuth valid_oauth'},
    )
    assert response.status == 200
    data = await response.json()
    assert isinstance(data['id'], int)


@pytest.mark.pgsql('clownductor')
async def test_projects_add_conflict(
        web_app_client, login_mockserver, add_namespace,
):
    login_mockserver()
    namespace = await add_namespace('taxi')
    response = await web_app_client.post(
        '/api/projects',
        json={
            'name': 'taxi',
            'network_testing': '_TEST_NET_',
            'network_stable': '_STABLE_NET_',
            'service_abc': 'someserviceabcslug',
            'yp_quota_abc': 'slugwithqouta',
            'tvm_root_abc': 'tvmtvmtvm',
            'env_params': {
                'stable': {
                    'domain': 'taxi.yandex.net',
                    'juggler_folder': 'taxi.prod',
                },
                'testing': {
                    'domain': 'taxi.tst.yandex.net',
                    'juggler_folder': 'taxi.test',
                },
                'unstable': {
                    'domain': 'taxi.dev.yandex.net',
                    'juggler_folder': 'taxi.unst',
                },
                'general': {
                    'project_prefix': 'taxi',
                    'docker_image_tpl': 'taxi/{{ service }}/$',
                },
            },
            'pgaas_root_abc': 'pgaassomeserviceabcslug',
            'namespace_id': namespace['id'],
        },
        headers={'Authorization': 'OAuth valid_oauth'},
    )
    assert response.status == 200
    response = await web_app_client.post(
        '/api/projects',
        json={
            'name': 'taxi',
            'network_testing': '_TEST_NET_',
            'network_stable': '_STABLE_NET_',
            'service_abc': 'someserviceabcslug',
            'yp_quota_abc': 'slugwithqouta',
            'tvm_root_abc': 'tvmtvmtvm',
            'env_params': {
                'stable': {
                    'domain': 'taxi.yandex.net',
                    'juggler_folder': 'taxi.prod',
                },
                'testing': {
                    'domain': 'taxi.tst.yandex.net',
                    'juggler_folder': 'taxi.test',
                },
                'unstable': {
                    'domain': 'taxi.dev.yandex.net',
                    'juggler_folder': 'taxi.unst',
                },
                'general': {
                    'project_prefix': 'taxi',
                    'docker_image_tpl': 'taxi/{{ service }}/$',
                },
            },
            'pgaas_root_abc': 'pgaassomeserviceabcslug',
            'namespace_id': namespace['id'],
        },
        headers={'Authorization': 'OAuth valid_oauth'},
    )
    assert response.status == 409


@pytest.mark.pgsql('clownductor')
async def test_projects_get_all(web_app_client, login_mockserver, add_project):
    login_mockserver()
    projects = ['taxi', 'taximeter', 'eda']
    for project in projects:
        await add_project(project)

    response = await web_app_client.get(
        '/api/projects', headers={'Authorization': 'OAuth valid_oauth'},
    )
    assert response.status == 200
    content = await response.json()

    assert isinstance(content, list)
    assert len(content) == len(projects)


@pytest.mark.pgsql('clownductor')
async def test_projects_with_filter(
        web_app_client, login_mockserver, add_project,
):
    login_mockserver()
    taxi_project = await add_project('taxi')
    await add_project('taximeter')

    response = await web_app_client.get(
        '/api/projects',
        params={'name': 'taxi'},
        headers={'Authorization': 'OAuth valid_oauth'},
    )
    assert response.status == 200
    content = await response.json()

    assert isinstance(content, list)
    assert len(content) == 1
    assert content[0]['id'] == taxi_project['id']
    assert content[0]['name'] == 'taxi'
    assert content[0]['network_testing'] == '_TEST_NET_'
    assert content[0]['network_stable'] == '_STABLE_NET_'
    assert content[0]['service_abc'] == 'someserviceabcslug'
    assert content[0]['yp_quota_abc'] == 'slugwithqouta'
    assert content[0]['tvm_root_abc'] == 'tvmtvmtvm'
    assert content[0]['owners'] == {
        'logins': ['test_login1', 'test_login2'],
        'groups': ['test_group'],
    }
    assert content[0]['approving_managers'] == {
        'logins': ['damsker'],
        'cgroups': [123, 456],
    }
    assert content[0]['approving_devs'] == {
        'logins': ['abcdefg'],
        'cgroups': [246, 123],
    }
    assert content[0]['env_params'] == {
        'stable': {'domain': 'taxi.pytest', 'juggler_folder': 'taxi.prod'},
        'testing': {
            'domain': 'taxi.tst.pytest',
            'juggler_folder': 'taxi.test',
        },
        'unstable': {
            'domain': 'taxi.dev.pytest',
            'juggler_folder': 'taxi.unst',
        },
        'general': {
            'project_prefix': 'taxi',
            'docker_image_tpl': 'taxi/{{ service }}/$',
        },
    }
    assert content[0]['responsible_team'] == {
        'ops': ['yandex_distproducts_browserdev_mobile_taxi_mnt'],
        'developers': [],
        'managers': [],
        'superusers': ['isharov', 'nikslim'],
    }
    assert content[0]['yt_topic'] == {
        'path': 'taxi/taxi-access-log',
        'permissions': ['WriteTopic'],
    }
    assert content[0]['namespace_id'] == 1


@pytest.mark.parametrize('handler', ['/v1/projects'])
@pytest.mark.pgsql('clownductor')
async def test_projects_get_by_namespace(
        web_app_client, handler, login_mockserver, add_project, add_namespace,
):
    login_mockserver()
    projects_namespaces = [('taxi', 'taxi'), ('lavka_frontend', 'lavka')]
    for project_name, namespace_name in projects_namespaces:
        namespace = await add_namespace(namespace_name)
        await add_project(project_name, namespace['id'])

    for project_name, namespace_name in projects_namespaces:
        response = await web_app_client.get(
            handler,
            params={'tplatform_namespace': namespace_name},
            headers={'Authorization': 'OAuth valid_oauth'},
        )
        assert response.status == 200
        project_data = await response.json()
        projects_names = [pd['name'] for pd in project_data]
        assert project_name in projects_names and len(projects_names) == 1


@pytest.mark.parametrize('handler', ['/api/projects', '/v1/projects'])
@pytest.mark.parametrize(
    'filters', [{'project_id': 1}, {'namespace': 'taxi'}, {'name': 'taxi'}],
)
async def test_projects_get_not_found(web_app_client, handler, filters):
    # Since we do not add any projects during the test
    # the response should be empty
    response = await web_app_client.get(
        handler,
        params=filters,
        headers={'Authorization': 'OAuth valid_oauth'},
    )
    assert response.status == 200
    assert (await response.json()) == []


@pytest.mark.pgsql('clownductor')
async def test_project_with_bad_name(
        web_app_client, login_mockserver, add_project,
):
    login_mockserver()
    response = await web_app_client.post(
        '/api/projects',
        json={'name': 'really bad name!'},
        headers={'Authorization': 'OAuth valid_oauth'},
    )
    assert response.status == 400
