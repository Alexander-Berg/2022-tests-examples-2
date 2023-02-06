from odoo import exceptions
from odoo.tests import SavepointCase, tagged

from odoo.addons.lavka.backend.models.task import monitor_task, FUNC_NAMES


FUNC_NAME = FUNC_NAMES[0][0]


@tagged('lavka', 'autoorder', 'tasks')
class TestExportYT(SavepointCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        # динамически задать доступные для выбора func_name в модели autoorder.task
        # нельзя после загрузки модуля, по-этому используем одно из зарегестрированных имен и
        # назначим его тестовым функциям, на результат работы функций это не повлияет
        cls.success_method.__qualname__ = FUNC_NAME
        cls.success_method = monitor_task(cls.success_method)

        cls.error_method.__qualname__ = FUNC_NAME
        cls.error_method = monitor_task(cls.error_method)

    def success_method(self):
        return True

    def error_method(self):
        raise ValueError

    def test_run_tasks(self):
        result = self.success_method()
        self.assertEqual(result, None, 'Запуск без поставленной в очередь задачи')

        task1 = self.env['autoorder.task'].create({
            'func_name': FUNC_NAME,
        })
        result = self.success_method()
        self.assertEqual(result, True, 'Запуск с поставленной в очередь задачей')
        task1 = self.env['autoorder.task'].browse([task1.id])
        self.assertEqual(task1.state, 'done')
        self.assertNotEqual(task1.finished, None)

        task2 = self.env['autoorder.task'].create({
            'func_name': FUNC_NAME,
        })
        self.error_method()
        task2 = self.env['autoorder.task'].browse([task2.id])
        self.assertEqual(task2.state, 'failed')
        self.assertNotEqual(task2.traceback, None)
        self.assertNotEqual(task2.finished, None)

    def test_create_tasks(self):
        self.env['autoorder.task'].create({
            'func_name': FUNC_NAME,
        })
        self.assertRaises(
            exceptions.UserError,
            self.env['autoorder.task'].create,
            {'func_name': FUNC_NAME}
        )
