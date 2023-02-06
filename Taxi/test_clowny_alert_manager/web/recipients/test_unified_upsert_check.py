import pytest


REMOTE_VALUES_RESPONSE = {
    'subsystems': [
        {
            'subsystem_name': 'nanny',
            'parameters': [{'name': 'cpu', 'value': 2000, 'unit': 'ms'}],
        },
        {
            'subsystem_name': 'service_info',
            'parameters': [
                {'name': 'clownductor_project', 'value': 'taxi-infra'},
                {'name': 'duty_group_id', 'value': 'hejmdal_duty_group_id'},
            ],
        },
    ],
}

REMOTE_VALUES_RESPONSE_2 = {
    'subsystems': [
        {
            'subsystem_name': 'nanny',
            'parameters': [{'name': 'cpu', 'value': 1000, 'unit': 'ms'}],
        },
        {
            'subsystem_name': 'service_info',
            'parameters': [
                {'name': 'clownductor_project', 'value': 'taxi-devops'},
                {'name': 'duty_group_id', 'value': 'clown_duty_group_id'},
            ],
        },
    ],
}


@pytest.fixture(name='mock_clown_remote_values')
def _mock_clown_remote_values(mockserver):
    @mockserver.handler('/clownductor/v1/parameters/remote_values/')
    async def _handler(request):
        if (
                request.query['service_id'] == '139'
                and request.query['branch_id'] == '18'
        ):
            return mockserver.make_response(
                status=200, json=REMOTE_VALUES_RESPONSE,
            )
        if (
                request.query['service_id'] == '1'
                and request.query['branch_id'] == '1'
        ):
            return mockserver.make_response(
                status=200, json=REMOTE_VALUES_RESPONSE_2,
            )
        return mockserver.make_response(
            status=404, json={'code': 'not-found', 'message': 'not-found'},
        )

    return _handler


@pytest.fixture(name='mock_abc_api_duty')
def _mock_abc_api_duty(mockserver):
    @mockserver.json_handler('/client-abc/v4/duty/on_duty/')
    def _handler(request):
        if request.query['schedule__slug'] == 'hejmdal_duty_group_id':
            return [{'schedule': {'id': 2902}}]
        if request.query['schedule__slug'] == 'clown_duty_group_id':
            return [{'schedule': {'id': 1234}}]
        return []

    return _handler


@pytest.fixture(name='mock_abc_api_schedules')
def _mock_abc_api_schedules(mockserver):
    @mockserver.json_handler('/client-abc/v4/duty/schedules/', prefix=True)
    def _handler(request):
        if request.path == '/client-abc/v4/duty/schedules/2902/':
            return {'service': {'slug': 'hejmdalduty'}}
        if request.path == '/client-abc/v4/duty/schedules/1234/':
            return {'service': {'slug': 'clownduty'}}
        return {}

    return _handler


@pytest.fixture(name='mock_duty_api')
def _mock_duty_api(mockserver):
    @mockserver.json_handler('/duty-api/api/duty_group')
    def _handler(request):
        if (
                request.query['group_id'] == 'clown_duty_group_id'
                or request.query['group_id'] == 'hejmdal_duty_group_id'
        ):
            return {
                'result': {
                    'data': {
                        'currentEvent': {'user': 'user1'},
                        'suggestedEvents': [
                            {'user': 'user1'},
                            {'user': 'user2'},
                        ],
                        'staffGroups': [],
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


@pytest.mark.features_on(
    'get_duty_group_from_clown',
    'enable_update_abc_duty_info',
    'enable_clownductor_cache',
)
async def test_unified_recipients_upsert_check_create(
        web_context,
        unified_recipients_upsert_check,
        mock_clown_remote_values,
        mock_abc_api_duty,
        mock_abc_api_schedules,
        mock_duty_api,
):
    await web_context.clownductor_cache.refresh_cache()
    data = {
        'clown_service_id': 1,
        'chats': ['chat'],
        'logins': ['username'],
        'duty': 'off',
        'do_merge_with_telegram_options': False,
        'receive_testing_alerts': False,
    }

    response = await unified_recipients_upsert_check(data=data)

    assert response == {
        'change_doc_id': 'unified_recipients_service_1_update',
        'data': data,
        'diff': {'new': data},
    }


@pytest.mark.features_on(
    'get_duty_group_from_clown',
    'enable_update_abc_duty_info',
    'enable_clownductor_cache',
)
async def test_unified_recipients_upsert_check_create_w_testing(
        web_context,
        unified_recipients_upsert_check,
        mock_clown_remote_values,
        mock_abc_api_duty,
        mock_abc_api_schedules,
        mock_duty_api,
):
    await web_context.clownductor_cache.refresh_cache()
    data = {
        'clown_service_id': 139,
        'chats': ['chat'],
        'logins': ['username'],
        'testing_chats': ['testing-chat'],
        'duty': 'off',
        'do_merge_with_telegram_options': False,
        'receive_testing_alerts': True,
    }

    response = await unified_recipients_upsert_check(data=data)

    assert response == {
        'change_doc_id': 'unified_recipients_service_139_update',
        'data': data,
        'diff': {'new': data},
    }


@pytest.mark.features_on(
    'get_duty_group_from_clown',
    'enable_update_abc_duty_info',
    'enable_clownductor_cache',
)
async def test_unified_recipients_upsert_check_create_w_duty(
        web_context,
        unified_recipients_upsert_check,
        mockserver,
        mock_clown_remote_values,
        mock_abc_api_duty,
        mock_abc_api_schedules,
        mock_duty_api,
):
    await web_context.clownductor_cache.refresh_cache()
    data = {
        'clown_service_id': 139,
        'chats': ['chat'],
        'logins': ['username'],
        'testing_chats': ['testing-chat'],
        'duty': 'to_all_duty_group_members',
        'do_merge_with_telegram_options': False,
        'receive_testing_alerts': True,
    }

    response = await unified_recipients_upsert_check(data=data)

    assert response == {
        'change_doc_id': 'unified_recipients_service_139_update',
        'data': data,
        'diff': {'new': data},
    }


@pytest.mark.features_on(
    'get_duty_group_from_clown',
    'enable_update_abc_duty_info',
    'enable_clownductor_cache',
)
async def test_unified_recipients_upsert_check_with_diff(
        web_context,
        unified_recipients_upsert_check,
        mock_clown_remote_values,
        mock_abc_api_duty,
        mock_abc_api_schedules,
        mock_duty_api,
):
    await web_context.pg.primary.execute(
        query='INSERT INTO alert_manager.unified_recipients '
        '(clown_service_id, chats, logins, duty, receive_testing_alerts) '
        'VALUES (1, \'{chat1}\'::TEXT[], \'{alexrasyuk}\'::TEXT[], '
        '\'off\', FALSE);',
    )
    await web_context.clownductor_cache.refresh_cache()
    data = {
        'clown_service_id': 1,
        'chats': ['chat1', 'chat2'],
        'logins': ['alexrasyuk'],
        'duty': 'off',
        'receive_testing_alerts': False,
        'do_merge_with_telegram_options': True,
    }

    response = await unified_recipients_upsert_check(data=data)

    assert response == {
        'change_doc_id': 'unified_recipients_service_1_update',
        'data': data,
        'diff': {
            'new': data,
            'current': {
                'clown_service_id': 1,
                'chats': ['chat1'],
                'logins': ['alexrasyuk'],
                'duty': 'off',
                'do_merge_with_telegram_options': True,
                'receive_testing_alerts': False,
            },
        },
    }


@pytest.mark.features_on(
    'get_duty_group_from_clown',
    'enable_update_abc_duty_info',
    'enable_clownductor_cache',
)
async def test_unified_recipients_upsert_check_diff_w_duty(
        web_context,
        unified_recipients_upsert_check,
        mockserver,
        mock_clown_remote_values,
        mock_abc_api_duty,
        mock_abc_api_schedules,
        mock_duty_api,
):
    await web_context.pg.primary.execute(
        query='INSERT INTO alert_manager.unified_recipients '
        '(clown_service_id, chats, logins, duty, receive_testing_alerts) '
        'VALUES (139, \'{chat1}\'::TEXT[], \'{alexrasyuk}\'::TEXT[], '
        '\'off\', FALSE);',
    )

    await web_context.clownductor_cache.refresh_cache()
    data = {
        'clown_service_id': 139,
        'chats': ['chat1'],
        'logins': ['alexrasyuk'],
        'duty': 'to_person_on_duty',
        'do_merge_with_telegram_options': True,
        'receive_testing_alerts': False,
    }

    response = await unified_recipients_upsert_check(data=data)

    assert response == {
        'change_doc_id': 'unified_recipients_service_139_update',
        'data': data,
        'diff': {
            'new': data,
            'current': {
                'clown_service_id': 139,
                'chats': ['chat1'],
                'logins': ['alexrasyuk'],
                'duty': 'off',
                'do_merge_with_telegram_options': True,
                'receive_testing_alerts': False,
            },
        },
    }


async def test_unified_recipients_upsert_check_unknown_service(
        web_context, unified_recipients_upsert_check,
):
    await web_context.clownductor_cache.refresh_cache()
    data = {
        'clown_service_id': 999,
        'chats': ['chat1', 'chat2'],
        'logins': ['alexrasyuk'],
        'duty': 'to_all_duty_group_members',
        'receive_testing_alerts': True,
        'do_merge_with_telegram_options': True,
    }
    await unified_recipients_upsert_check(data=data, status=400)


async def test_unified_recipients_upsert_check_unparsed_service(
        web_context, unified_recipients_upsert_check,
):
    await web_context.clownductor_cache.refresh_cache()
    data = {
        'clown_service_id': 2,
        'chats': ['chat1', 'chat2'],
        'logins': ['alexrasyuk'],
        'duty': 'to_all_duty_group_members',
        'receive_testing_alerts': True,
        'do_merge_with_telegram_options': True,
    }
    await unified_recipients_upsert_check(data=data, status=400)


async def test_unified_recipients_upsert_check_service_without_stable(
        web_context, unified_recipients_upsert_check,
):
    await web_context.clownductor_cache.refresh_cache()
    data = {
        'clown_service_id': 666,
        'chats': ['chat1', 'chat2'],
        'logins': ['alexrasyuk'],
        'duty': 'to_all_duty_group_members',
        'receive_testing_alerts': True,
        'do_merge_with_telegram_options': True,
    }
    await unified_recipients_upsert_check(data=data, status=400)


async def test_unified_recipients_upsert_check_service_without_testing(
        web_context, unified_recipients_upsert_check,
):
    await web_context.clownductor_cache.refresh_cache()
    data = {
        'clown_service_id': 1,
        'chats': ['chat1', 'chat2'],
        'logins': ['alexrasyuk'],
        'duty': 'to_all_duty_group_members',
        'receive_testing_alerts': True,
        'do_merge_with_telegram_options': True,
    }
    await unified_recipients_upsert_check(data=data, status=400)


async def test_unified_recipients_upsert_check_w_testing_but_no_chats(
        web_context,
        unified_recipients_upsert_check,
        mock_clown_remote_values,
        mock_abc_api_duty,
        mock_abc_api_schedules,
        mock_duty_api,
):
    await web_context.clownductor_cache.refresh_cache()
    data = {
        'clown_service_id': 139,
        'chats': ['chat1', 'chat2'],
        'logins': ['alexrasyuk'],
        'testing_chats': [],
        'duty': 'off',
        'receive_testing_alerts': True,
        'do_merge_with_telegram_options': True,
    }
    await unified_recipients_upsert_check(data=data, status=400)


async def test_unified_recipients_upsert_check_invalid_duty(
        web_context, unified_recipients_upsert_check,
):
    await web_context.clownductor_cache.refresh_cache()
    data = {
        'clown_service_id': 139,
        'chats': ['chat1', 'chat2'],
        'logins': ['alexrasyuk'],
        'duty': 'on',
        'receive_testing_alerts': False,
        'do_merge_with_telegram_options': True,
    }
    await unified_recipients_upsert_check(data=data, status=400)


async def test_unified_recipients_upsert_check_no_changes(
        web_context, unified_recipients_upsert_check,
):
    await web_context.pg.primary.execute(
        query='INSERT INTO alert_manager.unified_recipients '
        '(clown_service_id, chats, logins, duty, receive_testing_alerts) '
        'VALUES (1, \'{chat2}\'::TEXT[], \'{alexrasyuk}\'::TEXT[], '
        '\'off\', FALSE);',
    )
    await web_context.clownductor_cache.refresh_cache()
    data = {
        'clown_service_id': 1,
        'chats': ['chat2'],
        'logins': ['alexrasyuk'],
        'duty': 'off',
        'receive_testing_alerts': False,
        'do_merge_with_telegram_options': True,
    }
    await unified_recipients_upsert_check(data=data, status=400)


async def test_unified_recipients_upsert_check_no_duty_group_no_diff(
        web_context, unified_recipients_upsert_check, mockserver,
):
    await web_context.clownductor_cache.refresh_cache()
    data = {
        'clown_service_id': 123,
        'chats': ['chat1'],
        'logins': ['alexrasyuk'],
        'duty': 'to_person_on_duty',
        'do_merge_with_telegram_options': True,
        'receive_testing_alerts': False,
    }

    await unified_recipients_upsert_check(data=data, status=400)
