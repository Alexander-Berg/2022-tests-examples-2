from passport.backend.tools.metrics.aggregates import should_sort_data
import pytest


@pytest.mark.parametrize(
    "agg_f, bool_expected",
    [
        ('sum', False),
        ('min', False),
        ('max', False),
        ('avg', False),
        ('median', True),
        ('p_50', True),
        ('p_90', True),
        ('p_95', True),
        ('p_98', True),
        ('p_99', True),
        ('non_negative_derivative', False),
],
)
def test_should_sort_data(agg_f, bool_expected):
    assert should_sort_data([agg_f]) == bool_expected
