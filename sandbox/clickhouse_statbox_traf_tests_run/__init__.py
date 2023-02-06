# coding=utf-8
import logging

from sandbox import sdk2
from sandbox.common import errors
from sandbox.projects.common import binary_task
from sandbox.projects.metrika.admins.clickhouse.clickhouse_statbox_traf_queries_prepare import ClickHouseB2BStatBoxTrafQueriesResource
from sandbox.projects.metrika.admins import base_metrika_tests_run
from sandbox.projects.metrika.utils.base_metrika_task import with_parents
from sandbox.sdk2 import parameters


@with_parents
class ClickHouseStatboxTrafTestRun(base_metrika_tests_run.BaseMetrikaTestsRun):
    """
    B2B тесты Трафа
    """
    name = "CLICKHOUSE_STATBOX_TRAF_TESTS_RUN"

    class Parameters(base_metrika_tests_run.BaseMetrikaTestsRun.Parameters):
        description = "B2B тесты Трафа"

        with parameters.Group("Параметры теста") as tests_block:
            queries = ClickHouseB2BStatBoxTrafQueriesResource("Тестовые запросы", required=True)
            test_uri = parameters.Url("Тестируемый инстанс ClickHouse", required=True)
            stable_uri = parameters.Url("Образцовый инстанс ClickHouse", required=True)

            properties = parameters.Dict("Дополнительные Java-properties", default={})

        with parameters.Group("Секреты") as secrets_group:
            ch_user = parameters.String("ClickHouse user", required=True, default="robot-metrika-traf-test")
            ch_password = sdk2.parameters.YavSecret('ClickHouse password', required=True, default='sec-01fayv6gt8nfdtfhpjn4hppr7e#password')

        _binary = binary_task.binary_release_parameters_list(stable=True)

    def on_enqueue(self):
        if not self.Parameters.test_uri or not self.Parameters.stable_uri:
            raise errors.TaskFailure("Не задан тестируемый инстанс!")

    def shortcut(self):
        return "B2B Трафа"

    def report_description(self):
        return "Протокол B2B тестов Трафа"

    def _package_to_build(self):
        return "ru.yandex.autotests.metrika:clickhouse-statbox-tests"

    def _build(self):
        pass

    def _run_tests(self):
        queries_dir = sdk2.ResourceData(self.Parameters.queries).path.as_posix()

        logging.info("Queries directory: {}".format(queries_dir))

        properties = {
            "queries.base.dir": queries_dir,
            "uri.test": self.Parameters.test_uri,
            "uri.ref": self.Parameters.stable_uri,
            "user": self.Parameters.ch_user,
            "password": self.Parameters.ch_password.data()[self.Parameters.ch_password.default_key]
        }

        properties.update({key: value for key, value in self.Parameters.properties.iteritems()})

        self._execute_maven(["test", "--file", self._pom(), "--projects", self._package_to_build()], properties=properties, cwd=self.wd())
