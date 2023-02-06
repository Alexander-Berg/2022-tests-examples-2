# coding=utf-8
import logging

from sandbox import sdk2
from sandbox.common import config
from sandbox.common.types import client
from sandbox.projects.common import binary_task
from sandbox.projects.metrika.admins import base_metrika_tests_run
from sandbox.projects.metrika.core import base_metrika_core_tests_run
from sandbox.projects.metrika.core.metrika_core_local_functional_tests_run import tests_helper
from sandbox.projects.metrika.utils import base_metrika_task
from sandbox.projects.metrika.utils import settings
from sandbox.sdk2 import helpers, parameters
from sandbox.sdk2.vcs.svn import Arcadia


@base_metrika_task.with_parents
class MetrikaCoreLocalFunctionalTestsRun(base_metrika_core_tests_run.BaseMetrikaCoreTestsRun):
    """
    Функциональное тестирование демонов Движка Метрики
    """

    class Requirements(base_metrika_core_tests_run.BaseMetrikaCoreTestsRun.Requirements):
        privileged = True
        client_tags = (client.Tag.MULTISLOT | client.Tag.GENERIC) & client.Tag.Group.LINUX & client.Tag.SSD

    class Parameters(base_metrika_core_tests_run.BaseMetrikaCoreTestsRun.Parameters):
        description = "Функциональное тестирование демонов Движка Метрики"

        kill_timeout = 7 * 60 * 60

        with parameters.Group("Tests") as tests_block:
            packages = sdk2.parameters.Dict("Пакеты", required=True, default={},
                                            description="Пакеты, которые будут тестироваться. Если версия не указана - будет установлена stable версия пакета.")

            tests = parameters.String("Тесты", required=True, default="*",
                                      description="Спецификация тестов для выполнения. http://maven.apache.org/surefire/maven-surefire-plugin/examples/single-test.html")

            use_custom_host = parameters.Bool("Произвольный хост", required=True, default=False,
                                              description="Запуск тестов на произвольном хосте. По умолчанию запускается на SB агенте")

            with use_custom_host.value[True]:
                custom_host = parameters.String("Хост", required=True, default="",
                                                description="FQDN хоста, на котором будут запускаться тесты")

        _binary = binary_task.binary_release_parameters_list(stable=True)

    def on_prepare(self):
        self.Context.host = self.Parameters.custom_host if self.Parameters.use_custom_host else "localhost"
        self.Context.hostname = self.Parameters.custom_host if self.Parameters.use_custom_host else config.Registry().this.fqdn

        with sdk2.helpers.ProgressMeter("Checkout"):
            self._checkout_branch()

    @base_metrika_task.exclude_parents(base_metrika_tests_run.BaseMetrikaTestsRun)
    def on_execute(self):
        with sdk2.ssh.Key(self, settings.owner, settings.ssh_key):
            with helpers.ProgressMeter("Preparation"):
                self._preparation()
            with sdk2.helpers.ProgressMeter("Build steps"):
                self._build()
            try:
                with sdk2.helpers.ProgressMeter("Run tests"):
                    self._run_tests()
            except:
                logging.error("Exception during tests run.", exc_info=True)
                raise
            finally:
                with sdk2.helpers.ProgressMeter("Build Report"):
                    self._generate_report()
                if not self.Parameters.use_custom_host:
                    with sdk2.helpers.ProgressMeter("Archive Directories"):
                        self._archive_additional_directories()
                if self.Parameters.report_startrek:
                    with sdk2.helpers.ProgressMeter("Comment Issue"):
                        self._report_startrek()
                with sdk2.helpers.ProgressMeter("Analyze Results"):
                    self._analyze_results()

    def shortcut(self):
        return "ФТ"

    def project_name(self):
        return "metrika-core-tests-functional"

    def report_description(self):
        return "Протокол функциональных тестов Движка Метрики"

    def _preparation(self):
        tests_helper.TestsHelper.prepare(self, self.Parameters.packages, self.Parameters.custom_host)

    def _run_tests(self):
        properties = {
            "ssh.user": settings.login,
            "host": self.Context.host,
            "hostname": self.Context.hostname,
            "ssh.port": 22,
            "test": self.Parameters.tests,
            "maven.test.failure.ignore": "true",
            "allure.report.remove.attachments": "",
            "branch": Arcadia.parse_url(self.Parameters.arcadia_url).revision,
        }

        self._execute_maven(["test", "--file", self._pom(), "--projects", self._package_to_build()], properties=properties, cwd=self.wd(), env=self.get_environment())

    def _get_additional_directories(self):
        return {
            "/etc": ["clickhouse-server", "mysql", "zookeeper", "counters-server", "goals-server", "user-attr-server"],
            "/var/log": ["clickhouse-server", "mysql", "zookeeper", "counters-server", "goals-server", "user-attr-server"]
        }
