# -*- coding: utf-8 -*-
import logging
from sandbox import sdk2
import sandbox.common.types.resource as ctr
import sandbox.common.types.client as ctc
import sandbox.common.types.misc as ctm
import sandbox.sdk2.helpers
import subprocess
import os
import json

from sandbox.projects.clickhouse.BaseOnCommitTask.base import PostStatuses
from sandbox.projects.clickhouse.BaseOnCommitTask.test_task import BaseOnCommitTestTask
from sandbox.projects.clickhouse.resources import CLICKHOUSE_BUILD, CLICKHOUSE_BUILD_LXC_CONTAINER, CLICKHOUSE_REPO_NO_SUBMODULES
from sandbox.projects.clickhouse.util.task_helper import decompress_fast, get_ci_config
from sandbox.projects.clickhouse.util.deprecated import IntergationTestDeprecated, IntergationTestFlakyCheckDeprecated


class ClickhouseIntegrationTestsBase(BaseOnCommitTestTask):
    @staticmethod
    def need_docker():
        return True

    # Start earlier, because these tests are long.
    @staticmethod
    def order():
        return 11

    class Parameters(BaseOnCommitTestTask.Parameters):
        _container = sdk2.parameters.Container(
            "Environment container resource",
            resource_type=CLICKHOUSE_BUILD_LXC_CONTAINER,
        )
        kill_timeout = 8 * 60 * 60
        test_to_skip = sdk2.parameters.List("Test to skip", default=[])

    class Requirements(BaseOnCommitTestTask.Requirements):
        client_tags = ctc.Tag.GENERIC & (ctc.Tag.INTEL_E5_2660 | ctc.Tag.INTEL_E5_2660V1 | ctc.Tag.INTEL_E5_2660V4 | ctc.Tag.INTEL_E5_2683V4 | ctc.Tag.INTEL_E5_2683)
        ram = 32 * 1024  # 32GB
        disk_space = 45 * 1024
        privileged = True
        ramdrive = ctm.RamDrive(ctm.RamDriveType.TMPFS, 32 * 1024, None)

    def on_create(self):
        self.Parameters._container = sdk2.Resource.find(
            CLICKHOUSE_BUILD_LXC_CONTAINER,
            status=ctr.State.READY,
            attrs=dict(released="stable")
        ).order(-CLICKHOUSE_BUILD_LXC_CONTAINER.id).first().id

    @staticmethod
    def docker_root_on_tmpfs():
        return True

    @staticmethod
    def require_internet():
        return True

    def post_statuses(self):
        return PostStatuses.ALWAYS

    @staticmethod
    def required_build_properties():
        raise Exception("Unimplemented")

    def get_additional_envs(self):
        return {}

    @staticmethod
    def get_images_names():
        return ["yandex/clickhouse-integration-tests-runner", "yandex/clickhouse-mysql-golang-client",
                "yandex/clickhouse-mysql-java-client", "yandex/clickhouse-mysql-js-client",
                "yandex/clickhouse-mysql-php-client", "yandex/clickhouse-postgresql-java-client",
                "yandex/clickhouse-integration-test", "yandex/clickhouse-kerberos-kdc",
                "yandex/clickhouse-integration-helper", ]

    @classmethod
    def get_resources(cls, commit, repo, pull_request):
        ci_config = get_ci_config(pull_request, commit)
        if not ci_config or cls.get_context_name() not in ci_config["tests_config"]:
            logging.info("Build config not found :(, will use default from params")
            compiler, package_type, build_type, sanitizer, bundled, splitted, tidy, with_coverage = cls.required_build_properties()
        else:
            logging.info("Build config found, will take info from repository")
            tests_config = ci_config["tests_config"]
            test_config = tests_config[cls.get_context_name()]["required_build_properties"]
            compiler = test_config["compiler"]
            package_type = test_config["package_type"]
            build_type = test_config["build_type"]
            sanitizer = test_config["sanitizer"]
            bundled = test_config["bundled"]
            splitted = test_config["splitted"]
            tidy = test_config["clang-tidy"]
            with_coverage = test_config["with_coverage"]

        logging.info("Searching for CLICKHOUSE_BUILD at commit %s", commit.sha)
        bresources = sdk2.Resource.find(
            CLICKHOUSE_BUILD,
            attrs=dict(
                commit=commit.sha,
                pr_number=pull_request.number,
                compiler=compiler,
                package_type=package_type,
                build_type=build_type,
                sanitizer=sanitizer,
                bundled=bundled,
                splitted=splitted,
                tidy=tidy,
                with_coverage=with_coverage,
            ),
            state=ctr.State.READY
        ).order(-CLICKHOUSE_BUILD.id).limit(1)
        logging.info("Search finished")

        build_resource = bresources.first()

        if build_resource is None:
            return None

        logging.info("Searching for CLICKHOUSE_REPO_NO_SUBMODULES at commit %s", commit.sha)

        rresources = sdk2.Resource.find(
            CLICKHOUSE_REPO_NO_SUBMODULES,
            attrs=dict(commit=commit.sha, pr_number=pull_request.number),
            state=ctr.State.READY
        ).order(-CLICKHOUSE_REPO_NO_SUBMODULES.id).limit(1)
        logging.info("Search finished")

        repo_resporce = rresources.first()

        if repo_resporce is None:
            return None

        return build_resource, repo_resporce

    def should_skip_tests(self):
        return self.Parameters.test_to_skip

    def save_resources(self, commit, repo, pull_request):
        logging.info("Downloading CLICKHOUSE_BUILD resource")
        build_resource, repo_resource = self.get_resources(commit, repo, pull_request)
        build_data = sdk2.ResourceData(build_resource)
        build_path = str(build_data.path)  # deb package
        logging.info("Download finished, build path %s", build_path)

        logging.info("Downloading CLICKHOUSE_REPO_NO_SUBMODULES resource")
        repo_data = sdk2.ResourceData(repo_resource)
        repo_path = str(repo_data.path)
        logging.info("Download finished, repo path %s", repo_path)

        base_dir = str(self.ramdrive.path) if self.ramdrive is not None and self.ramdrive.path is not None else str(self.path())
        decompress_fast(repo_path, base_dir)

        return build_path, os.path.join(base_dir, "ClickHouse")

    def shuffle_test_groups(self):
        return False

    def _update_desc(self, log_name, group):
        self.Parameters.description += '\n<a href="https://proxy.sandbox.yandex-team.ru/task/{}/log1/{}.out.log">Test run log {}</a>'.format(self.id, log_name, group)

    def get_json_params_path(self):
        return os.path.join(str(self.path()), "params.json")

    def get_json_params_dict(self, commit, pull_request):
        return {
            'context_name': self.get_context_name(),
            'commit': commit.sha,
            'pull_request': pull_request.number,
            'pr_info': None,
            'docker_images_with_versions': self.Parameters.docker_images_with_versions,
            'shuffle_test_groups': self.shuffle_test_groups()
        }

    def get_env_for_tests_runner(self, build_path, repo_path, result_folder):
        binary_path, odbc_bridge_path, library_bridge_path = IntergationTestDeprecated._get_install_path(self)
        my_env = os.environ.copy()
        my_env["CLICKHOUSE_TESTS_BUILD_PATH"] = build_path
        my_env["CLICKHOUSE_TESTS_SERVER_BIN_PATH"] = binary_path
        my_env["CLICKHOUSE_TESTS_CLIENT_BIN_PATH"] = binary_path
        my_env["CLICKHOUSE_TESTS_ODBC_BRIDGE_BIN_PATH"] = odbc_bridge_path
        my_env["CLICKHOUSE_TESTS_LIBRARY_BRIDGE_BIN_PATH"] = library_bridge_path
        my_env["CLICKHOUSE_TESTS_REPO_PATH"] = repo_path
        my_env["CLICKHOUSE_TESTS_RESULT_PATH"] = result_folder
        my_env["CLICKHOUSE_TESTS_BASE_CONFIG_DIR"] = "{}/programs/server".format(repo_path)
        my_env["CLICKHOUSE_TESTS_DOCKERD_HOST"] = self.docker_sock()
        my_env["CLICKHOUSE_TESTS_JSON_PARAMS_PATH"] = self.get_json_params_path()
        add_env = self.get_additional_envs()
        for key in add_env:
            my_env[key] = add_env[key]
        return my_env

    def run(self, commit, repo, pull_request):
        if self.ramdrive is None or self.ramdrive.path is None:
            logging.warning("RamDrive is not created")
        else:
            logging.debug("RamDrive path:{}".format(self.ramdrive.path))

        build_path, repo_path = self.save_resources(commit, repo, pull_request)
        logging.info("Got build path %s", build_path)
        logging.info("Got repo path %s", repo_path)
        base_dir = str(self.path())
        result_folder = os.path.join(base_dir, "test_output")

        my_env = self.get_env_for_tests_runner(build_path, repo_path, result_folder)

        runner_path = os.path.join(repo_path, "tests/integration", "ci-runner.py")
        if not os.path.exists(runner_path):
            if 'flaky check' in self.get_context_name():
                return IntergationTestFlakyCheckDeprecated.run_impl(self, commit, repo, pull_request, repo_path, build_path, my_env)
            else:
                return IntergationTestDeprecated.run_impl(self, commit, repo, pull_request, repo_path, build_path, my_env)

        logging.info("Found ci-runner.py script")
        if not os.path.exists(result_folder):
            os.mkdir(result_folder)
        with open(self.get_json_params_path(), 'w') as json_params:
            json_params.write(json.dumps(self.get_json_params_dict(commit, pull_request)))

        log_path = None
        output_path = os.path.join(str(self.path()), "test_output/main_script_log.txt")
        cmd = "{} | tee {}".format(runner_path, output_path)
        with sandbox.sdk2.helpers.ProcessLog(self, logger="main_script_log.txt") as pl:
            logging.info("Executing cmd: %s", cmd)
            retcode = subprocess.Popen(cmd, shell=True, stderr=pl.stdout, stdout=pl.stdout, env=my_env).wait()
            if retcode == 0:
                logging.info("Run tests successfully")
            else:
                logging.info("Some tests failed")
            log_path = str(pl.stdout.path)

        state, description, test_results, additional_logs = self.process_result_simple(result_folder, None, None, commit, repo, pull_request)
        return state, description, test_results, log_path, additional_logs
