# pylint: disable=redefined-outer-name
import pytest

from eats_courier_scoring.generated.cron import run_cron
from test_eats_courier_scoring import conftest
from test_eats_courier_scoring import consts

CRONTASK = 'eats_courier_scoring.crontasks.punish_couriers_with_low_orders'
SETTINGS = {
    'low_orders_block': {
        'min_score': 1,
        'reapplication_days': 1,
        'punishment_type': 'blocking',
        'worst_percentage': 80,
        'task_name': 'punish_couriers_with_low_orders',
        'punishment_kwargs': {'mechanics': 'mechanics'},
    },
    'low_orders_communication': {
        'min_score': 1,
        'reapplication_days': 1,
        'punishment_type': 'communication',
        'worst_percentage': 80,
        'task_name': 'punish_couriers_with_low_orders',
        'punishment_kwargs': {'title': 'title', 'text': 'text'},
    },
}


@pytest.mark.config(EATS_COURIER_SCORING_PUNISHMENTS_BY_NAME=SETTINGS)
@conftest.create_exp3_response(
    1,
    True,
    ['low_orders_block', 'low_orders_communication'],
    consts.CONFIG_DEFECT_SCORES,
)
@conftest.create_exp3_response(
    2, False, defect_scores=consts.CONFIG_DEFECT_SCORES,
)
@conftest.create_exp3_response(
    3,
    True,
    ['low_orders_block', 'low_orders_communication'],
    consts.CONFIG_DEFECT_SCORES,
)
@conftest.create_exp3_response(
    4,
    True,
    ['low_orders_block', 'low_orders_communication'],
    consts.CONFIG_DEFECT_SCORES,
)
async def test_punish_couriers_with_low_orders(
        cron_context, patch_load_couriers_and_defects,
):
    patch_load_couriers_and_defects([1, 2, 3, 4, 5])
    async with conftest.DiffCountPunishmentsByName(
            cron_context,
            {'low_orders_block': 3, 'low_orders_communication': 3},
    ):
        await run_cron.main([CRONTASK, '-t', '0'])
