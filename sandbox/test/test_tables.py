import logging
from collections import OrderedDict

import pytest

from yt.wrapper import ypath_join
from yt import yson
from sandbox.projects.yabs.qa.bases.sample_tables import tables
from sandbox.projects.yabs.qa.bases.sample_tables.test.misc import create_test_table


class TestTableConfig(object):
    @pytest.mark.parametrize('is_dynamic', [True, False], ids=['dynamic', 'static'])
    def test_single_table_config(self, input_prefix, output_prefix, yt_client, is_dynamic):
        table_relative_path = 'my_{}_table'.format('dynamic' if is_dynamic else 'static')
        event_join_key = ['BannerID']
        sort_key = ['Column1', 'Column2']

        create_test_table(input_prefix, table_relative_path, sort_key, event_join_key, yt_client, is_dynamic)

        # Test
        table_config = tables.SamplingTableConfig(
            table_relative_path,
            event_join_key,
            sort_key,
            input_prefix,
            output_prefix,
            need_mount=is_dynamic,
        )
        table_config.check_original_table_type(yt_client)

        # Validate
        assert table_config.absolute_input_path == '{}/{}'.format(input_prefix, table_relative_path)
        assert table_config.absolute_output_path == '{}/{}'.format(output_prefix, table_relative_path)
        assert table_config.is_dynamic == is_dynamic
        assert table_config.intermediate_absolute_output_path == '{}/{}.sampled'.format(output_prefix, table_relative_path)
        assert table_config.intermediate_merged_absolute_output_path == '{}/{}.merged'.format(output_prefix, table_relative_path)
        assert table_config.event_join_key == event_join_key
        assert table_config.sort_key == sort_key
        assert table_config.need_mount == is_dynamic

    def test_absent_table_config(self, input_prefix, output_prefix, yt_client):
        test_tables = OrderedDict([
            ('my_absent_table', {'join_key': ['BannerID']})
        ])

        # Test
        table_configs = tables.create_sampling_tables_config(input_prefix, output_prefix, yt_client, tables=test_tables)

        # Validate
        assert table_configs == []

    def test_multiple_tables_config(self, input_prefix, output_prefix, yt_client):
        test_tables_list = [
            ('my_first_table', ['BannerID'], ['FirstKey']),
            ('my_second_table', ['GroupExportID'], ['SecondKey']),
        ]
        test_tables = OrderedDict([
            (table_relative_path, {'join_key': event_join_key})
            for table_relative_path, event_join_key, _ in test_tables_list
        ])
        for table_relative_path, event_join_key, sort_key in test_tables_list:
            create_test_table(input_prefix, table_relative_path, sort_key, event_join_key, yt_client, is_dynamic=False)

        # Test
        table_configs = tables.create_sampling_tables_config(input_prefix, output_prefix, yt_client, tables=test_tables)

        # Validate
        for idx, table_config in enumerate(table_configs):
            expected_table_relative_path, expected_event_join_key, expected_sort_key = test_tables_list[idx]
            logging.info('Checking %s', test_tables_list[idx])

            assert table_config.absolute_input_path == '{}/{}'.format(input_prefix, expected_table_relative_path)
            assert table_config.absolute_output_path == '{}/{}'.format(output_prefix, expected_table_relative_path)
            assert table_config.is_dynamic is False
            assert table_config.intermediate_absolute_output_path == '{}/{}.sampled'.format(output_prefix, expected_table_relative_path)
            assert table_config.event_join_key == expected_event_join_key
            assert table_config.sort_key == expected_sort_key


class TestCreateDynamicTableEmptyCopy(object):
    @pytest.mark.parametrize('already_created', [True, False], ids=['already_created', 'should_be_created'])
    def test_create_dynamic_table_empty_copy(self, yt_client, already_created):
        work_prefix = '//home/test/dynamic_table_copy_test_{}'.format('already_created' if already_created else 'should_be_created')
        source_table_name = 'dynamic_table'
        target_table_name = 'dynamic_table.copy'
        create_test_table(work_prefix, source_table_name, ['Key1'], ['Column'], yt_client, True)
        if already_created:
            create_test_table(work_prefix, target_table_name, ['Key2'], ['Column'], yt_client, True)

        source = '{}/{}'.format(work_prefix, source_table_name)
        target = '{}/{}'.format(work_prefix, target_table_name)
        should_be_created = not already_created

        created = tables.create_dynamic_table_empty_copy(source, target, yt_client)

        assert created == should_be_created
        if already_created:
            source_schema = yt_client.get(ypath_join(source, '@schema'))
            target_schema = yt_client.get(ypath_join(target, '@schema'))

            assert source_schema != target_schema


class TestCloneArchiveWithSymlinks(object):
    def test_clone_table(self, yt_client, input_prefix, input_table, output_prefix):

        tables.clone_archive_with_symlinks(input_table, input_prefix, output_prefix, yt_client)

        expected_table_path = ypath_join(output_prefix, input_table[len(input_prefix):].lstrip('/'))

        assert yt_client.exists(expected_table_path)
        assert yt_client.get(expected_table_path + '&/@type') == 'link'
        assert yt_client.get(expected_table_path + '/@path') == input_table

    def test_clone_symlink(self, yt_client, input_table, input_prefix, output_prefix):
        input_symlink = ypath_join(input_prefix, 'my_symlink')
        yt_client.link(input_table, input_symlink, recursive=True)

        tables.clone_archive_with_symlinks(input_symlink, input_prefix, output_prefix, yt_client)

        expected_table_path = ypath_join(output_prefix, input_table[len(input_prefix):].lstrip('/'))
        expected_symlink_path = ypath_join(output_prefix, 'my_symlink')

        assert yt_client.exists(expected_table_path)
        assert yt_client.get(expected_table_path + '&/@type') == 'link'
        assert yt_client.get(expected_table_path + '/@path') == input_table

        assert yt_client.exists(expected_symlink_path)
        assert yt_client.get(expected_symlink_path + '&/@type') == 'link'
        assert yt_client.get(expected_symlink_path + '/@path') == input_table

    def test_clone(self, yt_client, input_table, input_prefix, output_prefix):
        input_symlink = ypath_join(input_prefix, 'my_symlink')
        yt_client.link(input_table, input_symlink, recursive=True)
        nested_table = ypath_join(input_prefix, 'folder', 'my_nested_table')
        yt_client.create('table', nested_table, recursive=True)

        tables.clone_archive_with_symlinks(input_prefix, input_prefix, output_prefix, yt_client)

        expected_table_path = ypath_join(output_prefix, input_table[len(input_prefix):].lstrip('/'))
        expected_folder_path = ypath_join(output_prefix, 'folder')
        expected_nested_table_path = ypath_join(output_prefix, 'folder', 'my_nested_table')
        expected_symlink_path = ypath_join(output_prefix, 'my_symlink')

        assert yt_client.exists(expected_table_path)
        assert yt_client.get(expected_table_path + '&/@type') == 'link'
        assert yt_client.get(expected_table_path + '/@path') == input_table

        assert yt_client.exists(expected_symlink_path)
        assert yt_client.get(expected_symlink_path + '&/@type') == 'link'
        assert yt_client.get(expected_symlink_path + '/@path') == input_table

        assert yt_client.exists(expected_folder_path)
        assert yt_client.exists(expected_nested_table_path)
        assert yt_client.get(expected_nested_table_path + '&/@type') == 'link'
        assert yt_client.get(expected_nested_table_path + '/@path') == nested_table


class TestCheckMergedTablesExistence(object):
    @pytest.mark.parametrize('merged', (True, False))
    def test_static(self, input_prefix, output_prefix, static_table_config, yt_client, schema, merged):
        if merged:
            yt_client.create('table', static_table_config.intermediate_absolute_output_path, attributes={'schema': schema})
            yt_client.link(static_table_config.intermediate_absolute_output_path, static_table_config.intermediate_merged_absolute_output_path)
        assert tables.check_merged_intermediate_tables_existence([static_table_config], yt_client) == [] if merged else [static_table_config]

    @pytest.mark.parametrize('merged', (True, False))
    def test_dynamic(self, input_prefix, output_prefix, dynamic_table_config, yt_client, schema, merged):
        if merged:
            yt_client.create('table', dynamic_table_config.intermediate_absolute_output_path, attributes={'schema': schema})
            yt_client.link(dynamic_table_config.intermediate_absolute_output_path, dynamic_table_config.intermediate_merged_absolute_output_path)
        assert tables.check_merged_intermediate_tables_existence([dynamic_table_config], yt_client) == [] if merged else [dynamic_table_config]

    def test_static_change_to_dynamic(self, input_prefix, output_prefix, dynamic_table_config, yt_client, schema):
        yson_schema = yson.YsonList(schema)
        yson_schema.attributes['strict'] = False
        yt_client.create('table', dynamic_table_config.intermediate_absolute_output_path, attributes={'schema': yson_schema})
        yt_client.link(dynamic_table_config.intermediate_absolute_output_path, dynamic_table_config.intermediate_merged_absolute_output_path)
        assert tables.check_merged_intermediate_tables_existence([dynamic_table_config], yt_client) == [dynamic_table_config]
