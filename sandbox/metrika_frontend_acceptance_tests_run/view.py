# coding=utf-8
from sandbox.common import utils


class ViewModel(object):

    def __init__(self, task):
        self.task = task

    @property
    def id(self):
        return self.task.id

    @property
    def type(self):
        return self.task.type.name

    @property
    def shortcut(self):
        return self.task.shortcut

    @property
    def link(self):
        return utils.get_task_link(self.task.id)

    @property
    def has_report_link(self):
        return self.task.Parameters.report_resource is not None

    @property
    def report_link(self):
        return self.task.Parameters.report_resource.http_proxy

    @property
    def has_statistics(self):
        return self.task.Parameters.tests_statistics is not None

    @property
    def suites_total(self):
        return self.task.Parameters.tests_statistics["total"] if self.has_statistics else "-"

    @property
    def suites_success(self):
        return self.task.Parameters.tests_statistics["success"] if self.has_statistics else "-"

    @property
    def suites_failed(self):
        return self.task.Parameters.tests_statistics["failed"] if self.has_statistics else "-"

    @property
    def tests_status(self):
        if self.has_statistics:
            if self.suites_failed:
                return "Есть падения тестов"
            else:
                return "Все тесты пройдены"
        else:
            return "Результаты тестов не получены"

    @property
    def report_description(self):
        return self.task.report_description
