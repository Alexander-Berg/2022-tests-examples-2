# pylint: disable=W0212
from typing import Callable

import pytest

from supportai.common import configuration as configuration_module
from supportai.common import feature as feature_module
from supportai.common import policy as policy_module
from supportai.common import state as state_module


@pytest.fixture(name='create_policy')
def create_policy_fixture(load_json) -> Callable[[str], policy_module.Policy]:
    def policy_fn(config_path: str) -> policy_module.Policy:
        policy = policy_module.Policy()
        configuration = configuration_module.Configuration.deserialize(
            load_json(config_path),
        )
        policy.load_from_configuration(
            configuration.policy, configuration.flags,
        )
        return policy

    return policy_fn


@pytest.mark.parametrize('config_path', ['configuration.json'])
async def test_get_evaluation_results(create_policy, config_path):
    policy = create_policy(config_path)
    await policy.prepare()

    evaluations_results = await policy._executor.assign({})

    evaluation_results = policy._main_group.convert_evaluation_results(
        evaluations_results,
    )
    assert evaluation_results == [[True, False], [True, False, False]]

    evaluations_results = await policy._executor.assign({'a': 1})

    evaluation_results_of_group = (
        policy._main_group.convert_evaluation_results(evaluations_results)
    )
    assert evaluation_results_of_group == [[False, True], [True, False, False]]

    evaluations_results = await policy._executor.assign({'a': 1, 'b': 2})

    evaluation_results_of_group = (
        policy._main_group.convert_evaluation_results(evaluations_results)
    )
    assert evaluation_results_of_group == [[False, True], [False, True, False]]

    evaluations_results = await policy._executor.assign({'a': 2, 'b': 1})

    evaluation_results_of_group = (
        policy._main_group.convert_evaluation_results(evaluations_results)
    )
    assert evaluation_results_of_group == [
        [False, False],
        [False, False, False],
    ]


@pytest.mark.parametrize('config_path', ['configuration.json'])
def test_get_policy_items_weights(create_policy, config_path):
    policy = create_policy(config_path)
    weights = policy._main_group._get_policy_items_weights()
    assert weights == [[1 / 2, 1], [1 / 3, 2 / 3, 1]]


@pytest.mark.parametrize('config_path', ['configuration.json'])
async def test_get_prioritized_policy_item(create_policy, config_path):
    policy = create_policy(config_path)
    await policy.prepare()

    features = {}
    evaluations_results = await policy._executor.assign(features)
    evaluation_results = policy._main_group.convert_evaluation_results(
        evaluations_results,
    )
    policy_item = policy._main_group.get_prioritized_policy_item(
        evaluation_results,
    )
    assert policy_item.response_action is not None
    assert policy_item.response_action._texts == ['Уточняю a']

    features = {'a': 1, 'b': 2}

    evaluations_results = await policy._executor.assign(features)
    evaluation_results = policy._main_group.convert_evaluation_results(
        evaluations_results,
    )

    policy_item = policy._main_group.get_prioritized_policy_item(
        evaluation_results,
    )
    assert policy_item.response_action is not None
    assert policy_item.response_action._texts == ['Уточнил a']

    features = {'b': 2, 'c': 3}

    evaluations_results = await policy._executor.assign(features)
    evaluation_results = policy._main_group.convert_evaluation_results(
        evaluations_results,
    )

    policy_item = policy._main_group.get_prioritized_policy_item(
        evaluation_results,
    )
    assert policy_item.response_action is not None
    assert policy_item.response_action._texts == ['Уточнил все']
    assert policy_item.response_action._defer_time_sec == 125
    assert policy_item.response_action._forward_line == 'line1'
    assert policy_item.response_action._close
    assert policy_item.response_action._operator

    features = {'a': 2, 'b': 1}

    evaluations_results = await policy._executor.assign(features)
    evaluation_results = policy._main_group.convert_evaluation_results(
        evaluations_results,
    )

    policy_item = policy._main_group.get_prioritized_policy_item(
        evaluation_results,
    )
    assert policy_item is None


@pytest.mark.parametrize('config_path', ['configuration.json'])
async def test_fallback_and_pre_group(create_policy, config_path):
    policy = create_policy(config_path)
    await policy.prepare()

    state = state_module.State()

    state['pre'] = feature_module.Feature.as_defined(key='pre', value=True)

    policy_item = await policy.get_policy_item_by(state)

    assert 'Попали в pre' in policy_item.response_action._texts

    state.pop_feature('pre')

    for feature_name in ('a', 'b', 'c'):
        state[feature_name] = feature_module.Feature.as_defined(
            key=feature_name, value=100,
        )

    policy_item = await policy.get_policy_item_by(state)

    assert 'Попали в fallback' in policy_item.response_action._texts
