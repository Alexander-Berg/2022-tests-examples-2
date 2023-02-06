# -*- coding: utf-8 -*-
import json
from unittest import TestCase

from nose.tools import (
    assert_raises,
    eq_,
    ok_,
)
from passport.backend.core.builders.base.faker.fake_builder import assert_builder_requested
from passport.backend.core.builders.federal_configs_api import (
    BaseFederalConfigsApiError,
    FederalConfigsApi,
)
from passport.backend.core.builders.federal_configs_api.faker import (
    FakeFederalConfigsApi,
    federal_config_ok,
)
from passport.backend.core.test.test_utils import with_settings
from passport.backend.core.tvm.faker.fake_tvm_credentials_manager import (
    fake_tvm_credentials_data,
    FakeTvmCredentialsManager,
    TEST_TICKET,
)


@with_settings(
    FEDERAL_CONFIGS_API_URL='http://localhost/',
    FEDERAL_CONFIGS_API_RETRIES=2,
    FEDERAL_CONFIGS_API_TIMEOUT=1,
    FEDERAL_CONFIGS_API_NAMESPACE='360',
)
class FakeFederalConfigsApiTestCase(TestCase):
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

        self.faker = FakeFederalConfigsApi()
        self.faker.start()
        self.federal_configs_api = FederalConfigsApi()

    def tearDown(self):
        self.faker.stop()
        del self.faker
        self.fake_tvm.stop()
        del self.fake_tvm

    def test_config_by_domain_id(self):
        self.faker.set_response_value(
            'config_by_domain_id',
            json.dumps(federal_config_ok()),
        )
        eq_(
            self.federal_configs_api.get_config_by_domain_id(domain_id=1),
            federal_config_ok(),
        )

    def test_config_by_entity_id(self):
        self.faker.set_response_value(
            'config_by_entity_id',
            json.dumps(federal_config_ok()),
        )
        eq_(
            self.federal_configs_api.get_config_by_entity_id(entity_id='http://entity.com'),
            federal_config_ok(),
        )

    def test_set_response_side_effect(self):
        ok_(not self.faker._mock.request.called)

        builder = FederalConfigsApi()
        self.faker.set_response_side_effect('user_orders', BaseFederalConfigsApiError)
        with assert_raises(BaseFederalConfigsApiError):
            builder.get_config_by_domain_id(11)
        assert_builder_requested(self.faker)
