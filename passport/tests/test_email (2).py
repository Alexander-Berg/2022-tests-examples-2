# -*- coding: utf-8 -*-

from datetime import datetime
import unittest

from nose.tools import (
    eq_,
    ok_,
    raises,
)
from passport.backend.core.models.email import (
    Email,
    Emails,
)
from passport.backend.core.undefined import Undefined
from passport.backend.utils.string import smart_text


TEST_ADDRESS = 'test@okna.ru'
TEST_ADDRESS2 = 'test2@okna.ru'
TEST_ADDRESS3 = 'test3@okna.ru'
TEST_CYRILLIC_ADDRESS = u'абырвалг@яндекс.рф'


class TestEmailModel(unittest.TestCase):
    def test_parse_basic(self):
        email = Email().parse({'address': TEST_ADDRESS})

        eq_(email.address, TEST_ADDRESS)
        ok_(not email.is_confirmed)
        ok_(not email.is_native)
        ok_(not email.is_default)
        ok_(not email.is_rpop)
        ok_(not email.is_unsafe)

    def test_parse_full(self):
        email = Email().parse({
            'address': TEST_ADDRESS,
            'validated': False,
            'default': True,
            'prohibit-restore': False,
            'rpop': True,
            'silent': False,
            'unsafe': True,
            'native': False,
            'born-date': '2015-10-02 16:02:22',
        })

        eq_(email.address, TEST_ADDRESS)
        ok_(not email.is_confirmed)
        ok_(not email.is_native)
        eq_(email.id, Undefined)

        ok_(email.is_default)
        ok_(email.is_rpop)
        ok_(email.is_unsafe)

        eq_(
            email._last_changed_in_old_db,
            datetime(2015, 10, 2, 16, 2, 22),
        )

        eq_(
            email.created_at,
            datetime(2015, 10, 2, 16, 2, 22),
        )
        eq_(email.confirmed_at, Undefined)
        eq_(email.bound_at, Undefined)

    def test_parse_full_confirmed(self):
        email = Email().parse({
            'address': TEST_ADDRESS,
            'validated': True,
            'default': True,
            'prohibit-restore': False,
            'rpop': True,
            'silent': False,
            'unsafe': True,
            'native': False,
            'born-date': '2015-10-02 16:02:22',
        })

        eq_(email.address, TEST_ADDRESS)
        ok_(email.is_confirmed)
        ok_(not email.is_native)
        eq_(email.id, Undefined)

        ok_(email.is_default)
        ok_(email.is_rpop)
        ok_(email.is_unsafe)

        eq_(
            email._last_changed_in_old_db,
            datetime(2015, 10, 2, 16, 2, 22),
        )

        eq_(
            email.created_at,
            datetime(2015, 10, 2, 16, 2, 22),
        )
        eq_(
            email.confirmed_at,
            datetime(2015, 10, 2, 16, 2, 22),
        )
        eq_(
            email.bound_at,
            datetime(2015, 10, 2, 16, 2, 22),
        )

    def test_parse_from_extended_attributes(self):
        email = Email().parse({
            'address': TEST_ADDRESS,
            'validated': False,
            'default': True,
            'rpop': True,
            'silent': False,
            'unsafe': True,
            'id': 12345,
            'created': '1',
            'confirmed': '2',
            'bound': '3',
        })

        eq_(email._last_changed_in_old_db, Undefined)
        eq_(email.address, TEST_ADDRESS)
        ok_(email.is_confirmed)
        eq_(email.id, 12345)
        ok_(email.is_default)
        ok_(email.is_rpop)
        ok_(email.is_unsafe)

        eq_(
            email.created_at,
            datetime.fromtimestamp(1),
        )
        eq_(
            email.confirmed_at,
            datetime.fromtimestamp(2),
        )
        eq_(
            email.bound_at,
            datetime.fromtimestamp(3),
        )

    def test_is_external(self):
        email = Email().parse({
            'address': TEST_ADDRESS,
            'native': False,
        })
        ok_(email.is_external)

        email = Email().parse({
            'address': TEST_ADDRESS,
            'native': True,
        })
        ok_(not email.is_external)

    def test_is_suitable_for_restore(self):
        initial_state = {
            'address': TEST_ADDRESS,
            'validated': False,
            'native': False,
            'rpop': False,
            'unsafe': False,
            'silent': False,
        }

        states = (
            (True, ['validated']),
            (False, ['validated', 'native']),
            (False, ['validated', 'rpop']),
            (False, ['validated', 'unsafe']),
            (False, ['validated', 'silent']),
        )

        for expected_result, flags in states:
            sample = dict(
                initial_state,
                **{flag: True for flag in flags}
            )
            email = Email().parse(sample)
            eq_(
                email.is_suitable_for_restore,
                expected_result,
            )

    def test_username_domain(self):
        email = Email().parse({'address': TEST_ADDRESS})
        eq_(email.username, 'test')
        eq_(email.domain, 'okna.ru')

    def test_weird_username_domain(self):
        for login, domain in (
            (u'фываолдж', u'абырвалг'.encode('idna').decode('utf-8')),
            (r'log\@\@in', 'example.com'),
            ('$A12345', 'example.com'),
            ('!def!xyz%abc', 'example.com'),
        ):
            email = Email().parse({'address': '@'.join([login, domain])})
            eq_(email.username, login)
            eq_(email.domain, domain)

    @raises(ValueError)
    def test_normalize_address_fails_domain_too_long(self):
        Email.normalize_address('test@%s' % ('a' * 64))

    def test_str(self):
        for original, converted in (
            (TEST_ADDRESS, TEST_ADDRESS),
            (TEST_CYRILLIC_ADDRESS, TEST_CYRILLIC_ADDRESS.encode('utf-8')),
            (TEST_CYRILLIC_ADDRESS.encode('utf-8'), TEST_CYRILLIC_ADDRESS.encode('utf-8')),
        ):
            email = Email().parse({'address': original})
            eq_(
                smart_text(str(email)),
                smart_text(converted),
            )

    def test_repr(self):
        eq_(
            repr(Email().parse({'address': TEST_ADDRESS})),
            '<Email: %s>' % TEST_ADDRESS,
        )

    def test_normalize_address(self):
        for original, normalized in (
            (u'hello@world.ru', u'hello@world.ru'),
            (u' hello @ world.ru ', u'hello@world.ru'),
            (u'hello@окна.ру', u'hello@xn--80atjc.xn--p1ag'),
            (u'пользователь@окна.ру', u'пользователь@xn--80atjc.xn--p1ag'),
            (u'     пользователь@\tокна.ру', u'пользователь@xn--80atjc.xn--p1ag'),
            (u'ПоЛьЗоваТельские@ОкНа.Рф', u'пользовательские@xn--80atjc.xn--p1ai'),
        ):
            eq_(
                Email.normalize_address(original),
                normalized,
            )

    def test_address_and_normalized_address(self):
        for original, normalized in (
            (u'hello@world.ru', u'hello@world.ru'),
            (u' hello @ world.ru ', u'hello@world.ru'),
            (u'hello@окна.ру', u'hello@xn--80atjc.xn--p1ag'),
            (u'пользователь@окна.ру', u'пользователь@xn--80atjc.xn--p1ag'),
            (u'     пользователь@\tокна.ру', u'пользователь@xn--80atjc.xn--p1ag'),
            (u'MiXeDcAsE@Yandex.ru', u'mixedcase@yandex.ru'),
        ):
            email = Email().parse({'address': original})
            eq_(
                email.normalized_address,
                normalized,
            )
            eq_(
                email.address,
                original,
            )

    @raises(ValueError)
    def test_normalize_address_invalid_address_failes(self):
        Email.normalize_address('address')

    def test_split_simple(self):
        eq_(Email.split('u_se_r12@domain.com'), ['u_se_r12', 'domain.com'])

    def test_split_multiple(self):
        eq_(Email.split('u_se_r12@usus@domain.com'), ['u_se_r12@usus', 'domain.com'])

    def test_split_unicode(self):
        eq_(Email.split(u'у_зе_р12@домен.ком'), [u'у_зе_р12', u'домен.ком'])

    def test_split_no_domain(self):
        eq_(Email.split('some_thing'), (None, None))


class TestEmailsModel(unittest.TestCase):
    def test_parse_ok(self):
        emails = Emails().parse({
            'address-list': [
                {
                    'address': TEST_ADDRESS,
                    'validated': False,
                },
                {
                    'address': TEST_ADDRESS2,
                    'validated': False,
                    'native': True,
                },
            ],
        })

        eq_(len(list(emails.all)), 2)

    def test_parse_with_extended(self):
        emails = Emails().parse({
            'address-list': [
                {
                    'address': TEST_ADDRESS,
                    'validated': False,
                },
                {
                    'address': TEST_ADDRESS2,
                    'validated': False,
                    'native': True,
                },
            ],
            'emails': [
                {
                    'address': TEST_ADDRESS3,
                    'confirmed': 1,
                    'id': 12345,
                },
            ],
        })

        eq_(len(list(emails._emails)), 3)

    def test_parse_with_incorrect_addresses_drops_errors(self):
        emails = Emails().parse({
            'address-list': [
                {
                    'address': TEST_ADDRESS,
                    'validated': False,
                },
                {
                    'address': TEST_ADDRESS2,
                    'validated': False,
                    'native': True,
                },
                # Дальше идут плохие адреса, которых в окончательном выводе
                # быть не должно.
                {
                    'address': 'bad@.ru',
                    'validated': False,
                    'native': True,
                },
                {
                    'address': 'user.yandex.ru',
                    'validated': False,
                    'native': True,
                },
                {
                    'address': 'user&amp;yandex.ru',
                    'validated': False,
                    'native': True,
                },
            ],
        })

        eq_(len(list(emails._emails)), 2)

    def test_native(self):
        emails = Emails().parse({
            'address-list': [
                {
                    'address': TEST_ADDRESS,
                    'validated': False,
                },
                {
                    'address': TEST_ADDRESS2,
                    'validated': False,
                    'native': True,
                },
                {
                    'address': TEST_ADDRESS3,
                    'validated': True,
                    'native': True,
                },
            ],
        })

        eq_(len(emails.native), 2)
        for email in emails.native:
            ok_(
                email.is_native,
                '%s should be native!' % email,
            )

    def test_external(self):
        emails = Emails().parse({
            'address-list': [
                {
                    'address': TEST_ADDRESS,
                    'native': False,
                },
                {
                    'address': TEST_ADDRESS2,
                    'native': True,
                },
            ],
        })

        eq_(len(emails.external), 1)
        ok_(not emails.external[0].is_native)

    def test_confirmed_external(self):
        emails = Emails().parse({
            'address-list': [
                {
                    'address': TEST_ADDRESS,
                    'validated': True,
                },
                {
                    'address': TEST_ADDRESS2,
                    'validated': True,
                    'native': False,
                },
                {
                    'address': TEST_ADDRESS2,
                    'validated': True,
                    'native': True,
                },
            ],
        })

        eq_(len(emails.confirmed_external), 1)
        email = emails.confirmed_external[0]
        ok_(
            email.is_external,
            '%s should be external!' % email,
        )
        ok_(
            email.is_confirmed,
            '%s should be confirmed!' % email,
        )

    def test_suitable_for_restore(self):
        emails = Emails().parse({
            'address-list': [
                {
                    'address': TEST_ADDRESS,
                    'validated': True,
                    'native': False,
                },
                {
                    'address': TEST_ADDRESS2,
                    'validated': True,
                    'native': True,
                    'rpop': False,
                    'silent': False,
                    'unsafe': False,
                },
                {
                    'address': TEST_ADDRESS3,
                    'validated': True,
                    'native': False,
                    'rpop': True,
                    'unsafe': False,
                    'silent': False,
                },
            ],
        })

        eq_(len(emails.suitable_for_restore), 1)
        email = emails.suitable_for_restore[0]

        ok_(email.is_confirmed)
        ok_(email.is_external)
        ok_(not email.is_rpop)
        ok_(not email.is_unsafe)
        ok_(not email.is_silent)

    def test_len_emails(self):
        eq_(
            len(Emails().parse({})),
            0,
        )

        emails = Emails().parse({
            'address-list': [
                {
                    'address': TEST_ADDRESS,
                    'validated': True,
                    'native': False,
                },
                {
                    'address': TEST_ADDRESS2,
                    'validated': True,
                    'native': True,
                    'rpop': False,
                    'silent': False,
                    'unsafe': False,
                },
            ],
        })
        eq_(len(emails), 2)

    def test_get_unknown_email(self):
        emails = Emails().parse({})
        try:
            emails[u'ненормализованный@адрес.рф']
        except KeyError as e:
            eq_(e.args[0], u'ненормализованный@адрес.рф')

    def test_get_email_by_address(self):
        emails = Emails().parse({})

        email = Email(address=TEST_ADDRESS)
        email2 = Email(address=TEST_ADDRESS2)

        emails.add(email)
        emails.add(email2)

        eq_(emails[TEST_ADDRESS], email)
        eq_(emails[TEST_ADDRESS2], email2)

    def test_del_email(self):
        emails = Emails().parse({})

        email = Email(address=TEST_ADDRESS)
        email2 = Email(address=TEST_ADDRESS2)

        emails.add(email)
        emails.add(email2)

        del emails[TEST_ADDRESS]

        ok_(emails.find(TEST_ADDRESS) is None)
        ok_(emails.find(TEST_ADDRESS2) is not None)

    @raises(KeyError)
    def test_del_nonexistent_email(self):
        emails = Emails().parse({})
        del emails[TEST_ADDRESS]

    def test_pop_default_address(self):
        emails = Emails().parse({
            'address-list': [
                {
                    'address': TEST_ADDRESS,
                    'validated': True,
                    'native': False,
                    'default': True,
                },
                {
                    'address': TEST_ADDRESS2,
                    'validated': True,
                    'native': True,
                    'rpop': False,
                    'silent': False,
                    'unsafe': False,
                },
            ],
        })
        ok_(emails.default is not None)

        emails.pop(TEST_ADDRESS)
        ok_(emails.default is None)
        ok_(emails.find(TEST_ADDRESS) is None)

    def test_emails_repr(self):
        emails = Emails().parse({})

        email = Email(address=TEST_ADDRESS)
        email2 = Email(address=TEST_ADDRESS2)

        emails.add(email)
        emails.add(email2)

        eq_(
            repr(emails),
            '<Emails: [%s, %s]>' % (repr(email2), repr(email)),
        )

    def test_emails_add(self):
        email = Email().parse({
            'address': TEST_ADDRESS,
        })

        emails = Emails().parse({})
        emails.add(email)

        eq_(len(emails), 1)
        ok_(TEST_ADDRESS in emails)
        eq_(emails[TEST_ADDRESS].address, TEST_ADDRESS)

    def test_emails_contains(self):
        email = Email().parse({
            'address': TEST_ADDRESS,
        })

        emails = Emails().parse({})
        emails.add(email)

        mixedcase_version = TEST_ADDRESS.lower().capitalize()
        not_normalized_version = '    ' + TEST_ADDRESS + '    '

        ok_('hello@helo.ru' not in emails)

        ok_(TEST_ADDRESS in emails)
        ok_(not_normalized_version in emails)
        ok_(mixedcase_version in emails)
