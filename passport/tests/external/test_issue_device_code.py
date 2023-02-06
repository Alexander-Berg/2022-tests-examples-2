# -*- coding: utf-8 -*-
from django.test.utils import override_settings
from django.urls import reverse_lazy
import mock
from nose.tools import (
    assert_almost_equal,
    eq_,
    ok_,
)
from passport.backend.oauth.core.db.errors import VerificationCodeCollisionError
from passport.backend.oauth.core.db.request import (
    CodeStrength,
    Request,
)
from passport.backend.oauth.core.test.framework.testcases.bundle_api_testcase import BundleApiTestCase


TEST_DEFAULT_VERIFICATION_URL = 'https://ya.ru/device'


@override_settings(
    DEFAULT_DEVICE_CODE_VERIFICATION_URL_TEMPLATE='https://yandex.%(tld)s/device',
    CUSTOM_DEVICE_CODE_VERIFICATION_URLS_BY_TLD={
        'ru': TEST_DEFAULT_VERIFICATION_URL,
    },
)
class TestIssueDeviceCode(BundleApiTestCase):
    default_url = reverse_lazy('api_issue_device_code')
    http_method = 'POST'

    def default_params(self):
        return {
            'consumer': 'dev',
            'client_id': self.test_client.display_id,
            'code_strength': 'medium_with_crc',
        }

    def check_statbox(self, request_id, code_strength, **kwargs):
        entry = {
            'mode': 'issue_device_code',
            'status': 'ok',
            'client_id': self.test_client.display_id,
            'token_request_id': request_id,
            'code_strength': code_strength,
        }
        entry.update(kwargs)
        self.check_statbox_entries([
            entry,
        ])

    def test_ok(self):
        rv = self.make_request()
        self.assert_status_ok(rv)
        assert_almost_equal(rv['expires_in'], 300, delta=3)
        eq_(rv['verification_url'], '%s?client_id=%s' % (TEST_DEFAULT_VERIFICATION_URL, self.test_client.display_id))

        request = Request.by_verification_code(self.test_client.id, rv['user_code'])
        ok_(request is not None)
        eq_(request.display_id, rv['device_code'])
        eq_(request.code_strength, CodeStrength.MediumWithCRC)
        eq_(request.scopes, self.test_client.scopes)
        assert_almost_equal(request.ttl, rv['expires_in'], delta=3)
        ok_(not request.device_id)
        ok_(not request.device_name)

        self.check_statbox(request_id=request.display_id, code_strength='medium_with_crc')

    def test_ok_with_device_info(self):
        rv = self.make_request(code_strength='below_medium', device_id='deviceid', device_name='name')
        self.assert_status_ok(rv)
        assert_almost_equal(rv['expires_in'], 300, delta=3)
        eq_(rv['verification_url'], '%s?client_id=%s' % (TEST_DEFAULT_VERIFICATION_URL, self.test_client.display_id))

        request = Request.by_verification_code(self.test_client.id, rv['user_code'])
        ok_(request is not None)
        eq_(request.display_id, rv['device_code'])
        eq_(request.code_strength, CodeStrength.BelowMedium)
        eq_(request.scopes, self.test_client.scopes)
        assert_almost_equal(request.ttl, rv['expires_in'], delta=3)
        eq_(request.device_id, 'deviceid')
        eq_(request.device_name, 'name')

        self.check_statbox(
            request_id=request.display_id,
            code_strength='below_medium',
            device_id='deviceid',
            device_name='name',
        )

    def test_client_not_found(self):
        rv = self.make_request(client_id='a' * 32)
        self.assert_status_error(rv, ['client.not_found'])

    def test_verification_code_collizion_error(self):
        with mock.patch(
            'passport.backend.oauth.api.api.external.views.create_request',
            mock.Mock(side_effect=VerificationCodeCollisionError),
        ):
            rv = self.make_request()
            self.assert_status_error(rv, ['backend.failed'])
