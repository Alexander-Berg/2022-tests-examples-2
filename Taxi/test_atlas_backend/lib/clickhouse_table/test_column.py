import pytest

import atlas_backend.lib.clickhouse_table.column as clickhouse_column
import atlas_backend.lib.exceptions as exceptions


async def test_main():
    column_config = {'type': 'Date', 'sort_position': 0, 'is_key': True}
    column = clickhouse_column.Column(name='date', config=column_config)
    assert column.name == 'date'
    assert column.type == 'Date'
    assert column.is_null is False
    assert column.create_string() == '"date" Date'


async def test_nullable():
    column_config = {'is_null': True, 'type': 'String'}
    column = clickhouse_column.Column(name='city', config=column_config)
    assert column.create_string() == '"city" Nullable(String)'


async def test_array_type():
    column_config = {'type': 'Array(UInt8)'}
    assert clickhouse_column.Column(name='city', config=column_config)


async def test_null_values():
    column_config = {}
    with pytest.raises(exceptions.ConfigError):
        clickhouse_column.Column(name='city', config=column_config)

    column_config = {'is_null': True, 'type': 'Error'}

    with pytest.raises(exceptions.ConfigError):
        clickhouse_column.Column(name=None, config=column_config)

    column_config = {'is_null': True, 'type': 'String'}

    with pytest.raises(exceptions.ConfigError):
        clickhouse_column.Column(name='', config=column_config)


async def test_incorrect_types():
    column_config = {'is_null': True, 'type': 'Error'}

    with pytest.raises(exceptions.ConfigError):
        clickhouse_column.Column(name='city', config=column_config)

    column_config['type'] = 'Array(Error)'
    with pytest.raises(exceptions.ConfigError):
        clickhouse_column.Column(name='city', config=column_config)


async def test_nested_table_columns_create_string():
    column_config = {
        'type': 'Nested',
        'nested_table': {
            'status': {'type': 'String', 'is_null': 'True'},
            'value': {'type': 'Float64'},
        },
    }

    column = clickhouse_column.Column(name='table', config=column_config)
    assert (
        column.create_string()
        == '"table" Nested("status" Nullable(String), "value" Float64)'
    )


async def test_empty_nested():
    column_config = {'type': 'Nested'}

    with pytest.raises(exceptions.ConfigError):
        clickhouse_column.Column(name='table', config=column_config)
