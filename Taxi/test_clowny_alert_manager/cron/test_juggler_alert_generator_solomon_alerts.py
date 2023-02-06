import pytest

from taxi.clients import juggler_api

from clowny_alert_manager.generated.cron import run_cron

CLOWN_BRANCH_ID = 2
TEMPLATE_ID = 'test-multialert'
ALERT_ID = 'test-alert-id'


def create_mock_alert() -> dict:
    return {
        'id': ALERT_ID,
        'projectId': 'test_project_id',
        'name': 'Test Alert',
        'version': 1,
        'createdBy': 'tvm-2015275',
        'createdAt': '2022-05-05T11:50:31Z',
        'updatedBy': 'tvm-2015275',
        'updatedAt': '2022-05-05T11:50:31Z',
        'state': 'ACTIVE',
        'notificationChannels': ['webhook-solomon_alerts-from_template'],
        'channels': [
            {
                'id': 'webhook-solomon_alerts-from_template',
                'config': {
                    'notifyAboutStatuses': ['WARN', 'ERROR', 'ALARM', 'OK'],
                    'repeatDelaySecs': 90,
                },
            },
        ],
        'type': {
            'fromTemplate': {
                'templateId': TEMPLATE_ID,
                'templateVersionTag': 'v3',
                'textValueParameters': [
                    {'value': 'taxi_hejmdal_stable', 'name': 'direct_link'},
                    {'value': 'hejmdal', 'name': 'service_name'},
                ],
                'doubleValueThresholds': [{'value': 0.5, 'name': 'threshold'}],
                'serviceProvider': 'hejmdal',
            },
        },
        'annotations': {
            'alert_description': (
                '{{expression.alert_reason}}\\n---\\nСервис: '
                '{{templateParameter.service_name}}\\nБранч: '
                '{{templateParameter.direct_link}}'
            ),
        },
        'periodMillis': 0,
        'delaySeconds': 0,
        'windowSecs': 0,
        'delaySecs': 0,
        'description': 'Test alert',
        'resolvedEmptyPolicy': 'RESOLVED_EMPTY_DEFAULT',
        'noPointsPolicy': 'NO_POINTS_DEFAULT',
        'labels': {
            'created_by': 'hejmdal_testing',
            'created_for': f'{CLOWN_BRANCH_ID}',
        },
        'serviceProviderAnnotations': {},
    }


@pytest.mark.config(
    CLOWNY_ALERT_MANAGER_FEATURES={'juggler_alert_generator_enabled': True},
    CLOWNY_ALERT_MANAGER_NAMESPACE_SETTINGS=[
        {'name': '__default__', 'dry_run': False},
    ],
    CLOWNY_ALERT_MANAGER_SETTINGS={
        'projects': {
            'test': {
                'default_namespace': 'test.test',
                'duty': [
                    {'duty_taxi': 'default_duty', 'namespace': 'default'},
                    {'duty_taxi': 'other_duty', 'namespace': 'test.test'},
                ],
                'mark_prefix': 'taxi-monitoring',
                'phone_escalation_options': {
                    'delay': 900,
                    'on_success_next_call_delay': 60,
                    'repeat': 2,
                },
                'repo': (
                    'https://github.yandex-team.ru/taxi/infra-cfg-juggler.git'
                ),
                'repo_path': '',
                'telegram': [
                    {
                        'copy_to_default_telegram': True,
                        'namespace': 'taxi.eda',
                        'telegram_name': 'tlg_chanel',
                    },
                ],
            },
        },
    },
)
@pytest.mark.features_on('enable_clownductor_cache', 'use_arc')
@pytest.mark.usefixtures('clownductor_mock')
async def test_juggler_alert_generator_solomon_multialert(
        mockserver,
        mock_solomon_v2,
        monkeypatch,
        patch,
        pack_repo,
        patch_aiohttp_session,
        response_mock,
):
    repo_tarball = pack_repo('infra-cfg-juggler_simple')

    @patch('clowny_alert_manager.internal.utils.repo._get_tarball_path')
    async def _patch_get_tarball_path(_):
        return str(repo_tarball)

    # Mock ABC
    @mockserver.json_handler('/duty-api/api/duty_group', prefix=True)
    def _duty_handler(req):
        assert 'Authorization' in req.headers
        duty_name = req.path.split('/')[-1]
        return {
            'result': {
                'data': {
                    'staffGroups': [],
                    'suggestedEvents': [],
                    'currentEvent': {'user': f'duty-user-{duty_name}'},
                },
                'ok': True,
            },
        }

    # Mock solomon alerts cache initialization
    @mock_solomon_v2('/api/v2/projects/hejmdal/alertsFullModel')
    def _mock_solomon_alert_full_model(request):
        assert (
            request.query['labelsSelector'] == 'created_by=hejmdal_testsuite'
        )

        return mockserver.make_response(
            status=200, json={'items': [create_mock_alert()]},
        )

    # Mock juggler calls
    @patch_aiohttp_session(
        juggler_api.JUGGLER_API_URL + '/api/checks/checks', 'GET',
    )
    def _mock_get_checks(method, url, **kwargs):
        assert 'Authorization' in kwargs['headers']
        assert kwargs['params']['do'] == 1
        return response_mock(json={})

    @patch_aiohttp_session(
        juggler_api.JUGGLER_API_URL + '/api/system/config_tree', 'GET',
    )
    def _mock_system_config_tree(method, url, **kwargs):
        assert kwargs['params']['do'] == 1
        return response_mock(
            json={
                'jctl': {'new_check_downtime': 1200},
                'main': {
                    'default_check_ttl': 900,
                    'default_check_refresh_time': 90,
                },
            },
        )

    alert_created = False

    @patch_aiohttp_session(
        juggler_api.JUGGLER_API_URL + '/api/checks/add_or_update', 'POST',
    )
    def _mock_checks_add_or_update(method, url, **kwargs):
        assert 'Authorization' in kwargs['headers']
        assert kwargs['params']['do'] == 1

        data = kwargs['json']

        if data['host'] == 'some_host':
            children = data['children']
            assert len(children) == 1

            child = children[0]
            assert child['type'] == 'EVENTS'
            assert (
                child['host'] == f'(service={TEMPLATE_ID} & '
                f'tag=monitoring_alert_id_{ALERT_ID})'
            )
            nonlocal alert_created
            alert_created = True

        return response_mock(json={'status': 200})

    # Run cron
    await run_cron.main(
        ['clowny_alert_manager.crontasks.juggler_alert_generator', '-t', '0'],
    )
    assert alert_created
