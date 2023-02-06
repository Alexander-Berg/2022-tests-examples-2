# -*- coding: utf-8 -*-
import os
import pytest

from lib.clickhouse.table import Schema
import utils.common as common
import lib.exceptions as exceptions

distr_metadata_file_path = os.path.dirname(__file__) + '/test.table_distr.yaml'
distr_metadata = common.read_yaml(distr_metadata_file_path)

distr_nested_metadata_file_path = os.path.dirname(__file__) + '/test.table_distr_nested.yaml'
distr_nested_metadata = common.read_yaml(distr_nested_metadata_file_path)

easy_table_columns_clause = \
    """    "car_class" String,
    "city" Nullable(String),
    "date" Date,
    "sign" Int8"""

nested_table_columns_clause = \
    """    "car_class" String,
    "city" Nullable(String),
    "date" Date,
    "sign" Int8,
    "statuses" Nested("status" String, "date" DateTime, "value" Nullable(Float64))"""


class TestSchema(object):
    def test_empty(self):
        config = {}

        with pytest.raises(exceptions.ConfigError):
            Schema.from_config(config)

    def test_easy_example(self):
        config = distr_metadata

        schema = Schema.from_config(config)

        assert schema.get_column_names == ['car_class', 'city', 'date', 'sign']
        assert schema.table_columns_clause == easy_table_columns_clause

    def test_nested_table(self):
        config = distr_nested_metadata

        schema = Schema.from_config(config)

        assert schema.get_column_names == \
               ['car_class', 'city', 'date', 'sign', 'statuses.date', 'statuses.status', 'statuses.value']
        assert schema.table_columns_clause == nested_table_columns_clause
