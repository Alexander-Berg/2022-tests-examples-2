# flake8: noqa: I100
# pylint: disable=broad-except
import pytest

from supportai_actions.actions import action as action_module
from supportai_actions.actions import features as feature_module
from supportai_actions.actions import state as state_module

from supportai_actions.action_types.litres_dialog import get_promo_features


@pytest.mark.parametrize('_call_params', [[]])
async def test_litres_promocode_action_validate(_call_params):
    get_promo_features.GetPromoFeaturesAction(
        'litres_dialog', 'litres_dialog_promocodes', '0', _call_params,
    )


@pytest.mark.parametrize(
    'state, _call_params',
    [
        (
            state_module.State(
                features=feature_module.Features(
                    features=[{'key': 'ticket_id', 'value': 'some'}],
                ),
            ),
            [],
        ),
        pytest.param(
            state_module.State(
                features=feature_module.Features(
                    features=[{'key': 'no_ticket_id', 'value': 'some'}],
                ),
            ),
            [],
            marks=pytest.mark.xfail(
                raises=action_module.ValidationError, strict=True,
            ),
        ),
    ],
)
async def test_litres_promocode_action_validate_state(state, _call_params):
    get_promo_features.GetPromoFeaturesAction(
        'litres_dialog', 'litres_dialog_promocodes', '0', _call_params,
    ).validate_state(state)


@pytest.mark.pgsql('supportai_actions', files=['sample.sql'])
@pytest.mark.parametrize(
    'state, _call_params',
    [
        (
            state_module.State(
                features=feature_module.Features(
                    features=[{'key': 'ticket_id', 'value': 'gained'}],
                ),
            ),
            [],
        ),
    ],
)
async def test_litres_promocode_used_action_call(
        web_context, _call_params, state,
):
    action = get_promo_features.GetPromoFeaturesAction(
        'litres_dialog', 'litres_dialog_promocodes', '1', _call_params,
    )

    output_state = await action(web_context, state)
    assert len(output_state.features) == 2
    assert output_state.features.get('promocode_expired_at') is None


@pytest.mark.pgsql('supportai_actions', files=['sample.sql'])
@pytest.mark.parametrize(
    'state, _call_params',
    [
        (
            state_module.State(
                features=feature_module.Features(
                    features=[{'key': 'ticket_id', 'value': 'lolkek1'}],
                ),
            ),
            [],
        ),
    ],
)
async def test_litres_promocode_different_action_calls(
        web_context, _call_params, state,
):
    action = get_promo_features.GetPromoFeaturesAction(
        'litres_dialog', 'litres_dialog_promocodes', '1', _call_params,
    )

    output_state_1 = await action(web_context, state)
    assert len(output_state_1.features) == 3
    assert output_state_1.features.get('promocode_code') == 'XXX-02-XXXX'
    assert output_state_1.features.get('promocode_expired_at') == '11-05-2022'

    state_2 = state_module.State(
        features=feature_module.Features(
            features=[{'key': 'ticket_id', 'value': 'lolkek2'}],
        ),
    )
    output_state_2 = await action(web_context, state_2)
    assert len(output_state_2.features) == 3
    assert output_state_2.features.get('promocode_code') == 'XXX-03-XXXX'
    assert output_state_2.features.get('promocode_expired_at') == '11-05-2022'


@pytest.mark.pgsql('supportai_actions', files=['sample.sql'])
@pytest.mark.parametrize(
    'state, _call_params',
    [
        (
            state_module.State(
                features=feature_module.Features(
                    features=[{'key': 'ticket_id', 'value': 'lolkek'}],
                ),
            ),
            [],
        ),
    ],
)
async def test_litres_promocode_double_call_action_call(
        web_context, _call_params, state,
):
    action = get_promo_features.GetPromoFeaturesAction(
        'litres_dialog', 'litres_dialog_promocodes', '1', _call_params,
    )

    output_state_1 = await action(web_context, state)
    assert len(output_state_1.features) == 3
    assert output_state_1.features.get('promocode_code') == 'XXX-02-XXXX'
    assert output_state_1.features.get('promocode_expired_at') == '11-05-2022'

    output_state_2 = await action(web_context, state)
    assert len(output_state_2.features) == 2
    assert output_state_2.features.get('promocode_expired_at') is None
