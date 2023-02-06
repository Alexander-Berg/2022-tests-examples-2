from typing import Optional

import pytest

DEFAULT_KEY = '__default__'
PROJECT = 'test_project'
SERVICE = 'test_service'

CLOWNDUCTOR_FEATURES = {'allow_auto_unstable_creation': True}

CLOWNDUCTOR_FEATURES_PS = {
    '__default__': {'task_processor_enabled': True, 'locks_for_deploy': False},
}

CLOWN_PS_WITH_PROJECT = {
    '__default__': {'abc_service_removal': True, 'locks_for_deploy': False},
    'test_project': {'__default__': {'locks_for_deploy': True}},
}
CLOWN_PS_WITH_SERVICE = {
    '__default__': {
        'abc_service_removal': True,
        'cancel_old_deploys': False,
        'locks_for_deploy': False,
    },
    'test_project': {
        '__default__': {'locks_for_deploy': True, 'cancel_old_deploys': True},
        'test_service': {'cancel_old_deploys': False},
    },
}


def select_function(
        web_context,
        feature_name: str,
        project_name: Optional[str] = None,
        service_name: Optional[str] = None,
):
    mapping = {
        'abc_service_removal': (
            web_context.features.get_abc_service_removal(
                project_name=project_name, service_name=service_name,
            ),
            web_context.features.abc_service_removal,
        ),
        'allow_auto_unstable_creation': (
            web_context.features.get_allow_auto_unstable_creation(
                project_name=project_name, service_name=service_name,
            ),
            web_context.features.allow_auto_unstable_creation,
        ),
        'cancel_old_deploys': (
            web_context.features.get_cancel_old_deploys(
                project_name=project_name, service_name=service_name,
            ),
            web_context.features.cancel_old_deploys,
        ),
        'task_processor_enabled': (
            web_context.features.get_task_processor_enabled(
                project_name=project_name, service_name=service_name,
            ),
            web_context.features.task_processor_enabled,
        ),
        'locks_for_deploy': (
            web_context.features.get_locks_for_deploy(
                project_name=project_name, service_name=service_name,
            ),
            web_context.features.locks_for_deploy,
        ),
        'summon_users': (
            web_context.features.get_summon_users(
                project_name=project_name, service_name=service_name,
            ),
            web_context.features.summon_users,
        ),
    }
    return mapping.get(feature_name)


@pytest.mark.parametrize(
    'project_name, service_name, feature_name, '
    'expected_result_get, expected_result_prop',
    [
        pytest.param(
            None,
            None,
            'task_processor_enabled',
            False,
            False,
            id='both configs are empty',
            marks=[
                pytest.mark.config(
                    CLOWNDUCTOR_FEATURES_PER_SERVICE={'__default__': {}},
                    CLOWNDUCTOR_FEATURES={},
                ),
            ],
        ),
        pytest.param(
            None,
            None,
            'task_processor_enabled',
            True,
            True,
            id='feature is specified in new config; old config is empty',
            marks=[
                pytest.mark.config(
                    CLOWNDUCTOR_FEATURES_PER_SERVICE=CLOWNDUCTOR_FEATURES_PS,
                ),
            ],
        ),
        pytest.param(
            None,
            None,
            'task_processor_enabled',
            False,
            False,
            id='feature is not specified in old config; new config is empty',
            marks=[
                pytest.mark.config(CLOWNDUCTOR_FEATURES=CLOWNDUCTOR_FEATURES),
            ],
        ),
        pytest.param(
            None,
            None,
            'allow_auto_unstable_creation',
            True,
            True,
            id='feature is not specified in new config, '
            'but its specified in old config',
            marks=[
                pytest.mark.config(
                    CLOWNDUCTOR_FEATURES_PER_SERVICE=CLOWNDUCTOR_FEATURES_PS,
                    CLOWNDUCTOR_FEATURES=CLOWNDUCTOR_FEATURES,
                ),
            ],
        ),
        pytest.param(
            None,
            None,
            'summon_users',
            False,
            False,
            id='feature is not specified in either '
            'the new config or the old config',
            marks=[
                pytest.mark.config(
                    CLOWNDUCTOR_FEATURES_PER_SERVICE=CLOWNDUCTOR_FEATURES_PS,
                    CLOWNDUCTOR_FEATURES=CLOWNDUCTOR_FEATURES,
                ),
            ],
        ),
        pytest.param(
            'test_project',
            None,
            'locks_for_deploy',
            True,
            False,
            id='feature is specified in project clause',
            marks=[
                pytest.mark.config(
                    CLOWNDUCTOR_FEATURES_PER_SERVICE=CLOWN_PS_WITH_PROJECT,
                ),
            ],
        ),
        pytest.param(
            'test_project',
            None,
            'abc_service_removal',
            True,
            True,
            id='feature is not specified in project clause, '
            'but specified in default',
            marks=[
                pytest.mark.config(
                    CLOWNDUCTOR_FEATURES_PER_SERVICE=CLOWN_PS_WITH_PROJECT,
                ),
            ],
        ),
        pytest.param(
            'test_project',
            'service_does_not_exist',
            'locks_for_deploy',
            True,
            False,
            id='pass service that is not specified in config '
            'without services defined',
            marks=[
                pytest.mark.config(
                    CLOWNDUCTOR_FEATURES_PER_SERVICE=CLOWN_PS_WITH_PROJECT,
                ),
            ],
        ),
        pytest.param(
            'test_project',
            'service_does_not_exist',
            'cancel_old_deploys',
            True,
            False,
            id='pass service that is not specified ' 'in config with services',
            marks=[
                pytest.mark.config(
                    CLOWNDUCTOR_FEATURES_PER_SERVICE=CLOWN_PS_WITH_SERVICE,
                ),
            ],
        ),
        pytest.param(
            'test_project',
            'test_service',
            'cancel_old_deploys',
            False,
            False,
            id='feature is specified in the service clause',
            marks=[
                pytest.mark.config(
                    CLOWNDUCTOR_FEATURES_PER_SERVICE=CLOWN_PS_WITH_SERVICE,
                ),
            ],
        ),
        pytest.param(
            'test_project',
            'test_service',
            'locks_for_deploy',
            True,
            False,
            id='feature is not specified in the service clause',
            marks=[
                pytest.mark.config(
                    CLOWNDUCTOR_FEATURES_PER_SERVICE=CLOWN_PS_WITH_SERVICE,
                ),
            ],
        ),
        pytest.param(
            'test_project',
            'test_service',
            'allow_auto_unstable_creation',
            True,
            True,
            id='feature is not specified in the new config; '
            'its specified in the old one',
            marks=[
                pytest.mark.config(
                    CLOWNDUCTOR_FEATURES_PER_SERVICE=CLOWN_PS_WITH_SERVICE,
                    CLOWNDUCTOR_FEATURES=CLOWNDUCTOR_FEATURES,
                ),
            ],
        ),
    ],
)
async def test_config_per_service(
        web_context,
        project_name,
        service_name,
        feature_name,
        expected_result_get,
        expected_result_prop,
):
    assert select_function(
        web_context, feature_name, project_name, service_name,
    ) == (expected_result_get, expected_result_prop)


@pytest.mark.parametrize(
    'feature_name, expected_result',
    [
        pytest.param(
            'task_processor_enabled',
            False,
            id='turn off of the feature specified in the config',
            marks=[
                pytest.mark.config(
                    CLOWNDUCTOR_FEATURES_PER_SERVICE=CLOWNDUCTOR_FEATURES_PS,
                ),
                pytest.mark.features_off('task_processor_enabled'),
            ],
        ),
        pytest.param(
            'cancel_old_deploys',
            False,
            id='turn off of the feature not specified in the config',
            marks=[
                pytest.mark.config(
                    CLOWNDUCTOR_FEATURES_PER_SERVICE=CLOWNDUCTOR_FEATURES_PS,
                ),
                pytest.mark.features_off('cancel_old_deploys'),
            ],
        ),
        pytest.param(
            'cancel_old_deploys',
            False,
            id='turn off of the feature in the empty config',
            marks=[pytest.mark.features_off('cancel_old_deploys')],
        ),
        pytest.param(
            'locks_for_deploy',
            True,
            id='turn on of the feature specified in the config',
            marks=[
                pytest.mark.config(
                    CLOWNDUCTOR_FEATURES_PER_SERVICE=CLOWNDUCTOR_FEATURES_PS,
                ),
                pytest.mark.features_on('locks_for_deploy'),
            ],
        ),
        pytest.param(
            'abc_service_removal',
            True,
            id='turn on of the feature not specified in the config',
            marks=[
                pytest.mark.config(
                    CLOWNDUCTOR_FEATURES_PER_SERVICE=CLOWNDUCTOR_FEATURES_PS,
                ),
                pytest.mark.features_on('abc_service_removal'),
            ],
        ),
        pytest.param(
            'abc_service_removal',
            True,
            id='turn on of the feature in the empty config',
            marks=[pytest.mark.features_on('abc_service_removal')],
        ),
    ],
)
async def test_feature_config(web_context, feature_name, expected_result):
    assert select_function(web_context, feature_name) == (
        expected_result,
        expected_result,
    )
