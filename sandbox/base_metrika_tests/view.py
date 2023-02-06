# coding=utf-8

from sandbox import sdk2
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
        return self.task.shortcut()

    @property
    def link(self):
        return utils.get_task_link(self.task.id)

    @property
    def has_allure_link(self):
        return self.task.Parameters.report_resource is not None

    @property
    def allure_link(self):
        return "{}/site/allure-maven-plugin/index.html".format(sdk2.Resource[self.task.Parameters.report_resource.id].http_proxy)

    @property
    def has_results(self):
        return self.task.Parameters.test_results is not None

    @property
    def suites_total(self):
        return self.task.Parameters.test_results["total"] if self.has_results else "-"

    @property
    def suites_success(self):
        return self.task.Parameters.test_results["success"] if self.has_results else "-"

    @property
    def suites_failed(self):
        return self.task.Parameters.test_results["failed"] if self.has_results else "-"

    @property
    def has_failed_suites(self):
        return self.suites_failed > 0

    @property
    def failed_suites(self):
        return [utils.display(suite) for suite in self.task.Parameters.test_results["failed_suites"]] if self.task.Parameters.test_results else []

    @property
    def tests_status(self):
        if self.has_results:
            return "есть падения тестов" if self.has_failed_suites else "все тесты пройдены"
        else:
            return "результаты тестов не получены"

    @property
    def report_description(self):
        return self.task.report_description()
