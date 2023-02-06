from functools import reduce
from typing import Optional

import pytest
from pyspark.sql import SparkSession
from pyspark.sql.types import LongType
from pyspark.sql.types import StringType
from pyspark.sql.types import StructField
from pyspark.sql.types import StructType

from dmp_suite.spark.dataframe_utils import union_merging_schemas
# noinspection PyUnresolvedReferences
from test_dmp_suite.testing_utils.spark_testing_utils import local_spark_session

df1 = [
    dict(col1=1, col2='a', col3=None, col4='b'),
    dict(col1=2, col2='c', col3=3, col4='d')
]

df2 = [
    dict(col1=None, col2=None, col3=None, col4=None),
    dict(col1=4, col2='e', col3=5, col4='f')
]

df3 = [
    dict(col4='g', col2='h'),
    dict(col4='i', col2=None)
]

df4 = [
    dict(col3=6, col5='j'),
    dict(col3=None, col5='h')
]


@pytest.mark.parametrize(
    'inputs, expected_schema',
    [
        pytest.param(
            [],
            None,
        ),
        pytest.param(
            [df1],
            StructType([
                StructField('col1',LongType()),
                StructField('col2',StringType()),
                StructField('col3',LongType()),
                StructField('col4',StringType()),
            ]),
        ),
        pytest.param(
            [df1, df2],
            StructType([
                StructField('col1', LongType()),
                StructField('col2', StringType()),
                StructField('col3', LongType()),
                StructField('col4', StringType()),
            ]),
        ),
        pytest.param(
            [df1, df2, df3],
            StructType([
                StructField('col1', LongType()),
                StructField('col2', StringType()),
                StructField('col3', LongType()),
                StructField('col4', StringType()),
            ]),
        ),
        pytest.param(
            [df4, df3],
            StructType([
                StructField('col3', LongType()),
                StructField('col5', StringType()),
                StructField('col2', StringType()),
                StructField('col4', StringType()),
            ]),
        ),
    ]
)
@pytest.mark.slow
def test_union_merging_schemas(inputs, expected_schema, local_spark_session):
    spark: SparkSession = local_spark_session

    input_dfs = [spark.createDataFrame(data) for data in inputs]

    result_df = union_merging_schemas(*input_dfs)

    if expected_schema is None:
        assert result_df is None
        return

    assert result_df is not None

    expected_data = reduce(lambda x, y: x+y, inputs)
    expected_df = spark.createDataFrame(expected_data)

    assert result_df.schema == expected_schema
    assert result_df.collect() == expected_df.collect()
