import pytest

from discounts_operation_calculations.algorithms import (
    segment_stats_data as sd,
)
from discounts_operation_calculations.algorithms.katusha2 import blocks
from discounts_operation_calculations.algorithms.katusha2 import budget_metrics


DATA = """
    step_metric,cost_per_metric,step_budget,segment,discount,price_from
    4,0,0,sas,0,0
    1,5,3,sas,3,0
    5,7,2,sas,6,0

    2,0,0,sas,0,25
    9,8,9,sas,3,25
    1,4,1,sas,6,25

    0,0,0,seg,0,0
    3,15,13,seg,3,0
    7,17,12,seg,6,0

    11,0,0,seg,0,25
    9,18,19,seg,3,25
    1,14,11,seg,6,25
"""


def test_make_metrics(create_dataframe):
    dataframe = create_dataframe(DATA)
    builder = budget_metrics.MetricsBuilder(dataframe)
    blocks_mngr = blocks.BlocksManager(dataframe)

    indexes = [
        sd.Index(segment='sas', bucket_num=0, discount=0),
        sd.Index(segment='sas', bucket_num=0, discount=3),
        sd.Index(segment='sas', bucket_num=0, discount=6),
        sd.Index(segment='sas', bucket_num=25, discount=0),
        sd.Index(segment='sas', bucket_num=25, discount=3),
        sd.Index(segment='seg', bucket_num=25, discount=0),
        sd.Index(segment='seg', bucket_num=25, discount=3),
        sd.Index(segment='seg', bucket_num=25, discount=6),
    ]
    for i in indexes:
        builder.add_block(blocks_mngr.create_block(i))

    metrics = builder.make_metrics()

    assert metrics == budget_metrics.BudgetMetrics(
        budgets=[0, 3, 5, 5, 14, 14, 33, 44],
        metrics=[4, 5, 10, 12, 21, 32, 41, 42],
        avg_metric_costs=[
            pytest.approx(v)
            for v in [
                0,
                3 / 5,
                0.5,
                5 / 12,
                14 / 21,
                14 / 32,
                33 / 41,
                44 / 42,
            ]
        ],
        costs_per_metric=[0, 5, 7, 0, 8, 0, 18, 14],
    )


def test_make_discounts_mega_blocks(create_dataframe):
    dataframe = create_dataframe(DATA)
    builder = budget_metrics.MetricsBuilder(dataframe)
    blocks_mngr = blocks.BlocksManager(dataframe)

    blocks_to_add = [
        blocks_mngr.create_mega_block(
            [
                # cpm = (0 + 3 + 2 + 0 + 9) / (4 + 1 + 5 + 2 + 9) = 0.666
                sd.Index(segment='sas', bucket_num=0, discount=0),
                sd.Index(segment='sas', bucket_num=0, discount=3),
                sd.Index(segment='sas', bucket_num=0, discount=6),
                sd.Index(segment='sas', bucket_num=25, discount=0),
                sd.Index(segment='sas', bucket_num=25, discount=3),
            ],
        ),
        blocks_mngr.create_block(
            sd.Index(segment='sas', bucket_num=25, discount=6),
        ),
        blocks_mngr.create_block(
            sd.Index(segment='seg', bucket_num=25, discount=0),
        ),
    ]
    for block in blocks_to_add:
        builder.add_block(block)

    discounts = builder.make_metrics()
    assert discounts == budget_metrics.BudgetMetrics(
        budgets=[14, 15, 15],
        metrics=[21, 22, 33],
        avg_metric_costs=[
            pytest.approx(v) for v in [14 / 21, 15 / 22, 15 / 33]
        ],
        costs_per_metric=[14 / 21, 4, 0],
    )


def test_empty_metric(create_dataframe):
    dataframe = create_dataframe(DATA)
    builder = budget_metrics.MetricsBuilder(dataframe)
    result = builder.make_metrics()

    assert result == budget_metrics.BudgetMetrics(
        budgets=[], metrics=[], avg_metric_costs=[], costs_per_metric=[],
    )
