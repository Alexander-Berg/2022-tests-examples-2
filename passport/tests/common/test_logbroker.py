# -*- coding: utf-8 -*-
import mock
from nose_parameterized import parameterized
from passport.backend.api.common.logbroker import (
    ApiLogbrokerWriterProto,
    get_api_logbroker_writer,
)
from passport.backend.core.logbroker.test.constants import TEST_NAME1
from passport.backend.core.logbroker.tests.base.base import BaseTestCases


TEST_REQUEST_ID = 'abcdef123456'


class TestApiLogbrokerWriter(BaseTestCases.LogbrokerWriterClassTestBase):
    writer_class = ApiLogbrokerWriterProto

    def get_logbroker_writer(self, name):
        return get_api_logbroker_writer(name)

    @parameterized.expand([(TEST_REQUEST_ID,), (None,), ('',)])
    def test_send__auto_header__ok(self, request_id):
        with mock.patch('passport.backend.api.common.logbroker.get_request_id') as get_request_id:
            get_request_id.return_value = request_id
            writer = self.get_logbroker_writer(TEST_NAME1)
            self.send_writer1(writer)
            msg = self.assert_sent(writer)
            self.assertEqual(msg.header.passport_api.request_id_string, request_id or '')
