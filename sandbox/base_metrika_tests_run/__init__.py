# coding=utf-8
import logging

from sandbox.projects.resource_types import TASK_CUSTOM_LOGS

from sandbox import sdk2
from sandbox.projects.metrika.admins import base_metrika_tests
from sandbox.projects.metrika.admins.cosmos import utils as cosmos_utils
from sandbox.projects.metrika.admins.cosmos.utils import surefire_report
from sandbox.projects.metrika.utils import artifacts
from sandbox.projects.metrika.utils import parameters
from sandbox.projects.metrika.utils import settings
from sandbox.projects.metrika.utils import vcs
from sandbox.projects.metrika.utils.mixins import maven
from sandbox.sdk2 import Path


class BaseMetrikaTestsRun(base_metrika_tests.BaseMetrikaTests, maven.BaseMavenMixin, sdk2.Task):
    """
    Базовый класс запуска тестов Метрики
    """

    class Parameters(base_metrika_tests.BaseMetrikaTests.Parameters):
        container = parameters.LastPeasantContainerResource("Environment container resource", required=True)

        vcs_block = parameters.VcsParameters()

    def on_execute(self):
        with sdk2.ssh.Key(self, settings.owner, settings.ssh_key):
            with sdk2.helpers.ProgressMeter("Checkout"):
                self._checkout_branch()
            with sdk2.helpers.ProgressMeter("Build tests"):
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
                if self.Parameters.report_startrek:
                    with sdk2.helpers.ProgressMeter("Comment Issue"):
                        self._report_startrek()
                with sdk2.helpers.ProgressMeter("Analyze Results"):
                    self._analyze_results()

    def _build(self):
        raise NotImplementedError()

    def _run_tests(self):
        raise NotImplementedError()

    def _package_to_build(self):
        raise NotImplementedError()

    def _target_dir_path(self, *path):
        return Path(self.wd("target", *path))

    def _target_dir(self, *path):
        return self._target_dir_path(*path).as_posix()

    def _artifacts_dir(self):
        return self.path("artifacts").as_posix()

    def _pom(self):
        return self.wd("pom.xml")

    def _checkout_branch(self):
        vcs.checkout(self.Parameters.vcs_block, self.wd())

    def _generate_report(self):
        artifact_dirs = ["logs", "surefire-reports", "allure-results", "site"]
        try:
            self.Parameters.test_results = surefire_report.parse_surefire_reports(self._target_dir_path("surefire-reports"))

            self._execute_maven(["site", "--file", self._pom(), "--projects", self._package_to_build()], cwd=self.wd())
        except:
            logging.warning("Ошибка в генерации отчёта, чего быть не должно.", exc_info=True)
            raise cosmos_utils.ReportNotGenerated()
        finally:
            self.Parameters.report_resource = artifacts.archive_artifacts(self, self._target_dir(), self._artifacts_dir(), TASK_CUSTOM_LOGS, *artifact_dirs, ttl=self.Parameters.report_ttl)
