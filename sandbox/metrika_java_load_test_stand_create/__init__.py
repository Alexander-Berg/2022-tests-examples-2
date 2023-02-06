# coding=utf-8

import yaml

from sandbox import sdk2
from sandbox.sdk2 import parameters
from sandbox.projects.common import binary_task
from sandbox.projects.common.decorators import memoized_property
from sandbox.projects.metrika import utils
from sandbox.projects.metrika.utils import base_metrika_task, settings
from sandbox.projects.metrika.utils.parameters import DataCenterParameters


@base_metrika_task.with_parents
class MetrikaJavaLoadTestStandCreate(base_metrika_task.BaseMetrikaTask):
    """
    Создание нагрузочного стенда для java демонов Метрики
    """

    class Parameters(utils.CommonParameters):
        description = "Создание нагрузочного стенда для java демонов Метрики"

        name = parameters.String(
            "Имя стенда", required=True, default="", description="Имя нагрузочного стенда из которого будет формироваться имя стейджа в Деплое"
        )

        daemon_name = parameters.String(
            "Имя демона", required=True, default="", description="Имя демона, для которого создается нагрузочный стенд в Деплое"
        )

        data_center_params = DataCenterParameters()

        with parameters.Group("Секреты") as secrets_group:
            tokens_secret = parameters.YavSecret("Секрет с токенами", required=True, default=settings.yav_uuid)
            deploy_token_key = parameters.String("Ключ токена Деплоя в секрете", required=True, default="deploy-token")

        with sdk2.parameters.Output:
            fqdn = parameters.String("FQDN стенда", required=True, description="Адрес нагрузочного стенда в Деплое")
            stage_name = parameters.String("Имя стейджа", required=True)

        _binary = binary_task.binary_release_parameters_list(stable=True)

    def on_execute(self):
        self.create_stage()

    @property
    def deploy_client(self):
        import metrika.pylib.deploy.client as deploy
        return deploy.DeployAPI(token=self.Parameters.tokens_secret.data().get(self.Parameters.deploy_token_key))

    def create_stage(self):
        stage_specification = yaml.safe_load(utils.read_sources_file("resources/config.yaml"))
        stage_specification["meta"]["id"] = self.stage_name

        deploy_unit_specification = stage_specification["spec"]["deploy_units"]["DeployUnit"]

        replica_set = deploy_unit_specification["replica_set"]
        replica_set["per_cluster_settings"] = {self.Parameters.data_center: {"deployment_strategy": {"max_unavailable": 1}, "pod_count": 1}}

        self.comment("<a href=\"https://deploy.yandex-team.ru/stages/{}\">Deploy Stage</a>".format(self.stage_name))
        self.deploy_client.stage.deploy_stage(stage_specification, wait=True, wait_kwargs={"timeout": 1800})

        self.fill_fqdn()
        self.Parameters.stage_name = self.stage_name

    def fill_fqdn(self):
        self.Parameters.fqdn = MetrikaJavaLoadTestStandCreate.get_fqdn(self.Parameters.name, self.Parameters.daemon_name, self.Parameters.data_center)

    @memoized_property
    def stage_name(self):
        return MetrikaJavaLoadTestStandCreate.get_stage_name(self.Parameters.daemon_name, self.stand_name)

    @memoized_property
    def stand_name(self):
        return MetrikaJavaLoadTestStandCreate.get_stand_name(self.Parameters.name)

    @memoized_property
    def endpoint_set_id(self):
        return MetrikaJavaLoadTestStandCreate.get_endpoint_set_id(self.stage_name)

    @staticmethod
    def get_resolver():
        import metrika.pylib.deploy.resolver as resolver
        return resolver.Resolver()

    @staticmethod
    def get_stand_name(name):
        return name.replace(".", "-")

    @staticmethod
    def get_stage_name(daemon_name, stand_name):
        return "{}-tank-{}".format(daemon_name, stand_name)

    @staticmethod
    def get_endpoint_set_id(stage_name):
        return "{}.{}".format(stage_name, "DeployUnit")

    @staticmethod
    def get_fqdn(name, daemon_name, data_center="vla"):
        resolver = MetrikaJavaLoadTestStandCreate.get_resolver()
        stand_name = MetrikaJavaLoadTestStandCreate.get_stand_name(name)
        stage_name = MetrikaJavaLoadTestStandCreate.get_stage_name(daemon_name, stand_name)
        endpoint_set_id = MetrikaJavaLoadTestStandCreate.get_endpoint_set_id(stage_name)
        return resolver.resolve_endpoints(endpoint_set_id, data_center)[0].fqdn
