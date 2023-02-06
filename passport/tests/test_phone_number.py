# -*- coding: utf-8 -*-

import re
import unittest

from mock import Mock
from nose.tools import (
    eq_,
    ok_,
    raises,
)
from passport.backend.core.conf import settings
from passport.backend.core.test.test_utils.utils import settings_context
from passport.backend.core.types.phone_number.phone_number import (
    FakePhoneNumber,
    get_alt_phone_numbers_of_phone_number,
    initialize,
    InvalidPhoneNumber,
    mask_for_statbox,
    mask_phone_number,
    parse_phone_number,
    PhoneNumber,
)
from phonenumbers import PhoneMetadata
from six import iteritems


def test_initialize():
    loader = Mock()
    PhoneMetadata.register_region_loader('TEST_REGION', loader)
    initialize()
    loader.assert_called_once_with('TEST_REGION')


class TestPhoneNumber(unittest.TestCase):
    def test_phone_parse_ok(self):
        PhoneNumber.parse('+74951234567')  # Россия
        PhoneNumber.parse('+90 538 377 3877')  # Турция
        PhoneNumber.parse('+380 44 279 1967')  # Киев
        PhoneNumber.parse('+1 650 253 0000')  # США
        PhoneNumber.parse('+993 61 365583')  # Туркменистан
        PhoneNumber.parse('+251 94 3891308')  # Эфиопия
        PhoneNumber.parse('+229 62 067548')  # Бенин
        PhoneNumber.parse('+229 65 801108')  # Бенин
        PhoneNumber.parse('+253 77 0 30813')  # Джибути
        PhoneNumber.parse('+1 268 732 6382')  # Антигуа и Барбуда
        PhoneNumber.parse('+373 677 5 7553')  # Молдова
        PhoneNumber.parse('+9 0561 61 35355')  # Турция
        PhoneNumber.parse('+228 97 347328')  # Того
        PhoneNumber.parse('+596 696 52 8615')  # Мартиника
        PhoneNumber.parse('+992 50 0000220')  # Таджикистан
        PhoneNumber.parse('+992 77 7159972')  # Таджикистан
        PhoneNumber.parse('+380 71 30 15613')  # Украина
        PhoneNumber.parse('+1 868 267 2002')  # Тринидад и Тобаго
        PhoneNumber.parse('+374 44 98 90 02')  # Армения
        PhoneNumber.parse('+38 072 300 11 11')  # Украина
        PhoneNumber.parse('+995559000001')  # Грузия
        PhoneNumber.parse('+263719112069')  # Зимбабве
        PhoneNumber.parse('+38267112005')  # Черногория
        PhoneNumber.parse('+77064000188')  # Казахстан
        PhoneNumber.parse('+22570109807')  # Кот-д'Ивуар
        PhoneNumber.parse('+22504563616')  # Кот-д'Ивуар
        PhoneNumber.parse('+2250504563616')  # Кот-Д'Ивуар

        phone_number = PhoneNumber.parse('+992 88 0387848')  # Таджикистан
        eq_(phone_number.e164, '+992880387848')

        PhoneNumber.parse('+992 55 2056588')  # Таджикистан

    def test_parse_from_country_ok(self):
        pn = PhoneNumber.parse('4951234567', 'RU')
        eq_(pn.e164, '+74951234567')
        eq_(pn.original_country, 'ru')
        assert type(pn) is PhoneNumber

        pn = PhoneNumber.parse('(650) 253 0000', 'US')
        eq_(pn.e164, '+16502530000')
        eq_(pn.original_country, 'us')

        pn = PhoneNumber.parse('+1 (650) 253 0000')
        eq_(pn.e164, '+16502530000')
        eq_(pn.country, 'US')

        pn = PhoneNumber.parse('+1 (650) 253 0000', 'RU')
        eq_(pn.e164, '+16502530000')
        eq_(pn.country, 'US')

    def test_parse_local_kz_ru_cases_ok(self):
        phones_countries = (
            (' 7(495) 123-45-67', '+74951234567', 'ru', 'ru', 'RU'),
            (' 7(495) 123-45-67', '+74951234567', 'kz', None, 'RU'),
            ('77715512922', '+77715512922', 'kz', 'kz', 'KZ'),
            ('77715512922', '+77715512922', 'ru', 'ru', 'KZ'),
        )
        for phone, expected_phone, country, original_country, correct_country in phones_countries:
            pn = PhoneNumber.parse(phone, country)
            eq_(pn.e164, expected_phone)
            eq_(pn.original_country, original_country)
            eq_(pn.country, correct_country)

    def test_parse_local_from_wrong_country_ok(self):
        phones_countries = (
            (' 7(495) 123-45-67', '+74951234567', 'EN', 'RU'),
            ('77715512922', '+77715512922', 'EN', 'KZ'),
            ('9033837 7 3877', '+903383773877', 'RU', 'TR'),
            ('(380) 44 279 1967', '+380442791967', 'UK', 'UA'),
            ('375 29260 5281', '+375292605281', 'RU', 'BY'),
        )
        for phone, expected_phone, country, correct_country in phones_countries:
            pn = PhoneNumber.parse(phone, country)
            eq_(pn.e164, expected_phone)
            eq_(pn.original_country, None)
            eq_(pn.country, correct_country)

    def test_parse_local_from_none_country_ok(self):
        phones_countries = (
            (' 7(495) 123-45-67', '+74951234567', 'RU'),
            ('77715512922', '+77715512922', 'KZ'),
            ('9033837 7 3877', '+903383773877', 'TR'),
            ('(380) 44 279 1967', '+380442791967', 'UA'),
            ('375 29260 5281', '+375292605281', 'BY'),
        )
        for phone, expected_phone, country in phones_countries:
            pn = PhoneNumber.parse(phone)
            eq_(pn.e164, expected_phone)
            eq_(pn.original_country, None)
            eq_(pn.country, country)

    def test_parse_invalid_whitelisted_ok(self):
        phones = (
            ('+998 61 35 62752', '+998613562752', 'UZ'),   # Узбекистан
            ('+382679112005', '+382679112005', 'ME'),      # Черногория
            ('+972572398670', '+972572398670', 'IL'),      # Израиль
            ('+8401678123456', '+841678123456', 'VN'),     # Вьетнам
        )
        for raw_number, e164, country in phones:
            pn = PhoneNumber.parse(raw_number)
            ok_(pn.is_possible, pn)
            ok_(not pn.is_valid, pn)
            eq_(pn.e164, e164)
            eq_(pn.country, country)

    def test_parse_invalid_whitelisted_overrided_ok(self):
        whitelist = [
            [re.compile(r'^\+7966\d{6}$'), 'russia'],
            [re.compile(r'^\+59669659\d{4}$'), 'martinique_59'],
        ]
        pn = PhoneNumber.parse('+596696598615', invalid_whitelist=whitelist)
        ok_(pn.is_possible)
        ok_(not pn.is_valid)
        eq_(pn.e164, '+596696598615')
        eq_(pn.international, '+596 696 59 86 15')
        eq_(pn.national, '0696 59 86 15')
        eq_(pn.country, 'MQ')
        assert type(pn) is PhoneNumber

    def test_fake_phone_numbers(self):
        for digit in range(10):
            number = '+7000%d123456' % digit
            pn = PhoneNumber.parse(number)
            ok_(pn.is_possible)
            ok_(not pn.is_valid)
            eq_(pn.e164, number)

        pn = PhoneNumber.parse('+70000123456')
        assert type(pn) is FakePhoneNumber
        eq_(pn.international, '+7 000 012-34-56')
        eq_(pn.national, '8 (000) 012-34-56')

        assert type(PhoneNumber.parse('+70000123456', allow_impossible=True)) is FakePhoneNumber

    def test_parse_impossible_whitelisted_ok(self):
        phones = [
            ('+7966000000', '+7966000000', 'RU'),          # Россия
        ]

        whitelist = list(settings.PHONE_NUMBERS_WHITELIST)
        whitelist.extend(
            [
                [re.compile(r'^\+7966\d{6}$'), 'russia'],
            ],
        )

        for raw_number, e164, country in phones:
            pn = PhoneNumber.parse(raw_number, invalid_whitelist=whitelist)
            ok_(not pn.is_possible, pn)
            ok_(not pn.is_valid, pn)
            eq_(pn.e164, e164)
            eq_(pn.country, country)

    def test_blacklist_invalid_phone(self):
        """
        Можно отключать правила в белом списке
        """
        mynumber = '+7 966 000 000'

        with self.assertRaises(InvalidPhoneNumber):
            PhoneNumber.parse(mynumber)

        whitelist = [
            [r'^ \+7 966 000 000 $', 'mynumber'],
        ]
        for rule in whitelist:
            rule[0] = re.compile(rule[0], re.VERBOSE)

        with settings_context(
            PHONE_NUMBERS_WHITELIST=whitelist,
            PHONE_NUMBERS_WHITELIST_DISABLED_RULES=set([]),
        ):
            phone = PhoneNumber.parse(mynumber)

        ok_(not phone.is_possible)
        ok_(not phone.is_valid)

        with settings_context(
            PHONE_NUMBERS_WHITELIST=whitelist,
            PHONE_NUMBERS_WHITELIST_DISABLED_RULES=set(['mynumber']),
        ):
            with self.assertRaises(InvalidPhoneNumber):
                PhoneNumber.parse(mynumber)

    def test_blacklist_valid_phone(self):
        """
        Даже валидные номера не должны парситься, если они в чёрном списке
        """
        mynumber = '+7 925 916 1234'

        phone = PhoneNumber.parse(mynumber)

        ok_(phone.is_possible)
        ok_(phone.is_valid)

        whitelist = [
            [r'^ \+7 925 916 1234 $', 'mynumber'],
        ]
        for rule in whitelist:
            rule[0] = re.compile(rule[0], re.VERBOSE)

        with settings_context(
            PHONE_NUMBERS_WHITELIST=whitelist,
            PHONE_NUMBERS_WHITELIST_DISABLED_RULES=set(['mynumber']),
        ):
            with self.assertRaises(InvalidPhoneNumber):
                PhoneNumber.parse(mynumber)

    def test_repr(self):
        eq_(repr(PhoneNumber.parse('+74951234567')), '<PhoneNumber: +7 495 123-45-67>')

    def test_original_number(self):
        eq_(PhoneNumber.parse('+74951234567').original, '+74951234567')
        eq_(PhoneNumber.parse('7495 123 45 67').original, '7495 123 45 67')

    @raises(InvalidPhoneNumber)
    def test_phone_parse_fail_1(self):
        PhoneNumber.parse('+749599999999')

    @raises(InvalidPhoneNumber)
    def test_phone_parse_fail_2(self):
        PhoneNumber.parse('+700099999999')

    @raises(InvalidPhoneNumber)
    def test_phone_parse_fail_3(self):
        PhoneNumber.parse('999999')

    @raises(InvalidPhoneNumber)
    def test_phone_parse_fail_4(self):
        # Таджикский костыль
        PhoneNumber.parse('+99280387848')

    def test_phone_parse_allow_impossible(self):
        pn = PhoneNumber.parse('+791234567802', allow_impossible=True)

        ok_(not pn.is_possible)
        ok_(not pn.is_valid)

        eq_(pn.number_type_id, 99)
        eq_(pn.number_type, 'unknown')

        eq_(pn.e164, '+791234567802')
        eq_(pn.digital, '791234567802')

        # Полноценного форматирования международного номера может не быть, только разделение кода страны и остального номера.
        eq_(pn.international, '+7 91234567802')
        # Также может не быть полноценного форматирования.
        eq_(pn.national, '91234567802')

        # Однако номер разбивается на часть после кода страны...
        eq_(pn.national_significant_number, '91234567802')
        # ...и сам код страны распознаётся, и ...
        eq_(pn.country_code, '7')
        # ...идентификатор страны определяется (конкретно для этого номера, для других страна может и не определиться).
        eq_(pn.country, 'RU')

        # Однако не распознаётся код назначения...
        eq_(pn.national_destination_code_length, 0)
        eq_(pn.national_destination_code, '')
        # ...из-за чего криво маскируется для Фродо (нули сразу после кода страны, а не после кода назначения).
        eq_(pn.masked_format_for_frodo, '700034567802')

        # Однако это не мешает маскированию для statbox-логов.
        eq_(pn.masked_format_for_statbox, '+79123*******')

    def test_number_type(self):
        phones = (
            ('+74951234567', 0, 'fixed_line'),
            ('+905383773877', 1, 'mobile'),
        )
        for raw_number, number_type_id, number_type in phones:
            pn = PhoneNumber.parse(raw_number)
            eq_(pn.number_type_id, number_type_id)
            eq_(pn.number_type, number_type)

    def test_phone_e164(self):
        mapping = {
            '+74951234567': '+74951234567',
            '+90 538 377 3877': '+905383773877',
            '+380 44 279 1967': '+380442791967',
            '+1 650 253 0000': '+16502530000',
        }
        for actual, expected in iteritems(mapping):
            eq_(PhoneNumber.parse(actual).e164, expected)

    def test_phone_international(self):
        mapping = {
            '+74951234567': '+7 495 123-45-67',
            '+90 538 377 38 77': '+90 538 377 38 77',
            '+380 44 279 1967': '+380 44 279 1967',
            '+1 650 253 0000': '+1 650-253-0000',
        }
        for actual, expected in iteritems(mapping):
            eq_(PhoneNumber.parse(actual).international, expected)

    def test_phone_national(self):
        mapping = {
            '+74951234567': '8 (495) 123-45-67',
            '+90 538 377 38 77': '0538 377 38 77',
            '+380 44 279 1967': '044 279 1967',
            '+1 650 253 0000': '(650) 253-0000',
        }
        for actual, expected in iteritems(mapping):
            eq_(PhoneNumber.parse(actual).national, expected)

    def test_national_significant_number(self):
        eq_(PhoneNumber.parse('+79161234567').national_significant_number, '9161234567')

    def test_country_code(self):
        eq_(PhoneNumber.parse('+79161234567').country_code, '7')

    def test_national_destination_code_length(self):
        eq_(PhoneNumber.parse('+79161234567').national_destination_code_length, 3)

    def test_national_destination_code(self):
        eq_(PhoneNumber.parse('+79161234567').national_destination_code, '916')

    def test_masked_format_for_frodo(self):
        mapping = {
            '+74951234567': '74950004567',
            '+90 538 377 3877': '905380003877',
            '+380 44 279 1967': '380440001967',
            '+1 650 253 1234': '16500001234',
        }
        for actual, expected in iteritems(mapping):
            eq_(PhoneNumber.parse(actual).masked_format_for_frodo, expected)

        eq_(PhoneNumber.parse('+749', allow_impossible=True).masked_format_for_frodo, '700')

    def test_masked_format_for_statbox(self):
        mapping = {
            '+74951234567': '+74951******',
            '+90 538 377 3877': '+90538*******',
            '+380 44 279 1967': '+38044*******',
            '+1 650 253 1234': '+16502******',
        }
        for actual, expected in iteritems(mapping):
            eq_(len(PhoneNumber.parse(actual).e164), len(PhoneNumber.parse(actual).masked_format_for_statbox))
            eq_(PhoneNumber.parse(actual).masked_format_for_statbox, expected)

    def test_masked_format_for_challenge(self):
        mapping = {
            '+74951234567': '+7 495 ***-**-67',
            '+90 538 377 38 77': '+90 538 *** ** 77',
            '+380 44 279 1967': '+380 44 *** **67',
            '+1 650 253 1234': '+1 650-***-**34',
            '+7 72641 92678': '+7 726** * ** 78',
        }
        for actual, expected in iteritems(mapping):
            eq_(
                len(PhoneNumber.parse(actual).international),
                len(PhoneNumber.parse(actual).masked_format_for_challenge),
            )
            eq_(
                PhoneNumber.parse(actual).masked_format_for_challenge,
                expected,
            )

    def test_mask_for_flash_call(self):
        mapping = {
            '+74951234567': '+7 495 123-XX-XX',
            '+90 538 377 38 77': '+90 538 377 XX XX',
            '+380 44 279 1967': '+380 44 279 XXXX',
            '+1 650 253 1234': '+1 650-253-XXXX',
            '+7 72641 92678': '+7 72641 9 XX XX',
        }
        for actual, expected in iteritems(mapping):
            eq_(
                len(PhoneNumber.parse(actual).international),
                len(PhoneNumber.parse(actual).masked_for_flash_call),
            )
            eq_(
                PhoneNumber.parse(actual).masked_for_flash_call,
                expected,
            )

    def test_mask_for_statbox_short_phone(self):
        eq_(mask_for_statbox('12345'), '12345')
        eq_(mask_for_statbox(''), '')
        ok_(mask_for_statbox(None) is None)

    def test_mask_phone_number(self):
        mapping = {
            '+74951234567': '+7495*****67',
            '+7(495)123-45-67': '+7(495)***-**-67',
            '8(495)123-45-67': '8(495)***-**-67',
            '+90 538 377 38 77': '+90 538 *** ** 77',
            '+380 44 279 1967': '+380 44 *** **67',
            '+1 650 253 1234': '+1 650 *** **34',
            '+373 677 5 7553': '+373 6** * **53',
            '12': '12',
            '': '',
        }
        for actual, expected in iteritems(mapping):
            eq_(mask_phone_number(actual), expected)

    def test_aliases(self):
        phone = PhoneNumber.parse('+7 495 123 45 67', 'RU')
        eq_(phone.original, '+7 495 123 45 67')
        eq_(phone.e164, '+74951234567')
        eq_(phone.international, '+7 495 123-45-67')

    def test_digital(self):
        phone = PhoneNumber.parse('+7 495 123 45 67')
        eq_(phone.digital, '74951234567')

    def test_eq_ne(self):
        phone1 = PhoneNumber.parse('+7 495 123 45 67')
        phone2 = PhoneNumber.parse('+7 495 123 45 67')

        ok_(phone1 == phone2)
        ok_(not phone1 == '1234')
        ok_(not phone1 == PhoneNumber.parse('+7 495 123 45 68'))
        ok_(not phone1 != phone2)

    def test_set(self):
        phones = set()
        phones.add(PhoneNumber.parse('+7 495 123 45 67'))
        phones.add(PhoneNumber.parse('+7-495-123-45-67'))
        eq_(
            phones,
            {
                PhoneNumber.parse('495 123 45 67', 'RU'),
            },
        )

    def test_parse_phone_number_helper(self):
        eq_(
            parse_phone_number('4951234567', 'RU'),
            PhoneNumber.parse('4951234567', 'RU'),
        )
        eq_(
            parse_phone_number(PhoneNumber.parse('+1 (650) 253 0000')),
            PhoneNumber.parse('+1 (650) 253 0000'),
        )
        eq_(
            parse_phone_number('+700099999999'),
            None,
        )
        eq_(
            parse_phone_number('+700099999999', allow_impossible=True),
            PhoneNumber.parse('+700099999999', allow_impossible=True),
        )

    def test_is_similar_to(self):
        possible_number = PhoneNumber.parse('+79161112233')
        right_possible_country = 'RU'
        wrong_possible_country = 'US'

        # Возможная страна не важна,
        ok_(possible_number.is_similar_to('9161112233', right_possible_country))
        ok_(possible_number.is_similar_to('9161112233', wrong_possible_country))
        ok_(possible_number.is_similar_to('9161112233', None))

        ok_(possible_number.is_similar_to('89161112233', right_possible_country))
        ok_(possible_number.is_similar_to('(916)111-22-33', right_possible_country))
        ok_(possible_number.is_similar_to('(916)111 22 33', right_possible_country))

        ok_(not possible_number.is_similar_to('(916)111 22 ~33', right_possible_country))
        ok_(not possible_number.is_similar_to('(916)111 22 q33', right_possible_country))
        ok_(not possible_number.is_similar_to('4951234567', right_possible_country))

    def test_vietnam_11_to_10(self):
        PhoneNumber.parse('+8401678123456')
        PhoneNumber.parse('+840378123456')

    def test_brasil_10_to_11(self):
        PhoneNumber.parse('+555198179688')
        PhoneNumber.parse('+5551998179688')

    @raises(InvalidPhoneNumber)
    def test_brasil_10_zero_leading_number(self):
        PhoneNumber.parse('+550976918505')

    @raises(InvalidPhoneNumber)
    def test_brasil_11_zero_leading_number(self):
        PhoneNumber.parse('+5500976918505')

    def test_from_deprecated_of_old_deprecated_phone(self):
        with settings_context(
            IS_IVORY_COAST_8_DIGIT_PHONES_DEPRECATED=True,
        ):
            self.assertEqual(
                PhoneNumber.from_deprecated(PhoneNumber.parse('+22503123456')),
                PhoneNumber.parse('+2250103123456'),
            )

    def test_from_deprecated_of_old_deprecated_phone_and_invalid_new_phone(self):
        phone = PhoneNumber.parse('+22503123456')
        with settings_context(
            IS_IVORY_COAST_8_DIGIT_PHONES_DEPRECATED=True,
            PHONE_NUMBERS_WHITELIST_DISABLED_RULES=set(['ivory_coast_10_digits']),
        ):
            self.assertEqual(PhoneNumber.from_deprecated(phone), phone)

    def test_from_deprecated_of_new_phone(self):
        phone = PhoneNumber.parse('+2250103123456')
        self.assertEqual(PhoneNumber.from_deprecated(phone), phone)


class TestGetAltPhoneNumbersOfPhoneNumber(unittest.TestCase):
    def test_ivory_coast(self):
        d8_and_d10 = [
            ('+22503123456', '+2250103123456'),
            ('+22504123456', '+2250504123456'),
            ('+22508123456', '+2250708123456'),
        ]
        for d8, d10 in d8_and_d10:
            d8 = PhoneNumber.parse(d8)
            d10 = PhoneNumber.parse(d10)
            self.assertEqual(get_alt_phone_numbers_of_phone_number(d8), [d10], (d8, d10))
            self.assertEqual(get_alt_phone_numbers_of_phone_number(d10), [d8], (d10, d8))

    def test_no_alts(self):
        self.assertEqual(get_alt_phone_numbers_of_phone_number(PhoneNumber.parse('+79251234567')), list())
