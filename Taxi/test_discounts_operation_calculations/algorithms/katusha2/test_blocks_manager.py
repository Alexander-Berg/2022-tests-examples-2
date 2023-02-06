# pylint: disable=redefined-outer-name
import pytest

from discounts_operation_calculations.algorithms import (
    segment_stats_data as sd,
)
from discounts_operation_calculations.algorithms.katusha2 import blocks


DATA = """
    cost_per_metric,step_budget,step_metric,segment,discount,price_from
    0,0,4,sas,0,0
    5,3,0.6,sas,3,0
    7,2,0.28,sas,6,0

    0,0,0,sas,0,25
    8,9,1.125,sas,3,25
    4,1,0.25,sas,6,25

    0,0,0,seg,0,0
    15,13,0.86,seg,3,0
    17,12,0.705,seg,6,0

    0,0,0,seg,0,25
    18,19,1.05,seg,3,25
    14,11,0.785,seg,6,25
"""


@pytest.fixture(scope='function')
def blocks_manager(create_dataframe):
    yield blocks.BlocksManager(create_dataframe(DATA))


def test_create_block(blocks_manager):
    idx = sd.Index(segment='sas', bucket_num=0, discount=3)
    block = blocks_manager.create_block(idx)

    assert isinstance(block, blocks.JustBlock)
    assert block.cost_per_metric == 5

    idx = sd.Index(segment='seg', bucket_num=25, discount=6)
    block = blocks_manager.create_block(idx)

    assert isinstance(block, blocks.JustBlock)
    assert block.cost_per_metric == 14


def test_create_mega_block(blocks_manager):
    indexes = [
        sd.Index(segment='sas', bucket_num=0, discount=3),
        sd.Index(segment='sas', bucket_num=25, discount=3),
        sd.Index(segment='sas', bucket_num=25, discount=6),
    ]
    block = blocks_manager.create_mega_block(indexes)

    assert isinstance(block, blocks.MegaBlock)
    assert block.cost_per_metric == pytest.approx(
        (3 + 9 + 1) / (0.6 + 0.25 + 1.125),
    )


def test_budget(blocks_manager):
    idx = sd.Index(segment='sas', bucket_num=0, discount=3)
    block = blocks_manager.create_block(idx)
    assert blocks_manager.budget(block) == 3

    indexes = [
        sd.Index(segment='sas', bucket_num=0, discount=3),
        sd.Index(segment='sas', bucket_num=0, discount=6),
        sd.Index(segment='sas', bucket_num=25, discount=3),
        sd.Index(segment='sas', bucket_num=25, discount=6),
    ]

    block = blocks_manager.create_mega_block(indexes)
    assert blocks_manager.budget(block) == 15


def test_next_blocks(blocks_manager):
    idx = sd.Index(segment='sas', bucket_num=0, discount=3)
    block = blocks_manager.create_block(idx)

    next_blocks = blocks_manager.next_blocks(block)
    assert len(next_blocks) == 1

    next_block_index = next_blocks[0].index
    assert next_block_index == sd.Index(
        segment='sas', bucket_num=0, discount=6,
    )
    next_blocks = blocks_manager.next_blocks(next_blocks[0])
    assert next_blocks == []

    indexes = [
        sd.Index(segment='seg', bucket_num=0, discount=0),
        sd.Index(segment='seg', bucket_num=0, discount=3),
        sd.Index(segment='seg', bucket_num=25, discount=0),
        sd.Index(segment='seg', bucket_num=25, discount=3),
    ]

    block = blocks_manager.create_mega_block(indexes)
    next_blocks_indexes = {b.index for b in blocks_manager.next_blocks(block)}
    assert next_blocks_indexes == {
        sd.Index(segment='seg', bucket_num=0, discount=6),
        sd.Index(segment='seg', bucket_num=25, discount=6),
    }
