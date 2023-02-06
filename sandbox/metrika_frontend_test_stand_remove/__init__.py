# coding=utf-8

from sandbox.projects.common import binary_task
from sandbox.projects.metrika import utils
from sandbox.projects.metrika.frontend import metrika_frontend_test_stand_create
from sandbox.projects.metrika.utils import base_metrika_task, settings, bishop
from sandbox.sdk2 import parameters


@base_metrika_task.with_parents
class MetrikaFrontendTestStandRemove(base_metrika_task.BaseMetrikaTask):
    """
    Удаление тестового стенда фронтенда Метрики
    """

    class Parameters(utils.CommonParameters):
        description = "Удаление тестового стенда фронтенда Метрики"

        stage_name = parameters.String("Имя стейджа", required=True, default="", description="Имя стейджа в Деплое, который будет удален. Удалять можно только автобеты")

        with parameters.Group("Секреты") as secrets_group:
            tokens_secret = parameters.YavSecret("Секрет с токенами", required=True, default=settings.yav_uuid)

            deploy_token_key = parameters.String("Ключ токена Деплоя в секрете", required=True, default="deploy-token")

            awacs_token_key = parameters.String("Ключ токена AWACS в секрете", required=True, default="awacs-token")

        _binary = binary_task.binary_release_parameters_list(stable=True)

    def on_execute(self):
        self.remove_crowdtest_domain(metrika_frontend_test_stand_create.AWACS_CROWDTEST_NAMESPACE_ID, self.Parameters.stage_name)
        for namespace in [metrika_frontend_test_stand_create.AWACS_NAMESPACE_ID, metrika_frontend_test_stand_create.AWACS_CROWDTEST_NAMESPACE_ID]:
            self.remove_upstream(namespace, self.Parameters.stage_name)
            self.remove_backend(namespace, self.Parameters.stage_name)
        self.remove_stage(self.Parameters.stage_name)
        self.remove_bishop_environment()

    @property
    def awacs_client(self):
        from metrika.pylib import awacs
        return awacs.AwacsAPI(self.Parameters.tokens_secret.data().get(self.Parameters.awacs_token_key))

    @property
    def deploy_client(self):
        import metrika.pylib.deploy.client as deploy
        return deploy.DeployAPI(token=self.Parameters.tokens_secret.data().get(self.Parameters.deploy_token_key))

    def remove_crowdtest_domain(self, namespace, id):
        from nanny_rpc_client import exceptions

        try:
            self.awacs_client.remove_domain(namespace, id)
        except exceptions.NotFoundError:
            pass

    def remove_upstream(self, namespace, id):
        from nanny_rpc_client import exceptions

        try:
            upstream = self.awacs_client.get_upstream(namespace, id)
        except exceptions.NotFoundError:
            pass
        else:
            self.awacs_client.client.remove_upstream(namespace, id, upstream.meta.version)

    def remove_backend(self, namespace, id):
        from nanny_rpc_client import exceptions

        try:
            backend = self.awacs_client.get_backend(namespace, id)
        except exceptions.NotFoundError:
            pass
        else:
            self.awacs_client.client.remove_backend(namespace, id, backend.meta.version)

    def remove_stage(self, id):
        from yp import common

        try:
            self.deploy_client.stage.remove_stage(id)
        except common.YpNoSuchObjectError:
            pass

    def remove_bishop_environment(self):
        service, stand_name = self.Parameters.stage_name.split('-autobeta-')
        base_env = metrika_frontend_test_stand_create.SERVICES_BISHOP[service][0]
        env = "metrika.deploy.frontend.{}.testing.development.{}".format(base_env, stand_name)
        bishop.delete_bishop_environment(bishop.get_bishop_client(), env)
