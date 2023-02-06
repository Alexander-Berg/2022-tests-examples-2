# -*- coding: utf-8 -*
from nose.tools import eq_
from passport.backend.oauth.admin.admin.templatetags.core import url_set_arg
from passport.backend.oauth.core.test.framework import BaseTestCase


class TemplateTagsTestcase(BaseTestCase):
    def test_url_set_arg(self):
        for url, param, value, expected_result in (
            ('https://yandex.ru', 'p', 1, 'https://yandex.ru?p=1'),
            ('https://yandex.ru?p=2', 'p', 1, 'https://yandex.ru?p=1'),
            ('https://yandex.ru?q=2', 'p', 1, 'https://yandex.ru?q=2&p=1'),
        ):
            eq_(url_set_arg(url, param, value), expected_result)
