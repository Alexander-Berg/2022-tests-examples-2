# flake8: noqa: I100
# pylint: disable=broad-except
import pytest

from supportai_actions.actions import action as action_module
from supportai_actions.actions import params as param_module
from supportai_actions.actions import features as feature_module
from supportai_actions.actions import state as state_module

from supportai_actions.action_types.detmir_dialog import get_geo2store_id


@pytest.mark.parametrize('_call_params', [[]])
async def test_detmir_geo2store_id_action_validate(_call_params):
    get_geo2store_id.GetStoreIDAction(
        'detmir_dialog', 'geo_stores2ids_dm', '0', _call_params,
    )


@pytest.mark.parametrize(
    'state, _call_params',
    [
        (
            state_module.State(
                features=feature_module.Features(
                    features=[{'key': 'metro', 'value': 'выставочная'}],
                ),
            ),
            [],
        ),
        pytest.param(
            state_module.State(
                features=feature_module.Features(
                    features=[{'key': 'no_city', 'value': 'some'}],
                ),
            ),
            [],
        ),
    ],
)
async def test_detmir_geo2store_id_action_validate_state(state, _call_params):
    get_geo2store_id.GetStoreIDAction(
        'detmir_dialog', 'geo_stores2ids_dm', '0', _call_params,
    ).validate_state(state)


@pytest.mark.pgsql('supportai_actions', files=['sample.sql'])
@pytest.mark.parametrize(
    'state, _call_params',
    [
        (
            state_module.State(
                features=feature_module.Features(
                    features=[
                        {'key': 'metro', 'value': 'выставочная'},
                        {'key': 'store_id', 'value': '1976'},
                    ],
                ),
            ),
            [],
        ),
    ],
)
async def test_detmir_geo2store_id_action_call(
        web_context, _call_params, state,
):
    action = get_geo2store_id.GetStoreIDAction(
        'detmir_dialog', 'geo_stores2ids_dm', '1', _call_params,
    )

    _state = await action(web_context, state)

    assert _state.features == state.features
