# coding=utf-8
import cgi
import logging

from sandbox import sdk2
from sandbox.common import errors
from sandbox.projects.metrika import utils
from sandbox.projects.metrika.admins.cosmos import utils as cosmos_utils
from sandbox.projects.metrika.admins.base_metrika_tests import view
from sandbox.projects.metrika.utils import CommonParameters, render, custom_report_logger
from sandbox.projects.metrika.utils.base_metrika_task import BaseMetrikaMixin
from sandbox.projects.metrika.utils.requirements import MetrikaLargeRequirements


class BaseMetrikaTests(BaseMetrikaMixin):
    """
    Базовый класс задач тестов Метрики
    """

    class Requirements(MetrikaLargeRequirements):
        pass

    class Parameters(CommonParameters):
        check_test_results = cosmos_utils.CheckTestsResultParameters()

        reporting = cosmos_utils.ReportStartrekParameters()

        report_ttl_params = cosmos_utils.ReportTtlParameters()

        with sdk2.parameters.Output:
            with sdk2.parameters.Group("Результаты тестов") as output:
                report_resource = sdk2.parameters.Resource("Отчёты", description="Ресурс, содержащий отчёты выполнения тестов", required=True)

                test_results = sdk2.parameters.JSON("Результаты тестов", description="Краткие результаты тестов", required=True)

    def shortcut(self):
        raise NotImplementedError()

    def report_description(self):
        raise NotImplementedError()

    def _report_startrek(self):
        try:
            issue = self.st_client.issues[self.Parameters.issue_key]
            issue.comments.create(text=self.get_wiki_comment())
        except Exception as e:
            self.set_info(e.message)
            logging.warning("Ошибка в отправке комментария в Startrek", exc_info=True)

    def _analyze_results(self):
        if int(self.Parameters.test_results["total"]) == 0:
            raise cosmos_utils.NoTestsRunException()

        if self.Parameters.fail_task_on_test_failure:
            if not self.is_all_tests_passed:
                raise cosmos_utils.TestFailures()

    @property
    def is_all_tests_passed(self):
        if self.Parameters.test_results:
            return int(self.Parameters.test_results["failed"]) == 0
        else:
            raise errors.TaskError("Результаты тестов недоступны")

    @sdk2.header()
    @custom_report_logger
    def header(self):
        return self.get_html_comment()

    @sdk2.report(utils.display("wiki-комментарий"))
    @custom_report_logger
    def wiki_comment(self):
        return "<pre>" + self.get_wiki_comment() + "</pre>"

    @sdk2.report(utils.display("html-комментарий"))
    @custom_report_logger
    def html_comment(self):
        return "<pre>" + cgi.escape(self.get_html_comment()) + "</pre>"

    def _get_view_model(self):
        return view.ViewModel(self)

    def get_wiki_comment(self):
        return render("wiki.jinja2", {"view": self._get_view_model()})

    def get_html_comment(self):
        return render("html.jinja2", {"view": self._get_view_model()})
