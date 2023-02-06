import typing as tp

import pytest

from discounts_operation_calculations.algorithms import (
    segment_stats_data as sd,
)
from discounts_operation_calculations.algorithms.katusha2 import blocks
from discounts_operation_calculations.algorithms.katusha2 import katusha2


class TestBuildInitialBlocks:
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

    @pytest.mark.parametrize(
        'min_discount, expected_indexes',
        [
            (
                0,
                {
                    sd.Index(segment='sas', bucket_num=0, discount=0),
                    sd.Index(segment='sas', bucket_num=25, discount=0),
                    sd.Index(segment='seg', bucket_num=0, discount=0),
                    sd.Index(segment='seg', bucket_num=25, discount=0),
                },
            ),
            (
                3,
                {
                    sd.Index(segment='sas', bucket_num=0, discount=0),
                    sd.Index(segment='sas', bucket_num=0, discount=3),
                    sd.Index(segment='sas', bucket_num=25, discount=0),
                    sd.Index(segment='sas', bucket_num=25, discount=3),
                    sd.Index(segment='seg', bucket_num=0, discount=0),
                    sd.Index(segment='seg', bucket_num=0, discount=3),
                    sd.Index(segment='seg', bucket_num=25, discount=0),
                    sd.Index(segment='seg', bucket_num=25, discount=3),
                },
            ),
        ],
    )
    def test_build_init_blocks_min_disc(
            self, create_dataframe, min_discount, expected_indexes,
    ):
        katya = katusha2.Katusha(create_dataframe(self.DATA))

        # pylint: disable=protected-access
        init_blocks = katya._build_initial_blocks(min_discount)

        assert all(isinstance(b, blocks.MegaBlock) for b in init_blocks)
        assert len(init_blocks) == 2

        simple_blocks_idx = {
            b.index
            for ib in init_blocks
            for b in blocks.BlocksManager.breakdown(ib)
        }

        assert simple_blocks_idx == expected_indexes

    def test_build_initial_blocks(self, create_dataframe):
        katya = katusha2.Katusha(create_dataframe(self.DATA))

        # pylint: disable=protected-access
        init_blocks = katya._build_initial_blocks()

        assert all(isinstance(b, blocks.JustBlock) for b in init_blocks)
        assert len(init_blocks) == 4

        init_blocks_idx = {
            tp.cast(blocks.JustBlock, ib).index for ib in init_blocks
        }

        assert init_blocks_idx == {
            sd.Index(segment='sas', bucket_num=0, discount=0),
            sd.Index(segment='sas', bucket_num=25, discount=0),
            sd.Index(segment='seg', bucket_num=0, discount=0),
            sd.Index(segment='seg', bucket_num=25, discount=0),
        }


class TestIterBlocks:
    DATA = """
        cost_per_metric,step_budget,step_metric,segment,discount,price_from
        5,3,0.6,sas,3,0
        17,2,0.117,sas,6,0

        8,9,1.125,sas,3,25
        4,1,0.25,sas,6,25

        3,13,4.333,seg,3,0
        13,12,0.923,seg,6,0

        11,19,1.72,seg,3,25
        1,11,11.0,seg,6,25
    """

    def test_iter_blocks(self, create_dataframe):
        katya = katusha2.Katusha(create_dataframe(self.DATA))
        # pylint: disable=protected-access
        blocks_seq = list(katya._iter_optimal_blocks())
        assert all(isinstance(b, blocks.JustBlock) for b in blocks_seq)

        # must be sorted by cost_per_metric descending
        # and smaller discounts first
        index_seq = [tp.cast(blocks.JustBlock, b).index for b in blocks_seq]
        assert index_seq == [
            sd.Index(segment='seg', bucket_num=0, discount=3),
            sd.Index(segment='sas', bucket_num=0, discount=3),
            sd.Index(segment='sas', bucket_num=25, discount=3),
            sd.Index(segment='sas', bucket_num=25, discount=6),
            sd.Index(segment='seg', bucket_num=25, discount=3),
            sd.Index(segment='seg', bucket_num=25, discount=6),
            sd.Index(segment='seg', bucket_num=0, discount=6),
            sd.Index(segment='sas', bucket_num=0, discount=6),
        ]

    def test_iter_blocks_min_disc(self, create_dataframe):
        katya = katusha2.Katusha(create_dataframe(self.DATA))
        # pylint: disable=protected-access
        blocks_seq = list(katya._iter_optimal_blocks(min_discount=3))

        index_seq = [
            tp.cast(blocks.JustBlock, block).index
            if isinstance(block, blocks.JustBlock)
            else {b.index for b in tp.cast(blocks.MegaBlock, block).blocks}
            for block in blocks_seq
        ]

        assert index_seq == [
            # seg have smaller compound cost_per_metric
            {
                # cpm = (13 + 19) / (4.333 + 1.72) = 5.286
                sd.Index(segment='seg', bucket_num=0, discount=3),
                sd.Index(segment='seg', bucket_num=25, discount=3),
            },
            sd.Index(segment='seg', bucket_num=25, discount=6),  # cpm = 1
            {
                # cpm = (3 + 9) / (0.6 + 1.125) = 6.956
                sd.Index(segment='sas', bucket_num=0, discount=3),
                sd.Index(segment='sas', bucket_num=25, discount=3),
            },
            sd.Index(segment='sas', bucket_num=25, discount=6),  # cpm = 0.25
            sd.Index(segment='seg', bucket_num=0, discount=6),  # cpm = 13
            sd.Index(segment='sas', bucket_num=0, discount=6),  # cpm = 17
        ]
