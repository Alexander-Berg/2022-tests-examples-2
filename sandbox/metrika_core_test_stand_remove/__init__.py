# coding=utf-8

from sandbox.projects.common import binary_task
from sandbox.projects.metrika import utils
from sandbox.projects.metrika.utils import base_metrika_task, bishop, settings
from sandbox.sdk2 import parameters


@base_metrika_task.with_parents
class MetrikaCoreTestStandRemove(base_metrika_task.BaseMetrikaTask):
    """
    Удаление тестового стенда Движка Метрики
    """

    class Parameters(utils.CommonParameters):
        description = "Удаление тестового стенда Движка Метрики"

        stage_name = parameters.String("Имя стейджа", required=True, default="", description="Имя стейджа в Деплое, который будет удален. Удалять можно только тестовые стенды")

        with parameters.Group("Секреты") as secrets_group:
            tokens_secret = parameters.YavSecret("Секрет с токенами", required=True, default=settings.yav_uuid)

            deploy_token_key = parameters.String("Ключ токена Деплоя в секрете", required=True, default="deploy-token")

        _binary = binary_task.binary_release_parameters_list(stable=True)

    def on_execute(self):
        self.remove_bishop_environment()
        self.remove_stage()

    @property
    def deploy_client(self):
        import metrika.pylib.deploy.client as deploy
        return deploy.DeployAPI(token=self.Parameters.tokens_secret.data().get(self.Parameters.deploy_token_key))

    def remove_bishop_environment(self):
        environment = "metrika.deploy.core.testing.autobetas"

        names = self.Parameters.stage_name.split("-autobeta-")
        daemon_name = names[0]
        stand_name = names[1]

        environment = "{}.{}.{}".format(environment, daemon_name, stand_name)

        bishop.delete_bishop_environment(bishop.get_bishop_client(), environment)

    def remove_stage(self):
        from yp import common
        try:
            self.deploy_client.stage.remove_stage(self.Parameters.stage_name)
        except common.YpNoSuchObjectError:
            pass
