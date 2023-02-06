import uuid
import pytest

from sandbox.projects.yabs.qa.bases.save_input import save_table_if_new


class TestSaveTableIfNew(object):

    def check_node(self, yt_client, node_path, expected_node_type, expected_node_contents=None):
        assert yt_client.exists(node_path)
        actual_node_type = yt_client.get(node_path + '&/@type')
        assert actual_node_type == expected_node_type
        if actual_node_type == 'table' and expected_node_contents is not None:
            actual_node_contents = list(yt_client.read_table(node_path))
            assert actual_node_contents == expected_node_contents

    def check_symlink(self, yt_client, symlink_path, expected_target_path):
        assert yt_client.exists(symlink_path)
        actual_node_type = yt_client.get(symlink_path + '&/@type')
        assert actual_node_type == 'link'
        actual_target_path = yt_client.get(symlink_path + '/@path')
        assert actual_target_path == expected_target_path

    def test_copy(self, yt_client, input_table, output_table, input_data):

        save_table_if_new(
            yt_client,
            input_table,
            output_table,
            True,  # save_input_no_quota_attrs
        )

        self.check_node(yt_client, output_table, 'table', expected_node_contents=input_data)

    def test_copy_with_symlinks(self, yt_client, input_prefix, input_table, input_table_name, output_prefix):
        input_symlink = input_prefix + '/symlink_' + str(uuid.uuid4())
        yt_client.link(input_table, input_symlink, recursive=True)

        output_symlink = output_prefix + '/symlink_' + str(uuid.uuid4())

        save_table_if_new(
            yt_client,
            input_symlink,
            output_symlink,
            True,  # save_input_no_quota_attrs
            destination_to_recreate_links=output_prefix,
        )

        self.check_symlink(yt_client, output_symlink, output_prefix + '/' + input_table.lstrip('//'))

    @pytest.mark.parametrize('node_type', ('table', 'map_node', 'string_node'))
    def test_copy_already_exists(self, yt_client, node_type, input_table, output_table, input_data):
        yt_client.create(node_type, output_table, recursive=True)
        table_contents = None
        if node_type == 'table':
            table_contents = [{'my_column_name': str(uuid.uuid4())}]
            yt_client.write_table(output_table, table_contents)

        save_table_if_new(
            yt_client,
            input_table,
            output_table,
            True,  # save_input_no_quota_attrs
        )

        self.check_node(yt_client, output_table, node_type, expected_node_contents=table_contents)
