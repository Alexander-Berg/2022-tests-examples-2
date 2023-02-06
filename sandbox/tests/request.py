# -*- coding: utf-8 -*-

import unittest
from sandbox.projects.sandbox_ci.tests import MagicMock
from sandbox.projects.sandbox_ci.utils.request import send_request
from requests.exceptions import ChunkedEncodingError


class TestRequest(unittest.TestCase):
    def test_econnreset(self):
        """Should make another try in case of econnreset"""
        self.mocked_request = MagicMock(side_effect=ChunkedEncodingError)
        self.make_request = MagicMock(return_value=self.mocked_request)

        with self.assertRaises(ChunkedEncodingError):
            send_request('post', 'http://yandex.ru', make_request=self.make_request)
            self.mocked_request.assert_called_count(2)
