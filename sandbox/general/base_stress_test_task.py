# -*- coding: utf-8 -*-
import sandbox.common.types.client as ctc
from sandbox.projects.clickhouse.BaseOnCommitTask.simple_test_task import SimpleDockerBuildTestTask
from sandbox.projects.clickhouse.util.deprecated import StressTestDeprecated


class ClickhouseStressTestBase(SimpleDockerBuildTestTask):

    class Requirements(SimpleDockerBuildTestTask.Requirements):
        client_tags = ctc.Tag.GENERIC & (ctc.Tag.INTEL_E5_2660V4 | ctc.Tag.INTEL_E5_2660 | ctc.Tag.INTEL_E5_2650 | ctc.Tag.INTEL_E5_2683V4 | ctc.Tag.INTEL_E5_2683)

    def should_skip_tests(self):
        return []

    def get_run_cmd(self, build_path, result_folder, server_log_folder, repo_path, perfraw_path):
        skip_tests = self.should_skip_tests()
        skip_test_cmd = ""
        if skip_tests:
            skip_test_cmd = ' -e SKIP_TESTS_OPTION="--skip ' + ' '.join(skip_tests) + '"'

        cmd = "docker run " + \
              "--volume={}:/package_folder ".format(build_path) + \
              "--volume={}:/test_output ".format(result_folder) + \
              "--volume={}:/var/log/clickhouse-server ".format(server_log_folder) + \
              skip_test_cmd + " " + \
              self.get_single_image_with_version()

        return cmd

    @staticmethod
    def order():
        return 1000

    @staticmethod
    def get_images_names():
        return ["yandex/clickhouse-stress-test"]

    def process_result(self, result_folder, server_log_folder, perfraw_path, commit, repo, pull_request):
        return StressTestDeprecated.process_result(self, result_folder, server_log_folder, perfraw_path, commit, repo, pull_request)
