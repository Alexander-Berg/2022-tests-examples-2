# coding: utf-8

import re

from passport.backend.vault.api.test.base_test_class import BaseTestClass


class TestGenerateCommands(BaseTestClass):
    maxDiff = None

    def setUp(self):
        super(TestGenerateCommands, self).setUp()
        self.runner = self.app.test_cli_runner()

    def test_schema_ok(self):
        with self.app.app_context():
            result = self.runner.invoke(self.cli, ['generate', 'schema'])
            self.assertEqual(result.exit_code, 0)
            self.assertRegexpMatches(result.output, re.compile(r'CREATE\sTABLE\ssecrets\s\(.+?CREATE\sINDEX', re.DOTALL))

    def test_schema_dialect_error(self):
        with self.app.app_context():
            result = self.runner.invoke(self.cli, ['generate', 'schema', '--dialect', 'unknown'])
            self.assertEqual(result.exit_code, 1)
            self.assertEqual(result.output, u'Dialect "unknown" not found\n')

    def test_sql_for_ok(self):
        with self.app.app_context():
            result = self.runner.invoke(self.cli, ['generate', 'sql_for', 'Secret'])
            self.assertEqual(result.exit_code, 0)
            self.assertRegexpMatches(result.output, re.compile(r'CREATE\sTABLE\ssecrets\s\(.+?CREATE\sINDEX', re.DOTALL))

    def test_sql_for_dialect_error(self):
        with self.app.app_context():
            result = self.runner.invoke(self.cli, ['generate', 'sql_for', 'Secret', '--dialect', 'unknown'])
            self.assertEqual(result.exit_code, 1)
            self.assertEqual(result.output, u'Dialect "unknown" not found\n')

    def test_sql_for_model_error(self):
        with self.app.app_context():
            result = self.runner.invoke(self.cli, ['generate', 'sql_for', 'UnknownModel'])
            self.assertEqual(result.exit_code, 1)
            self.assertEqual(result.output, u'Model "UnknownModel" not found.\n')

    def test_generate_keys(self):
        with self.app.app_context():
            result = self.runner.invoke(self.cli, ['generate', 'keys'])
            self.assertEqual(result.exit_code, 0)
            self.assertRegexpMatches(result.output, re.compile(r'^2\d{5}\s[a-zA-Z0-9_-]{24}$', re.MULTILINE))
            self.assertEqual(len(result.output.split('\n')), 145)
