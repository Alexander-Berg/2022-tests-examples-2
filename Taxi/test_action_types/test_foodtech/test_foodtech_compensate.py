# flake8: noqa: I100
# pylint: disable=broad-except
import pytest

from supportai_actions.actions import action as action_module
from supportai_actions.actions import params as param_module
from supportai_actions.actions import features as feature_module
from supportai_actions.actions import state as state_module

from supportai_actions.action_types.foodtech_client import foodtech_compensate


@pytest.fixture(name='complaint_response')
def gen_complaint_response(mockserver):
    @mockserver.json_handler('/eats-core-complaint/complaint/auto')
    async def _(request):
        return mockserver.make_response(
            status=200,
            json={
                'complaint_id': '123',
                'can_compensate': (
                    request.json.get('situation_code') == 'compensate'
                ),
            },
        )

    @mockserver.json_handler('/eats-core-complaint/compensation/auto')
    async def _(request):
        return mockserver.make_response(
            status=200,
            json={
                'compensations': {
                    'promocode': {
                        'compensation_id': 'abc',
                        'rate': 20,
                        'code': 'Lavka-20',
                        'expire_at': '2021-06-30',
                    },
                },
            },
        )


@pytest.mark.parametrize(
    '_call_param', [[param_module.ActionParam({'situation_code': 'XXX'})]],
)
async def test_foodtech_compensate_validation(_call_param):
    _ = foodtech_compensate.FoodtechCompensateAction(
        '...', 'foodtech_compensate', '0', _call_param,
    )


@pytest.mark.parametrize(
    'state, _call_param',
    [
        pytest.param(
            state_module.State(
                features=feature_module.Features(
                    features=[{'key': 'random_feature', 'value': 'random'}],
                ),
            ),
            [],
            marks=pytest.mark.xfail(
                raises=action_module.ValidationError, strict=True,
            ),
        ),
        pytest.param(
            state_module.State(
                features=feature_module.Features(
                    features=[{'key': 'order_id', 'value': 'XXX XXX XXX'}],
                ),
            ),
            [],
            marks=pytest.mark.xfail(
                raises=action_module.ValidationError, strict=True,
            ),
        ),
        (
            state_module.State(
                features=feature_module.Features(
                    features=[
                        {'key': 'order_id', 'value': 'XXX XXX XXX'},
                        {'key': 'chat_id', 'value': 'chat-XXX'},
                    ],
                ),
            ),
            [param_module.ActionParam({'situation_code': 'XXX'})],
        ),
    ],
)
async def test_foodtech_compensate_state_validation(state, _call_param):
    action = foodtech_compensate.FoodtechCompensateAction(
        '...', 'foodtech_compensate', '0', _call_param,
    )

    action.validate_state(state)


@pytest.mark.parametrize(
    'state, _call_param',
    [
        (
            state_module.State(
                features=feature_module.Features(
                    features=[
                        {'key': 'order_id', 'value': 'XXX XXX XXX'},
                        {'key': 'chat_id', 'value': 'chatterbox-XXX'},
                    ],
                ),
            ),
            [param_module.ActionParam({'situation_code': 'compensate'})],
        ),
        (
            state_module.State(
                features=feature_module.Features(
                    features=[
                        {'key': 'order_id', 'value': 'XXX XXX XXX'},
                        {'key': 'chat_id', 'value': 'chatterbox-XXX'},
                    ],
                ),
            ),
            [param_module.ActionParam({'situation_code': 'not compensate'})],
        ),
    ],
)
async def test_foodtech_compensate_call(
        web_context, state, _call_param, complaint_response,
):
    action = foodtech_compensate.FoodtechCompensateAction(
        '...', 'foodtech_compensate', '0', _call_param,
    )

    _state = await action(web_context, state)

    _can_compensate = _call_param[0]['situation_code'] == 'compensate'

    assert 'can_compensate' in _state.features
    assert _state.features['can_compensate'] == _can_compensate
    assert 'complaint_id' in _state.features

    if _can_compensate:
        assert 'compensations_count' in _state.features
