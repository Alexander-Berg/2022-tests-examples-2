from argparse import Namespace
from typing import Dict, List, Any

import pytest

import numpy as np
from pyspark.sql import SparkSession
from pyspark.sql.dataframe import DataFrame
import dmp_suite.spark.client as spark_client

from dmp_suite.yt.task.etl.spark_transform import _SparkAccessor


def do_check(check, spark, expected_result, expected_report):
    check.spark = spark
    assert_df(check.collect_errors_df(), expected_result)
    result = check._check_result()
    assert result.description == expected_report.description
    assert result.errors_total == expected_report.errors_total
    assert result.errors_new == expected_report.errors_new


# FIXME: scope должен быть session, но не может быть пока таковым
#  а тесты его использующие должны быть unit тестами, а не slow
#  см TAXIDWH-8892, TAXIDWH-8677
@pytest.fixture(scope='function')
def local_spark_session():
    with spark_client.create_local_spark_session() as spark:
        yield spark


@pytest.fixture(scope='function')
def spark_session():
    """Пришлось создать так как local_spark_session не умел
    `local_spark_session.read.yt()`.

    Если в тестах можно предоставить dataframe без чтения YT, то используйте
    `local_spark_session`
    """
    with spark_client.create_spark_session(
            num_executors=1,
            cores_per_executor=1
    ) as spark:
        yield spark


TestData = List[Dict[str, Any]]


def order_data(data: Any):
    if isinstance(data, dict):
        return sorted((k, order_data(v)) for k, v in data.items())
    if isinstance(data, list) or isinstance(data, np.ndarray):
        return sorted(order_data(x) for x in data)
    if data is None:
        return 'NONE'
    else:
        return str(data)


def apply_spark_source_function(spark: SparkSession,
                                source: _SparkAccessor,
                                inputs: Dict[str, TestData],
                                args: Namespace = Namespace()
                                ):
    input_dfs = {
        name: spark.createDataFrame(data)
        for (name, data) in inputs.items()
    }

    # noinspection PyProtectedMember
    output_df: DataFrame = source._func(args, **input_dfs)
    actual_output = output_df.toPandas().to_dict(orient='records')
    return order_data(actual_output)


def assert_df(
        actual: DataFrame,
        expected: List[Dict],
        nan_to_none: bool = False,
):
    if actual.count() == 0:
        assert [] == expected
        return

    actual = actual.toPandas()
    if nan_to_none:
        actual = actual.replace({np.nan: None})
    assert actual.to_dict(orient='records') == expected
