import os
import time

from sandbox import sdk2
from sandbox.sandboxsdk import environments
from sandbox.sdk2.helpers import subprocess as sp, ProcessLog
import sandbox.projects.news.resources as resources


class GetNewsApphostServiceRequests(sdk2.Task):

    environment = (
        environments.SvnEnvironment(),
    )

    class Requirements(sdk2.Task.Requirements):
        cores = 1
        disk_space = 1 * 1024
        ram = 2 * 1024

        class Caches(sdk2.Requirements.Caches):
            pass

    class Parameters(sdk2.Task.Parameters):
        service_name = sdk2.parameters.String(
            'Service name',
            required=True
        )

        custom_ammo_generation_command = sdk2.parameters.String(
            'Custom command to generate ammo for the service',
            required=False
        )

        graph_source_names = sdk2.parameters.List(
            'List of source names in graphs',
            required=True
        )

    def on_execute(self):
        with ProcessLog(self, 'bash_magic.log') as pl:
            environments.SvnEnvironment().prepare()

            sp.check_call(
                ["bash", "-c", "svn cat svn+ssh://arcadia.yandex.ru/arc/trunk/arcadia/ya | python - clone"],
                stdout=pl.stdout, stderr=pl.stderr
            )

            sp.check_call(
                ["arcadia/ya", "make", "--checkout", "arcadia/yweb/news/runtime_scripts/yappy"],
                stdout=pl.stdout, stderr=pl.stderr
            )

            sp.check_call(
                ["arcadia/ya", "make", "--checkout", "arcadia/yweb/news/runtime_scripts/load_testing/background_bullets"],
                stdout=pl.stdout, stderr=pl.stderr
            )

        generation_command = "arcadia/yweb/news/runtime_scripts/yappy/generate_reqs_for_service"
        if self.Parameters.custom_ammo_generation_command:
            generation_command = self.Parameters.custom_ammo_generation_command

        with ProcessLog(self, 'reqs_bash_magic.log') as pl:
            with sdk2.ssh.Key(self, "NEWS", "ssh_key"):
                assert os.environ["SSH_AUTH_SOCK"]
                assert os.environ["SSH_AGENT_PID"]

                sp.check_call([
                    generation_command,
                    self.Parameters.graph_source_names[0],
                ], stdout=pl.stdout, stderr=pl.stderr)

        ammo = resources.NEWS_APPHOST_SERVICE_REQUESTS(
            self,
            "Reqs for " + str(self.Parameters.service_name),
            self.Parameters.graph_source_names[0] + ".reqs",
        )
        ammo.service_name = self.Parameters.service_name

        fake_now = resources.NEWS_FAKE_NOW_FILE(
            self,
            "Fake now for " + str(self.Parameters.service_name),
            str(self.Parameters.service_name) + "_fake_now.txt",
        )
        fake_now.service_name = self.Parameters.service_name

        fake_now_data = sdk2.ResourceData(fake_now)
        fake_now_data.path.write_bytes(str(int(time.time())))

        sdk2.ResourceData(ammo).ready()
        fake_now_data.ready()

    def on_failure(self, prev_status):
        self.set_info("on_failure called")

    def on_break(self, prev_status, status):
        self.set_info("on_break called")
