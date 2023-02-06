# coding=utf-8

import os
import logging

from sandbox import sdk2
from sandbox.projects.common.arcadia import sdk
from sandbox.sdk2.helpers.process import subprocess
import sandbox.common.types.misc as ctm
import sandbox.common.types.client as ctc


class DcArtifactsData(sdk2.Resource):
    """ Artifacts directory """
    pack_tar = 1


class DcTests(sdk2.Task):
    class Requirements(sdk2.Requirements):
        container_resource = 2562397288
        cores = 2
        ram = 3000
        disk_space = 20 * 1024
        dns = ctm.DnsType.DNS64
        client_tags = ctc.Tag.Group.LINUX & ctc.Tag.LINUX_BIONIC
        environments = (sdk2.environments.NodeJS('12.13.0', 'linux'),)

    class Parameters(sdk2.Task.Parameters):
        tcpdump_args = "-v 'host api.test.direct.yandex.ru'"

        tokens = sdk2.parameters.YavSecret(
            "YAV secret id",
            default="sec-01crdc7rw80nvwge7aej7ztdnv"
        )

        with sdk2.parameters.Group('Настройки репозитория') as repo_block:
            arc_branch = sdk2.parameters.String(
                'Build branch',
                default='DIRECTCLIENT-14384',
                required=True,
                description='Имя ветки, из которой должна происходить сборка'
            )

        with sdk2.parameters.Group('Настройки тестов') as test_block:
            run_unit_tests = sdk2.parameters.Bool(
                'Run unit tests',
                default=True,
                required=True,
                description='Unit тесты'
            )

            run_integration_tests = sdk2.parameters.Bool(
                'Run integration tests',
                default=True,
                required=True,
                description='Интеграционные тесты'
            )

            run_ui_tests = sdk2.parameters.Bool(
                'Run ui tests',
                default=True,
                required=True,
                description='UI тесты'
            )

            run_func_tests = sdk2.parameters.Bool(
                'Run func tests',
                default=True,
                required=True,
                description='Функциональные тесты'
            )

            smoke_only = sdk2.parameters.Bool(
                'Run smoke only tests',
                default=True,
                required=True,
                description='Запускать только smoke тесты'
            )

    def get_env(self):
        logging.debug('Initializing environments: {}'.format(os.environ))

        command_env = os.environ.copy()
        command_env["SMOKE_ONLY"] = "1" if self.Parameters.smoke_only else "0"
        command_env["RUN_UNIT"] = "1" if self.Parameters.run_unit_tests else "0"
        command_env["RUN_INTEGR"] = "1" if self.Parameters.run_integration_tests else "0"
        command_env["RUN_UI"] = "1" if self.Parameters.run_ui_tests else "0"
        command_env["RUN_FUNC"] = "1" if self.Parameters.run_func_tests else "0"

        return command_env

    def on_prepare(self):
        logging.debug('Preparing task...')
        with sdk.mount_arc_path(self.parameters.arcadia_url) as arcadia:

            logging.debug('Listing dir: {}'.format(os.listdir(os.getcwd())))
            repo_path = os.path.join(arcadia, 'adv', 'frontend', 'services', 'commander')

            self.save_secret("notarizeAppleId.js", os.path.join(repo_path, "scripts/notarizeAppleId.js"))
            self.save_secret("notarizeApplePassword.js", os.path.join(repo_path, "scripts/notarizeApplePassword.js"))
            self.save_secret("signerToken.js", os.path.join(repo_path, "scripts/signerToken.js"))
            self.save_secret("mds-access-key", os.path.join(repo_path, "scripts/mdsAccessKey.js"), False)
            self.save_secret("mds-secret-key", os.path.join(repo_path, "scripts/mdsSecretKey.js"), False)
            self.save_secret("developer-id-cert", os.path.join(repo_path, "scripts/developerIdCert.js"))

    def get_artifacts(self):
        artifacts_path = "repo/artifacts"
        artifacts_resource = DcArtifactsData(self, "Artifacts directory", artifacts_path)

        return sdk2.ResourceData(artifacts_resource)

    def save_secret(self, secret_name, secret_path, is_file_secret=True):
        logging.debug('Save secret {}'.format(secret_name))
        secret_file = open(secret_path, 'w')

        secret = self.Parameters.tokens.data()[secret_name]
        secret_file.write(secret.decode("base64") if is_file_secret else secret)

        secret_file.close()

    def on_timeout(self, prev_status):
        self.get_artifacts().ready()

    def on_failure(self, prev_status):
        self.get_artifacts().ready()

    def on_execute(self):
        logging.info("Start build...")

        tests_path = os.path.abspath("repo/scripts/sandbox/tests_linux.sh")

        with sdk2.helpers.ProcessLog(self, logger='build') as pl:
            subprocess.check_call(
                "chmod +x {}".format(tests_path),
                env=self.get_env(),
                cwd="repo",
                shell=True,
                stdout=pl.stdout,
                stderr=pl.stderr
            )

            subprocess.check_call(
                tests_path,
                env=self.get_env(),
                cwd="repo",
                shell=True,
                stdout=pl.stdout,
                stderr=pl.stderr
            )

            self.get_artifacts().ready()
