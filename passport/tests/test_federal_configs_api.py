# -*- coding: utf-8 -*-
import json

from nose.tools import (
    assert_raises,
    eq_,
)
from passport.backend.core.builders.federal_configs_api import (
    FederalConfigsApi,
    FederalConfigsApiTemporaryError,
)
from passport.backend.core.builders.federal_configs_api.faker import (
    FakeFederalConfigsApi,
    federal_config_ok,
)
from passport.backend.core.test.test_utils import (
    PassportTestCase,
    with_settings,
)
from passport.backend.core.tvm.faker.fake_tvm_credentials_manager import (
    fake_tvm_credentials_data,
    FakeTvmCredentialsManager,
    TEST_TICKET,
)
from passport.backend.core.useragent.faker.useragent import (
    FakedTimeoutError,
    UserAgentFaker,
)


@with_settings(
    FEDERAL_CONFIGS_API_URL='http://localhost/',
    FEDERAL_CONFIGS_API_RETRIES=2,
    FEDERAL_CONFIGS_API_TIMEOUT=1,
    FEDERAL_CONFIGS_API_NAMESPACE='360',
)
class TestFederalConfigsApi(PassportTestCase):
    def setUp(self):
        self.fake = FakeFederalConfigsApi()
        self.fake.start()
        self.fake.set_response_value('config_by_domain_id', json.dumps(federal_config_ok()))
        self.fake.set_response_value('config_by_entity_id', json.dumps(federal_config_ok()))
        self.fake_tvm = FakeTvmCredentialsManager()
        self.fake_tvm.set_data(fake_tvm_credentials_data(
            ticket_data={
                '1': {
                    'alias': 'federal_configs_api',
                    'ticket': TEST_TICKET,
                },
            },
        ))
        self.fake_tvm.start()

    def tearDown(self):
        self.fake_tvm.stop()
        self.fake.stop()
        del self.fake_tvm
        del self.fake

    def test_get_config_by_domain_id(self):
        client = FederalConfigsApi()
        response = client.get_config_by_domain_id(1)
        eq_(response, federal_config_ok())

        request = self.fake.requests[0]
        request.assert_url_starts_with('http://localhost/1/config/by_domain_id/1/')

    def test_get_config_by_entity_id(self):
        client = FederalConfigsApi()
        response = client.get_config_by_entity_id('http://entity.com')
        eq_(response, federal_config_ok())

        request = self.fake.requests[0]
        request.assert_url_starts_with('http://localhost/1/config/by_entity_id/http%3A%2F%2Fentity.com/')


@with_settings(
    FEDERAL_CONFIGS_API_URL='http://localhost/',
    FEDERAL_CONFIGS_API_RETRIES=2,
    FEDERAL_CONFIGS_API_TIMEOUT=1,
    FEDERAL_CONFIGS_API_NAMESPACE='360',
)
class TestFederalConfigsApiCommon(PassportTestCase):
    def setUp(self):
        self.fake_tvm = FakeTvmCredentialsManager()
        self.fake_tvm.set_data(fake_tvm_credentials_data(
            ticket_data={
                '1': {
                    'alias': 'federal_configs_api',
                    'ticket': TEST_TICKET,
                },
            },
        ))
        self.fake_tvm.start()
        self.user_agent_faker = UserAgentFaker()
        self.user_agent_faker.start()

    def tearDown(self):
        self.user_agent_faker.stop()
        self.fake_tvm.stop()

        del self.user_agent_faker
        del self.fake_tvm

    def test_timeout(self):
        self.user_agent_faker.set_responses([
            FakedTimeoutError(),
        ])

        client = FederalConfigsApi()
        with assert_raises(FederalConfigsApiTemporaryError):
            client.get_config_by_domain_id(1)
