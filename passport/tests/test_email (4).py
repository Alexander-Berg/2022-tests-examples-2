# -*- coding: utf-8 -*-

from copy import copy
from datetime import datetime
import unittest

from nose.tools import (
    assert_is_none,
    eq_,
    ok_,
)
from passport.backend.core.test.test_utils import with_settings
from passport.backend.core.test.time_utils.time_utils import DatetimeNow
from passport.backend.core.types.email.email import (
    build_emails,
    domain_from_email,
    Email,
    Emails,
    get_default_native_emails,
    is_yandex_email,
    mask_email_for_challenge,
    mask_email_for_statbox,
    normalize_email_with_phonenumber,
    punycode_email,
    unicode_email,
)
from passport.backend.utils.common import merge_dicts
from six import iteritems


class TestEmail(unittest.TestCase):
    def setUp(self):
        self.email = Email(
            is_native=True,
            is_confirmed=False,
            is_rpop=False,
            is_unsafe=False,
            is_default=False,
            is_silent=False,
            creation_datetime=datetime.now(),
            address='test@yandex.ru',
        )

    def test_basic_email(self):
        ok_(self.email.is_native)
        ok_(not self.email.is_external)
        ok_(not self.email.is_default)
        ok_(not self.email.is_confirmed)
        ok_(not self.email.is_rpop)
        ok_(not self.email.is_unsafe)
        ok_(not self.email.is_silent)
        ok_(not self.email.is_suitable_for_restore)
        eq_(self.email.creation_datetime, DatetimeNow())

        eq_(self.email.address, 'test@yandex.ru')
        eq_(self.email.username, 'test')
        eq_(self.email.domain, 'yandex.ru')

    def test_domain_email(self):
        eq_(self.email.address, 'test@yandex.ru')
        eq_(self.email.domain, 'yandex.ru')

    def test_str(self):
        eq_(str(self.email), 'test@yandex.ru')

    def test_repr(self):
        ok_(repr(self.email))

    def test_eq_ne(self):
        ok_(self.email, self.email)
        not_equal_email = Email(
            is_native=True,
            is_confirmed=True,
            is_rpop=False,
            is_unsafe=False,
            is_default=False,
            is_silent=False,
            creation_datetime=datetime.now(),
            address='test@yandex.ru',
        )
        equal_email = copy(self.email)
        equal_email_without_creation_datetime = copy(self.email)
        equal_email_without_creation_datetime.creation_datetime = None

        not_equal_email_without_creation_datetime = copy(not_equal_email)
        not_equal_email_without_creation_datetime.creation_datetime = None

        ok_(not self.email == not_equal_email)
        ok_(not self.email == 123456)
        ok_(self.email == equal_email)
        ok_(not self.email != equal_email)
        ok_(self.email != not_equal_email)

        ok_(self.email == equal_email_without_creation_datetime)
        ok_(not self.email != equal_email_without_creation_datetime)

        ok_(not self.email == not_equal_email_without_creation_datetime)
        ok_(self.email != not_equal_email_without_creation_datetime)

    def test_without_creation_datetime(self):
        email = Email(
            is_native=True,
            is_confirmed=True,
            is_rpop=False,
            is_unsafe=False,
            is_default=False,
            is_silent=False,
            address='test@yandex.ru',
        )

        ok_(email.is_native)
        ok_(not email.is_external)
        ok_(not email.is_default)
        ok_(email.is_confirmed)
        ok_(not email.is_rpop)
        ok_(not email.is_unsafe)

        eq_(email.address, 'test@yandex.ru')
        eq_(email.username, 'test')
        eq_(email.domain, 'yandex.ru')
        assert_is_none(email.creation_datetime)


class TestEmails(unittest.TestCase):
    def test_empty_emails(self):
        emails = Emails()
        assert_is_none(emails.default)
        eq_(emails._emails, dict())
        eq_(emails.native, [])
        eq_(emails.external, [])
        eq_(emails.confirmed_external, [])
        eq_(list(emails), [])

    def test_add_and_find_email(self):
        emails = Emails()
        email = Email(
            is_native=True,
            is_confirmed=False,
            is_rpop=False,
            is_unsafe=False,
            is_default=True,
            is_silent=False,
            creation_datetime=datetime.now(),
            address='test@yandex.ru',
        )

        emails.add(email)

        eq_(len(emails._emails), 1)
        eq_(emails.default, email)
        eq_(emails.find('test@yandex.ru'), email)
        eq_(list(emails), [email])

    def test_native_emails(self):
        emails = Emails()

        confirmed_internal_email = Email(
            is_native=True,
            is_confirmed=True,
            is_rpop=False,
            is_unsafe=False,
            is_default=True,
            is_silent=False,
            creation_datetime=datetime.now(),
            address='test1@yandex.ru',
        )
        unconfirmed_external_email = Email(
            is_native=False,
            is_confirmed=False,
            is_rpop=False,
            is_unsafe=False,
            is_default=False,
            is_silent=False,
            creation_datetime=datetime.now(),
            address='test3@yandex.ru',
        )
        for email in [confirmed_internal_email,
                      unconfirmed_external_email]:
            emails.add(email)

        eq_(len(emails._emails), 2)
        eq_(emails.native, [confirmed_internal_email])
        eq_(list(emails), [confirmed_internal_email, unconfirmed_external_email])

    def test_external_emails(self):
        emails = Emails()

        confirmed_external_email = Email(
            is_native=False,
            is_confirmed=True,
            is_rpop=False,
            is_unsafe=False,
            is_default=True,
            is_silent=False,
            creation_datetime=datetime.now(),
            address='test2@yandex.ru',
        )
        unconfirmed_external_email = Email(
            is_native=False,
            is_confirmed=False,
            is_rpop=False,
            is_unsafe=False,
            is_default=False,
            is_silent=False,
            creation_datetime=datetime.now(),
            address='test3@yandex.ru',
        )
        for email in [confirmed_external_email,
                      unconfirmed_external_email]:
            emails.add(email)

        eq_(len(emails._emails), 2)
        eq_(emails.default, confirmed_external_email)

        eq_(sorted(emails.external), sorted([unconfirmed_external_email, confirmed_external_email]))

    def test_external_confirmed_emails(self):
        emails = Emails()

        confirmed_external_email = Email(
            is_native=False,
            is_confirmed=True,
            is_rpop=False,
            is_unsafe=False,
            is_default=True,
            is_silent=False,
            creation_datetime=datetime.now(),
            address='test2@yandex.ru',
        )
        unconfirmed_external_email = Email(
            is_native=False,
            is_confirmed=False,
            is_rpop=False,
            is_unsafe=False,
            is_default=False,
            is_silent=False,
            creation_datetime=datetime.now(),
            address='test3@yandex.ru',
        )
        for email in [confirmed_external_email,
                      unconfirmed_external_email]:
            emails.add(email)

        eq_(len(emails._emails), 2)
        eq_(emails.default, confirmed_external_email)

        eq_(emails.confirmed_external, [confirmed_external_email])

    def test_empty_external_confirmed_emails(self):
        emails = Emails()

        confirmed_internal_email = Email(
            is_native=True,
            is_confirmed=True,
            is_rpop=False,
            is_unsafe=False,
            is_default=True,
            is_silent=False,
            creation_datetime=datetime.now(),
            address='test1@yandex.ru',
        )

        unconfirmed_external_email = Email(
            is_native=False,
            is_confirmed=False,
            is_rpop=False,
            is_unsafe=False,
            is_default=False,
            is_silent=False,
            creation_datetime=datetime.now(),
            address='test3@yandex.ru',
        )

        for email in [confirmed_internal_email,
                      unconfirmed_external_email]:
            emails.add(email)

        eq_(len(emails._emails), 2)
        eq_(emails.confirmed_external, [])

    def test_suitable_for_restore_emails(self):
        emails = Emails()

        confirmed_internal_email = Email(
            is_native=True,
            is_confirmed=True,
            is_rpop=False,
            is_unsafe=False,
            is_default=True,
            is_silent=False,
            creation_datetime=datetime.now(),
            address='test1@yandex.ru',
        )
        unconfirmed_external_email = Email(
            is_native=False,
            is_confirmed=False,
            is_rpop=False,
            is_unsafe=False,
            is_default=False,
            is_silent=False,
            creation_datetime=datetime.now(),
            address='test2@yandex.ru',
        )
        confirmed_external_unsafe_email = Email(
            is_native=False,
            is_confirmed=True,
            is_rpop=False,
            is_unsafe=True,
            is_default=False,
            is_silent=False,
            creation_datetime=datetime.now(),
            address='test3@yandex.ru',
        )
        confirmed_external_rpop_email = Email(
            is_native=False,
            is_confirmed=True,
            is_rpop=True,
            is_unsafe=False,
            is_default=False,
            is_silent=False,
            creation_datetime=datetime.now(),
            address='test4@yandex.ru',
        )
        confirmed_external_silent_email = Email(
            is_native=False,
            is_confirmed=True,
            is_rpop=False,
            is_unsafe=False,
            is_default=False,
            is_silent=True,
            creation_datetime=datetime.now(),
            address='test_silent@yandex.ru',
        )
        suitable_for_restore_email = Email(
            is_native=False,
            is_confirmed=True,
            is_rpop=False,
            is_unsafe=False,
            is_default=False,
            is_silent=False,
            creation_datetime=datetime.now(),
            address='test5@yandex.ru',
        )

        for email in [
            confirmed_internal_email,
            unconfirmed_external_email,
            confirmed_external_unsafe_email,
            confirmed_external_rpop_email,
            confirmed_external_silent_email,
            suitable_for_restore_email,
        ]:
            emails.add(email)

        eq_(len(emails._emails), 6)
        eq_(
            sorted(emails.confirmed_external),
            sorted([
                confirmed_external_silent_email,
                confirmed_external_unsafe_email,
                suitable_for_restore_email,
                confirmed_external_rpop_email,
            ]),
        )
        eq_(
            sorted(emails.suitable_for_restore),
            sorted([suitable_for_restore_email]),
        )
        ok_(suitable_for_restore_email.is_suitable_for_restore)
        for email in [
            confirmed_internal_email,
            unconfirmed_external_email,
            confirmed_external_unsafe_email,
            confirmed_external_rpop_email,
            confirmed_external_silent_email,
        ]:
            ok_(not email.is_suitable_for_restore)


class TestBuildEmails(unittest.TestCase):
    def setUp(self):
        self.value = {
            'default': False,
            'prohibit-restore': False,
            'validated': False,
            'native': False,
            'rpop': False,
            'unsafe': False,
            'silent': False,
            'address': 'test@yandex.ru',
        }

    def test_build_empty_list(self):
        emails = build_emails([])
        eq_(len(emails._emails), 0)

    def test_build_all_fields_in_address(self):
        emails = build_emails((self.value,))

        eq_(len(emails._emails), 1)

        email = emails.find('test@yandex.ru')

        ok_(not email.is_default)
        ok_(not email.is_confirmed)
        ok_(not email.is_native)
        ok_(email.is_external)
        ok_(not email.is_rpop)
        ok_(not email.is_unsafe)
        ok_(not email.is_silent)
        eq_(email.address, 'test@yandex.ru')
        eq_(email.username, 'test')
        eq_(email.domain, 'yandex.ru')

    def test_native_email(self):
        value = merge_dicts(self.value, {'native': True})
        emails = build_emails((value,))

        eq_(len(emails._emails), 1)

        email = emails.find('test@yandex.ru')

        ok_(email.is_native)
        ok_(not email.is_external)

    def test_silent_email(self):
        value = merge_dicts(self.value, {'silent': True})
        emails = build_emails((value,))

        eq_(len(emails._emails), 1)

        email = emails.find('test@yandex.ru')

        ok_(email.is_silent)

    def test_suitable_for_restore_email(self):
        value = merge_dicts(self.value, {'validated': True})
        emails = build_emails((value,))

        eq_(len(emails._emails), 1)

        email = emails.find('test@yandex.ru')

        ok_(email.is_suitable_for_restore)


def test_domain_from_email():
    test_map = [
        ('foo@bar', 'bar'),
        ('123foo@bar.com', 'bar.com'),
        ('foo@bar-baz.com', 'bar-baz.com'),
        ('foo@bar.baz.com', 'bar.baz.com'),
        (u'foo@окна.рф', u'окна.рф'),
        (u'foo@xn--80atjc.xn--p1ai', u'xn--80atjc.xn--p1ai'),
    ]
    for actual, expected in test_map:
        eq_(domain_from_email(actual), expected)


def test_punycode_email():
    test_map = [
        ('foo@bar', 'foo@bar'),
        ('123@foo@bar.com', '123@foo@bar.com'),
        (u'foo@окна.рф', u'foo@xn--80atjc.xn--p1ai'),
        (u'ок@на@окна.рф', u'ок@на@xn--80atjc.xn--p1ai'),
        (u'foo@xn--80atjc.xn--p1ai', u'foo@xn--80atjc.xn--p1ai'),
        (u'foo@' + 'd' * 100 + '.ru', u'foo@' + 'd' * 100 + '.ru'),  # кодирование в idna вызывает UnicodeError
    ]
    for email, expected in test_map:
        eq_(punycode_email(email), expected)


def test_unicode_email():
    test_map = [
        ('foo@bar', u'foo@bar'),
        ('123@foo@bar.com', u'123@foo@bar.com'),
        ('foo@xn--80atjc.xn--p1ai', u'foo@окна.рф'),
        (u'ок@на@xn--80atjc.xn--p1ai', u'ок@на@окна.рф'),
        (u'foo@окна.рф', u'foo@окна.рф'),  # декодирование из idna вызывает UnicodeError
        ('окна@xn--80atjc.xn--p1ai', u'окна@окна.рф'),
    ]
    for email, expected in test_map:
        eq_(unicode_email(email), expected)


def test_normalize_email_with_phonenumber():
    test_map = [
        ('login', 'login', None),
        ('login@yandex.ru', 'login@yandex.ru', None),
        (u'login.login@яндекс.рф', u'login-login@яндекс.рф', None),
        (u'логин.логин@яндекс.рф', u'логин-логин@яндекс.рф', None),
        ('xyz100500200@google.ru', 'xyz100500200@google.ru', None),
        ('89121234567@domain.ru', '89121234567@domain.ru', None),
        ('+79121234567@domain.ru', '79121234567@domain.ru', None),
        ('89121234567@domain.ru', '79121234567@domain.ru', 'RU'),
        ('(912)1234567@domain.ru', '79121234567@domain.ru', 'RU'),
        ('3801234567@domain.ru', '3801234567@domain.ru', 'UA'),
        ('+(375)152450911@domain.ru', '375152450911@domain.ru', None),
        ('+700099999999@zzz.ru', '+700099999999@zzz.ru', 'RU'),
    ]
    for email, expected, country in test_map:
        eq_(normalize_email_with_phonenumber(email, country), expected)


def test_mask_for_statbox():
    values = (
        ('bad-email', 'bad-*****'),
        ('a@yandex.ru', '*****@yandex.ru'),
        ('a1234@yandex.ru', '*****@yandex.ru'),
        ('abcdef@yandex.ru', 'a*****@yandex.ru'),
        ('very-long-email@yandex.ru', 'very-**********@yandex.ru'),
    )
    for email, expected in values:
        eq_(mask_email_for_statbox(email), expected)


def test_mask_for_challenge():
    mapping = {
        'login@mail.ru': 'l***n@m***.ru',
        'abc@de.ru': 'a***c@d***.ru',
        'ab@c.ru': '***@***.ru',
        'a@ru': '***@***',
    }
    for actual, expected in iteritems(mapping):
        eq_(mask_email_for_challenge(actual), expected)

    mapping = {
        'login@mail.ru': 'l***n@mail.ru',
        'abc@de.ru': 'a***c@de.ru',
        'ab@c.ru': '***@c.ru',
        'a@ru': '***@ru',
    }
    for actual, expected in iteritems(mapping):
        eq_(mask_email_for_challenge(actual, mask_domain=False), expected)


def test_get_default_native_emails():
    eq_(
        get_default_native_emails('login'),
        {
            'login@ya.ru',
            'login@yandex.ru',
            'login@yandex.com',
            'login@narod.ru',
            'login@yandex.ua',
            'login@yandex.kz',
            'login@yandex.by',
        },
    )


@with_settings(
    NATIVE_EMAIL_DOMAINS=('yandex.ru', 'yandex.com.tr', u'яндекс.рф'),
)
def test_is_native_yandex_email():
    native_emails = (
        u'логин.логин@яндекс.рф',
        u'логин.логин@' + u'яндекс.рф'.encode('idna').decode('utf-8'),
        'login-login@yandex.com.tr',
        'login@YANDEX.RU',
        '@yandex.ru',  # корректность адреса не проверяется
    )
    non_native_emails = (
        'email@domain.com',
        'yandex.ru@',
        'not_an_email',
        'email@yandex.bla.bla',
    )
    for email in native_emails:
        ok_(is_yandex_email(email))
    for email in non_native_emails:
        ok_(not is_yandex_email(email))
