# -*- coding: utf-8 -*-
from nose.tools import (
    assert_false,
    eq_,
    ok_,
)
from passport.backend.oauth.core.db.acl import (
    is_action_enabled,
    services_to_admin,
)
from passport.backend.oauth.core.test.framework.testcases import DBTestCase


class TestACL(DBTestCase):
    def test_all_enabled(self):
        eq_(services_to_admin(uid=1), set(['test', 'lunapark', 'app_password', 'money']))
        ok_(is_action_enabled(uid=1, action='enter_admin'))
        ok_(is_action_enabled(uid=1, action='destroy_death_star'))

    def test_smth_enabled(self):
        eq_(services_to_admin(uid=2), set(['test']))
        ok_(is_action_enabled(uid=2, action='enter_admin'))
        assert_false(is_action_enabled(uid=2, action='destroy_death_star'))

    def test_all_disabled(self):
        eq_(services_to_admin(uid=3), set())
        assert_false(is_action_enabled(uid=3, action='enter_admin'))
        assert_false(is_action_enabled(uid=3, action='destroy_death_star'))
