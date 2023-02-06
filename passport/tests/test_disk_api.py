# -*- coding: utf-8 -*-
import json
import unittest

import mock
from nose.tools import (
    assert_raises,
    eq_,
)
from passport.backend.core.builders.datasync_api import DiskApi
from passport.backend.core.builders.datasync_api.exceptions import (
    DatasyncAccountInvalidTypeError,
    DatasyncApiAuthorizationInvalidError,
    DatasyncApiObjectNotFoundError,
    DatasyncApiPermanentError,
    DatasyncApiTemporaryError,
    DatasyncUserBlockedError,
    DatasyncUserNotFound,
)
from passport.backend.core.builders.datasync_api.faker.fake_disk_api import (
    billing_subscriptions_successful_response,
    disk_error_response,
    disk_info_successful_response,
    FakeDiskApi,
    plus_subscribe_already_provided_response,
    plus_subscribe_created_response,
    plus_subscribe_removed_response,
    plus_subscription_not_found_response,
)
from passport.backend.core.test.test_utils import with_settings
from passport.backend.core.tvm.faker.fake_tvm_credentials_manager import (
    fake_tvm_credentials_data,
    FakeTvmCredentialsManager,
    TEST_CLIENT_ID_2,
    TEST_TICKET,
)


TEST_UID = 123
TEST_IP = '1.2.3.4'
TEST_PLUS_PARTNER_ID = 'yandex_plus'
TEST_PLUS_PRODUCT_ID = 'yandex_plus_10gb'


@with_settings(
    DATASYNC_API_URL='http://localhost/',
    DATASYNC_API_TIMEOUT=0.5,
    DATASYNC_API_RETRIES=2,
)
class TestDiskApiCommon(unittest.TestCase):
    def setUp(self):
        self.disk_api = DiskApi(tvm_credentials_manager=mock.Mock())
        self.disk_api.useragent = mock.Mock()

        self.response = mock.Mock()
        self.disk_api.useragent.request.return_value = self.response
        self.disk_api.useragent.request_error_class = self.disk_api.temporary_error_class
        self.response.content = json.dumps({})
        self.response.status_code = 200

    def tearDown(self):
        del self.disk_api
        del self.response

    def test_failed_to_parse_response(self):
        self.response.status_code = 200
        self.response.content = 'not a json'
        with assert_raises(DatasyncApiPermanentError):
            self.disk_api.disk_info(uid=TEST_UID)

    def test_internal_server_error(self):
        self.response.status_code = 500
        self.response.content = disk_error_response('InternalServerError')
        with assert_raises(DatasyncApiTemporaryError):
            self.disk_api.disk_info(uid=TEST_UID)

    def test_server_error(self):
        self.response.status_code = 503
        self.response.content = disk_error_response('ServerError')
        with assert_raises(DatasyncApiPermanentError):
            self.disk_api.disk_info(uid=TEST_UID)

    def test_service_unavailable(self):
        self.response.status_code = 503
        self.response.content = disk_error_response('DiskServiceUnavailableError')
        with assert_raises(DatasyncApiTemporaryError):
            self.disk_api.disk_info(uid=TEST_UID)

    def test_bad_status_code(self):
        self.response.status_code = 418
        self.response.content = disk_error_response('IAmATeapot')
        with assert_raises(DatasyncApiPermanentError):
            self.disk_api.disk_info(uid=TEST_UID)

    def test_oauth_token_invalid_error(self):
        self.response.status_code = 403
        self.response.content = disk_error_response('UnauthorizedError')
        with assert_raises(DatasyncApiAuthorizationInvalidError):
            self.disk_api.disk_info(uid=TEST_UID)

    def test_account_invalid_type_error(self):
        self.response.status_code = 403
        self.response.content = disk_error_response('DiskUnsupportedUserAccountTypeError')
        with assert_raises(DatasyncAccountInvalidTypeError):
            self.disk_api.disk_info(uid=TEST_UID)

    def test_user_blocked_error(self):
        self.response.status_code = 403
        self.response.content = disk_error_response('DiskUserBlockedError')
        with assert_raises(DatasyncUserBlockedError):
            self.disk_api.disk_info(uid=TEST_UID)

    def test_user_not_found_error(self):
        self.response.status_code = 403
        self.response.content = disk_error_response('UserNotFoundInPassportError')
        with assert_raises(DatasyncUserNotFound):
            self.disk_api.disk_info(uid=TEST_UID)


@with_settings(
    DATASYNC_API_URL='http://localhost/',
    DATASYNC_API_TIMEOUT=0.5,
    DATASYNC_API_RETRIES=2,
)
class TestDiskApiMethods(unittest.TestCase):
    def setUp(self):
        self.fake_disk_api = FakeDiskApi()
        self.fake_disk_api.start()
        self.fake_tvm_credentials_manager = FakeTvmCredentialsManager()
        self.fake_tvm_credentials_manager.set_data(fake_tvm_credentials_data(
            ticket_data={
                str(TEST_CLIENT_ID_2): {
                    'alias': 'datasync_api',
                    'ticket': TEST_TICKET,
                },
            },
        ))
        self.fake_tvm_credentials_manager.start()
        self.disk_api = DiskApi()

    def tearDown(self):
        self.fake_tvm_credentials_manager.stop()
        self.fake_disk_api.stop()
        del self.fake_tvm_credentials_manager
        del self.fake_disk_api

    def test_disk_info_ok(self):
        self.fake_disk_api.set_response_value(
            'disk_info',
            disk_info_successful_response(),
        )
        response = self.disk_api.disk_info(uid=TEST_UID)
        eq_(
            response,
            json.loads(disk_info_successful_response()),
        )
        eq_(len(self.fake_disk_api.requests), 1)
        self.fake_disk_api.requests[0].assert_url_starts_with('http://localhost/v1/disk')
        self.fake_disk_api.requests[0].assert_query_equals({
            'fields': 'used_space,total_space,trash_size,is_paid',
        })
        self.fake_disk_api.requests[0].assert_headers_contain({
            'X-Ya-Service-Ticket': TEST_TICKET,
            'X-Uid': str(TEST_UID),
        })

    def test_disk_info_custom_fields_ok(self):
        self.fake_disk_api.set_response_value(
            'disk_info',
            disk_info_successful_response(),
        )
        response = self.disk_api.disk_info(uid=TEST_UID, fields=['total_space'])
        eq_(
            response,
            json.loads(disk_info_successful_response()),
        )
        eq_(len(self.fake_disk_api.requests), 1)
        self.fake_disk_api.requests[0].assert_url_starts_with('http://localhost/v1/disk')
        self.fake_disk_api.requests[0].assert_query_equals({
            'fields': 'total_space',
        })
        self.fake_disk_api.requests[0].assert_headers_contain({
            'X-Ya-Service-Ticket': TEST_TICKET,
            'X-Uid': str(TEST_UID),
        })

    def test_billing_subscriptions_ok(self):
        self.fake_disk_api.set_response_value(
            'billing_subscriptions',
            billing_subscriptions_successful_response(),
        )
        response = self.disk_api.billing_subscriptions(uid=TEST_UID, user_ip=TEST_IP)
        eq_(
            response,
            json.loads(billing_subscriptions_successful_response())['items'],
        )
        eq_(len(self.fake_disk_api.requests), 1)
        self.fake_disk_api.requests[0].assert_url_starts_with('http://localhost/v1/disk/billing/subscriptions')
        self.fake_disk_api.requests[0].assert_query_equals({
            'offset': '0',
            'limit': '100',
        })
        self.fake_disk_api.requests[0].assert_headers_contain({
            'X-Ya-Service-Ticket': TEST_TICKET,
            'X-Uid': str(TEST_UID),
            'X-Real-Ip': TEST_IP,
        })

    def test_billing_subscriptions_with_pagination_ok(self):
        self.fake_disk_api.set_response_value(
            'billing_subscriptions',
            billing_subscriptions_successful_response(),
        )
        response = self.disk_api.billing_subscriptions(uid=TEST_UID, user_ip=TEST_IP, offset=20, limit=10)
        eq_(
            response,
            json.loads(billing_subscriptions_successful_response())['items'],
        )
        eq_(len(self.fake_disk_api.requests), 1)
        self.fake_disk_api.requests[0].assert_url_starts_with('http://localhost/v1/disk/billing/subscriptions')
        self.fake_disk_api.requests[0].assert_query_equals({
            'offset': '20',
            'limit': '10',
        })
        self.fake_disk_api.requests[0].assert_headers_contain({
            'X-Ya-Service-Ticket': TEST_TICKET,
            'X-Uid': str(TEST_UID),
            'X-Real-Ip': TEST_IP,
        })

    def test_billing_subscriptions_not_found_ok(self):
        self.fake_disk_api.set_response_side_effect(
            'billing_subscriptions',
            DatasyncApiObjectNotFoundError,
        )
        response = self.disk_api.billing_subscriptions(uid=TEST_UID, user_ip=TEST_IP)
        eq_(
            response,
            [],
        )

    def test_billing_subscriptions_bad_response_ok(self):
        self.fake_disk_api.set_response_value(
            'billing_subscriptions',
            '{}',
        )
        response = self.disk_api.billing_subscriptions(uid=TEST_UID, user_ip=TEST_IP)
        eq_(
            response,
            [],
        )

    def test_plus_subscribe_201_ok(self):
        self.fake_disk_api.set_response_value(
            'plus_subscribe',
            plus_subscribe_created_response(),
            status=201,
        )
        self.disk_api.plus_subscribe(uid=TEST_UID, partner_id=TEST_PLUS_PARTNER_ID, product_id=TEST_PLUS_PRODUCT_ID)
        eq_(len(self.fake_disk_api.requests), 1)
        self.fake_disk_api.requests[0].assert_properties_equal(
            url='http://localhost/v1/disk/partners/yandex_plus/services?product_id=yandex_plus_10gb',
            method='POST',
        )
        self.fake_disk_api.requests[0].assert_headers_contain({
            'X-Ya-Service-Ticket': TEST_TICKET,
            'X-Uid': str(TEST_UID),
        })

    def test_plus_subscribe_409_ok(self):
        self.fake_disk_api.set_response_value(
            'plus_subscribe',
            plus_subscribe_already_provided_response(),
            status=409,
        )
        self.disk_api.plus_subscribe(uid=TEST_UID, partner_id=TEST_PLUS_PARTNER_ID, product_id=TEST_PLUS_PRODUCT_ID)
        eq_(len(self.fake_disk_api.requests), 1)
        self.fake_disk_api.requests[0].assert_properties_equal(
            url='http://localhost/v1/disk/partners/yandex_plus/services?product_id=yandex_plus_10gb',
            method='POST',
        )
        self.fake_disk_api.requests[0].assert_headers_contain({
            'X-Ya-Service-Ticket': TEST_TICKET,
            'X-Uid': str(TEST_UID),
        })

    def test_plus_unsubscribe_204_ok(self):
        self.fake_disk_api.set_response_value(
            'plus_unsubscribe',
            plus_subscribe_removed_response(),
            status=204,
        )
        self.disk_api.plus_unsubscribe(uid=TEST_UID, partner_id=TEST_PLUS_PARTNER_ID, product_id=TEST_PLUS_PRODUCT_ID)
        eq_(len(self.fake_disk_api.requests), 1)
        self.fake_disk_api.requests[0].assert_properties_equal(
            url='http://localhost/v1/disk/partners/yandex_plus/services/remove_by_product?product_id=yandex_plus_10gb',
            method='DELETE',
        )
        self.fake_disk_api.requests[0].assert_headers_contain({
            'X-Ya-Service-Ticket': TEST_TICKET,
            'X-Uid': str(TEST_UID),
        })

    def test_plus_unsubscribe_404_ok(self):
        self.fake_disk_api.set_response_value(
            'plus_unsubscribe',
            plus_subscription_not_found_response(),
            status=404,
        )
        self.disk_api.plus_unsubscribe(uid=TEST_UID, partner_id=TEST_PLUS_PARTNER_ID, product_id=TEST_PLUS_PRODUCT_ID)
        eq_(len(self.fake_disk_api.requests), 1)
        self.fake_disk_api.requests[0].assert_properties_equal(
            url='http://localhost/v1/disk/partners/yandex_plus/services/remove_by_product?product_id=yandex_plus_10gb',
            method='DELETE',
        )
        self.fake_disk_api.requests[0].assert_headers_contain({
            'X-Ya-Service-Ticket': TEST_TICKET,
            'X-Uid': str(TEST_UID),
        })
