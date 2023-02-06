# -*- coding: utf-8 -*-
import pytest

import lib.clickhouse.column as clickhouse_column
import lib.exceptions as exceptions


class TestColumn(object):
    def test_main(self):
        column_config = {
            'type': 'Date',
            'sort_position': 0,
            'is_key': True
        }
        column = clickhouse_column.Column(name='date', config=column_config)
        assert column.name == 'date'
        assert column.type == 'Date'
        assert column.is_null is False
        assert column.create_string() == '"date" Date'

    def test_nullable(self):
        column_config = {
            'is_null': True,
            'type': 'String'
        }
        column = clickhouse_column.Column(name='city', config=column_config)
        assert column.create_string() == '"city" Nullable(String)'

    def test_array_type(self):
        column_config = {
            'type': 'Array(UInt8)'
        }
        assert clickhouse_column.Column(name='city', config=column_config)

    def test_null_values(self):
        column_config = {}
        with pytest.raises(exceptions.ConfigError):
            clickhouse_column.Column(name='city', config=column_config)

        column_config = {
            'is_null': True,
            'type': 'Error'
        }

        with pytest.raises(exceptions.ConfigError):
            clickhouse_column.Column(name=None, config=column_config)

        column_config = {
            'is_null': True,
            'type': 'String'
        }

        with pytest.raises(exceptions.ConfigError):
            clickhouse_column.Column(name='', config=column_config)

    def test_incorrect_types(self):
        column_config = {
            'is_null': True,
            'type': 'Error'
        }

        with pytest.raises(exceptions.ConfigError):
            clickhouse_column.Column(name='city', config=column_config)

        column_config['type'] = 'Array(Error)'
        with pytest.raises(exceptions.ConfigError):
            clickhouse_column.Column(name='city', config=column_config)

        column_config['type'] = 'Array(Unknown)'
        with pytest.raises(exceptions.ConfigError):
            clickhouse_column.Column(name='city', config=column_config)

    def test_nested_table_columns_create_string(self):
        column_config = {
            'type': 'Nested',
            'nested_table': {
                'status': {'type': 'String', 'is_null': 'True'},
                'value': {'type': 'Float64'}
            }
        }

        column = clickhouse_column.Column(name='table', config=column_config)
        assert column.create_string() == '"table" Nested("status" Nullable(String), "value" Float64)'

    def test_empty_nested(self):
        column_config = {
            'type': 'Nested'
        }

        with pytest.raises(exceptions.ConfigError):
            clickhouse_column.Column(name='table', config=column_config)
