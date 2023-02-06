import pytest

from atlas_etl.lib import exceptions
from atlas_etl.lib.clickhouse_table import metadata_utils as meta_lib


SIMPLE_TABLE_COLUMNS_CLAUSE = """    "car_class" String,
    "city" Nullable(String),
    "date" Date,
    "sign" Int8"""

NESTED_TABLE_COLUMNS_CLAUSE = """    "car_class" String,
    "city" Nullable(String),
    "date" Date,
    "sign" Int8,
    "statuses" Nested("status" String, "date" DateTime, "value" Nullable(Float64))"""  # noqa: E501


async def test_empty():
    config = {}

    with pytest.raises(exceptions.ConfigError):
        meta_lib.Schema.from_config(config)


@pytest.mark.parametrize('yaml_name', ['table_distr.yaml'])
async def test_easy_example(clickhouse_table_config, yaml_name):
    schema = meta_lib.Schema.from_config(clickhouse_table_config)

    assert schema.get_column_names == ['car_class', 'city', 'date', 'sign']
    assert schema.table_columns_clause == SIMPLE_TABLE_COLUMNS_CLAUSE


@pytest.mark.parametrize('yaml_name', ['table_distr_nested.yaml'])
async def test_nested_table(clickhouse_table_config, yaml_name):
    schema = meta_lib.Schema.from_config(clickhouse_table_config)

    assert schema.get_column_names == [
        'car_class',
        'city',
        'date',
        'sign',
        'statuses.date',
        'statuses.status',
        'statuses.value',
    ]
    assert schema.table_columns_clause == NESTED_TABLE_COLUMNS_CLAUSE
