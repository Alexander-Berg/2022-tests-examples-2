# -*- coding: utf-8 -*-
import unittest

from passport.backend.api.test.utils import check_bundle_form as check_form
from passport.backend.api.views.bundle.mdapi.forms import (
    PddAddDomainAliasForm,
    PddAddDomainForm,
    PddAliasToMasterForm,
    PddDeleteDomainAliasForm,
    PddDeleteDomainForm,
    PddEditDomainForm,
)


class TestForms(unittest.TestCase):
    def test_add_domain_form(self):
        invalid_params = [
            (
                {},
                ['domain.empty', 'admin_uid.empty'],
            ),
            (
                {'domain': '', 'admin_uid': ''},
                ['domain.empty', 'admin_uid.empty'],
            ),
            (
                {'domain': ' ', 'admin_uid': 'foo', 'mx': 'bar', 'enabled': 'zar'},
                ['domain.invalid', 'admin_uid.invalid', 'mx.invalid', 'enabled.invalid'],
            ),
        ]

        valid_params = [
            (
                {'domain': 'okna.ru', 'admin_uid': '1'},
                {'domain': 'okna.ru', 'admin_uid': 1, 'mx': False, 'enabled': True},
            ),
            (
                {'domain': u'ёлки.рф', 'admin_uid': '1', 'mx': 'true', 'enabled': 'no'},
                {'domain': u'ёлки.рф', 'admin_uid': 1, 'mx': True, 'enabled': False},
            ),
        ]

        check_form(PddAddDomainForm(), invalid_params, valid_params, None)

    def test_edit_domain_form(self):
        invalid_params = [
            (
                {},
                ['domain_id.empty'],
            ),
            (
                {'domain_id': ''},
                ['domain_id.empty'],
            ),
            (
                {'domain_id': 'foo'},
                ['domain_id.invalid'],
            ),
            (
                {'domain_id': str(2 ** 64), 'display_master_id': str(2 ** 64)},
                ['domain_id.invalid', 'display_master_id.invalid'],
            ),
            (
                {'domain_id': 1, 'display_master_id': 0},
                ['display_master_id.invalid'],
            ),
        ]

        valid_params = [
            (
                {
                    'domain_id': '1',
                },
                {
                    'domain_id': 1,
                    'admin_uid': None,
                    'mx': None,
                    'enabled': None,
                    'default': None,
                    'can_users_change_password': None,
                    'display_master_id': None,
                    'organization_name': None,
                    'glogouted': None,
                },
            ),
            (
                {
                    'domain_id': str(2 ** 62),
                    'admin_uid': '1',
                    'mx': 'true',
                    'enabled': 'false',
                    'default': 'no-reply',
                    'can_users_change_password': 'no',
                    'display_master_id': str(2 ** 62 - 1),
                    'organization_name': 'PDD',
                    'glogouted': 'true',
                },
                {
                    'domain_id': 2 ** 62,
                    'admin_uid': 1,
                    'mx': True,
                    'enabled': False,
                    'default': 'no-reply',
                    'can_users_change_password': False,
                    'display_master_id': 2 ** 62 - 1,
                    'organization_name': 'PDD',
                    'glogouted': True,
                },
            ),
            (
                {
                    'domain_id': '1',
                    'display_master_id': '',
                    'organization_name': '',
                },
                {
                    'domain_id': 1,
                    'admin_uid': None,
                    'mx': None,
                    'enabled': None,
                    'default': None,
                    'can_users_change_password': None,
                    'display_master_id': 0,
                    'organization_name': '',
                    'glogouted': None,
                },
            ),
        ]

        check_form(PddEditDomainForm(), invalid_params, valid_params, None)

    def test_delete_domain_form(self):
        invalid_params = [
            (
                {},
                ['domain_id.empty'],
            ),
            (
                {'domain_id': ''},
                ['domain_id.empty'],
            ),
            (
                {'domain_id': 'foo'},
                ['domain_id.invalid'],
            ),
            (
                {'domain_id': str(2 ** 64)},
                ['domain_id.invalid'],
            ),
        ]

        valid_params = [
            (
                {
                    'domain_id': '1',
                },
                {
                    'domain_id': 1,
                },
            ),
            (
                {
                    'domain_id': str(2 ** 62),
                },
                {
                    'domain_id': 2 ** 62,
                },
            ),
        ]

        check_form(PddDeleteDomainForm(), invalid_params, valid_params, None)

    def test_add_domain_alias_form(self):
        invalid_params = [
            (
                {},
                ['domain_id.empty', 'alias.empty'],
            ),
            (
                {'domain_id': '', 'alias': ''},
                ['domain_id.empty', 'alias.empty'],
            ),
            (
                {'domain_id': 'foo', 'alias': '_foo'},
                ['domain_id.invalid', 'alias.invalid'],
            ),
            (
                {'domain_id': str(2 ** 64), 'alias': 'okna.ru'},
                ['domain_id.invalid'],
            ),
        ]

        valid_params = [
            (
                {
                    'domain_id': '1',
                    'alias': 'okna.ru',
                },
                {
                    'domain_id': 1,
                    'alias': 'okna.ru',
                },
            ),
            (
                {
                    'domain_id': str(2 ** 62),
                    'alias': u'ёлки.рф',
                },
                {
                    'domain_id': 2 ** 62,
                    'alias': u'ёлки.рф',
                },
            ),
        ]

        check_form(PddAddDomainAliasForm(), invalid_params, valid_params, None)

    def test_delete_domain_alias_form(self):
        invalid_params = [
            (
                {},
                ['domain_id.empty', 'alias_id.empty'],
            ),
            (
                {'domain_id': '', 'alias_id': ''},
                ['domain_id.empty', 'alias_id.empty'],
            ),
            (
                {'domain_id': 'foo', 'alias_id': 'foo'},
                ['domain_id.invalid', 'alias_id.invalid'],
            ),
            (
                {'domain_id': str(2 ** 64), 'alias_id': str(2 ** 64)},
                ['domain_id.invalid', 'alias_id.invalid'],
            ),
        ]

        valid_params = [
            (
                {
                    'domain_id': '1',
                    'alias_id': '2',
                },
                {
                    'domain_id': 1,
                    'alias_id': 2,
                },
            ),
            (
                {
                    'domain_id': str(2 ** 62),
                    'alias_id': str(2 ** 62),
                },
                {
                    'domain_id': 2 ** 62,
                    'alias_id': 2 ** 62,
                },
            ),
        ]

        check_form(PddDeleteDomainAliasForm(), invalid_params, valid_params, None)

    def test_alias_to_master_form(self):
        invalid_params = [
            (
                {},
                ['domain_id.empty', 'alias_id.empty'],
            ),
            (
                {'domain_id': '', 'alias_id': ''},
                ['domain_id.empty', 'alias_id.empty'],
            ),
            (
                {'domain_id': 'foo', 'alias_id': 'foo'},
                ['domain_id.invalid', 'alias_id.invalid'],
            ),
            (
                {'domain_id': str(2 ** 64), 'alias_id': str(2 ** 64)},
                ['domain_id.invalid', 'alias_id.invalid'],
            ),
        ]

        valid_params = [
            (
                {
                    'domain_id': '1',
                    'alias_id': '2',
                },
                {
                    'domain_id': 1,
                    'alias_id': 2,
                },
            ),
            (
                {
                    'domain_id': str(2 ** 62),
                    'alias_id': str(2 ** 62),
                },
                {
                    'domain_id': 2 ** 62,
                    'alias_id': 2 ** 62,
                },
            ),
        ]

        check_form(PddAliasToMasterForm(), invalid_params, valid_params, None)
