# -*- coding: utf-8 -*-
from django.test.utils import override_settings
from django.urls import reverse_lazy
from nose.tools import (
    assert_almost_equal,
    eq_,
    ok_,
)
from passport.backend.oauth.core.db.eav import UPDATE
from passport.backend.oauth.core.db.request import (
    CodeStrength,
    CodeType,
    Request,
)
from passport.backend.oauth.core.db.scope import Scope
from passport.backend.oauth.core.test.fake_configs import mock_scope_grant
from passport.backend.oauth.core.test.framework import ApiTestCase


TEST_DEFAULT_VERIFICATION_URL = 'https://ya.ru/device'
TEST_DEVICE_ID = 'device-id'
TEST_DEVICE_NAME = 'Device-Name'


@override_settings(
    DEFAULT_DEVICE_CODE_VERIFICATION_URL_TEMPLATE='https://yandex.%(tld)s/device',
    CUSTOM_DEVICE_CODE_VERIFICATION_URLS_BY_TLD={
        'ru': TEST_DEFAULT_VERIFICATION_URL,
    },
)
class IssueDeviceCodeTestCase(ApiTestCase):
    default_url = reverse_lazy('issue_device_code')
    http_method = 'POST'

    def default_params(self):
        return {
            'client_id': self.test_client.display_id,
        }

    def assert_error(self, rv, error, error_description=None, **kwargs):
        expected = dict(error=error, **kwargs)
        if error_description is not None:
            expected['error_description'] = error_description
        eq_(rv, expected)

    def assert_ok(self, rv, verification_url=TEST_DEFAULT_VERIFICATION_URL,
                  device_id=None, device_name=None, scopes=None,
                  code_type=CodeType.Unique, code_strength=CodeStrength.Medium):
        eq_(rv['verification_url'], verification_url)
        eq_(rv['interval'], 5)
        assert_almost_equal(rv['expires_in'], 300, delta=5)

        request = Request.by_display_id(display_id=rv['device_code'])
        eq_(request.code, rv['user_code'])
        eq_(request.code_type, code_type)
        eq_(request.code_strength, code_strength)
        eq_(request.client_id, self.test_client.id)
        ok_(not request.uid)
        ok_(not request.is_accepted)
        eq_(request.device_id, device_id or '')
        eq_(request.device_name, device_name or '')
        eq_(
            request.scopes,
            {Scope.by_keyword(kw) for kw in scopes} if scopes else self.test_client.scopes,
        )

        statbox_entry = {
            'mode': 'issue_device_code',
            'status': 'ok',
            'client_id': self.test_client.display_id,
            'token_request_id': request.display_id,
        }
        if device_id:
            statbox_entry.update(
                device_id=device_id,
                device_name=device_name,
            )
        self.check_statbox_entry(statbox_entry)

    def test_ok(self):
        rv = self.make_request()
        self.assert_ok(rv)

    def test_custom_ok(self):
        rv = self.make_request(
            headers={
                'HTTP_HOST': 'oauth.yandex.com',
            },
            device_id=TEST_DEVICE_ID,
            device_name=TEST_DEVICE_NAME,
            scope='test:foo',
        )
        self.assert_ok(
            rv,
            verification_url='https://yandex.com/device',
            device_id=TEST_DEVICE_ID,
            device_name=TEST_DEVICE_NAME,
            scopes=['test:foo'],
        )

    def test_client_bound_ok(self):
        rv = self.make_request(client_bound='yes')
        self.assert_ok(
            rv,
            verification_url='%s?client_id=%s' % (TEST_DEFAULT_VERIFICATION_URL, self.test_client.display_id),
            code_type=CodeType.ClientBound,
            code_strength=CodeStrength.BelowMedium,
        )

    def test_client_id_missing(self):
        rv = self.make_request(expected_status=400, exclude=['client_id'])
        self.assert_error(rv, error='invalid_request', error_description='client_id not in POST')

    def test_client_not_found(self):
        rv = self.make_request(client_id='foo', expected_status=400)
        self.assert_error(rv, error='invalid_client', error_description='Client not found')

    def test_client_blocked(self):
        with UPDATE(self.test_client) as client:
            client.block()
        rv = self.make_request(expected_status=400)
        self.assert_error(rv, error='invalid_client', error_description='Client blocked')

    def test_ok_with_counters(self):
        self.fake_kolmogor.set_response_value('get', '2')
        with override_settings(ENABLE_RATE_LIMITS=True, DEVICE_CODE_RATE_LIMIT_IP=2):
            rv = self.make_request()
        self.assert_ok(rv)
        eq_(len(self.fake_kolmogor.requests), 2)
        eq_(len(self.fake_kolmogor.get_requests_by_method('get')), 1)
        eq_(len(self.fake_kolmogor.get_requests_by_method('inc')), 1)

    def test_ok_with_disabled_counters(self):
        with override_settings(ENABLE_RATE_LIMITS=False):
            rv = self.make_request()
        self.assert_ok(rv)
        eq_(len(self.fake_kolmogor.requests), 0)

    def test_rate_limit_exceeded(self):
        self.fake_kolmogor.set_response_value('get', '3')
        with override_settings(ENABLE_RATE_LIMITS=True, DEVICE_CODE_RATE_LIMIT_IP=2):
            rv = self.make_request(expected_status=429)
        self.assert_error(
            rv,
            error='invalid_request',
            error_description='Too many requests',
        )
        eq_(len(self.fake_kolmogor.requests), 1)
        eq_(len(self.fake_kolmogor.get_requests_by_method('get')), 1)

    def test_grant_type_forbidden(self):
        self.fake_grants.set_data({
            'test:foo': mock_scope_grant(grant_types=[]),
        })
        rv = self.make_request(expected_status=400)
        self.assert_error(rv, error='unauthorized_client')
