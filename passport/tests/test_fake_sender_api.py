# -*- coding: utf-8 -*-
import unittest

from passport.backend.core.builders.sender_api.faker.sender_api import (
    sender_api_reply_error,
    sender_api_reply_ok,
)


class TestFakeSenderApiResponses(unittest.TestCase):
    def test_sender_api_reply_ok(self):
        self.assertEqual(
            sender_api_reply_ok(param1='value1'),
            dict(
                parameters=dict(param1='value1'),
                result=dict(status='ok'),
            ),
        )

    def test_sender_api_reply_error(self):
        self.assertEqual(
            sender_api_reply_error(error='error1', param1='value1'),
            dict(
                parameters=dict(param1='value1'),
                result=dict(status='error', error='error1'),
            ),
        )
