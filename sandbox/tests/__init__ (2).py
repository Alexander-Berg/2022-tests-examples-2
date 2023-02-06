import os

from sandbox.agentr import utils

from sandbox.common import fs as common_fs


class TestUtils(object):
    def test__dump_disk_usage(self, tmpdir):
        os.makedirs(os.path.join(str(tmpdir), 'testdir', 'innerdir'))
        testdir = os.path.join(str(tmpdir), 'testdir')
        common_fs.allocate_file(os.path.join(testdir, 'foo'), 1024)
        common_fs.allocate_file(os.path.join(testdir, 'innerdir', 'bar'), 2048)
        common_fs.allocate_file(os.path.join(testdir, 'innerdir', 'baz'), 1000)

        # testing get_disk_usage
        assert utils.get_disk_usage(testdir)[1] == 4072
        assert utils.get_disk_usage(os.path.join(testdir, 'foo'), allow_files=True)[1] == 1024

        # testing normal mode
        dump_path = os.path.join(str(tmpdir), 'dump')
        utils.dump_dir_disk_usage_scandir(testdir, dump_path)

        assert os.stat(dump_path).st_size == 70

        os.remove(dump_path)

        # testing overwrite mode
        dump_path = os.path.join(str(tmpdir), 'dump')
        common_fs.allocate_file(dump_path, 10 * 1024 ** 2)
        utils.dump_dir_disk_usage_scandir(testdir, dump_path)

        assert os.stat(dump_path).st_size == 70
