# coding=utf-8

from sandbox import sdk2
from sandbox.projects.common import binary_task
from sandbox.projects.metrika.admins import base_metrika_tests, base_metrika_tests_run
from sandbox.projects.metrika.core import base_metrika_core_tests_run, metrika_core_arcadia_tests_run
from sandbox.projects.metrika.core.metrika_core_arcadia_b2b_tests_run import tests_helper
from sandbox.projects.metrika.core.metrika_core_arcadia_tests_run import view
from sandbox.projects.metrika.core.metrika_core_b2b_scenario_execute import tests_helper as scenario_helper
from sandbox.projects.metrika.core.utils import metrika_core_tests_helper
from sandbox.projects.metrika.utils import base_metrika_task, parameters as metrika_parameters, resource_types
from sandbox.sdk2 import parameters


@base_metrika_task.with_parents
class MetrikaCoreArcadiaB2bTestsRun(base_metrika_core_tests_run.BaseMetrikaCoreTestsRun):
    """
    B2B тестирование демонов Движка Метрики
    """
    name = "METRIKA_CORE_ARCADIA_B2B_TESTS_RUN"

    class Context(sdk2.Context):
        test_packages_versions = {}
        stable_packages_versions = {}
        scenarios_task_ids = []
        test_resource_id = None
        test_resource_task = False
        stable_resource_id = None
        stable_resource_task = False

    class Parameters(base_metrika_tests.BaseMetrikaTests.Parameters):
        description = "B2B тестирование демонов Движка Метрики"

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
                        required=True, resource_type=metrika_core_tests_helper.MetrikaCoreOutputB2bTestData,
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
                        required=True, resource_type=metrika_core_tests_helper.MetrikaCoreOutputB2bTestData,
                        description="Содержит результаты работы стабильного сценария"
                    )

            local_daemons = sdk2.parameters.Bool("Запускать конвейер с демонами из ветки (не использовать ресурсы)", required=True, default=False)

            local_configs = sdk2.parameters.Bool("Запускать конвейер с конфигами из ветки (не использовать ресурсы)", required=True, default=False)

            fast = sdk2.parameters.Bool("Запускать быстрый конвейер (используется урезанный Исток)", required=True, default=False)

        _binary = binary_task.binary_release_parameters_list(stable=True)

    @base_metrika_task.exclude_parents(base_metrika_tests_run.BaseMetrikaTestsRun)
    def on_execute(self):
        with sdk2.helpers.ProgressMeter("Versions"):
            self._get_packages_versions()
        with sdk2.helpers.ProgressMeter("Scenarios"):
            self._get_scenarios_result()
        with sdk2.helpers.ProgressMeter("Run tests"):
            self._run_tests()
        with sdk2.helpers.ProgressMeter("Analyze Results"):
            self._analyze_results()

    def shortcut(self):
        return "B2B"

    def project_name(self):
        return "metrika-core-tests-b2b"

    def report_description(self):
        return "Протокол B2B тестов Движка Метрики"

    def _get_view_model(self):
        return view.ViewModel(self)

    def _get_packages_versions(self):
        return scenario_helper.TestsHelper._get_different_url_packages_versions(self, self.Parameters.arcadia_url)

    def _get_scenarios_result(self):
        tests_helper.TestsHelper._get_scenarios_result(self, metrika_core_tests_helper.MetrikaCoreOutputB2bTestData)

    def _run_tests(self):
        self.Context.test_task = self.run_subtasks((
            metrika_core_arcadia_tests_run.MetrikaCoreArcadiaTestsRun,
            dict(
                checkout_arcadia_from_url=self.Parameters.arcadia_url,
                targets="metrika/core/b2b/web/tests",
                fail_task_on_test_failure=False,
                failed_tests_cause_error=False,
                report_startrek=self.Parameters.report_startrek,
                issue_key=self.Parameters.issue_key,
                tests_type="B2B",
                test_size_filter="large",
                definition_flags="-Dtest-resource={} -Dstable-resource={}".format(self.Context.test_resource_id, self.Context.stable_resource_id),
                report_ttl=self.Parameters.report_ttl,
                allure_report_ttl=self.Parameters.report_ttl
            )
        ))[0]
        self.Parameters.report_resource = sdk2.Task[self.Context.test_task].Parameters.report_resource
        self.Parameters.test_results = sdk2.Task[self.Context.test_task].Parameters.test_results
