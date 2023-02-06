# -*- coding: utf-8 -*-
import json
from unittest import TestCase

import mock
from nose.tools import (
    assert_is_none,
    eq_,
)
from passport.backend.core.builders.datasync_api import DiskApi
from passport.backend.core.builders.datasync_api.faker.fake_disk_api import (
    billing_subscriptions_successful_response,
    disk_info_successful_response,
    FakeDiskApi,
    plus_subscribe_already_provided_response,
    plus_subscribe_created_response,
    plus_subscribe_removed_response,
    plus_subscription_not_found_response,
)
from passport.backend.core.test.test_utils import with_settings


TEST_UID = 123
TEST_IP = '1.2.3.4'
TEST_PLUS_PARTNER_ID = 'yandex_plus'
TEST_PLUS_PRODUCT_ID = 'yandex_plus_10gb'


@with_settings(
    DATASYNC_API_URL='http://localhost/',
    DATASYNC_API_TIMEOUT=0.5,
    DATASYNC_API_RETRIES=2,
)
class FakeDiskApiTestCase(TestCase):
    def setUp(self):
        self.faker = FakeDiskApi()
        self.faker.start()
        self.disk_api = DiskApi(tvm_credentials_manager=mock.Mock())

    def tearDown(self):
        self.faker.stop()
        del self.faker
        del self.disk_api

    def test_disk_info(self):
        self.faker.set_response_value(
            'disk_info',
            disk_info_successful_response(),
        )
        eq_(
            self.disk_api.disk_info(uid=TEST_UID),
            json.loads(disk_info_successful_response()),
        )

    def test_billing_subscriptions(self):
        self.faker.set_response_value(
            'billing_subscriptions',
            billing_subscriptions_successful_response(),
        )
        eq_(
            self.disk_api.billing_subscriptions(uid=TEST_UID, user_ip=TEST_IP),
            json.loads(billing_subscriptions_successful_response())['items'],
        )

    def test_plus_subscribe_success(self):
        self.faker.set_response_value(
            'plus_subscribe',
            plus_subscribe_created_response(),
            status=201,
        )
        assert_is_none(self.disk_api.plus_subscribe(uid=TEST_UID, partner_id=TEST_PLUS_PARTNER_ID, product_id=TEST_PLUS_PRODUCT_ID))

    def test_plus_subscribe_already_provided(self):
        self.faker.set_response_value(
            'plus_subscribe',
            plus_subscribe_already_provided_response(),
            status=409,
        )
        assert_is_none(self.disk_api.plus_subscribe(uid=TEST_UID, partner_id=TEST_PLUS_PARTNER_ID, product_id=TEST_PLUS_PRODUCT_ID))

    def test_plus_unsubscribe_success(self):
        self.faker.set_response_value(
            'plus_unsubscribe',
            plus_subscribe_removed_response(),
            status=204,
        )
        assert_is_none(self.disk_api.plus_unsubscribe(uid=TEST_UID, partner_id=TEST_PLUS_PARTNER_ID, product_id=TEST_PLUS_PRODUCT_ID))

    def test_plus_unsubscribe_already_unsubscribed(self):
        self.faker.set_response_value(
            'plus_unsubscribe',
            plus_subscription_not_found_response(),
            status=404,
        )
        assert_is_none(self.disk_api.plus_unsubscribe(uid=TEST_UID, partner_id=TEST_PLUS_PARTNER_ID, product_id=TEST_PLUS_PRODUCT_ID))
