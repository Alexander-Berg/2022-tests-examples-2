from collections import OrderedDict

from yt.wrapper import ypath_join
from sandbox.projects.yabs.qa.bases.sample_tables import tables
from sandbox.projects.yabs.qa.bases.sample_tables.update_spec import replace_table_paths_with_sampled


def create_test_table(input_prefix, table_relative_path, yt_client):
    schema = [
        {'type': 'uint64', 'name': 'test_col', 'required': False, 'sort_order': 'ascending'}
    ]

    yt_client.create(
        'table',
        ypath_join(input_prefix, table_relative_path),
        recursive=True,
        attributes={
            'schema': schema,
            'dynamic': False,
        }
    )


def create_test_link(input_prefix, node_relative_path, target_relative_path, yt_client):
    yt_client.link(
        ypath_join(input_prefix, target_relative_path),
        ypath_join(input_prefix, node_relative_path),
        recursive=True
    )


class TestUpdateSpecSingleLink(object):
    def test_single_link(self, input_prefix, output_prefix, yt_client):
        # Create two tables
        test_tables_list = [
            's1',
            's9',
        ]
        # Create link to first table
        test_links_list = [
            ('s2', 's1'),
        ]
        # Sample first table
        test_sampled_tables = OrderedDict([
            ('s1', {'join_key': 'test_col'}),
        ])
        # Supply two tables and link in spec
        spec = OrderedDict([
            ('one', ypath_join(input_prefix, 's1')),
            ('two', ypath_join(input_prefix, 's2')),
            ('nine', ypath_join(input_prefix, 's9')),
        ])
        # Expect that first table and link will be replaced with sampled table path
        # Expect that path to s9 table is not replaced
        expected_spec = OrderedDict([
            ('one', ypath_join(output_prefix, 's1')),
            ('two', ypath_join(output_prefix, 's1')),
            ('nine', ypath_join(input_prefix, 's9')),
        ])
        for table_relative_path in test_tables_list:
            create_test_table(input_prefix, table_relative_path, yt_client)
        for node_relative_path, target_relative_path in test_links_list:
            create_test_link(input_prefix, node_relative_path, target_relative_path, yt_client)

        table_configs = tables.create_sampling_tables_config(
            input_prefix,
            output_prefix,
            yt_client,
            tables=test_sampled_tables
        )

        updated_spec = replace_table_paths_with_sampled(
            yt_client,
            spec,
            table_configs,
            input_prefix
        )

        assert updated_spec == expected_spec

    def test_multiple_links(self, input_prefix, output_prefix, yt_client):
        # Create three tables: m9 will have no links
        test_tables_list = [
            'm1',
            'm6',
            'm9',
        ]
        # Create a chain of links: m5 -> m3 -> m2 -> m1
        # Create a link: m4 -> m1
        # Create a link: m7 -> m6
        # Create a link: m8 -> m6
        test_links_list = [
            ('m2', 'm1'),
            ('m3', 'm2'),
            ('m4', 'm1'),
            ('m5', 'm3'),
            ('m7', 'm6'),
            ('m8', 'm6'),
        ]
        # Sample m2 link (which actually results in sampling table m1, but name of sampled table is m2.sampled) and m6 table
        test_sampled_tables = OrderedDict([
            ('m2', {'join_key': 'test_col'}),
            ('m6', {'join_key': 'test_col'}),
        ])
        # Supply all created tables and links in spec
        spec = OrderedDict([
            ('one', ypath_join(input_prefix, 'm1')),
            ('two', ypath_join(input_prefix, 'm2')),
            ('three', ypath_join(input_prefix, 'm3')),
            ('four', ypath_join(input_prefix, 'm4')),
            ('five', ypath_join(input_prefix, 'm5')),
            ('six', ypath_join(input_prefix, 'm6')),
            ('seven', ypath_join(input_prefix, 'm7')),
            ('eight', ypath_join(input_prefix, 'm8')),
            ('nine', ypath_join(input_prefix, 'm9')),
        ])
        # Expect that all links to tables m1 and m6 are replaced with paths to sampled tables
        # Expect that path to m9 table is not replaced
        expected_spec = OrderedDict([
            # These are m1 table and links to it
            ('one', ypath_join(output_prefix, 'm2')),
            ('two', ypath_join(output_prefix, 'm2')),
            ('three', ypath_join(output_prefix, 'm2')),
            ('four', ypath_join(output_prefix, 'm2')),
            ('five', ypath_join(output_prefix, 'm2')),
            # These are m6 table and links to it
            ('six', ypath_join(output_prefix, 'm6')),
            ('seven', ypath_join(output_prefix, 'm6')),
            ('eight', ypath_join(output_prefix, 'm6')),
            # This table m9 was not sampled
            ('nine', ypath_join(input_prefix, 'm9')),
        ])
        for table_relative_path in test_tables_list:
            create_test_table(input_prefix, table_relative_path, yt_client)
        for node_relative_path, target_relative_path in test_links_list:
            create_test_link(input_prefix, node_relative_path, target_relative_path, yt_client)

        table_configs = tables.create_sampling_tables_config(
            input_prefix,
            output_prefix,
            yt_client,
            tables=test_sampled_tables
        )

        updated_spec = replace_table_paths_with_sampled(
            yt_client,
            spec,
            table_configs,
            input_prefix
        )

        assert updated_spec == expected_spec
