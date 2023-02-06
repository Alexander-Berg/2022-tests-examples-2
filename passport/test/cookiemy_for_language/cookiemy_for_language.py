# -*- coding: utf-8 -*-

from cookiemy import Cookiemy


LANGUAGE_TO_COOKIEMY = {
    'auto': 0,
    'ru': 1,
    'uk': 2,
    'en': 3,
    'kk': 4,
    'be': 5,
    'tt': 6,
    'az': 7,
    'tr': 8,
}


def cookiemy_for_language(language):
    c = Cookiemy()
    c.insert(39, [0, LANGUAGE_TO_COOKIEMY[language]])
    return str(c)
