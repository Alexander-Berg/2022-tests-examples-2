# -*- coding: utf-8 -*-
import mock
from passport.backend.core.logbroker.faker.fake_logbroker import FakeLogbrokerWriterProto
from passport.backend.core.logbroker.logbroker import (
    get_logbroker_writer,
    LogbrokerWriterProto,
)
from passport.backend.core.logbroker.test.constants import (
    TEST_NAME1,
    TEST_NAME2,
    TEST_PAYLOAD,
)
from passport.backend.core.logbroker.tests.base.base import TestLogbrokerBase
from passport.backend.core.logbroker.tests.base.test_proto.test_proto_pb2 import TestMessage as ProtoTestMessage


TEST_PAYLOAD2 = 'test123zcc'
TEST_PROTOBUF = ProtoTestMessage(string_val=TEST_PAYLOAD)
TEST_PROTOBUF2 = ProtoTestMessage(string_val=TEST_PAYLOAD2)
TEST_META2 = {'key2': 'value2', 'key3': 'value3'}


class TestLogbrokerFaker(TestLogbrokerBase):
    def setUp(self):
        super(TestLogbrokerFaker, self).setUp()
        self._faker = FakeLogbrokerWriterProto(LogbrokerWriterProto, TEST_NAME1)
        self._patches.append(self._faker)
        self._faker.start()

    def test_patch__ok(self):
        logbroker = get_logbroker_writer(TEST_NAME1)
        self.assertIs(logbroker, self._faker)

    def test_non_patched__ok(self):
        logbroker = get_logbroker_writer(TEST_NAME2)
        self.assertIsNot(logbroker, self._faker)
        self.assertIsInstance(logbroker, LogbrokerWriterProto)

    def test_send__single__ok(self):
        logbroker = get_logbroker_writer(TEST_NAME1)
        logbroker.send(payload=TEST_PROTOBUF)
        self._faker.send_calls.assert_called_once_with(payload=TEST_PROTOBUF)
        self.assertEqual(
            self._faker.dict_requests,
            [
                {'string_val': TEST_PAYLOAD},
            ],
        )

    def test_send_multiple__ok(self):
        logbroker = get_logbroker_writer(TEST_NAME1)
        logbroker.send(payload=TEST_PROTOBUF)
        logbroker.send(payload=TEST_PROTOBUF2)
        self.assertEqual(self._faker.send_calls.call_count, 2)
        self._faker.send_calls.assert_has_calls(
            [
                mock.call(payload=TEST_PROTOBUF),
                mock.call(payload=TEST_PROTOBUF2),
            ],
            any_order=False,
        )
        self.assertEqual(
            self._faker.dict_requests,
            [
                {'string_val': TEST_PAYLOAD},
                {'string_val': TEST_PAYLOAD2},
            ],
        )
