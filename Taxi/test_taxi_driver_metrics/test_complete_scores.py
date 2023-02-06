import pytest

from taxi_driver_metrics.common.models.complete_scores import level_settings


@pytest.mark.parametrize(
    'scores, result, level_num',
    (
        (
            7,
            {
                'scores_to_reach': 7,
                'priority': 99,
                'is_current': False,
                'benefits': {'immunity': {'count': 1}},
            },
            6,
        ),
        (
            8,
            {
                'scores_to_reach': 7,
                'priority': 99,
                'is_current': False,
                'benefits': {'immunity': {'count': 1}},
            },
            6,
        ),
        (0, {'scores_to_reach': 0, 'priority': 0, 'is_current': True}, 3),
        (1, {'scores_to_reach': 1, 'priority': 1, 'is_current': False}, 4),
        (-1, {'scores_to_reach': -1, 'priority': -2, 'is_current': False}, 2),
    ),
)
async def test_processing_complete_scores(
        stq3_context, taxi_config, scores, result, dms_mockserver, level_num,
):
    range_levels = await level_settings.get_score_levels(
        stq3_context, 'izhesvk', '', set(),
    )
    scores = range_levels.by_range(scores)
    assert scores == level_settings.LevelBasedRangeDict.from_json_to_level(
        result, level_num=level_num,
    )


@pytest.mark.parametrize(
    'scores, result',
    (
        (7, (3, False)),
        (11, (4, True)),
        (16, (None, True)),
        (4, (3, False)),
        (3, (4, False)),
        (-6, (1, False)),
    ),
)
async def test_complete_scores_next_level(
        stq3_context, taxi_config, scores, result, dms_mockserver,
):
    range_levels = level_settings.LevelBasedRangeDict(
        [
            {
                'scores_to_reach': -8,
                'priority': -3,
                'is_current': False,
                'punishments': {'blocking': {'duration_seconds': 360}},
            },
            {
                'scores_to_reach': -5,
                'priority': -3,
                'is_current': False,
                'punishments': {'blocking': {'duration_seconds': 60}},
            },
            {'scores_to_reach': -3, 'priority': -3, 'is_current': False},
            {'scores_to_reach': -1, 'priority': -2, 'is_current': False},
            {'scores_to_reach': 0, 'priority': 0, 'is_current': True},
            {'scores_to_reach': 1, 'priority': 1, 'is_current': False},
            {'scores_to_reach': 3, 'priority': 5, 'is_current': False},
            {'scores_to_reach': 7, 'priority': 99, 'is_current': False},
            {
                'scores_to_reach': 10,
                'priority': 99,
                'is_current': False,
                'benefits': {'immunity': {'count': 1}},
            },
            {
                'scores_to_reach': 15,
                'priority': 99,
                'is_current': False,
                'benefits': {'immunity': {'count': 1}},
            },
        ],
    )

    data = range_levels.next_level_info(scores)
    assert data == result


@pytest.mark.parametrize(
    'current_score, add_levels, result, level_num',
    (
        (
            7,
            1,
            {
                'scores_to_reach': 7,
                'priority': 99,
                'is_current': False,
                'benefits': {'immunity': {'count': 1}},
            },
            6,
        ),
        (8, -3, {'priority': 0, 'scores_to_reach': 0, 'is_current': True}, 3),
        (
            0,
            -1,
            {'priority': -2, 'scores_to_reach': -1, 'is_current': False},
            2,
        ),
        (
            1,
            10,
            {
                'priority': 99,
                'scores_to_reach': 7,
                'is_current': False,
                'benefits': {'immunity': {'count': 1}},
            },
            6,
        ),
        (
            1,
            -25,
            {
                'priority': -3,
                'scores_to_reach': -3,
                'is_current': False,
                'punishments': {'blocking': {'duration_seconds': 60}},
            },
            1,
        ),
        (-1, 3, {'priority': 5, 'scores_to_reach': 3, 'is_current': False}, 5),
    ),
)
async def test_complete_scores_levels(
        stq3_context,
        taxi_config,
        current_score,
        add_levels,
        result,
        dms_mockserver,
        level_num,
):
    range_levels = await level_settings.get_score_levels(
        stq3_context, 'izhesvk', '', set(),
    )
    add_result = range_levels.add_levels(current_score, add_levels)
    assert add_result == level_settings.LevelBasedRangeDict.from_json_to_level(
        result, level_num=level_num,
    )
