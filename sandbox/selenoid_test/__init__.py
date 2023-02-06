# -*- coding: utf-8 -*-
import math
import time
import logging
import psutil


try:
    from multiprocessing import cpu_count
except ImportError:
    from os import cpu_count

from sandbox.common.errors import TaskFailure
from sandbox.common.utils import singleton_property
from sandbox.projects.common import binary_task
from sandbox.projects.common.yasm import push_api as yasm

import sandbox.sdk2 as sdk2
import sandbox.common.types.misc as ctm
import sandbox.common.types.resource as ctr
import sandbox.projects.common.network as network
import sandbox.projects.sandbox.resources as sb_resources
from sandbox.projects.surfwax.task_manager import get_task_manager


from sandbox.projects.surfwax.common.utils import has_mac_os_bro, shutdown_process
from sandbox.projects.surfwax.resource_types import SurfwaxLayersCache

# 5 minutes is first timeout checkpoint.
SAFE_EXECUTION_TIMEOUT_MARGIN_SEC = 6 * 60

# 1 minute less than gap between agent and task lifetime to allow for all other bookkeeping
SURFWAX_SESSION_SHUTDOWN_TIMEOUT_SEC = SURFWAX_GRACEFUL_SHUTDOWN_TIMEOUT_SEC = SAFE_EXECUTION_TIMEOUT_MARGIN_SEC - 1 * 60

SELENOID_GRACEFUL_SHUTDOWN_TIMEOUT_SEC = 15

PODMAN_SERVICE_SHUTDOWN_TIMEOUT_SEC = 5

PODMAN_POLL_TIMEOUT_SEC = 5
PODMAN_POLL_INTERVAL_SEC = 0.1
PODMAN_POLL_RETRY_COUNT = PODMAN_POLL_TIMEOUT_SEC / PODMAN_POLL_INTERVAL_SEC

PRODUCTION_TAG = "PRODUCTION"

SOURCE_NVM = "source /home/sandbox/.nvm/nvm.sh"
NVM_EXEC = "/home/sandbox/.nvm/nvm-exec"
MAC_OS_BROWSERS = ['safari']

NODE_VERSION = "12.13.0"

INFINITY = float("inf")

MAC_OS_SANDBOX_TAG = "CUSTOM_IOSTEST"
DEFAULT_TASK_CONTAINER_RES_ID = "2312227314"


class SurfwaxSelenoidTest(binary_task.LastBinaryTaskRelease, sdk2.Task):
    """
    Runs selenoid task
    """

    class Requirements(sdk2.Requirements):
        dns = ctm.DnsType.DNS64

    class Parameters(sdk2.Task.Parameters):
        container = sdk2.parameters.Container(
            "Environment container resource",
            default_value=None,
            resource_type=sb_resources.LXC_CONTAINER,
            platform="linux_ubuntu_18.04_bionic",
            required=False,
        )
        binary_task_params = binary_task.binary_release_parameters(stable=True)

        with sdk2.parameters.Group('Project build') as project_build_block:
            build_id = sdk2.parameters.Integer(
                'Build ID',
                hint=True,
                default=0,
            )

        with sdk2.parameters.Group('Selenoid') as project_build_block:
            browsers = sdk2.parameters.String('Browsers json', default='', multiline=True)
            selenoid_sessions_per_agent_limit = sdk2.parameters.Integer("Selenoid sessions per agent limit")
            selenoid_cpu_cores_per_session = sdk2.parameters.Float("CPU cores usage per selenoid session")
            selenoid_ramdrive_gb_per_session = sdk2.parameters.Float("RamDrive Gb usage per selenoid session")
            selenoid_ram_gb_per_session = sdk2.parameters.Float("Ram Gb usage per selenoid session")
            selenoid_proxy_timeout = sdk2.parameters.String("Timeout on proxy requests from sw-agent to selenoid", default='241')
            session_attempt_timeout = sdk2.parameters.String("Selenoid session attempt timeout", default='120s')
            service_startup_timeout = sdk2.parameters.String("Selenoid service startup timeout", default='120s')
            # TODO remove ggr_host, because parameter is unnecessary for surfwax
            ggr_host = sdk2.parameters.String('GGR host value', default='')
            selenoid_port = sdk2.parameters.String('Selenoid port', default='10444')

        with sdk2.parameters.Group("SurfWax") as sw:
            # Default is current "stable" version
            # TODO implement genisys override?
            surfwax_agent_version = sdk2.parameters.String("SurfWax agent version", default="0.7.0")
            surfwax_browser_runner_version = sdk2.parameters.String("SurfWax browser runner version", default="0.2.1")
            appium_version = sdk2.parameters.String("Appium runner version", default="1.21.0")
            surfwax_agent_run_method = sdk2.parameters.RadioGroup('Run SurfWax agent as', choices=(
                ('npm package', 'npm'),
                ('OCI container', 'oci'),
            ), default='oci')
            surfwax_browser_group = sdk2.parameters.String("SurfWax browser group", default="")
            surfwax_quota = sdk2.parameters.String("SurfWax quota identifier", default="")
            surfwax_quota_agent_secret = sdk2.parameters.YavSecret("SurfWax quota agent secret", default="")
            surfwax_coordinator_address_type = sdk2.parameters.RadioGroup('SurfWax coordinator address type', choices=(
                ('Endpoint', 'endpoint'),
                ('Service in deploy', 'deploy'),
            ), default='deploy')

            with surfwax_coordinator_address_type.value['endpoint']:
                surfwax_coordinator_endpoint = sdk2.parameters.String("SurfWax coordinator endpoint", default="")

            with surfwax_coordinator_address_type.value['deploy']:
                surfwax_coordinator_deploy_stage = sdk2.parameters.String("SurfWax coordinator stage in Deploy", default="surfwax-production")
                surfwax_coordinator_deploy_unit = sdk2.parameters.String("SurfWax coordinator deploy unit in Deploy", default="coordinator")
                surfwax_coordinator_deploy_dc = sdk2.parameters.List("SurfWax coordinator DC in Deploy", default=["sas", "vla", "myt"])

            surfwax_browsers_cache_resources = sdk2.parameters.Resource(
                "SurfWax browsers cache resources",
                resource_type=SurfwaxLayersCache,
                required=False,
                multiple=True,
                default=[],
            )

            surfwax_layers_cache_resources = sdk2.parameters.Resource(
                "SurfWax layers cache resources",
                resource_type=SurfwaxLayersCache,
                required=False,
                multiple=True,
                default=["2815306218"],
            )

        with sdk2.parameters.Group("System") as sys:
            ramdrive_size_gb = sdk2.parameters.Float("RAM drive size", default=0)

        with sdk2.parameters.Output(reset_on_restart=True):
            sessions_per_agent = sdk2.parameters.Integer(
                "Sessions per agent",
            )
            endpoint = sdk2.parameters.String(
                "Selenoid address",
            )
            # This parameter is used in Surfwax ordinator to distinguish pending tasks from active
            ready = sdk2.parameters.Bool(
                "Task is ready for WebDriver sessions",
            )

    @property
    def binary_executor_query(self):
        return {
            "owner": "SURFWAX_STAGING_BROWSERS",
            "attrs": {"project": "surfwax", "released": self.Parameters.binary_executor_release_type},
            "state": [ctr.State.READY],
        }

    def _is_production(self):
        return PRODUCTION_TAG in self.Parameters.tags

    @singleton_property
    def _sessions_per_agent(self):
        sessions_per_agent = self.Parameters.selenoid_sessions_per_agent_limit

        if self.Parameters.selenoid_cpu_cores_per_session > 0:
            sessions_per_agent = min(sessions_per_agent or INFINITY, cpu_count() / self.Parameters.selenoid_cpu_cores_per_session)

        if self.Parameters.ramdrive_size_gb > 0 and self.Parameters.selenoid_ramdrive_gb_per_session > 0:
            sessions_per_agent = min(sessions_per_agent or INFINITY, self.Parameters.ramdrive_size_gb / self.Parameters.selenoid_ramdrive_gb_per_session)

        if self.Parameters.selenoid_ram_gb_per_session > 0:
            free_ram_gb = (psutil.virtual_memory().total >> 30) - self.Parameters.ramdrive_size_gb
            sessions_per_agent = min(sessions_per_agent or INFINITY, free_ram_gb / self.Parameters.selenoid_ram_gb_per_session)

        return int(math.floor(sessions_per_agent))

    def on_enqueue(self):
        super(SurfwaxSelenoidTest, self).on_enqueue()

        # Ramdirve is for podman data, to speed up new HDD hosts
        if self.Parameters.ramdrive_size_gb > 0:
            self.Requirements.ramdrive = ctm.RamDrive(ctm.RamDriveType.TMPFS, self.Parameters.ramdrive_size_gb * 1024, None)

    def on_prepare(self):
        super(SurfwaxSelenoidTest, self).on_prepare()

        self.Parameters.sessions_per_agent = self._sessions_per_agent

    def on_save(self):
        if has_mac_os_bro(self.Parameters.browsers):
            self.Requirements.client_tags = MAC_OS_SANDBOX_TAG
            self.Requirements.cores = 1
            self.Parameters.ramdrive_size_gb = 0
            self.Parameters.kill_timeout = 3600
            self.Parameters.session_attempt_timeout = '240s'
            self.Parameters.service_startup_timeout = '240s'
            # self.Requirements.tasks_resource = sdk2.service_resources.SandboxTasksBinary.find(
            #     attrs={'binary_hash': '345cb421d3142fd262f48d9ffe8bbca1'}
            # ).first()
        else:
            super(SurfwaxSelenoidTest, self).on_save()

            self.Requirements.privileged = True
            if not self.Parameters.container:
                self.Parameters.container = DEFAULT_TASK_CONTAINER_RES_ID

    def on_execute(self):
        super(SurfwaxSelenoidTest, self).on_execute()

        # This import is messing with non-binary tasks

        self._set_execution_start_time()
        task_manager = get_task_manager(self.Parameters.browsers, self)
        logging.info('MANAGER@@@@')
        self.processes = task_manager.get_task_processes()

        addr = network.get_my_ipv6()
        self.set_info("IP: {}".format(addr))
        self.Parameters.endpoint = addr

        # There is a gap between setting this parameter and agent registration in coordinator
        # TODO Fix this gap or workaround it completely in ordinator
        self.Parameters.ready = True

        while all(map(lambda (process, _): process.poll() is None, self.processes)):
            time.sleep(5)

        errors = []
        for process, graceful_timeout in self.processes:
            if process.returncode == 0:
                logging.info("process {} exited with return code 0".format(process.pid))
            elif process.returncode is None:
                shutdown_process(process, graceful_timeout)
            else:
                errors.append("process {} exited with return code {}".format(process.pid, process.returncode))

        if len(errors) > 0:
            raise TaskFailure("Task failed with: {}".format("\n".join(errors)))

    def on_break(self, prev_status, status):
        super(SurfwaxSelenoidTest, self).on_break(prev_status, status)

        self._push_signals_to_yasm(status)

    def on_finish(self, prev_status, status):
        super(SurfwaxSelenoidTest, self).on_finish(prev_status, status)

        self._push_signals_to_yasm(status)

    def _push_signals_to_yasm(self, status):
        if getattr(self.Context, 'copy_of', False):
            return

        try:
            yasm.push_signals(
                signals={
                    'status_{}_mmmm'.format(status.lower()): 1,
                },
                tags={
                    'itype': 'surfwax_selenoid',
                    'prj': self.Parameters.surfwax_quota,
                    'ctype': 'prod' if self._is_production() else 'testing',
                },
            )
        except Exception as e:
            logging.exception('Exception while pushing signals to yasm: {}'.format(e))

    def on_terminate(self):
        logging.info("on_terminate called")
        if self.processes is None:
            logging.info("no processes to shutdown")
            return

        for process, graceful_timeout in self.processes:
            # Shutting down surfwax first because there can be active sessions
            # Then shutdown selenoid, and only then - podman service
            shutdown_process(process, graceful_timeout)

    def _set_execution_start_time(self):
        self.Context.execution_started_at = time.time()
