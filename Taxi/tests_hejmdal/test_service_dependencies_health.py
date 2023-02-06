async def test_service_health_dependencies(
        taxi_hejmdal, mockserver, load_json,
):
    @mockserver.json_handler('/clowny-perforator/v1.0/services/rules/retrieve')
    async def _mock_clowny_perforator(request):
        if request.json.get('offset') == 0:
            return load_json('clowny-perforator_rules.json')
        return {'rules': []}

    related_services_response_map = {
        '1': [
            {
                'service_id': 4,
                'service_name': 'test_db1',
                'project_id': 39,
                'cluster_type': 'postgres',
                'relation_type': 'database',
            },
        ],
        '4': [
            {
                'service_id': 1,
                'service_name': 'test_service1',
                'project_id': 39,
                'cluster_type': 'nanny',
                'relation_type': 'database_consumer',
            },
        ],
    }

    @mockserver.json_handler('/clownductor/v1/service/related')
    async def _mock_clownductor_related(request):
        result = {
            'related_services': related_services_response_map.get(
                request.query['service_id'], [],
            ),
        }
        return result

    await taxi_hejmdal.run_task('services_component/invalidate')
    await taxi_hejmdal.run_task('circuit_states_cache/invalidate')
    await taxi_hejmdal.run_task('tuner/initialize')
    await taxi_hejmdal.run_task('distlock/tvm_rules_component')
    await taxi_hejmdal.invalidate_caches(
        clean_update=True, cache_names=['tvm-rules-cache'],
    )
    await taxi_hejmdal.run_task('distlock/db_deps_component')
    await taxi_hejmdal.invalidate_caches(
        clean_update=True, cache_names=['db-deps-cache'],
    )

    response = await taxi_hejmdal.post(
        '/v1/health/service-dependencies', params={'id': 1}, json={},
    )
    assert response.status_code == 200
    response_json = response.json()
    del response_json['timestamp']
    assert response_json == {
        'service_info': {
            'service_id': 1,
            'service_name': 'test_service1',
            'project_id': 39,
            'project_name': 'test_project',
            'cluster_type': 'nanny',
            'admin_page_link': (
                'https://tariff-editor.taxi.ya'
                'ndex-team.ru/services/39/edit/1/info'
            ),
            'tvm_name': 'test_service1',
        },
        # we added 3 circuit states for service_id 1,
        # but two of them should be filtered out
        # also there is 1 juggler check
        'health_stats': {
            'status': 'Warning',
            'states': {'Ok': 2, 'Warning': 1},
            'total_checks': 3,
        },
        'dependencies': {
            'outbound': [
                {
                    'service_info': {
                        'service_id': 2,
                        'service_name': 'test_service2',
                        'project_id': 39,
                        'project_name': 'test_project',
                        'cluster_type': 'nanny',
                        'admin_page_link': (
                            'https://tariff-editor.'
                            'taxi.yandex-team.ru/services/39'
                            '/edit/2/info'
                        ),
                        'tvm_name': 'test_service2',
                    },
                    'health_stats': {
                        'status': 'Critical',
                        'states': {'Critical': 1},
                        'total_checks': 1,
                    },
                },
                {
                    'service_info': {
                        'service_id': 3,
                        'service_name': 'test_service3',
                        'project_id': 39,
                        'project_name': 'test_project',
                        'cluster_type': 'nanny',
                        'admin_page_link': (
                            'https://tariff-editor.'
                            'taxi.yandex-team.ru/services'
                            '/39/edit/3/info'
                        ),
                        'tvm_name': 'test_service3',
                    },
                    'health_stats': {
                        'status': 'NoData',
                        'states': {},
                        'total_checks': 0,
                    },
                },
            ],
            'databases': [
                {
                    'service_info': {
                        'service_id': 4,
                        'service_name': 'test_db1',
                        'project_id': 39,
                        'project_name': 'test_project',
                        'cluster_type': 'postgres',
                        'admin_page_link': (
                            'https://tariff-editor.'
                            'taxi.yandex-team.ru/services'
                            '/39/edit/4/info'
                        ),
                    },
                    'health_stats': {
                        'status': 'Warning',
                        'states': {'Warning': 1},
                        'total_checks': 1,
                    },
                },
            ],
        },
        'refresh_interval_sec': 60,
    }

    response = await taxi_hejmdal.post(
        '/v1/health/service-dependencies', params={'id': 2}, json={},
    )
    assert response.status_code == 200
    response_json = response.json()
    del response_json['timestamp']
    assert response_json == {
        'service_info': {
            'service_id': 2,
            'service_name': 'test_service2',
            'project_id': 39,
            'project_name': 'test_project',
            'cluster_type': 'nanny',
            'admin_page_link': (
                'https://tariff-editor.taxi.'
                'yandex-team.ru/services/39/'
                'edit/2/info'
            ),
            'tvm_name': 'test_service2',
        },
        'health_stats': {
            'status': 'Critical',
            'states': {'Critical': 1},
            'total_checks': 1,
        },
        'dependencies': {
            'inbound': [
                {
                    'service_info': {
                        'service_id': 1,
                        'service_name': 'test_service1',
                        'project_id': 39,
                        'project_name': 'test_project',
                        'cluster_type': 'nanny',
                        'admin_page_link': (
                            'https://tariff-editor.'
                            'taxi.yandex-team.ru/'
                            'services/39/edit/1/'
                            'info'
                        ),
                        'tvm_name': 'test_service1',
                    },
                    'health_stats': {
                        'status': 'Warning',
                        'states': {'Ok': 2, 'Warning': 1},
                        'total_checks': 3,
                    },
                },
            ],
        },
        'refresh_interval_sec': 60,
    }

    response = await taxi_hejmdal.post(
        '/v1/health/service-dependencies', params={'id': 3}, json={},
    )
    assert response.status_code == 200
    response_json = response.json()
    del response_json['timestamp']
    assert response_json == {
        'service_info': {
            'service_id': 3,
            'service_name': 'test_service3',
            'project_id': 39,
            'project_name': 'test_project',
            'cluster_type': 'nanny',
            'admin_page_link': (
                'https://tariff-editor.'
                'taxi.yandex-team.ru/'
                'services/39/edit/3/info'
            ),
            'tvm_name': 'test_service3',
        },
        'health_stats': {'status': 'NoData', 'states': {}, 'total_checks': 0},
        'dependencies': {
            'inbound': [
                {
                    'service_info': {
                        'service_id': 1,
                        'service_name': 'test_service1',
                        'project_id': 39,
                        'project_name': 'test_project',
                        'cluster_type': 'nanny',
                        'admin_page_link': (
                            'https://tariff-editor.'
                            'taxi.yandex-team.ru/'
                            'services/39/edit/1/'
                            'info'
                        ),
                        'tvm_name': 'test_service1',
                    },
                    'health_stats': {
                        'status': 'Warning',
                        'states': {'Ok': 2, 'Warning': 1},
                        'total_checks': 3,
                    },
                },
            ],
            'outbound': [{'service_info': {'tvm_name': 'external_service'}}],
        },
        'refresh_interval_sec': 60,
    }

    response = await taxi_hejmdal.post(
        '/v1/health/service-dependencies', params={'id': 4}, json={},
    )
    assert response.status_code == 200
    response_json = response.json()
    del response_json['timestamp']
    assert response_json == {
        'service_info': {
            'service_id': 4,
            'service_name': 'test_db1',
            'project_id': 39,
            'project_name': 'test_project',
            'cluster_type': 'postgres',
            'admin_page_link': (
                'https://tariff-editor.'
                'taxi.yandex-team.ru/services'
                '/39/edit/4/info'
            ),
        },
        'health_stats': {
            'status': 'Warning',
            'states': {'Warning': 1},
            'total_checks': 1,
        },
        'dependencies': {
            'inbound': [
                {
                    'service_info': {
                        'service_id': 1,
                        'service_name': 'test_service1',
                        'project_id': 39,
                        'project_name': 'test_project',
                        'cluster_type': 'nanny',
                        'admin_page_link': (
                            'https://tariff-editor.'
                            'taxi.yandex-team.ru/'
                            'services/39/edit/1/'
                            'info'
                        ),
                        'tvm_name': 'test_service1',
                    },
                    'health_stats': {
                        'status': 'Warning',
                        'states': {'Ok': 2, 'Warning': 1},
                        'total_checks': 3,
                    },
                },
            ],
        },
        'refresh_interval_sec': 60,
    }
