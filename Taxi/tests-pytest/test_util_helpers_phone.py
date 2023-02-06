# -*- coding: utf-8 -*-
import pytest

from taxi.internal.city_kit import country_manager

params_test_check_phone = [
    ('+71234567890', u'rus', u'+71234567890'),
    ('+71234567890', None, u'+71234567890'),
    ('-71234567890', 'rus', u'+71234567890'),
    ('-71234567890', None, None),
    (u'+71234567890', u'rus', u'+71234567890'),
    ('+7123456789', 'rus', None),
    ('+712345678901', u'rus', None),
    (' +7(918) 761-80-09', 'rus', u'+79187618009'),
    (' +7(918) 761-80-09', None, u'+79187618009'),
    ('Телефон: +7(918) 761-80-09 (Сергей)', u'rus', u'+79187618009'),
    (u'Телефон: +7(918) 761+80+09 (Сергей)', 'rus', u'+79187618009'),
    ('8-918-761+80+09', 'rus', u'+79187618009'),
    ('8-918-761+80+09', None, None),
    ('+8-918-761+80+09', 'rus', None),
    ('+375(173)28-19-61', 'rus', u'+375173281961'),
    ('+375(173)28-19-61-1', 'rus', None),
    ('+375(173)28-19-6', 'blr', None),
    ('375(173)28-19-61', 'rus', None),
    ('375(173)28-19-61', 'blr', u'+375173281961'),
    ('80(173)28-19-61', 'blr', u'+375173281961'),
    ('+80(173)28-19-61', 'blr', None),
    ('80(173)28-19-61', None, None),
    (u'555-31-34', 'rus', None),
]


@pytest.mark.parametrize(
    'phone,country,result', params_test_check_phone,
    ids=['param%d' % i for i in xrange(len(params_test_check_phone))])
@pytest.inline_callbacks
def test_check_phone(phone, country, result):
    res = yield country_manager.clean_international_phone(phone, country)
    if result is None:
        assert res is None
    else:
        assert res == result
        assert isinstance(res, unicode)


@pytest.mark.parametrize(
    'phone,country,result', [
        ('555-31-34', 'rus', None),
        ('555-31-34', 'rus', None),
        ('+71234567890123', 'rus', None),
        ('+999999999', None, '+999999999'),
    ])
@pytest.inline_callbacks
def test_clean_international_phone_forced(phone, country, result):
    res = yield country_manager.clean_international_phone(
        phone, country, force=True)
    if result is None:
        assert res is None
    else:
        assert res == result
        assert isinstance(res, unicode)
