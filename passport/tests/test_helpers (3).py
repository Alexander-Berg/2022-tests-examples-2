# -*- coding: utf-8 -*-
import mock
import pytest
from nose.tools import (
    assert_is_none,
    eq_,
)
from passport.infra.daemons.yasmsapi.common.helpers import (
    count_sms_segments,
    detect_sms_encoding,
    make_weighted_random_choice,
    mask_for_statbox,
    pack_sms_id,
)


@pytest.mark.parametrize(
    'text',
    [
        u'abc@abc.fun',
        u'€£¥$',
        u'0x1B65',
        u'^~[]{}|\f',
        u'ΦΓΛΩΨΣö',
        u'0x1B',
        u'simple text#1 =^_^=',
    ],
)
def test_detect_sms_encoding_gsm(text):
    gsm_encoding = 'gsm0338'
    eq_(detect_sms_encoding(text), gsm_encoding)


@pytest.mark.parametrize(
    'text',
    [
        u'Какая гадость эта ваша заливная рыба',
        u'天津風',
        u'💔',
    ],
)
def test_detect_sms_encoding_utf16(text):
    utf16_encoding = 'utf16'
    eq_(detect_sms_encoding(text), utf16_encoding)


@pytest.mark.parametrize(
    ('text', 'count'),
    [
        (u'abc@abc.fun', 1),
        (u'~' * 160, 1),
        (u'33' * 153, 2),
        (u'gh' * 154, 3),
        (u'💔' * 70, 1),
        pytest.param(u'💔' * 160, 3, id=u'160💔'.encode('utf8')),
        (u'' * 160, 0),
        ('hola!', 1),
        ('йо!', 1),
    ],
)
def test_count_sms_segments(text, count):
    eq_(count_sms_segments(text), count)


@pytest.mark.parametrize(
    ('weight_list', 'i'),
    [
        ([1, 1, 1, 1], 2),
        ([10, 100], 0),
        ([1, 2, 1000], 1),
        ([1, 1], -1),  # невозможный вариант, взято из перла
    ],
)
def test_make_weighted_random_choice(weight_list, i):
    with mock.patch('random.randint', return_value=3):
        eq_(make_weighted_random_choice(weight_list), i)


def test_randint_for_teapots():
    index_choice = make_weighted_random_choice([1, 2, 3])
    assert -1 <= index_choice <= 2


@pytest.mark.parametrize(
    'params',
    [
        ('', 3, True),
        (2, '2', False),
        (3, 1000, True),
    ],
)
def test_pack_sms_id_none(params):
    assert_is_none(pack_sms_id(*params))


@pytest.mark.parametrize(
    ('params', 'result'),
    [
        ((2, 3, True), 2003000000000002),
        ((500, 0x3, False), 1003000000000500),
        ((-1, 999, False), 1998999999999999),
        ((1, 999, False), 1999000000000001),
    ],
)
def test_pack_sms_id(params, result):
    eq_(pack_sms_id(*params), result)


@pytest.mark.parametrize(
    ('case', 'res'),
    [
        ('', '****'),
        ('+79990010101', '+7999001****'),
        ('+799', '****'),
    ],
)
def test_mask_for_statbox(case, res):
    eq_(mask_for_statbox(case), res)
