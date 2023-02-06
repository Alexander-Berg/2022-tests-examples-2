# flake8: noqa: I100
# pylint: disable=broad-except
import pytest

from supportai_actions.actions import action as action_module
from supportai_actions.actions import params as param_module
from supportai_actions.actions import features as feature_module
from supportai_actions.actions import state as state_module

from supportai_actions.action_types.justschool_dialog import (
    check_if_able_to_cancel,
)


@pytest.mark.parametrize('_call_param', [[]])
async def test_justschool_dialog_check_if_able_to_cancel_validation(
        _call_param,
):
    _ = check_if_able_to_cancel.CheckIfAbleToCancelAction(
        'justschool_dialog', 'cehck_if_able_to_cancel', '0', _call_param,
    )


@pytest.mark.parametrize(
    'state, _call_param',
    [
        (
            state_module.State(
                features=feature_module.Features(
                    features=[
                        {
                            'key': 'lesson_to_cancel_dttm',
                            'value': '2021-01-01T4:19',
                        },
                    ],
                ),
            ),
            [],
        ),
        pytest.param(
            state_module.State(
                features=feature_module.Features(
                    features=[{'key': 'some', 'value': 'some'}],
                ),
            ),
            [],
            marks=pytest.mark.xfail(
                raises=action_module.ValidationError, strict=True,
            ),
        ),
    ],
)
async def test_justschool_dialog_check_if_able_to_cancel_state_validation(
        state, _call_param,
):
    action = check_if_able_to_cancel.CheckIfAbleToCancelAction(
        'justschool_dialog', 'cehck_if_able_to_cancel', '0', _call_param,
    )

    action.validate_state(state)


@pytest.mark.now('2021-12-12T11:00')
@pytest.mark.parametrize(
    'state, _call_param, expected_available_to_cancel',
    [
        (
            state_module.State(
                features=feature_module.Features(
                    features=[
                        {
                            'key': 'lesson_to_cancel_dttm',
                            'value': '2021-12-12T11:01',
                        },
                    ],
                ),
            ),
            [],
            True,
        ),
        (
            state_module.State(
                features=feature_module.Features(
                    features=[
                        {
                            'key': 'lesson_to_cancel_dttm',
                            'value': '2021-12-12T13:00',
                        },
                    ],
                ),
            ),
            [],
            True,
        ),
        (
            state_module.State(
                features=feature_module.Features(
                    features=[
                        {
                            'key': 'lesson_to_cancel_dttm',
                            'value': '2021-12-12T11:30',
                        },
                    ],
                ),
            ),
            [],
            True,
        ),
        (
            state_module.State(
                features=feature_module.Features(
                    features=[
                        {
                            'key': 'lesson_to_cancel_dttm',
                            'value': '2021-12-12T10:20',
                        },
                    ],
                ),
            ),
            [],
            False,
        ),
        (
            state_module.State(
                features=feature_module.Features(
                    features=[
                        {
                            'key': 'lesson_to_cancel_dttm',
                            'value': '2021-12-12T00:00',
                        },
                    ],
                ),
            ),
            [],
            False,
        ),
    ],
)
async def test_justschool_dialog_check_if_able_to_cancel_call(
        web_context, state, _call_param, expected_available_to_cancel,
):
    action = check_if_able_to_cancel.CheckIfAbleToCancelAction(
        'justschool_dialog', 'cehck_if_able_to_cancel', '0', _call_param,
    )

    _state = await action(web_context, state)

    assert 'is_available_to_cancel' in _state.features
    assert (
        _state.features['is_available_to_cancel']
        == expected_available_to_cancel
    )
