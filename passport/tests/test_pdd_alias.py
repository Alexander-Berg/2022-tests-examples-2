# -*- coding: utf-8 -*-
import unittest

from nose.tools import (
    assert_raises,
    eq_,
    ok_,
)
from passport.backend.core.eav_type_mapping import ALIAS_NAME_TO_TYPE as ATT
from passport.backend.core.models.account import Account
from passport.backend.core.models.alias import PddAlias
from passport.backend.core.models.domain import Domain
from passport.backend.core.undefined import Undefined


TEST_DOMAIN = 'okna.ru'
TEST_DOMAIN_ID = 1
TEST_LOGIN = 'login.login'
TEST_PDD_ALIAS = '@'.join([TEST_LOGIN, TEST_DOMAIN])
TEST_SERIALIZED_PDD_ALIAS = '%s/%s' % (TEST_DOMAIN_ID, TEST_LOGIN)
TEST_NONNORMALIZED_PDD_ALIAS = '@'.join([
    TEST_LOGIN.capitalize(),
    TEST_DOMAIN.upper(),
])


class TestPddAlias(unittest.TestCase):
    def setUp(self):
        self.account = Account()
        self.account.domain = Domain(
            id=TEST_DOMAIN_ID,
            domain=TEST_DOMAIN,
        )

    def test_parse(self):
        alias = PddAlias(self.account).parse({
            'aliases': {
                str(ATT['pdd']): TEST_PDD_ALIAS,
            },
        })

        eq_(alias.email, TEST_PDD_ALIAS)
        eq_(alias.alias, TEST_PDD_ALIAS)
        eq_(alias.serialized_alias, TEST_SERIALIZED_PDD_ALIAS)

    def test_normalize(self):
        alias = PddAlias(self.account).parse({
            'aliases': {
                str(ATT['pdd']): TEST_NONNORMALIZED_PDD_ALIAS,
            },
        })

        eq_(alias.email, TEST_NONNORMALIZED_PDD_ALIAS)
        eq_(alias.alias, TEST_NONNORMALIZED_PDD_ALIAS)
        eq_(alias.serialized_alias, '1/login.login')

    def test_parse_unknown_domain(self):
        account = Account()
        alias = PddAlias(account).parse({
            'aliases': {
                str(ATT['pdd']): TEST_PDD_ALIAS,
            },
        })
        eq_(alias.email, TEST_PDD_ALIAS)
        eq_(alias.alias, TEST_PDD_ALIAS)
        with assert_raises(ValueError):
            ok_(alias.serialized_alias)

    def test_empty(self):
        account = Account()
        alias = PddAlias(account).parse({})
        eq_(alias.email, Undefined)
        eq_(alias.alias, Undefined)
        eq_(alias.serialized_alias, Undefined)


class TestPddAditionalLogins(unittest.TestCase):
    def setUp(self):
        self.account = Account()
        self.account.domain = Domain(
            id=TEST_DOMAIN_ID,
            domain=TEST_DOMAIN,
        )
        self.account.pdd_alias = PddAlias(self.account).parse({
            'aliases': {
                str(ATT['pdd']): TEST_PDD_ALIAS,
            },
        })

    def test_parse_additional_logins(self):
        self.account.parse({
            'aliases': {
                str(ATT['pddalias']): [
                    'alias1@okna.ru',
                    'alias2@okna.ru',
                ],
            },
        })

        eq_(
            self.account.pdd_alias.additional_logins,
            {
                'alias1',
                'alias2',
            },
        )

    def test_parse_additional_logins_along_with_pdd_alias(self):
        account = Account()
        account.parse({
            'aliases': {
                str(ATT['pdd']): TEST_PDD_ALIAS,
                str(ATT['pddalias']): [
                    'alias1@okna.ru',
                    'alias2@okna.ru',
                ],
            },
        })
        eq_(
            account.pdd_alias.additional_logins,
            {
                'alias1',
                'alias2',
            },
        )

    def test_has_alias(self):
        account = Account()
        account.parse({
            'aliases': {
                str(ATT['pdd']): TEST_PDD_ALIAS,
                str(ATT['pddalias']): [
                    'alias1@okna.ru',
                    'alias2@okna.ru',
                ],
            },
        })
        ok_(not account.pdd_alias.has_login(TEST_PDD_ALIAS))
        for login in ('alias1', 'alias2', 'AliAs1'):
            ok_(account.pdd_alias.has_login(login))

    def test_remove_nonexistent_login(self):
        account = Account()
        account.parse({
            'aliases': {
                str(ATT['pdd']): TEST_PDD_ALIAS,
            },
        })

        with assert_raises(ValueError):
            account.pdd_alias.remove_login('something')

    def test_remove_unnormalized_login(self):
        account = Account()
        account.parse({
            'aliases': {
                str(ATT['pdd']): TEST_PDD_ALIAS,
                str(ATT['pddalias']): [
                    'alias1@okna.ru',
                    'alias2@okna.ru',
                ],
            },
        })

        account.pdd_alias.remove_login('AliaS1')
        ok_(not account.pdd_alias.has_login('alias1'))
