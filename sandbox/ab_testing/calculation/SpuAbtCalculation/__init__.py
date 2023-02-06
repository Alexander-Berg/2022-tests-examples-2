# -*- coding: utf-8 -*-
import logging
import json
import os
import sys

from sandbox import sdk2
from sandbox.sdk2.helpers import subprocess as sp
from sandbox.projects.common import file_utils as fu
from sandbox.common.errors import TaskFailure
from sandbox.common.utils import classproperty
import sandbox.sandboxsdk.svn as svn
import sandbox.common.types.task as ctt
import sandbox.common.types.resource as ctr
import sandbox.common.types.notification as ctn
from sandbox.projects.resource_types import AB_TESTING_SPU_TEST_YA_PACKAGE


class LastBinaryResource(sdk2.parameters.Resource):
    resource_type = AB_TESTING_SPU_TEST_YA_PACKAGE
    state = (ctr.State.READY,)
    required = True

    @classproperty
    def default_value(cls):
        return sdk2.Resource.find(
            cls.resource_type,
            state=cls.state
        ).first()


class SpuAbtCalculationResult(sdk2.Resource):
    key = sdk2.parameters.String(
        "Calculation key",
        description="Calcullation key",
        required=True,
        hint=True,
    )


class SpuAbtCalculation(sdk2.Task):
    """SPU calculation"""

    class Requirements(sdk2.Task.Requirements):
        cores = 4
        ram = 1024 * 80
        disk_space = 8192

    class Parameters(sdk2.Task.Parameters):
        kill_timeout = 12 * 60 * 60
        notifications = [
            sdk2.Notification(
                [ctt.Status.FAILURE, ctt.Status.EXCEPTION, ctt.Status.NO_RES, ctt.Status.TIMEOUT],
                ['lpshka'],
                ctn.Transport.EMAIL
            )
        ]

        key = sdk2.parameters.String(
            "Calculation key",
            description="Calcullation key",
            required=True,
            hint=True,
        )
        author = sdk2.parameters.String(
            "Author"
        )
        resource = LastBinaryResource(
            "Resource with spu binary",
        )
        yt_token = sdk2.parameters.Vault(
            "YT token",
            description="'name' or 'owner:name' for extracting from Vault",
            required=True
        )
        yt_pool = sdk2.parameters.String(
            "YT pool",
            default=""
        )
        config = sdk2.parameters.JSON(
            "Config",
            required=True,
            default=[]
        )
        server = sdk2.parameters.String(
            "MR Server",
            required=True,
            default="hahn"
        )
        command_to_execute = sdk2.parameters.String(
            "Command to execute",
            default=""
        )
        threads = sdk2.parameters.Integer(
            "Thread",
            required=True,
            default=8
        )
        path = sdk2.parameters.String(
            "Path to spu session data",
            default=""
        )
        ignore_temporary_tables = sdk2.parameters.Bool(
            "Ignore temporary tables",
            default=True
        )

    class Context(sdk2.Task.Context):
        shell_commands = []
        files = {}

    def on_execute(self):
        with self.memoize_stage.prepare_environment(commit_on_entrance=False):
            logging.info("Extract binary")
            logging.info("Get shellabt lib")
            shellabt_path = svn.Arcadia.get_arcadia_src_dir("arcadia:/arc/trunk/arcadia/quality/ab_testing/scripts/shellabt/")
            sys.path.append(shellabt_path)
            import shellabt

            logging.info("Get binary resource")
            resource_path = str(sdk2.ResourceData(self.Parameters.resource).path)
            extract_path = "./"

            logging.info("Extract binary from archive '{resource_path}' to '{extract_path}'".format(resource_path=resource_path, extract_path=extract_path))
            for path_in_deb in ('/Berkanavt/ab_testing/bin', '/Berkanavt/ab_testing/scripts/interface'):
                for name, path in shellabt.DebianYaPackagePaths(resource_path, path_in_deb, extract_path).items.iteritems():
                    self.Context.files[name] = path

            logging.info("Binary extracted")

            logging.info("Save config")
            config_path = os.path.abspath("cfg.cfg")
            with open(config_path, "w") as config:
                json.dump(self.Parameters.config, config)
            self.Context.files["config"] = str(config_path)
            logging.info("Config saved")

            logging.info("Set YT environ")
            os.environ["MR_RUNTIME"] = "YT"
            os.environ["YT_TOKEN"] = self.Parameters.yt_token.data()
            if self.Parameters.yt_pool:
                os.environ["YT_POOL"] = self.Parameters.yt_pool

            self.Context.files["prepared_result"] = os.path.abspath("prepared_result.json")
            logging.info("Create shell commands")
            shell_command = [
                self.Context.files["spu-test"],
                "-s", self.Parameters.server,
                "-j", str(max(self.Requirements.cores, self.Parameters.threads)),
                "-f", self.Context.files["config"],
                "-o",
                "-r", self.Context.files["prepared_result"],
            ]
            if self.Parameters.command_to_execute:
                shell_command.extend(["-c", self.Parameters.command_to_execute])
            if self.Parameters.path:
                shell_command.extend(["-p", self.Parameters.path])
            if self.Parameters.ignore_temporary_tables:
                shell_command.append("-e")
            self.Context.shell_commands.append(" ".join(shell_command))

            self.Context.files["result"] = os.path.abspath("result.json")
            shell_command = [
                "python", self.Context.files["web.py"],
                self.Context.files["prepared_result"], self.Context.files["result"]
            ]
            self.Context.shell_commands.append(" ".join(shell_command))

        for shell_num, shell_command in enumerate(self.Context.shell_commands):
            shell_name = "shell_{shell_num}".format(shell_num=shell_num)
            with self.memoize_stage[shell_name](commit_on_entrance=False):
                with sdk2.helpers.ProcessLog(self, logger=logging.getLogger(shell_name)) as pl:
                    returncode = sp.Popen(shell_command, shell=True, stdout=pl.stdout, stderr=sp.STDOUT).wait()
                    if returncode != 0:
                        raise sp.CalledProcessError(returncode, shell_command)

        with self.memoize_stage.create_resource(commit_on_entrance=False):
            if not os.path.exists(self.Context.files["result"]):
                raise TaskFailure("Result file not exists")

            logging.info("Create resource")
            resource_data = sdk2.ResourceData(SpuAbtCalculationResult(
                self, "Result json", "result.json", key=self.Parameters.key
            ))
            resource_data.path.write_bytes(fu.read_file(self.Context.files["result"]))
            resource_data.ready()
