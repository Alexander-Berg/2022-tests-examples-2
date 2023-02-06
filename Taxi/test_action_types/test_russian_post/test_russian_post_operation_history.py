# flake8: noqa: I100
# pylint: disable=broad-except
import pytest

from supportai_actions.actions import action as action_module
from supportai_actions.actions import params as param_module
from supportai_actions.actions import features as feature_module
from supportai_actions.actions import state as state_module

from supportai_actions.action_types.russian_post import (
    russian_post_operation_history,
)


@pytest.mark.parametrize(
    '_call_param',
    [
        [],
        pytest.param(
            [param_module.ActionParam({'message_type': 'failed'})],
            marks=pytest.mark.xfail(
                raises=action_module.ValidationError, strict=True,
            ),
        ),
        [param_module.ActionParam({'response_mapping': []})],
        pytest.param(
            [
                param_module.ActionParam(
                    {'response_mapping': [{'key': 'value'}]},
                ),
            ],
            marks=pytest.mark.xfail(
                raises=action_module.ValidationError, strict=True,
            ),
        ),
        [
            param_module.ActionParam(
                {
                    'response_mapping': [
                        {
                            'feature_name': 'oper_date',
                            'json_path': '$[-1:].OperationParameters.OperDate',
                        },
                        {
                            'feature_name': 'oper_type',
                            'json_path': (
                                '$[-1:].OperationParameters.OperType.Name'
                            ),
                        },
                    ],
                },
            ),
        ],
    ],
)
async def test_russian_post_operation_history_validation(_call_param):
    _ = russian_post_operation_history.RussianPostOperationHistory(
        'test', 'operation_history', '0', _call_param,
    )


@pytest.mark.parametrize(
    'state, _call_param',
    [
        (
            state_module.State(
                features=feature_module.Features(
                    features=[{'key': 'track_number', 'value': 'XXX-XXXX'}],
                ),
            ),
            [],
        ),
        pytest.param(
            state_module.State(
                features=feature_module.Features(
                    features=[{'key': 'track_number', 'value': 'some'}],
                ),
            ),
            [
                param_module.ActionParam(
                    {'track_number_feature_name': 'number'},
                ),
            ],
            marks=pytest.mark.xfail(
                raises=action_module.ValidationError, strict=True,
            ),
        ),
        (
            state_module.State(
                features=feature_module.Features(
                    features=[{'key': 'track_number_2', 'value': 'some'}],
                ),
            ),
            [
                param_module.ActionParam(
                    {'track_number_feature_name': 'track_number_2'},
                ),
            ],
        ),
    ],
)
async def test_russian_post_operation_history_state_validation(
        state, _call_param,
):
    action = russian_post_operation_history.RussianPostOperationHistory(
        'test', 'operation_history', '0', _call_param,
    )

    action.validate_state(state)


@pytest.mark.parametrize(
    'state, _call_param',
    [
        (
            state_module.State(
                features=feature_module.Features(
                    features=[{'key': 'track_number', 'value': 'XXX-XXXX'}],
                ),
            ),
            [],
        ),
        (
            state_module.State(
                features=feature_module.Features(
                    features=[{'key': 'track_number_2', 'value': 'some'}],
                ),
            ),
            [
                param_module.ActionParam(
                    {'track_number_feature_name': 'track_number_2'},
                ),
            ],
        ),
    ],
)
@pytest.mark.russian_post_mock(
    records=[{'oper_type': 'Test', 'oper_type_id': 3}],
)
async def test_russian_post_operation_history_call(
        web_context, state, _call_param,
):
    action = russian_post_operation_history.RussianPostOperationHistory(
        'test', 'operation_history', '0', _call_param,
    )

    _state = await action(web_context, state)

    assert 'oper_type' in _state.features
    assert 'return_flag' in _state.features
    assert _state.features['return_flag'] is True
