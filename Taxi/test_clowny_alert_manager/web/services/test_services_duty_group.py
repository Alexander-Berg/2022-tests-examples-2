import pytest


MOCK_DATA = [
    {'service_id': 1, 'branch_id': 1, 'duty_group_id': 'some_duty_group_id'},
    {'service_id': 139, 'branch_id': 18, 'duty_group_id': 'hejmdaldutygroup'},
    {
        'service_id': 13,
        'branch_id': 13,
        'duty_group_id': 'alert_manager_duty_group_id',
    },
    {'service_id': 1234, 'branch_id': 1},
    {
        'service_id': 100500,
        'branch_id': 100500,
        'duty': {
            'abc_slug': 'hejmdalduty',
            'primary_schedule': 'taxidutyhejmdal',
        },
    },
]


@pytest.fixture(name='mock_clown_remote_values')
def _mock_clown_remote_values(mockserver):
    @mockserver.handler('/clownductor/v1/parameters/remote_values/')
    async def _handler(request):
        for mock_data in MOCK_DATA:
            if request.query['service_id'] == str(
                    mock_data['service_id'],
            ) and request.query['branch_id'] == str(mock_data['branch_id']):
                service_info = [
                    {'name': 'clownductor_project', 'value': 'taxi-infra'},
                ]
                if mock_data.get('duty_group_id'):
                    service_info.append(
                        {
                            'name': 'duty_group_id',
                            'value': mock_data['duty_group_id'],
                        },
                    )
                if mock_data.get('duty'):
                    service_info.append(
                        {'name': 'duty', 'value': mock_data['duty']},
                    )
                return mockserver.make_response(
                    status=200,
                    json={
                        'subsystems': [
                            {
                                'subsystem_name': 'nanny',
                                'parameters': [
                                    {
                                        'name': 'cpu',
                                        'value': 1000,
                                        'unit': 'ms',
                                    },
                                ],
                            },
                            {
                                'subsystem_name': 'service_info',
                                'parameters': service_info,
                            },
                        ],
                    },
                )
        return mockserver.make_response(
            status=404, json={'code': 'not-found', 'message': 'not-found'},
        )

    return _handler


@pytest.fixture(name='mock_abc_api_duty')
def _mock_abc_api_duty(mockserver):
    @mockserver.json_handler('/client-abc/v4/duty/on_duty/')
    def _handler(request):
        if request.query.get('schedule__slug') == 'hejmdaldutygroup':
            return [{'schedule': {'id': 2902}}]
        if request.query.get('service__slug') == 'hejmdalduty':
            return [{'schedule': {'id': 2902}, 'person': {'login': 'd1mbas'}}]
        return []

    return _handler


@pytest.fixture(name='mock_abc_api_schedules')
def _mock_abc_api_schedules(mockserver):
    @mockserver.json_handler('/client-abc/v4/duty/schedules/', prefix=True)
    def _handler(request):
        if request.path == '/client-abc/v4/duty/schedules/2902/':
            return {
                'service': {'slug': 'hejmdalduty'},
                'orders': [{'person': {'login': 'd1mbas'}, 'order': 0}],
            }
        return {}

    return _handler


@pytest.fixture(name='mock_duty_api')
def _mock_duty_api(mockserver):
    @mockserver.json_handler('/duty-api/api/duty_group')
    def _handler(request):
        if request.query['group_id'] == 'alert_manager_duty_group_id':
            return {
                'result': {
                    'data': {
                        'currentEvent': {'user': 'user1'},
                        'suggestedEvents': [
                            {'user': 'user2'},
                            {'user': 'user1'},
                            {'user': 'user2'},
                            {'user': 'user1'},
                        ],
                        'staffGroups': [
                            'svc_duty_group_from_old_duty_administration',
                        ],
                    },
                    'error': None,
                    'ok': True,
                },
            }
        if request.query['group_id'] == 'hejmdaldutygroup':
            return {
                'result': {
                    'data': {
                        'currentEvent': {
                            'calendar_event_id': None,
                            'calendar_layer': 0,
                            'end': 'Sun, 23 Jan 2022 21:00:00 GMT',
                            'st_key': None,
                            'start': 'Sun, 16 Jan 2022 21:00:00 GMT',
                            'started': False,
                            'user': 'mirasharf',
                        },
                        'suggestedEvents': [
                            {
                                'calendar_event_id': None,
                                'calendar_layer': 0,
                                'end': 'Sun, 30 Jan 2022 21:00:00 GMT',
                                'st_key': None,
                                'start': 'Sun, 23 Jan 2022 21:00:00 GMT',
                                'started': False,
                                'user': 'victorshch',
                            },
                            {
                                'calendar_event_id': None,
                                'calendar_layer': 0,
                                'end': 'Sun, 06 Feb 2022 21:00:00 GMT',
                                'st_key': None,
                                'start': 'Sun, 30 Jan 2022 21:00:00 GMT',
                                'started': False,
                                'user': 'atsinin',
                            },
                        ],
                        'staffGroups': [
                            'svc_duty_group_from_old_duty_administration',
                        ],
                    },
                    'error': None,
                    'ok': True,
                },
            }
        return {
            'result': {
                'data': {'currentEvent': None, 'staffGroups': []},
                'error': None,
                'ok': True,
            },
        }

    return _handler


@pytest.mark.config(
    CLOWNY_ALERT_MANAGER_DUTY_GROUPS=[
        {
            'duty_mode': 'full',
            'id': 'some_duty_group_id',
            'telegram_options': {
                'production': 'custom_channel_prod',
                'testing': 'custom_channel_test',
            },
        },
    ],
    CLOWNY_ALERT_MANAGER_DUTY_GROUP_ABC_SETTINGS={
        'some_duty_group_id': 'clown_duty_group',
    },
)
@pytest.mark.features_on(
    'get_duty_group_from_clown',
    'enable_update_abc_duty_info',
    'enable_clownductor_cache',
)
async def test_services_duty_group_full(
        web_context,
        get_services_duty_group,
        mockserver,
        mock_clown_remote_values,
        mock_abc_api_duty,
        mock_abc_api_schedules,
        mock_duty_api,
):
    await web_context.clownductor_cache.refresh_cache()
    response = await get_services_duty_group(
        params={'clown_service_id': 1}, status=200,
    )
    assert response == {
        'has_duty_group': True,
        'duty_group_id': 'some_duty_group_id',
        'duty_mode': 'FULL',
        'abc_duty_group_slug': 'clown_duty_group',
    }


@pytest.mark.config(
    CLOWNY_ALERT_MANAGER_DUTY_GROUPS=[
        {
            'duty_mode': 'full',
            'id': 'hejmdalduty:taxidutyhejmdal',
            'telegram_options': {
                'production': 'custom_channel_prod',
                'testing': 'custom_channel_test',
            },
        },
    ],
)
@pytest.mark.features_on(
    'get_duty_group_from_clown',
    'enable_update_abc_duty_info',
    'enable_clownductor_cache',
)
async def test_services_abc_duty_group_full(
        web_context,
        get_services_duty_group,
        mockserver,
        mock_clown_remote_values,
        mock_abc_api_duty,
        mock_abc_api_schedules,
        mock_duty_api,
):
    @mockserver.json_handler('/client-abc/v4/duty/schedules-cursor/')
    def _handler(request):
        results = []
        if request.query['service__slug'] == 'hejmdalduty':
            results.append(
                {
                    'id': 2902,
                    'name': 'our duty',
                    'algorithm': 'manual_order',
                    'service': {'id': 1, 'slug': 'hejmdalduty'},
                    'slug': 'taxidutyhejmdal',
                },
            )
        return {'next': None, 'previous': None, 'results': results}

    await web_context.clownductor_cache.refresh_cache()
    response = await get_services_duty_group(
        params={'clown_service_id': 100500}, status=200,
    )
    assert response == {
        'abc_duty_group_slug': 'hejmdalduty',
        'all_duty_group_members': ['d1mbas'],
        'person_on_duty': 'd1mbas',
        'duty': {
            'abc_primary_schedule_slug': 'taxidutyhejmdal',
            'abc_service_slug': 'hejmdalduty',
        },
        'duty_mode': 'FULL',
        'has_duty_group': True,
    }


@pytest.mark.features_on(
    'get_duty_group_from_clown',
    'enable_update_abc_duty_info',
    'enable_clownductor_cache',
)
async def test_services_duty_group_not_in_config(
        web_context,
        get_services_duty_group,
        mockserver,
        mock_clown_remote_values,
        mock_abc_api_duty,
        mock_abc_api_schedules,
        mock_duty_api,
):
    await web_context.clownductor_cache.refresh_cache()

    response = await get_services_duty_group(
        params={'clown_service_id': 139}, status=200,
    )
    assert response == {
        'has_duty_group': True,
        'duty_group_id': 'hejmdaldutygroup',
        'duty_mode': 'IRRESPONSIBLE',
        'abc_duty_group_slug': 'hejmdalduty',
        'person_on_duty': 'mirasharf',
        'all_duty_group_members': ['atsinin', 'mirasharf', 'victorshch'],
    }


@pytest.mark.features_on(
    'get_duty_group_from_clown',
    'enable_update_abc_duty_info',
    'enable_clownductor_cache',
)
async def test_services_duty_group_from_old_duty(
        web_context,
        get_services_duty_group,
        mockserver,
        mock_clown_remote_values,
        mock_abc_api_duty,
        mock_abc_api_schedules,
        mock_duty_api,
):
    await web_context.clownductor_cache.refresh_cache()

    response = await get_services_duty_group(
        params={'clown_service_id': 13}, status=200,
    )
    assert response == {
        'has_duty_group': True,
        'duty_group_id': 'alert_manager_duty_group_id',
        'duty_mode': 'IRRESPONSIBLE',
        'abc_duty_group_slug': 'duty_group_from_old_duty',
        'person_on_duty': 'user1',
        'all_duty_group_members': ['user1', 'user2'],
    }


@pytest.mark.features_on(
    'get_duty_group_from_clown', 'enable_update_abc_duty_info',
)
async def test_services_duty_group_no_duty_group(
        web_context,
        get_services_duty_group,
        mockserver,
        mock_clown_remote_values,
        mock_abc_api_duty,
        mock_abc_api_schedules,
        mock_duty_api,
):
    await web_context.clownductor_cache.refresh_cache()

    response = await get_services_duty_group(
        params={'clown_service_id': 1234}, status=200,
    )
    assert response == {'has_duty_group': False}


@pytest.mark.features_on(
    'get_duty_group_from_clown', 'enable_update_abc_duty_info',
)
async def test_services_duty_group_unknown_service(
        web_context,
        get_services_duty_group,
        mockserver,
        mock_clown_remote_values,
        mock_abc_api_duty,
        mock_abc_api_schedules,
        mock_duty_api,
):
    await web_context.clownductor_cache.refresh_cache()

    await get_services_duty_group(params={'clown_service_id': 666}, status=404)
