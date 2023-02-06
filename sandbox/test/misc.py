from yt.wrapper import ypath_join
from sandbox.projects.yabs.qa.bases.sample_tables.tables import SamplingTableConfig


def create_schema(sort_key, event_join_key):
    schema = [
        {'type': 'uint64', 'name': name, 'required': False, 'sort_order': 'ascending'}
        for name in sort_key
    ] + [
        {'type': 'uint64', 'name': name, 'required': False}
        for name in event_join_key
    ]
    return schema


def create_test_table(input_prefix, table_relative_path, sort_key, event_join_key, yt_client, is_dynamic=False):
    yt_client.create(
        'table',
        ypath_join(input_prefix, table_relative_path),
        recursive=True,
        attributes={
            'schema': create_schema(sort_key, event_join_key),
            'dynamic': is_dynamic,
        }
    )

    return table_relative_path


def create_test_table_config(input_prefix, output_prefix, table_relative_path, sort_key, event_join_key, yt_client, is_dynamic=False):
    create_test_table(input_prefix, table_relative_path, sort_key, event_join_key, yt_client, is_dynamic=is_dynamic)
    table_config = SamplingTableConfig(
        table_relative_path,
        sort_key,
        event_join_key,
        input_prefix,
        output_prefix,
        need_mount=is_dynamic,
    )
    table_config.check_original_table_type(yt_client)
    return table_config
