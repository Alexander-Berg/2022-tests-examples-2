# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from passport.backend.social.common.fraud import find_url
from passport.backend.social.common.test.test_case import TestCase


class TestFindUrl(TestCase):
    def _assert_ok_urls(self, urls):
        for url in urls:
            self.assertTrue(find_url(url), url)

    def _assert_bad_urls(self, urls):
        for url in urls:
            self.assertFalse(find_url(url), url)

    def test_urls(self):
        self._assert_ok_urls([
            '//foo.xeon',
            '//FOO.XEON',
            '//hello@foo.xeon',
            '//foo.xeon.',
            '//foo.xeon%1)+!%#',
            '//x.foo.xeon',
            '//foo.xeon:80',
            '//login@foo.xeon',
            '//login:password@foo.xeon',
            '//яндекс.рф',
            '//xn--d1acpjx3f.xn--p1ai',

            't.xeon/',
            'T.XEON/',
            't.xeon/lol',
            't.xeon./',
            'x.y.xeon/',
            't.xeon/h%2,%$',
            't.xeon:80/',
            'login@t.xeon/',
            'login:password@t.xeon/',
            'яндекс.рф/',
            'xn--d1acpjx3f.xn--p1ai/',

            't.ru',
            'T.RU',
            't.ru.',
            't.com',
            't.com.',
            't.com.ru',
            't.com.ru.',
            't.ru:80',
            't.ru ',
            'яндекс.рф',
            'xn--d1acpjx3f.xn--p1ai',
            '(t.ru)',
            '[t.ru]',

            '1.2.3.4',
            '1.2.3.4:80',

            '[f::]',
            '[f::]:80',
            '[f::f]',
            '[f::f]:80',
            '[::f:f:f:f:f:f:f]',
            '[::f:f:f:f:f:f:f]:80',
            '[f:f:f:f:f:f:f]',
            '[f:f:f:f:f:f:f]:80',
            '[f:f:f:f:f:f:f:f]',
            '[f:f:f:f:f:f:f:f]:80',

            'scheme://www.bit.ly/gold',
            'приставкаwww.bit.ly/gold',
            'www.bit.ly/goldсуффикс',
        ])

    def test_not_urls(self):
        self._assert_bad_urls([
            'hello@foo.xeon',
            '//xeon',
            '//xeon.',
            '//.xeon',
            't.xeon',
            't.xeon?1',
            '.xeon',
            'xeon/',
            'xeon./',
            'super.xeon',
            'super.xeon.',
            'super.duper.xeon',
            't.rueldo',
            'петров.гриша',
            'xeon.ru.xeon',
            'login@foo.ru',
            'login:password@foo.ru',
            '//..x',
            '..x/',
            '//.x.',
            '.x./',
        ])
