# -*- coding: utf-8 -*-
from itertools import chain
from nose.tools import (
    assert_raises,
    eq_,
)

from common.astromath import (
    AstroError,
    number_to_slug,
    slug_to_number,
)


def test_slug_to_number():
    # До первой итерации правок
    less_than_first_boundary = [
        ('aM0', 157121),
        ('_', 37),
        ('-', 0),
        ('---', 0),
        ('--1', 2),
        ('-1-', 128),
        ('1', 2),
        ('ab', 2471),
        ('ab-', 158144),
        ('9', 10),
        ('-_-', 2368),
    ]
    # Между первой и второй итерациями правок
    less_than_second_boundary = [
        ('8d221', 156707306),
        ('1AB', 8908),
        ('11111', 33028652),
        ('----1', 6832),
    ]
    # Современные ссылки
    modern_xids = [
        ('8d224', 156707309),
        ('EAndx', 215188107),
    ]

    for test, expected in chain(
        less_than_first_boundary,
        less_than_second_boundary,
        modern_xids,
    ):
        yield eq_, slug_to_number(test), expected


def test_astro_error():
    with assert_raises(AstroError):
        slug_to_number('------')


def test_number_to_slug():
    less_than_first_boundary = [
        ('aM0', 157121),
        ('_', 37),
        ('-', 0),
        ('1', 2),
        ('1-', 128),
        ('1', 2),
        ('ab', 2471),
        ('ab-', 158144),
        ('9', 10),
        ('_-', 2368),
    ]
    # Между первой и второй итерациями правок
    less_than_second_boundary = [
        ('8d221', 156707306),
        ('1AB', 8908),
        ('11111', 33028652),
        ('0ek', 6832),
    ]
    # Современные ссылки
    modern_xids = [
        ('8d224', 156707309),
        ('EAndx', 215188107),
    ]

    for expected, test in chain(
        less_than_first_boundary,
        less_than_second_boundary,
        modern_xids,
    ):
        yield eq_, number_to_slug(test), expected
