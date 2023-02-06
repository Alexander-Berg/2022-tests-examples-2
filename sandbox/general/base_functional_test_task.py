# -*- coding: utf-8 -*-
import os

from sandbox import sdk2
import datetime
from sandbox.sdk2.path import Path
import logging
import sandbox.common.types.resource as ctr
import sandbox.common.types.misc as ctm
from sandbox.projects.clickhouse.BaseOnCommitTask.simple_test_task import SimpleDockerBuildTestTask
from sandbox.projects.clickhouse.resources import CLICKHOUSE_COVERAGE_PART
from sandbox.projects.clickhouse.BaseOnCommitTask.base import NeedToRunDescription
from sandbox.projects.clickhouse.util.deprecated import FunctionalTestDeprecated
from sandbox.projects.clickhouse.resources import CLICKHOUSE_BUILD_LXC_CONTAINER

import sandbox.common.types.client as ctc


class ClickhouseFunctionalTestBase(SimpleDockerBuildTestTask):

    class Requirements(SimpleDockerBuildTestTask.Requirements):
        client_tags = ctc.Tag.GENERIC & (ctc.Tag.INTEL_E5_2660 | ctc.Tag.INTEL_E5_2650 | ctc.Tag.INTEL_E5_2660V4 | ctc.Tag.INTEL_E5_2683V4 | ctc.Tag.INTEL_E5_2683)
        ram = 96 * 1024  # 96GB

    class Parameters(SimpleDockerBuildTestTask.Parameters):
        env_to_image = sdk2.parameters.List("Env variables passed to docker image", default=[])

    @staticmethod
    def order():
        return 100

    def should_skip_tests(self):
        return []

    def with_coverage(self):
        return False

    def with_raw_logs(self):
        return True

    def run_tests_randomly(self):
        return False

    def get_tests_to_run(self):
        return []

    def get_additional_envs(self):
        return {"S3_ACCESS_KEY_ID" : sdk2.Vault.data(self.Parameters.s3_access_key_id),
                "S3_SECRET_ACCESS" : sdk2.Vault.data(self.Parameters.s3_access_key),
                "MAX_RUN_TIME" : str(int(self.Parameters.kill_timeout * 0.9))}

    def need_ramdrive_for_paths(self):
        return {}

    def on_create(self):
        self.Parameters._container = sdk2.Resource.find(
            CLICKHOUSE_BUILD_LXC_CONTAINER,
            state=ctr.State.READY,
            attrs=dict(released="stable")
        ).order(-CLICKHOUSE_BUILD_LXC_CONTAINER.id).limit(1).first().id

        if self.need_ramdrive_for_paths():
            logging.info("Adding ramdrive to run")
            self.Requirements.ramdrive = ctm.RamDrive(ctm.RamDriveType.TMPFS, 25 * 1024, None)

    def get_run_cmd(self, build_path, result_path, server_log_path, repo_path, perfraw_path):
        skip_tests = self.should_skip_tests()

        # Additionally, read file with skipped tests from current branch.
        # It is needed to skip tests for release branch.
        # TODO: remove after 20.3 expires
        try:
            skip_tests_path = os.path.join(repo_path, 'tests', 'skip_tests.txt')
            if not os.path.exists(skip_tests_path):
                logging.info("File %s not found. No additional tests will be skipped.", skip_tests_path)
            else:
                with open(skip_tests_path) as f:
                    skip_tests += [test for test in f.read().split()]
        except Exception:
            logging.exception("Cannot read file with skipped tests")

        skip_test_cmd = ""
        if skip_tests:
            skip_test_cmd = '-e SKIP_TESTS_OPTION="--skip ' + ' '.join(skip_tests) + '"'

        additional_options = ['--hung-check']
        if self.run_tests_randomly():
            additional_options.append('--order=random')

        additional_options.append('--print-time')

        additional_options += self.get_tests_to_run()
        additional_options_str = '-e ADDITIONAL_OPTIONS="' + ' '.join(additional_options) + '"'

        env_str = ''
        if self.Parameters.env_to_image:
            env_str = ' '.join(['-e ' + var for var in self.Parameters.env_to_image])

        additional_envs = self.get_additional_envs()
        if additional_envs:
            env_str += ' ' + ' '.join(['-e {}={}'.format(env, value) for env, value in additional_envs.items()])

        if self.with_coverage():
            coverage_part = "--volume={}:/profraw".format(perfraw_path)
        else:
            coverage_part = ""

        ramdrive_volume_str = ""
        if self.need_ramdrive_for_paths():
            cmd_parts = []
            ramdrive_base_path = str(self.ramdrive.path)
            for mounted_path in self.need_ramdrive_for_paths():
                fname = mounted_path.replace('/', '_')
                ramdrive_path = os.path.join(ramdrive_base_path, fname)
                os.mkdir(ramdrive_path)
                os.chmod(ramdrive_path, 0o777)
                cmd_parts.append("--volume={}:{}".format(ramdrive_path, mounted_path))
            ramdrive_volume_str = ' '.join(cmd_parts)

        cmd = "docker run --volume={}:/package_folder --volume={}:/test_output --volume={}:/var/log/clickhouse-server {} --cap-add=SYS_PTRACE {coverage} {skip} {additional} {envstr} {image}".format(
            build_path,
            result_path,
            server_log_path,
            ramdrive_volume_str,
            skip=skip_test_cmd,
            coverage=coverage_part,
            image=self.get_single_image_with_version(),
            additional=additional_options_str,
            envstr=env_str,
        )

        return cmd

    def make_coverage_resource(self, path_to_compressed_coverage, commit, pull_request):
        compiler, package, build_type, sanitizer, bundled, splitted, tidy, _ = self.required_build_properties()
        coverage_res = CLICKHOUSE_COVERAGE_PART(
            self,
            "Clickhouse coverage part with commit {} ".format(commit.sha),
            "./coverage_part_" + str(self.id) + ".tar.gz",
            commit=commit.sha,
            date=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            pr_number=pull_request.number,
            compiler=compiler,
            build_type=build_type,
            sanitizer=sanitizer,
            bundled=bundled,
            package_type=package,
            splitted=splitted,
            tidy=tidy,
            task_context_name=self.get_context_name(),
        )

        coverage_res_data = sdk2.ResourceData(coverage_res)
        coverage_res_data.path.write_bytes(Path(path_to_compressed_coverage).read_bytes())
        coverage_res_data.ready()

    def process_result(self, result_path, server_log_path, perfraw_path, commit, repo, pull_request):
        return FunctionalTestDeprecated.process_result(self, result_path, server_log_path, perfraw_path, commit, repo, pull_request)

    @staticmethod
    def run_if_not_release_or_backport(pr_info):
        if 'pr-backport' in pr_info.labels or 'release' in pr_info.labels:
            return NeedToRunDescription(False, 'Not ran for backport or release PRs', False)
        return SimpleDockerBuildTestTask.need_to_run(pr_info)

    @staticmethod
    def run_if_master(pr_info):
        if pr_info.number != 0 and not ('pr-backport' in pr_info.labels or 'release' in pr_info.labels):
            return NeedToRunDescription(False, 'Not ran for PRs', False)
        return SimpleDockerBuildTestTask.need_to_run(pr_info)

    @staticmethod
    def run_if_ordinary_pr(pr_info):
        if 'pr-backport' in pr_info.labels or 'release' in pr_info.labels:
            return NeedToRunDescription(False, 'Not ran for backport or release PRs', False)
        if pr_info.number == 0:
            return NeedToRunDescription(False, 'Not ran for master', False)
        return SimpleDockerBuildTestTask.need_to_run(pr_info)
