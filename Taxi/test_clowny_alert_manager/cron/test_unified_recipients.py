# pylint: disable=protected-access
import pytest

from taxi.clients import juggler_api

from clowny_alert_manager.internal.generator_tools import common as gt_common
from clowny_alert_manager.internal.generator_tools.notifications import (
    impl as gt_notifications_impl,
)
from clowny_alert_manager.internal.generator_tools.notifications import (
    interface as gt_notifications,
)
from clowny_alert_manager.internal.models import branch as branch_models
from clowny_alert_manager.internal.models import service as service_models


STATUS = [
    {'from': 'OK', 'to': 'CRIT'},
    {'from': 'WARN', 'to': 'CRIT'},
    {'from': 'CRIT', 'to': 'WARN'},
    {'from': 'CRIT', 'to': 'OK'},
    {'from': 'OK', 'to': 'WARN'},
    {'from': 'WARN', 'to': 'OK'},
]
BRANCH = branch_models.BareBranch.custom_create(
    [18, 19],
    ['taxi_hejmdal_stable', 'taxi_hejmdal_pre_stable'],
    'taxi_hejmdal_stable',
    'taxi_hejmdal_stable',
    'taxi.platform.test',
)
SERVICE = service_models.BareService.custom_create(
    139, 150, 'hejmdal', 'project', 'rtc',
)

pytestmark = [  # pylint: disable=invalid-name
    pytest.mark.features_on('use_arc'),
]


@pytest.fixture(name='mock_clown_remote_values')
def _mock_clown_remote_values(mockserver):
    @mockserver.handler('/clownductor/v1/parameters/remote_values/')
    async def _handler(request):
        if (
                request.query['service_id'] == '139'
                and request.query['branch_id'] == '18'
        ):
            return mockserver.make_response(
                status=200,
                json={
                    'subsystems': [
                        {
                            'subsystem_name': 'nanny',
                            'parameters': [
                                {'name': 'cpu', 'value': 2000, 'unit': 'ms'},
                            ],
                        },
                        {
                            'subsystem_name': 'service_info',
                            'parameters': [
                                {
                                    'name': 'duty_group_id',
                                    'value': 'taxidutyhejmdal',
                                },
                            ],
                        },
                    ],
                },
            )
        if (
                request.query['service_id'] == '123'
                and request.query['branch_id'] == '1234'
        ):
            return mockserver.make_response(
                status=200,
                json={
                    'subsystems': [
                        {
                            'subsystem_name': 'service_info',
                            'parameters': [
                                {
                                    'name': 'duty',
                                    'value': {
                                        'abc_slug': 'hejmdalduty',
                                        'primary_schedule': 'taxidutyhejmdal',
                                    },
                                },
                            ],
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
        if request.query.get('schedule__slug') == 'taxidutyhejmdal':
            return [{'schedule': {'id': 2902}}]
        if request.query.get('service__slug') == 'hejmdalduty':
            return [{'schedule': {'id': 2902}, 'person': {'login': 'd1mbas'}}]
        return []

    return _handler


@pytest.fixture(name='mock_abc_schedules_cursor')
def _mock_abc_schedules_cursor(mockserver):
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
        return mockserver.make_response(status=404)

    return _handler


@pytest.fixture(name='mock_duty_api')
def _mock_duty_api(mockserver):
    @mockserver.json_handler('/duty-api/api/duty_group')
    def _handler(request):
        if request.query['group_id'] == 'taxidutyhejmdal':
            return {
                'result': {
                    'data': {
                        'currentEvent': {'user': 'alexrasyuk'},
                        'suggestedEvents': [
                            {'user': 'oboroth'},
                            {'user': 'alexrasyuk'},
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


@pytest.fixture(autouse=True)
def _setup_repo(patch, pack_repo):
    repo_tarball = pack_repo('infra-cfg-juggler_simple')

    @patch('clowny_alert_manager.internal.utils.repo._get_tarball_path')
    async def _patch_get_tarball_path(_):
        return str(repo_tarball)


@pytest.fixture(autouse=True)
def solomon_client_mock(mockserver):
    @mockserver.json_handler('/api/v2/projects/hejmdal/alertsFullModel')
    def _mock_alert_full_model(request):
        return mockserver.make_response(status=200, json={'items': []})


@pytest.fixture(name='refresh_caches')
async def refresh_caches_fixture(cron_context):
    await cron_context.clownductor_cache.init_cache()
    await cron_context.infra_cfg_juggler.init_cache()


@pytest.mark.features_on(
    'get_duty_group_from_clown', 'enable_update_abc_duty_info',
)
async def test_build_aggregate_notifications(
        cron_context,
        clown_branches,
        clownductor_mock,
        mock_clown_remote_values,
        mock_abc_api_duty,
        mock_abc_api_schedules,
        mock_duty_api,
        refresh_caches,
):
    await cron_context.pg.primary.execute(
        query='INSERT INTO alert_manager.unified_recipients '
        '(clown_service_id, chats, logins, duty, '
        'receive_testing_alerts) '
        f'VALUES (139, \'{{chat1}}\'::TEXT[], \'{{user1}}\'::TEXT[], '
        '\'off\', FALSE);',
    )
    await cron_context.unified_recipients_cache.refresh_cache()

    result = await gt_notifications_impl.collect_unified_recipients(
        features=cron_context.features,
        clownductor_cache=cron_context.clownductor_cache,
        unified_recipients_cache=cron_context.unified_recipients_cache,
        duty_cache=cron_context.duty_cache,
        juggler_host='some_host',
        clown_service_id=139,
        is_stable=True,
    )
    assert result == juggler_api.NotificationOptions(
        template_name='on_status_change',
        template_kwargs={
            'method': 'telegram',
            'login': ['chat1', 'user1'],
            'status': STATUS,
        },
        description=None,
    )


@pytest.mark.parametrize(
    'receive_testing_alerts, testing_chats, expected_notify_opt',
    [
        (
            True,
            '{"test-chat1", "test-chat2"}',
            juggler_api.NotificationOptions(
                template_name='on_status_change',
                template_kwargs={
                    'method': 'telegram',
                    'login': ['test-chat1', 'test-chat2'],
                    'status': STATUS,
                },
                description=None,
            ),
        ),
        (
            True,
            '{}',
            juggler_api.NotificationOptions(
                template_name='on_status_change',
                template_kwargs={
                    'method': 'telegram',
                    'login': ['chat2', 'user2'],
                    'status': STATUS,
                },
                description=None,
            ),
        ),
        (False, '{}', None),
    ],
)
async def test_build_aggregate_notifications_for_testing_branch(
        cron_context,
        clown_branches,
        clownductor_mock,
        receive_testing_alerts,
        testing_chats,
        expected_notify_opt,
        refresh_caches,
):
    await cron_context.pg.primary.execute(
        query='INSERT INTO alert_manager.unified_recipients '
        '(clown_service_id, chats, logins, testing_chats, duty, '
        'receive_testing_alerts) '
        f'VALUES (139, \'{{chat2}}\'::TEXT[], \'{{user2}}\'::TEXT[], '
        f'\'{testing_chats}\'::TEXT[], \'off\', {receive_testing_alerts});',
    )
    await cron_context.unified_recipients_cache.refresh_cache()

    result = await gt_notifications_impl.collect_unified_recipients(
        features=cron_context.features,
        clownductor_cache=cron_context.clownductor_cache,
        unified_recipients_cache=cron_context.unified_recipients_cache,
        duty_cache=cron_context.duty_cache,
        juggler_host='some_host',
        clown_service_id=139,
        is_stable=False,
    )
    assert result == expected_notify_opt


async def test_build_aggregate_notifications_empty_urs(
        cron_context, clown_branches, clownductor_mock, refresh_caches,
):
    # pylint: disable=protected-access
    result = await gt_notifications.build_aggregate_notifications(
        context=cron_context,
        aggregate_id=gt_common.AggregateId(
            juggler_host='some_host', juggler_service='some_other_service',
        ),
        clown_service_id=139,
        is_stable=True,
    )
    assert result.notification_options == [
        juggler_api.NotificationOptions(
            template_name='on_status_change',
            template_kwargs={
                'method': 'telegram',
                'login': ['mirasharf', 'taxi-alerts-other'],
                'status': STATUS,
            },
            description=None,
        ),
    ]


async def test_build_aggregate_notifications_urs_and_to(
        cron_context, clown_branches, clownductor_mock, refresh_caches,
):
    await cron_context.pg.primary.execute(
        query='INSERT INTO alert_manager.unified_recipients '
        '(clown_service_id, chats, logins, duty, '
        'receive_testing_alerts) '
        f'VALUES (139, \'{{chat}}\'::TEXT[], \'{{user}}\'::TEXT[], '
        '\'off\', FALSE);',
    )
    await cron_context.unified_recipients_cache.refresh_cache()

    # pylint: disable=protected-access
    result = await gt_notifications.build_aggregate_notifications(
        context=cron_context,
        aggregate_id=gt_common.AggregateId(
            juggler_host='some_host', juggler_service='some_other_service',
        ),
        clown_service_id=139,
        is_stable=True,
    )

    assert result.notification_options == [
        juggler_api.NotificationOptions(
            template_name='on_status_change',
            template_kwargs={
                'method': 'telegram',
                'login': ['mirasharf', 'taxi-alerts-other'],
                'status': STATUS,
            },
            description=None,
        ),
        juggler_api.NotificationOptions(
            template_name='on_status_change',
            template_kwargs={
                'method': 'telegram',
                'login': ['chat', 'user'],
                'status': STATUS,
            },
            description=None,
        ),
    ]


@pytest.mark.features_on(
    'get_duty_group_from_clown',
    'enable_update_abc_duty_info',
    'enable_clownductor_cache',
)
@pytest.mark.parametrize(
    ['service_id', 'chats', 'logins', 'duty_mode', 'expected_logins'],
    [
        (
            139,
            [],
            [],
            'to_person_on_duty',
            ['@svc_hejmdalduty:taxidutyhejmdal'],
        ),
        (139, [], [], 'to_all_duty_group_members', ['alexrasyuk', 'oboroth']),
        (
            139,
            ['chat1'],
            ['user1'],
            'to_person_on_duty',
            ['@svc_hejmdalduty:taxidutyhejmdal', 'chat1', 'user1'],
        ),
        (
            139,
            ['chat1'],
            ['user1'],
            'to_all_duty_group_members',
            ['alexrasyuk', 'chat1', 'oboroth', 'user1'],
        ),
        (
            139,
            ['chat1'],
            ['user1', 'alexrasyuk', 'oboroth'],
            'to_all_duty_group_members',
            ['alexrasyuk', 'chat1', 'oboroth', 'user1'],
        ),
        pytest.param(
            123,
            ['chat1'],
            ['login1'],
            'to_person_on_duty',
            ['@svc_hejmdalduty:taxidutyhejmdal', 'chat1', 'login1'],
            id='service with duty - alert only for on_duty',
        ),
        pytest.param(
            123,
            [],
            [],
            'to_all_duty_group_members',
            ['d1mbas'],
            id='service with duty - alert for all members',
        ),
        pytest.param(
            123,
            ['chat1'],
            ['login1'],
            'to_all_duty_group_members',
            ['chat1', 'd1mbas', 'login1'],
            id='service with duty - alert for all members with extra chats',
        ),
    ],
)
async def test_build_aggregate_notifications_to_person_on_duty(
        cron_context,
        clown_branches,
        clownductor_mock,
        mock_clown_remote_values,
        mock_abc_api_duty,
        mock_abc_api_schedules,
        mock_abc_schedules_cursor,
        mock_duty_api,
        service_id,
        chats,
        logins,
        duty_mode,
        expected_logins,
        refresh_caches,
):
    await cron_context.pg.primary.execute(
        """INSERT INTO alert_manager.unified_recipients
        (clown_service_id, chats, logins, duty, receive_testing_alerts)
        VALUES ($1, $2::TEXT[], $3::TEXT[], $4, FALSE)
        """,
        service_id,
        chats,
        logins,
        duty_mode,
    )
    await cron_context.unified_recipients_cache.refresh_cache()

    result = await gt_notifications_impl.collect_unified_recipients(
        features=cron_context.features,
        clownductor_cache=cron_context.clownductor_cache,
        unified_recipients_cache=cron_context.unified_recipients_cache,
        duty_cache=cron_context.duty_cache,
        juggler_host='some_host',
        clown_service_id=service_id,
        is_stable=True,
    )
    assert result == juggler_api.NotificationOptions(
        template_name='on_status_change',
        template_kwargs={
            'method': 'telegram',
            'login': expected_logins,
            'status': STATUS,
        },
        description=None,
    )
