from libstall import json_pp as json
from libstall.money import Money


def test_parse_numeric(tap):
    tap.plan(5)

    tap.eq(Money(0), '0.00', 'ноль денег')

    tap.eq(Money(10), '10.00', '10')
    tap.eq(Money(1.0 / 3), '0.33', 'обрезка')

    tap.eq(Money(-1), '-1.00', 'отрицательные деньги')
    tap.eq(Money(-1 / 3), '-0.33', 'отлицательная обрезка')

    tap()


def test_parse_str(tap):
    tap.plan(5)

    tap.eq(Money('0'), '0.00', 'ноль денег')

    tap.eq(Money('10'), '10.00', '10')
    tap.eq(Money(str(1.0 / 3)), '0.33', 'обрезка')

    tap.eq(Money('-1'), '-1.00', 'отрицательные деньги')
    tap.eq(Money(str(-1 / 3)), '-0.33', 'отлицательная обрезка')

    tap()


def test_add(tap):
    tap.plan(5)

    tap.eq(Money('1') + 2, '3.00', 'сложение с числом левое')
    tap.eq(Money('1') + '2', '3.00', 'сложение со строкой')
    tap.eq(Money('1') + Money(2), '3.00', 'сложение с Money')

    tap.eq(2 + Money('1'), '3.00', 'сложение с числом правое')
    tap.eq('2' + Money('1'), '3.00', 'сложение со строкой')

    tap()


def test_sub(tap):
    tap.plan(5)

    tap.eq(Money('5') - 2, '3.00', 'вычитание с числом левое')
    tap.eq(Money('5') - '2', '3.00', 'вычитание со строкой')
    tap.eq(Money('5') - Money(2), '3.00', 'вычитание с Money')

    tap.eq(4 - Money('1'), '3.00', 'вычитание с числом правое')
    tap.eq('5' - Money('1'), '4.00', 'вычитание со строкой')

    tap()


def test_div_mul(tap):
    tap.plan(4)

    tap.eq(Money('5') * 2, '10.00', 'умножение с числом левое')
    tap.eq(7 * Money('5'), '35.00', 'умножение с числом правое')

    tap.eq(Money('5') / 3, '1.67', 'деление с числом левое')
    tap.eq(Money('1') / 3, '0.33', 'деление с числом левое')
    tap()


def test_pure_python(tap):
    with tap.plan(3):
        tap.eq(Money('42').pure_python(), '42.00', 'метод есть')
        tap.eq(
            json.dumps({'a': Money('42')}),
            '{"a":"42.00"}',
            'дамп дикта в json',
        )
        tap.eq(
            json.dumps([Money('42')]),
            '["42.00"]',
            'дамп листа в json',
        )
