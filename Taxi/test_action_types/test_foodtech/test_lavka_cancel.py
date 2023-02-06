import pytest

from supportai_actions.action_types.foodtech_client import lavka_cancel
from supportai_actions.actions import action as action_module
from supportai_actions.actions import features as feature_module
from supportai_actions.actions import params as params_module
from supportai_actions.actions import state as state_module


@pytest.fixture(name='cancellation_response')
def gen_cancellation_response(mockserver):
    @mockserver.json_handler('/grocery-support/internal/ml/v1/cancel')
    async def _(request):
        data_200 = {
            'compensation': {
                'id': 123,
                'description': 'smth',
                'type': 'promocode',
                'max_value': 100,
                'min_value': 50,
                'rate': 10,
                'is_full_refund': False,
                'promocode_info': {
                    'generated_promo': '777lol777',
                    'compensation_value': 75,
                    'currency': 'rub',
                    'status': 'success',
                },
                'refund_info': {
                    'compensation_value': 100500,
                    'currency': 'rub',
                    'status': 'error',
                },
            },
        }
        if (
                request.json.get('group') == 'kek'
                and request.json.get('reason') == 'lol'
        ):
            return mockserver.make_response(status=200, json=data_200)
        if (
                request.json.get('group') == 'kek'
                and request.json.get('reason') == 'lol2'
        ):
            return mockserver.make_response(status=200, json={})
        return mockserver.make_response(status=400, json={})


@pytest.mark.parametrize(
    '_call_param',
    [
        pytest.param(
            [params_module.ActionParam({'kek': 'lol'})],
            marks=pytest.mark.xfail(
                raises=action_module.ValidationError, strict=True,
            ),
        ),
        pytest.param(
            [params_module.ActionParam({'group': 1234, 'reason': 'kek'})],
            marks=pytest.mark.xfail(
                raises=action_module.ValidationError, strict=True,
            ),
        ),
        pytest.param(
            [params_module.ActionParam({'group': 'kek', 'reason': 1234})],
            marks=pytest.mark.xfail(
                raises=action_module.ValidationError, strict=True,
            ),
        ),
        pytest.param(
            [params_module.ActionParam({'group': 'kek', 'reason': 'lol'})],
        ),
    ],
)
async def test_lavka_cancel_validation(_call_param):
    _ = lavka_cancel.LavkaCancellationAction(
        'lavka_client_dialog', 'cancel', '1', _call_param,
    )


@pytest.mark.parametrize(
    'state, _call_param',
    [
        pytest.param(
            state_module.State(
                features=feature_module.Features(
                    features=[{'key': 'random_state', 'value': 'kek'}],
                ),
            ),
            [params_module.ActionParam({'group': 'kek', 'reason': 'lol'})],
            marks=pytest.mark.xfail(
                raises=action_module.ValidationError, strict=True,
            ),
        ),
        pytest.param(
            state_module.State(
                features=feature_module.Features(
                    features=[{'key': 'order_id', 'value': 'kek'}],
                ),
            ),
            [params_module.ActionParam({'group': 'kek', 'reason': 'lol'})],
        ),
    ],
)
async def test_lavka_cancel_state_validation(state, _call_param):
    action = lavka_cancel.LavkaCancellationAction(
        'lavka_client_dialog', 'cancel', '1', _call_param,
    )

    action.validate_state(state)


@pytest.mark.config(
    SUPPORTAI_ACTIONS_GROCERY_SUPPORT_POLLING_POLICY={
        'max_retries': 3,
        'sleep_duration': 200,
    },
)
@pytest.mark.parametrize(
    'state, _call_param',
    [
        (
            state_module.State(
                features=feature_module.Features(
                    features=[{'key': 'order_id', 'value': 'kek-grocery'}],
                ),
            ),
            [params_module.ActionParam({'group': 'kek', 'reason': 'lol'})],
        ),
        (
            state_module.State(
                features=feature_module.Features(
                    features=[{'key': 'order_id', 'value': 'kek-grocery'}],
                ),
            ),
            [params_module.ActionParam({'group': 'kek', 'reason': 'lol2'})],
        ),
    ],
)
async def test_lavka_cancel_call_200(
        web_context, state, _call_param, cancellation_response,
):
    action = lavka_cancel.LavkaCancellationAction(
        'lavka_client_dialog', 'cancel', '1', _call_param,
    )

    _state = await action(web_context, state)

    assert _state.features['group'] == 'kek'
    assert _state.features['reason'] in ['lol', 'lol2']

    if _state.features['reason'] == 'lol':
        assert _state.features['order_compensation_id'] == 123
        assert _state.features['order_compensation_description'] == 'smth'
        assert _state.features['order_compensation_type'] == 'promocode'
        assert _state.features['order_compensation_max_value'] == 100
        assert _state.features['order_compensation_min_value'] == 50
        assert _state.features['order_compensation_rate'] == 10
        assert _state.features['order_compensation_is_full_refund'] is False
        assert (
            _state.features[
                'order_compensation_promocode_info_generated_promo'
            ]
            == '777lol777'
        )
        assert (
            _state.features[
                'order_compensation_promocode_info_compensation_value'
            ]
            == 75
        )
        assert (
            _state.features['order_compensation_promocode_info_currency']
            == 'rub'
        )
        assert (
            _state.features['order_compensation_promocode_info_status']
            == 'success'
        )
        assert (
            _state.features[
                'order_compensation_refund_info_compensation_value'
            ]
            == 100500
        )
        assert (
            _state.features['order_compensation_refund_info_currency'] == 'rub'
        )
        assert (
            _state.features['order_compensation_refund_info_status'] == 'error'
        )


@pytest.mark.config(
    SUPPORTAI_ACTIONS_GROCERY_SUPPORT_POLLING_POLICY={
        'max_retries': 3,
        'sleep_duration': 200,
    },
)
@pytest.mark.parametrize(
    'state, _call_param',
    [
        (
            state_module.State(
                features=feature_module.Features(
                    features=[{'key': 'order_id', 'value': 'kek-grocery'}],
                ),
            ),
            [params_module.ActionParam({'group': 'kek', 'reason': 'not lol'})],
        ),
    ],
)
async def test_lavka_cancel_call_400(
        web_context, state, _call_param, cancellation_response,
):
    action = lavka_cancel.LavkaCancellationAction(
        'lavka_client_dialog', 'cancel', '1', _call_param,
    )

    _state = await action(web_context, state)

    assert _state.features['group'] == 'kek'
    assert _state.features['reason'] == 'not lol'
