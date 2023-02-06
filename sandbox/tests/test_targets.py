# coding=utf-8
from __future__ import absolute_import, unicode_literals, print_function

import re
from unittest import TestCase, main

from sandbox.projects.direct_internal_analytics.laborer.content.test_targets import TestTask1
from sandbox.projects.direct_internal_analytics.laborer_base.imports import get_target_by_name, collect_targets, content_path


class TargetsTestCase(TestCase):
    TITLE_REGEX = re.compile(r"^[a-z0-9][a-z0-9_-]*$")

    def test_get_by_name(self):
        self.assertEqual(
            TestTask1,
            get_target_by_name("projects.direct_internal_analytics.laborer.content.test_targets.TestTask1"),
            "get_target_by_name provides correct class"
        )

    def test_all_targets(self):
        targets = collect_targets([content_path])
        self.assertTrue(targets, "Получили непустой список")

        self.assertIn(TestTask1, targets, "Тестовая таска попала в список")

        for target in targets:
            self.assertRegexpMatches(target.title, self.TITLE_REGEX, "Title of {} is correct".format(target))
            self.assertRegexpMatches(target._namespace, self.TITLE_REGEX, "Namespace of {} is correct".format(target))
            self.assertIn(target.final, (True, False), "Final property of {} is correct".format(target))
            self.assertIsInstance(target.dependencies, (list, tuple),
                                  "Dependencies property of {} is correct".format(target))


if __name__ == '__main__':
    main()
