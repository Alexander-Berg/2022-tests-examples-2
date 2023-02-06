# pylint: disable=W0212
import copy

import pytest

from eats_courier_scoring.common import db
from eats_courier_scoring.common import entities
from eats_courier_scoring.common import punishments
from test_eats_courier_scoring import conftest
from test_eats_courier_scoring import consts

SCORES_BY_DEFECT_TYPE = {1: {entities.DefectType('new_defect'): 1.0}}
EXPERIMENT = {1}
COURIERS_MODELS = {1: conftest.create_courier_model(1)}
DEFECTS = {1: [conftest.create_defect(1, order_id=1)]}
COURIERS = [
    entities.Courier(
        model=model,
        defects=DEFECTS.get(model.courier_id, []),
        scores_by_defect_type=SCORES_BY_DEFECT_TYPE[model.courier_id],
    )
    for model in COURIERS_MODELS.values()
]


async def get_history(context):
    return await db.get_last_punishments(context, [1])


@pytest.mark.parametrize(
    'punishment_config',
    [
        {
            'test_punishment': {
                'min_score': 0,
                'reapplication_days': 1,
                'worst_percentage': 100,
                'punishment_type': 'communication',
                'task_name': 'task_name',
                'punishment_kwargs': {'title': 'title', 'text': 'text'},
            },
            'test_punishment_2': {
                'min_score': 0,
                'reapplication_days': 1,
                'worst_percentage': 100,
                'punishment_type': 'communication',
                'task_name': 'task_name',
                'punishment_kwargs': {'title': 'title', 'text': 'text'},
            },
        },
        {
            'test_punishment': {
                'min_score': 1,
                'reapplication_days': 1,
                'worst_percentage': 100,
                'punishment_type': 'blocking',
                'task_name': 'task_name',
                'punishment_kwargs': {'mechanics': 'mechanics'},
            },
        },
    ],
)
async def test_punishments(
        cron_context,
        mock_driver_wall_add,
        patch_create_startrack_ticket,
        punishment_config,
):
    punishment_contexts = punishments.parse_punishments_config(
        punishment_config,
        task_name='task_name',
        region_stats={},
        region_rules={},
    )

    patch_create_startrack_ticket({})
    mock_driver_wall_add(
        check_request_drivers=[
            {'driver': '1_1', 'title': 'title', 'text': 'text'},
        ],
    )

    for correct_count_punishments, punishment_context in enumerate(
            punishment_contexts, start=1,
    ):
        punishment_name = punishment_context.punishment_name
        punishment_type = punishment_context.punishment_type

        res = await punishment_context.apply_punishments(
            cron_context,
            experiment_courier_ids=EXPERIMENT,
            active_couriers_by_region={},
            couriers=COURIERS,
        )
        assert len(res) == 1

        history = await get_history(cron_context)
        history_by_name = {h.punishment_name: h for h in history}
        assert len(history_by_name) == correct_count_punishments
        assert history_by_name[punishment_name].courier_id == 1
        assert (
            history_by_name[punishment_name].punishment_type == punishment_type
        )

        res = await punishment_context.apply_punishments(
            cron_context,
            experiment_courier_ids=EXPERIMENT,
            active_couriers_by_region={},
            couriers=COURIERS,
        )
        assert len(res) == 1

        history = await get_history(cron_context)
        assert len(history) == correct_count_punishments


@pytest.mark.parametrize(
    'punishment_config',
    [
        {
            'min_score': 1,
            'reapplication_days': 1,
            'worst_percentage': 100,
            'punishment_type': 'blocking',
            'punishment_kwargs': {'mechanics': 'mechanics'},
        },
    ],
)
async def test_other_history(
        cron_context,
        mock_driver_wall_add,
        patch_create_startrack_ticket,
        punishment_config,
):
    patch_create_startrack_ticket({})

    mock_driver_wall_add(
        check_request_drivers=[
            {'driver': '1_1', 'title': 'title', 'text': 'text'},
        ],
    )

    communication = punishments.parse_punishment_config(
        'communication',
        {
            'min_score': 1,
            'reapplication_days': 1,
            'worst_percentage': 100,
            'punishment_type': 'communication',
            'punishment_kwargs': {'title': 'title', 'text': 'text'},
        },
        {},
        {},
    )
    res = await communication.apply_punishments(
        cron_context,
        experiment_courier_ids=EXPERIMENT,
        active_couriers_by_region={},
        couriers=COURIERS,
    )
    assert len(res) == 1
    history = await get_history(cron_context)
    couriers = copy.deepcopy(COURIERS)
    entities.update_last_punishments(couriers, history)

    punishment = punishments.parse_punishment_config(
        'punishment', punishment_config, {}, {},
    )
    res = await punishment.apply_punishments(
        cron_context,
        experiment_courier_ids=EXPERIMENT,
        active_couriers_by_region={},
        couriers=couriers,
    )
    assert len(res) == 1

    history = await get_history(cron_context)
    assert len(history) == 2


@pytest.mark.parametrize(
    ('region_blocks', 'region_rules', 'expected_blocks'),
    (
        # not regional rules
        (0, {}, 5),
        (5, {}, 5),
        # regional rules with absolute value (_filter_ids_by_absolute_limit)
        (0, {'count': 5}, 5),
        (0, {'count': 10}, 5),
        (5, {'count': 5}, 0),
        (6, {'count': 5}, 0),
        (2, {'count': 5}, 3),
        (1, {'count': 3}, 2),
        (4, {'count': 5}, 1),
        # regional rules with percent value (_filter_ids_by_percent_limit)
        # total active couriers - 10
        (0, {'percent': 10.0}, 1),
        (0, {'percent': 25.0}, 2),
        (0, {'percent': 29.99}, 2),
        (0, {'percent': 50.0}, 5),
        (2, {'percent': 70.0}, 5),
        (5, {'percent': 70.0}, 2),
        # regional rules with absolute and percent
        (0, {'count': 10, 'percent': 100.0}, 5),
        (0, {'count': 5, 'percent': 100.0}, 5),
        (0, {'count': 3, 'percent': 100.0}, 3),
        (0, {'count': 10, 'percent': 50.0}, 5),
        (0, {'count': 10, 'percent': 30.0}, 3),
        (0, {'count': 2, 'percent': 30.0}, 2),
        (2, {'count': 10, 'percent': 50.0}, 3),
        (2, {'count': 4, 'percent': 50.0}, 2),
        (2, {'count': 5, 'percent': 50.0}, 3),
        (2, {'count': 6, 'percent': 50.0}, 3),
        (2, {'count': 10, 'percent': 30.0}, 1),
        (2, {'count': 10, 'percent': 20.0}, 0),
    ),
)
async def test_region_filter(region_blocks, region_rules, expected_blocks):
    punishment = punishments.BlockingPunishmentContext(
        name='permanent_block',
        settings={
            'min_score': 1,
            'reapplication_days': 1,
            'worst_percentage': 100,
            'punishment_type': 'blocking',
            'punishment_kwargs': {'mechanics': 'mechanics'},
        },
        region_stats={'permanent_block': {'region': region_blocks}},
        region_rules={
            'punishments': {'permanent_block': {'region': region_rules}},
        },
    )

    couriers_ids = {1, 2, 3, 4, 5}
    couriers = [
        entities.Courier(
            model=conftest.create_courier_model(courier_id=x, region='region'),
            defects=[],
        )
        for x in couriers_ids
    ]
    ids = punishment._filter_ids_by_region_limits(
        couriers=couriers, active_couriers_by_region={'region': 10},
    )
    assert len(ids) == expected_blocks


@pytest.mark.config(
    EATS_COURIER_SCORING_DEFECT_TYPES=consts.EATS_COURIER_SCORING_DEFECT_TYPES,
    EATS_COURIER_SCORING_STARTREK_SETTINGS_BY_REGION=(
        consts.EATS_COURIER_SCORING_STARTREK_SETTINGS_BY_REGION
    ),
)
@pytest.mark.translations()
@pytest.mark.parametrize(['error_flag'], ((False,), (True,)))
async def test_startrek(
        cron_context,
        mock_driver_wall_add,
        patch_create_startrack_ticket,
        error_flag,
):
    patch_create_startrack_ticket = patch_create_startrack_ticket(
        {}, raise_exception=error_flag,
    )

    mock_driver_wall_add(
        check_request_drivers=[
            {'driver': '1_1', 'title': 'title', 'text': 'text'},
        ],
    )

    punishment = punishments.StartrekPunishmentContext(
        name='startrek',
        settings={
            'min_score': 1.0,
            'reapplication_days': 1,
            'worst_percentage': 100,
            'punishment_type': 'startrek',
        },
        region_stats={},
        region_rules={},
    )
    couriers_ids = {1, 2, 3, 4, 5}
    couriers = [
        entities.Courier(
            model=conftest.create_courier_model(courier_id, region='region'),
            defects=[conftest.create_defect(courier_id, order_id=1)],
            scores_by_defect_type={entities.DefectType('new_defect'): 1.0},
        )
        for courier_id in couriers_ids
    ]
    await punishment.apply_punishments(
        cron_context,
        couriers=couriers,
        experiment_courier_ids=couriers_ids,
        active_couriers_by_region={},
    )
    async with cron_context.pg.master.acquire() as connection:
        rows = await connection.fetch(
            'SELECT is_sent FROM eats_courier_scoring.punishments',
        )
    assert all(row['is_sent'] is not error_flag for row in rows)
    assert len(patch_create_startrack_ticket.calls) == len(couriers)


@pytest.mark.parametrize(
    ('courier_count', 'batch_size'),
    (
        (0, None),
        (1, None),
        (10, None),
        (10, 500),
        (10, 5),
        (10000, None),
        (10000, 500),
        (10000, 1000),
    ),
)
async def test_create_db_punishments_batch(
        cron_context, courier_count, batch_size,
):
    if batch_size:
        cron_context.config.EATS_COURIER_SCORING_BATCHES[
            'send_punishment'
        ] = batch_size

    punishment = punishments.CommunicationPunishmentContext(
        name='communication',
        settings={
            'min_score': 0,
            'reapplication_days': 1,
            'worst_percentage': 100,
            'punishment_type': 'communication',
        },
        region_stats={},
        region_rules={},
    )
    couriers = [
        entities.Courier(
            model=conftest.create_courier_model(courier_id=courier_id),
            scores_by_defect_type={},
            defects=[],
        )
        for courier_id in range(courier_count)
    ]
    async with conftest.DiffCountPunishments(cron_context, courier_count):
        await punishment.apply_punishments(
            cron_context,
            couriers=couriers,
            experiment_courier_ids=set(range(courier_count)),
            active_couriers_by_region={},
        )
