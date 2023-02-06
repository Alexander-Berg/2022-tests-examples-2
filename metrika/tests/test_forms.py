# -*- coding: utf-8 -*-
import unittest2
from nose.tools import (
    assert_raises,
    eq_,
)

from passport import validators
from passport.test.utils import with_settings

from clck_api.forms.long_url import ShortenForm


@with_settings(
    MAX_URL_LENGTH=100,
    YANDEX_TEAM_DOMAIN='yandex-team.ru',
)
class TestForms(unittest2.TestCase):

    def test_shorten_form(self):
        ok_url = 'http://test.com/abc'
        eq_(ShortenForm.to_python({'url': ok_url}, None), {'url': ok_url, 'json': False, 'type': None})

        long_url = 'http://test.com/{}'.format('a' * 100)
        with assert_raises(validators.Invalid):
            ShortenForm.to_python({'url': long_url}, None)
