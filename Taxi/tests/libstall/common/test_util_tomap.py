from libstall.util import (
    tomap
)


def test_tomap_simple(tap):
    with tap.plan(7, 'Простое приведение к диапазону'):

        tap.eq(tomap(50, 0, 5), 2, '50 -> 0 .. 5')
        tap.eq(tomap(51, 0, 5), 3, '51 -> 0 .. 5')
        tap.eq(tomap(52, 0, 5), 4, '52 -> 0 .. 5')
        tap.eq(tomap(53, 0, 5), 5, '53 -> 0 .. 5')
        tap.eq(tomap(54, 0, 5), 0, '54 -> 0 .. 5')
        tap.eq(tomap(55, 0, 5), 1, '55 -> 0 .. 5')
        tap.eq(tomap(56, 0, 5), 2, '56 -> 0 .. 5')


def test_tomap_not_start(tap):
    with tap.plan(3, 'Диапазон не с нуля'):
        tap.eq(tomap(50, 4, 5), 4, '50 -> 4 .. 5')
        tap.eq(tomap(51, 4, 5), 5, '51 -> 4 .. 5')
        tap.eq(tomap(52, 4, 5), 4, '52 -> 4 .. 5')


def test_tomap_eq(tap):
    with tap.plan(2, 'Диапазон из одного числа'):
        tap.eq(tomap(50, 5, 5), 5, '50 -> 5 .. 5')
        tap.eq(tomap(51, 5, 5), 5, '51 -> 5 .. 5')


def test_tomap_zero(tap):
    with tap.plan(2, 'Диапазон из нуля'):
        tap.eq(tomap(50, 0, 0), 0, '50 -> 0 .. 0')
        tap.eq(tomap(51, 0, 0), 0, '51 -> 0 .. 0')


def test_tomap_negative(tap):
    with tap.plan(6, 'С отрицательным началом'):
        tap.eq(tomap(50, -2, 2), 0, '50 -> -2 .. 2')
        tap.eq(tomap(51, -2, 2), 1, '51 -> -2 .. 2')
        tap.eq(tomap(52, -2, 2), 2, '52 -> -2 .. 2')
        tap.eq(tomap(53, -2, 2), -2, '53 -> -2 .. 2')
        tap.eq(tomap(54, -2, 2), -1, '54 -> -2 .. 2')
        tap.eq(tomap(55, -2, 2), 0, '55 -> -2 .. 2')
