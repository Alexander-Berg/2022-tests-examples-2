import pytest

TRANSLATIONS = {
    'clowny-balancer.enable_dc_local.ticket.summary': {
        'ru': (
            'Включение режима локализации трафика в ДЦ (режима dc-local) '
            'для сервиса {service_name}.'
        ),
    },
    'clowny-balancer.enable_dc_local.ticket.description': {
        'ru': (
            'Тикет для включения режима локализации трафика в ДЦ '
            '(режима dc-local) для сервиса service-31.\n\n'
            'Ссылка на сервис в админке:\n'
            'https://tariff-editor.taxi.yandex-team.ru/'
            'services/150/edit/31/info\n\n'
            'Ссылка на неймспейс:\n'
            'https://nanny.yandex-team.ru/ui/#/awacs/'
            'namespaces/list/taxi-service-31/show\n\n'
            'Дежурные групп эксплуатации и разработки общих инструментов '
            'будут оповещены для подключения создаваемого апстрима в домен '
            'и переключения режима маршрутизации для энтрипоинта '
            'с идентификатором 41.\n\n'
            'Внимание! При работе сервиса в режиме dc-local на данный момент '
            'существует риск того, что при смене ДЦ '
            '(ручной или автоматической) в новые ДЦ '
            'не начнёт поступать трафик!'
        ),
    },
    'clowny-balancer.enable_dc_local.draft.description': {
        'ru': (
            'Внимание! При работе сервиса в режиме dc-local на данный момент '
            'существует риск того, что при смене ДЦ '
            '(ручной или автоматической) в новые ДЦ '
            'не начнёт поступать трафик!'
        ),
    },
}


@pytest.mark.config(
    CLOWNDUCTOR_AVAILABLE_DATACENTERS={
        'all_datacenters': ['vla', 'man', 'sas', 'iva', 'myt'],
        'projects': [
            {'datacenters': ['sas', 'vla', 'myt'], 'name': 'taxi-devops'},
            {'datacenters': ['sas', 'vla', 'myt'], 'name': '__default__'},
        ],
    },
)
@pytest.mark.translations(clownductor=TRANSLATIONS)
@pytest.mark.parametrize('use_drafts', [True, False])
@pytest.mark.parametrize(
    'data, expected_status, expected_result',
    [
        pytest.param({'entry_point_id': 41}, 200, {'job_id': 1}, id='ok'),
        pytest.param(
            {'entry_point_id': 42},
            404,
            {
                'code': 'NOT_FOUND',
                'message': 'Entry point with id 42 not found',
            },
            id='entry_point_not_found',
        ),
        pytest.param(
            {'entry_point_id': 43},
            404,
            {'code': 'NOT_FOUND', 'message': 'Service with id 33 not found'},
            id='service_not_found',
        ),
        pytest.param(
            {'entry_point_id': 44},
            404,
            {
                'code': 'NOT_FOUND',
                'message': 'Stable branch for service with id 34 not found',
            },
            id='branch_not_found',
        ),
        pytest.param(
            {'entry_point_id': 45},
            400,
            {
                'code': 'REQUEST_ERROR',
                'message': (
                    'Number of datacenters with prestable pods '
                    'for service with id 35 is more than one'
                ),
            },
            id='more_than_one_dc_with_prestable_pods',
        ),
        pytest.param(
            {'entry_point_id': 46},
            400,
            {
                'code': 'REQUEST_ERROR',
                'message': (
                    'Numbers of pods by region '
                    'for service with id 36 are not equal'
                ),
            },
            id='different_numbers_of_pods_by_region',
        ),
    ],
)
@pytest.mark.pgsql('clowny_balancer', files=['init.sql'])
async def test_dc_local_enable(
        mock_clownductor,
        mockserver,
        mock_task_processor_start_job,
        taxi_clowny_balancer_web,
        use_drafts,
        data,
        expected_status,
        expected_result,
        load_json,
):
    @mock_clownductor('/v1/services/')
    def _services_handler(request):
        services = [
            {
                'id': 31,
                'project_id': 150,
                'name': 'service-31',
                'cluster_type': 'nanny',
                'project_name': 'taxi-devops',
            },
            {
                'id': 34,
                'project_id': 150,
                'name': 'service-34',
                'cluster_type': 'nanny',
                'project_name': 'taxi-devops',
            },
            {
                'id': 35,
                'project_id': 150,
                'name': 'service-35',
                'cluster_type': 'nanny',
                'project_name': 'taxi-devops',
            },
            {
                'id': 36,
                'project_id': 150,
                'name': 'service-36',
                'cluster_type': 'nanny',
                'project_name': 'taxi-devops',
            },
        ]
        if request.query.get('service_id'):
            return [
                service
                for service in services
                if str(service['id']) == request.query['service_id']
            ]
        return []

    @mock_clownductor('/v1/branches/')
    def _branches_handler(request):
        branches = [
            {
                'id': 1,
                'env': 'stable',
                'direct_link': 'taxi_service-31_stable',
                'service_id': 31,
                'name': 'stable',
            },
            {
                'id': 2,
                'env': 'prestable',
                'direct_link': 'taxi_service-31_pre_stable',
                'service_id': 31,
                'name': 'pre_stable',
            },
            {
                'id': 3,
                'env': 'stable',
                'direct_link': 'taxi_service-35_stable',
                'service_id': 35,
                'name': 'stable',
            },
            {
                'id': 4,
                'env': 'prestable',
                'direct_link': 'taxi_service-35_pre_stable',
                'service_id': 35,
                'name': 'pre_stable',
            },
            {
                'id': 5,
                'env': 'stable',
                'direct_link': 'taxi_service-36_stable',
                'service_id': 36,
                'name': 'stable',
            },
            {
                'id': 6,
                'env': 'prestable',
                'direct_link': 'taxi_service-36_pre_stable',
                'service_id': 36,
                'name': 'pre_stable',
            },
        ]
        if request.query.get('service_id'):
            return [
                branch
                for branch in branches
                if str(branch['service_id']) == request.query['service_id']
            ]
        return []

    @mockserver.json_handler('/client-nanny-yp/api/yplite/pod-sets/ListPods/')
    def _get_pods(request):
        def _add_ratemask_and_state(pod):
            pod.update(
                {
                    'spec': {
                        'sysctlProperties': [
                            {
                                'name': 'net.ipv6.icmp.ratemask',
                                'value': '0,3-127',
                            },
                        ],
                    },
                    'status': {
                        'agent': {
                            'iss': {
                                'currentStates': [{'currentState': 'ACTIVE'}],
                            },
                        },
                    },
                },
            )
            return pod

        if request.json['serviceId'] == 'taxi_service-31_stable':
            if request.json['cluster'] == 'SAS':
                return {
                    'pods': [
                        _add_ratemask_and_state({}),
                        _add_ratemask_and_state({}),
                    ],
                }
            if request.json['cluster'] == 'VLA':
                return {
                    'pods': [
                        _add_ratemask_and_state({}),
                        _add_ratemask_and_state({}),
                    ],
                }
            if request.json['cluster'] == 'MYT':
                return {'pods': [_add_ratemask_and_state({})]}
        if request.json['serviceId'] == 'taxi_service-35_stable':
            if request.json['cluster'] == 'SAS':
                return {
                    'pods': [
                        _add_ratemask_and_state({}),
                        _add_ratemask_and_state({}),
                    ],
                }
            if request.json['cluster'] == 'VLA':
                return {
                    'pods': [
                        _add_ratemask_and_state({}),
                        _add_ratemask_and_state({}),
                    ],
                }
            if request.json['cluster'] == 'MYT':
                return {'pods': [_add_ratemask_and_state({})]}
        if request.json['serviceId'] == 'taxi_service-36_stable':
            if request.json['cluster'] == 'SAS':
                return {'pods': [_add_ratemask_and_state({})]}
            if request.json['cluster'] == 'VLA':
                return {'pods': [_add_ratemask_and_state({})]}
            if request.json['cluster'] == 'MYT':
                return {'pods': [_add_ratemask_and_state({})]}
        if request.json['serviceId'] == 'taxi_service-31_pre_stable':
            if request.json['cluster'] == 'MYT':
                return {'pods': [_add_ratemask_and_state({})]}
        if request.json['serviceId'] == 'taxi_service-35_pre_stable':
            if request.json['cluster'] == 'VLA':
                return {'pods': [_add_ratemask_and_state({})]}
            if request.json['cluster'] == 'MYT':
                return {'pods': [_add_ratemask_and_state({})]}
        if request.json['serviceId'] == 'taxi_service-36_pre_stable':
            if request.json['cluster'] == 'MYT':
                return {'pods': [_add_ratemask_and_state({})]}
        return {'pods': []}

    @mock_clownductor('/api/projects')
    def _projects_handler(request):
        projects = [{'id': 150, 'name': 'taxi-devops', 'namespace_id': 1}]
        if request.query.get('project_id'):
            return [
                project
                for project in projects
                if str(project['id']) == request.query['project_id']
            ]
        return []

    task_processor_mock = mock_task_processor_start_job()

    if not use_drafts:
        response = await taxi_clowny_balancer_web.post(
            '/v1/entry-points/dc-local/enable/',
            json=data,
            headers={'X-Yandex-Login': 'antonvasyuk'},
        )
        result = await response.json()
        assert response.status == expected_status, result
        if expected_result is not None:
            assert result == expected_result
        return

    response = await taxi_clowny_balancer_web.post(
        '/v1/entry-points/dc-local/enable/check/',
        json=data,
        headers={'X-Yandex-Login': 'antonvasyuk'},
    )
    result = await response.json()
    assert response.status == expected_status, result
    if expected_status != 200:
        return
    expected_check_result = load_json(
        f'check_handler_entry_point_{data["entry_point_id"]}_response.json',
    )
    assert expected_check_result == result

    response = await taxi_clowny_balancer_web.post(
        '/v1/entry-points/dc-local/enable/apply/',
        json=result['data'],
        headers={'X-Yandex-Login': 'antonvasyuk'},
    )
    result = await response.json()
    assert response.status == expected_status, result
    if expected_result is not None:
        assert result == expected_result
    assert task_processor_mock.times_called == 1
