# -*- coding: utf-8 -*-
from nose.tools import (
    assert_almost_equal,
    eq_,
)
from passport.backend.core.compare.equality.trigrams import (
    StringTrigrams,
    trigrams_compare,
)


def test_make_trigrams():
    for td in TRIGRAMS_TEST_DATA:
        result = StringTrigrams(td[0]).trigrams
        eq_(
            result,
            td[1],
            u'StringTrigrams("{}"), {} != {}'.format(td[0], result, td[1]),
        )


def test_trigrams_compare():
    for td in TRIGRAMS_COMPARE_TEST_DATA:
        result = trigrams_compare(td[0], td[1])
        assert_almost_equal(
            result,
            td[2],
            delta=0.015,
            msg=u'trigrams_compare("{}", "{}") != {} ({})'.format(td[0], td[1], td[2], result),
        )


TRIGRAMS_COMPARE_TEST_DATA = [
    (None, '', 0.0),
    ('', None, 0.0),
    (None, None, 0.0),
    (u'', u'', 1.0),
    (u'Равные строки', u'Равные строки', 1.0),

    (u'Очень похожие строки', u'Очень непохожие строки', 0.87),
    (u'Строка с одной опечаткой', u'Строка с одной опчаткой', 0.9),

    (u'1919', u'1919', 1.0),
    (u'CyBerr_BOT_1921344442A', u'CyBerr_BOT_19213442A', 0.96),
    (u'e3323thg', u'(e3323thg)', 0.55),
    (u'n-95)', u'n95)', 0.62),
    (u'акимова', u'окимова', 0.67),
    (u'Бадунова', u'Бодунова', 0.7),
    (u'борщ', u'борьщь', 0.43),
    (u'В блокноте', u'В блокноте .', 0.77),
    (u'Гусева', u'гусева', 0.63),
    (u'ЕК732132', u'732132', 0.67),
    (u'конфета', u'канфети', 0.33),
    (u'мюллер', u'мюлер', 0.8),
    (u'окрошка', u'крошка', 0.71),
    (u'отдых', u'отды', 0.62),
    (u'пельмени', u'бульмени', 0.6),
    (u'пушка', u'пушки', 0.57),
    (u'Себастьян Перейра', u'Сибостьян Перейро', 0.58),
    (u'уракова', u'уракова7', 0.74),
    (u'федор кибалник', u'федор кибальник', 0.85),
    (u'целовальникова', u'целовальника', 0.8),
]

TRIGRAMS_TEST_DATA = [
    (None, []),
    (u'', []),
    (u'abc', [u'$$a', u'$ab', u'abc', u'bc$', u'c$$']),
    (u'abcd', [u'$$a', u'$ab', u'abc', u'bcd', u'cd$', u'd$$']),
    (u'Очень похожие строки', [
        u'$$\u041e', u'$\u041e\u0447', u'\u041e\u0447\u0435', u'\u0447\u0435\u043d', u'\u0435\u043d\u044c',
        u'\u043d\u044c ', u'\u044c \u043f', u' \u043f\u043e', u'\u043f\u043e\u0445', u'\u043e\u0445\u043e',
        u'\u0445\u043e\u0436', u'\u043e\u0436\u0438', u'\u0436\u0438\u0435', u'\u0438\u0435 ',
        u'\u0435 \u0441', u' \u0441\u0442', u'\u0441\u0442\u0440', u'\u0442\u0440\u043e',
        u'\u0440\u043e\u043a', u'\u043e\u043a\u0438', u'\u043a\u0438$', u'\u0438$$'
    ]),
]
