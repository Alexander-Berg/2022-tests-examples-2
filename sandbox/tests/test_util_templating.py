# coding=utf-8
from __future__ import absolute_import, unicode_literals, print_function

from datetime import date
from unittest import TestCase, main

from sandbox.projects.direct_internal_analytics.laborer.util.templating import smart_apply_template


class TemplatingTestCase(TestCase):
    def setUp(self):
        self.context = {
            'date': date(2017, 10, 3)
        }

    def test_format(self):
        self.assertEqual(smart_apply_template("{date} - {date}", self.context), '2017-10-03 - 2017-10-03')

    def test_no_data(self):
        self.assertEqual(smart_apply_template("Some string", self.context), 'Some string')

    def test_jinja(self):
        self.assertEqual(smart_apply_template("{{date}} - {date}", self.context), '2017-10-03 - {date}')

    def test_jinja_minus_days(self):
        self.assertEqual(smart_apply_template("{{date}}\n{{ (date|minus_days(4)).isoformat() }}", self.context),
                         '2017-10-03\n2017-09-29')

    def test_jinja_other_tags(self):
        self.assertEqual(smart_apply_template("Text{# comment #}\n{% for i in (1,2) %}{{ i }}{% endfor %}", self.context),
                         'Text\n12')

    def test_jinja_minus_days_no_escaping(self):
        self.assertEqual(smart_apply_template("<br><{{date}}></{{date|minus_days(4)}}>", self.context),
                         '<br><2017-10-03></2017-09-29>')

    def test_jinja_day_fmt(self):
        self.assertEqual(
            smart_apply_template("{{date|format_date('Test date: %Y-%m-%d %H:%M:%S')}}", self.context),
            'Test date: 2017-10-03 00:00:00')

    def test_format_day_fmt(self):
        self.assertEqual(smart_apply_template("{date:%Y-%m-%d}", self.context), '2017-10-03')

    def test_jinja_minus_days_no_escaping_x(self):
        self.assertEqual(smart_apply_template("<br><{{date}}></{{date|minus_days(4)|format_date('%Y-%m-%d')}}>", self.context),
                         '<br><2017-10-03></2017-09-29>')


if __name__ == '__main__':
    main()
