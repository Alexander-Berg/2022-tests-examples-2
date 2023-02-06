from unittest import TestCase

import mock
from passport.backend.tvm_keyring import settings
from passport.backend.tvm_keyring.test.base import BaseTestCase
from passport.backend.tvm_keyring.test.base_test_data import TEST_TVM_KEYS
from passport.backend.tvm_keyring.test.fake_tvm import tvm_ticket_response
from passport.backend.tvm_keyring.tvm import (
    TVM,
    TVMPermanentError,
    TVMTemporaryError,
)
import pytest
import requests
from ticket_parser2.low_level import ServiceContext


TEST_CLIENT_ID = 1
TEST_CLIENT_SECRET = settings.FAKE_CLIENT_SECRET


class TVMRequestTestCase(TestCase):
    def setUp(self):
        super(TVMRequestTestCase, self).setUp()
        self.tvm = TVM()
        self.service_context = ServiceContext(
            client_id=TEST_CLIENT_ID,
            secret=TEST_CLIENT_SECRET,
            # приведение к строке - make ServiceContext happy
            tvm_keys=TEST_TVM_KEYS.decode('utf-8'),
        )

        self.request_mock = mock.Mock()
        self.request_patch = mock.patch('requests.request', self.request_mock)
        self.request_patch.start()

    def tearDown(self):
        self.request_patch.stop()
        super(TVMRequestTestCase, self).tearDown()

    def _make_resp(self, content):
        resp = mock.Mock()
        resp.content = content
        resp.status_code = 200
        return resp

    def test_keys(self):
        self.request_mock.return_value = self._make_resp(b'keys')
        assert self.tvm.keys() == 'keys'
        assert self.request_mock.call_args[1]['method'] == 'GET'
        assert 'lib_version' in self.request_mock.call_args[1]['params']

    def test_client_credentials(self):
        self.request_mock.return_value = self._make_resp(tvm_ticket_response({'2': 'ticket2'}))
        self.tvm.client_credentials(src=TEST_CLIENT_ID, dst=[2, 3], service_context=self.service_context)

        assert self.request_mock.call_args[1]['method'] == 'POST'
        request_data = self.request_mock.call_args[1]['data']
        assert 'sign' in request_data
        assert 'ts' in request_data
        assert request_data['grant_type'] == 'client_credentials'
        assert request_data['src'] == TEST_CLIENT_ID
        assert request_data['dst'] == '2,3'


class TVMTestCase(BaseTestCase):
    def setUp(self):
        super(TVMTestCase, self).setUp()
        self.tvm = TVM()
        self.service_context = ServiceContext(
            client_id=TEST_CLIENT_ID,
            secret=TEST_CLIENT_SECRET,
            # приведение к строке - make ServiceContext happy
            tvm_keys=TEST_TVM_KEYS.decode('utf-8'),
        )

    def test_keys_ok(self):
        self.fake_tvm.set_response_value(TEST_TVM_KEYS)
        # tvm.keys() возвращает строку, поэтому правую часть выражения приводим к строке
        assert self.tvm.keys() == TEST_TVM_KEYS.decode('utf-8')

    def test_tickets_ok(self):
        self.fake_tvm.set_response_value(tvm_ticket_response({'2': 'ticket2'}))
        actual = self.tvm.client_credentials(src=TEST_CLIENT_ID, dst=[2], service_context=self.service_context)
        expected = {'2': {'ticket': 'ticket2'}}
        assert actual == expected

    def test_tickets_no_client(self):
        self.fake_tvm.set_response_value(tvm_ticket_response({}, {'2': 'No client'}))
        actual = self.tvm.client_credentials(src=TEST_CLIENT_ID, dst=[2], service_context=self.service_context)
        expected = {'2': {'error': 'No client'}}
        assert actual == expected

    def test_network_problem(self):
        with pytest.raises(TVMTemporaryError):
            self.fake_tvm.set_response_side_effect(requests.Timeout)
            self.tvm.client_credentials(src=TEST_CLIENT_ID, dst=[2], service_context=self.service_context)

    def test_server_down(self):
        with pytest.raises(TVMPermanentError):
            self.fake_tvm.set_response_value('server_down', status=500)
            self.tvm.client_credentials(src=TEST_CLIENT_ID, dst=[2], service_context=self.service_context)

    def test_bad_return_code(self):
        with pytest.raises(TVMPermanentError):
            self.fake_tvm.set_response_value('{}', status=419)
            self.tvm.client_credentials(src=TEST_CLIENT_ID, dst=[2], service_context=self.service_context)

    def test_invalid_request(self):
        with pytest.raises(TVMPermanentError):
            self.fake_tvm.set_response_value('{"desc": "no client"}', status=400)
            self.tvm.client_credentials(src=42, dst=[2], service_context=self.service_context)
