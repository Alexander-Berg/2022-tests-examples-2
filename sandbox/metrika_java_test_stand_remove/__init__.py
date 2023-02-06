# coding=utf-8
import logging
from sandbox.projects.common.decorators import memoized_property
from sandbox.projects.common import binary_task
from sandbox.projects.metrika import utils
from sandbox.projects.metrika.utils import base_metrika_task, bishop, settings
from sandbox.projects.metrika.utils.maas import MaasProvider
from sandbox.projects.metrika.utils.parameters import hide
from sandbox.sdk2 import parameters


@base_metrika_task.with_parents
class MetrikaJavaTestStandRemove(base_metrika_task.BaseMetrikaTask):
    """
    Удаление тестового стенда java демонов Метрики
    """

    class Parameters(utils.CommonParameters):
        description = "Удаление тестового стенда java демонов Метрики"

        stage_name = parameters.String("Имя стейджа", required=True, default="", description="Имя стейджа в Деплое, который будет удален. Удалять можно только тестовые стенды")

        with parameters.Group("Секреты") as secrets_group:
            tokens_secret = parameters.YavSecret("Секрет с токенами", required=True, default=settings.yav_uuid)

            deploy_token_key = parameters.String("Ключ токена Деплоя в секрете", required=True, default="deploy-token")

            bishop_token = parameters.YavSecretWithKey('Bishop token', required=True, default=settings.rmt_bishop_yav,
                                                       description="Секрет с токеном для доступа к bishop")

        _binary = hide(binary_task.binary_release_parameters_list(stable=True))

    def on_execute(self):
        self.remove_maas_instance()
        self.remove_bishop_environment()
        self.remove_stage()

    @property
    def deploy_client(self):
        import metrika.pylib.deploy.client as deploy
        return deploy.DeployAPI(token=self.Parameters.tokens_secret.data().get(self.Parameters.deploy_token_key))

    @memoized_property
    def maas_provider(self):
        return MaasProvider(self.Parameters.bishop_token.value())

    def remove_maas_instance(self):
        # тут нужно пройти по всем ДЦ и в каждом попробовать удалить
        for maas in self.maas_provider.get_maas_clients():
            try:
                maas.delete_all_instances_by_name(self.Parameters.stage_name)
            except:
                logging.exception("Ошибка при удалении инстанса в MaaS. Пропускаем.")

    def remove_bishop_environment(self):
        bishop_environment_prefix = None

        stage_specification = self.deploy_client.stage.get_stage_specification(self.Parameters.stage_name)
        replica_set = stage_specification["deploy_units"]["DeployUnit1"]["replica_set"]
        pod_specification = replica_set["replica_set_template"]["pod_template_spec"]["spec"]
        workloads_specification = pod_specification["pod_agent_payload"]["spec"]

        for workload in workloads_specification["workloads"]:
            if "env" in workload:
                for env in workload["env"]:
                    if env.get("name") == "BISHOP_ENVIRONMENT_PART":
                        bishop_environment_prefix = env.get("value").get("literal_env").get("value")

        environment = "metrika.deploy.java.testing.autobetas"
        if bishop_environment_prefix:
            environment += "." + bishop_environment_prefix

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
