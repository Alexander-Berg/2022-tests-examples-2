# -*- coding: utf-8 -*-

from __future__ import absolute_import, print_function, unicode_literals

import logging

from sandbox import sdk2
from sandbox.sdk2 import yav
from sandbox.sdk2.vcs.svn import Arcadia

from sandbox.projects.di.settings import SANDBOX_VAULT
from sandbox.projects.trendbox_ci.beta.resources import TRENDBOX_CI_LXC_IMAGE_BETA


class DiTestingPullUp(sdk2.Task):

    @property
    def script(self):
        return str(self.path("script.sh"))

    class Requirements(sdk2.Requirements):
        disk_space = 300 * 1024  # 300 Gb
        cores = 2

        container_resource = sdk2.parameters.Container(
            resource_type=TRENDBOX_CI_LXC_IMAGE_BETA,
            attrs={
                "owner": "DI",
            },
        )

    class Parameters(sdk2.Task.Parameters):

        with sdk2.parameters.RadioGroup("Destination cluster") as dst_db:
            dst_db.values["distribution2_test"] = dst_db.Value(value="ts")
            dst_db.values["distribution_development"] = dst_db.Value(value="dev")

        kill_timeout = 5 * 60 * 60
        description = "terrain ahead"

    def on_execute(self):

        Arcadia.export(
            "arcadia:/arc/trunk/arcadia/distribution_interface/scripts/testing_pullup.sh",
            self.script,
        )

        secret = yav.Secret(SANDBOX_VAULT).data()

        sdk2.paths.chmod(self.script, 0o755)
        with sdk2.helpers.ProcessLog(self, logger=logging.getLogger("pullup")) as pl:
            proc = sdk2.helpers.subprocess.Popen(
                self.script,
                stdout=pl.stdout,
                stderr=sdk2.helpers.subprocess.STDOUT,
                env={
                    "DST_DB": self.Parameters.dst_db,
                    "DST_DB_USER": secret["di_dev_db_user"],
                    "DST_DB_PASS": secret["di_dev_db_pass"],
                    "SRC_DB_USER": secret["di_src_db_user"],
                    "SRC_DB_PASS": secret["di_src_db_pass"],
                }
            )
            proc.communicate()
            if proc.returncode:
                raise RuntimeError("the script returned {}".format(proc.returncode))
