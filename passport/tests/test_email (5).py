# -*- coding: utf-8 -*-

import unittest

from nose.tools import (
    assert_raises,
    eq_,
)
from passport.backend.core import validators
from passport.backend.core.test.test_utils import with_settings


class TestSimpleEmailValidator(unittest.TestCase):
    def setUp(self):
        self.validator = validators.SimpleEmailValidator()

    def test_valid(self):
        valid_emails = (
            u'  a@b.cd  ',
            u'vasia@pupkin.subdomain.tld',
            u'вася@домен.рф',
            u'"вася@пупкин"@домен.рф',
            u'lo!gin@yandex.ru',
            u'lo-g_i234n@яндекс.рф',
            u'zzz@yandex.2.ru',
        )
        for email in valid_emails:
            eq_(self.validator.to_python(email), email.strip())

    def test_invalid(self):
        invalid_emails = (
            u'',
            None,
            {},
            [],
            100500,
            {'abcd@ef.ru'},
            u'  ',
            u'@b.c',
            u'a@',
            u'a b@c.d',
            u'ab@ c.d',
            u'zzz@yandex',
            u'zzz@yandex.',
            u'zzz@.yandex',
            u'q@.yandex.ru',
            u'w@yandex.ru.',
            u'zzz@yandex..ru',
        )
        for email in invalid_emails:
            assert_raises(validators.Invalid, self.validator.to_python, email)


class TestLooseEmailValidator(unittest.TestCase):
    def setUp(self):
        self.validator = validators.LooseEmailValidator()

    def test_valid(self):
        valid_emails = (
            u'login',
            u'  wrong--login\n',
            u'+79991234567',
            u'valid@email.com',
            u'captain@jack@sparrow.com',
        )
        for email in valid_emails:
            eq_(self.validator.to_python(email), email.strip())

    def test_invalid(self):
        invalid_emails = (
            u'',
            u'h@cker',
            u'foobar@',
        )
        for email in invalid_emails:
            assert_raises(validators.Invalid, self.validator.to_python, email)


class TestExternalEmailValidator(unittest.TestCase):
    def setUp(self):
        self.validator = validators.ExternalEmailValidator()

    def test_valid(self):
        valid_emails = (
            u'  a@b.cd  ',
            u'vasia@pupkin.subdomain.tld',
            u'вася@домен.рф',
            u'"вася@пупкин"@домен.рф',
            u'zzz@yandex.2.ru',
            u'captain@jack@sparrow.com',
        )
        for email in valid_emails:
            eq_(self.validator.to_python(email), email.strip())

    def test_invalid(self):
        invalid_emails = (
            u'',
            u'h@cker',
            u'foobar@',
            u'test@yandex.ru',
        )
        for email in invalid_emails:
            assert_raises(validators.Invalid, self.validator.to_python, email)


@with_settings(
    NATIVE_EMAIL_DOMAINS=[u'yandex.ru', u'яндекс.рф', u'yandex.com.tr'],
    ALLOW_NONASCII_IN_EMAILS=True,
)
class TestComprehensiveEmailValidator(unittest.TestCase):
    def setUp(self):
        self.validator = validators.ComprehensiveEmailValidator()

    def test_valid(self):
        valid_emails = (
            u'  a@b.cd  ',
            u'vasia@pupkin.subdomain.tld',
            u'вася@домен.рф',
            u'zzz@yandex.2.ru',
            u'test+test@gmail.com',
            u'"Vasya Poupkine"@example.com',
            # FIXME: Данный случай требует специального патча к python-pyisemail,
            # надо раскомментировать как только вмержим поддержку случая
            # "юникодные символы внутри кавычек в localpart".
            # u'"вася пупкин"@яндекс.рф'
            u'" "@example.com',
            u'!#$%&\'*+-/=?^_`{}|~@example.com',
        )
        for email in valid_emails:
            eq_(
                self.validator.to_python(email),
                email.strip(),
                email,
            )

    def test_invalid(self):
        invalid_emails = (
            u'',
            u'h@cker',
            u'foobar@',
            u'каённ>ый>@перец.рф',
            u'a@a@a.ru',
            u'@gmail.com',
            u'much.“more\\ unusual”@example.com',
            u'very.unusual.“@”.unusual.com@example.com',
            u'very.“(),:;<>[]”.VERY.“very@\\ "very”.unusual@strange.example.com',
            u'“(),:;<>[\\]@example.com',
            u'just"not"right@example.com',
            u'this\\ is"really"not\allowed@example.com',
        )
        for email in invalid_emails:
            assert_raises(validators.Invalid, self.validator.to_python, email)

    def test_native_rejected(self):
        validator = validators.ComprehensiveEmailValidator(allow_native=False)

        valid_emails = (
            u'test@gmail.com',
            u'вася@домен.рф',
            u'zzz@yandex.2.ru',
        )
        invalid_emails = (
            u'test@YaNdEx.rU',
            u'тест@ЯНДекс.РФ',
            u'test@yandex.ru',
            u'test@yandex.com.tr',
            u'тест@яндекс.рф',
        )

        for email in invalid_emails:
            assert_raises(validators.Invalid, validator.to_python, email)

        for email in valid_emails:
            eq_(
                validator.to_python(email),
                email.strip(),
                email,
            )

    def test_bad_domains_rejected(self):
        validator = validators.ComprehensiveEmailValidator(max_domain_level=2, blacklisted_domains=['evil.com'])

        valid_emails = (
            u'test@gmail.com',
            u'вася@домен.рф',
            u'zzz@good.ru',
            u'zzz@good.com.tr',
        )
        invalid_emails = (
            u'test@some.long.domain.ru',
            u'тест@evil.com',
            u'test@EvIl.CoM',
        )

        for email in invalid_emails:
            assert_raises(validators.Invalid, validator.to_python, email)

        for email in valid_emails:
            eq_(
                validator.to_python(email),
                email.strip(),
                email,
            )


@with_settings(
    NATIVE_EMAIL_DOMAINS=[u'yandex.ru', u'яндекс.рф'],
    ALLOW_NONASCII_IN_EMAILS=False,
)
class TestNonAsciiEmailsOption(unittest.TestCase):
    def test_nonascii_only(self):
        validator = validators.ComprehensiveEmailValidator(ascii_only=True)

        valid_emails = (
            u'test@gmail.com',
            u'!#$%&\'*+-/=?^_`{}|~@example.com',
            u'zzz@yandex.2.ru',
        )
        invalid_emails = (
            u'привет@мир123.рф',
            'волож@яндекс.рф',
            u'testЫ@style.ru',
        )

        for email in invalid_emails:
            assert_raises(validators.Invalid, validator.to_python, email)

        for email in valid_emails:
            eq_(
                validator.to_python(email),
                email.strip(),
                email,
            )
