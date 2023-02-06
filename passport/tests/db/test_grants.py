# -*- coding: utf-8 -*-
from nose.tools import (
    assert_raises,
    ok_,
)
from passport.backend.oauth.core.db.config.grants_config import (
    AccessDeniedError,
    get_grants,
    GrantsMissingError,
    TVMTicketInvalidError,
)
from passport.backend.oauth.core.test.base_test_data import TEST_TVM_TICKET
from passport.backend.oauth.core.test.framework.testcases import DBTestCase


class TestGrants(DBTestCase):
    def assert_ok(self, consumer, grant, ip='192.168.0.1', service_ticket=None):
        ok_(get_grants().has_grant(grant=grant, consumer=consumer, ip=ip, service_ticket=service_ticket))
        ok_(get_grants().check_grant(grant=grant, consumer=consumer, ip=ip, service_ticket=service_ticket) is None)

    def assert_error(self, consumer, grant, ip='192.168.0.1', service_ticket=None):
        ok_(not get_grants().has_grant(grant=grant, consumer=consumer, ip=ip, service_ticket=service_ticket))
        with assert_raises(GrantsMissingError):
            get_grants().check_grant(grant=grant, consumer=consumer, ip=ip, service_ticket=service_ticket)

    def test_deprecated_notation_error(self):
        with assert_raises(ValueError):
            get_grants().check_grant(consumer='intranet', grant='api:format_c', ip='192.168.0.1', service_ticket=None)

    def test_invalid_service_ticket_error(self):
        with assert_raises(TVMTicketInvalidError):
            get_grants().check_grant(consumer='intranet', grant='api.test', ip='192.168.0.1', service_ticket='foo')

    def test_ok_unlimited(self):
        self.assert_ok('intranet', 'api.format_c')

    def test_unknown_consumer(self):
        self.assert_error('unknown', 'api.unknown')

    def test_no_grant(self):
        self.assert_error('noname', 'api.unknown')

    def test_unknown_ip(self):
        self.assert_error('noname', 'api.test')

    def test_ok(self):
        self.assert_ok('noname', 'api.test', ip='8.8.8.8')

    def test_ok_with_not_required_service_ticket(self):
        self.assert_ok('dev', 'api.revoke_tokens', ip='8.8.8.8', service_ticket=TEST_TVM_TICKET)

    def test_ok_with_service_ticket(self):
        self.assert_ok('tvm_dev', 'api.revoke_tokens', ip='8.8.8.8', service_ticket=TEST_TVM_TICKET)

    def test_service_ticket_missing_error(self):
        self.assert_error('tvm_dev', 'api.revoke_tokens', ip='8.8.8.8')


class TestScopeGrants(DBTestCase):
    def assert_ok(self, scope, grant_type='password', client_id='a' * 32, ip='192.168.0.1'):
        ok_(
            get_grants().check_scope_grants(
                consumer=scope,
                grant_type=grant_type,
                client_id=client_id,
                ip=ip,
            ) is None,
        )

    def assert_error(self, scope, grant_type='password', client_id='a' * 32, ip='192.168.0.1'):
        assert_raises(AccessDeniedError, get_grants().check_scope_grants, scope, grant_type, client_id, ip)

    def test_unlimited_ok(self):
        for grant_type in ['authorization_code', 'password', 'x-token', 'sessionid', 'assertion']:
            for client_id in ['a' * 32, 'b' * 32, 'ccc']:
                for ip in ['192.168.0.1', '127.0.0.1', '8.8.8.8']:
                    self.assert_ok('test:unlimited', grant_type, client_id, ip)

    def test_no_limits_password_ok(self):
        self.assert_ok('test:foo')

    def test_unknown_scope_password_ok(self):
        self.assert_ok('test:do_smth_strange')

    def test_limited_by_password_ok(self):
        self.assert_ok('test:limited:grant_type:password')

    def test_limited_by_password_error(self):
        self.assert_error('test:limited:grant_type:password', grant_type='x-token')

    def test_limited_by_assertion_ok(self):
        self.assert_ok('test:limited:grant_type:assertion', grant_type='assertion')

    def test_limited_by_assertion_error(self):
        self.assert_error('test:limited:grant_type:assertion', grant_type='password')

    def test_no_limits_assertion_error(self):
        self.assert_error('test:foo', grant_type='assertion')

    def test_unknown_scope_assertion_error(self):
        self.assert_error('test:do_smth_strange', grant_type='assertion')

    def test_client_id_ok(self):
        self.assert_ok('test:limited:client')

    def test_client_id_error(self):
        self.assert_error('test:limited:client', client_id='b' * 32)

    def test_ip_ok(self):
        self.assert_ok('test:limited:ip', ip='192.168.0.1')
        self.assert_ok('test:limited:ip', ip='192.168.0.2')
        self.assert_ok('test:limited:ip', ip='192.168.0.255')
        self.assert_ok('test:limited:ip', ip='::ffff:127.0.0.1')
        self.assert_ok('test:limited:ip', ip='127.0.0.1')
        self.assert_ok('test:limited:ip', ip='::ffff:192.168.0.1')
        self.assert_ok('test:limited:ip', ip='fe80::fe7b:fcff:fe3c:8e01')

    def test_ip_error(self):
        self.assert_error('test:limited:ip', ip='8.8.8.8')
        self.assert_error('test:limited:ip', ip='192.168.1.1')
        self.assert_error('test:limited:ip', ip='127.0.0.2')
        self.assert_error('test:limited:ip', ip='::ffff:127.0.0.2')
        self.assert_error('test:limited:ip', ip='fe80::fe7b:fcff:fe3c:8e02')
