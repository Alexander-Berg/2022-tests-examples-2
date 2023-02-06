import pytest


@pytest.fixture(name='mock_abc_api_duty')
def _mock_abc_api_duty(mockserver):
    @mockserver.json_handler('/client-abc/v4/duty/on_duty/')
    def _handler(request):
        if request.query['schedule__slug'] == 'hejmdaldutygroup':
            return [{'schedule': {'id': 2902}}]
        return []

    return _handler


@pytest.fixture(name='mock_abc_api_schedules')
def _mock_abc_api_schedules(mockserver):
    @mockserver.json_handler('/client-abc/v4/duty/schedules/', prefix=True)
    def _handler(request):
        if request.path == '/client-abc/v4/duty/schedules/2902/':
            return {'service': {'slug': 'hejmdalduty'}}
        return {}

    return _handler


@pytest.fixture(name='mock_duty_api')
def _mock_duty_api(mockserver):
    @mockserver.json_handler('/duty-api/api/duty_group')
    def _handler(request):
        if request.query['group_id'] == 'hejmdaldutygroup':
            return {
                'result': {
                    'data': {
                        'currentEvent': {'user': 'oboroth'},
                        'suggestedEvents': [{'user': 'alexrasyuk'}],
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


@pytest.mark.features_on('enable_update_abc_duty_info')
async def test_unified_recipients_set_default(
        web_context,
        unified_recipients_set_default,
        mock_abc_api_duty,
        mock_abc_api_schedules,
        mock_duty_api,
):
    await unified_recipients_set_default(
        data={
            'clown_service_id': 139,
            'duty_group_id': 'hejmdaldutygroup',
            'cluster_type': 'nanny',
        },
    )

    rows = await web_context.pg.primary.fetch(
        'SELECT clown_service_id, chats, logins, testing_chats, duty, '
        'receive_testing_alerts, do_merge_with_telegram_options '
        'FROM alert_manager.unified_recipients;',
    )
    assert len(rows) == 1
    assert dict(rows[0]) == {
        'clown_service_id': 139,
        'chats': [],
        'logins': [],
        'testing_chats': [],
        'duty': 'to_person_on_duty',
        'receive_testing_alerts': False,
        'do_merge_with_telegram_options': False,
    }


@pytest.mark.features_on('enable_update_abc_duty_info')
async def test_unified_recipients_set_default_no_duty_info(
        web_context,
        unified_recipients_set_default,
        mock_abc_api_duty,
        mock_abc_api_schedules,
        mock_duty_api,
):
    await unified_recipients_set_default(
        data={
            'clown_service_id': 666,
            'duty_group_id': 'some_duty_group',
            'cluster_type': 'nanny',
        },
        status=400,
    )


@pytest.mark.features_on('enable_update_abc_duty_info')
async def test_unified_recipients_set_default_unsupported_cluster_type(
        web_context,
        unified_recipients_set_default,
        mock_abc_api_duty,
        mock_abc_api_schedules,
        mock_duty_api,
):
    await unified_recipients_set_default(
        data={
            'clown_service_id': 139,
            'duty_group_id': 'hejmdaldutygroup',
            'cluster_type': 'conductor',
        },
        status=400,
    )
