# pylint: disable=redefined-outer-name
import pytest

from eats_courier_scoring.generated.cron import run_cron
from test_eats_courier_scoring import conftest
from test_eats_courier_scoring import consts

SETTINGS = {
    'blocking': {
        'min_score': 1,
        'reapplication_days': 1,
        'punishment_type': 'blocking',
        'worst_percentage': 100,
        'task_name': 'calculation_score_couriers',
        'punishment_kwargs': {'mechanics': 'mechanics'},
    },
    'communication_hard': {
        'min_score': 1,
        'reapplication_days': 1,
        'punishment_type': 'communication',
        'worst_percentage': 10,
        'task_name': 'calculation_score_couriers',
        'punishment_kwargs': {'title': 'title', 'text': 'text'},
    },
    'communication': {
        'min_score': 1,
        'reapplication_days': 1,
        'punishment_type': 'communication',
        'worst_percentage': 100,
        'task_name': 'calculation_score_couriers',
        'punishment_kwargs': {'title': 'title', 'text': 'text'},
    },
    'startrek': {
        'min_score': 1,
        'reapplication_days': 1,
        'punishment_type': 'startrek',
        'worst_percentage': 100,
        'task_name': 'calculation_score_couriers',
    },
}


@pytest.mark.config(
    EATS_COURIER_SCORING_DEFECT_TYPES=consts.EATS_COURIER_SCORING_DEFECT_TYPES,
    EATS_COURIER_SCORING_PUNISHMENTS_BY_NAME=SETTINGS,
    EATS_COURIER_SCORING_LIMITS_BY_REGION={
        'punishments_count_period': 7,
        'active_couriers_count_period': 7,
        'punishments': {
            'communication': {'region': {'count': 2, 'percent': 0.1}},
        },
    },
    EATS_COURIER_SCORING_STARTREK_SETTINGS_BY_REGION=(
        consts.EATS_COURIER_SCORING_STARTREK_SETTINGS_BY_REGION
    ),
)
@pytest.mark.translations()
@conftest.create_exp3_response(
    1,
    True,
    ['communication', 'startrek', 'blocking'],
    consts.CONFIG_DEFECT_SCORES,
)
@conftest.create_exp3_response(2, False)
async def test_calculation_score_couriers(
        cron_context,
        patch_load_couriers_and_defects,
        patch_get_active_couriers_count_by_region,
):
    patch_load_couriers_and_defects([1, 2, 3, 4, 5])
    patch_get_active_couriers_count_by_region({'region': 10})
    async with conftest.DiffCountPunishments(cron_context, 3):
        await run_cron.main(
            [
                'eats_courier_scoring.crontasks.calculation_score_couriers',
                '-t',
                '0',
            ],
        )


@pytest.mark.parametrize(
    ('region_config', 'expected_new_blocks'),
    (
        # 2 blocks for region for last 3 days
        (
            {
                'punishments_count_period': 3,
                'active_couriers_count_period': 7,
                'punishments': {},
            },
            5,
        ),
        (
            {
                'punishments_count_period': 3,
                'active_couriers_count_period': 7,
                'punishments': {'permanent_block': {'region': {'count': 3}}},
            },
            1,
        ),
        (
            {
                'punishments_count_period': 3,
                'active_couriers_count_period': 7,
                'punishments': {'permanent_block': {'region': {'count': 5}}},
            },
            3,
        ),
        (
            {
                'punishments_count_period': 3,
                'active_couriers_count_period': 7,
                'punishments': {
                    'permanent_block': {'region': {'percent': 30.0}},
                },
            },
            1,  # 10 active couriers, 2 blocked 2 days ago
        ),
    ),
)
@pytest.mark.config(
    EATS_COURIER_SCORING_PUNISHMENTS_BY_NAME={
        'permanent_block': {
            'min_score': 1,
            'reapplication_days': 1,
            'punishment_type': 'blocking',
            'worst_percentage': 100,
            'punishment_kwargs': {
                'blocking_days': 20,
                'mechanics': 'mechanics',
            },
            'task_name': 'calculation_score_couriers',
        },
    },
    EATS_COURIER_SCORING_PUNISHMENTS_BY_TASK={
        'calculation_score_couriers': ['permanent_block'],
    },
)
@pytest.mark.pgsql('eats_courier_scoring', files=['init_punishments_db.sql'])
@conftest.create_exp3_response(
    1, True, ['permanent_block'], consts.CONFIG_DEFECT_SCORES,
)
@conftest.create_exp3_response(
    2, True, ['permanent_block'], consts.CONFIG_DEFECT_SCORES,
)
@conftest.create_exp3_response(
    3, True, ['permanent_block'], consts.CONFIG_DEFECT_SCORES,
)
@conftest.create_exp3_response(
    4, True, ['permanent_block'], consts.CONFIG_DEFECT_SCORES,
)
@conftest.create_exp3_response(
    5, True, ['permanent_block'], consts.CONFIG_DEFECT_SCORES,
)
async def test_regional_rules(
        cron_context,
        patch_load_couriers_and_defects,
        patch_get_active_couriers_count_by_region,
        taxi_config,
        region_config,
        expected_new_blocks,
):
    taxi_config.set_values(
        {'EATS_COURIER_SCORING_LIMITS_BY_REGION': region_config},
    )
    patch_load_couriers_and_defects([1, 2, 3, 4, 5])
    patch_get_active_couriers_count_by_region({'region': 10})

    async with conftest.DiffCountPunishments(
            cron_context, expected_new_blocks,
    ):
        await run_cron.main(
            [
                'eats_courier_scoring.crontasks.calculation_score_couriers',
                '-t',
                '0',
            ],
        )
