import pytest

from eats_courier_scoring.common import entities
from eats_courier_scoring.common import experiments
from eats_courier_scoring.common import scoring
from test_eats_courier_scoring import conftest


ABSOLUTE = {
    entities.DefectType('damaged_order'): [
        experiments.DefectScore(
            score=10,
            thresholds_absolute=(10, float('inf')),
            thresholds_share=(0, 1),
        ),
        experiments.DefectScore(
            score=1,
            thresholds_absolute=(5, float('inf')),
            thresholds_share=(0, 1),
        ),
        experiments.DefectScore(
            score=0,
            thresholds_absolute=(0, float('inf')),
            thresholds_share=(0, 1),
        ),
    ],
}

SHARE = {
    entities.DefectType('damaged_order'): [
        experiments.DefectScore(
            score=10,
            thresholds_absolute=(0, float('inf')),
            thresholds_share=(0.5, 1),
        ),
        experiments.DefectScore(
            score=1,
            thresholds_absolute=(0, float('inf')),
            thresholds_share=(0.25, 1),
        ),
        experiments.DefectScore(
            score=0,
            thresholds_absolute=(0, float('inf')),
            thresholds_share=(0, 1),
        ),
    ],
}


@pytest.mark.parametrize(
    ('config', 'count_defects', 'n_orders_last_period', 'score'),
    [
        (ABSOLUTE, 100, 10, 100),
        (ABSOLUTE, 10, 10, 10),
        (ABSOLUTE, 5, 10, 0.5),
        (ABSOLUTE, 3, 10, 0),
        (SHARE, 100, 10, 100),
        (SHARE, 5, 10, 5),
        (SHARE, 3, 10, 0.3),
        (SHARE, 2, 10, 0),
    ],
)
async def test_scoring(
        cron_context, config, count_defects, n_orders_last_period, score,
):
    couriers = [
        entities.Courier(
            model=conftest.create_courier_model(
                1, n_orders_last_period=n_orders_last_period,
            ),
            defects=[
                conftest.create_defect(1, order_id=i)
                for i in range(count_defects)
            ],
        ),
    ]

    couriers_scoring_configs = {
        courier.model.courier_id: experiments.DefectsScoringConfigResult(
            enabled=True, punishment_names=set(), defect_scores=config,
        )
        for courier in couriers
    }

    scoring.calculate_and_update(couriers, couriers_scoring_configs)
    assert couriers[0].score == score
