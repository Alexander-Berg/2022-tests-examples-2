# coding=utf-8
import yaml

from sandbox.projects.common import binary_task
from sandbox.projects.metrika import utils
from sandbox.projects.metrika.utils import base_metrika_task, bishop, settings
from sandbox.projects.metrika.utils.parameters import DataCenterParameters
from sandbox.sdk2 import parameters


@base_metrika_task.with_parents
class MetrikaCoreTestStandCreate(base_metrika_task.BaseMetrikaTask):
    """
    Создание тестового стенда Движка Метрики
    """

    class Parameters(utils.CommonParameters):
        description = "Создание тестового стенда Движка Метрики"

        name = parameters.String("Имя стенда", required=True, default="", description="Имя тестового стенда из которого будет формироваться имя стейджа в Деплое")

        daemon_name = parameters.String("Имя демона", required=True, default="", description="Имя демона, для которого создается тестовый стенд в Деплое")

        version = parameters.String("Версия", required=True, default="", description="Версия демона, которая подставляются в конфиг стейджа в Деплое")

        data_center_params = DataCenterParameters()

        with parameters.Group("Секреты") as secrets_group:
            tokens_secret = parameters.YavSecret("Секрет с токенами", required=True, default=settings.yav_uuid)

            deploy_token_key = parameters.String("Ключ токена Деплоя в секрете", required=True, default="deploy-token")

        _binary = binary_task.binary_release_parameters_list(stable=True)

    def on_execute(self):
        self.create_bishop_environment()
        self.create_stage()

    @property
    def deploy_client(self):
        import metrika.pylib.deploy.client as deploy
        return deploy.DeployAPI(token=self.Parameters.tokens_secret.data().get(self.Parameters.deploy_token_key))

    def create_bishop_environment(self):
        parent = "metrika.deploy.core.testing.autobetas.{}".format(self.Parameters.daemon_name)

        self.Context.bishop_environment = bishop.create_bishop_environment(
            bishop.get_bishop_client(), parent, self.get_stand_name(), {}, self.Parameters.daemon_name
        )
        self.comment("<a href=\"https://bishop.mtrs.yandex-team.ru/environment/{}\">Bishop Env</a>".format(self.Context.bishop_environment))

    def create_stage(self):
        stage_specification = yaml.safe_load(utils.read_sources_file("resources/stand.yaml"))
        stage_specification["meta"]["id"] = self.get_stage_name()

        self.comment("<a href=\"https://deploy.yandex-team.ru/stages/{}\">Deploy Stage</a>".format(self.get_stage_name()))
        self.deploy_client.stage.deploy_stage(stage_specification, wait=True, wait_kwargs={"timeout": 1800})

    def get_stage_name(self):
        return "{}-autobeta-{}".format(self.Parameters.daemon_name, self.get_stand_name())

    def get_stand_name(self):
        return self.Parameters.name.replace(".", "-")
