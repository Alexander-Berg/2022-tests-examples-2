import pytest
from pyspark.sql import SparkSession

from dmp_suite.personal.yt import pd_types, spark_transform, tables as pd_tables

from test_dmp_suite.testing_utils.spark_testing_utils import (
    assert_df,
    local_spark_session as spark,
)
from . import tables


@pytest.mark.slow
def test_enrich_with_mapping(spark: SparkSession):
    data = [dict(a=1, pd=1), dict(a=2, pd=2)]
    mapping = [dict(id=1, val=2), dict(id=2, val=4)]
    actual = spark_transform.enrich_with_mapping(
        df=spark.createDataFrame(data),
        join_key_field='pd',
        value_field='pd_id',
        mapping_df=spark.createDataFrame(mapping),
        mapping_join_key_field='id',
        mapping_value_field='val',
    )
    assert_df(actual, [dict(a=1, pd=1, pd_id=2), dict(a=2, pd=2, pd_id=4)])


@pytest.mark.slow
def test_enrich_with_mapping_raises_on_not_mapped(spark: SparkSession):
    data = [dict(a=1, pd=1), dict(a=2, pd=2)]
    mapping = [dict(id=1, val=2)]
    with pytest.raises(spark_transform.SparkPersonalTransformError):
        spark_transform.enrich_with_mapping(
            df=spark.createDataFrame(data),
            join_key_field='pd',
            value_field='pd_id',
            mapping_df=spark.createDataFrame(mapping),
            mapping_join_key_field='id',
            mapping_value_field='val',
        )


@pytest.mark.slow
def test_enrich_with_mapping_not_raises_on_not_mapped(spark: SparkSession):
    data = [dict(a=1, pd=1), dict(a=2, pd=2)]
    mapping = [dict(id=1, val=2)]
    actual = spark_transform.enrich_with_mapping(
        df=spark.createDataFrame(data),
        join_key_field='pd',
        value_field='pd_id',
        mapping_df=spark.createDataFrame(mapping),
        mapping_join_key_field='id',
        mapping_value_field='val',
        raise_on_not_found_mapping=False,
    )
    assert_df(
        actual,
        [dict(a=1, pd=1, pd_id=2), dict(a=2, pd=2, pd_id=None)],
        nan_to_none=True,
    )


@pytest.mark.slow
def test_find_without_mapping(spark: SparkSession):
    data = [dict(a=1, pd=1), dict(a=2, pd=2)]
    mapping = [dict(id=1, val=2)]
    actual = spark_transform.find_without_mapping(
        df=spark.createDataFrame(data),
        join_key_field='pd',
        mapping_df=spark.createDataFrame(mapping),
        mapping_join_key_field='id',
    )

    # everything found
    assert_df(actual, [dict(pd=2)])
    mapping = [dict(id=1, val=2), dict(id=2, val=4)]
    actual = spark_transform.find_without_mapping(
        df=spark.createDataFrame(data),
        join_key_field='pd',
        mapping_df=spark.createDataFrame(mapping),
        mapping_join_key_field='id',
    )
    assert_df(actual, [])


def test_fill_pd_source_configuration():
    pd_type = pd_types.PdType(value_field='val', table=pd_tables.PersonalTable)
    source = spark_transform.FillPdSource(
        table=tables.PdTable
    ).add_pd(
        pd_id_field='phone_pd_id',
        pd_field='phone',
        pd_type=pd_type,
    ).add_pd_id(
        pd_field='identification',
        pd_id_field='identification_pd_id',
        pd_type=pd_type,
    )

    assert len(source.commands) == 2

    commands = iter(source.commands)
    cmd = next(commands)
    assert cmd.func == spark_transform.add_pd
    assert cmd.params['pd_id_field'] == 'phone_pd_id'
    assert cmd.params['pd_field'] == 'phone'
    assert cmd.params['pd_type'] == pd_type

    cmd = next(commands)
    assert cmd.func == spark_transform.add_pd_id
    assert cmd.params['pd_field'] == 'identification'
    assert cmd.params['pd_id_field'] == 'identification_pd_id'
    assert cmd.params['pd_type'] == pd_type
