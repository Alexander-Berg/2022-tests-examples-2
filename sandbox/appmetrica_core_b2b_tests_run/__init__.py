# coding=utf-8
import logging
import os
import shutil

from sandbox import sdk2
from sandbox.projects.common import binary_task
from sandbox.projects.metrika.admins import base_metrika_tests, base_metrika_tests_run
from sandbox.projects.metrika.core import base_metrika_core_tests_run
from sandbox.projects.metrika.core.appmetrica_core_b2b_scenario_execute import tests_helper as scenario_helper
from sandbox.projects.metrika.core.appmetrica_core_b2b_tests_run import tests_helper
from sandbox.projects.metrika.core.utils import metrika_core_tests_helper
from sandbox.projects.metrika.utils import base_metrika_task, parameters as metrika_parameters, resource_types, settings, vcs
from sandbox.sdk2 import helpers, parameters


@base_metrika_task.with_parents
class AppMetricaCoreB2bTestsRun(base_metrika_core_tests_run.BaseMetrikaCoreTestsRun):
    """
    B2B тестирование демонов Движка АппМетрики
    """
    name = "APPMETRICA_CORE_B2B_TESTS_RUN"

    class Context(sdk2.Context):
        test_packages_versions = {}
        stable_packages_versions = {}
        scenarios_task_ids = []
        test_resource_id = None
        test_resource_task = False
        stable_resource_id = None
        stable_resource_task = False

    class Requirements(base_metrika_core_tests_run.BaseMetrikaCoreTestsRun.Requirements):
        privileged = True

    class Parameters(base_metrika_tests.BaseMetrikaTests.Parameters):
        description = "B2B тестирование демонов Движка АппМетрики"

        container = metrika_parameters.LastPeasantContainerResource("Environment container resource", required=True)

        with parameters.Group("VCS") as vcs_common_block:
            arcadia_url = metrika_parameters.ArcadiaURL("URL Аркадии", required=True)

        with parameters.Group("Tests") as tests_block:
            test_packages = parameters.Dict(
                "Тестируемые пакеты",
                description="Пакеты, которые будут тестироваться. Если версия не указана - будет установлена stable версия пакета"
            )

            test_clickhouse_resource = parameters.Resource(
                "Тестовый ресурс с ClickHouse",
                required=False, resource_type=resource_types.MetrikaClickhouseBinary)

            force_test_scenario = parameters.Bool(
                "Принудительно прогнать тестовый сценарий",
                description="Независимо от наличия ресурса с результатами"
            )

            with force_test_scenario.value[False]:
                use_custom_test_resource = parameters.Bool(
                    "Использовать произвольный тестируемый ресурс с выходными данными",
                    description="Сценарий при этом не запускается"
                )

                with use_custom_test_resource.value[True]:
                    test_resource = parameters.Resource(
                        "Тестируемый ресурс с выходными тестовыми данными",
                        required=True, resource_type=metrika_core_tests_helper.AppMetricaCoreOutputB2bTestData,
                        description="Содержит результаты работы тестового сценария"
                    )

            stable_packages = parameters.Dict(
                "Эталонные пакеты",
                description="Пакеты, с которыми будет проводиться сравнение"
            )

            stable_clickhouse_resource = parameters.Resource(
                "Эталонный ресурс с ClickHouse",
                required=False, resource_type=resource_types.MetrikaClickhouseBinary)

            force_stable_scenario = parameters.Bool(
                "Принудительно прогнать стабильный сценарий",
                description="Независимо от наличия ресурса с результатами"
            )

            with force_stable_scenario.value[False]:
                use_custom_stable_resource = parameters.Bool(
                    "Использовать произвольный эталонный ресурс с выходными данными",
                    description="Сценарий при этом не запускается"
                )

                with use_custom_stable_resource.value[True]:
                    stable_resource = parameters.Resource(
                        "Эталонный ресурс с выходными тестовыми данными",
                        required=True, resource_type=metrika_core_tests_helper.AppMetricaCoreOutputB2bTestData,
                        description="Содержит результаты работы стабильного сценария"
                    )

            local_daemons = sdk2.parameters.Bool("Запускать конвейер с демонами из ветки (не использовать ресурсы)", required=True, default=False)

            local_configs = sdk2.parameters.Bool("Запускать конвейер с конфигами из ветки (не использовать ресурсы)", required=True, default=False)

            fast = sdk2.parameters.Bool("Запускать быстрый конвейер (используется урезанный Исток)", required=True, default=False)

        _binary = binary_task.binary_release_parameters_list(stable=True)

    @base_metrika_task.exclude_parents(base_metrika_tests_run.BaseMetrikaTestsRun)
    def on_execute(self):
        with sdk2.ssh.Key(self, settings.owner, settings.ssh_key):
            with sdk2.helpers.ProgressMeter("Versions"):
                self._get_packages_versions()
            with sdk2.helpers.ProgressMeter("Scenarios"):
                self._get_scenarios_result()
            with sdk2.helpers.ProgressMeter("Checkout"):
                with vcs.mount_arc(self.Parameters.arcadia_url) as arcadia:
                    shutil.copytree(os.path.join(arcadia, "metrika/core/tests"), self.wd())
            with helpers.ProgressMeter("Preparation"):
                self._preparation()
            with helpers.ProgressMeter("Extraction"):
                self._extraction()
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
                with sdk2.helpers.ProgressMeter("Archive Directories"):
                    self._archive_additional_directories()
                if self.Parameters.report_startrek:
                    with sdk2.helpers.ProgressMeter("Comment Issue"):
                        self._report_startrek()
                with sdk2.helpers.ProgressMeter("Analyze Results"):
                    self._analyze_results()

    def shortcut(self):
        return "B2B"

    def project_name(self):
        return "metrika-core-tests-b2b-appmetrica"

    def report_description(self):
        return "Протокол B2B тестов Движка АппМетрики"

    def _get_packages_versions(self):
        return scenario_helper.TestsHelper._get_different_url_packages_versions(self, self.Parameters.arcadia_url)

    def _get_scenarios_result(self):
        tests_helper.TestsHelper._get_scenarios_result(self, metrika_core_tests_helper.AppMetricaCoreOutputB2bTestData)

    def _preparation(self):
        tests_helper.TestsHelper.prepare(self)

    def _extraction(self):
        tests_helper.TestsHelper.extract_tests_output_resources(self, self.Context.test_resource_id, self.Context.stable_resource_id)

    def _run_tests(self):
        properties = {
            "ssh.user": settings.login,
            "ssh.port": 22,
            "test": "b2b.verification.**.*",
            "maven.test.failure.ignore": "true",
            "b2b.stand.test": "localhost",
            "b2b.stand.stable": "localhost",
            "b2b.stand.test.prefix": metrika_core_tests_helper.TEST_PREFIX,
            "b2b.stand.stable.prefix": metrika_core_tests_helper.STABLE_PREFIX,
            "allure.report.remove.attachments": ""
        }

        self._execute_maven(["test", "--file", self._pom(), "--projects", self._package_to_build()], properties=properties, cwd=self.wd())
