# -*- coding: utf-8 -*-

import os
import logging
import tarfile
import subprocess

import sandbox.sdk2 as sdk2
import sandbox.sdk2.parameters as sb_parameters
import sandbox.sdk2.ssh as ssh
from sandbox.projects.common.utils import sync_resource


class TelluriumAcceptanceTests(sdk2.Resource):
    pass


class QafwTelluriumAcceptanceTests(sdk2.Task):
    """
    Tellurium acceptance tests https://st.yandex-team.ru/QAFW-2688
    """
    class Parameters(sdk2.Parameters):
        QuotaGit = sb_parameters.String('Git', default='ssh://git@bb.yandex-team.ru/selenium/grid-router-deb.git')
        TelluriumAcceptanceTestsPackageId = sb_parameters.String('Resource of tellurium AT package', default='830914405')
        TelluriumATCmdArgs = sb_parameters.String('Cmd line args for tellurium_at')
        SendToGraphite = sb_parameters.Bool('Send to graphite')

    def on_enqueue(self):
        self.Context.tellurium_at = TelluriumAcceptanceTests(self, 'Tellurium AT', 'tellurium_at').id

    def on_execute(self):
        out_dir = str(self.log_path("out"))
        os.makedirs(out_dir)
        tellurium_at_dir = self._get_tellurium_at()

        command = [
            os.path.join(tellurium_at_dir, "tellurium_at"),
            "--http-url", "https://proxy.sandbox.yandex-team.ru/{}/features".format(self.Context.tellurium_at),
            "--quota", self._clone_quota_git(self.Parameters.QuotaGit),
            "--features-dir", os.path.join(tellurium_at_dir, "features"),
            self.Parameters.TelluriumATCmdArgs,
            "--out", out_dir,
        ]
        if self.Parameters.SendToGraphite:
            command += ["--send-stat"]

        env = os.environ.copy()
        env["VALID_PORT_RANGE"] = "10000:65536"
        self._execute_command(" ".join(command), shell=True, verify_exit_code=True, env=env)

    def _execute_command(self, command, cwd=None, env=None, under_robot_qafw=False, shell=False, verify_exit_code=False):
        def execute():
            logging.info("Running %s in %s with env %s", command, cwd, env)
            p = subprocess.Popen(command, shell=shell, cwd=cwd, env=env)
            p.communicate()
            logging.info("return code: %s", p.returncode)
            if verify_exit_code and p.returncode != 0:
                raise Exception("Command {} failed with code: {}".format(command, p.returncode))
        if under_robot_qafw:
            with ssh.Key(self, "QADEV", "robot-qafw-key"):
                execute()
        else:
            execute()

    def _get_tellurium_at(self):
        resource = sdk2.Resource[self.Context.tellurium_at]
        dest = str(resource.path)
        tools = str(sync_resource(self.Parameters.TelluriumAcceptanceTestsPackageId))
        with tarfile.open(tools) as tf:
            tf.extractall(dest)
        sdk2.ResourceData(resource).ready()
        return os.path.abspath(dest)

    def _git_clone(self, url, path):
        self._execute_command(" ".join(["git", "clone", url, path]), under_robot_qafw=True, shell=True)

    def _clone_quota_git(self, git_path):
        clone_path = os.path.abspath("grid-router-deb")
        self._git_clone(git_path, clone_path)
        return os.path.join(clone_path, "quota.json")
