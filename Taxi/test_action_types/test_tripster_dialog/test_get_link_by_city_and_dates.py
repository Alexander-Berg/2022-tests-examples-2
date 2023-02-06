# flake8: noqa: I100
# pylint: disable=broad-except
import pytest

from supportai_actions.actions import state as state_module
from supportai_actions.actions import features as feature_module
from supportai_actions.action_types.tripster_dialog import (
    get_link_by_city_and_dates,
)


@pytest.mark.parametrize(
    'state, _call_params',
    [
        (
            state_module.State(
                features=feature_module.Features(
                    features=[
                        {'key': 'city_ascii_name', 'value': 'Moscow'},
                        {
                            'key': 'date_excursion',
                            'value': [
                                '2021-12-05T20:32:22.637340',
                                '2021-12-16T20:32:22.637399',
                            ],
                        },
                        {
                            'key': 'excursion_link',
                            'value': (
                                'https://experience.tripster.ru/experience/'
                                'Moscow/?start_date=2021-12-05&end_date=2021-12-16'
                                '&filter_type=date'
                            ),
                        },
                    ],
                ),
            ),
            [],
        ),
    ],
)
async def test_get_link_by_city_and_dates_action_call(
        web_context, _call_params, state,
):
    action = get_link_by_city_and_dates.GetLinkByCityAndDatesAction(
        'tripster_dialog', 'get_link_by_city_and_dates', '1', _call_params,
    )

    _state = await action(web_context, state)

    assert _state.features == state.features
