# -*- coding: utf-8 -*
from django.test.utils import override_settings
from django.urls import reverse
from nose.tools import (
    eq_,
    ok_,
)
from nose_parameterized import parameterized
from passport.backend.oauth.core.test.base_test_data import (
    TEST_LOGIN,
    TEST_UID,
)
from passport.backend.oauth.core.test.framework import ApiTestCase


class ACLTestcase(ApiTestCase):
    def setUp(self):
        super(ACLTestcase, self).setUp()
        self.fake_login_to_uid_mapping.set_data({TEST_LOGIN: TEST_UID})

    @override_settings(YAUTH_TEST_USER=False)
    def _run_test_not_logged_in(self, url):
        response = self.client.get(url)
        eq_(response.status_code, 302, response.content.decode())
        ok_('passport' in response['location'])

    def _run_test_grant_missing(self, url, grants):
        for grant in grants:
            selected_grants = [
                'action:enter_admin',
                'action:view_clients',
                'action:edit_clients',
                'action:create_scopes',
                'service:*',
            ]
            selected_grants.remove(grant)
            self.fake_acl.set_data({
                TEST_LOGIN: selected_grants,
            })
            response = self.client.get(url)
            eq_(response.status_code, 403, response.content.decode())
            eq_(
                response.content.decode(),
                'У вас (uid=%d) нет гранта %s для доступа к данному разделу' % (
                    TEST_UID,
                    grant.replace('action:', ''),
                ),
            )

    def _run_test_ok(self, url, grants):
        if grants:
            self.fake_acl.set_data({
                TEST_LOGIN: grants + ('service:*', ),
            })
        response = self.client.get(url)
        eq_(response.status_code, 200, response.content.decode())

    @parameterized.expand([
        (
            'view_clients',
            ['production'],
            ('action:enter_admin', 'action:view_clients', ),
        ),
        (
            'edit_client',
            ['production', '<client_id>'],
            ('action:enter_admin', 'action:view_clients', ),
        ),
        (
            'new_scope',
            ['production'],
            ('action:enter_admin', 'action:create_scopes', ),
        ),
        (
            'index',
            ['production'],
            ('action:enter_admin', ),
        ),
    ])
    def test_acl(self, url_name, args, grants):
        args = [
            self.test_client.display_id if arg == '<client_id>' else arg
            for arg in args
        ]
        url = reverse(url_name, args=args)

        self._run_test_not_logged_in(url)
        self._run_test_grant_missing(url, grants)
        self._run_test_ok(url, grants)
