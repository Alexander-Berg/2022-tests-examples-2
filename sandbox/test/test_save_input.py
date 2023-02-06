from sandbox.projects.yabs.qa.bases.save_input import save_input


class TestSaveInput(object):

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

    def test_save_input(self, yt_client, input_table, input_table_name, output_prefix):
        tables_config = [
            {
                'id': input_table_name,
                'path': input_table,
            }
        ]

        save_input(
            yt_client,
            tables_config,
            output_prefix,
        )

        self.check_node(yt_client, output_prefix + '/yt_tables/' + input_table.lstrip('//'), 'table')
