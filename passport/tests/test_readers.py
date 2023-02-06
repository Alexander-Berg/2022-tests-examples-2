# -*- coding: utf-8 -*-

import mock
from passport.backend.core.sync_utils.readers import FileReader
from passport.backend.core.test.test_utils import PassportTestCase
import six


TEST_FILE_PATH = '/this/path/does/not/exist'


class FileReaderTestCase(PassportTestCase):
    def setUp(self):
        self.mock_open = mock.Mock(return_value=six.StringIO('\n'.join(map(str, range(10, 20)))))
        self.open_patch = mock.patch('passport.backend.core.sync_utils.readers.open', self.mock_open)
        self.open_patch.start()

    def tearDown(self):
        self.open_patch.stop()

    def test_open_close__ok(self):
        reader = FileReader(TEST_FILE_PATH)
        self.mock_open.assert_not_called()

        with reader as f:
            self.mock_open.assert_called_once_with(TEST_FILE_PATH)
            self.assertEqual(f.file_obj, self.mock_open())
            self.assertFalse(f.file_obj.closed)
            file_obj = f.file_obj

        self.assertTrue(file_obj.closed)
        self.assertIsNone(f.file_obj)

    def test_read__ok(self):
        with FileReader(TEST_FILE_PATH) as f:
            self.assertEqual(list(f), ['10', '11', '12', '13', '14', '15', '16', '17', '18', '19'])

    def test_seek__ok(self):
        with FileReader(TEST_FILE_PATH) as f:
            f.seek(5)
            self.assertEqual(f.file_obj.tell(), 15)
            self.assertEqual(list(f), ['15', '16', '17', '18', '19'])
