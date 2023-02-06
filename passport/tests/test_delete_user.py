# -*- coding: utf-8 -*-

from passport.backend.social.api.test import ApiV2TestCase
from passport.backend.social.common.profile import ProfileCreator
from passport.backend.social.common.test.consts import (
    CONSUMER1,
    CONSUMER_IP1,
    SIMPLE_USERID1,
    UID1,
)
from passport.backend.social.common.test.fake_billing_api import (
    billing_api_invalidate_account_bindings_response,
    FakeBillingApi,
)


class TestDeleteUser(ApiV2TestCase):
    REQUEST_HTTP_METHOD = 'DELETE'
    REQUEST_URL = '/api/user/' + str(UID1)
    REQUEST_QUERY = {
        'consumer': CONSUMER1,
    }
    REQUEST_HEADERS = {
        'X-Real-Ip': CONSUMER_IP1,
    }

    def setUp(self):
        super(TestDeleteUser, self).setUp()
        self._fake_billing = FakeBillingApi()
        self._fake_billing.start()

    def tearDown(self):
        self._fake_billing.stop()
        del self._fake_billing
        super(TestDeleteUser, self).tearDown()

    def build_settings(self):
        settings = super(TestDeleteUser, self).build_settings()
        settings['social_config'].update(
            billing_http_api_retries=1,
            billing_http_api_service_token='billing_service_token',
            billing_http_api_timeout=1,
            billing_http_api_url='https://trust',
            invalidate_billing_binding_cache=True,
        )
        return settings

    def test_phonish_profile(self):
        profile_info = dict(
            provider=dict(code='ya'),
            userid=SIMPLE_USERID1,
        )
        creator = ProfileCreator(
            self._fake_db.get_engine(),
            self._fake_db.get_engine(),
            UID1,
            profile_info,
            token=None,
            timestamp=None,
        )
        creator.create()

        self._fake_grants_config.add_consumer(
            CONSUMER1,
            networks=[CONSUMER_IP1],
            grants=['user-delete'],
        )

        self._fake_billing.set_response_side_effect(
            'invalidate_account_bindings',
            [
                billing_api_invalidate_account_bindings_response(),
            ],
        )

        rv = self._make_request()

        self.assertEqual(rv.status_code, 200)
        self.assertEqual(rv.data, '')
