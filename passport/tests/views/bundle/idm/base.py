# -*- coding: utf-8 -*-
import json

from nose.tools import eq_
from passport.backend.api.test.views import (
    BaseBundleTestViews,
    ViewsTestEnvironment,
)
from passport.backend.api.tests.views.bundle.test_base_data import (
    TEST_LOGIN,
    TEST_UID,
)
from passport.backend.api.views.bundle.idm.controllers import MAIL_ALTDOMAIN_ROLES
from passport.backend.core.builders.blackbox import BlackboxTemporaryError
from passport.backend.core.builders.blackbox.faker.blackbox import blackbox_userinfo_response
from passport.backend.core.dbmanager.exceptions import DBError
from passport.backend.core.test.test_utils.mock_objects import mock_grants
from passport.backend.core.test.test_utils.utils import (
    pseudo_diff,
    with_settings_hosts,
)


TEST_MAIL_ROLE_EXT = 'ext'

TEST_MAIL_ROLES_HIDING_YANDEX_EMAILS = [TEST_MAIL_ROLE_EXT]
TEST_MAIL_ROLES_SIMPLE = [
    role
    for role in MAIL_ALTDOMAIN_ROLES
    if role not in TEST_MAIL_ROLES_HIDING_YANDEX_EMAILS
]

TEST_ALTDOMAINS = {
    role_config.altdomain: domain_id
    for domain_id, role_config in enumerate(
        sorted(MAIL_ALTDOMAIN_ROLES.values(), key=lambda config: config.altdomain),
        start=1,
    )
}


def role_to_altdomain(role):
    return MAIL_ALTDOMAIN_ROLES[role].altdomain


def role_to_altdomain_id(role):
    return TEST_ALTDOMAINS[role_to_altdomain(role)]


TEST_ALTDOMAIN_EXT = role_to_altdomain(TEST_MAIL_ROLE_EXT)
TEST_ALTDOMAIN_ID_EXT = role_to_altdomain_id(TEST_MAIL_ROLE_EXT)


@with_settings_hosts(
    ALT_DOMAINS=TEST_ALTDOMAINS,
)
class BaseIDMTestCase(BaseBundleTestViews):
    def setUp(self):
        self.env = ViewsTestEnvironment()
        self.env.start()
        self.env.grants.set_grants_return_value(mock_grants(
            consumer='idm',
            grants={'idm': ['manage_roles']},
        ))
        self.setup_blackbox_response()

    def tearDown(self):
        self.env.stop()

    def setup_blackbox_response(self, uid=TEST_UID, enabled=True, has_role=False, altdomain=TEST_ALTDOMAIN_EXT):
        attributes = {
            'account.hide_yandex_domains_emails': str(int(has_role))
        }
        aliases = {
            'portal': TEST_LOGIN,
        }
        if has_role:
            aliases['altdomain'] = '%s@%s' % (TEST_LOGIN, altdomain)

        self.env.blackbox.set_blackbox_response_value(
            'userinfo',
            blackbox_userinfo_response(
                uid=uid,
                login=TEST_LOGIN,
                aliases=aliases,
                attributes=attributes,
                enabled=enabled,
            ),
        )

    def assert_ok_response(self, response, **expected_response):
        eq_(response.status_code, 200)

        expected_response['code'] = 0
        actual_response = json.loads(response.data)

        eq_(
            actual_response,
            expected_response,
            pseudo_diff(expected_response, actual_response),
        )

    def assert_error_response(self, response, error_code=400, **kwargs):
        eq_(response.status_code, 200)

        expected_response = dict(code=error_code, **kwargs)
        actual_response = json.loads(response.data)

        eq_(
            actual_response,
            expected_response,
            pseudo_diff(expected_response, actual_response),
        )

    def assert_historydb_empty(self):
        self.assert_events_are_logged(
            self.env.handle_mock,
            [],
        )


class CommonIDMTests(object):
    def test_no_grants(self):
        self.env.grants.set_grants_return_value(mock_grants(grants={}))
        rv = self.make_request()
        self.assert_error_response(
            rv,
            error_code=403,
            fatal=(
                'access.denied (Access denied for ip: 127.0.0.1; consumer: idm; tvm_client_id: None. '
                'Required grants: [\'idm.manage_roles\'])'
            ),
        )


class CommonIDMRoleTests(object):
    def test_role_invalid_error(self):
        rv = self.make_request(query_args=dict(role='{"smth": "unknown"}'))
        self.assert_error_response(
            rv,
            error_code=400,
            fatal='role.invalid',
        )

    def test_user_not_found(self):
        self.setup_blackbox_response(uid=None)
        rv = self.make_request()
        self.assert_error_response(
            rv,
            error_code=400,
            fatal='account.not_found',
        )

    def test_blackbox_temporary_error(self):
        self.env.blackbox.set_blackbox_response_side_effect(
            'userinfo',
            BlackboxTemporaryError,
        )
        rv = self.make_request()
        self.assert_error_response(
            rv,
            error_code=500,
            error='backend.blackbox_failed',
        )

    def test_db_temporary_error(self):
        self.env.db.set_side_effect_for_db('passportdbcentral', DBError)
        rv = self.make_request()
        self.assert_error_response(
            rv,
            error_code=500,
            error='backend.database_failed',
        )
