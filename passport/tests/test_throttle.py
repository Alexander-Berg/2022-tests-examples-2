# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from passport.backend.social.common.exception import RateLimitExceededError as RateLimitExceededCommonError
from passport.backend.social.common.providers.Vkontakte import Vkontakte
from passport.backend.social.common.test.consts import (
    APPLICATION_ID1,
    APPLICATION_NAME1,
    CONSUMER1,
    CONSUMER_IP1,
    EXTERNAL_APPLICATION_ID1,
)
from passport.backend.social.common.web_service import Request
from passport.backend.social.proxy2.exception import RateLimitExceededError as RateLimitExceededProxyError
from passport.backend.social.proxy2.test import TestCase
from passport.backend.social.proxy2.views.v1.views import view


@view('get_profile', [])
def _view(context):
    return dict(status='ok')


class TestThrottle(TestCase):
    def setUp(self):
        super(TestThrottle, self).setUp()
        self._fake_grants_config.add_consumer(
            consumer=CONSUMER1,
            grants=['no-cred-use-token'],
            networks=[CONSUMER_IP1],
        )

    def build_settings(self):
        settings = super(TestThrottle, self).build_settings()
        settings['applications'] = [
            dict(
                provider_id=Vkontakte.id,
                application_id=APPLICATION_ID1,
                application_name=APPLICATION_NAME1,
                provider_client_id=EXTERNAL_APPLICATION_ID1,
            ),
        ]
        return settings

    def _call_view(self):
        request = Request.create(
            method='GET',
            consumer_ip=CONSUMER_IP1,
        )
        return _view(request, app_name=APPLICATION_NAME1)

    def test_limit_not_exceeded(self):
        rv = self._call_view()

        self.assertIn('result', rv)
        self.assertEqual(rv['result'], dict(status='ok'))

    def test_limit_exceeded(self):
        self._fake_throttle.set_response_value(RateLimitExceededCommonError('foo'))

        with self.assertRaises(RateLimitExceededProxyError) as assertion:
            self._call_view()

        self.assertEqual(assertion.exception.description, 'foo')
