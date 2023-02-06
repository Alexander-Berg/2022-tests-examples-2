# coding=utf-8
import datetime
import logging

import yaml

from sandbox import sdk2
from sandbox.projects.common import binary_task
from sandbox.projects.common.decorators import memoized_property
from sandbox.projects.metrika import utils
from sandbox.projects.metrika.frontend import metrika_frontend_development
from sandbox.projects.metrika.utils import base_metrika_task, bishop, maas, settings
from sandbox.projects.metrika.utils.maas import MaasProvider
from sandbox.projects.metrika.utils.parameters import DataCenterParameters
from sandbox.projects.metrika.utils.pipeline import pipeline
from sandbox.sdk2 import parameters

DAEMON_SERVICES = {
    "faced": "metrika-frontend",
    "webvisor-api": "metrika-frontend",
    "mobmetd": "appmetrica-frontend",
}


@base_metrika_task.with_parents
class MetrikaJavaTestStandCreate(pipeline.PipelineBaseTask):
    """
    Создание тестового стенда java демонов Метрики
    """

    class Parameters(utils.CommonParameters):
        description = "Создание тестового стенда java демонов Метрики"

        name = parameters.String("Имя стенда", required=True, default="", description="Имя тестового стенда из которого будет формироваться имя стейджа в Деплое")

        daemon_name = parameters.String("Имя демона", required=True, default="", description="Имя демона, для которого создается тестовый стенд в Деплое")

        version = parameters.String("Версия", required=True, default="", description="Версия образа, которая подставляются в конфиг стейджа в Деплое")

        create_frontend_stand = parameters.Bool("Создать стенд фронтенда", default=False)

        with create_frontend_stand.value[True]:
            frontend_arcadia_url = parameters.ArcadiaUrl("URL Аркадии фронтенда", required=True, default="arcadia-arc:/#trunk",
                                                         description="Ветка или коммит, из которой будет собран фронтенд")

        bishop_environment_prefix = parameters.String("Префикс окружения в Бишоп", required=False, default="", description="Опциональный префикс окружения в Бишоп")

        power = parameters.Integer("X", default=1, required=True, description="Увеличить CPU и RAM в X раз", ui=None)

        with parameters.RadioGroup("Родительский инстанс") as maas_parent:
            maas_parent.values["Parent-80"] = None
            maas_parent.values["vanilla-80"] = None
            maas_parent.values["distilled-80"] = maas_parent.Value(default=True)

        sql_script = parameters.String("SQL скрипт", required=False, default="", multiline=True, description="Скрипт для применения к mysql базе.")

        data_center_params = DataCenterParameters()

        with parameters.Group("Секреты") as secrets_group:
            tokens_secret = parameters.YavSecret("Секрет с токенами", required=True, default=settings.yav_uuid)

            deploy_token_key = parameters.String("Ключ токена Деплоя в секрете", required=True, default="deploy-token")

            bishop_token = sdk2.parameters.YavSecretWithKey('Bishop token', required=True, default=settings.rmt_bishop_yav,
                                                            description="Секрет с токеном для доступа к bishop")

        with sdk2.parameters.Output:
            fqdn = parameters.String("FQDN стенда", required=True, description="Адрес тестового стенда в Деплое")
            stage_name = parameters.String("Имя стейджа", required=True)

        _binary = binary_task.binary_release_parameters_list(stable=True)

    @memoized_property
    def maas_provider(self):
        return MaasProvider(self.Parameters.bishop_token.value(), self.Parameters.data_center)

    def create_stages(self):
        stages = [
            (self.create_maas_instance, "MaaS"),
            (self.create_bishop_environment, "Bishop"),
            (self.create_stage, "Deploy"),
        ]
        if self.Parameters.create_frontend_stand:
            stages.append((self.create_frontend_stand, "Frontend"))
        return stages

    @property
    def deploy_client(self):
        import metrika.pylib.deploy.client as deploy
        return deploy.DeployAPI(token=self.Parameters.tokens_secret.data().get(self.Parameters.deploy_token_key))

    @property
    def vault_client(self):
        from library.python.vault_client import instances
        return instances.Production(authorization=self.Parameters.tokens_secret.data().get(self.Parameters.deploy_token_key))

    def create_frontend_stand(self):
        if self.Parameters.daemon_name not in DAEMON_SERVICES:
            self.comment("Для демона не указан сервис фронта (подходящие демона: {})".format(sorted(DAEMON_SERVICES)))
            return

        params = {
            metrika_frontend_development.MetrikaFrontendDevelopment.Parameters.service: DAEMON_SERVICES[self.Parameters.daemon_name],
            metrika_frontend_development.MetrikaFrontendDevelopment.Parameters.arcadia_url: self.Parameters.frontend_arcadia_url,
            metrika_frontend_development.MetrikaFrontendDevelopment.Parameters.data_center: self.Parameters.data_center,
            metrika_frontend_development.MetrikaFrontendDevelopment.Parameters.use_custom_name: True,
            metrika_frontend_development.MetrikaFrontendDevelopment.Parameters.custom_name: self.stand_name,
            metrika_frontend_development.MetrikaFrontendDevelopment.Parameters.run_tests: False,
        }
        url = "http://{}:8080".format(self.Parameters.fqdn)
        if self.Parameters.daemon_name == "faced":
            params[metrika_frontend_development.MetrikaFrontendDevelopment.Parameters.metrika_custom_api] = True
            params[metrika_frontend_development.MetrikaFrontendDevelopment.Parameters.faced_url] = url
        elif self.Parameters.daemon_name == "webvisor-api":
            params[metrika_frontend_development.MetrikaFrontendDevelopment.Parameters.metrika_custom_api] = True
            params[metrika_frontend_development.MetrikaFrontendDevelopment.Parameters.webvisor_url] = url
        elif self.Parameters.daemon_name == "mobmetd":
            params[metrika_frontend_development.MetrikaFrontendDevelopment.Parameters.appmetrica_custom_api] = True
            params[metrika_frontend_development.MetrikaFrontendDevelopment.Parameters.mobmetd_url] = url
        frontend_subtask_id = self.run_subtasks((metrika_frontend_development.MetrikaFrontendDevelopment, params))[0]
        self.comment("<a href=\"{}\">Интерфейс</a>".format(sdk2.Task[frontend_subtask_id].Context.url))

    def create_maas_instance(self):
        self.maas_provider.get_maas_client().delete_all_instances_by_name(self.stage_name)
        parent = self.maas_provider.get_maas_client().get_latest_instance_by_name(self.Parameters.maas_parent)

        instance = self.maas_provider.get_maas_client()
        instance.MAX_WAIT_TIME = 60 * 10
        instance.create(name=self.stage_name, parent_id=parent.id, version_tag=maas.VERSION_TAG, ttl=int(datetime.timedelta(weeks=2).total_seconds()))
        self.Context.maas_mysql_port = instance.ports["mysql"]

        if self.Parameters.sql_script:
            self.execute_alters()

    def execute_alters(self):
        import pymysql
        connection = pymysql.connect(
            host=self.maas_provider.maas_host, port=self.Context.maas_mysql_port,
            user="dba", password=self.vault_client.get_version("sec-01f2p6kyz96gzz6j8k0zjs9851")["value"]["dba"],
            use_unicode=True
        )
        with connection.cursor() as cursor:
            for line in self.Parameters.sql_script.split(";\n"):
                line = line.strip()
                if line:
                    logging.debug(line)
                    cursor.execute(line)
            connection.commit()

    def create_bishop_environment(self):
        parent = "metrika.deploy.java.testing.autobetas"
        if self.Parameters.bishop_environment_prefix:
            parent = "{}.{}".format(parent, self.Parameters.bishop_environment_prefix)
        parent = "{}.{}".format(parent, self.Parameters.daemon_name)
        environmet_variables = {
            "MYSQL_HOST": self.maas_provider.maas_host,
            "MYSQL_PORT": self.Context.maas_mysql_port,
            "is_autobeta_ng": "True"
        }

        self.Context.bishop_environment = bishop.create_bishop_environment(
            bishop.get_bishop_client(), parent, self.stand_name, environmet_variables, self.Parameters.daemon_name
        )
        self.comment("<a href=\"https://bishop.mtrs.yandex-team.ru/environment/{}\">Bishop Env</a>".format(self.Context.bishop_environment))

    def create_stage(self):
        stage_specification = yaml.safe_load(utils.read_sources_file("resources/stand.yaml"))
        stage_specification["meta"]["id"] = self.stage_name

        deploy_unit_specification = stage_specification["spec"]["deploy_units"]["DeployUnit1"]
        image = deploy_unit_specification["images_for_boxes"]["Box1"]
        image["name"] = self.image_name
        image["tag"] = self.Parameters.version

        replica_set = deploy_unit_specification["replica_set"]
        replica_set["per_cluster_settings"] = {self.Parameters.data_center: {"deployment_strategy": {"max_unavailable": 1}, "pod_count": 1}}

        pod_specification = replica_set["replica_set_template"]["pod_template_spec"]["spec"]

        resources = pod_specification["resource_requests"]
        for resource, value in resources.items():
            resources[resource] = value * self.Parameters.power

        workloads_specification = pod_specification["pod_agent_payload"]["spec"]
        for workload in workloads_specification["workloads"]:
            if "env" in workload:
                if self.Parameters.bishop_environment_prefix:
                    workload["env"].append({"name": "BISHOP_ENVIRONMENT_PART", "value": {"literal_env": {"value": self.Parameters.bishop_environment_prefix}}})
                workload["env"].append({"name": "BISHOP_ENVIRONMENT_SUFFIX", "value": {"literal_env": {"value": self.stand_name}}})
                workload["env"].append({"name": "RESTART", "value": {"literal_env": {"value": str(datetime.datetime.now())}}})

        self.comment("<a href=\"https://deploy.yandex-team.ru/stages/{}\">Deploy Stage</a>".format(self.stage_name))
        self.deploy_client.stage.deploy_stage(stage_specification, wait=True, wait_kwargs={"timeout": 1800})

        self.fill_fqdn()
        self.Parameters.stage_name = self.stage_name

    def fill_fqdn(self):
        self.Parameters.fqdn = MetrikaJavaTestStandCreate.get_fqdn(self.Parameters.name, self.Parameters.daemon_name, self.Parameters.data_center)

    @memoized_property
    def stage_name(self):
        return MetrikaJavaTestStandCreate.get_stage_name(self.Parameters.daemon_name, self.stand_name)

    @memoized_property
    def stand_name(self):
        return MetrikaJavaTestStandCreate.get_stand_name(self.Parameters.name)

    @memoized_property
    def image_name(self):
        return "metrika/java/{}".format(self.Parameters.daemon_name)

    @memoized_property
    def endpoint_set_id(self):
        return MetrikaJavaTestStandCreate.get_endpoint_set_id(self.stage_name)

    @staticmethod
    def get_resolver():
        import metrika.pylib.deploy.resolver as resolver
        return resolver.Resolver()

    @staticmethod
    def get_stand_name(name):
        return name.replace(".", "-")

    @staticmethod
    def get_stage_name(daemon_name, stand_name):
        return "{}-autobeta-{}".format(daemon_name, stand_name)

    @staticmethod
    def get_endpoint_set_id(stage_name):
        return "{}.{}".format(stage_name, "DeployUnit1")

    @staticmethod
    def get_fqdn(name, daemon_name, data_center="sas"):
        resolver = MetrikaJavaTestStandCreate.get_resolver()
        stand_name = MetrikaJavaTestStandCreate.get_stand_name(name)
        stage_name = MetrikaJavaTestStandCreate.get_stage_name(daemon_name, stand_name)
        endpoint_set_id = MetrikaJavaTestStandCreate.get_endpoint_set_id(stage_name)
        return resolver.resolve_endpoints(endpoint_set_id, data_center)[0].fqdn
