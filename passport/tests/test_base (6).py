# -*- coding: utf-8 -*-
from unittest import TestCase

import mock
from passport.backend.utils.file import read_file


class BaseLoader(TestCase):
    def setUp(self):
        self.io_open_mock = mock.MagicMock(name='read_file', spec=read_file)
        self.io_open_patch = mock.patch('passport.backend.utils.file.read_file', self.io_open_mock, create=True)

        self.io_open_patch.start()
        self.mocks = []

        self.maxDiff = None

    def setup_open_file_side_effect(self):
        self.io_open_mock.side_effect = self.mocks

    def add_mock_file(self, file_data):
        return file_data

    def tearDown(self):
        self.io_open_patch.stop()
        del self.io_open_patch
        del self.io_open_mock
        del self.mocks
