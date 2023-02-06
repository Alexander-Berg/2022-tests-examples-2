# -*- coding: utf-8 -*-

from unittest import TestCase

from nose.tools import (
    assert_raises,
    eq_,
)
from passport.backend.adm_api.common.exceptions import (
    AccessDeniedError,
    InternalError,
)
from passport.backend.adm_api.common.grants import GrantsLoader
from passport.backend.adm_api.test.grants import FakeGrantsLoader
from passport.backend.adm_api.test.mock_objects import mock_grants
from passport.backend.adm_api.test.utils import with_settings
from passport.backend.core.test.time_utils.time_utils import TimeNow


@with_settings()
class GrantsLoaderTestCase(TestCase):

    def setUp(self):
        self.grants_loader = FakeGrantsLoader()
        self.grants_loader.set_grants_json(mock_grants())

        self.grants_loader.start()

    def tearDown(self):
        self.grants_loader.stop()

    def test_cannot_load_grants_no_file(self):
        self.grants_loader.set_grants_side_effect(IOError)

        with assert_raises(InternalError):
            GrantsLoader()

    def test_cannot_load_grants_after_success(self):
        grants = GrantsLoader()
        self.grants_loader.set_grants_side_effect(ValueError)
        grants._load_roles()
        eq_(grants.roles, mock_grants())

    def test_load_grants_ok(self):
        grants = GrantsLoader()

        eq_(grants.roles, mock_grants())
        eq_(grants.update_time, TimeNow())
        eq_(
            grants.grant_name_to_id,
            {
                'allow_search': 1,
                'show_person': 4,
                'show_history': 5,
                'show_hint_answer': 7,
                'allow_phone_search': 2,
                'show_emails': 9,
                'show_phones': 8,
                'allow_restoration_link_create': 21,
                'show_restoration_form': 22,

                'allow_meltingpot_user_add': 31,
                'show_meltingpot_users': 32,
                'show_meltingpot_statistics': 33,
                'show_meltingpot_group': 34,
                'allow_meltingpot_group': 35,
                'show_meltingpot_schedule': 36,
                'allow_meltingpot_schedule': 37,
                'set_public_id': 38,
                'remove_public_id': 39,
                'remove_all_public_id': 40,
                'set_is_verified': 41,
                'phonish.disable_auth': 42,
                'set_takeout_subscription': 43,
                'set_sms_2fa': 44,
            },
        )
        eq_(
            grants.grant_id_to_name,
            {
                1: 'allow_search',
                2: 'allow_phone_search',
                4: 'show_person',
                5: 'show_history',
                7: 'show_hint_answer',
                8: 'show_phones',
                9: 'show_emails',
                21: 'allow_restoration_link_create',
                22: 'show_restoration_form',

                31: 'allow_meltingpot_user_add',
                32: 'show_meltingpot_users',
                33: 'show_meltingpot_statistics',
                34: 'show_meltingpot_group',
                35: 'allow_meltingpot_group',
                36: 'show_meltingpot_schedule',
                37: 'allow_meltingpot_schedule',
                38: 'set_public_id',
                39: 'remove_public_id',
                40: 'remove_all_public_id',
                41: 'set_is_verified',
                42: 'phonish.disable_auth',
                43: 'set_takeout_subscription',
                44: 'set_sms_2fa',
            },
        )
        eq_(
            grants.login_to_grant_ids,
            {
                'admin': {1, 2, 4, 5, 7, 8, 9, 21, 22, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44},
                'lite_support': {1},
                'support': {1, 4, 5, 8, 9, 22},
                'looser': set(),
            },
        )

    def test_check_grants_ok(self):
        grants = GrantsLoader()

        grants.check_grants('admin', {1, 2})

    def test_check_grants_access_denied(self):
        grants = GrantsLoader()

        with assert_raises(AccessDeniedError):
            grants.check_grants('support', {1, 7})

    def test_check_grants_with_unknown_login(self):
        grants = GrantsLoader()

        grants.check_grants('some_user', set())

    def test_update_roles_after_timeout(self):
        grants = GrantsLoader()
        grants.update_time = 0
        self.grants_loader.set_grants_json(mock_grants(users=[]))
        with assert_raises(AccessDeniedError):
            # информация о пользователях должна исчезнуть
            grants.check_grants('admin', {1, 2})

    def test_grants_to_ids(self):
        grants = GrantsLoader()
        eq_(
            grants.grants_to_ids(['show_hint_answer', 'allow_phone_search']),
            {2, 7},
        )
