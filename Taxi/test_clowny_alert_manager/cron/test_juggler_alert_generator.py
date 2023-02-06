# pylint: disable=too-many-lines

import pathlib
from typing import Set

import pytest

from clowny_alert_manager.generated.cron import run_cron
from clowny_alert_manager.internal import models
from clowny_alert_manager.internal.models import common as common_model
from clowny_alert_manager.internal.models import service as service_model


pytestmark = [  # pylint: disable=invalid-name
    pytest.mark.features_on(
        'enable_clownductor_cache',
        'enable_clownductor_hosts_update',
        'enable_upsert_from_crons',
    ),
    pytest.mark.config(
        CLOWNY_ALERT_MANAGER_UPSERT_SETTINGS={
            'by_model': {
                '__default__': {
                    'enabled': True,
                    'batch_size': 0,
                    'batch_delay': 0,
                },
            },
        },
        CLOWNY_ALERT_MANAGER_CONFIG_APPLY_QUEUE_SWITCH={
            '__default__': {'__default__': 'JugglerConfigApplyToGit'},
            'taxi-infra': {
                '__default__': 'JugglerConfigApplyToGit',
                'service-to-direct-commit': 'JugglerConfigApplyDirectly',
            },
        },
    ),
]


class _AnyInt:
    def __eq__(self, other):
        return isinstance(other, int)

    def __repr__(self):
        return self.__class__.__name__


ANY_INT = _AnyInt()


async def _check_db_state(
        cron_context,
        services=None,
        branches=None,
        templates=None,
        events=None,
        notify_options=None,
        configs=None,
        conf_tmpl_links=None,
        conf_no_links=None,
        conf_tmpl_no_links=None,
        event_no_links=None,
):
    def _compare(db_models, expected_models, repo_cls):
        assert len(db_models) == len(
            expected_models,
        ), repo_cls.model_cls.__name__
        for i, (db_model, expected_model) in enumerate(
                zip(db_models, expected_models),
        ):
            assert (
                _extract_dict(db_model.to_query_json(), expected_model.keys())
                == expected_model
            ), i

    def _extract_dict(model, keys):
        if isinstance(model, dict):
            return {x: model[x] for x in keys}
        return {x: getattr(model, x) for x in keys}

    _services = await models.ServicesRepository.fetch_many(
        context=cron_context, db_conn=cron_context.pg.primary,
    )
    if services is None:
        services = [
            {
                'service_name': 'host',
                'project_name': 'some',
                'type': service_model.ServiceType.cgroup,
                'clown_service_id': None,
                'clown_project_id': None,
            },
        ]
    if services:
        assert [
            _extract_dict(x, services[0].keys()) for x in _services.values()
        ] == services
    else:
        assert not _services, _services
    _branches = await models.BranchesRepository.fetch_many(
        context=cron_context, db_conn=cron_context.pg.primary,
    )
    if branches is None:
        branches = [
            {
                'service_id': 1,
                'clown_branch_ids': [ANY_INT],
                'names': ['child_1', 'child_2'],
                'repo_meta': common_model.RepoMeta(
                    file_path=pathlib.Path('check'),
                    file_name='check',
                    config_project='taxi',
                ),
            },
        ]
    if branches:
        assert [
            _extract_dict(x, branches[0].keys()) for x in _branches.values()
        ] == branches
    else:
        assert not _branches, _branches
    _templates = await models.TemplatesRepository.fetch_many(
        context=cron_context, db_conn=cron_context.pg.primary,
    )
    if templates is None:
        templates = [{'name': 'some_service'}, {'name': 'pkgver'}]
        templates = sorted(templates, key=lambda x: x['name'])
    if templates:
        assert [
            _extract_dict(x.to_query_json(), templates[0].keys())
            for x in sorted(_templates.values(), key=lambda x: x.name)
        ] == templates
    else:
        assert not _templates

    _configs = await models.ConfigsRepository.fetch_many(
        context=cron_context, db_conn=cron_context.pg.primary,
    )
    if configs is None:
        configs = [{'branch_id': 1}]
        configs = sorted(configs, key=lambda x: x['branch_id'])
    if configs:
        _compare(
            sorted(_configs.values(), key=lambda x: x.branch_id),
            configs,
            models.ConfigsRepository,
        )
    else:
        assert not _configs

    _events = await models.EventsRepository.fetch_many(
        context=cron_context, db_conn=cron_context.pg.primary,
    )
    if events is None:
        events = [
            {'name': 'service_without_phone', 'config_id': ANY_INT},
            {'name': 'some_other_service', 'config_id': ANY_INT},
            {'name': 'unmanageable_service', 'config_id': ANY_INT},
            {'name': 'invalid_agent_service', 'config_id': ANY_INT},
            {'name': 'invalid_mark_service', 'config_id': ANY_INT},
            {'name': 'pkgver-none', 'template_id': ANY_INT},
            {'name': 'some_service', 'template_id': ANY_INT},
            {
                'name': 'service_with_additional_telegram',
                'template_id': ANY_INT,
            },
            {'name': 'service_with_dynamic_limits', 'config_id': ANY_INT},
        ]
        events = sorted(events, key=lambda x: x['name'])
    if events:
        _compare(
            sorted(_events.values(), key=lambda x: x.name),
            events,
            models.EventsRepository,
        )
    else:
        assert not _events

    _notify_options = await models.NotificationOptionsRepository.fetch_many(
        context=cron_context, db_conn=cron_context.pg.primary,
    )
    if notify_options is None:
        notify_options = [
            {
                'logins': ['taxi-balancer-channel', 'd1mbas'],
                'name': 'balancer_channel',
                'statuses': [
                    {'from_': 'OK', 'to_': 'WARN'},
                    {'from_': 'WARN', 'to_': 'OK'},
                ],
                'type': 'telegram',
            },
            {
                'logins': ['elrusso_custom_prod', 'elrusso_admin_prod'],
                'name': 'custom_channel_prod',
                'statuses': [
                    {'from_': 'OK', 'to_': 'CRIT'},
                    {'from_': 'WARN', 'to_': 'CRIT'},
                    {'from_': 'CRIT', 'to_': 'WARN'},
                    {'from_': 'CRIT', 'to_': 'OK'},
                ],
                'type': 'telegram',
            },
            {
                'logins': ['taxi-alerts-default'],
                'name': 'default',
                'statuses': [
                    {'from_': 'OK', 'to_': 'CRIT'},
                    {'from_': 'WARN', 'to_': 'CRIT'},
                    {'from_': 'CRIT', 'to_': 'WARN'},
                    {'from_': 'CRIT', 'to_': 'OK'},
                ],
                'type': 'telegram',
            },
            {
                'logins': ['oboroth', 'taxi-alerts-other'],
                'name': 'my_telegram',
                'statuses': [
                    {'from_': 'OK', 'to_': 'CRIT'},
                    {'from_': 'WARN', 'to_': 'CRIT'},
                    {'from_': 'CRIT', 'to_': 'WARN'},
                    {'from_': 'CRIT', 'to_': 'OK'},
                ],
                'type': 'telegram',
            },
            {
                'logins': ['taxi-alerts-other'],
                'name': 'tlg_chanel',
                'statuses': [
                    {'from_': 'OK', 'to_': 'WARN'},
                    {'from_': 'WARN', 'to_': 'OK'},
                ],
                'type': 'telegram',
            },
        ]
    if notify_options:
        assert [
            _extract_dict(x.to_query_json(), notify_options[0].keys())
            for x in _notify_options.values()
        ] == notify_options
    else:
        assert not _notify_options

    await _check_db_links(
        cron_context,
        conf_tmpl_links,
        conf_no_links,
        conf_tmpl_no_links,
        event_no_links,
    )


async def _check_db_links(
        cron_context,
        conf_tmpl_links,
        conf_no_links,
        conf_tmpl_no_links,
        event_no_links,
):
    _conf_tmpl_links = await cron_context.pg.primary.fetch(
        """
            SELECT config_id, template_id
            FROM alert_manager.configs_templates_m2m
        """,
    )
    if conf_tmpl_links is None:
        conf_tmpl_links = [{'config_id': ANY_INT, 'template_id': ANY_INT}]
    if conf_tmpl_links:
        assert [dict(x) for x in _conf_tmpl_links] == conf_tmpl_links
    else:
        assert not _conf_tmpl_links

    _conf_no_links = await cron_context.pg.primary.fetch(
        """
            SELECT config_id, notification_option_id
            FROM alert_manager.configs_notifications_m2m
        """,
    )
    if conf_no_links is None:
        conf_no_links = [
            {'config_id': ANY_INT, 'notification_option_id': ANY_INT},
        ]
    if conf_no_links:
        assert [dict(x) for x in _conf_no_links] == conf_no_links
    else:
        assert not _conf_no_links

    _conf_tmpl_no_links = await cron_context.pg.primary.fetch(
        """
            SELECT config_template_id, notification_option_id
            FROM alert_manager.configs_templates_notifications_m2m
        """,
    )
    if conf_tmpl_no_links is None:
        conf_tmpl_no_links = [
            {'config_template_id': ANY_INT, 'notification_option_id': ANY_INT},
        ]
    if conf_tmpl_no_links:
        assert [dict(x) for x in _conf_tmpl_no_links] == conf_tmpl_no_links
    else:
        assert not _conf_tmpl_no_links

    _event_no_links = await cron_context.pg.primary.fetch(
        """
            SELECT event_id, notification_option_id
            FROM alert_manager.events_notifications_m2m
        """,
    )
    if event_no_links is None:
        event_no_links = [
            {'event_id': ANY_INT, 'notification_option_id': ANY_INT},
            {'event_id': ANY_INT, 'notification_option_id': ANY_INT},
            {'event_id': ANY_INT, 'notification_option_id': ANY_INT},
            {'event_id': ANY_INT, 'notification_option_id': ANY_INT},
            {'event_id': ANY_INT, 'notification_option_id': ANY_INT},
            {'event_id': ANY_INT, 'notification_option_id': ANY_INT},
        ]
    if event_no_links:
        assert [dict(x) for x in _event_no_links] == event_no_links
    else:
        assert not _event_no_links


@pytest.fixture(autouse=True)
def solomon_client_mock(mockserver):
    @mockserver.json_handler('/api/v2/projects/hejmdal/alertsFullModel')
    def _mock_alert_full_model(request):
        return mockserver.make_response(status=200, json={'items': []})


@pytest.fixture(name='get_responsible')
def get_responsible_fixture(juggler_api_mocks):
    def _impl(service):
        checks_requests = [
            x['kwargs']['json']
            for x in juggler_api_mocks.checks_add_or_update.calls
        ]
        service_data = [
            request
            for request in checks_requests
            if request['service'] == service
        ][0]
        phone_escalation = [
            notification
            for notification in service_data['notifications']
            if notification['template_name'] == 'phone_escalation'
        ][0]

        return phone_escalation['template_kwargs']['logins']

    return _impl


@pytest.mark.with_l7_check
@pytest.mark.usefixtures('juggler_alert_generator_mocks')
@pytest.mark.features_on(
    'startrek_notification_enabled',
    'enable_tg_options_for_duty',
    'get_duty_group_from_clown',
    'enable_clownductor_cache',
    'enable_clownductor_hosts_update',
)
@pytest.mark.config(
    CLOWNY_ALERT_MANAGER_NAMESPACE_SETTINGS=[
        {
            'name': '__default__',
            'dry_run': False,
            'features': {'extend_phone_escalation_with_ops': True},
        },
    ],
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
)
async def test_juggler_alert_generator(
        load_json,
        cron_context,
        juggler_api_mocks,
        clownductor_mock,
        clown_parameters,
        clown_branches,
        duty_api_mocks,
):
    await cron_context.clownductor_cache.refresh_cache()
    await run_cron.main(
        ['clowny_alert_manager.crontasks.juggler_alert_generator', '-t', '0'],
    )

    assert [
        x['kwargs']['json']
        for x in juggler_api_mocks.checks_add_or_update.calls
    ] == load_json('update_checks_requests.json')
    await _check_db_state(
        cron_context,
        templates=[
            {'name': 'l7-monitorings'},
            {'name': 'pkgver'},
            {'name': 'some_service'},
        ],
        events=[
            {'name': 'invalid_agent_service', 'config_id': ANY_INT},
            {'name': 'invalid_mark_service', 'config_id': ANY_INT},
            {'name': 'l7_balancer_cpu_usage', 'template_id': ANY_INT},
            {'name': 'l7_balancer_cpu_wait_cores', 'template_id': ANY_INT},
            {'name': 'l7_balancer_logs_vol_usage', 'template_id': ANY_INT},
            {'name': 'l7_balancer_mem_usage', 'template_id': ANY_INT},
            {'name': 'pkgver-none', 'template_id': ANY_INT},
            {
                'name': 'service_with_additional_telegram',
                'template_id': ANY_INT,
            },
            {'name': 'service_with_dynamic_limits', 'config_id': ANY_INT},
            {'name': 'service_without_phone', 'config_id': ANY_INT},
            {'name': 'some_other_service', 'config_id': ANY_INT},
            {'name': 'some_service', 'template_id': ANY_INT},
            {'name': 'unmanageable_service', 'config_id': ANY_INT},
        ],
        services=[
            {
                'clown_project_id': None,
                'clown_service_id': None,
                'project_name': 'some',
                'service_name': 'host',
                'type': service_model.ServiceType.cgroup,
            },
            {
                'clown_project_id': None,
                'clown_service_id': None,
                'project_name': 'taxi',
                'service_name': 'abt',
                'type': service_model.ServiceType.host,
            },
        ],
        branches=[
            {
                'clown_branch_ids': [ANY_INT],
                'names': ['child_1', 'child_2'],
                'repo_meta': common_model.RepoMeta(
                    file_path=pathlib.Path('check'),
                    file_name='check',
                    config_project='taxi',
                ),
                'service_id': 1,
            },
            {
                'clown_branch_ids': [],
                'names': ['taxi_abt_stable'],
                'repo_meta': common_model.RepoMeta(
                    file_path=pathlib.Path('balancer_check'),
                    file_name='balancer_check',
                    config_project='taxi',
                ),
                'service_id': 2,
            },
        ],
        configs=[{'branch_id': 1}, {'branch_id': 2}],
        conf_tmpl_links=[
            {'config_id': ANY_INT, 'template_id': ANY_INT},
            {'config_id': ANY_INT, 'template_id': ANY_INT},
        ],
    )


@pytest.mark.usefixtures('juggler_alert_generator_mocks')
@pytest.mark.config(
    CLOWNY_ALERT_MANAGER_NAMESPACE_SETTINGS=[
        {'name': '__default__', 'dry_run': True},
    ],
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
)
@pytest.mark.features_on(
    'startrek_notification_enabled',
    'enable_tg_options_for_duty',
    'get_duty_group_from_clown',
)
async def test_juggler_alert_generator_dry_run(
        cron_context,
        juggler_api_mocks,
        clown_parameters,
        clown_branches,
        duty_api_mocks,
):
    await run_cron.main(
        ['clowny_alert_manager.crontasks.juggler_alert_generator', '-t', '0'],
    )

    assert not juggler_api_mocks.checks_add_or_update.calls
    await _check_db_state(cron_context)


@pytest.mark.usefixtures('juggler_alert_generator_mocks')
@pytest.mark.config(
    CLOWNY_ALERT_MANAGER_NAMESPACE_SETTINGS=[
        {'name': '__default__', 'dry_run': False},
    ],
)
@pytest.mark.parametrize('smart_cleanup, expected_deletions', [(True, 4)])
async def test_juggler_alert_generator_cleanup(
        cron_context,
        juggler_api_mocks,
        taxi_config,
        smart_cleanup,
        expected_deletions,
):
    features = taxi_config.get('CLOWNY_ALERT_MANAGER_FEATURES')
    features.update(
        {
            'juggler_alert_generator_cleanup_checks': True,
            'juggler_alert_generator_smart_cleanup': smart_cleanup,
        },
    )
    taxi_config.set_values({'CLOWNY_ALERT_MANAGER_FEATURES': features})

    await run_cron.main(
        ['clowny_alert_manager.crontasks.juggler_alert_generator', '-t', '0'],
    )

    assert len(juggler_api_mocks.checks_remove.calls) == expected_deletions
    await _check_db_state(cron_context)


@pytest.mark.usefixtures('juggler_alert_generator_mocks')
@pytest.mark.config(
    CLOWNY_ALERT_MANAGER_NAMESPACE_SETTINGS=[
        {'name': '__default__', 'dry_run': True},
    ],
)
async def test_juggler_alert_generator_cleanup_dry_run(
        cron_context, juggler_api_mocks, taxi_config,
):
    features = taxi_config.get('CLOWNY_ALERT_MANAGER_FEATURES')
    features.update(
        {
            'juggler_alert_generator_cleanup_checks': True,
            'juggler_alert_generator_smart_cleanup': True,
        },
    )
    taxi_config.set_values({'CLOWNY_ALERT_MANAGER_FEATURES': features})

    await run_cron.main(
        ['clowny_alert_manager.crontasks.juggler_alert_generator', '-t', '0'],
    )

    assert not juggler_api_mocks.checks_remove.calls
    await _check_db_state(cron_context)


@pytest.mark.usefixtures('juggler_alert_generator_mocks')
@pytest.mark.config(
    CLOWNY_ALERT_MANAGER_NAMESPACE_SETTINGS=[
        {'name': '__default__', 'dry_run': False},
    ],
)
async def test_juggler_alert_generator_set_downtimes(
        cron_context, juggler_api_mocks, taxi_config,
):
    features = taxi_config.get('CLOWNY_ALERT_MANAGER_FEATURES')
    features.update({'juggler_alert_generator_set_downtimes': True})
    taxi_config.set_values({'CLOWNY_ALERT_MANAGER_FEATURES': features})

    await run_cron.main(
        ['clowny_alert_manager.crontasks.juggler_alert_generator', '-t', '0'],
    )

    assert len(juggler_api_mocks.set_downtimes.calls) == 6
    assert len(juggler_api_mocks.system_config_tree.calls) == 1
    await _check_db_state(cron_context)


@pytest.mark.usefixtures('juggler_alert_generator_mocks')
@pytest.mark.config(
    CLOWNY_ALERT_MANAGER_NAMESPACE_SETTINGS=[
        {'name': '__default__', 'dry_run': True},
    ],
)
async def test_juggler_alert_generator_set_downtimes_dry_run(
        cron_context, juggler_api_mocks, taxi_config,
):
    features = taxi_config.get('CLOWNY_ALERT_MANAGER_FEATURES')
    features.update({'juggler_alert_generator_set_downtimes': True})
    taxi_config.set_values({'CLOWNY_ALERT_MANAGER_FEATURES': features})

    await run_cron.main(
        ['clowny_alert_manager.crontasks.juggler_alert_generator', '-t', '0'],
    )

    assert not juggler_api_mocks.set_downtimes.calls
    assert len(juggler_api_mocks.system_config_tree.calls) == 1
    await _check_db_state(cron_context)


@pytest.mark.usefixtures('juggler_alert_generator_mocks')
@pytest.mark.check_broken()
@pytest.mark.config(
    CLOWNY_ALERT_MANAGER_NAMESPACE_SETTINGS=[
        {'name': '__default__', 'dry_run': False},
    ],
)
@pytest.mark.parametrize('smart_cleanup', [True, False])
async def test_juggler_alert_generator_check_broken(
        cron_context, juggler_api_mocks, taxi_config, smart_cleanup,
):
    features = taxi_config.get('CLOWNY_ALERT_MANAGER_FEATURES')
    features.update(
        {
            'juggler_alert_generator_cleanup_checks': True,
            'juggler_alert_generator_smart_cleanup': smart_cleanup,
        },
    )
    taxi_config.set_values({'CLOWNY_ALERT_MANAGER_FEATURES': features})

    await run_cron.main(
        ['clowny_alert_manager.crontasks.juggler_alert_generator', '-t', '0'],
    )

    assert not juggler_api_mocks.checks_remove.calls
    await _check_db_state(
        cron_context,
        services=[],
        branches=[],
        events=[
            {'name': 'pkgver-none', 'template_id': ANY_INT, 'config_id': None},
            {
                'name': 'service_with_additional_telegram',
                'template_id': ANY_INT,
            },
            {
                'name': 'some_service',
                'template_id': ANY_INT,
                'config_id': None,
            },
        ],
        configs=[],
        conf_tmpl_links=[],
        conf_no_links=[],
        conf_tmpl_no_links=[],
        event_no_links=[],
    )


@pytest.mark.usefixtures('juggler_alert_generator_mocks')
@pytest.mark.config(
    CLOWNY_ALERT_MANAGER_NAMESPACE_SETTINGS=[
        {'name': '__default__', 'dry_run': False},
    ],
)
@pytest.mark.telegram_opt_broken()
@pytest.mark.parametrize(
    'smart_cleanup, expected_deletions', [(True, 4), (False, 0)],
)
async def test_juggler_alert_generator_telegram_opt_broken(
        cron_context,
        juggler_api_mocks,
        taxi_config,
        smart_cleanup,
        expected_deletions,
):
    features = taxi_config.get('CLOWNY_ALERT_MANAGER_FEATURES')
    features.update(
        {
            'juggler_alert_generator_cleanup_checks': True,
            'juggler_alert_generator_smart_cleanup': smart_cleanup,
        },
    )
    taxi_config.set_values({'CLOWNY_ALERT_MANAGER_FEATURES': features})

    await run_cron.main(
        ['clowny_alert_manager.crontasks.juggler_alert_generator', '-t', '0'],
    )

    assert len(juggler_api_mocks.checks_add_or_update.calls) == 1
    assert len(juggler_api_mocks.checks_remove.calls) == expected_deletions
    await _check_db_state(
        cron_context,
        notify_options=[],
        configs=[],
        events=[
            {'name': 'pkgver-none', 'template_id': ANY_INT},
            {
                'name': 'service_with_additional_telegram',
                'template_id': ANY_INT,
            },
            {'name': 'some_service', 'template_id': ANY_INT},
        ],
        conf_no_links=[],
        conf_tmpl_no_links=[],
        event_no_links=[],
        conf_tmpl_links=[],
    )


@pytest.mark.usefixtures('juggler_alert_generator_mocks')
@pytest.mark.config(
    CLOWNY_ALERT_MANAGER_NAMESPACE_SETTINGS=[
        {'name': '__default__', 'dry_run': False},
    ],
)
@pytest.mark.template_broken()
@pytest.mark.parametrize('smart_cleanup, expected_deletions', [(True, 4)])
async def test_juggler_alert_generator_template_broken(
        cron_context,
        juggler_api_mocks,
        taxi_config,
        smart_cleanup,
        expected_deletions,
):
    features = taxi_config.get('CLOWNY_ALERT_MANAGER_FEATURES')
    features.update(
        {
            'juggler_alert_generator_cleanup_checks': True,
            'juggler_alert_generator_smart_cleanup': smart_cleanup,
        },
    )
    taxi_config.set_values({'CLOWNY_ALERT_MANAGER_FEATURES': features})

    await run_cron.main(
        ['clowny_alert_manager.crontasks.juggler_alert_generator', '-t', '0'],
    )

    assert len(juggler_api_mocks.checks_add_or_update.calls) == 6
    assert len(juggler_api_mocks.checks_remove.calls) == expected_deletions
    await _check_db_state(
        cron_context,
        templates=[{'name': 'pkgver'}],
        events=[
            {'name': 'invalid_agent_service'},
            {'name': 'invalid_mark_service'},
            {'name': 'pkgver-none'},
            {'name': 'service_with_additional_telegram'},
            {'name': 'service_with_dynamic_limits'},
            {'name': 'service_without_phone'},
            {'name': 'some_other_service'},
            {'name': 'unmanageable_service'},
        ],
    )


@pytest.mark.usefixtures('juggler_alert_generator_mocks')
@pytest.mark.config(
    CLOWNY_ALERT_MANAGER_NAMESPACE_SETTINGS=[
        {'name': '__default__', 'dry_run': False},
    ],
)
async def test_juggler_alert_generator_update_changed_checks(
        cron_context, juggler_api_mocks, taxi_config,
):
    features = taxi_config.get('CLOWNY_ALERT_MANAGER_FEATURES')
    features.update({'juggler_alert_generator_update_changed': True})
    features.update({'juggler_alert_generator_show_diff': True})
    taxi_config.set_values({'CLOWNY_ALERT_MANAGER_FEATURES': features})

    await run_cron.main(
        ['clowny_alert_manager.crontasks.juggler_alert_generator', '-t', '0'],
    )

    assert len(juggler_api_mocks.checks_add_or_update.calls) == 6
    assert len(juggler_api_mocks.system_config_tree.calls) == 1
    await _check_db_state(cron_context)


@pytest.mark.usefixtures('juggler_alert_generator_mocks')
@pytest.mark.config(
    CLOWNY_ALERT_MANAGER_NAMESPACE_SETTINGS=[
        {'name': '__default__', 'dry_run': True},
    ],
)
async def test_juggler_alert_generator_update_changed_checks_dry_run(
        cron_context, juggler_api_mocks, taxi_config,
):
    features = taxi_config.get('CLOWNY_ALERT_MANAGER_FEATURES')
    features.update({'juggler_alert_generator_update_changed': True})
    features.update({'juggler_alert_generator_show_diff': True})
    taxi_config.set_values({'CLOWNY_ALERT_MANAGER_FEATURES': features})

    await run_cron.main(
        ['clowny_alert_manager.crontasks.juggler_alert_generator', '-t', '0'],
    )

    assert not juggler_api_mocks.checks_add_or_update.calls
    assert len(juggler_api_mocks.system_config_tree.calls) == 1
    await _check_db_state(cron_context)


@pytest.mark.now('2020-06-21T15:00:00')
@pytest.mark.usefixtures('juggler_alert_generator_mocks')
@pytest.mark.config(
    CLOWNY_ALERT_MANAGER_NAMESPACE_SETTINGS=[
        {'name': '__default__', 'dry_run': False},
    ],
    CLOWNY_ALERT_MANAGER_DUTY_GROUPS=[
        {'id': 'some_duty_group_id', 'duty_mode': 'full'},
    ],
)
@pytest.mark.features_on('enable_tg_options_for_duty')
@pytest.mark.parametrize(
    'phone_escalated_logins',
    [
        pytest.param(
            [
                'abc_duty_user_2222',
                'current-other_duty-devop',
                'next-other_duty-devop',
            ],
            marks=pytest.mark.config(
                CLOWNY_ALERT_MANAGER_FEATURES={
                    'juggler_alert_generator_enabled': True,
                    'get_duty_group_from_clown': False,
                    'startrek_notification_enabled': True,
                },
                CLOWNY_ALERT_MANAGER_NAMESPACE_SETTINGS=[
                    {'dry_run': False, 'name': '__default__'},
                ],
            ),
            id='feature_disabled',
        ),
        pytest.param(
            [
                'abc_duty_user_2222',
                'current-duty-user',
                'current-other_duty-devop',
                'current-other_duty-devop',
                'next-duty-user',
                'next-other_duty-devop',
                'next-other_duty-devop',
            ],
            marks=pytest.mark.config(
                CLOWNY_ALERT_MANAGER_FEATURES={
                    'juggler_alert_generator_enabled': True,
                    'get_duty_group_from_clown': True,
                    'startrek_notification_enabled': True,
                },
                CLOWNY_ALERT_MANAGER_NAMESPACE_SETTINGS=[
                    {'dry_run': False, 'name': '__default__'},
                    {
                        'name': 'taxi.eda',
                        'dry_run': False,
                        'features': {'extend_phone_escalation_with_ops': True},
                    },
                ],
            ),
            id='feature_enabled',
        ),
    ],
)
async def test_get_duty_group_from_clown(
        cron_context,
        clown_parameters,
        clown_branches,
        duty_api_mocks,
        juggler_api_mocks,
        phone_escalated_logins,
):

    await run_cron.main(
        ['clowny_alert_manager.crontasks.juggler_alert_generator', '-t', '0'],
    )

    checks_add_or_update_calls = juggler_api_mocks.checks_add_or_update.calls
    assert len(checks_add_or_update_calls) == 6
    assert (
        sorted(
            [
                login
                for x in checks_add_or_update_calls
                for notifi in x['kwargs']['json']['notifications']
                if notifi.get('template_name') == 'phone_escalation'
                for login in notifi['template_kwargs']['logins']
            ],
        )
        == phone_escalated_logins
    )

    assert len(juggler_api_mocks.system_config_tree.calls) == 1
    await _check_db_state(cron_context)


def get_recipients(notifications) -> Set[str]:
    assert notifications is not None
    recipients_list = []
    for x in notifications:
        recipients_list.extend(x['template_kwargs'].get('login', []))
    return set(recipients_list)


@pytest.mark.usefixtures('juggler_alert_generator_mocks')
@pytest.mark.config(
    CLOWNY_ALERT_MANAGER_NAMESPACE_SETTINGS=[
        {'name': '__default__', 'dry_run': False},
    ],
)
async def test_juggler_alert_generator_additional_telegram(
        cron_context, juggler_api_mocks, taxi_config,
):
    features = taxi_config.get('CLOWNY_ALERT_MANAGER_FEATURES')
    features.update({'juggler_alert_generator_update_changed': True})
    features.update({'juggler_alert_generator_show_diff': True})
    taxi_config.set_values({'CLOWNY_ALERT_MANAGER_FEATURES': features})

    await run_cron.main(
        ['clowny_alert_manager.crontasks.juggler_alert_generator', '-t', '0'],
    )

    calls = juggler_api_mocks.checks_add_or_update.calls

    assert len(calls) == 6

    for call in calls:
        request = call['kwargs']['json']
        if request['service'] != 'service_with_additional_telegram':
            continue
        recipients = get_recipients(request['notifications'])
        assert recipients == {
            'oboroth',  # from additional telegram
            'taxi-alerts-other',  # from the use of template
        }


CLOWNY_ALERT_MANAGER_SETTINGS_GIT = {
    'duty_abc_url': {'$mockserver': '/api/v4/duty/shifts/service/'},
    'duty_url': {'$mockserver': '/api/duty_group/group_id/'},
    'projects': {
        'taxi': {
            'default_namespace': 'taxi.eda',
            'duty': [
                {'duty_taxi': 'default_duty', 'namespace': 'default'},
                {'duty_taxi': 'other_duty', 'namespace': 'taxi.eda'},
            ],
            'mark_prefix': 'taxi-monitoring',
            'phone_escalation_options': {
                'delay': 900,
                'on_success_next_call_delay': 60,
                'repeat': 2,
            },
            'repo': 'https://github.yandex-team.ru/taxi/infra-cfg-juggler.git',
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
}


@pytest.mark.config(
    CLOWNY_ALERT_MANAGER_SETTINGS=CLOWNY_ALERT_MANAGER_SETTINGS_GIT,
    CLOWNY_ALERT_MANAGER_NAMESPACE_SETTINGS=[
        {'name': '__default__', 'dry_run': False},
    ],
)
@pytest.mark.features_on('use_arc')
async def test_repo_from_tarball(
        taxi_clowny_alert_manager_web,
        patch,
        juggler_api_mocks,
        clown_parameters,
        clown_branches,
        duty_api_mocks,
        pack_repo,
):
    repo_tarball = pack_repo('infra-cfg-juggler_simple')

    # use patch instead of testpoint('repo_tarball_path') as cron is run
    # manually, not with testsuite
    @patch('clowny_alert_manager.internal.utils.repo._get_tarball_path')
    async def _patch_get_tarball_path(_):
        return str(repo_tarball)

    await run_cron.main(
        ['clowny_alert_manager.crontasks.juggler_alert_generator', '-t', '0'],
    )

    logins = []
    for call in juggler_api_mocks.checks_add_or_update.calls:
        request_json = call['kwargs']['json']
        for notification in request_json['notifications']:
            logins.extend(notification['template_kwargs'].get('login', []))

    assert 'taxi-alerts-default-from-tarball' in logins


@pytest.mark.config(
    CLOWNY_ALERT_MANAGER_SETTINGS=CLOWNY_ALERT_MANAGER_SETTINGS_GIT,
    CLOWNY_ALERT_MANAGER_NAMESPACE_SETTINGS=[
        {'name': '__default__', 'dry_run': False},
    ],
)
@pytest.mark.features_on('use_arc')
@pytest.mark.parametrize(
    ['repo', 'expected_checks_requests'],
    [
        pytest.param(
            'infra-cfg-juggler_simple',
            'exp_checks_requests_simple.json',
            id='reference run',
        ),
        pytest.param(
            'infra-cfg-juggler_service_disabled',
            'exp_checks_requests_service_disabled.json',
            id=(
                'same as reference run, but disabled is set to true '
                'for `some_other_service`'
            ),
        ),
    ],
)
async def test_service_disabled(
        taxi_clowny_alert_manager_web,
        load_json,
        patch,
        juggler_api_mocks,
        clown_parameters,
        clown_branches,
        duty_api_mocks,
        pack_repo,
        repo,
        expected_checks_requests,
):
    repo_tarball = pack_repo(repo)

    # use patch instead of testpoint('repo_tarball_path') as cron is run
    # manually, not with testsuite
    @patch('clowny_alert_manager.internal.utils.repo._get_tarball_path')
    async def _patch_get_tarball_path(_):
        return str(repo_tarball)

    await run_cron.main(
        ['clowny_alert_manager.crontasks.juggler_alert_generator', '-t', '0'],
    )

    checks_requests = [
        x['kwargs']['json']
        for x in juggler_api_mocks.checks_add_or_update.calls
    ]

    assert checks_requests == load_json(expected_checks_requests)


@pytest.mark.config(
    CLOWNY_ALERT_MANAGER_SETTINGS=CLOWNY_ALERT_MANAGER_SETTINGS_GIT,
)
@pytest.mark.features_on('use_arc')
async def test_proxy_duty_group_phone_escalation(
        mockserver,
        load_json,
        patch,
        juggler_api_mocks,
        get_responsible,
        duty_api_mocks,
        pack_repo,
):
    repo_tarball = pack_repo('infra-cfg-juggler_proxy_duty_group')

    # use patch instead of testpoint('repo_tarball_path') as cron is run
    # manually, not with testsuite
    @patch('clowny_alert_manager.internal.utils.repo._get_tarball_path')
    async def _patch_get_tarball_path(_):
        return str(repo_tarball)

    await run_cron.main(
        ['clowny_alert_manager.crontasks.juggler_alert_generator', '-t', '0'],
    )

    assert get_responsible('some_other_service') == [
        '@svc_lavka_efficiency:autoorder_stability',
        'johnyh',
    ]


@pytest.mark.config(
    CLOWNY_ALERT_MANAGER_SETTINGS=CLOWNY_ALERT_MANAGER_SETTINGS_GIT,
    CLOWNY_ALERT_MANAGER_NAMESPACE_SETTINGS=[
        {'name': '__default__', 'dry_run': False},
    ],
    CLOWNY_ALERT_MANAGER_DUTY_GROUPS=[
        {'duty_mode': 'full', 'id': 'hejmdalduty:taxidutyhejmdal'},
    ],
)
@pytest.mark.features_on('use_arc', 'get_duty_group_from_clown')
@pytest.mark.now('2020-06-21T15:00:00')
async def test_custom_abc_duty_phone_escalation(
        mockserver,
        load_json,
        patch,
        juggler_api_mocks,
        duty_api_mocks,
        pack_repo,
        get_responsible,
):
    repo_tarball = pack_repo('infra-cfg-juggler_custom_abc_duty')

    # use patch instead of testpoint('repo_tarball_path') as cron is run
    # manually, not with testsuite
    @patch('clowny_alert_manager.internal.utils.repo._get_tarball_path')
    async def _patch_get_tarball_path(_):
        return str(repo_tarball)

    @mockserver.json_handler('/client-abc/v4/duty/schedules-cursor/')
    def _schedules_cursor_handler(request):
        assert set(request.query['fields'].split(',')) == {
            'id',
            'slug',
            'algorithm',
        }
        assert request.query['service__slug'] == 'hejmdalduty'

        results = [
            {
                'id': 2902,
                'algorithm': 'manual_order',
                'slug': 'taxidutyhejmdal',
            },
            {'id': 2903, 'slug': 'taxihejmdalduty'},
            {'id': 2904, 'slug': 'hejmdaltaxiduty'},
            {'id': 2905, 'slug': 'hejmdaldutytaxi'},
        ]

        return {'next': None, 'previous': None, 'results': results}

    @mockserver.json_handler(
        r'/client-abc/v4/duty/schedules/(?P<schedule_id>\d+)/', regex=True,
    )
    def _schedules_handler(request, schedule_id):
        assert schedule_id == '2902'
        assert set(request.query['fields'].split(',')) == {
            'orders.person.login',
            'orders.order',
        }

        return {
            'orders': [
                {'person': {'login': login}, 'order': order}
                for order, login in [
                    (2, 'd1mbas'),
                    (3, 'htorobo'),
                    (1, 'sabm1d'),
                    (0, 'oboroth'),
                ]
            ] + [{'person': None, 'order': 666}],
        }

    @mockserver.json_handler('/client-abc/v4/duty/shifts/')
    def _shifts_handler(request):
        schedule_id = request.query['schedule']
        assert request.query['date_from'] == '2020-06-21'
        assert request.query['date_to'] == '2020-07-31'

        assert set(request.query['fields'].split(',')) == {'person.login'}

        logins = {'2903': ['a', 'b', 'c'], '2904': ['b', 'c'], '2905': []}[
            schedule_id
        ]

        return {'results': [{'person': {'login': login}} for login in logins]}

    @mockserver.json_handler('/client-abc/v4/duty/on_duty/')
    def _on_duty_handler(request):
        assert request.query['service__slug'] == 'hejmdalduty'
        assert set(request.query['fields'].split(',')) == {
            'schedule.id',
            'person.login',
        }

        return [
            {'schedule': {'id': 2903}, 'person': {'login': 'b'}},
            {'schedule': {'id': 2902}, 'person': {'login': 'd1mbas'}},
        ]

    @mockserver.handler('/clownductor/v1/parameters/remote_values/')
    async def _remote_values_handler(request):
        if (
                request.query['service_id'] == '2'
                and request.query['branch_id'] == '2'
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

    await run_cron.main(
        ['clowny_alert_manager.crontasks.juggler_alert_generator', '-t', '0'],
    )

    assert get_responsible('some_other_service') == [
        'd1mbas',  # primary on_duty, order=2
        'b',  # backup on_duty
        'htorobo',  # person from primary schedule, order=3
        'oboroth',  # person from primary schedule, order=0
        'sabm1d',  # person from primary schedule, order=1
        'c',  # person from backup schedule__slug=hejmdaltaxiduty
        'a',  # person from backup schedule__slug=taxihejmdalduty
    ]


@pytest.mark.config(
    CLOWNY_ALERT_MANAGER_SETTINGS=CLOWNY_ALERT_MANAGER_SETTINGS_GIT,
    CLOWNY_ALERT_MANAGER_NAMESPACE_SETTINGS=[
        {'name': '__default__', 'dry_run': False},
    ],
    CLOWNY_ALERT_MANAGER_DUTY_GROUPS=[{'duty_mode': 'full', 'id': '666'}],
)
@pytest.mark.features_on(
    'use_arc',
    'get_duty_group_from_clown',
    'juggler_alert_generator_cleanup_checks',
    'juggler_alert_generator_smart_cleanup',
)
@pytest.mark.parametrize(
    'expect_aggregate_updated, expected_responsible',
    [
        pytest.param(
            True,
            ['eda', 'ops'],
            id='default config: fallback_to_ns_responsible',
        ),
        pytest.param(
            False,
            None,
            marks=pytest.mark.config(
                CLOWNY_ALERT_MANAGER_ESCALATION_BLACKLIST={
                    '__default__': 'keep_aggregate',
                },
            ),
            id='keep_aggregate',
        ),
        pytest.param(
            True,
            None,
            marks=pytest.mark.config(
                CLOWNY_ALERT_MANAGER_ESCALATION_BLACKLIST={
                    '__default__': 'drop_escalation',
                },
            ),
            id='drop_escalation',
        ),
        pytest.param(
            True,
            None,
            marks=pytest.mark.config(
                CLOWNY_ALERT_MANAGER_ESCALATION_BLACKLIST={
                    '__default__': 'fallback_to_ns_responsible',
                    'taxi.eda': {
                        '__default__': 'drop_escalation',
                        'nonexistent_host': {
                            '__default__': 'fallback_to_ns_responsible',
                        },
                    },
                    'nonexistent_namespace': {
                        '__default__': 'fallback_to_ns_responsible',
                    },
                },
            ),
            id='namespace-level settings',
        ),
        pytest.param(
            True,
            None,
            marks=pytest.mark.config(
                CLOWNY_ALERT_MANAGER_ESCALATION_BLACKLIST={
                    '__default__': 'fallback_to_ns_responsible',
                    'taxi.eda': {
                        '__default__': 'fallback_to_ns_responsible',
                        'some_host': {
                            '__default__': 'drop_escalation',
                            'nonexistent_service': (
                                'fallback_to_ns_responsible'
                            ),
                        },
                        'nonexistent_host': {
                            '__default__': 'fallback_to_ns_responsible',
                        },
                    },
                    'nonexistent_namespace': {
                        '__default__': 'fallback_to_ns_responsible',
                    },
                },
            ),
            id='host-level settings',
        ),
        pytest.param(
            True,
            None,
            marks=pytest.mark.config(
                CLOWNY_ALERT_MANAGER_ESCALATION_BLACKLIST={
                    '__default__': 'fallback_to_ns_responsible',
                    'taxi.eda': {
                        '__default__': 'fallback_to_ns_responsible',
                        'some_host': {
                            '__default__': 'fallback_to_ns_responsible',
                            'some_other_service': 'drop_escalation',
                            'nonexistent_service': (
                                'fallback_to_ns_responsible'
                            ),
                        },
                        'nonexistent_host': {
                            '__default__': 'fallback_to_ns_responsible',
                        },
                    },
                    'nonexistent_namespace': {
                        '__default__': 'fallback_to_ns_responsible',
                    },
                },
            ),
            id='service-level settings',
        ),
    ],
)
async def test_fallback_on_empty_responsibles(
        mockserver,
        load_json,
        patch,
        juggler_api_mocks,
        mock_juggler_get_checks,
        pack_repo,
        expect_aggregate_updated,
        expected_responsible,
):
    repo_tarball = pack_repo('infra-cfg-juggler_phone_escalation')

    # use patch instead of testpoint('repo_tarball_path') as cron is run
    # manually, not with testsuite
    @patch('clowny_alert_manager.internal.utils.repo._get_tarball_path')
    async def _patch_get_tarball_path(_):
        return str(repo_tarball)

    @mockserver.handler('/clownductor/v1/parameters/remote_values/')
    async def _remote_values_handler(request):
        if (
                request.query['service_id'] == '2'
                and request.query['branch_id'] == '2'
        ):
            return mockserver.make_response(
                status=200,
                json={
                    'subsystems': [
                        {
                            'subsystem_name': 'service_info',
                            'parameters': [
                                {'name': 'duty_group_id', 'value': '666'},
                            ],
                        },
                    ],
                },
            )

        return mockserver.make_response(
            status=404, json={'code': 'not-found', 'message': 'not-found'},
        )

    @mockserver.json_handler('/duty-api/api/duty_group', prefix=True)
    def _duty_handler(request):
        if request.query['group_id'] == 'other_duty':
            return {
                'result': {
                    'data': {
                        'staffGroups': [],
                        'suggestedEvents': [{'user': 'ops'}],
                        'currentEvent': {'user': 'eda'},
                    },
                    'ok': True,
                },
            }

        return {
            'result': {
                'data': {
                    'staffGroups': [],
                    'suggestedEvents': [],
                    'currentEvent': None,
                },
                'ok': True,
            },
        }

    mock_juggler_get_checks(
        load_json('server_check_keep.json'), ignore_filters=True,
    )

    await run_cron.main(
        ['clowny_alert_manager.crontasks.juggler_alert_generator', '-t', '0'],
    )

    check_remove_requests = [
        x['kwargs']['params'] for x in juggler_api_mocks.checks_remove.calls
    ]

    assert len(check_remove_requests) == 1
    assert check_remove_requests[0]['service_name'] == 'some_service'

    checks_requests = [
        x['kwargs']['json']
        for x in juggler_api_mocks.checks_add_or_update.calls
    ]

    service_data = None
    for request in checks_requests:
        if request['service'] == 'some_other_service':
            service_data = request

    if not expect_aggregate_updated:
        assert service_data is None
        return

    phone_escalation = None
    for notification in service_data['notifications']:
        if notification['template_name'] == 'phone_escalation':
            phone_escalation = notification

    if expected_responsible is None:
        assert phone_escalation is None
        return

    assert (
        phone_escalation['template_kwargs']['logins'] == expected_responsible
    )


@pytest.mark.config(
    CLOWNY_ALERT_MANAGER_SETTINGS=CLOWNY_ALERT_MANAGER_SETTINGS_GIT,
    CLOWNY_ALERT_MANAGER_NAMESPACE_SETTINGS=[
        {'name': '__default__', 'dry_run': False},
    ],
)
@pytest.mark.features_on('use_arc')
async def test_children_objects(
        mockserver,
        load_json,
        patch,
        juggler_api_mocks,
        duty_api_mocks,
        pack_repo,
):
    repo_tarball = pack_repo('infra-cfg-juggler_children_objects')

    # use patch instead of testpoint('repo_tarball_path') as cron is run
    # manually, not with testsuite
    @patch('clowny_alert_manager.internal.utils.repo._get_tarball_path')
    async def _patch_get_tarball_path(_):
        return str(repo_tarball)

    await run_cron.main(
        ['clowny_alert_manager.crontasks.juggler_alert_generator', '-t', '0'],
    )

    checks_requests = [
        x['kwargs']['json']
        for x in juggler_api_mocks.checks_add_or_update.calls
    ]

    assert checks_requests == load_json(
        'expected_checks_requests_children_object.json',
    )


@pytest.mark.config(
    CLOWNY_ALERT_MANAGER_SETTINGS=CLOWNY_ALERT_MANAGER_SETTINGS_GIT,
    CLOWNY_ALERT_MANAGER_NAMESPACE_SETTINGS=[
        {'name': '__default__', 'dry_run': False},
    ],
)
@pytest.mark.features_on('use_arc')
async def test_env_folders(
        mockserver,
        load_json,
        patch,
        juggler_api_mocks,
        duty_api_mocks,
        pack_repo,
):
    repo_tarball = pack_repo('infra-cfg-juggler_env_folders')

    # use patch instead of testpoint('repo_tarball_path') as cron is run
    # manually, not with testsuite
    @patch('clowny_alert_manager.internal.utils.repo._get_tarball_path')
    async def _patch_get_tarball_path(_):
        return str(repo_tarball)

    await run_cron.main(
        ['clowny_alert_manager.crontasks.juggler_alert_generator', '-t', '0'],
    )

    checks_requests = [
        x['kwargs']['json']
        for x in juggler_api_mocks.checks_add_or_update.calls
    ]

    assert checks_requests == load_json('exp_checks_requests_env_folders.json')
