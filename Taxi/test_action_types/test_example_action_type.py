# flake8: noqa: I100
# pylint: disable=broad-except
import pytest

from supportai_actions.actions import state as state_module
from supportai_actions.actions import features as feature_module
from supportai_actions.action_types import example_action_type


@pytest.mark.parametrize('_call_param', [([])])
async def test_example_action_validate(_call_param):
    example_action_type.ExampleAction('echo', 'echo', '0', _call_param)


@pytest.mark.parametrize(
    'state, _call_param',
    [
        (
            state_module.State(
                features=feature_module.Features(
                    features=[{'key': 'a', 'value': 'b'}],
                ),
            ),
            [],
        ),
    ],
)
async def test_example_action_validate_state(state, _call_param):
    example_action_type.ExampleAction(
        'echo', 'echo', '0', _call_param,
    ).validate_state(state)


@pytest.mark.parametrize('_call_param', [[]])
@pytest.mark.parametrize(
    'state',
    [
        state_module.State(
            features=feature_module.Features(
                features=[{'key': 'a', 'value': 'b'}],
            ),
        ),
    ],
)
async def test_example_action_call(web_context, _call_param, state):
    action = example_action_type.ExampleAction(
        'echo', 'echo', '0', _call_param,
    )

    _state = await action(web_context, state)

    assert _state.features == state.features


@pytest.mark.parametrize('_call_param', [[]])
@pytest.mark.parametrize(
    'state',
    [
        state_module.State(
            features=feature_module.Features(
                features=[{'key': 'a', 'value': 'b'}],
            ),
        ),
    ],
)
async def test_example_action_mock_call(web_context, _call_param, state):
    action = example_action_type.ExampleAction(
        'echo', 'echo', '0', _call_param, is_mock=True,
    )

    _state = await action(web_context, state)

    assert 'is_mock' in _state.features
    assert _state.features['is_mock'] is True
    assert _state.features['is_mock_from_config'] is True
