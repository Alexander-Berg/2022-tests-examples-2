# -*- coding: utf-8 -*-

import unittest

from nose.tools import (
    eq_,
    ok_,
)
from passport.backend.api.settings import (
    captcha,
    settings,
)


# Этот тест проверяет консистентность языков в разных компонентах
class LanguagesTestCase(unittest.TestCase):

    def test_for_questions(self):
        eq_(set(settings.DISPLAY_LANGUAGES),
            set(settings.translations.QUESTIONS.keys()))
        eq_(set(settings.DISPLAY_LANGUAGES),
            set(settings.HINT_QUESTION_IDS_FOR_LANGUAGES.keys()))

    def test_for_sms(self):
        eq_(set(settings.DISPLAY_LANGUAGES), set(settings.translations.SMS.keys()))
