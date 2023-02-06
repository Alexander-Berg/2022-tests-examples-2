# -*- coding: utf-8 -*-

from __future__ import absolute_import, print_function, unicode_literals

import logging
import os
import shutil

import sandbox.common.types.misc as ctm
import sandbox.common.types.resource as ct_resource
import sandbox.projects.common.nanny.nanny as nanny
from sandbox import sdk2
from sandbox.common.errors import TaskFailure
from sandbox.projects.common.vcs.arc import Arc
from sandbox.projects.di.common.tasks import TemplateMixin
from sandbox.projects.di.common.utils import GpgKey3
from sandbox.projects.di.resources import (DiSandboxSoxTool,
                                           PydiFrontendResource)
from sandbox.projects.di.settings import SANDBOX_VAULT
from sandbox.sandboxsdk import ssh
from sandbox.sdk2 import yav
from sandbox.sdk2.helpers.process import ProcessLog, subprocess

# Непротухающий (ttl=inf) контейнер с окружением для сборки фронта.
IMMORTAL_CONTAINER_ID = 658230636


class BuildPydiFrontendPnpmTest(TemplateMixin, nanny.ReleaseToNannyTask2, sdk2.Task):
    """Собирает фронтенд Интерфейса Дистрибуции (нода + статика) и в случае необходимости деплоит статику."""

    class Requirements(sdk2.Requirements):
        # для доступа к нпм (нпм летом 2018 все еще не умеет в ipv6)
        dns = ctm.DnsType.DNS64
        # Запускаемся рутом
        privileged = True

    class Parameters(sdk2.Parameters):

        with sdk2.parameters.Group("[SOX]") as sox:
            with sdk2.parameters.RadioGroup(
                    "SOX-compliant release (saves checksums for production code verification)"
            ) as do_sox:
                do_sox.values["do_sox"] = do_sox.Value(value="Yes", default=True)
                do_sox.values["nope"] = do_sox.Value(value="No")

            with do_sox.value["do_sox"]:
                version = sdk2.parameters.String("Build version")
                yndx_vault_secret_name = sdk2.parameters.String(
                    "Name of Yandex Vault secret for checksums",
                    default="sec-01d16bhmz9xpe88pjb4yw492x9",
                )
                yndx_vault_releases_timeline_secret_name = sdk2.parameters.String(
                    "Name of Yandex Vault secret for releases",
                    default="sec-01d16bg03kknntkqq7bd3s2jyz",
                )
                sox_tool_binary = sdk2.parameters.Resource(
                    "Sox tool binary",
                    required=True,
                    resource_type=DiSandboxSoxTool,
                    state=(ct_resource.State.READY,),
                    default_value=1356056110,
                )

            with do_sox.value["nope"]:
                pass

        with sdk2.parameters.Group("Base build parameters") as bbp:
            branch = sdk2.parameters.String(
                "Check project out from branch",
                default="trunk",
                required=True,
            )
            node_version = sdk2.parameters.String(
                "NodeJS version to install",
                default="12.22.12",
                required=True,
            )
            build_deb = sdk2.parameters.Bool(
                "Build deb with static (works only with trunk)",
                default=True,
                required=True,
            )

        with sdk2.parameters.Group("Nanny") as base:
            startrek_ticket_ids = nanny.StartrekTicketIdsParameter2(
                "Tracker Tickers IDs",
                description="Список тикетов в StartTrek в которые Няня оставит комментарии о состоянии релиза",
                required=True,
            )

        container = sdk2.parameters.Container(
            "Container",
            description="LXC Container with docker installed",
            default_value=IMMORTAL_CONTAINER_ID,
            required=True,
        )

    @property
    def project_path(self):
        return str(self.path("frontend"))

    def create_resource(self):
        sdk2.ResourceData(PydiFrontendResource(
            self,
            "DI Front from {}".format(self.Parameters.branch),
            "front.tar.gz"
        )).ready()

    def preinstall(self):
        """Ставится прибитая гвоздями версия ноды."""

        with ProcessLog(logger=logging.getLogger("receive keys")) as pl:
            subprocess.Popen(
                ["apt-key", "adv", "--keyserver", "keyserver.ubuntu.com", "--recv-keys", "7FCD11186050CD1A"],
                stdout=pl.stdout,
                stderr=pl.stderr,
            ).wait()

        with ProcessLog(logger=logging.getLogger("apt update")) as pl:
            subprocess.Popen(["apt-get", "update"], stdout=pl.stdout, stderr=pl.stderr).wait()
            subprocess.Popen(["apt-get", "install", "-y", "--force-yes", "wget"], stdout=pl.stdout, stderr=pl.stderr).wait()
            subprocess.Popen(["apt-get", "install", "-y", "yandex-arc-launcher"], stdout=pl.stdout, stderr=pl.stderr).wait()

        with ProcessLog(logger=logging.getLogger("make_node_from_scratch")) as pl:
            node = "node-v{}-linux-x64".format(self.Parameters.node_version)
            vnode = "v{}".format(self.Parameters.node_version)
            node_arch = "{}.tar.gz".format(node)
            params = dict(stdout=pl.stdout, stderr=pl.stderr)
            subprocess.Popen([
                "wget", "https://nodejs.org/download/release/{}/{}".format(vnode, node_arch)], **params
            ).wait()
            subprocess.Popen(["tar", "-xf", node_arch], **params).wait()
            node_path = str(self.path(node, "bin", "node"))
            npm_path = str(self.path(node, "bin", "npm"))
            for package, path in [("node", node_path), ("npm", npm_path)]:
                subprocess.Popen(["ln", "-s", path, "/bin/{}".format(package)], **params).wait()
                subprocess.Popen(["ln", "-s", path, "/usr/bin/{}".format(package)], **params).wait()

        with ProcessLog(logger=logging.getLogger("apt update")) as pl:
            subprocess.Popen(["apt-get", "update"], stdout=pl.stdout, stderr=pl.stderr).wait()
            subprocess.Popen(["apt-get", "install", "-y", "--force-yes", "wget"], stdout=pl.stdout, stderr=pl.stderr).wait()

        with ProcessLog(logger=logging.getLogger("install pnpm")) as pl:
                    subprocess.Popen(["npm", "install", "-g", "pnpm@7", "--prefix", "/usr/"], stdout=pl.stdout, stderr=pl.stderr).wait()

    def install(self):
        """Маркирует сборку для SOX-валидаций."""
        secret = yav.Secret(SANDBOX_VAULT).data()
        ssh_key_name = "{}[SSH_KEY]".format(SANDBOX_VAULT)
        secret_key_name = "{}[GPG_PRIVATE]".format(SANDBOX_VAULT)
        public_key_name = "{}[GPG_PUBLIC]".format(SANDBOX_VAULT)

        with ssh.Key(self, None, ssh_key_name):
            with ProcessLog(logger=logging.getLogger("clone_repo")) as pl:
                params = dict(stdout=pl.stdout, stderr=pl.stderr)
                subprocess.Popen(["ln", "-s", "./arcadia/distribution_interface/frontend", "./yharnam"], **params).wait()
                self.prepare_sox_resource(
                    resource_root_for_sox=str(self.path("yharnam", "server")),
                    file_inclusion_callable="only_js"
                )
                ticket = ""
                if isinstance(self.Parameters.startrek_ticket_ids, list):
                    ticket = self.Parameters.startrek_ticket_ids[0]
                elif isinstance(self.Parameters.startrek_ticket_ids, str):
                    ticket = list(self.Parameters.startrek_ticket_ids.split(","))[0]
                with GpgKey3(None, secret_key_name, public_key_name):
                    with ProcessLog(logger=logging.getLogger("build")) as pl:
                        retcode = subprocess.Popen([
                            "make", "-f", "yharnam/Makefile.build",
                            (
                                (
                                    "build-prod-from-release"
                                    if "releases/distribution_interface_frontend/" in self.Parameters.branch else
                                    "build-prod"
                                )
                                if self.Parameters.build_deb else
                                "build-testing"
                            ),
                            "CONDUCTOR_TOKEN={}".format(secret["CONDUCTOR_TOKEN"]),
                            "ARCADIA_TOKEN={}".format(secret["ARCADIA_TOKEN"]),
                            "BUILD_FROM_BRANCH={}".format(self.Parameters.branch),
                            "STARTREK_TICKET={}".format(ticket)
                        ], stderr=pl.stderr, stdout=pl.stdout).wait()
                        if retcode:
                            raise TaskFailure(
                                "GNU Make exited with code {}. See task logs for details".format(retcode)
                            )

    def make_arguments_for_prepare_sox_resource(self, resource_root_for_sox, file_inclusion_callable):
        secret = yav.Secret(SANDBOX_VAULT).data()
        params = dict(
            file_inclusion_callable=file_inclusion_callable,
            resource_root=resource_root_for_sox,
            is_binary=0,
            version=self.Parameters.version,
            number_of_entries_to_keep=10,
            vault_secret_key=self.Parameters.yndx_vault_secret_name,
            releases_timeline_key=self.Parameters.yndx_vault_releases_timeline_secret_name,
            is_production=1,
            vault_token=secret["VAULT_TOKEN"],
        )
        return ["--{}={}".format(k, v) for k, v in params.items()]

    def prepare_sox_resource(self, resource_root_for_sox, file_inclusion_callable):
        if not self.Parameters.version:
            return

        original_sox_tool_binary = str(sdk2.ResourceData(self.Parameters.sox_tool_binary).path)
        sox_tool_binary = str(self.path("sox_binary"))
        shutil.copy(os.path.join(original_sox_tool_binary, "pydi_sox_sandbox_tool"), sox_tool_binary)
        os.chmod(sox_tool_binary, 0o777)

        with ProcessLog(logger=logging.getLogger("lets_do_it_sox_way")) as pl:
            retcode = subprocess.Popen(
                [sox_tool_binary] +
                self.make_arguments_for_prepare_sox_resource(resource_root_for_sox, file_inclusion_callable),
                stdout=pl.stdout,
                stderr=pl.stderr
            ).wait()

        if retcode != 0:
            raise TaskFailure("Sox tools binary returned non-zero code: {}".format(retcode))

    def on_execute(self):
        self.preinstall()
        secret = yav.Secret(SANDBOX_VAULT).data()
        arc = Arc(arc_oauth_token=secret["ARCADIA_TOKEN"])
        with arc.mount_path("", self.Parameters.branch, fetch_all=False, mount_point="./arcadia") as mp:
            print(mp)
            self.install()
            self.create_resource()

    def on_release(self, additional_parameters):
        if additional_parameters["release_status"] == "stable" and not self.Parameters.build_deb:
            raise TaskFailure("This is test build, it cannot be released in production")
        super(BuildPydiFrontendNew, self).on_release(additional_parameters)
