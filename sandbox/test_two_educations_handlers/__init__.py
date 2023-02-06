# -*- coding: utf-8 -*-

from sandbox import sdk2
from sandbox.sdk2.helpers import subprocess
from sandbox.projects.common import network
import os
import time

SECONDS_TO_WAIT_FOR_EXECUTABLES = 10

CONFIG_FILES_FOLDER = "/config_files/"
BETA_1_CONFIG = "beta_1_config.cfg"
BETA_2_CONFIG = "beta_2_config.cfg"
ADD_CONFIG = "add_config.cfg"

EDUCATION_EXECUTABLE_FOLDER = "some_directory"
EDUCATION_EXECUTABLE_NAME = "education"
TESTS_EXECUTABLE_NAME = "test_handlers"


class BetaJsonDump(sdk2.Resource):
    pass


class DumpsDiff(sdk2.Resource):
    pass


class DiffTestResult(sdk2.Resource):
    pass


class TestTwoEducationsHandlers(sdk2.Task):
    class Parameters(sdk2.Parameters):
        BETA_1_ARCHIVE = sdk2.parameters.Resource("Resource id for beta 1 archive")
        BETA_2_ARCHIVE = sdk2.parameters.Resource("Resource id for beta 2 archive")
        TESTS_EXECUTABLE = sdk2.parameters.Resource("Resource id for handlers_test script executable")
        TUTOR_CONFIG = sdk2.parameters.Resource("Resource id for archive with Tutor configs")

        YQL_TOKEN_OWNER = sdk2.parameters.String("YQL token owner")
        YQL_TOKEN_NAME = sdk2.parameters.String("YQL token name")
        TVM_TOKEN_OWNER = sdk2.parameters.String("TVM token owner")
        TVM_TOKEN_NAME = sdk2.parameters.String("TVM token name")

    def on_execute(self):
        beta_1_archive = str(sdk2.ResourceData(self.Parameters.BETA_1_ARCHIVE).path)
        beta_2_archive = str(sdk2.ResourceData(self.Parameters.BETA_2_ARCHIVE).path)
        tests_executable = str(sdk2.ResourceData(self.Parameters.TESTS_EXECUTABLE).path) + '/' + TESTS_EXECUTABLE_NAME
        tutor_config = str(sdk2.ResourceData(self.Parameters.TUTOR_CONFIG).path)

        yql_token = sdk2.Vault.data(
            self.Parameters.YQL_TOKEN_OWNER, self.Parameters.YQL_TOKEN_NAME)
        tvm_token = sdk2.Vault.data(
            self.Parameters.TVM_TOKEN_OWNER, self.Parameters.TVM_TOKEN_NAME)

        os.environ["TVM_TOKEN"] = tvm_token
        os.environ["OAUTH_TOKEN"] = yql_token

        configs_path = self.get_configs(tutor_config)
        beta_1_config = configs_path + BETA_1_CONFIG
        beta_2_config = configs_path + BETA_2_CONFIG
        add_config = configs_path + ADD_CONFIG

        self.run_beta(beta_1_archive, beta_1_config, add_config)
        self.run_beta(beta_2_archive, beta_2_config, add_config)

        self.run_tests(tests_executable, beta_1_config, beta_2_config)

        self.deploy_resource("dump_1", "json", "dump")
        self.deploy_resource("dump_2", "json", "dump")
        self.deploy_resource("dump_diff", "json", "diff")
        self.deploy_resource("result", "txt", "result")

    def extract(self, archive):
        cur_dir = os.getcwd()

        command = [
            "tar", "-xvzf",
            archive,
            "-C", cur_dir
        ]

        subprocess.Popen(command).wait()

    def get_configs(self, tutor_config):
        cur_dir = os.getcwd()
        self.extract(tutor_config)

        return cur_dir + CONFIG_FILES_FOLDER

    def run_beta(self, beta_archive, config, add_config):
        cur_dir = os.getcwd()
        self.extract(beta_archive)

        beta_exec = "{}/{}/{}".format(
            cur_dir,
            EDUCATION_EXECUTABLE_FOLDER,
            EDUCATION_EXECUTABLE_NAME)

        command = [
            beta_exec,
            "-c", config,
            "-a", add_config
        ]

        return subprocess.Popen(command)

    def run_tests(self, tests_executable, beta_1_config, beta_2_config):
        # wait a little bit so education executables have enough time to start up
        time.sleep(SECONDS_TO_WAIT_FOR_EXECUTABLES)

        address = network.get_my_ipv6()

        beta_1_port = self.get_port_from_config(beta_1_config)
        beta_2_port = self.get_port_from_config(beta_2_config)

        srcrwr1 = "[{}]:{}".format(address, str(beta_1_port))
        srcrwr2 = "[{}]:{}".format(address, str(beta_2_port))

        command = [
            tests_executable,
            "--need_dump", "--need_print",
            "--check_post",
            "--srcrwr1", srcrwr1,
            "--srcrwr2", srcrwr2,
            "--alias1", "old_executable",
            "--alias2", "new_executable"
        ]

        return subprocess.Popen(command).wait()

    def get_port_from_config(self, config_file):
        with open(config_file, "r") as config:
            for line in config:
                try:
                    option = line.split(':')
                    if option[0] == "AppHostPort":
                        return int(option[1].strip())
                except:
                    continue

        raise Exception("Port was not found in config file!")

    def deploy_resource(self, name, extension, file_type):
        file_name = name + '.' + extension

        if file_type == "dump":
            resource = sdk2.ResourceData(BetaJsonDump(self, name, file_name))
        if file_type == "diff":
            resource = sdk2.ResourceData(DumpsDiff(self, name, file_name))
        if file_type == "result":
            resource = sdk2.ResourceData(DiffTestResult(self, name, file_name))

        with open(file_name, 'r') as file:
            file_content = file.read()
            resource.path.write_bytes(file_content)
