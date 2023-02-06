from datetime import datetime, date

import pytest
from dmp_suite import (
    data_quality_utils as dqu, datetime_utils as dtu
)


@pytest.mark.parametrize('expected, data', [
    (
        '2017-10-10 20:00:00',
        {
            'created_at': '2017-10-10 23:00:00',
        }
    ),
    (
        '2017-10-10 20:00:00',
        {
            'updated_at': '2017-10-10 23:00:00',
        }
    ),
    (
        '2017-10-10 20:00:01',
        {
            'created_at': '2017-10-10 23:00:00',
            'updated_at': '2017-10-10 23:00:01',
        }
    ),
    (
        '2017-11-09 22:00:00',
        {
            'created_at': '2017-11-10 01:00:00',
            'updated_at': '2017-10-10 23:00:00'
        }
    ),
    (
        '2017-11-09 22:00:00',
        {
            'created_at': '2017-11-10 01:00:00',
            'updated_at': None,
        }
    ),
    (
        '2017-11-09 22:00:00',
        {
            'created_at': None,
            'updated_at': '2017-11-10 01:00:00',
        }
    ),
    (
        '2017-11-10 01:00:00',
        {
            'created_at': '2017-11-10 04:00:00.123456',
            'updated_at': '2017-11-10 04:00:00',
        }
    ),
    (
        '2018-11-10 01:00:00',
        {
            'created_at': '2017-11-10 04:00:00.123456',
            'updated_at': '2017-11-10 04:00:00',
            'deleted_at': '2018-11-10 04:00:00',
        }
    ),
    (
        '2018-11-10 01:00:00',
        {
            'created_at': '2017-11-10 04:00:00.123456',
            'updated_at': None,
            'deleted_at': '2018-11-10 04:00:00',
        }
    ),
    (
        '2018-11-10 01:00:00',
        {
            'created_at': datetime(2017, 11, 10, 4, 0, 0, 123456),
            'updated_at': None,
            'deleted_at': '2018-11-10 04:00:00',
        }
    ),
])
def test_business_msk2utc_dttm_returns_valid_dttm_str(expected, data):
    extractor = dqu.business_msk2utc_dttm_extractor('created_at', 'updated_at', 'deleted_at')
    assert expected == extractor(data)


@pytest.mark.parametrize('expected, formatter, data', [
    (
        '2017-10-10 20:00:00',
        dtu.msk2utc_dttm,
        {
            'created_at': '2017-10-10 23:00:00',
        }
    ),
    (
        '2017-10-10 23:00:00',
        dtu.format_datetime,
        {
            'created_at': '2017-10-10 23:00:00',
        }
    ),
    (
        '2017-10-10 20:00:00',
        dtu.msk2utc_dttm,
        {
            'updated_at': '2017-10-10 23:00:00',
        }
    ),
    (
        '2017-10-10 20:00:01',
        dtu.msk2utc_dttm,
        {
            'created_at': '2017-10-10 23:00:00',
            'updated_at': '2017-10-10 23:00:01',
        }
    ),
    (
        '2017-10-10 23:00:01.000000',
        dtu.format_datetime_microseconds,
        {
            'created_at': '2017-10-10 23:00:00',
            'updated_at': '2017-10-10 23:00:01',
        }
    ),
    (
        '2017-11-09 22:00:00',
        dtu.msk2utc_dttm,
        {
            'created_at': '2017-11-10 01:00:00',
            'updated_at': '2017-10-10 23:00:00'
        }
    ),
    (
        '2017-11-09 22:00:00',
        dtu.msk2utc_dttm,
        {
            'created_at': '2017-11-10 01:00:00',
            'updated_at': None,
        }
    ),
    (
        '2017-11-09 22:00:00',
        dtu.msk2utc_dttm,
        {
            'created_at': None,
            'updated_at': '2017-11-10 01:00:00',
        }
    ),
    (
        '2017-11-10 01:00:00',
        dtu.msk2utc_dttm,
        {
            'created_at': '2017-11-10 04:00:00.123456',
            'updated_at': '2017-11-10 04:00:00',
        }
    ),
    (
        '2018-11-10 01:00:00',
        dtu.msk2utc_dttm,
        {
            'created_at': '2017-11-10 04:00:00.123456',
            'updated_at': '2017-11-10 04:00:00',
            'deleted_at': '2018-11-10 04:00:00',
        }
    ),
    (
        '2018-11-10 01:00:00',
        dtu.msk2utc_dttm,
        {
            'created_at': '2017-11-10 04:00:00.123456',
            'updated_at': None,
            'deleted_at': '2018-11-10 04:00:00',
        }
    ),
    (
        '2018-11-10 01:00:00',
        dtu.msk2utc_dttm,
        {
            'created_at': datetime(2017, 11, 10, 4, 0, 0, 123456),
            'updated_at': None,
            'deleted_at': '2018-11-10 04:00:00',
        }
    ),
])
def test_business_returns_valid_dttm_str(expected, formatter, data):
    extractor = dqu.business_dttm_extractor(formatter, 'created_at', 'updated_at', 'deleted_at')
    assert expected == extractor(data)


@pytest.mark.parametrize('data', [
    {'created_at': None},
    {'created_at': ''},
    {'updated_at': None},
    {'created_at': None, 'updated_at': None},
    {'created_at': None, 'updated_at': None, 'deleted_at': None},
    {},
    None,
    {'created_at': 1, 'updated_at': '2018-11-10 04:00:00'},
    {'created_at': '2018-1-1', 'updated_at': '2018-1-20'},
    {'created_at': 2, 'updated_at': True},
])
def test_business_msk2utc_dttm_returns_none(data):
    extractor = dqu.business_msk2utc_dttm_extractor('created_at', 'updated_at', 'deleted_at')
    assert extractor(data) is None


@pytest.mark.parametrize('email, result', [
    ('me@example.com', True),
    ('eda@yandex-team.ru', True),
    ('awesome-developer@ya.ru', True),
    ('@yandex.ru', False),
    ('developer@', False),
    ('develop@ya', False),
    ('developerya.ru', False),
])
def test_check_email(email, result):
    assert dqu.check_email(email) is result


@pytest.mark.parametrize('email', [
    'me@example.com',
    'eda@yandex-team.ru',
    'awesome-developer@ya.ru'
])
def test_get_email_correct_input(email):
    assert dqu.get_email(email) == email


@pytest.mark.parametrize('email', [
    '@yandex.ru',
    'developer@',
    'develop@ya',
    'developerya.ru'
])
def test_get_email_incorrect_input(email):
    assert dqu.get_email(email) is None


@pytest.mark.parametrize('dttm, expected', [
    (None, False),
    (datetime(2019, 1, 1), True),
    (u'2018-12-01 00:23:13', True),
    (u'incorrect unicode', False)
])
def test_check_datetime(dttm, expected):
    assert dqu.check_datetime(dttm) == expected


@pytest.mark.parametrize('dttm', [
    1, [1, 2, 3], (123, 231, 1), {'a': 'b'}, {1, 45, 5}
])
def test_check_datetime_on_invalid_type(dttm):
    with pytest.raises(TypeError):
        assert dqu.check_datetime(dttm)


def test_geo_point():
    func = dqu.geo_point_extractor('longitude', 'latitude')
    assert func({'latitude': 47.1, 'longitude': 39.39}) == {'lon': 39.39, 'lat': 47.1}
    assert func({'longitude': 39.39, 'latitude': 47.1}) == {'lon': 39.39, 'lat': 47.1}
    assert func({'longitude': 39.39, 'latitude': 0.0}) == {'lon': 39.39, 'lat': 0.0}
    assert func({'longitude': 39.0, 'latitude': 47}) is None
    assert func({'longitude': '39.39', 'latitude': '47.1'}) is None
    assert func({'longitude': 39.39, 'wrong_key_name': 47.1}) is None
    assert func({'longitude': 39.39, 'latitude': None}) is None
    assert func({'longitude': '', 'latitude': 47.1}) is None
    assert func({'longitude': [], 'latitude': 47.1}) is None
    assert func({'longitude': [39.39], 'latitude': 47.1}) is None
    assert func({}) is None


def test_geo_point_from_strings():
    func = dqu.geo_point_extractor_from_strings('longitude', 'latitude')
    assert func({'latitude': '47.1', 'longitude': '39.39'}) == {'lon': 39.39, 'lat': 47.1}
    assert func({'longitude': '39.39', 'latitude': '47.1'}) == {'lon': 39.39, 'lat': 47.1}
    assert func({'longitude': '39.39', 'latitude': '0.0'}) == {'lon': 39.39, 'lat': 0.0}
    assert func({'longitude': '39.39', 'wrong_key_name': '47.1'}) is None
    assert func({'longitude': '39.39', 'latitude': None}) is None
    assert func({'latitude': '47.1'}) is None
    assert func({'longitude': '', 'latitude': '47.1'}) is None
    assert func({'longitude': [], 'latitude': '47.1'}) is None
    assert func({'longitude': ['39.39'], 'latitude': '47.1'}) is None
    assert func({}) is None


@pytest.mark.parametrize(
    "test_input,expected",
    [
        # None
        (None, None), (0, None),  ('918-371-06-64', None),
        ('799912345678', None), ('+799912345678', None),
        ('899912345678', None), ('8 9999 123456', None),

        # 1 main phone
        ('+79991234567', [{'main_phone': '+79991234567'}]),
        ('89991234567', [{'main_phone': '+79991234567'}]),
        ('8 9991234567', [{'main_phone': '+79991234567'}]),
        ('+7 999 1234567', [{'main_phone': '+79991234567'}]),
        ('+7 999 1234567', [{'main_phone': '+79991234567'}]),
        ('+7 999 123 4 567', [{'main_phone': '+79991234567'}]),
        ('+7(999)-123-45-67', [{'main_phone': '+79991234567'}]),
        ('8-999-123-45-67', [{'main_phone': '+79991234567'}]),
        ('+7+79991234567', [{'main_phone': '+79991234567'}]),
        ('+7-9991234567', [{'main_phone': '+79991234567'}]),
        ('8-999-123-45-67', [{'main_phone': '+79991234567'}]),
        ('79991234567', [{'main_phone': '+79991234567'}]),
        ('79991234567', [{'main_phone': '+79991234567'}]),

        # 2 main phone
        ('89991234567; 89991234555', [{'main_phone': '+79991234567'}, {'main_phone': '+79991234555'}]),
        ('+7(999)123-4567, +7(999)122-3344', [{'main_phone': '+79991234567'}, {'main_phone': '+79991223344'}]),

        # 1 main phone and 1 ext
        (u'+79991234567 доб.1522', [{'main_phone': '+79991234567', 'ext_phone': '1522'}]),
        (u'+79991234567 доп1522', [{'main_phone': '+79991234567', 'ext_phone': '1522'}]),
        (u'+79991234567 (доп. 1522)', [{'main_phone': '+79991234567', 'ext_phone': '1522'}]),
        (u'+79991234567 доб.25-076', [{'main_phone': '+79991234567', 'ext_phone': '25076'}]),
        (u'+79991234567 (доб 1)', [{'main_phone': '+79991234567', 'ext_phone': '1'}]),
        (u'89991234567 (доб.103)', [{'main_phone': '+79991234567', 'ext_phone': '103'}]),
        ('+79991234567 (103)', [{'main_phone': '+79991234567', 'ext_phone': '103'}]),
        ('+79991234567 , 103', [{'main_phone': '+79991234567', 'ext_phone': '103'}]),
        ('+79991234567(3)', [{'main_phone': '+79991234567', 'ext_phone': '3'}]),

        # 2 main phone and 1 ext
        (
                '+79991234567 (103) +79991234568',
                [{'main_phone': '+79991234567', 'ext_phone': '103'}, {'main_phone': '+79991234568'}]
        ),
        (
                u'+79991234567; +79991234568 доп1522',
                [{'main_phone': '+79991234567'}, {'main_phone': '+79991234568', 'ext_phone': '1522'}]
        ),

        # 2 main phone and 2 ext
        (
                u'+79991234567 (3) +79991234568 доп1522',
                [
                    {'main_phone': '+79991234567', 'ext_phone': '3'},
                    {'main_phone': '+79991234568', 'ext_phone': '1522'}
                ]
        ),
        (
                u'+79991234567 доб.111 +79991234568 доп1522',
                [
                    {'main_phone': '+79991234567', 'ext_phone': '111'},
                    {'main_phone': '+79991234568', 'ext_phone': '1522'}
                ]
        ),
    ]
)
def test_normalize_phone_number_w_ext_phone(test_input, expected):
    assert dqu.normalize_phone_number_w_ext_phone(test_input) == expected


@pytest.mark.parametrize(
    "test_input, expected",
    [
        (None, False), ('', False), (' ', False),
        ("-1", False), (-1, False), (u'ХАЙУ-Хай!', False),
        (-1.0, False), (u' ХАЙУ-Хай!', False),  (u' 11 22', False),
        (-1.0, False), ("+1", True), (u' 11 ', True),
        ("1", True), (1, True), (1.0, True), (0, True),
    ]
)
def test_check_unsigned(test_input, expected):
    assert dqu.check_unsigned(test_input) == expected


@pytest.mark.parametrize(
    "doc, expected",
    [
        ({}, None), ({'name': ' '}, None),
        ({'name': 1}, 1), ({'name': ''}, None),
        ({'name': '-1'}, None), ({'name': '1'}, '1'),
        ({'name': -1}, None),
        ({'name': u'test'}, None), ({'name': -1.0}, None),
        ({'name': 0}, 0), ({'name': 1.0}, 1.0),
    ]
)
def test_unsigned_extractor(doc, expected):
    assert dqu.unsigned_extractor(doc, 'name') == expected


@pytest.mark.parametrize(
    "test_input, expected",
    [
        (None, None),
        ('918-371-06-64', '+79183710664'),
        ('+79991234567', '+79991234567'),
        ('89991234567', '+79991234567'),
        ('9000276644', '+79000276644'),
        ('8 9991234567', '+79991234567'),
        ('+7 999 1234567', '+79991234567'),
        ('+7 999 123 4 567', '+79991234567'),
        ('+7(999)-123-45-67', '+79991234567'),
        ('8-999-123-45-67', '+79991234567'),
        ('+7-9991234567', '+79991234567'),
        ('8-999-123-45-67', '+79991234567'),
        ('79991234567', '+79991234567'),
        ('+3721234567', '+3721234567'),
        ('+8611234567890', '+8611234567890'),
        ('+998123456789', '+998123456789'),
        (998123456789, '+998123456789'),
        ('+ +99812 3456   789', '+998123456789'),
        ('+79271961916                       ','+79271961916')
    ]
)
def test_normalize_phone_number(test_input, expected):
    assert dqu.normalize_phone_number(test_input) == expected


@pytest.mark.parametrize(
    "test_input, expected",
    [
        ({'input_phone': '+8611234567890', 'min_phone_length': 10}, '+8611234567890'),
        ({'input_phone': '+3721234567', 'min_phone_length': 10}, '+3721234567'),
        ({'input_phone': '+3721234567', 'min_phone_length': 12}, None),
        ({'input_phone': '', 'min_phone_length': 1}, None),
    ]
)
def test_normalize_phone_number_w_min_phone_length(test_input, expected):
    assert dqu.normalize_phone_number(
        input_phone=test_input['input_phone'],
        min_phone_length=test_input['min_phone_length']
    ) == expected


@pytest.mark.parametrize(
    "test_input",
    [
        '+123456789123456789123456789',
        'e1e7ad08-f7d7',
        'e1e7ad08-f7d7-4082-b049-37954e3a3a1d',
        '+123456789 доб 5',
        '+123456789\f5',
        '+7927196191666666666666666666666666'
    ]
)
def test_normalize_phone_number_w_invalid_chars(test_input):
    with pytest.raises(ValueError):
        assert dqu.normalize_phone_number(test_input)


@pytest.mark.parametrize(
    'input_phone, expected',
    [
        ('7(999)1234567', '+79991234567'),
        ('+7-999-123-45-67 ', '+79991234567'),
        ('89991234567', '+89991234567'),
        ('+89991234567', '+89991234567'),
        ('9991234567', '+9991234567'),
        ('+9991234567', '+9991234567'),
        ('1991234567', '+1991234567'),
        ('+1991234567', '+1991234567'),
    ]
)
def test_normalize_phone_number_not_russian_numbers(input_phone, expected):
    assert dqu.normalize_phone_number(
        input_phone=input_phone,
        assume_russian_format_flg=False
    ) == expected


@pytest.mark.parametrize(
    'input_date, filtered_date',
    [
        (None, None),
        (date(2005, 7, 14), date(2005, 7, 14)),
        (date(1503, 7, 31), None),
        ('2005-07-14', '2005-07-14'),
        ('1503-07-31', None),
        ('20-05-08 00:00:00.000000', None),
    ]
)
def test_filtering_invalid_dates(input_date, filtered_date):
    assert dqu.filter_invalid_date(input_date) == filtered_date
