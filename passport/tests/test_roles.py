# coding: utf-8

import unittest

from passport.backend.vault.utils.roles import (
    format_role,
    RoleAction,
)


class TestRolesFormatter(unittest.TestCase):
    def test_format_role_ok(self):
        test_data = [
            [dict(role_slug='owner', uid=100, login='user_1'), 'owner:user:user_1'],
            [dict(role_slug='owner', uid=100), 'owner:user:100'],
            [dict(role_slug='owner', abc_id=123), 'owner:abc:123'],
            [dict(role_slug='owner', staff_id=456, staff_slug='staff_slug'), 'owner:staff:staff_slug'],
            [dict(role_slug='owner', abc_id=123, abc_slug='abc_slug'), 'owner:abc:abc_slug'],
            [dict(role_slug='owner', abc_id=123, abc_name='abc_name'), 'owner:abc:123 (abc_name)'],
            [dict(role_slug='owner', abc_id=123, abc_scope='development'), 'owner:abc:123:scope:development'],
            [
                dict(
                    role_slug='owner',
                    abc_id=123, abc_scope='development', abc_name=u'Паспорт....', abc_scope_name=u'Разработка',
                ),
                u'owner:abc:123:scope:development (Паспорт. Scope: Разработка)',
            ],
            [
                dict(
                    role_slug='owner',
                    abc_id=123, abc_role='630', abc_name=u'Паспорт....', abc_role_name=u'TVM менеджер',
                ),
                u'owner:abc:123:role:630 (Паспорт. Role: TVM менеджер)',
            ],
            [dict(role_slug='owner', staff_id=456, staff_slug='staff_slug'), 'owner:staff:staff_slug'],
            [
                dict(role_slug='owner', staff_id=456, staff_slug='staff_slug', staff_name=u'Разработка Морды'),
                u'owner:staff:staff_slug (Разработка Морды)',
            ],
            [dict(role_slug='owner'), 'owner:unknown:unknown'],
        ]
        for row in test_data:
            self.assertEqual(format_role(row[0]), row[1])


class TestRoleAction(unittest.TestCase):
    def test_parse_valid_roles(self):
        test_data = [
            ['owner:user_1', '+owner:user:user_1'],
            ['owner:user:user_1', '+owner:user:user_1'],
            ['-owner:user_1', '-owner:user:user_1'],
            ['-owner:user:user_1', '-owner:user:user_1'],
            ['owner:abc:123', '+owner:abc:123'],
            ['-owner:abc:123', '-owner:abc:123'],
            ['owner:staff:345', '+owner:staff:345'],
            ['-owner:staff:345', '-owner:staff:345'],
            ['reader:user_1', '+reader:user:user_1'],
            ['reader:user:user_1', '+reader:user:user_1'],
            ['-reader:user_1', '-reader:user:user_1'],
            ['-reader:user:user_1', '-reader:user:user_1'],
            ['reader:abc:123', '+reader:abc:123'],
            ['-reader:abc:123', '-reader:abc:123'],
            ['reader:abc:123:development', '+reader:abc:123:scope:development'],
            ['-reader:abc:123:administration', '-reader:abc:123:scope:administration'],
            ['reader:abc:123:scope:development', '+reader:abc:123:scope:development'],
            ['-reader:abc:123:scope:administration', '-reader:abc:123:scope:administration'],
            ['reader:abc:123:role:630', '+reader:abc:123:role:630'],
            ['-reader:abc:123:role:16', '-reader:abc:123:role:16'],
            ['reader:staff:345', '+reader:staff:345'],
            ['-reader:staff:345', '-reader:staff:345'],
            ['appender:user_1', '+appender:user:user_1'],
            ['appender:abc:123:development', '+appender:abc:123:scope:development'],
            ['appender:staff:345', '+appender:staff:345'],
            ['-appender:staff:345', '-appender:staff:345'],
        ]
        for row in test_data:
            self.assertEqual(
                str(RoleAction.from_string(row[0])),
                row[1],
            )

    def test_parse_invalid_roles(self):
        test_data = [
            ('', '', '', ''),
            ('unknown', 'owner', 'user', '100'),
            ('assign', 'unknown', 'user', '100'),
            ('assign', 'reader', 'unknown', '100'),
            ('assign', 'reader', 'user', ''),
            ('assign', 'reader', 'abc', None, 'role_name'),
        ]
        for row in test_data:
            with self.assertRaises(ValueError):
                RoleAction(*row)

        with self.assertRaises(ValueError):
            RoleAction.from_string('owner:')

    def test_action_role_magick_methods(self):
        role_action = RoleAction('assign', 'owner', 'user', 'user_1')
        self.assertEqual(str(role_action), '+owner:user:user_1')
        self.assertEqual(repr(role_action), '<RoleAction("assign", "owner", "user", "user_1")>')

        role_action.scope = 'test_scope'
        self.assertEqual(repr(role_action), '<RoleAction("assign", "owner", "user", "user_1", scope="test_scope")>')

        role_action.scope = None
        role_action.role_id = '630'
        self.assertEqual(repr(role_action), '<RoleAction("assign", "owner", "user", "user_1", role_id="630")>')

    def test_role_action_as_method_params(self):
        test_data = [
            ['owner:user:user_1', dict(login='user_1')],
            ['owner:user:100', dict(uid='100')],
            ['owner:staff:123', dict(staff_id='123')],
            ['owner:abc:456', dict(abc_id='456')],
            ['owner:abc:456:administration', dict(abc_id='456', abc_scope='administration')],
            ['owner:abc:456:scope:administration', dict(abc_id='456', abc_scope='administration')],
            ['owner:abc:passp:scope:administration', dict(abc_id='passp', abc_scope='administration')],
            ['owner:abc:456:role:630', dict(abc_id='456', abc_role_id='630')],
            ['owner:abc:passp:role:630', dict(abc_id='passp', abc_role_id='630')],
        ]
        for row in test_data:
            self.assertDictEqual(
                RoleAction.from_string(row[0]).as_method_params(),
                row[1],
            )
