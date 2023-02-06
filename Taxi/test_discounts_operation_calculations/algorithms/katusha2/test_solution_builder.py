from discounts_operation_calculations.algorithms import (
    segment_stats_data as sd,
)
from discounts_operation_calculations.algorithms.katusha2 import blocks
from discounts_operation_calculations.algorithms.katusha2 import solution


DATA = """
    cost_per_metric,step_budget,step_metric,segment,discount,price_from
    0,0,1,sas,0,0
    5,3,2,sas,3,0
    7,2,3,sas,6,0

    0,0,0,sas,0,25
    8,9,2,sas,3,25
    4,1,4,sas,6,25

    0,0,6,sas,0,50
    10,5,7,sas,3,50
    14,4,9,sas,6,50

    0,0,1,seg,0,0
    15,13,2,seg,3,0
    17,12,7,seg,6,0

    0,0,0,seg,0,25
    18,19,4,seg,3,25
    14,11,3,seg,6,25
"""


def test_make_discounts(create_dataframe):
    dataframe = create_dataframe(DATA)
    builder = solution.SolutionBuilder(dataframe, 25)
    blocks_mngr = blocks.BlocksManager(dataframe)

    indexes = [
        sd.Index(segment='sas', bucket_num=0, discount=0),
        sd.Index(segment='sas', bucket_num=0, discount=3),
        sd.Index(segment='sas', bucket_num=0, discount=6),
        sd.Index(segment='sas', bucket_num=25, discount=0),
        sd.Index(segment='sas', bucket_num=25, discount=3),
        sd.Index(segment='sas', bucket_num=50, discount=0),
        sd.Index(segment='seg', bucket_num=25, discount=0),
        sd.Index(segment='seg', bucket_num=25, discount=3),
        sd.Index(segment='seg', bucket_num=25, discount=6),
    ]
    for i in indexes:
        builder.add_block(blocks_mngr.create_block(i))

    # pylint: disable=protected-access
    discounts = builder._make_discounts()

    assert discounts == [
        solution.SegmentDiscounts(
            segment='sas', bucket_discount={0: 6, 25: 3, 50: 0},
        ),
        solution.SegmentDiscounts(
            segment='seg', bucket_discount={25: 6, 50: 0},
        ),
    ]


def test_make_discounts_mega_blocks(create_dataframe):
    dataframe = create_dataframe(DATA)
    builder = solution.SolutionBuilder(dataframe, 25)
    blocks_mngr = blocks.BlocksManager(dataframe)

    blocks_to_add = [
        blocks_mngr.create_mega_block(
            [
                sd.Index(segment='sas', bucket_num=0, discount=0),
                sd.Index(segment='sas', bucket_num=0, discount=3),
                sd.Index(segment='sas', bucket_num=0, discount=6),
                sd.Index(segment='sas', bucket_num=25, discount=0),
                sd.Index(segment='sas', bucket_num=25, discount=3),
                sd.Index(segment='sas', bucket_num=50, discount=0),
            ],
        ),
        blocks_mngr.create_block(
            sd.Index(segment='sas', bucket_num=25, discount=6),
        ),
        blocks_mngr.create_block(
            sd.Index(segment='sas', bucket_num=50, discount=3),
        ),
    ]
    for block in blocks_to_add:
        builder.add_block(block)

    # pylint: disable=protected-access
    discounts = builder._make_discounts()

    assert discounts == [
        solution.SegmentDiscounts(
            segment='sas', bucket_discount={0: 6, 25: 6, 50: 3, 75: 0},
        ),
    ]


def test_empty_solution(create_dataframe):
    dataframe = create_dataframe(DATA)
    builder = solution.SolutionBuilder(dataframe, 25)
    result = builder.make_solution(1000)

    assert result == solution.Solution(
        spent_budget=1000, discounts=[], segments_meta=[],
    )
