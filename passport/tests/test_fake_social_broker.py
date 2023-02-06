# -*- coding: utf-8 -*-

import unittest

from nose.tools import (
    assert_raises,
    eq_,
    ok_,
)
from passport.backend.core.builders.social_broker import (
    SocialBroker,
    SocialBrokerRequestError,
)
from passport.backend.core.builders.social_broker.faker.social_broker import (
    check_pkce_ok_response,
    FakeSocialBroker,
)
from passport.backend.core.test.test_utils import with_settings
from passport.backend.core.tvm.faker.fake_tvm_credentials_manager import (
    fake_tvm_credentials_data,
    FakeTvmCredentialsManager,
    TEST_TICKET,
)


@with_settings(SOCIAL_BROKER_URL='http://none.yandex.ru/brokerapi/', SOCIAL_BROKER_RETRIES=2, SOCIAL_BROKER_TIMEOUT=1)
class FakeSocialBrokerTestCase(unittest.TestCase):
    def setUp(self):
        self.fake_tvm_credentials_manager = FakeTvmCredentialsManager()
        self.fake_tvm_credentials_manager.set_data(fake_tvm_credentials_data(
            ticket_data={
                '1': {
                    'alias': 'social_broker',
                    'ticket': TEST_TICKET,
                },
            },
        ))
        self.fake_tvm_credentials_manager.start()

        self.fake_social_broker = FakeSocialBroker()
        self.fake_social_broker.start()
        self.task_id = '1234567890fedcba'

    def tearDown(self):
        self.fake_social_broker.stop()
        del self.fake_social_broker
        self.fake_tvm_credentials_manager.stop()
        del self.fake_tvm_credentials_manager

    def test_set_social_broker_response_value(self):
        ok_(not self.fake_social_broker._mock.request.called)
        self.fake_social_broker.set_social_broker_response_value(
            FakeSocialBroker.get_task_by_token_response(task_id=self.task_id),
        )
        result = SocialBroker().get_task_by_token('fb', None, 'consumer', 'abc', 'def', 's1,s2')
        ok_(self.fake_social_broker._mock.request.called)
        eq_(result['task_id'], self.task_id)

    def test_set_social_broker_response_side_effect(self):
        ok_(not self.fake_social_broker._mock.request.called)
        self.fake_social_broker.set_social_broker_response_side_effect(
            SocialBrokerRequestError('fake_message'),
        )
        with assert_raises(SocialBrokerRequestError):
            SocialBroker().get_task_by_token('fb', None, 'consumer', 'abc', 'def', 's1,s2')
        ok_(self.fake_social_broker._mock.request.called)

    def test_get_task_by_token(self):
        self.fake_social_broker.set_response_value(
            'get_task_by_token',
            FakeSocialBroker.get_task_by_token_response(task_id=self.task_id),
        )
        result = SocialBroker().get_task_by_token('fb', None, 'consumer', 'abc', 'def', 's1,s2')
        eq_(result['task_id'], self.task_id)

    def test_check_pkce(self):
        self.fake_social_broker.set_response_value(
            'check_pkce',
            check_pkce_ok_response(),
        )
        result = SocialBroker().check_pkce('task_id', 'verifier')
        eq_(result, {'status': 'ok'})
