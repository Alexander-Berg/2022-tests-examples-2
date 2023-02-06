# -*- coding: utf-8 -*-
import json

from nose.tools import (
    istest,
    ok_,
)
from passport.backend.core.builders.datasync_api import (
    DatasyncAccountInvalidTypeError,
    DatasyncApiObjectNotFoundError,
    DatasyncApiTemporaryError,
    DatasyncUserBlockedError,
)
from passport.backend.core.builders.datasync_api.faker.fake_disk_api import (
    billing_subscriptions_successful_response,
    disk_info_successful_response,
)
from passport.backend.core.test.test_utils.utils import with_settings_hosts

from .base import (
    BaseExternalDataTestCase,
    TEST_COOKIE_HEADERS,
    TEST_TOKEN_HEADERS,
    TEST_TVM_TICKET_OTHER,
    TEST_UID,
    TEST_USER_IP,
)


TEST_API_URL = 'https://disk.net'


@with_settings_hosts(
    DATASYNC_API_URL=TEST_API_URL,
)
class BaseDiskTestCase(BaseExternalDataTestCase):
    oauth_scope = 'cloud_api:disk.info'

    http_query_args = dict(
        consumer='dev',
    )

    def setUp(self):
        super(BaseDiskTestCase, self).setUp()
        self.setup_blackbox_responses(subscribed_to=[59])

    def test_not_subscribed_to_disk(self):
        self.setup_blackbox_responses(subscribed_to=[])

        rv = self.make_request(headers=TEST_TOKEN_HEADERS)
        self.assert_error_response(rv, ['disk.not_found'])
        ok_(not self.env.disk_api.requests)

    def test_account_cannot_use_disk(self):
        self.setup_blackbox_responses(aliases={'social': 'uid-xxx'})
        rv = self.make_request(headers=TEST_TOKEN_HEADERS)
        self.assert_error_response(rv, ['account.invalid_type'])


@istest
class DiskInfoTestCase(BaseDiskTestCase):
    default_url = '/1/bundle/account/external_data/disk/info/'

    def setUp(self):
        super(DiskInfoTestCase, self).setUp()
        self.env.disk_api.set_response_value(
            'disk_info',
            disk_info_successful_response(),
        )

    def test_ok_with_token(self):
        rv = self.make_request(headers=TEST_TOKEN_HEADERS)
        self.assert_ok_response(
            rv,
            **json.loads(disk_info_successful_response())
        )
        self.env.disk_api.requests[0].assert_properties_equal(
            method='GET',
            url='%s/v1/disk?fields=used_space,total_space,trash_size,is_paid' % TEST_API_URL,
            headers={
                'X-Ya-Service-Ticket': TEST_TVM_TICKET_OTHER,
                'X-Uid': str(TEST_UID),
            },
        )

    def test_ok_with_session(self):
        rv = self.make_request(headers=TEST_COOKIE_HEADERS)
        self.assert_ok_response(
            rv,
            **json.loads(disk_info_successful_response())
        )
        self.env.disk_api.requests[0].assert_properties_equal(
            method='GET',
            url='%s/v1/disk?fields=used_space,total_space,trash_size,is_paid' % TEST_API_URL,
            headers={
                'X-Ya-Service-Ticket': TEST_TVM_TICKET_OTHER,
                'X-Uid': str(TEST_UID),
            },
        )

    def test_disk_unavailable(self):
        self.env.disk_api.set_response_side_effect(
            'disk_info',
            DatasyncApiTemporaryError,
        )
        rv = self.make_request(headers=TEST_TOKEN_HEADERS)
        self.assert_error_response(rv, ['backend.datasync_api_failed'])

    def test_disk_permanent_error(self):
        self.env.disk_api.set_response_value(
            'disk_info',
            'Internal Server Error',
        )
        rv = self.make_request(headers=TEST_TOKEN_HEADERS)
        self.assert_error_response(rv, ['backend.datasync_api_failed'])

    def test_disk_missing(self):
        self.env.disk_api.set_response_side_effect(
            'disk_info',
            DatasyncApiObjectNotFoundError,
        )
        rv = self.make_request(headers=TEST_TOKEN_HEADERS)
        self.assert_error_response(rv, ['disk.not_found'])

    def test_account_invalid_type(self):
        self.env.disk_api.set_response_side_effect(
            'disk_info',
            DatasyncAccountInvalidTypeError,
        )
        rv = self.make_request(headers=TEST_TOKEN_HEADERS)
        self.assert_error_response(rv, ['account.invalid_type'])

    def test_user_blocked(self):
        self.env.disk_api.set_response_side_effect(
            'disk_info',
            DatasyncUserBlockedError,
        )
        rv = self.make_request(headers=TEST_TOKEN_HEADERS)
        self.assert_error_response(rv, ['account.invalid_type'])


@istest
class DiskSubscriptionsTestCase(BaseDiskTestCase):
    default_url = '/1/bundle/account/external_data/disk/subscriptions/'

    def setUp(self):
        super(DiskSubscriptionsTestCase, self).setUp()
        self.env.disk_api.set_response_value(
            'billing_subscriptions',
            billing_subscriptions_successful_response(),
        )

    def test_ok_with_token(self):
        rv = self.make_request(headers=TEST_TOKEN_HEADERS)
        self.assert_ok_response(
            rv,
            subscriptions=json.loads(billing_subscriptions_successful_response())['items'],
        )
        self.env.disk_api.requests[0].assert_properties_equal(
            method='GET',
            url='%s/v1/disk/billing/subscriptions?offset=0&limit=10' % TEST_API_URL,
            headers={
                'X-Ya-Service-Ticket': TEST_TVM_TICKET_OTHER,
                'X-Uid': str(TEST_UID),
                'X-Real-Ip': TEST_USER_IP,
            },
        )

    def test_ok_with_session_and_pagination(self):
        rv = self.make_request(query_args={'page': 3, 'page_size': 20}, headers=TEST_COOKIE_HEADERS)
        self.assert_ok_response(
            rv,
            subscriptions=json.loads(billing_subscriptions_successful_response())['items'],
        )
        self.env.disk_api.requests[0].assert_properties_equal(
            method='GET',
            url='%s/v1/disk/billing/subscriptions?offset=40&limit=20' % TEST_API_URL,
            headers={
                'X-Ya-Service-Ticket': TEST_TVM_TICKET_OTHER,
                'X-Uid': str(TEST_UID),
                'X-Real-Ip': TEST_USER_IP,
            },
        )

    def test_disk_unavailable(self):
        self.env.disk_api.set_response_side_effect(
            'billing_subscriptions',
            DatasyncApiTemporaryError,
        )
        rv = self.make_request(headers=TEST_TOKEN_HEADERS)
        self.assert_error_response(rv, ['backend.datasync_api_failed'])

    def test_subscriptions_missing(self):
        self.env.disk_api.set_response_side_effect(
            'billing_subscriptions',
            DatasyncApiObjectNotFoundError,
        )
        rv = self.make_request(headers=TEST_TOKEN_HEADERS)
        self.assert_ok_response(rv, subscriptions=[])
