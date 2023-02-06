# -*- coding: utf-8 -*-
import unittest

from nose.tools import eq_
from passport.backend.core.eav_type_mapping import ALIAS_NAME_TO_TYPE as ATT
from passport.backend.core.models.alias import AltDomainAlias
from passport.backend.core.undefined import Undefined


class TestAltDomainAlias(unittest.TestCase):
    def test_parse_from_string(self):
        alias = AltDomainAlias().parse({
            'aliases': {
                str(ATT['altdomain']): 'login.login@galatasaray.net',
            },
        })

        eq_(alias.login, 'login.login@galatasaray.net')
        eq_(alias.alias, '1/login-login')
        eq_(alias.domain_id, 1)
        eq_(alias.login_part, 'login-login')

    def test_parse_unknown_domain(self):
        alias = AltDomainAlias().parse({
            'aliases': {
                str(ATT['altdomain']): 'login.login@somedomain.ru',
            },
        })

        eq_(alias.login, 'login.login@somedomain.ru')
        eq_(alias.alias, Undefined)
        eq_(alias.domain_id, Undefined)
        eq_(alias.login_part, 'login-login')

    def test_empty(self):
        alias = AltDomainAlias().parse({})
        eq_(alias.login, Undefined)
        eq_(alias.alias, Undefined)
        eq_(alias.domain_id, Undefined)
        eq_(alias.login_part, Undefined)
        eq_(alias.serialized_alias, Undefined)
