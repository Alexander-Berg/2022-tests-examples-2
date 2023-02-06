import datetime

import pytest

from delivery.models import avito as avito_models


@pytest.mark.parametrize(
    'config, now, previous_ts, max_period_minutes, nsubs',
    [
        pytest.param(
            {
                'city1': {
                    'turbo_sale&xl': {
                        'item_ids': [1, 2, 3, 4],
                        'time_of_day_start': '09:00',
                        'time_of_day_finish': '12:00',
                    },
                },
            },
            datetime.datetime(2020, 4, 21, 12, 0, 0),
            datetime.datetime(2020, 4, 21, 8, 59, 0),
            180,
            4,
            id='no period_minutes',
        ),
        pytest.param(
            {
                'city1': {
                    'pushup': {
                        'item_ids': [1, 2, 3],
                        'time_of_day_start': '09:00',
                        'time_of_day_finish': '18:00',
                        'period_minutes': 30,
                    },
                },
            },
            datetime.datetime(2020, 4, 21, 18, 0, 0),
            datetime.datetime(2020, 4, 21, 8, 59, 0),
            60 * 9,
            2 * 9,
            id='with period_minutes',
        ),
    ],
)
async def test_generate_subscriptions(
        config, now, previous_ts, max_period_minutes, nsubs,
):
    avito_models.MAX_PERIOD_MINUTES = max_period_minutes
    subscriptions = avito_models.subscriptions_from_config(
        config, now, previous_ts,
    )
    assert len(subscriptions) == nsubs
