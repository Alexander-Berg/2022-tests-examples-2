# coding=utf-8
import yaml

from sandbox.projects.common import binary_task
from sandbox.projects.metrika import utils
from sandbox.projects.metrika.utils import base_metrika_task, bishop
from sandbox.projects.metrika.utils import settings
from sandbox.projects.metrika.utils.base_metrika_task import BaseMetrikaTask
from sandbox.projects.metrika.utils.parameters import DataCenterParameters
from sandbox.sdk2 import parameters

SERVICES = [
    "metrika-frontend",
    "radar-frontend",
    "audience-frontend",
    "appmetrica-frontend",
    "mediametrika-frontend"
]
CROWD_SERVICES = [
    "metrika-assessor-frontend"
]
DEPLOY_UNIT_NAME = "frontend"
AWACS_NAMESPACE_ID = "frontend-autobetas"
AWACS_CROWDTEST_NAMESPACE_ID = "crowdtest.metrika.yandex.ru"

SERVICES_BISHOP = {
    "metrika-frontend": [
        "metrika-bem", "metrika-bem-frontend"
    ],
    "appmetrica-frontend": [
        "appmetrica-bem", "appmetrica-bem-frontend"
    ],
}


@base_metrika_task.with_parents
class MetrikaFrontendTestStandCreate(BaseMetrikaTask):
    """
    Создание тестового стенда фронтенда Метрики
    """

    class Parameters(utils.CommonParameters):
        description = "Создание тестового стенда фронтенда Метрики"

        service = parameters.String("Сервис", required=True, default=SERVICES[0], choices=[(item, item) for item in SERVICES + CROWD_SERVICES], description="Сервис, для которого создается стенд")

        name = parameters.String("Имя стенда", required=True, default="", description="Имя тестового стенда из которого будет формироваться имя стейджа в Деплое")

        images = parameters.Dict("Настройки образов", required=True, default={}, description="Названия и версии образов, которые подставляются в конфиг стейджа в Деплое")

        deploy_description = parameters.String("Описание ревизии в тестовом стенде", default="")

        with service.value["metrika-frontend"]:
            metrika_custom_api = parameters.Bool("Переопределить адрес апи метрики", default=False)
            with metrika_custom_api.value[True]:
                faced_url = parameters.String("Faced (var faced_serverUrl)")
                webvisor_url = parameters.String("Webvisor (var webvisor_serverUrl)")

        with service.value["appmetrica-frontend"]:
            appmetrica_custom_api = parameters.Bool("Переопределить адрес апи аппметрики", default=False)
            with appmetrica_custom_api.value[True]:
                mobmetd_url = parameters.String("Mobmetd (var hosts_mobmetHostName)")

        data_center_params = DataCenterParameters()

        with parameters.Group("Секреты") as secrets_group:
            tokens_secret = parameters.YavSecret("Секрет с токенами", required=True, default=settings.yav_uuid)

            deploy_token_key = parameters.String("Ключ токена Деплоя в секрете", required=True, default="deploy-token")

        _binary = binary_task.binary_release_parameters_list(stable=True)

    def on_execute(self):
        if self.Parameters.service in SERVICES_BISHOP and (
            self.Parameters.metrika_custom_api and (self.Parameters.faced_url or self.Parameters.webvisor_url) or
            self.Parameters.appmetrica_custom_api and self.Parameters.webvisor_url
        ):
            self.create_bishop_environment()
        self.create_stage()
        self.create_backend()
        if self.Parameters.service in CROWD_SERVICES:
            self.create_crowd_domain()
        self.create_upstream()
        self.comment("<a href=\"https://{}\">Интерфейс</a>".format(self.Context.url))

    @property
    def deploy_client(self):
        import metrika.pylib.deploy.client as deploy
        return deploy.DeployAPI(token=self.Parameters.tokens_secret.data().get(self.Parameters.deploy_token_key))

    @property
    def awacs_client(self):
        from metrika.pylib import awacs
        return awacs.AwacsAPI(self.Parameters.tokens_secret.data().get(self.Parameters.deploy_token_key))

    def create_stage(self):
        stage_specification = yaml.safe_load(utils.read_sources_file("resources/{}.yaml".format(self.Parameters.service)))
        stage_specification["meta"]["id"] = self.get_stage_name()
        stage_specification["spec"]["revision_info"]["description"] = self.Parameters.deploy_description

        deploy_unit_specification = stage_specification["spec"]["deploy_units"][DEPLOY_UNIT_NAME]
        for image in deploy_unit_specification["images_for_boxes"].values():
            if image["name"] in self.Parameters.images:
                image["tag"] = self.Parameters.images[image["name"]]

        replica_set = deploy_unit_specification["replica_set"]
        replica_set["per_cluster_settings"] = {self.Parameters.data_center: {"deployment_strategy": {"max_unavailable": 1}, "pod_count": 1}}

        pod_specification = replica_set["replica_set_template"]["pod_template_spec"]["spec"]

        workloads = pod_specification["pod_agent_payload"]["spec"]["workloads"]
        hermione_host = "{}.dev.{}.yandex.ru".format(self.get_stand_name(), self.Parameters.service.replace("-frontend", ""))
        for workload in workloads:
            if self.Context.bishop_environment and workload["id"] == "BEM-workload":
                for var in workload["env"]:
                    if var["name"] == "BISHOP_ENVIRONMENT_NAME":
                        var["value"]["literal_env"]["value"] = self.Context.bishop_environment
            workload["env"].append({"name": "HERMIONE_HOST", "value": {"literal_env": {"value": hermione_host}}})
        self.Context.url = hermione_host
        self.comment('<a href="https://deploy.yandex-team.ru/stages/{}">Deploy Stage</a>'.format(self.get_stage_name()))
        self.deploy_client.stage.deploy_stage(stage_specification, wait=True, wait_kwargs={'timeout': 1800})

    def create_bishop_environment(self):
        env, prog = SERVICES_BISHOP[self.Parameters.service]
        parent = "metrika.deploy.frontend.{}.testing.development".format(env)
        environmet_variables = {}
        if self.Parameters.service == "metrika-frontend":
            if self.Parameters.faced_url:
                environmet_variables["faced_serverUrl"] = self.Parameters.faced_url
            if self.Parameters.webvisor_url:
                environmet_variables["webvisor_serverUrl"] = self.Parameters.webvisor_url
        elif self.Parameters.service == "appmetrica-frontend":
            if self.Parameters.mobmetd_url:
                environmet_variables["hosts_mobmetHostName"] = self.Parameters.mobmetd_url

        self.Context.bishop_environment = bishop.create_bishop_environment(
            bishop.get_bishop_client(), parent, self.get_stand_name(), environmet_variables, prog
        )
        self.comment("<a href=\"https://bishop.mtrs.yandex-team.ru/environment/{}\">Bishop Env</a>".format(self.Context.bishop_environment))

    def create_backend(self):
        yp_endpoint_sets_config = [{"cluster": self.Parameters.data_center, "endpoint_set_id": self.get_endpoint_set_id()}]
        awacs_namespace_id = self.get_namespace_id(self.Parameters.service)
        self.awacs_client.update_backend_yp_endpoint_sets(awacs_namespace_id, self.get_stage_name(), yp_endpoint_sets_config)
        self.comment("<a href=\"https://nanny.yandex-team.ru/ui/#/awacs/namespaces/list/{}/backends/list/{}/show/\">Awacs Backend</a>".format(
            awacs_namespace_id, self.get_stage_name()
        ))

    def create_crowd_domain(self):
        awacs_namespace_id = self.get_namespace_id(self.Parameters.service)
        fqdns = [template.format(self.get_stand_name()) for template in ["{}.crowdtest.metrika.yandex.ru", "{}.crowdtest.metrika.yandex.com"]]
        self.awacs_client.update_domain(awacs_namespace_id, self.get_stage_name(), fqdns, self.get_stage_name(), "crowdtest.metrika.yandex.ru")

    def create_upstream(self):
        yandex_balancer = yaml.safe_load(utils.read_sources_file("resources/yandex-balancer-template.yaml"))
        yandex_balancer["regexp_section"]["matcher"] = yaml.safe_load(
            utils.read_sources_file("resources/{}-matcher-template.yaml".format(self.Parameters.service)).format(self.get_stand_name())
        )
        for module in yandex_balancer["regexp_section"]["modules"]:
            module["balancer2"]["generated_proxy_backends"]["include_backends"]["ids"] = [self.get_stage_name()]
        labels = {"order": "00000010"}
        awacs_namespace_id = self.get_namespace_id(self.Parameters.service)
        self.awacs_client.update_upstream(awacs_namespace_id, self.get_stage_name(), yaml.safe_dump(yandex_balancer), labels, wait_seconds=1200)
        self.comment("<a href=\"https://nanny.yandex-team.ru/ui/#/awacs/namespaces/list/{}/upstreams/list/{}/show/\">Awacs Upstream</a>".format(
            awacs_namespace_id, self.get_stage_name()
        ))

    def get_namespace_id(self, service):
        return AWACS_CROWDTEST_NAMESPACE_ID if service in CROWD_SERVICES else AWACS_NAMESPACE_ID

    def get_stage_name(self):
        return "{}-autobeta-{}".format(self.Parameters.service, self.get_stand_name())

    def get_stand_name(self):
        return self.Parameters.name.replace(".", "-")

    def get_endpoint_set_id(self):
        return "{}.{}".format(self.get_stage_name(), DEPLOY_UNIT_NAME)
