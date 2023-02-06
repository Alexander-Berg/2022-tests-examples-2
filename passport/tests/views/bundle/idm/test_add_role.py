# -*- coding: utf-8 -*-
import json

from nose_parameterized import parameterized
from passport.backend.api.tests.views.bundle.idm.base import (
    BaseIDMTestCase,
    CommonIDMRoleTests,
    CommonIDMTests,
    role_to_altdomain,
    role_to_altdomain_id,
    TEST_ALTDOMAIN_ID_EXT,
    TEST_LOGIN,
    TEST_MAIL_ROLE_EXT,
    TEST_MAIL_ROLES_SIMPLE,
)


class IDMAddRoleTestCase(BaseIDMTestCase, CommonIDMTests, CommonIDMRoleTests):
    default_url = '/1/bundle/idm/add-role/'
    http_method = 'POST'
    http_query_args = {
        'login': TEST_LOGIN,
        'role': json.dumps({'mail': TEST_MAIL_ROLE_EXT}),
    }

    def assert_historydb_ok(self, altdomain_id=TEST_ALTDOMAIN_ID_EXT, hide_yandex=True):
        entries = {
            'alias.altdomain.add': '%s/%s' % (altdomain_id, TEST_LOGIN),
            'action': 'add_role',
            'consumer': 'idm',
        }
        if hide_yandex:
            entries['info.hide_yandex_domains_emails'] = '1'
        self.assert_events_are_logged(
            self.env.handle_mock,
            entries,
        )

    def test_mail_ext_ok(self):
        rv = self.make_request()
        self.assert_ok_response(rv)
        self.assert_historydb_ok()

    @parameterized.expand([
        (role, )
        for role in TEST_MAIL_ROLES_SIMPLE
    ])
    def test_simple_mail_roles_ok(self, role):
        rv = self.make_request(query_args={'role': json.dumps({'mail': role})})
        self.assert_ok_response(rv)
        self.assert_historydb_ok(altdomain_id=role_to_altdomain_id(role), hide_yandex=False)

    def test_has_role_ok(self):
        self.setup_blackbox_response(has_role=True)
        rv = self.make_request()
        self.assert_ok_response(rv)
        self.assert_historydb_empty()

    def test_has_other_altdomain_alias_error(self):
        self.setup_blackbox_response(has_role=True, altdomain=role_to_altdomain(TEST_MAIL_ROLES_SIMPLE[0]))
        rv = self.make_request()
        self.assert_error_response(rv, error_code=400, fatal='altdomain_alias.exists')
        self.assert_historydb_empty()

    def test_user_disabled_error(self):
        self.setup_blackbox_response(enabled=False)
        rv = self.make_request()
        self.assert_error_response(
            rv,
            error_code=400,
            fatal='account.disabled',
        )
