# coding: utf-8

from passport.backend.vault.api.test.base_test_class import BaseTestClass


class TestFindCommands(BaseTestClass):
    maxDiff = None

    def setUp(self):
        super(TestFindCommands, self).setUp()
        self.runner = self.app.test_cli_runner()

    def test_find_abc_by_id_ok(self):
        with self.app.app_context():
            result = self.runner.invoke(
                self.cli, ['find', 'abc', '50'],
            )
            self.assertEqual(result.exit_code, 0)
            self.assertEqual(
                result.output,
                u'Environment: development\n'
                u'\n'
                u'Service: Перевод саджеста\n'
                u'ABC ID: 50\n'
                u'ABC slug: suggest\n'
                u'\n'
                u'Scopes:\n'
                u'+-----------------------------------+-------------------+\n'
                u'| owner:abc:50:scope:administration | Администрирование |\n'
                u'| owner:abc:50:scope:development    | Разработка        |\n'
                u'+-----------------------------------+-------------------+\n'
                u'\n'
                u'Roles:\n'
                u'+----------------------+-------------------------+\n'
                u'| owner:abc:50:role:8  | Разработчик             |\n'
                u'| owner:abc:50:role:16 | Системный администратор |\n'
                u'+----------------------+-------------------------+\n'
                u'\n'
            )

    def test_find_abc_by_slug_ok(self):
        with self.app.app_context():
            result = self.runner.invoke(
                self.cli, ['find', 'abc', 'suggest'],
            )
            self.assertEqual(result.exit_code, 0)
            self.assertEqual(
                result.output,
                u'Environment: development\n'
                u'\n'
                u'Service: Перевод саджеста\n'
                u'ABC ID: 50\n'
                u'ABC slug: suggest\n'
                u'\n'
                u'Scopes:\n'
                u'+-----------------------------------+-------------------+\n'
                u'| owner:abc:50:scope:administration | Администрирование |\n'
                u'| owner:abc:50:scope:development    | Разработка        |\n'
                u'+-----------------------------------+-------------------+\n'
                u'\n'
                u'Roles:\n'
                u'+----------------------+-------------------------+\n'
                u'| owner:abc:50:role:8  | Разработчик             |\n'
                u'| owner:abc:50:role:16 | Системный администратор |\n'
                u'+----------------------+-------------------------+\n'
                u'\n'
            )

    def test_find_abc_error(self):
        with self.app.app_context():
            result = self.runner.invoke(
                self.cli, ['find', 'abc', 'unknown_service'],
            )
            self.assertEqual(result.exit_code, 1)
            self.assertEqual(
                result.output,
                u'Environment: development\n'
                u'\n'
                u'Service "unknown_service" not found\n'
            )
