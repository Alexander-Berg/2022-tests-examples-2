import pytest

from taxi_antifraud.amayak import counters
from taxi_antifraud.generated.service.swagger.models import api as models

ThresholdRange = models.ThresholdRange


@pytest.mark.parametrize(
    'threshold,counters_sum,expected_result',
    [(1, 1, True), (1, 2, False), (2, 1, False)],
)
def test_int(threshold, counters_sum, expected_result):
    assert (
        counters.counters_sum_reach_threshold(threshold, counters_sum)
        == expected_result
    )


@pytest.mark.parametrize(
    'threshold,counters_sum,expected_result',
    [
        (ThresholdRange(begin=1, end=1), 1, True),
        (ThresholdRange(begin=1, end=2), 1, True),
        (ThresholdRange(begin=1, end=2), 2, True),
        (ThresholdRange(begin=1, end=2), 3, False),
        (ThresholdRange(begin=2, end=3), 1, False),
        (ThresholdRange(begin=2, end=3), 1, False),
    ],
)
def test_threshold(threshold, counters_sum, expected_result):
    assert (
        counters.counters_sum_reach_threshold(threshold, counters_sum)
        == expected_result
    )


@pytest.mark.parametrize(
    'threshold,counters_sum', [(1.0, 1), ('1', 1), ([], 1), ({}, 1)],
)
def test_something_else(threshold, counters_sum):
    with pytest.raises(
            Exception,
            message='level.threshold must be integer or models.ThresholdRange',
    ):
        counters.counters_sum_reach_threshold(threshold, counters_sum)
