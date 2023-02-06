# -*- coding: utf-8 -*-
import unittest

from nose.tools import (
    eq_,
    ok_,
)
from passport.backend.core.suggest.faker import FakeLoginSuggester
from passport.backend.core.suggest.login_suggester import LoginSuggester
from passport.backend.core.suggest.tests.test_data import (
    LANG_TO_MIXES,
    LETTER_TO_NUMBER_REPLACEMENTS,
    LETTER_TO_NUMBER_REPLACEMENTS_KEYS,
    PREFIX_WEIGHT,
    TEST_LOGIN_PREFIXES,
)
from passport.backend.core.test.test_utils import with_settings


@with_settings(
    LANG_TO_MIXES=LANG_TO_MIXES,
    LOGIN_PREFIXES=TEST_LOGIN_PREFIXES,
    PREFIX_WEIGHT=PREFIX_WEIGHT,
    LETTER_TO_NUMBER_REPLACEMENTS=LETTER_TO_NUMBER_REPLACEMENTS,
    LETTER_TO_NUMBER_REPLACEMENTS_KEYS=LETTER_TO_NUMBER_REPLACEMENTS_KEYS,
)
class TestFakeLoginSuggester(unittest.TestCase):
    def setUp(self):
        self.login_suggester = LoginSuggester()
        self.fake_login_suggester = FakeLoginSuggester()
        self.fake_login_suggester.start()

    def tearDown(self):
        self.fake_login_suggester.stop()
        del self.fake_login_suggester

    def test_names_cleaned(self):
        login_suggester = LoginSuggester(first_name=u'мисс', last_name=u'перегрин', login=u'ymbryne')
        ok_(not login_suggester.first_name)
        ok_(not login_suggester.last_name)
        ok_(not login_suggester.login)

        ok_(not self.login_suggester.clean(u'мисс'))
        ok_(not self.login_suggester.clean(u'перегрин'))
        ok_(not self.login_suggester.clean(u'ymbryne'))

    def test_setup_response(self):
        response = [[u'jake', u'emma'], [u'enoch', u'elephanta']]
        self.fake_login_suggester.setup_next_pack_side_effect(response)

        eq_(self.login_suggester.next_pack(), [u'jake', u'emma'])
        eq_(self.login_suggester.next_pack(), [u'enoch', u'elephanta'])

    def test_empty_response(self):
        self.fake_login_suggester.setup_next_pack_side_effect([[]])
        ok_(not self.login_suggester.next_pack())
