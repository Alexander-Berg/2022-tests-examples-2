import os
from time import sleep
import json
import logging

from sandbox import sdk2
from sandbox.sdk2.helpers import subprocess as sp
from sandbox.common.types.misc import DnsType
import sandbox.common.types.client as ctc
import sandbox.common.types.resource as ctr

from sandbox.projects.antiadblock.qa.resource_types import AntiadblockCryproxPackage
from sandbox.projects.antiadblock.qa.utils.constants import SHOOT_CONTAINER_ID, NGINX_BINARY_RESOURCE_ID, CRYPROX_TVM2_SECRET, ANTIADBLOCK_COOKIEMATCHER_CRYPT_KEYS

from sandbox.projects.antiadblock.utils import ROBOT_ANTIADB_TOKENS_YAV_ID

logger = logging.getLogger("run_task_log")


class AntiadblockServerTest(sdk2.Task):
    name = 'ANTIADBLOCK_SERVER_TEST'

    class Requirements(sdk2.Task.Requirements):
        privileged = True  # for root
        cores = 16
        disk_space = 40 * 1024  # 40 GB
        ram = 16 * 1024  # 16 GB
        client_tags = ctc.Tag.LINUX_XENIAL
        dns = DnsType.DNS64  # for external interactions

    class Parameters(sdk2.Task.Parameters):
        _container = sdk2.parameters.Container(
            'LXC container for ANTIADBLOCK shoot tests',
            default_value=SHOOT_CONTAINER_ID,
            platform='linux_ubuntu_16.04_xenial',
            required=True,
        )
        description = "Antiadblock server test task"

    def prepare_cryprox_package(self):
        logger.info("Prepare cryprox package")
        cryprox_package = AntiadblockCryproxPackage.find(
            state=ctr.State.READY
        ).limit(1).first()

        resource_data = sdk2.ResourceData(cryprox_package)  # synchronizing resource data on disk
        # extract tar archive
        cryprox_package_path = str(resource_data.path)
        with sdk2.helpers.ProcessLog(self, logger="run_task_log") as log:
            cmd = ['tar', '-xvzf', cryprox_package_path]
            sp.check_call(cmd, stdout=log.stdout, stderr=log.stderr)

    def prepare_nginx_binary(self):
        logger.info("Get NGINX binary")
        nginx_resorse = sdk2.Resource.find(id=NGINX_BINARY_RESOURCE_ID).limit(1).first()
        nginx_resource_data = sdk2.ResourceData(nginx_resorse)
        self.nginx_path = str(nginx_resource_data.path)

    def check(self):
        with sdk2.helpers.ProcessLog(self, logger="run_task_log") as log:
            cmd = ['ps', 'ax']
            sp.check_call(cmd, stdout=log.stdout, stderr=log.stderr)
            cmd = ['ls', '-lah', '/perm']
            sp.check_call(cmd, stdout=log.stdout, stderr=log.stderr)
            cmd = ['ls', '-lah', '/tmp_uids']
            sp.check_call(cmd, stdout=log.stdout, stderr=log.stderr)

            with open('/perm/cached_configs.json') as fin:
                configs = json.load(fin)
            services = " ".join(sorted({service.split("::")[0] for service in configs.keys()}))
            log.logger.info("services: {}".format(services))

            cmd = ['curl', '-v', 'http://localhost:8081/']
            sp.check_call(cmd, stdout=log.stdout, stderr=log.stderr)
            cmd = ['curl', '-v', 'http://localhost:8080/ping']
            sp.check_call(cmd, stdout=log.stdout, stderr=log.stderr)

    def make_cryprox_env(self):
        env = os.environ.copy()
        env["ENV_TYPE"] = "load_testing"
        env["LOGGING_LEVEL"] = "DEBUG"
        env["REQUEST_TIMEOUT"] = "60"
        env["CONFIGSAPI_URL"] = "https://api.aabadmin.yandex.ru/v2/configs_hierarchical_handler"
        env["CRYPROX_TVM2_CLIENT_ID"] = "2001021"
        env["CRYPROX_TVM2_SECRET"] = sdk2.yav.Secret(ROBOT_ANTIADB_TOKENS_YAV_ID).data()[CRYPROX_TVM2_SECRET]
        env["ADMIN_TVM2_CLIENT_ID"] = "2000629"
        env["REDIS_HOSTS"] = ""
        env["WORKERS_COUNT"] = "14"
        return env

    def make_nginx_env(self):
        env = os.environ.copy()
        env["WORKERS_COUNT"] = "2"
        env["JSTRACER_URL"] = "https://an.yandex.ru/jstracer"
        env["CRYPROX"] = "[::1]:8081"
        env["ACCELREDIRECT_TARGET"] = "proxy_pass $1$is_args$args;"
        env["EXTERNAL_RESOLVER"] = "[2a02:6b8:0:3400::5005]"
        env["UNICERT_SSL"] = ""
        return env

    def on_execute(self):
        self.prepare_cryprox_package()
        self.prepare_nginx_binary()

        with sdk2.helpers.ProcessLog(self, logger="run_task_log") as log:
            prepare_script_path = os.path.join(os.getcwd(), "usr/bin/init_instance_for_sandbox.sh")
            log.logger.info("Run init_instance_for_sandbox.sh")
            cmd = [prepare_script_path]
            sp.check_call(cmd, stdout=log.stdout, stderr=log.stderr, env=self.make_cryprox_env())

            prepare_script_path = os.path.join(os.getcwd(), "usr/bin/make_nginx_conf.sh")
            log.logger.info("Run make_nginx_conf.sh")
            cmd = [prepare_script_path]
            sp.check_call(cmd, stdout=log.stdout, stderr=log.stderr, env=self.make_nginx_env())

            cookiematcher_crypt_keys = sdk2.yav.Secret(ROBOT_ANTIADB_TOKENS_YAV_ID).data()[ANTIADBLOCK_COOKIEMATCHER_CRYPT_KEYS]
            with open("/etc/cookiematcher/cookiematcher_crypt_keys.txt", mode="w") as fout:
                fout.write(cookiematcher_crypt_keys)

            log.logger.info("Run nginx")

            cmd = [self.nginx_path]
            sp.check_call(cmd, stdout=log.stdout, stderr=log.stderr, env=os.environ.copy())

        sleep(300)
        self.check()
