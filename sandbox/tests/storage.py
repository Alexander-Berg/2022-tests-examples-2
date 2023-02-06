import os

from sandbox.tasklet.sidecars.resource_manager.lib import storage


class TestStorage:
    def test_resource_storage(
        self, sample_file, sample_dir, sample_file_new_resource, sample_dir_new_resource, clear_storage
    ):
        resource_storage1 = storage.Storage()
        sample_filename, sample_filepath, sample_filedata = sample_file
        sample_dir_path = sample_dir[0]

        resource1 = resource_storage1.register_resource(**sample_file_new_resource)
        resource_file_name1 = resource_storage1.resource_sync(resource1["id"])
        with open(resource_file_name1, "rb") as f:
            assert f.read() == sample_filedata

        resource2 = resource_storage1.register_resource(**sample_dir_new_resource)
        resource_file_name2 = resource_storage1.resource_sync(resource2["id"])
        assert os.listdir(sample_dir_path) == os.listdir(resource_file_name2)

        resource_storage2 = storage.Storage()
        assert len(resource_storage2.resources) == 2
        assert resource_storage2.resources[resource1["id"]] == resource1
        assert resource_storage2.resources[resource2["id"]] == resource2
