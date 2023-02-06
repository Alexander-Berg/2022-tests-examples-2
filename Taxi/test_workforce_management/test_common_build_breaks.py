import datetime
import typing as tp

import pytest

from workforce_management.common.models import breaks as breaks_module
from workforce_management.common.models import shift as shift_module


@pytest.mark.parametrize(
    '',
    [
        pytest.param(
            marks=pytest.mark.config(
                WORKFORCE_MANAGEMENT_BREAK_BUILD_SETTINGS={
                    'use_new_order_approach': True,
                },
            ),
        ),
        pytest.param(
            marks=pytest.mark.config(
                WORKFORCE_MANAGEMENT_BREAK_BUILD_SETTINGS={
                    'use_new_order_approach': False,
                },
            ),
        ),
    ],
)
@pytest.mark.parametrize(
    'shift_duration, shift_start, break_rules, expected_breaks_len',
    [
        (
            510,
            datetime.datetime(2020, 1, 1),
            [
                breaks_module.BreakRule(
                    shift_duration_minutes_from=100,
                    shift_duration_minutes_to=1000,
                    breaks=[
                        {
                            'min_time_without_break_minutes': 45,
                            'max_time_without_break_minutes': 60,
                            'duration_minutes': 15,
                            'type': 'technical',
                            'count': 4,
                        },
                        {
                            'min_time_without_break_minutes': 120,
                            'max_time_without_break_minutes': 180,
                            'duration_minutes': 30,
                            'type': 'food',
                            'count': 1,
                        },
                    ],
                ),
            ],
            5,
        ),
        (
            660,
            datetime.datetime(2020, 1, 1),
            [
                breaks_module.BreakRule(
                    shift_duration_minutes_from=100,
                    shift_duration_minutes_to=1000,
                    breaks=[
                        {
                            'min_time_without_break_minutes': 45,
                            'max_time_without_break_minutes': 60,
                            'duration_minutes': 15,
                            'type': 'technical',
                            'count': 4,
                        },
                        {
                            'min_time_without_break_minutes': 120,
                            'max_time_without_break_minutes': 180,
                            'duration_minutes': 30,
                            'type': 'food',
                            'count': 1,
                        },
                    ],
                ),
            ],
            5,
        ),
        (
            960,
            datetime.datetime(2020, 1, 1),
            [
                breaks_module.BreakRule(
                    shift_duration_minutes_from=100,
                    shift_duration_minutes_to=1000,
                    breaks=[
                        {
                            'min_time_without_break_minutes': 105,
                            'max_time_without_break_minutes': 120,
                            'duration_minutes': 15,
                            'type': 'technical',
                            'count': 6,
                        },
                        {
                            'min_time_without_break_minutes': 45,
                            'max_time_without_break_minutes': 60,
                            'min_time_from_start_minutes': 180,
                            'max_time_from_start_minutes': 360,
                            'duration_minutes': 30,
                            'type': 'food',
                            'count': 1,
                        },
                    ],
                ),
            ],
            7,
        ),
    ],
)
async def test_breaks_building(
        stq3_context,
        shift_duration,
        shift_start,
        break_rules,
        expected_breaks_len,
):
    breaks = breaks_module.build_breaks_simple(
        stq3_context.config.WORKFORCE_MANAGEMENT_BREAK_BUILD_SETTINGS,
        shift_duration,
        shift_start,
        break_rules,
        shift_statistic=prepare_statistic(shift_start, shift_duration),
    )
    assert len(breaks) == expected_breaks_len


def prepare_statistic(
        shift_start: datetime.datetime, shift_duration: int,
) -> tp.Dict:
    statistic: tp.Dict = {}
    shift_module.update_statistic_by_shifts(
        [{'start': shift_start, 'duration_minutes': shift_duration}],
        statistic,
    )
    return statistic


@pytest.mark.config(
    WORKFORCE_MANAGEMENT_BREAK_BUILD_SETTINGS={'use_new_order_approach': True},
)
@pytest.mark.parametrize(
    'shift_duration, shift_start, break_rules,',
    [
        (
            720,
            datetime.datetime(2020, 1, 1),
            [
                breaks_module.BreakRule(
                    shift_duration_minutes_from=720,
                    shift_duration_minutes_to=779,
                    breaks=[
                        {
                            'min_time_without_break_minutes': 60,
                            'max_time_without_break_minutes': 180,
                            'duration_minutes': 15,
                            'type': 'technical',
                            'count': 4,
                        },
                        {
                            'min_time_without_break_minutes': 60,
                            'max_time_without_break_minutes': 180,
                            'allowed_breaks_count_before': [2, 3],
                            'duration_minutes': 30,
                            'type': 'food',
                            'count': 1,
                        },
                    ],
                ),
            ],
        ),
        (
            720,
            datetime.datetime(2020, 1, 1),
            [
                breaks_module.BreakRule(
                    shift_duration_minutes_from=720,
                    shift_duration_minutes_to=779,
                    breaks=[
                        {
                            'min_time_without_break_minutes': 60,
                            'max_time_without_break_minutes': 180,
                            'duration_minutes': 15,
                            'type': 'technical',
                            'count': 4,
                        },
                        {
                            'min_time_without_break_minutes': 60,
                            'max_time_without_break_minutes': 180,
                            'allowed_breaks_count_before': [2],
                            'duration_minutes': 30,
                            'type': 'food',
                            'count': 2,
                        },
                    ],
                ),
            ],
        ),
    ],
)
async def test_breaks_building_food(
        stq3_context, shift_duration, shift_start, break_rules,
):
    breaks = breaks_module.build_breaks_simple(
        stq3_context.config.WORKFORCE_MANAGEMENT_BREAK_BUILD_SETTINGS,
        shift_duration,
        shift_start,
        break_rules,
        shift_statistic=prepare_statistic(shift_start, shift_duration),
    )

    food_break_description = [
        break_['allowed_breaks_count_before']
        for break_ in break_rules[0].breaks
        if break_['type'] == 'food'
    ][0]
    food_break_description = tp.cast(tp.List[int], food_break_description)

    food_index = [
        break_index
        for break_index, break_ in enumerate(breaks)
        if break_['type'] == 'food'
    ]

    cumulative_sum = 0
    for index in food_index:
        assert index - cumulative_sum in food_break_description
        cumulative_sum += index
