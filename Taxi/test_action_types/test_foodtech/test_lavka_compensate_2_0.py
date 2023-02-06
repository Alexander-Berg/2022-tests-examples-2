import pytest

from supportai_actions.action_types.foodtech_client import lavka_compensate_2_0
from supportai_actions.actions import action as action_module
from supportai_actions.actions import features as feature_module
from supportai_actions.actions import params as params_module
from supportai_actions.actions import state as state_module


@pytest.fixture(name='compensation_response')
def gen_compensation_response(mockserver):
    @mockserver.json_handler(
        '/grocery-support/internal/ml/v1/get-compensation-by-situation-code',
    )
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
        if request.json.get('situation_code') == 'kek':
            return mockserver.make_response(status=200, json=data_200)
        return mockserver.make_response(status=404, json={})


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
            [params_module.ActionParam({'situation_code': 1234})],
            marks=pytest.mark.xfail(
                raises=action_module.ValidationError, strict=True,
            ),
        ),
        pytest.param([params_module.ActionParam({'situation_code': 'kek'})]),
        pytest.param(
            [
                params_module.ActionParam({'situation_code': 'kek'}),
                params_module.ActionParam({'custom_voucher_value': 'kek'}),
            ],
            marks=pytest.mark.xfail(
                raises=action_module.ValidationError, strict=True,
            ),
        ),
        pytest.param(
            [
                params_module.ActionParam({'situation_code': 'kek'}),
                params_module.ActionParam({'custom_voucher_value': 123}),
            ],
        ),
    ],
)
async def test_lavka_compensate_2_0_validation(_call_param):
    _ = lavka_compensate_2_0.LavkaCompensate20Action(
        'lavka_client_dialog', 'compensate', '2', _call_param,
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
            [params_module.ActionParam({'situation_code': 'lol'})],
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
            [params_module.ActionParam({'situation_code': 'lol'})],
        ),
    ],
)
async def test_lavka_compensate_2_0_state_validation(state, _call_param):
    action = lavka_compensate_2_0.LavkaCompensate20Action(
        'lavka_client_dialog', 'compensate', '2', _call_param,
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
                    features=[{'key': 'order_id', 'value': 'keklol-grocery'}],
                ),
            ),
            [params_module.ActionParam({'situation_code': 'kek'})],
        ),
        (
            state_module.State(
                features=feature_module.Features(
                    features=[{'key': 'order_id', 'value': 'keklol-grocery'}],
                ),
            ),
            [
                params_module.ActionParam({'situation_code': 'kek'}),
                params_module.ActionParam({'custom_voucher_value': 123}),
            ],
        ),
    ],
)
async def test_lavka_compensate_2_0_call_200(
        web_context, state, _call_param, compensation_response,
):
    action = lavka_compensate_2_0.LavkaCompensate20Action(
        'lavka_client_dialog', 'compensate', '2', _call_param,
    )

    _state = await action(web_context, state)

    assert _state.features['situation_code'] == 'kek'
    if (
            params_module.find_param('custom_voucher_value', _call_param)
            is not None
    ):
        assert _state.features['custom_voucher_value'] == 123
    else:
        assert 'custom_voucher_value' not in _state.features

    assert _state.features['order_compensation_id'] == 123
    assert _state.features['order_compensation_description'] == 'smth'
    assert _state.features['order_compensation_type'] == 'promocode'
    assert _state.features['order_compensation_max_value'] == 100
    assert _state.features['order_compensation_min_value'] == 50
    assert _state.features['order_compensation_rate'] == 10
    assert _state.features['order_compensation_is_full_refund'] is False
    assert (
        _state.features['order_compensation_promocode_info_generated_promo']
        == '777lol777'
    )
    assert (
        _state.features['order_compensation_promocode_info_compensation_value']
        == 75
    )
    assert (
        _state.features['order_compensation_promocode_info_currency'] == 'rub'
    )
    assert (
        _state.features['order_compensation_promocode_info_status']
        == 'success'
    )
    assert (
        _state.features['order_compensation_refund_info_compensation_value']
        == 100500
    )
    assert _state.features['order_compensation_refund_info_currency'] == 'rub'
    assert _state.features['order_compensation_refund_info_status'] == 'error'


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
                    features=[{'key': 'order_id', 'value': 'onfodf-grocery'}],
                ),
            ),
            [params_module.ActionParam({'situation_code': 'lol'})],
        ),
        (
            state_module.State(
                features=feature_module.Features(
                    features=[{'key': 'order_id', 'value': 'onfodf-grocery'}],
                ),
            ),
            [
                params_module.ActionParam({'situation_code': 'lol'}),
                params_module.ActionParam({'custom_voucher_value': 123}),
            ],
        ),
    ],
)
async def test_lavka_compensate_2_0_call_404(
        web_context, state, _call_param, compensation_response,
):
    action = lavka_compensate_2_0.LavkaCompensate20Action(
        'lavka_client_dialog', 'compensate', '2', _call_param,
    )

    _state = await action(web_context, state)

    assert _state.features['situation_code'] == 'lol'
    if (
            params_module.find_param('custom_voucher_value', _call_param)
            is not None
    ):
        assert _state.features['custom_voucher_value'] == 123
        assert len(_state.features) == 4
    else:
        assert 'custom_voucher_value' not in _state.features
        assert len(_state.features) == 3
