# -*- coding: utf-8 -*-
import json
from unittest import TestCase

from nose.tools import (
    eq_,
    raises,
)
from passport.backend.core.builders.blackbox.faker.blackbox import (
    blackbox_check_sign_response,
    blackbox_sign_response,
    FakeBlackbox,
)
from passport.backend.core.encrypted_container import (
    BaseEncryptedContainer,
    EncryptedContainerInvalid,
    EncryptedContainerUnknownType,
)
from passport.backend.core.test.test_utils import with_settings
from passport.backend.core.tvm.faker.fake_tvm_credentials_manager import (
    fake_tvm_credentials_data,
    FakeTvmCredentialsManager,
    TEST_TICKET,
)


class SampleContainer(BaseEncryptedContainer):
    type_to_ttl = {
        'basic': 10,
        'long': 100,
    }
    type_to_sign_space = {
        'long': 'custom_space',
    }
    default_type = 'basic'


@with_settings(
    BLACKBOX_URL='http://localhost/',
)
class TestEncryptedContainer(TestCase):
    def setUp(self):
        self.fake_tvm_credentials_manager = FakeTvmCredentialsManager()
        self.fake_tvm_credentials_manager.set_data(fake_tvm_credentials_data(
            ticket_data={
                '1': {
                    'alias': 'blackbox',
                    'ticket': TEST_TICKET,
                },
            },
        ))
        self.fake_tvm_credentials_manager.start()

        self.fake_blackbox = FakeBlackbox()
        self.fake_blackbox.start()

    def tearDown(self):
        self.fake_blackbox.stop()
        self.fake_tvm_credentials_manager.stop()
        del self.fake_blackbox
        del self.fake_tvm_credentials_manager

    def test_container(self):
        container = SampleContainer(data={'foo': 1, 'bar': '2'})
        container['zar'] = 3
        eq_(
            container.data,
            {'foo': 1, 'bar': '2', 'zar': 3},
        )
        eq_(container['foo'], 1)

    @raises(EncryptedContainerUnknownType)
    def test_pack__unkhown_type(self):
        SampleContainer(data={}, container_type='unknown')

    def test_pack_default_type__ok(self):
        self.fake_blackbox.set_response_value(
            'sign',
            blackbox_sign_response('abc'),
        )
        container = SampleContainer(data={})
        eq_(container.pack(), 'abc')
        self.fake_blackbox.requests[0].assert_query_contains({
            'sign_space': 'basic',
            'ttl': '10',
        })

    def test_pack_custom_type__ok(self):
        self.fake_blackbox.set_response_value(
            'sign',
            blackbox_sign_response('abc'),
        )
        container = SampleContainer(data={}, container_type='long')
        eq_(container.pack(), 'abc')
        self.fake_blackbox.requests[0].assert_query_contains({
            'sign_space': 'custom_space',
            'ttl': '100',
        })

    @raises(EncryptedContainerInvalid)
    def test_unpack__invalid_error(self):
        self.fake_blackbox.set_response_value(
            'check_sign',
            blackbox_check_sign_response(status='INVALID'),
        )
        SampleContainer.unpack('abc', container_type='basic')

    @raises(EncryptedContainerUnknownType)
    def test_unpack__unknown_type(self):
        self.fake_blackbox.set_response_value(
            'check_sign',
            blackbox_check_sign_response(value=json.dumps({'uid': 1, 'ts': 300})),
        )
        SampleContainer.unpack('abc', container_type='unknown')

    def test_unpack_default_type_ok(self):
        self.fake_blackbox.set_response_value(
            'check_sign',
            blackbox_check_sign_response(value=json.dumps({'uid': 1, 'ts': 300})),
        )
        container = SampleContainer.unpack('abc')
        eq_(container.data, {'uid': 1, 'ts': 300})
        self.fake_blackbox.requests[0].assert_query_contains({
            'sign_space': 'basic',
        })

    def test_unpack_custom_type__ok(self):
        self.fake_blackbox.set_response_value(
            'check_sign',
            blackbox_check_sign_response(value=json.dumps({'uid': 1, 'ts': 300})),
        )
        container = SampleContainer.unpack('abc', container_type='long')
        eq_(container.data, {'uid': 1, 'ts': 300})
        self.fake_blackbox.requests[0].assert_query_contains({
            'sign_space': 'custom_space',
        })
