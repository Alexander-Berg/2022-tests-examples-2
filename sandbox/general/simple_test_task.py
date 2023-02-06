# -*- coding: utf-8 -*-
import logging
from sandbox import sdk2
import sandbox.sdk2.helpers
import subprocess
import os
import sandbox.common.types.resource as ctr

from sandbox.projects.clickhouse.BaseOnCommitTask.base import PostStatuses
from sandbox.projects.clickhouse.BaseOnCommitTask.test_task import BaseOnCommitTestTask
from sandbox.projects.clickhouse.resources import CLICKHOUSE_BUILD, CLICKHOUSE_BUILD_LXC_CONTAINER
from sandbox.projects.clickhouse.util.task_helper import get_ci_config

PERFRAW_DIR_NAME = "perfraw"


class SimpleDockerBuildTestTask(BaseOnCommitTestTask):

    build_path = ""

    @staticmethod
    def need_docker():
        return True

    class Requirements(BaseOnCommitTestTask.Requirements):
        ram = 32 * 1024  # 32GB
        privileged = True

    class Parameters(BaseOnCommitTestTask.Parameters):
        _container = sdk2.parameters.Container(
            "Environment container resource",
            resource_type=CLICKHOUSE_BUILD_LXC_CONTAINER,
        )

    def on_create(self):
        self.Parameters._container = sdk2.Resource.find(
            CLICKHOUSE_BUILD_LXC_CONTAINER,
            state=ctr.State.READY,
            attrs=dict(released="stable")
        ).order(-CLICKHOUSE_BUILD_LXC_CONTAINER.id).limit(1).first().id

    def post_statuses(self):
        return PostStatuses.ALWAYS

    @staticmethod
    def required_build_properties():
        raise Exception("Unimplemented")

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

        attrs = dict(
            commit=commit.sha,
            pr_number=pull_request.number,
            package_type=package_type,
            build_type=build_type,
            sanitizer=sanitizer,
            bundled=bundled,
            compiler=compiler,
            splitted=splitted,
            tidy=tidy,
            with_coverage=with_coverage,
        )
        logging.info("Searching for CLICKHOUSE_BUILD at commit %s filter %s", commit.sha, attrs)
        bresources = sdk2.Resource.find(
            CLICKHOUSE_BUILD,
            attrs=attrs,
            state=ctr.State.READY
        ).order(-CLICKHOUSE_BUILD.id).limit(1)
        logging.info("Search finished. Found {} resources, first: {}".format(bresources.count, bresources.first()))

        return bresources.first()

    def _save_resources(self, commit, repo, pull_request):
        if not self.build_path:
            logging.info("Downloading CLICKHOUSE_BUILD resource")
            build_resource = self.get_resources(commit, repo, pull_request)
            build_data = sdk2.ResourceData(build_resource)
            self.build_path = str(build_data.path)  # deb package
            logging.info("Download finished, build path %s", self.build_path)
        else:
            logging.info("Resource already downloaded %s", self.build_path)
        return self.build_path

    def run_cmd(self, cmd, log_name):
        with sandbox.sdk2.helpers.ProcessLog(self, logger=log_name) as pl:
            with open(str(pl.stdout.path), 'a') as f:
                f.write("Executing cmd: '{}'\n".format(cmd))
            logging.info("Executing cmd: %s", cmd)
            process = subprocess.Popen(cmd, shell=True, stderr=pl.stdout, stdout=pl.stdout)
            retcode = process.wait()  # no timeout in python2
            if retcode == 0:
                logging.info("Run successfully")
            else:
                logging.info("Run failed")
            return str(pl.stdout.path)

    # currenly doesn't work
    def async_callback_on_run_cmd_log(self, log_path):
        pass

    def get_prepare_cmd(self, build_path, result_folder, server_log, repo_path):
        return ""

    def get_run_cmd(self, build_path, result_folder, server_log, repo_path, perfraw_path):
        raise Exception("Unimplemented")

    def process_result(self, result_folder, server_log_folder, perfraw_path, commit, repo, pull_request):
        raise Exception("Unimplemented")

    def make_coverage_resource(self, path_to_part_directory, commit, pull_request):
        logging.info("Found coverage files, but coverage is not supported for %s", self.get_context_name())

    def with_coverage(self):
        return False

    def run(self, commit, repo, pull_request):
        build_path = self._save_resources(commit, repo, pull_request)
        logging.info("Got build %s", build_path)
        repo_resource = self.resource_helper.get_repo_with_submodules_resource()
        repo_path = self.resource_helper.save_any_repo_resource(repo_resource, os.path.join(str(self.path()), "ClickhouseSource"))
        result_folder = os.path.join(str(self.path()), "test_output")
        if not os.path.exists(result_folder):
            logging.info("Folder %s not exists", result_folder)
            os.mkdir(result_folder)
        else:
            logging.info("Folder %s exists", result_folder)

        server_log_folder = os.path.join(str(self.path()), "server_log")
        if not os.path.exists(server_log_folder):
            logging.info("Folder %s not exists", server_log_folder)
            os.mkdir(server_log_folder)
        else:
            logging.info("Folder %s exists", server_log_folder)

        prepare_cmd = self.get_prepare_cmd(build_path, result_folder, server_log_folder, repo_path)
        if prepare_cmd:
            logging.info("Running prepare cmd")
            prepare_log_path = self.run_cmd(prepare_cmd, "prepare_test_run.txt")
            logging.info("Prepared, log path %s", prepare_log_path)
        else:
            logging.info("Prepare cmd empty will do nothing")

        perfraw_path = os.path.join(str(self.path()), PERFRAW_DIR_NAME)

        cmd = self.get_run_cmd(build_path, result_folder, server_log_folder, repo_path, perfraw_path)
        logging.info("Running cmd type %s text '%s'", type(cmd), cmd)
        if isinstance(cmd, list):
            logging.info("Running list of commands")
            for single_command in cmd:
                log_path = self.run_cmd(single_command, "test_run.txt")  # log path same for all
            logging.info("List run finished")
        else:
            logging.info("Run single cmd {}".format(cmd))
            log_path = self.run_cmd(cmd, "test_run.txt")
            logging.info("finished")

        state, description, test_results, additional_logs = self.process_result_simple(result_folder, server_log_folder, perfraw_path, commit, repo, pull_request)
        return state, description, test_results, log_path, additional_logs
