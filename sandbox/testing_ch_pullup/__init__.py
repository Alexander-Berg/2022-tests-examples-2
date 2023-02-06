# -*- coding: utf-8 -*-

from __future__ import absolute_import, print_function, unicode_literals

import logging

import sandbox.common.types.misc as ctm
from sandbox import sdk2
from sandbox.projects.di.settings import SANDBOX_VAULT
from sandbox.sdk2 import yav
from sandbox.sdk2.helpers.process import ProcessLog, subprocess
from sandbox.sdk2.vcs.svn import Arcadia

# Непротухающий (ttl=inf) контейнер с окружением для сборки фронта.
IMMORTAL_CONTAINER_ID = 658230636


class DiTestingChPullUp(sdk2.Task):

    @property
    def script(self):
        return str(self.path("script.sh"))

    class Requirements(sdk2.Requirements):
        disk_space = 300 * 1024  # 300 Gb
        cores = 2

        # для доступа к нпм (нпм летом 2018 все еще не умеет в ipv6)
        dns = ctm.DnsType.DNS64
        # Запускаемся рутом
        privileged = True

    class Parameters(sdk2.Task.Parameters):

        with sdk2.parameters.RadioGroup("Suspend before script") as suspend_before_script:
            suspend_before_script.values["suspend_before_script"] = suspend_before_script.Value(value="true")
            suspend_before_script.values["not_suspend_before_script"] = suspend_before_script.Value(value="false")

        kill_timeout = 5 * 60 * 60
        description = "terrain ahead"

        container = sdk2.parameters.Container(
            "Container",
            description="LXC Container with docker installed",
            default_value=IMMORTAL_CONTAINER_ID,
            required=True,
        )

    def preinstall(self):
        with ProcessLog(logger=logging.getLogger("apt update")) as pl:
            subprocess.Popen(["apt-get", "update"], stdout=pl.stdout, stderr=pl.stderr).wait()
            subprocess.Popen(
                ["apt-get", "install", "-y", "--force-yes", "wget"],
                stdout=pl.stdout,
                stderr=pl.stderr,
            ).wait()
            subprocess.Popen(
                ["apt-get", "install", "-y", "--force-yes", "apt-transport-https" "ca-certificates", "dirmngr"],
                stdout=pl.stdout,
                stderr=pl.stderr,
            ).wait()
            subprocess.Popen(
                ["echo", "\"deb https://repo.clickhouse.tech/deb/stable/ main/\"", "|", "tee", "/etc/apt/sources.list.d/clickhouse.list"],
                stdout=pl.stdout,
                stderr=pl.stderr,
            ).wait()
            subprocess.Popen(["apt-get", "update"], stdout=pl.stdout, stderr=pl.stderr).wait()
            subprocess.Popen(
                ["apt-get", "install", "-y", "--force-yes", "clickhouse-client"],
                stdout=pl.stdout,
                stderr=pl.stderr,
            ).wait()
            subprocess.Popen(
                ["mkdir", "-p", "~/.clickhouse-client"],
                stdout=pl.stdout,
                stderr=pl.stderr,
            ).wait()
            subprocess.Popen(
                [
                    "wget",
                    "\"https://storage.yandexcloud.net/mdb/clickhouse-client.conf.example\"",
                    "-O",
                    "~/.clickhouse-client/config.xml",
                ],
                stdout=pl.stdout,
                stderr=pl.stderr,
            ).wait()

    def on_execute(self):
        self.preinstall()
        Arcadia.export(
            "arcadia:/arc/trunk/arcadia/distribution_interface/scripts/testing_ch_pullup.sh",
            self.script,
        )

        secret = yav.Secret(SANDBOX_VAULT).data()

        sdk2.paths.chmod(self.script, 0o755)
        if self.Parameters.suspend_before_script == "suspend_before_script":
            self.suspend()
        with sdk2.helpers.ProcessLog(self, logger=logging.getLogger("pullup")) as pl:
            proc = sdk2.helpers.subprocess.Popen(
                self.script,
                stdout=pl.stdout,
                stderr=sdk2.helpers.subprocess.STDOUT,
                env={
                    "DST_DB_USER": secret["di_dev_ch_user"],
                    "DST_DB_PASS": secret["di_dev_ch_pass"],
                    "SRC_DB_USER": secret["di_src_ch_user"],
                    "SRC_DB_PASS": secret["di_src_ch_pass"],
                }
            )
            proc.communicate()
            if proc.returncode:
                raise RuntimeError("the script returned {}".format(proc.returncode))
