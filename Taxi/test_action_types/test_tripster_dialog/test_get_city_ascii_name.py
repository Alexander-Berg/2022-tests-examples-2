# flake8: noqa: I100
# pylint: disable=broad-except
import pytest

from supportai_actions.actions import state as state_module
from supportai_actions.actions import features as feature_module

from supportai_actions.action_types.tripster_dialog import get_city_ascii_name


@pytest.mark.pgsql('supportai_actions', files=['sample.sql'])
@pytest.mark.parametrize(
    'state, _call_params',
    [
        (
            state_module.State(
                features=feature_module.Features(
                    features=[
                        {'key': 'city_excursion_text', 'value': 'джубга'},
                        {'key': 'city_ascii_name', 'value': 'Dzhubga'},
                    ],
                ),
            ),
            [],
        ),
        (
            state_module.State(
                features=feature_module.Features(
                    features=[
                        {
                            'key': 'city_excursion_text',
                            'value': 'гусь-хрустальный',
                        },
                        {'key': 'city_ascii_name', 'value': 'Gus_Khrustalny'},
                    ],
                ),
            ),
            [],
        ),
    ],
)
async def test_get_city_ascii_name_action_call(
        web_context, _call_params, state,
):
    action = get_city_ascii_name.GetCityAsciiNameAction(
        'tripster_dialog', 'get_city_ascii_name', '1', _call_params,
    )

    _state = await action(web_context, state)
    assert _state.features == state.features
