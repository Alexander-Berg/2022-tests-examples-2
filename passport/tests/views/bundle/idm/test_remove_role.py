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
from passport.backend.api.views.bundle.idm.controllers import MAIL_ALTDOMAIN_ROLES


class IDMRemoveRoleTestCase(BaseIDMTestCase, CommonIDMTests, CommonIDMRoleTests):
    default_url = '/1/bundle/idm/remove-role/'
    http_method = 'POST'
    http_query_args = {
        'login': TEST_LOGIN,
        'role': json.dumps({'mail': TEST_MAIL_ROLE_EXT}),
    }

    def setup_blackbox_response(self, has_role=True, **kwargs):
        super(IDMRemoveRoleTestCase, self).setup_blackbox_response(has_role=has_role, **kwargs)

    def assert_historydb_ok(self, altdomain_id=TEST_ALTDOMAIN_ID_EXT, alias_removed=True):
        entries = {
            'info.hide_yandex_domains_emails': '0',
            'action': 'remove_role',
            'consumer': 'idm',
        }
        if alias_removed:
            entries['alias.altdomain.rm'] = '%s/%s' % (altdomain_id, TEST_LOGIN)
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
        self.setup_blackbox_response(altdomain=MAIL_ALTDOMAIN_ROLES[role].altdomain)
        rv = self.make_request(query_args={'role': json.dumps({'mail': role})})
        self.assert_ok_response(rv)
        self.assert_historydb_ok(altdomain_id=role_to_altdomain_id(role))

    def test_user_disabled_ok(self):
        self.setup_blackbox_response(enabled=False)
        rv = self.make_request()
        self.assert_ok_response(rv)
        self.assert_historydb_ok()

    def test_has_no_role_ok(self):
        self.setup_blackbox_response(has_role=False)
        rv = self.make_request()
        self.assert_ok_response(rv)
        self.assert_historydb_empty()

    def test_has_other_altdomain_alias_ok(self):
        other_role = TEST_MAIL_ROLES_SIMPLE[0]
        self.setup_blackbox_response(has_role=True, altdomain=role_to_altdomain(other_role))
        rv = self.make_request()
        self.assert_ok_response(rv)
        self.assert_historydb_ok(alias_removed=False)
