# pylint: disable=broad-except
import contextlib

import pytest

from generated.models import foxford_api as foxford_api_model

from supportai_actions.action_types.foxford_dialog import get_user_meta_info
from supportai_actions.actions import action as action_module
from supportai_actions.actions import features as feature_module
from supportai_actions.actions import state as state_module
from test_supportai_actions.test_action_types.test_foxford import (
    utils as test_utils,
)

ACTION_NAME = 'get_user_meta_info'
PROJECT_NAME = 'foxford_dialog'


async def test_get_user_meta_info_validation():
    _ = get_user_meta_info.GetUserInfoAction(
        PROJECT_NAME, 'get_user_meta_info', '0', [],
    )


@pytest.mark.parametrize(
    'state, raises',
    [
        (
            state_module.State(
                features=feature_module.Features(
                    [
                        {'key': 'user_phone', 'value': '88005553535'},
                        {'key': 'user_email', 'value': 'example@example.com'},
                    ],
                ),
            ),
            contextlib.nullcontext(),
        ),
        (
            state_module.State(
                features=feature_module.Features(
                    [{'key': 'user_phone', 'value': '88005553535'}],
                ),
            ),
            contextlib.nullcontext(),
        ),
        (
            state_module.State(
                features=feature_module.Features(
                    [{'key': 'user_email', 'value': 'example@example.com'}],
                ),
            ),
            contextlib.nullcontext(),
        ),
        pytest.param(
            state_module.State(
                features=feature_module.Features(
                    [
                        {
                            'key': 'some_weird_feature',
                            'value': 'some_weird_feature_value',
                        },
                    ],
                ),
            ),
            pytest.raises(action_module.ValidationStateError),
        ),
        pytest.param(
            state_module.State(
                features=feature_module.Features(
                    [{'key': 'user_email', 'value': 42}],
                ),
            ),
            pytest.raises(action_module.ValidationStateError),
        ),
        pytest.param(
            state_module.State(
                features=feature_module.Features(
                    [{'key': 'user_phone', 'value': 42}],
                ),
            ),
            pytest.raises(action_module.ValidationStateError),
        ),
    ],
)
async def test_get_user_meta_info_state_validation(state, raises):
    action = get_user_meta_info.GetUserInfoAction(
        PROJECT_NAME, ACTION_NAME, '0', [],
    )
    with raises:
        action.validate_state(state)


@pytest.fixture(name='mock_foxford')
def _mock_foxford(mockserver):
    @mockserver.json_handler(
        path='/foxford-api/api/yandex_support_ai/users/me',
    )
    def _(_):
        return mockserver.make_response(
            json=foxford_api_model.UserInfo(
                id=42,
                timezone='Europe/Moscow',
                email='example@example',
                personal_name='Алёша',
                phone='555',
                parent_phone='554',
                type_name='Ученик',
            ).serialize(),
        )


@pytest.mark.parametrize(
    'state, _call_params',
    [
        (
            state_module.State(
                features=feature_module.Features(
                    features=[
                        {'key': 'user_email', 'value': 'example@example'},
                    ],
                ),
            ),
            [],
        ),
    ],
)
async def test_get_user_meta_info_state_call(
        web_context, state, _call_params, mock_foxford,
):

    action = get_user_meta_info.GetUserInfoAction(
        PROJECT_NAME, ACTION_NAME, '0', _call_params,
    )

    _state = await action(web_context, state)
    assert 'user_id' in _state.features
    assert 'user_type_name' in _state.features
    new_call_params, new_state = test_utils.make_new_call_params_and_state(
        state,
    )
    action = get_user_meta_info.GetUserInfoAction(
        PROJECT_NAME, ACTION_NAME, '0', new_call_params,
    )

    _state = await action(web_context, new_state)
    assert 'user_id' in _state.features
    assert 'user_type_name' in _state.features
