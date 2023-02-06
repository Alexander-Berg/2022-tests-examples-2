# -*- coding: utf-8 -*-

import os

import sandbox.common.types.client as ctc
import sandbox.sandboxsdk.environments as environments
import sandbox.projects.common.build.parameters as build_params

from sandbox.projects.common.build.YaMake import YaMakeTask
from sandbox.projects.common import constants


class MyTestFilters(build_params.TestFilters):
    description = 'Test filter (e.g. ru.yandex.tycoon.api.rest.resource.company.CompaniesResourceTest::testCompanyGet)'


class MyTestLogLevel(build_params.TestLogLevel):
    default_value = constants.INFO_TEST_LOG_LEVEL


class TycoonTest(YaMakeTask):
    """
        Запуск интеграционных тестов Тайкуна
    """

    type = "TYCOON_TEST"

    environment = [environments.SvnEnvironment()]
    client_tags = ctc.Tag.GENERIC
    cores = 24

    input_parameters = [
        build_params.ArcadiaUrl,
        MyTestFilters,
        MyTestLogLevel,
        build_params.JvmArgs
    ]

    def pre_build(self, source_dir):
        self.ctx[constants.TESTS_REQUESTED] = True
        self.ctx[constants.REPORT_TESTS_ONLY] = True
        self.ctx[constants.TEST_THREADS] = 1

        os.environ["ENVIRONMENT_TYPE"] = "sandbox"
        os.environ["YT_TOKEN"] = self.get_vault_data("TYCOON", "tycoon_yt_token")
        os.environ["YQL_TOKEN"] = self.get_vault_data("TYCOON", "YQL_TOKEN")

    def get_targets(self):
        return ["sprav/tycoon"]


__Task__ = TycoonTest
