# -*- coding: utf-8 -*-

from passport.backend.core.test.test_utils.form_utils import (
    check_equality,
    check_raise_error,
)
from passport.backend.core.validators import (
    AntiFraudFirstName,
    AntiFraudLastName,
    AntiFraudName,
    FirstName,
    LastName,
    Name,
)
from passport.backend.core.validators.utils import fold_whitespace
import pytest


@pytest.mark.parametrize('valid_name', [
    u'Анастасия',
    'Morozova    ',
    'a' * 51,
    'aa   aaa',
    'www.ru',
    'www.yandex.rutrailingtext',
    'a b c d',
    u'Волоская СОШ №1',
    u'\U0001F631',
    u'sereja.berezhnoj2016',
    ])
def test_name(valid_name):
    check_equality(
        Name(antifraud_heuristics=True),
        (valid_name, fold_whitespace(valid_name).strip()[:50])
    )


@pytest.mark.parametrize('validator', [
    Name,
    FirstName,
    LastName,
    AntiFraudName,
    AntiFraudLastName,
    AntiFraudName,
    ])
@pytest.mark.parametrize('invalid_name', [
    u'\u200CАнастасия',
    ])
def test_name_invalid(validator, invalid_name):
    check_raise_error(validator, invalid_name)


@pytest.mark.parametrize('validator', [
    Name,
    FirstName,
    LastName,
    AntiFraudName,
    AntiFraudLastName,
    AntiFraudName,
    ])
@pytest.mark.parametrize('empty_name', [
    '',
    '   ',
    None,
    ])
def test_name_empty(validator, empty_name):
    check_equality(validator, (empty_name, None))


@pytest.mark.parametrize('validator', [Name, FirstName, LastName])
@pytest.mark.parametrize('value', [
    0,
    {1: 2},
    ['value'],
    object(),
    ])
def test_names_with_strict_option(validator, value):
    check_raise_error(validator(strict=True), value)


@pytest.mark.parametrize('validator', [AntiFraudName, AntiFraudFirstName, AntiFraudLastName])
@pytest.mark.parametrize('value', [
    'Вы победили в акции.Забрать тут - www.lfe.ru ay',
    '">qw<script src=https://xawdxawdx.xss.ht></script>',
    u'Кликай кек.москва',
    u' www.ru.',
    u' www.ru?',
    u' www.ru,',
    u' www.ru-',
    u' www.ru_',
    u' www.ru/',
    u'www.ru/index.html',
    u'www.yandex.ru',
    'aa \n         aaa',
    'a' * 10 + ' ' * 40 + 'a' * 10,
    '1234567890',
    u'Ваш подарок тут диваны.рф',
    u'Ваш подарок тут ДиВаНы.Рф',
    u'Ваш подарок тут xn--80adfq1a8f.xn--p1ai',
    u'Ваш подарок тут xn--80adfq1a8f.xn--P1ai',
    ])
def test_fio_antifraud_heuristics(validator, value):
    check_raise_error(validator(), value)
