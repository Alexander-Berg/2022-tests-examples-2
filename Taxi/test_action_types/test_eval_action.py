import pytest

from supportai_actions.action_types import eval_action
from supportai_actions.actions import action as action_module
from supportai_actions.actions import features as feature_module
from supportai_actions.actions import params as params_module
from supportai_actions.actions import state as state_module


@pytest.mark.parametrize(
    '_call_param',
    [
        pytest.param([params_module.ActionParam({})]),
        pytest.param(
            [
                params_module.ActionParam(
                    {'features_to_evaluate': 'some_feature'},
                ),
            ],
            marks=pytest.mark.xfail(
                raises=action_module.ValidationError, strict=True,
            ),
        ),
        pytest.param(
            [
                params_module.ActionParam(
                    {
                        'features_to_evaluate': [
                            'some_feature',
                            'another_feature',
                        ],
                    },
                ),
            ],
            marks=pytest.mark.xfail(
                raises=action_module.ValidationError, strict=True,
            ),
        ),
        pytest.param(
            [
                params_module.ActionParam(
                    {
                        'features_to_evaluate': {
                            1: 'some_feature',
                            2: 'another_feature',
                        },
                    },
                ),
            ],
            marks=pytest.mark.xfail(
                raises=action_module.ValidationError, strict=True,
            ),
        ),
        pytest.param(
            [
                params_module.ActionParam(
                    {
                        'features_to_evaluate': {
                            'some_feature': 'some_feature',
                            'another_feature': 'another_feature',
                        },
                    },
                ),
            ],
        ),
    ],
)
async def test_validate(_call_param):
    eval_action.EvalAction('echo', 'echo', '0', _call_param)


@pytest.mark.parametrize(
    'state, _call_param, result',
    [
        pytest.param(
            state_module.State(features=feature_module.Features(features=[])),
            [
                params_module.ActionParam(
                    {
                        'features_to_evaluate': {
                            'incredible_feature': '5',
                            'another_incredible_feature': '1 + 2 + 3',
                            'ultimate_incredible_feature': 'sum([3, 6, 9])',
                        },
                    },
                ),
            ],
            {
                'incredible_feature': 5,
                'another_incredible_feature': 6,
                'ultimate_incredible_feature': 18,
            },
        ),
        pytest.param(
            state_module.State(
                features=feature_module.Features(
                    features=[
                        {'key': 'a', 'value': 123},
                        {'key': 'b', 'value': 786},
                        {'key': 'c', 'value': 323},
                    ],
                ),
            ),
            [
                params_module.ActionParam(
                    {
                        'features_to_evaluate': {
                            'incredible_feature': 'a + b + c',
                            'a': 'a + 35',
                        },
                    },
                ),
            ],
            {'incredible_feature': 1232, 'a': 158},
        ),
        pytest.param(
            state_module.State(
                features=feature_module.Features(
                    features=[
                        {
                            'key': 'extracted_datetime',
                            'value': '2022-02-19T11:00:17.893204',
                        },
                        {'key': 'user_timezone', 'value': 'Europe/Moscow'},
                    ],
                ),
            ),
            [
                params_module.ActionParam(
                    {
                        'features_to_evaluate': {
                            'timeaware_datetime': (
                                'timezone(user_timezone).'
                                'localize(datetime.datetime.'
                                'fromisoformat(extracted_datetime)).'
                                'isoformat()'
                            ),
                        },
                    },
                ),
            ],
            {'timeaware_datetime': '2022-02-19T11:00:17.893204+03:00'},
        ),
    ],
)
async def test_call(web_context, _call_param, state, result):
    action = eval_action.EvalAction('echo', 'echo', '0', _call_param)
    _state = await action(web_context, state)

    for feature_name, value in result.items():
        assert _state.features[feature_name] == value
