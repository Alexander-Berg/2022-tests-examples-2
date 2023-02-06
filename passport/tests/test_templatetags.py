# -*- coding: utf-8 -*-
import unittest

from nose.tools import (
    assert_in,
    eq_,
)
from passport.backend.api.templatetags import (
    l,
    T,
    tags,
)
from passport.backend.core.test.test_utils.utils import with_settings


class _TranslationSettings(object):
    MAIL_TEXT = {
        'ru': {
            'subject': u'Аккаунт на Яндексе: добавление телефонного номера',
        }
    }


@with_settings(translations=_TranslationSettings())
class TemplateTagsTestCase(unittest.TestCase):
    """Проверим как работают наши "шаблонные теги"."""

    def test_get_translation(self):
        """Тест зависит от содержимого Танкера =("""
        text = l(dict(language='ru'), 'MAIL_TEXT', 'subject')
        expected_text = u"Аккаунт на Яндексе: добавление телефонного номера"
        eq_(text, expected_text)

    def test_subtemplate(self):
        """Проверим что мы можем получить шаблон,
        который будет воспринимать нестандартные шаблонные теги"""
        template_text = u"Привет, %username%!"
        context = dict(username=u"Чапаев")
        rendered = T(context, template_text)
        expected = u"Привет, Чапаев!"
        eq_(rendered, expected)

    def test_context_processor_completed(self):
        """Все функции должны быть доступны через контекст-процессор"""
        exported_tags = tags()
        assert_in('l', exported_tags)
        assert_in('T', exported_tags)
