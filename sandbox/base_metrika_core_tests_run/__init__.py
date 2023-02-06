# coding=utf-8
import os

from sandbox.projects.metrika.utils import artifacts
from sandbox.projects import resource_types
from sandbox.projects.metrika.utils import settings
from sandbox.projects.metrika.admins import base_metrika_tests_run
from sandbox.sdk2 import yav, Path


class BaseMetrikaCoreTestsRun(base_metrika_tests_run.BaseMetrikaTestsRun):
    """
    Базовый класс запуска тестов демонов Движка Метрики
    """

    def project_name(self):
        raise NotImplementedError()

    def _target_dir_path(self, *path):
        return Path(self.wd(self.project_name(), "target", *path))

    def _target_dir(self, *path):
        return self._target_dir_path(*path).as_posix()

    def _custom_dir(self, *path):
        return self.path(*path).as_posix()

    def _package_to_build(self):
        return "ru.yandex.autotests.metrika.core:{}".format(self.project_name())

    def _build(self):
        self._execute_maven(["install", "--file", self._pom(),
                             "--projects", "{0}:metrika-core-bean-generators,{0}:metrika-core-beans,{0}:metrika-core-steps".format("ru.yandex.autotests.metrika.core")], cwd=self.wd())

    def get_environment(self):
        secret_id = settings.yav_uuid

        environment = os.environ.copy()

        environment["BISHOP_OAUTH_TOKEN"] = yav.Secret(secret_id).data()["bishop-token"]
        environment["CLICKHOUSE_PASSWORD"] = yav.Secret(secret_id).data()["clickhouse-password"]
        environment["METRIKA_VAULT_TOKEN"] = yav.Secret(secret_id).data()["yav-token"]

        return environment

    def _get_additional_directories(self):
        return {
            "/etc": ["clickhouse-server", "mysql", "zookeeper"],
            "/var/log": ["clickhouse-server", "mysql", "zookeeper"]
        }

    def _archive_additional_directories(self):
        for directory, arts in self._get_additional_directories().items():
            artifacts.archive_artifacts(self, directory, self._custom_dir(directory[1:]), resource_types.TASK_CUSTOM_LOGS, *arts, ttl=self.Parameters.report_ttl)
