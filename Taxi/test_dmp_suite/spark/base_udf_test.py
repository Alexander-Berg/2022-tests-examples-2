import pytest

from dmp_suite.spark.base_udf import DatetimeUDF, StringUDF
from .utils import assert_udf


@pytest.mark.parametrize('udf', [DatetimeUDF, StringUDF])
def test_datetime_udf(udf):
    assert_udf(udf)
