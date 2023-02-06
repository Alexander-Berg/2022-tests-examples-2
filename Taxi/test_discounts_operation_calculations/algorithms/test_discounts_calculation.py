# pylint: disable=redefined-outer-name
from unittest import mock

import pytest

from discounts_operation_calculations.algorithms import discounts_calculation
from discounts_operation_calculations.internals.models import (
    calc_statistics_params as models,
)

DISCOUNTS = {10: 12, 20: 3, 30: 9, 40: 0, 50: 3}
ZERO_DISCOUNTS = {20: 0, 30: 0, 40: 0, 50: 0}
EQUAL_DISCOUNTS = {20: 6, 30: 6, 40: 6, 50: 6}


@pytest.fixture(scope='function')
def optimizer():
    def make_optimizer(seg_elasticities, fixed_segments=None):
        data_mock = mock.MagicMock()
        data_mock.get_segments = mock.MagicMock(
            return_value=list(seg_elasticities.keys()),
        )

        opt = discounts_calculation.DiscountsOptimizer(
            segments_stats_data=data_mock,
            budget=0,
            smooth_threshold=0,
            min_discount=0,
            fixed_discounts=[
                models.FixedDiscountInternal(
                    algorithm='1', segment=s, discount_value=3,
                )
                for s in fixed_segments or []
            ],
            segments_elasticities=seg_elasticities,
        )
        return opt

    yield make_optimizer


def test_discounts_above_limit():
    assert discounts_calculation.above_limit(DISCOUNTS, 3)
    assert discounts_calculation.above_limit(DISCOUNTS, 0)
    assert not discounts_calculation.above_limit(DISCOUNTS, 5)


def test_discounts_equal():
    assert discounts_calculation.equal(ZERO_DISCOUNTS, 0)
    assert not discounts_calculation.equal(ZERO_DISCOUNTS, 4)

    assert discounts_calculation.equal(EQUAL_DISCOUNTS, 6)
    assert not discounts_calculation.equal(EQUAL_DISCOUNTS, 0)
    assert not discounts_calculation.equal(EQUAL_DISCOUNTS, 9)

    assert not discounts_calculation.equal(DISCOUNTS, 3)
    assert not discounts_calculation.equal(DISCOUNTS, 0)


def test_build_segments_set(optimizer):
    seg_elasticities = {
        'seg_high': 1,
        'seg_low': 0,
        'seg1': 0.1,
        'seg2': 0.3,
        'seg3': 0.8,
    }
    opt = optimizer(seg_elasticities)
    # pylint: disable=protected-access
    sets = opt._build_segments_sets()

    assert sets == [
        ['seg_high'],
        ['seg_high', 'seg3'],
        ['seg_high', 'seg3', 'seg2'],
        ['seg_high', 'seg3', 'seg2', 'seg1'],
        ['seg_high', 'seg3', 'seg2', 'seg1', 'seg_low'],
    ]

    fixed_segments = ['seg1']
    opt = optimizer(seg_elasticities, fixed_segments)
    # pylint: disable=protected-access
    sets = opt._build_segments_sets()
    assert sets == [
        ['seg1'],
        ['seg1', 'seg_high'],
        ['seg1', 'seg_high', 'seg3'],
        ['seg1', 'seg_high', 'seg3', 'seg2'],
        ['seg1', 'seg_high', 'seg3', 'seg2', 'seg_low'],
    ]
