from __future__ import absolute_import

import pytest
import os
import mock
import decimal
import datetime
import copy

import utils.common as common
import lib.exceptions as exceptions
import etl.transform_methods.common
from etl.data_transformers import DataTransformer, parse_calculated_fields_config

ch_table_config_file_path = os.path.join(os.path.dirname(__file__), './metadata/test.table.yaml')
ch_table_config = common.read_yaml(ch_table_config_file_path)

transform_config_file_path = os.path.join(os.path.dirname(__file__), './metadata/test_transformer.yaml')
transform_config = common.read_yaml(transform_config_file_path)

magick_datetime = datetime.datetime(2011, 2, 28, 23, 59, 59)


def patch_get_current_datetime():
    return lambda: magick_datetime


class TestConfigParser(object):
    def test_empty_config(self):
        config = {}
        parsed_config = parse_calculated_fields_config(config)
        assert parsed_config == {}

    def test_parameters(self):
        parsed_config = parse_calculated_fields_config(transform_config)

        parameters = parsed_config['orders_quadkey']._parameters
        expected_param_names = iter(['lat', 'lon', 'zoom'])
        expected_param_values = iter([None, None, 18])
        expected_column_names = iter(['latitude', 'longitude', None])
        for param in sorted(parameters, key=lambda x: x.name):
            assert param.name == next(expected_param_names)
            assert param.value == next(expected_param_values)
            assert param.column_name == next(expected_column_names)

    def test_function_empty(self):
        config = copy.deepcopy(transform_config)
        del config['calculated_fields']['orders_quadkey']['function']

        with pytest.raises(exceptions.ConfigError) as exinfo:
            parse_calculated_fields_config(config)

        assert "not declared" in str(exinfo.value)

    def test_not_existed_parameter(self):
        config = copy.deepcopy(transform_config)
        config['calculated_fields']['orders_quadkey']['parameters']['qwe'] = {'value': 42}

        with pytest.raises(exceptions.ConfigError) as exinfo:
            parse_calculated_fields_config(config)

        assert "isn't acceptable to function" in str(exinfo.value)
        assert "qwe" in str(exinfo.value)

    def test_wrong_parameter(self):
        config = copy.deepcopy(transform_config)
        del config['calculated_fields']['orders_quadkey']['parameters']['lat']
        config['calculated_fields']['orders_quadkey']['parameters']['lat'] = {'qwe': 123}

        with pytest.raises(exceptions.ConfigError) as exinfo:
            parse_calculated_fields_config(config)

        assert "'column_name' and 'value' cannot both be empty!" in str(exinfo.value)

    def test_real_config(self):
        parsed_config = parse_calculated_fields_config(transform_config)
        expected_field_names = iter(['created_at', 'latitude', 'longitude', 'orders_quadkey',
                                     'statuses.date', 'statuses.status', 'statuses.value'])
        expected_column_names = iter(['created_at', 'latitude', 'longitude', 'orders_quadkey',
                                      'statuses.date', 'statuses.status', 'statuses.value'])
        expected_method_names = iter(['get_current_datetime', 'to_float_converter',
                                      'to_float_converter', 'latlon2quadkeychecknone',
                                      'str_to_array', 'str_to_array', 'str_to_array'])
        for field_name, field_info in sorted(parsed_config.items()):
            assert field_info.destination_column_name
            assert field_name == next(expected_field_names)
            assert field_info.destination_column_name == next(expected_column_names)
            assert field_info._method.__name__ == next(expected_method_names)
            assert field_info._method.__module__ == 'etl.transform_methods.common'


class TestCalculatedField(object):
    def test_quadkey_method(self):
        calculated_fields = parse_calculated_fields_config(transform_config)
        orders_quadkey_field = calculated_fields['orders_quadkey']

        row = {'latitude': 55.123, 'longitude': 55.234}
        assert orders_quadkey_field.run(row) == '121201130100213300'

        row_with_none = {'latitude': 55.123, 'longitude': None}
        assert orders_quadkey_field.run(row_with_none) is None

    def test_float_converter(self):
        calculated_fields = parse_calculated_fields_config(transform_config)
        latitude_field = calculated_fields['latitude']

        row = {'latitude': decimal.Decimal('55.123')}
        assert latitude_field.run(row) == 55.123
        assert isinstance(latitude_field.run(row), float)

    @mock.patch.object(etl.transform_methods.common, 'get_current_datetime',
                       new_callable=patch_get_current_datetime)
    def test_get_current_datetime(self, a):
        calculated_fields = parse_calculated_fields_config(transform_config)
        created_at_field = calculated_fields['created_at']

        row = {}

        assert created_at_field.run(row) == magick_datetime

    def test_default_value(self):
        config = copy.deepcopy(transform_config)
        config['calculated_fields']['orders_quadkey']['parameters']['lat'].update({'value': 10})
        calculated_fields = parse_calculated_fields_config(config)
        orders_quadkey_field = calculated_fields['orders_quadkey']

        rows = [{'latitude': None, 'longitude': 55.234},
                {'latitude': 0, 'longitude': 55.234},
                {'latitude': 50, 'longitude': 55.234}]

        expected_results = iter(['123221112320033102', '301001110100011100', '121203330100033322'])
        for row in rows:
            assert orders_quadkey_field.run(row) == next(expected_results)


class TestDataTransformer(object):
    def test_empty(self):
        data_transformer = DataTransformer(transform_config)
        rows = [{}, {}]
        with pytest.raises(KeyError):
            list(data_transformer.transform_data(rows))

    @mock.patch.object(etl.transform_methods.common, 'get_current_datetime',
                       new_callable=patch_get_current_datetime)
    def test_all(self, a):
        data_transformer = DataTransformer(transform_config)
        rows = [{
                 'qwe': 'qwe',
                 'time': magick_datetime + datetime.timedelta(seconds=1),
                 'orders_id': 42,
                 'latitude': decimal.Decimal('55.123'),
                 'longitude': decimal.Decimal('55.234'),
                 'cars_class': 'UltraMegaBusiness',
                 'statuses.date': '2020-02-10 00:00:00#2020-02-10 01:00:00',
                 'statuses.status': 'good,bad',
                 'statuses.value': 'Null;12.234'
                },
                {
                 'time': '12:00:00',
                 'orders_id': 43,
                 'latitude': '55.123',
                 'longitude': '55.234',
                 'cars_class': 'Econom',
                 'statuses.date': '2020-02-11 01:00:00#0000-00-00 00:00:00',
                 'statuses.status': ',good',
                 'statuses.value': '12;03.2'
                },
                {
                 'time': None,
                 'orders_id': None,
                 'latitude': None,
                 'longitude': None,
                 'cars_class': None,
                 'statuses.date': '0000-00-00 00:00:00',
                 'statuses.status': '',
                 'statuses.value': 'Null'
                }]
        expected_rows = [{'qwe': 'qwe',
                          'time': magick_datetime + datetime.timedelta(seconds=1),
                          'orders_id': 42,
                          'latitude': 55.123,
                          'longitude': 55.234,
                          'cars_class': 'UltraMegaBusiness',
                          'orders_quadkey': '121201130100213300',
                          'created_at': magick_datetime,
                          'statuses.date': [
                              datetime.datetime(2020, 2, 9, 21, 0, tzinfo=datetime.timezone.utc),
                              datetime.datetime(2020, 2, 9, 22, 0, tzinfo=datetime.timezone.utc)],
                          'statuses.status': ['good', 'bad'],
                          'statuses.value': [None, 12.234]
                          },
                         {'time': '12:00:00',
                          'orders_id': 43,
                          'latitude': 55.123,
                          'longitude': 55.234,
                          'cars_class': 'Econom',
                          'orders_quadkey': '121201130100213300',
                          'created_at': magick_datetime,
                          'statuses.date': [
                              datetime.datetime(2020, 2, 10, 22, 0, tzinfo=datetime.timezone.utc),
                              None],
                          'statuses.status': [None, 'good'],
                          'statuses.value': [12.0, 3.2]
                          },
                         {'time': None,
                          'orders_id': None,
                          'latitude': None,
                          'longitude': None,
                          'cars_class': None,
                          'orders_quadkey': None,
                          'created_at': magick_datetime,
                          'statuses.date': [None],
                          'statuses.status': [None],
                          'statuses.value': [None]
                          }]
        transformed_rows = list(data_transformer.transform_data(rows))

        assert transformed_rows == expected_rows
