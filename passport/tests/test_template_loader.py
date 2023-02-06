# -*- coding: utf-8 -*-
import os
from os.path import (
    abspath,
    dirname,
    join,
)
import unittest

from jinja2 import TemplateNotFound
import mock
from nose.tools import (
    eq_,
    raises,
)
from passport.backend.utils.template_loader import CachedTemplateLoader
import six


class CachedTemplateLoaderTestCase(unittest.TestCase):
    """
    Тестируется по модели "белый ящик" - если я знаю внутреннее устройство
    загрузчиков из jinja2, то мокаю только ключевые системные функции.
    """

    # Предполагаем, шаблоны лежат в ../templates
    TEMPLATE_DIR = join(dirname(abspath(__file__)), os.pardir, 'templates')

    def setUp(self):
        self.patches = []
        self.setup_resources_mock()
        self.setup_files_walk_mock()
        self.setup_file_read_mock()
        self.setup_getmtime_mock()

        for p in self.patches:
            p.start()

    def tearDown(self):
        for p in self.patches:
            p.stop()
        del self.patches
        del self.walk_mock
        del self.read_mock
        del self.read_resource_mock
        del self.list_resources_mock

    def setup_getmtime_mock(self):
        patch = mock.patch('os.path.getmtime', mock.Mock(return_value=0))
        self.patches.append(patch)

    def setup_files_walk_mock(self):
        self.file_names = [
            'test-first-template-file.html',
            'test-second-template-file.html',
        ]
        # Подготавливаем ответ по которому будет итерировать цикл
        # for a, b, c in os.walk():
        result = [
            (
                self.TEMPLATE_DIR,
                [],
                self.file_names,
            ),
        ]
        self.walk_mock = mock.Mock(return_value=result)
        patch = mock.patch('os.walk', self.walk_mock)

        self.patches.append(patch)

    def setup_resources_mock(self):
        self.resources_names = [
            'templates/test-first-template-file.html',
            'templates/test-second-template-file.html',
        ]
        self.resources_content = [
            'test-first-file-content',
            'test-second-file-content',
        ]
        self.list_resources_mock = mock.Mock(return_value=self.resources_names)
        self.read_resource_mock = mock.Mock(side_effect=self.resources_content)
        patch_list = mock.patch('passport.backend.utils.file._get_resources', self.list_resources_mock)
        patch_read = mock.patch('passport.backend.utils.file.read_file', self.read_resource_mock)
        self.patches.extend([patch_list, patch_read])

    def setup_file_read_mock(self):
        self.files_content = [
            'test-first-file-content',
            'test-second-file-content',
        ]
        self.read_mock = mock.Mock(side_effect=self.files_content)
        open_mock = mock.MagicMock()
        open_mock.return_value.read = self.read_mock
        builtins_name = '__builtin__' if six.PY2 else 'builtins'
        patch = mock.patch('{}.open'.format(builtins_name), open_mock)

        self.patches.append(patch)

    def test_loads_files(self):
        # Загружает шаблоны с диска сразу
        loader = CachedTemplateLoader(self.TEMPLATE_DIR)
        files = loader.list_templates()

        eq_(files, ['test-first-template-file.html', 'test-second-template-file.html'])

        # Еще раз позовем список шаблонов
        loader.list_templates()

        # Поиск файлов на диске произошел только один раз
        eq_(self.walk_mock.call_count + self.list_resources_mock.call_count, 1)
        # Прочитали всего два файла
        eq_(self.read_mock.call_count + self.read_resource_mock.call_count, 2)

    def test_get_files_content(self):
        env = {}
        loader = CachedTemplateLoader(self.TEMPLATE_DIR)

        for filename, expected_content in zip(self.file_names, self.files_content):
            content, _, _ = loader.get_source(env, filename)
            eq_(content, expected_content)

        # Extra: еще один раз вызываем шаблон. для уверенности
        loader.get_source(env, 'test-first-template-file.html')

        # Поиск по диску был 1 раз
        eq_(self.walk_mock.call_count + self.list_resources_mock.call_count, 1)
        # Прочитали всего два файла
        eq_(self.read_mock.call_count + self.read_resource_mock.call_count, 2)

    @raises(TemplateNotFound)
    def test_unknown_template__error(self):
        loader = CachedTemplateLoader(self.TEMPLATE_DIR)

        loader.get_source({}, 'wrong-template-name')
