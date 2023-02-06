import dataclasses

import pytest

from clownductor.internal import branches
from clownductor.internal.param_defs.subsystems import service_info
from clownductor.internal.sync_duty_admins import models
from clownductor.internal.sync_duty_admins import (
    rtc_targets as rtc_targets_module,
)
from clownductor.internal.sync_duty_admins import targets as targets_module


async def _init_params(context):
    config = service_info.ServiceInfoEnvConfig()
    config.set('duty_group_id', 'abc')
    await context.service_manager.parameters.save_subsystem_config(
        service_id=1,
        branch_id=1,
        subsystem_name='service_info',
        config=config,
        is_remote=True,
    )

    config = service_info.ServiceInfoEnvConfig()
    config.set(
        'duty', {'abc_slug': 'some_abc', 'primary_schedule': 'some_schedule'},
    )
    await context.service_manager.parameters.save_subsystem_config(
        service_id=4,
        branch_id=3,
        subsystem_name='service_info',
        config=config,
        is_remote=True,
    )


def _duty_admins_conf(*no_duty_stable):
    return {
        'enabled': True,
        'dry_run': False,
        'enabled_for_all': True,
        'no_duty_in_stable_owners': no_duty_stable,
    }


def _duty_settings_conf(
        use_project_owners=None, give_root_from_idm_for_duty_excludes=True,
):
    result = {
        '__default__': {
            '__default__': {
                'remove_old_admins': True,
                'add_admins_from_idm_for_project': True,
                'add_admins_from_idm_for_service': True,
                'give_root_from_idm_for_duty_excludes': (
                    give_root_from_idm_for_duty_excludes
                ),
            },
        },
    }
    if use_project_owners is not None:
        result['__default__']['__default__'][
            'use_project_owners'
        ] = use_project_owners
    return result


@pytest.mark.pgsql(
    'clownductor', files=['init_services.sql', 'init_default_roles.sql'],
)
@pytest.mark.config(
    CLOWNDUCTOR_SYNC_DUTY_ADMINS=_duty_admins_conf(),
    CLOWNDUCTOR_SYNC_DUTY_SETTINGS=_duty_settings_conf(),
)
@pytest.mark.parametrize(
    'project_admins, service_admins',
    [
        pytest.param(
            {
                'stable': ['d1mbas-project_1_s', 'd1mbas-super'],
                'testing': [
                    'd1mbas-project_1_s',
                    'd1mbas-project_1_t',
                    'd1mbas-super',
                ],
            },
            {
                'stable': ['d1mbas-service_1_s'],
                'testing': ['d1mbas-service_1_s', 'd1mbas-service_1_t'],
            },
            id='no ignores',
        ),
        pytest.param(
            {
                'stable': ['d1mbas-project_1_s', 'd1mbas-super'],
                'testing': [
                    'd1mbas-project_1_s',
                    'd1mbas-project_1_t',
                    'd1mbas-super',
                ],
            },
            {
                'stable': ['d1mbas-service_1_s'],
                'testing': ['d1mbas-service_1_s', 'd1mbas-service_1_t'],
            },
            marks=[
                pytest.mark.config(
                    CLOWNDUCTOR_SYNC_DUTY_ADMINS=_duty_admins_conf(
                        {
                            'project_name': 'test_project',
                            'service_name': 'test-service',
                        },
                    ),
                ),
            ],
            id='ignore stable',
        ),
    ],
)
async def test_prepare_targets(cron_context, project_admins, service_admins):
    await _init_params(cron_context)
    context = models.TaskContext(cron_context)
    targets = await targets_module.prepare(context)
    assert len(targets) == 2

    assert [x.duty for x in targets] == [
        None,
        {'abc_slug': 'some_abc', 'primary_schedule': 'some_schedule'},
    ]
    assert [x.duty_group_id for x in targets] == ['abc', None]

    assert dataclasses.asdict(targets[0].project_admins) == project_admins
    assert dataclasses.asdict(targets[0].service_admins) == service_admins


# in lists
# 0: service with some service roles and with duty_group_id defined and db
# 1: service with no service roles and with duty defined and no db
@pytest.mark.pgsql(
    'clownductor', files=['init_services.sql', 'init_default_roles.sql'],
)
@pytest.mark.config(
    CLOWNDUCTOR_SYNC_DUTY_ADMINS=_duty_admins_conf(),
    CLOWNDUCTOR_SYNC_DUTY_SETTINGS=_duty_settings_conf(),
)
@pytest.mark.parametrize(
    'superusers, project_admins, db_services_names',
    [
        pytest.param(
            [
                {
                    branches.Env.STABLE: [
                        'd1mbas-service_1_s',
                        'duty_1',
                        'duty_2',
                        'project_login_11',
                    ],
                    branches.Env.TESTING: [
                        'd1mbas-service_1_s',
                        'd1mbas-service_1_t',
                        'duty_1',
                        'duty_2',
                        'project_login_11',
                    ],
                },
                {branches.Env.STABLE: ['project_login_11']},
            ],
            [
                {
                    'stable': ['d1mbas-project_1_s', 'd1mbas-super'],
                    'testing': [
                        'd1mbas-project_1_s',
                        'd1mbas-project_1_t',
                        'd1mbas-super',
                    ],
                },
                {
                    'stable': ['d1mbas-project_1_s', 'd1mbas-super'],
                    'testing': [
                        'd1mbas-project_1_s',
                        'd1mbas-project_1_t',
                        'd1mbas-super',
                    ],
                },
            ],
            [['test-db-service'], []],
            id='no ignores',
        ),
        pytest.param(
            [
                {
                    branches.Env.STABLE: [
                        'd1mbas-service_1_s',
                        'duty_1',
                        'duty_2',
                    ],
                    branches.Env.TESTING: [
                        'd1mbas-service_1_s',
                        'd1mbas-service_1_t',
                        'duty_1',
                        'duty_2',
                    ],
                },
                {branches.Env.STABLE: []},
            ],
            [
                {
                    'stable': ['d1mbas-project_1_s', 'd1mbas-super'],
                    'testing': [
                        'd1mbas-project_1_s',
                        'd1mbas-project_1_t',
                        'd1mbas-super',
                    ],
                },
                {
                    'stable': ['d1mbas-project_1_s', 'd1mbas-super'],
                    'testing': [
                        'd1mbas-project_1_s',
                        'd1mbas-project_1_t',
                        'd1mbas-super',
                    ],
                },
            ],
            [['test-db-service'], []],
            marks=[
                pytest.mark.config(
                    CLOWNDUCTOR_SYNC_DUTY_SETTINGS=_duty_settings_conf(
                        use_project_owners=False,
                    ),
                ),
            ],
            id='no ignores (use project.owners disabled)',
        ),
        pytest.param(
            [
                {
                    branches.Env.STABLE: ['project_login_11'],
                    branches.Env.TESTING: [
                        'd1mbas-service_1_s',
                        'd1mbas-service_1_t',
                        'duty_1',
                        'duty_2',
                        'project_login_11',
                    ],
                },
                {branches.Env.STABLE: ['project_login_11']},
            ],
            [
                {
                    'stable': ['d1mbas-project_1_s', 'd1mbas-super'],
                    'testing': [
                        'd1mbas-project_1_s',
                        'd1mbas-project_1_t',
                        'd1mbas-super',
                    ],
                },
                {
                    'stable': ['d1mbas-project_1_s', 'd1mbas-super'],
                    'testing': [
                        'd1mbas-project_1_s',
                        'd1mbas-project_1_t',
                        'd1mbas-super',
                    ],
                },
            ],
            [['test-db-service'], []],
            marks=[
                pytest.mark.config(
                    CLOWNDUCTOR_SYNC_DUTY_ADMINS=_duty_admins_conf(
                        {
                            'project_name': 'test_project',
                            'service_name': 'test-service',
                        },
                    ),
                    CLOWNDUCTOR_SYNC_DUTY_SETTINGS=_duty_settings_conf(
                        give_root_from_idm_for_duty_excludes=False,
                    ),
                ),
            ],
            id='ignore stable (no idm roles)',
        ),
        pytest.param(
            [
                {
                    branches.Env.STABLE: ['d1mbas-service_1_s'],
                    branches.Env.TESTING: [
                        'd1mbas-service_1_s',
                        'd1mbas-service_1_t',
                        'duty_1',
                        'duty_2',
                    ],
                },
                {branches.Env.STABLE: []},
            ],
            [
                {
                    'stable': ['d1mbas-project_1_s', 'd1mbas-super'],
                    'testing': [
                        'd1mbas-project_1_s',
                        'd1mbas-project_1_t',
                        'd1mbas-super',
                    ],
                },
                {
                    'stable': ['d1mbas-project_1_s', 'd1mbas-super'],
                    'testing': [
                        'd1mbas-project_1_s',
                        'd1mbas-project_1_t',
                        'd1mbas-super',
                    ],
                },
            ],
            [['test-db-service'], []],
            marks=[
                pytest.mark.config(
                    CLOWNDUCTOR_SYNC_DUTY_ADMINS=_duty_admins_conf(
                        {
                            'project_name': 'test_project',
                            'service_name': 'test-service',
                        },
                    ),
                    CLOWNDUCTOR_SYNC_DUTY_SETTINGS=_duty_settings_conf(
                        use_project_owners=False,
                    ),
                ),
            ],
            id='ignore stable (use project.owners disabled)',
        ),
        pytest.param(
            [
                {
                    branches.Env.STABLE: [],
                    branches.Env.TESTING: [
                        'd1mbas-service_1_s',
                        'd1mbas-service_1_t',
                        'duty_1',
                        'duty_2',
                    ],
                },
                {branches.Env.STABLE: []},
            ],
            [
                {
                    'stable': ['d1mbas-project_1_s', 'd1mbas-super'],
                    'testing': [
                        'd1mbas-project_1_s',
                        'd1mbas-project_1_t',
                        'd1mbas-super',
                    ],
                },
                {
                    'stable': ['d1mbas-project_1_s', 'd1mbas-super'],
                    'testing': [
                        'd1mbas-project_1_s',
                        'd1mbas-project_1_t',
                        'd1mbas-super',
                    ],
                },
            ],
            [['test-db-service'], []],
            marks=[
                pytest.mark.config(
                    CLOWNDUCTOR_SYNC_DUTY_ADMINS=_duty_admins_conf(
                        {
                            'project_name': 'test_project',
                            'service_name': 'test-service',
                        },
                    ),
                    CLOWNDUCTOR_SYNC_DUTY_SETTINGS=_duty_settings_conf(
                        use_project_owners=False,
                        give_root_from_idm_for_duty_excludes=False,
                    ),
                ),
            ],
            id='ignore stable (no idm roles) (use project.owners disabled)',
        ),
        pytest.param(
            [
                {
                    branches.Env.STABLE: [
                        'd1mbas-service_1_s',
                        'project_login_11',
                    ],
                    branches.Env.TESTING: [
                        'd1mbas-service_1_s',
                        'd1mbas-service_1_t',
                        'duty_1',
                        'duty_2',
                        'project_login_11',
                    ],
                },
                {branches.Env.STABLE: ['project_login_11']},
            ],
            [
                {
                    branches.Env.STABLE.value: [
                        'd1mbas-project_1_s',
                        'd1mbas-super',
                    ],
                    branches.Env.TESTING.value: [
                        'd1mbas-project_1_s',
                        'd1mbas-project_1_t',
                        'd1mbas-super',
                    ],
                },
                {
                    'stable': ['d1mbas-project_1_s', 'd1mbas-super'],
                    'testing': [
                        'd1mbas-project_1_s',
                        'd1mbas-project_1_t',
                        'd1mbas-super',
                    ],
                },
            ],
            [['test-db-service'], []],
            marks=[
                pytest.mark.config(
                    CLOWNDUCTOR_SYNC_DUTY_ADMINS=_duty_admins_conf(
                        {
                            'project_name': 'test_project',
                            'service_name': 'test-service',
                        },
                    ),
                ),
            ],
            id='ignore stable (by excludes)',
        ),
        pytest.param(
            [
                {
                    branches.Env.STABLE: [
                        'd1mbas-service_1_s',
                        'project_login_11',
                    ],
                    branches.Env.TESTING: [
                        'd1mbas-service_1_s',
                        'd1mbas-service_1_t',
                        'duty_1',
                        'duty_2',
                        'project_login_11',
                    ],
                },
                {branches.Env.STABLE: ['project_login_11']},
            ],
            [
                {
                    branches.Env.STABLE.value: [
                        'd1mbas-project_1_s',
                        'd1mbas-super',
                    ],
                    branches.Env.TESTING.value: [
                        'd1mbas-project_1_s',
                        'd1mbas-project_1_t',
                        'd1mbas-super',
                    ],
                },
                {
                    'stable': ['d1mbas-project_1_s', 'd1mbas-super'],
                    'testing': [
                        'd1mbas-project_1_s',
                        'd1mbas-project_1_t',
                        'd1mbas-super',
                    ],
                },
            ],
            [['test-db-service'], []],
            marks=[
                pytest.mark.config(
                    CLOWNDUCTOR_FEATURES_PER_SERVICE={
                        '__default__': {'__default__': {}},
                        'test_project': {
                            '__default__': {
                                'disable_stable_roots_for_duty': True,
                            },
                        },
                    },
                ),
            ],
            id='ignore stable (by project feature)',
        ),
        pytest.param(
            [
                {
                    branches.Env.STABLE: [
                        'd1mbas-service_1_s',
                        'project_login_11',
                    ],
                    branches.Env.TESTING: [
                        'd1mbas-service_1_s',
                        'd1mbas-service_1_t',
                        'duty_1',
                        'duty_2',
                        'project_login_11',
                    ],
                },
                {branches.Env.STABLE: ['project_login_11']},
            ],
            [
                {
                    branches.Env.STABLE.value: [
                        'd1mbas-project_1_s',
                        'd1mbas-super',
                    ],
                    branches.Env.TESTING.value: [
                        'd1mbas-project_1_s',
                        'd1mbas-project_1_t',
                        'd1mbas-super',
                    ],
                },
                {
                    'stable': ['d1mbas-project_1_s', 'd1mbas-super'],
                    'testing': [
                        'd1mbas-project_1_s',
                        'd1mbas-project_1_t',
                        'd1mbas-super',
                    ],
                },
            ],
            [['test-db-service'], []],
            marks=[
                pytest.mark.config(
                    CLOWNDUCTOR_FEATURES_PER_SERVICE={
                        '__default__': {'__default__': {}},
                        'test_project': {
                            '__default__': {
                                'disable_stable_roots_for_duty': True,
                            },
                            'test-service': {
                                'disable_stable_roots_for_duty': True,
                            },
                        },
                    },
                ),
            ],
            id='ignore stable (by service feature)',
        ),
    ],
)
async def test_prepare_rtc_targets(
        mockserver,
        cron_context,
        superusers,
        project_admins,
        db_services_names,
):
    await _init_params(cron_context)

    @mockserver.json_handler('/duty-api/api/duty_group')
    def _duty_group_handler(request):
        if request.query['group_id'] == 'abc':
            return {
                'result': {
                    'data': {
                        'currentEvent': {'user': 'duty_2'},
                        'suggestedEvents': [
                            {'user': 'duty_1'},
                            {'user': 'duty_2'},
                        ],
                        'staffGroups': ['svc_taxidutyadmins_administration'],
                    },
                    'ok': True,
                },
            }
        return mockserver.make_response(status=404)

    context = models.TaskContext(cron_context)
    targets = await rtc_targets_module.prepare(
        context, await targets_module.prepare(context),
    )
    assert len(targets) == 2
    assert [x.superusers for x in targets] == superusers
    assert [
        dataclasses.asdict(x.project_admins) for x in targets
    ] == project_admins
    assert [
        [y['name'] for y in x.db_services] for x in targets
    ] == db_services_names
