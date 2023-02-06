from sandbox.projects.yabs.qa.bases.sample_tables.tables import create_dynamic_table_empty_copy

from sandbox.projects.yabs.qa.bases.sample_tables.sampling import merge_sampled_tables


class TestMergeSampledTables(object):
    def test_merge_static_table(self, input_prefix, output_prefix, static_table_config, yt_client):
        yt_client.create('table', static_table_config.intermediate_absolute_output_path, recursive=True)

        merge_sampled_tables([static_table_config], yt_client)
        assert yt_client.exists(static_table_config.intermediate_merged_absolute_output_path)
        assert yt_client.get(static_table_config.intermediate_merged_absolute_output_path + '&/@type') == 'link'
        assert yt_client.get(static_table_config.intermediate_merged_absolute_output_path + '/@path') == static_table_config.intermediate_absolute_output_path

    def test_merge_dynamic_table(self, input_prefix, output_prefix, dynamic_table_config, yt_client):
        create_dynamic_table_empty_copy(dynamic_table_config.absolute_input_path, dynamic_table_config.intermediate_absolute_output_path, yt_client)

        merge_sampled_tables([dynamic_table_config], yt_client)
        assert yt_client.exists(dynamic_table_config.intermediate_merged_absolute_output_path)
        assert yt_client.get(dynamic_table_config.intermediate_merged_absolute_output_path + '&/@type') == 'table'
        assert yt_client.get(dynamic_table_config.intermediate_merged_absolute_output_path + '&/@schema').attributes['strict']

    def test_merge_former_static_table(self, input_prefix, output_prefix, dynamic_table_config, schema, yt_client):
        yt_client.create('table', dynamic_table_config.intermediate_absolute_output_path, attributes={'schema': schema}, recursive=True)
        yt_client.link(dynamic_table_config.intermediate_absolute_output_path, dynamic_table_config.intermediate_merged_absolute_output_path)

        merge_sampled_tables([dynamic_table_config], yt_client)
        assert yt_client.exists(dynamic_table_config.intermediate_merged_absolute_output_path)
        assert yt_client.get(dynamic_table_config.intermediate_merged_absolute_output_path + '&/@type') == 'table'
        assert yt_client.get(dynamic_table_config.intermediate_merged_absolute_output_path + '&/@schema').attributes['strict']
