import pytest


TRANSLATIONS = {
    'fields.branch.id': {'ru': 'ID окружения', 'en': 'Environment id'},
    'fields.branch.name': {'ru': 'Название', 'en': 'Name'},
    'fields.branch.service_id': {'ru': 'ID сервиса', 'en': 'Service id'},
    'fields.branch.direct_link': {
        'ru': 'Ссылка на сущность',
        'en': 'Direct link',
    },
    'fields.branch.artifact_version': {'ru': 'Версия артефакта'},
    'fields.branch.env': {'ru': 'Окружение'},
    'fields.branch.configs': {'ru': 'Конфиги'},
    'fields.branch.balancer_id': {'ru': 'ID балансера'},
    'fields.branch.grafana': {'ru': 'Ссылка на графану'},
    'fields.branch.robots': {'ru': 'Логины роботов'},
    'fields.service.approvers_roles': {'ru': 'Доступные окари'},
    'fields.service.dev_approvers': {'ru': 'Разработческий ок'},
    'fields.service.approve_manager': {'ru': 'Есть ли окари от менеджеров'},
    'issues.service.service_yaml_condition.title': {
        'ru': 'Проблемы service.yaml',
    },
    'issues.service.service_yaml_condition.details': {
        'ru': (
            'На service.yaml завязаны некоторые операционные '
            'процессы поэтому важно чтобы он был в порядке'
        ),
    },
    'message.service.service_yaml_missed.title': {
        'ru': 'К сервису не привязан service.yaml',
    },
    'message.service.service_yaml_missed.details': {
        'ru': (
            'Это делает следующие действия невозможными:\n'
            ' - забрать сервис себе в дежурство\n'
            ' - получить рутовый доступ\n'
            ' - изменять автоматикой ресурсы'
        ),
    },
    'message.service.maintainer_absence.title': {
        'ru': 'В service.yaml не указаны ответственные за сервис',
    },
    'message.service.maintainer_absence.details': {
        'ru': (
            'Другим сотрудникам сложнее понять, к кому можно обратиться с '
            'вопросом/предложением по поводу сервиса'
        ),
    },
    'message.service.maintainer_dismiss.title': {
        'ru': 'Среди ответственных за сервис есть уволенные сотрудники',
    },
    'message.service.maintainer_dismiss.details': {
        'ru': 'Список уволенных сотрудников: {dismissed_maintainers}',
    },
}


@pytest.mark.parametrize(
    'branch_id, status, expected, locale',
    [
        (1, 200, 'response_branch_id_1.json', 'ru'),
        (2, 200, 'response_branch_id_2.json', 'en'),
        (55, 404, 'NOT_FOUND', 'pog'),
    ],
)
@pytest.mark.pgsql('clownductor', files=['init_db.sql'])
@pytest.mark.translations(clownductor=TRANSLATIONS)
async def test_full_info_branch(
        web_app_client, branch_id, status, expected, locale, load_json,
):
    response = await web_app_client.post(
        '/v1/branches/full_info/',
        json={'branch_id': branch_id},
        headers={'Accept-Language': locale},
    )
    assert response.status == status
    data = await response.json()
    if status == 404:
        assert expected == data['code']
    else:
        assert load_json(expected) == data


@pytest.mark.parametrize(
    'service_id, status, expected',
    [
        pytest.param(
            1,
            200,
            'response_service_id_1.json',
            marks=[pytest.mark.features_on('enable_use_abc_service_for_duty')],
            id='pg_service',
        ),
        pytest.param(
            2,
            200,
            'response_service_id_2.json',
            marks=[
                pytest.mark.features_on('enable_use_abc_service_for_duty'),
                pytest.mark.config(
                    CLOWNDUCTOR_NEW_IDM_SYSTEM_USAGE={
                        '__default__': {
                            '__default__': {
                                '__default__': {
                                    '__default__': False,
                                    'full_info': True,
                                },
                            },
                        },
                    },
                ),
            ],
            id='empty_fields using service',
        ),
        pytest.param(
            3,
            200,
            'response_service_id_3.json',
            marks=[
                pytest.mark.features_off('enable_use_abc_service_for_duty'),
            ],
        ),
        pytest.param(4, 200, 'response_service_id_4.json'),
        pytest.param(5, 200, 'response_service_id_5.json'),
        pytest.param(
            6,
            200,
            'response_service_id_6.json',
            id='check_no_approvers_duplicates',
        ),
        pytest.param(
            6,
            200,
            'response_service_id_6.json',
            marks=[
                pytest.mark.config(
                    CLOWNDUCTOR_NEW_IDM_SYSTEM_USAGE={
                        '__default__': {
                            '__default__': {
                                '__default__': {
                                    '__default__': False,
                                    'full_info': True,
                                },
                            },
                        },
                    },
                ),
            ],
            id='check_no_approvers_duplicates using service',
        ),
        pytest.param(
            7,
            200,
            'response_service_id_7.json',
            id='check_no_parameters_or_branches',
        ),
        pytest.param(
            8, 200, 'response_service_id_8.json', id='no_maintainers',
        ),
        pytest.param(9, 200, 'response_service_id_9.json', id='no_messages'),
        pytest.param(
            10, 200, 'response_service_id_10.json', id='dismissed_maintainers',
        ),
        pytest.param(55, 404, 'NOT_FOUND'),
    ],
)
@pytest.mark.pgsql('clownductor', files=['init_db.sql'])
@pytest.mark.translations(clownductor=TRANSLATIONS)
@pytest.mark.features_on(
    'enable_modal_fields',
    'enable_uptime',
    'enable_usage_fields',
    'enable_modal_approvers',
    'full_info_show_juggler_configs_update_status',
)
async def test_full_info_service(
        taxi_clownductor_web,
        mockserver,
        service_id,
        status,
        expected,
        load_json,
        mock_hejmdal,
        mock_clowny_alert_manager,
        load,
        patch,
        clowny_roles_grants,
):
    @mockserver.json_handler('/duty-api/api/duty_group')
    def duty_group_handler(request):
        assert request.query['group_id']
        return {
            'result': {
                'data': {
                    'currentEvent': {'user': 'karachevda'},
                    'suggestedEvents': [{'user': 'test_user'}],
                    'staffGroups': ['test_group'],
                },
                'ok': True,
            },
        }

    clowny_roles_grants.add_dev_approver(
        'd1mbas', {'id': 'abc_service', 'type': 'service'},
    )
    clowny_roles_grants.add_dev_approver(
        'deoevgen', {'id': 'abc_service_6', 'type': 'service'},
    )
    clowny_roles_grants.add_dev_approver(
        'deoevgen', {'id': 'cargo', 'type': 'project'},
    )

    @mockserver.json_handler('/client-abc/v4/duty/on_duty/')
    def client_abc_handler(request):

        if request.query.get('schedule__slug') == 'primary_shedule_service':
            return [
                {
                    'person': {'login': 'main_duty'},
                    'start_datetime': '2022-06-09T12:00:00+03:00',
                    'end_datetime': '2022-06-10T12:00:00+03:00',
                },
            ]
        if request.query.get('service__slug') == 'common_abc_slug':
            return [
                {
                    'person': {'login': 'assistant1'},
                    'start_datetime': '2022-06-08T12:00:00+03:00',
                    'end_datetime': '2022-06-10T12:00:00+03:00',
                },
                {
                    'person': {'login': 'assistant2'},
                    'start_datetime': '2022-06-09T12:00:00+03:00',
                    'end_datetime': '2022-06-10T12:00:00+03:00',
                },
                {
                    'person': {'login': 'main_duty'},
                    'start_datetime': '2022-06-09T12:00:00+03:00',
                    'end_datetime': '2022-06-10T12:00:00+03:00',
                },
            ]
        return []

    @mock_hejmdal('/v1/analytics/service_uptime', prefix=True)
    def hejmdal_uptime_handler(request):  # pylint: disable=unused-variable
        return {
            'uptime': [{'period': '30d', 'value': 0.999972622174006}],
            'uptime_link': 'monitoring.yandex-team.ru/dashboards/uptime',
        }

    @mock_hejmdal('/v1/analytics/service_resource_usage', prefix=True)
    def hejmdal_usage_handler(request):  # pylint: disable=unused-variable
        return {
            'cpu_usage': {
                'high_usage': {
                    'not_ok_time_prc': 34,
                    'period': {
                        'start': '2020-09-07T08:00:00.000+03:00',
                        'end': '2020-09-14T08:00:00.000+03:00',
                    },
                },
                'low_usage': {
                    'not_ok_time_prc': 7,
                    'period': {
                        'start': '2020-09-07T08:00:00.000+03:00',
                        'end': '2020-09-14T08:00:00.000+03:00',
                    },
                },
                'usage_graph_link': (
                    'https://yasm.yandex-team.ru/'
                    'link/to/cpu/usage/percent/graph'
                ),
            },
            'ram_usage': {
                'high_usage': {
                    'not_ok_time_prc': 0,
                    'period': {
                        'start': '2020-09-07T08:00:00.000+03:00',
                        'end': '2020-09-14T08:00:00.000+03:00',
                    },
                },
                'low_usage': {
                    'not_ok_time_prc': 4,
                    'period': {
                        'start': '2020-09-07T08:00:00.000+03:00',
                        'end': '2020-09-14T08:00:00.000+03:00',
                    },
                },
                'usage_graph_link': (
                    'https://yasm.yandex-team.ru/'
                    'link/to/ram/usage/percent/graph'
                ),
            },
        }

    @mock_clowny_alert_manager('/v1/configs/queue/list/')
    def _get_configs_queue_list_mock(request):
        _service_id = int(request.query['service_id'])
        if _service_id == 5:
            return {
                'configs': [
                    {
                        'branch_id': 1,
                        'clown_branch_ids': [7, 8],
                        'status': 'pending',
                        'updated_at': '2020.06.09T12:00:00',
                    },
                ],
            }
        return mockserver.make_response(
            status=404,
            json={
                'code': 'NOT_FOUND',
                'message': f'service {_service_id} not found',
            },
        )

    response = await taxi_clownductor_web.post(
        '/v1/services/full_info/',
        json={'service_id': service_id},
        headers={'X-Yandex-Login': 'deoevgen'},
    )
    assert response.status == status
    data = await response.json()
    if status == 404:
        assert expected == data['code']
    else:
        response_data = load_json(expected)
        assert data == response_data

    if service_id == 1:
        assert client_abc_handler.times_called == 2
    elif service_id == 2:
        assert duty_group_handler.times_called == 1
    else:
        assert not duty_group_handler.times_called
