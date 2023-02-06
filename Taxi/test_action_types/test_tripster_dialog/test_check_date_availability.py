# flake8: noqa: I100
# pylint: disable=broad-except
import pytest

from supportai_actions.actions import state as state_module
from supportai_actions.actions import features as feature_module

from supportai_actions.action_types.tripster_dialog import (
    check_date_availability,
)


@pytest.mark.parametrize(
    'state, _call_params',
    [
        (
            state_module.State(
                features=feature_module.Features(
                    features=[
                        {
                            'key': 'date_excursion',
                            'value': ['2015-11-23T17:27:05.184397'],
                        },
                        {'key': 'experience_id', 'value': 18072},
                        {'key': 'date_available', 'value': False},
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
                            'key': 'date_excursion',
                            'value': ['2021-12-05T17:27:05.184397'],
                        },
                        {'key': 'experience_id', 'value': 18072},
                        {'key': 'date_available', 'value': False},
                    ],
                ),
            ),
            [],
        ),
    ],
)
async def test_check_date_availability_call(web_context, _call_params, state):
    action = check_date_availability.CheckDateAvailabilityAction(
        'tripster_dialog', 'check_date_availability', '1', _call_params,
    )

    _state = await action(web_context, state)
    assert _state.features == state.features
