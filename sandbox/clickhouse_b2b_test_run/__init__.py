# coding=utf-8
import logging
import os

from sandbox import sdk2
from sandbox.projects.common import binary_task
from sandbox.projects.metrika.admins import base_metrika_tests_run
from sandbox.projects.metrika.admins.clickhouse.clickhouse_b2b_test_requests_download import ClickHouseB2BTestRequestsResource
from sandbox.projects.metrika.utils.base_metrika_task import with_parents
from sandbox.sdk2 import parameters


@with_parents
class ClickHouseB2BTestRun(base_metrika_tests_run.BaseMetrikaTestsRun):
    """
    B2B тесты API
    """
    name = "CLICKHOUSE_B2B_TEST_RUN"

    class Parameters(base_metrika_tests_run.BaseMetrikaTestsRun.Parameters):
        description = "B2B тесты API"

        kill_timeout = 48 * 60 * 60  # Ждём результата не более двух суток.

        with parameters.Group("Параметры теста") as tests_block:
            requests_resource = ClickHouseB2BTestRequestsResource("Тестовые запросы", required=True, description="Ресурс с тестовыми запросами")

            portion = parameters.Float("Доля запросов", required=True, description="Для каждого вида запросов какова должна быть их удельная доля среди всех запросов данного вида за период.")

            limit = parameters.Integer("Максимальное количество запросов каждого вида", required=True, default=1000, description="Ограничение сверху для каждого вида запросов.")

            start_date = parameters.String('Начальная дата, в формате YYYY-MM-DD', required=True)

            finish_date = parameters.String('Конечная дата, в формате YYYY-MM-DD', required=True)

            threads = parameters.Integer("Количество потоков", default=16,
                                         description="Количество потоков выполнения запросов. "
                                                     "Каждый поток последовательно выполняет два запроса - по одному на каждый полустенд, проводит анализ и записывает файл детального отчёта.")

            faced_api_test = parameters.Url("URL API faced на тестовом полустенде")
            faced_api_ref = parameters.Url("URL API faced на образцовом полустенде")

            mobmetd_api_test = parameters.Url("URL API mobmetd на тестовом полустенде")
            mobmetd_api_ref = parameters.Url("URL API mobmetd на образцовом полустенде")

            properties = parameters.Dict("Дополнительные Java-properties", default={})

        with parameters.Group("Секреты") as secrets_group:
            yav_token = parameters.Vault("OAuth-токен для доступа к секретнице", required=True, default="METRIKA:robot-metrika-test-yav")

        _binary = binary_task.binary_release_parameters_list(stable=True)

    def on_prepare(self):
        os.environ.update({"VAULT_TOKEN": self.Parameters.yav_token.data()})

    def shortcut(self):
        return "B2B API"

    def report_description(self):
        return "Протокол B2B тестов API"

    def _package_to_build(self):
        return "ru.yandex.autotests.metrika:clickhouse-b2b-tests"

    def _build(self):
        pass

    def _run_tests(self):
        if not (
            self.Parameters.faced_api_test and self.Parameters.faced_api_ref or
            self.Parameters.mobmetd_api_test and self.Parameters.mobmetd_api_ref
        ):
            raise Exception('Specify stands urls for at least one daemon (faced, mobmetd)')

        requests_dir = sdk2.ResourceData(self.Parameters.requests_resource).path.as_posix()

        logging.info("Requests directory: {}".format(requests_dir))

        properties = {
            "requests.base.dir": requests_dir,
            "faced.api.test": self.Parameters.faced_api_test,
            "faced.api.ref": self.Parameters.faced_api_ref,
            "mobmetd.api.test": self.Parameters.mobmetd_api_test,
            "mobmetd.api.ref": self.Parameters.mobmetd_api_ref,
            "start.date": self.Parameters.start_date,
            "finish.date": self.Parameters.finish_date,
            "limit.absolute": self.Parameters.limit,
            "limit.relative": self.Parameters.portion,
            "fork.pool.size": self.Parameters.threads
        }

        properties.update({key: value for key, value in self.Parameters.properties.iteritems()})

        self._execute_maven(["test", "--file", self._pom(), "--projects", self._package_to_build()], properties=properties, cwd=self.wd())

    def _generate_report(self):
        super(ClickHouseB2BTestRun, self)._generate_report()
        self.set_info('<a href="{}/site/response-report/index.html">Results</a>'.format(self.Parameters.report_resource.http_proxy), do_escape=False)
