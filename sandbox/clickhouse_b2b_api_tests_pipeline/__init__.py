# coding=utf-8
from urllib import quote_plus

import requests

from sandbox import sdk2
from sandbox.projects.common import binary_task
from sandbox.projects.common.decorators import memoized_property
from sandbox.projects.metrika.admins.clickhouse.clickhouse_b2b_api_tests_pipeline.state import State
from sandbox.projects.metrika.admins.clickhouse.clickhouse_b2b_test_run import ClickHouseB2BTestRequestsResource
from sandbox.projects.metrika.admins.clickhouse.clickhouse_b2b_test_run import ClickHouseB2BTestRun
from sandbox.projects.metrika.admins.clickhouse.clickhouse_b2b_test_stand_create import ClickHouseB2BTestStandCreate
from sandbox.projects.metrika.admins.clickhouse.clickhouse_b2b_test_stand_remove import ClickHouseB2BTestStandRemove
from sandbox.projects.metrika.admins.clickhouse.utils import build_clickhouse_docker_images
from sandbox.projects.metrika.admins.cosmos import utils as cosmos_utils
from sandbox.projects.metrika.utils import CommonParameters, settings
from sandbox.projects.metrika.utils.base_metrika_task import with_parents
from sandbox.projects.metrika.utils.maas import MaasProvider
from sandbox.projects.metrika.utils.mixins.console import BaseConsoleMixin
from sandbox.projects.metrika.utils.parameters import LastPeasantContainerResource, ArcadiaURL, DataCenterParameters
from sandbox.projects.metrika.utils.parameters import PackageVersion
from sandbox.projects.metrika.utils.pipeline.pipeline import PipelineBaseTask


@with_parents
class ClickHouseB2bApiTestsPipeline(PipelineBaseTask, BaseConsoleMixin):
    """
    Конвейер тестирования ClickHouse на запросах API-демонов
    """
    name = "CLICKHOUSE_B2B_TESTS_PIPELINE"

    @property
    def pipeline_state(self):
        return State(self.Context.pipeline_state)

    class Context(PipelineBaseTask.Context):
        pipeline_state = State().state

    class Parameters(CommonParameters):
        description = "B2B тесты ClickHouse на запросах API-демонов"

        container = LastPeasantContainerResource("Environment container resource", required=True)

        arcadia_url = ArcadiaURL('URL Аркадии', required=True, default='arcadia-arc:/#trunk')

        reporting = cosmos_utils.ReportStartrekParameters()

        with sdk2.parameters.Group("Тестовый стенд") as test_stand_group:
            data_center_params = DataCenterParameters()
            caas_parent = sdk2.parameters.String('CaaS parent name', required=True, default='days-32_sample-4',
                                                 description="Имя родительского инстанса, который содержит срез тестовых данных")
            maas_parent = sdk2.parameters.String("MaaS parent", required=True, default="vanilla-80",
                                                 description="Имя родительского инстанса")

        with sdk2.parameters.Group("Объект тестирования") as sut_group:
            clickhouse_version_ref = PackageVersion("ClickHouse стабильная версия", required=True, package="clickhouse-client", host_group="mtgiga",
                                                    description="Референсная версия ClickHouse, по умолчанию берётся с mtgiga")
            clickhouse_version_test = sdk2.parameters.String("ClickHouse тестируемая версия", required=True,
                                                             description="Тестируемая версия ClickHouse")

            config_version_ref = PackageVersion("clickhouse-server-metrika стабильная версия", required=True, package="clickhouse-server-metrika", host_group="mtgiga",
                                                description="Референсная версия clickhouse-server-metrika, по умолчанию берётся с mtgiga")
            config_version_test = sdk2.parameters.String("clickhouse-server-metrika тестируемая версия", required=True,
                                                         description="Тестируемая версия clickhouse-server-metrika")

            yt_dictionaries_ref = PackageVersion("Словари YT стабильная версия", required=True, package="yandex-clickhouse-dictionary-yt", host_group="mtgiga",
                                                 description="Референсная версия yt-словарей, по умолчанию берётся версия пакета yandex-clickhouse-dictionary-yt с mtgiga")
            yt_dictionaries_test = PackageVersion("Словари YT тестируемая версия", required=True, package="yandex-clickhouse-dictionary-yt", host_group="mtgiga",
                                                  description="Тестируемая версия yt-словарей, по умолчанию берётся версия пакета yandex-clickhouse-dictionary-yt с mtgiga")

            faced_version = PackageVersion("Версия faced", required=True, package="faced", env="production",
                                           description="Версия faced, по умолчанию берётся версия образа faced из стейджа production")
            mobmetd_version = PackageVersion("Версия mobmetd", required=True, package="mobmetd", env="production",
                                             description="Версия mobmetd, по умолчанию берётся версия образа mobmetd из стейджа production")

        with sdk2.parameters.Group("Параметры теста") as test_parameters_group:
            requests_resource = ClickHouseB2BTestRequestsResource("Тестовые запросы", required=True,
                                                                  description="Ресурс с тестовыми запросами")
            faced_handles_include = sdk2.parameters.String("Ручки faced (include)", default="",
                                                           description="Регулярное выражение под которое должны попадать ручки для faced.")
            faced_handles_exclude = sdk2.parameters.String("Ручки faced (exclude)", default="",
                                                           description="Регулярное выражение под которое должны не попадать ручки для faced.")
            mobmetd_handles_include = sdk2.parameters.String("Ручки mobmetd (include)", default="",
                                                             description="Регулярное выражение под которое должны попадать ручки для mobmetd.")
            mobmetd_handles_exclude = sdk2.parameters.String("Ручки mobmetd (exclude)", default="",
                                                             description="Регулярное выражение под которое должны не попадать ручки для mobmetd.")
            portion = sdk2.parameters.Float("Доля запросов", required=True, default=0.9,
                                            description="Для каждого вида запросов какова должна быть их удельная доля среди всех запросов данного вида за период.")
            limit = sdk2.parameters.Integer("Максимальное количество запросов каждого вида", required=True, default=1000,
                                            description="Ограничение сверху для каждого вида запросов.")

            threads = sdk2.parameters.Integer("Количество потоков", default=16,
                                              description="Количество потоков выполнения запросов. "
                                                          "Каждый поток последовательно выполняет два запроса - по одному на каждый полустенд, проводит анализ и записывает файл детального отчёта.")

        with sdk2.parameters.Group(label="Секреты") as secrets_group:
            ch_user = sdk2.parameters.String('ClickHouse user', required=True, default='robot-metrika-ch-test')
            ch_password = sdk2.parameters.Vault('ClickHouse password', required=True, default='METRIKA:robot-metrika-ch-test')
            bishop_token = sdk2.parameters.YavSecretWithKey('Bishop token', required=True, default=settings.rmt_bishop_yav,
                                                            description="Секрет с токеном для доступа к bishop")

        _binary = binary_task.binary_release_parameters_list(stable=True)

    @memoized_property
    def maas_provider(self):
        return MaasProvider(self.Parameters.bishop_token.value(), self.Parameters.data_center)

    def create_stages(self):
        return [
            (self.prepare_docker_images, "Docker-образы ClickHouse"),
            (self.create_daemons_stands, "Создание стендов"),
            (self.run_tests, "Прогон тестов"),
            (self.delete_daemon_stands, "Удаление стендов")
        ]

    def prepare_docker_images(self):
        build_clickhouse_docker_images(
            self,
            [
                (self.Parameters.clickhouse_version_ref, self.Parameters.config_version_ref, self.Parameters.yt_dictionaries_ref),
                (self.Parameters.clickhouse_version_test, self.Parameters.config_version_test, self.Parameters.yt_dictionaries_test)
            ],
            without_merges=True
        )

    def create_daemons_stands(self):
        subtasks = self.run_subtasks([
            (
                ClickHouseB2BTestStandCreate,
                {
                    ClickHouseB2BTestStandCreate.Parameters.description: 'Тесты API {} {} релиза ClickHouse {}'.format(daemon, version, self.Parameters.clickhouse_version_test),
                    ClickHouseB2BTestStandCreate.Parameters.name: 'ch-b2b-{}'.format(name),
                    ClickHouseB2BTestStandCreate.Parameters.daemon_name: daemon,
                    ClickHouseB2BTestStandCreate.Parameters.version: version,
                    ClickHouseB2BTestStandCreate.Parameters.data_center: self.Parameters.data_center,

                    ClickHouseB2BTestStandCreate.Parameters.caas_parent: self.Parameters.caas_parent,
                    ClickHouseB2BTestStandCreate.Parameters.clickhouse_version: clickhouse_version,

                    ClickHouseB2BTestStandCreate.Parameters.power: 2,
                    ClickHouseB2BTestStandCreate.Parameters.maas_parent: "vanilla-80",
                }
            )
            for daemon, version in [
                ('mobmetd', self.Parameters.mobmetd_version),
                ('faced', self.Parameters.faced_version)
            ]
            for name, clickhouse_version in zip(
                ['ref', 'test'],
                self.Context.caas_yt_no_merges_versions
            )
        ])
        self.Context.stages = [sdk2.Task[subtask].Parameters.stage_name for subtask in subtasks]
        self.pipeline_state.mobmetd_hostname_ref = sdk2.Task[subtasks[0]].Parameters.fqdn
        self.pipeline_state.mobmetd_hostname_test = sdk2.Task[subtasks[1]].Parameters.fqdn
        self.pipeline_state.faced_hostname_ref = sdk2.Task[subtasks[2]].Parameters.fqdn
        self.pipeline_state.faced_hostname_test = sdk2.Task[subtasks[3]].Parameters.fqdn

        resp = requests.post('http://{}:{}/?query={}'.format(
            self.maas_provider.caas_host,
            sdk2.Task[subtasks[0]].Context.caas_clickhouse_port,
            quote_plus('SELECT * FROM caas.metadata LIMIT 1 FORMAT JSON')
        ))
        resp.raise_for_status()
        data = resp.json().get("data")
        if data:
            self.pipeline_state.start_date = data[0]['StartDate']
            self.pipeline_state.finish_date = data[0]['FinishDate']
        else:
            raise Exception('Родительский инстанс CaaS не содержит метаданных')

    def run_tests(self):
        common_params = {
            ClickHouseB2BTestRun.Parameters.vcs.name: "arcadia",
            ClickHouseB2BTestRun.Parameters.arcadia_url.name: self.Parameters.arcadia_url,
            ClickHouseB2BTestRun.Parameters.arcadia_path.name: "metrika/qa/clickhouse-b2b-tests",

            ClickHouseB2BTestRun.Parameters.requests_resource.name: self.Parameters.requests_resource.id,
            ClickHouseB2BTestRun.Parameters.portion.name: self.Parameters.portion,
            ClickHouseB2BTestRun.Parameters.limit.name: self.Parameters.limit,

            ClickHouseB2BTestRun.Parameters.start_date.name: self.pipeline_state.start_date,
            ClickHouseB2BTestRun.Parameters.finish_date.name: self.pipeline_state.finish_date,

            ClickHouseB2BTestRun.Parameters.threads.name: self.Parameters.threads,

            ClickHouseB2BTestRun.Parameters.report_startrek.name: self.Parameters.report_startrek,
            ClickHouseB2BTestRun.Parameters.issue_key.name: self.Parameters.issue_key,

            ClickHouseB2BTestRun.Parameters.fail_task_on_test_failure.name: True,
        }

        daemon_params = {
            "faced": {
                ClickHouseB2BTestRun.Parameters.faced_api_test.name: "http://{host}:8080".format(host=self.pipeline_state.faced_hostname_test),
                ClickHouseB2BTestRun.Parameters.faced_api_ref.name: "http://{host}:8080".format(host=self.pipeline_state.faced_hostname_ref),
                ClickHouseB2BTestRun.Parameters.properties.name: {
                    "faced.handles.include": self.Parameters.faced_handles_include,
                    "faced.handles.exclude": self.Parameters.faced_handles_exclude,
                },
            },
            "mobmetd": {
                ClickHouseB2BTestRun.Parameters.mobmetd_api_test.name: "http://{host}:8080".format(host=self.pipeline_state.mobmetd_hostname_test),
                ClickHouseB2BTestRun.Parameters.mobmetd_api_ref.name: "http://{host}:8080".format(host=self.pipeline_state.mobmetd_hostname_ref),
                ClickHouseB2BTestRun.Parameters.properties.name: {
                    "mobmetd.handles.include": self.Parameters.mobmetd_handles_include,
                    "mobmetd.handles.exclude": self.Parameters.mobmetd_handles_exclude
                },
            }
        }

        self.pipeline_state.b2b_tests_tasks = self.run_subtasks([
            (
                ClickHouseB2BTestRun,
                dict(
                    common_params,
                    description="B2B тесты API {} релиза ClickHouse {}".format(daemon, self.Parameters.clickhouse_version_test),
                    **params
                )
            )
            for daemon, params in sorted(daemon_params.items())
        ])
        for test_id, daemon in zip(self.pipeline_state.b2b_tests_tasks, sorted(daemon_params)):
            res = sdk2.Task[test_id].Parameters.report_resource
            if res:
                self.comment('<a href="{}/site/response-report/index.html">Протоколы тестов {}</a>'.format(res.http_proxy, daemon))

    def delete_daemon_stands(self):
        self.run_subtasks([
            (ClickHouseB2BTestStandRemove, dict(stage_name=stage))
            for stage in self.Context.stages
        ])
