from __future__ import absolute_import

import pytest
import os
import copy

import etl.helpers as helpers
import lib.exceptions as exceptions
import utils.common as common


ch_table_config_file_path = os.path.join(os.path.dirname(__file__), './metadata/test.table.yaml')
ch_table_config = common.read_yaml(ch_table_config_file_path)

transform_config_file_path = os.path.join(os.path.dirname(__file__), './metadata/test_transformer.yaml')
transform_config = common.read_yaml(transform_config_file_path)


class TestCheckConfigCompatible(object):
    def test_empty(self):
        with pytest.raises(exceptions.ConfigError):
            helpers.check_config_compatible({}, {})
        with pytest.raises(exceptions.ConfigError):
            helpers.check_config_compatible({}, [{}])
        with pytest.raises(exceptions.ConfigError):
            helpers.check_config_compatible({}, [{}, {}])

    def test_with_one_empty(self):
        with pytest.raises(exceptions.ConfigError):
            helpers.check_config_compatible(transform_config, {})
        with pytest.raises(exceptions.ConfigError):
            helpers.check_config_compatible(transform_config, [{}])
        with pytest.raises(exceptions.ConfigError):
            helpers.check_config_compatible({}, ch_table_config)

    def test_equal(self):
        helpers.check_config_compatible(transform_config, ch_table_config)
        helpers.check_config_compatible(transform_config, [ch_table_config, ch_table_config])

    def test_unequal_less_table_config(self):
        changed_ch_table_config = copy.deepcopy(ch_table_config)
        del changed_ch_table_config['columns']['time']
        with pytest.raises(exceptions.ConfigError):
            helpers.check_config_compatible(transform_config, changed_ch_table_config)

    def test_unequal_less_transform_config(self):
        changed_transform_config = copy.deepcopy(transform_config)
        del changed_transform_config['table_names']['metadata']

        with pytest.raises(exceptions.ConfigError):
            helpers.check_config_compatible(changed_transform_config, ch_table_config)

        del changed_transform_config['calculated_fields']['orders_quadkey']

        with pytest.raises(exceptions.ConfigError):
            helpers.check_config_compatible(changed_transform_config, ch_table_config)

    def test_unequal_changed(self):
        changed_transform_config = copy.deepcopy(transform_config)
        changed_transform_config['table_names']['metadata']['dttm']['alias'] = 'tim'

        with pytest.raises(exceptions.ConfigError):
            helpers.check_config_compatible(changed_transform_config, ch_table_config)

    def test_all_unequal(self):
        changed_ch_table_config = copy.deepcopy(ch_table_config)
        changed_transform_config = copy.deepcopy(transform_config)

        del changed_transform_config['calculated_fields']['orders_quadkey']
        del changed_ch_table_config['columns']['time']

        with pytest.raises(exceptions.ConfigError):
            helpers.check_config_compatible(changed_transform_config, changed_ch_table_config)
