# -*- coding: utf-8 -*-

import unittest

from passport.backend.core.test.test_utils import with_settings
from passport.backend.core.test.test_utils.form_utils import (
    check_equality,
    check_raise_error,
)
from passport.backend.core.validators.language import (
    CaptchaDisplayLanguage,
    ConfirmationEmailLanguage,
    DetectedLanguage,
    DisplayLanguage,
    PortalLanguage,
)


@with_settings(PORTAL_LANGUAGES=['en'])
class TestPortalLanguage(unittest.TestCase):
    def test_portal_language(self):
        valid_languages = ['EN']

        for valid_language in valid_languages:
            check_equality(PortalLanguage(), (valid_language, valid_language.lower()))

        invalid_languages = ['ru', '123', '', '     ', 'ru    ']

        for invalid_language in invalid_languages:
            check_raise_error(PortalLanguage(), invalid_language)


@with_settings(DISPLAY_LANGUAGES=['ru', 'tr', 'uk'])
class TestDisplayLanguage(unittest.TestCase):

    def test_questions_language(self):
        valid_languages = ['ru', 'tr', 'uk']

        for valid_language in valid_languages:
            check_equality(DisplayLanguage(), (valid_language, valid_language))

        invalid_languages = ['', 'en', 'kz', '   en', '     ']

        for invalid_language in invalid_languages:
            check_raise_error(DisplayLanguage(), invalid_language)


@with_settings(
    DISPLAY_LANGUAGES=['ru', 'tr', 'uk', 'es'],
    ALL_SUPPORTED_LANGUAGES={
        'all': ['ru', 'en', 'uk', 'zh'],
        'default': 'ru',
    },
)
class TestDetectedLanguage(unittest.TestCase):

    def test_validator(self):
        valid_languages = ['ru', 'tr', 'uk', 'Es']

        for valid_language in valid_languages:
            check_equality(DetectedLanguage(), (valid_language, valid_language.lower()))

        to_default_languages = ['en', 'kz', '   en', 'zh']

        for invalid_language in to_default_languages:
            check_equality(DetectedLanguage(), (invalid_language, 'ru'))

        check_raise_error(DetectedLanguage(), '')


@with_settings(DISPLAY_LANGUAGES=['ru', 'tr'])
class TestCaptchaDisplayLanguage(unittest.TestCase):

    def test_questions_language(self):
        valid_languages = ['ru', 'tr']

        for valid_language in valid_languages:
            check_equality(CaptchaDisplayLanguage(), (valid_language, valid_language))

        unsupported_languages = ['en', 'kz', 'uk   ', '   en']

        for unsupported_language in unsupported_languages:
            check_equality(CaptchaDisplayLanguage(), (unsupported_language, ''))


@with_settings(EMAIL_VALIDATOR_EMAIL_LANGUAGES=['ru', 'tr', 'en'])
class TestConfirmationEmailLanguage(unittest.TestCase):

    def test_confirmation_email_language(self):
        valid_languages = ['ru', 'tr', 'en']

        for valid_language in valid_languages:
            check_equality(ConfirmationEmailLanguage(), (valid_language, valid_language))

        unsupported_languages = ['', 'kz', 'bz   ', '   rz', '     ']

        for unsupported_language in unsupported_languages:
            check_raise_error(ConfirmationEmailLanguage(), unsupported_language)
