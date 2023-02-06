import logging
import os
import shutil
import tempfile
import unittest

from sandbox.projects.mobile_apps.utils.archive import Archive

logger = logging.getLogger("test_archive")


class TestArchive(unittest.TestCase):

    src_filename = 'example.txt'
    data = 'Simple text'

    @staticmethod
    def _read_data(filename):
        with open(filename) as fh:
            data = fh.read()
        logger.debug("Read data {} from {}".format(data, filename))
        return data

    def _prepare_data(self, archive_filename):
        self.temp_src_dir = tempfile.mkdtemp()
        self.temp_dst_pack_dir = tempfile.mkdtemp()
        self.temp_dst_unpack_dir = tempfile.mkdtemp()

        self.src_full_path = os.path.join(self.temp_src_dir, self.src_filename)

        with open(self.src_full_path, 'w') as fh:
            fh.write(self.data)

        self.dst_archive_full_path = os.path.join(self.temp_dst_pack_dir, archive_filename)
        self.dst_unpacked_full_path = os.path.join(self.temp_dst_unpack_dir, self.src_filename)

    def _delete_data(self):
        for tmpdir in (self.temp_src_dir, self.temp_dst_pack_dir, self.temp_dst_unpack_dir):
            shutil.rmtree(tmpdir)

    def test_archives(self):
        for archive_filename in ['test.zip', 'test.tgz']:
            self._prepare_data(archive_filename)

            Archive.pack(archive_filename, self.temp_dst_pack_dir, self.temp_src_dir)
            Archive.unpack(self.dst_archive_full_path, self.temp_dst_unpack_dir)

            assert self.data == self._read_data(self.dst_unpacked_full_path)

            self._delete_data()
