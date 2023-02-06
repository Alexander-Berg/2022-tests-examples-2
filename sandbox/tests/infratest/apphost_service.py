# -*- coding: utf-8 -*-

import unittest

from sandbox.projects.sandbox_ci.infratest.apphost_service_create_package.utils import generate_content, parse_pr


class TestsGenerateContent(unittest.TestCase):
    maxDiff = None

    def test_should_replace_releasers(self):
        content = 'class WebProjectTemplatesPackage(ReportWebTemplatesPackage):\n' +\
                  '    releasers = [\'aaa\', \'bbb\'] + ROBOTS + INFRA_TEAM'
        actual = generate_content(content, dict(name='WebProjectTemplatesPackage', releasers=['bbb', 'ccc']))
        expected = '# -*- coding: utf-8 -*-\n\n' +\
                   '# Данный файл содержит типы ресурсов для проектов монорепо frontend,\n' +\
                   '# сгенерированные при помощи команды пакета apphost-service.\n' +\
                   '# Файл изменяется только при помощи утилиты, сделанные вручную изменения будут утеряны.\n\n' +\
                   'from releasers import *\n' +\
                   'from template_packages import ReportWebTemplatesPackage\n\n\n' +\
                   'class WebProjectTemplatesPackage(ReportWebTemplatesPackage):\n' +\
                   '    releasers = [\'bbb\', \'ccc\'] + ROBOTS + INFRA_TEAM\n'

        self.assertMultiLineEqual(actual, expected)

    def test_should_insert_new_package_before_old(self):
        content = 'class WebProjectTemplatesPackage(ReportWebTemplatesPackage):\n' + \
                  '    releasers = [\'aaa\', \'bbb\'] + ROBOTS + INFRA_TEAM'
        actual = generate_content(content, dict(name='WebAaaBbbTemplatesPackage', releasers=['aaa', 'bbb']))
        expected = '# -*- coding: utf-8 -*-\n\n' +\
                   '# Данный файл содержит типы ресурсов для проектов монорепо frontend,\n' +\
                   '# сгенерированные при помощи команды пакета apphost-service.\n' +\
                   '# Файл изменяется только при помощи утилиты, сделанные вручную изменения будут утеряны.\n\n' +\
                   'from releasers import *\n' +\
                   'from template_packages import ReportWebTemplatesPackage\n\n\n' +\
                   'class WebAaaBbbTemplatesPackage(ReportWebTemplatesPackage):\n' +\
                   '    releasers = [\'aaa\', \'bbb\'] + ROBOTS + INFRA_TEAM\n\n\n' +\
                   'class WebProjectTemplatesPackage(ReportWebTemplatesPackage):\n' +\
                   '    releasers = [\'aaa\', \'bbb\'] + ROBOTS + INFRA_TEAM\n'

        self.assertMultiLineEqual(actual, expected)

    def test_should_insert_new_package_after_old(self):
        content = 'class WebProjectTemplatesPackage(ReportWebTemplatesPackage):\n' + \
                  '    releasers = [\'aaa\', \'bbb\'] + ROBOTS + INFRA_TEAM'
        actual = generate_content(content, dict(name='WebWwwTemplatesPackage', releasers=['www', 'yyy']))
        expected = '# -*- coding: utf-8 -*-\n\n' +\
                   '# Данный файл содержит типы ресурсов для проектов монорепо frontend,\n' +\
                   '# сгенерированные при помощи команды пакета apphost-service.\n' +\
                   '# Файл изменяется только при помощи утилиты, сделанные вручную изменения будут утеряны.\n\n' +\
                   'from releasers import *\n' +\
                   'from template_packages import ReportWebTemplatesPackage\n\n\n' +\
                   'class WebProjectTemplatesPackage(ReportWebTemplatesPackage):\n' +\
                   '    releasers = [\'aaa\', \'bbb\'] + ROBOTS + INFRA_TEAM\n\n\n' +\
                   'class WebWwwTemplatesPackage(ReportWebTemplatesPackage):\n' +\
                   '    releasers = [\'www\', \'yyy\'] + ROBOTS + INFRA_TEAM\n'

        self.assertMultiLineEqual(actual, expected)


class TestsParsePr(unittest.TestCase):
    def test_should_parse(self):
        content = 'Creating Arcanum PR\n' +\
                  'Info: Source: svn\n\n' +\
                  'Changes:\n' +\
                  ' M generated.py\n\n' +\
                  'Info: Session: 4939929-39kyn\n' +\
                  'Info: PR: 791666, iteration 1\n\n' +\
                  'https://a.yandex-team.ru/review/791666\n'

        self.assertEqual(parse_pr(content), '791666')

    def test_should_return_none(self):
        content = 'Some log'

        self.assertEqual(parse_pr(content), None)
