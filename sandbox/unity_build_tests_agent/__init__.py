# coding=utf-8
import logging

import sandbox.common.types.client as ctc
import sandbox.common.types.task as ctt
from sandbox import sdk2
from sandbox.common.errors import TaskFailure
from sandbox.common.types.misc import DnsType
from sandbox.common.utils import get_task_link
from sandbox.sandboxsdk.environments import Xcode

from sandbox.projects.metrika.mobile.sdk.helpers.GradleExecutor import GradleExecutor
from sandbox.projects.metrika.mobile.sdk.helpers.ShellExecutor import ShellExecutor
from sandbox.projects.metrika.mobile.sdk.helpers.TarResourceHelper import TarResourceHelper
from sandbox.projects.metrika.mobile.sdk.helpers.VcsHelper import VcsHelper
from sandbox.projects.metrika.mobile.sdk.parameters.BuildAgentParameters import BuildAgentParameters
from sandbox.projects.metrika.mobile.sdk.parameters.GradleParameters import GradleParameters
from sandbox.projects.metrika.mobile.sdk.parameters.VcsParameters import VcsParameters
from sandbox.projects.metrika.mobile.unity.unity_environment import UnityEnvironment
from sandbox.projects.mobile_apps.utils import shellexecuter
from sandbox.projects.mobile_apps.utils.android_sdk_env import AndroidSdkEnvironment
from sandbox.projects.mobile_apps.utils.jdk_env import JdkEnvironment
from sandbox.projects.mobile_apps.utils.provision_profiles_env import ProvisionProfileEnvironment
from sandbox.projects.mobile_apps.utils.rvm_plus_ruby_env import RvmPlusRubyEnvironment


class UnityBuildTestsAgent(sdk2.Task):
    class Requirements(sdk2.Requirements):
        dns = DnsType.DNS64

        class Caches(sdk2.Requirements.Caches):
            pass  # Do not use any shared caches (required for running on multislot agent)

    class Parameters(sdk2.Parameters):
        time_to_kill = sdk2.parameters.Integer("Time to kill", default=None)
        task_vcs_group = VcsParameters()
        task_gradle_group = GradleParameters()
        with sdk2.parameters.Group("Gradle task") as gradle_task_group:
            build_task = sdk2.parameters.String("Gradle task", required=True)
            generate_project_task = sdk2.parameters.String("Generate project gradle task",
                                                           description="Gradle task to generate project from Unity3D")
        task_build_agent_group = BuildAgentParameters()
        with sdk2.parameters.Group("Host parameters") as host_group:
            with sdk2.parameters.RadioGroup("Host type") as host_type:
                host_type.values.linux = host_type.Value("Linux", default=True)
                host_type.values.mac = host_type.Value("MacOS")
            client_tags = sdk2.parameters.String("Client tags")
            disk_space = sdk2.parameters.Integer("Required disk space", default=None)
            with host_type.value.linux:
                cores = sdk2.parameters.Integer("Required CPU cores", default=None)
                ram = sdk2.parameters.Integer("Required RAM size", default=None)
                container_resource = sdk2.parameters.Integer("Resource with LXC container", default=None)
        with sdk2.parameters.Group("Environment") as environment_group:
            rvm_plus_ruby_version = sdk2.parameters.String("Rvm+Ruby version",
                                                           description="https://nda.ya.ru/t/kP42LAg15EHHBY")
            unity_version = sdk2.parameters.String("Unity version", required=True,
                                                   description="https://nda.ya.ru/t/U9Hjyy3V5EHHAj")
            with host_type.value.linux:
                android_sdk_version = sdk2.parameters.String("Android SDK version",
                                                             description="https://nda.ya.ru/t/AuYmfTmo5EHHqc")
            with host_type.value.mac:
                xcode_version = sdk2.parameters.String("Xcode version",
                                                       description="https://nda.ya.ru/t/9_Kdb0_y3mKvk7")
                jdk_version = sdk2.parameters.String("JDK version",
                                                     description="https://nda.ya.ru/t/vzG7R0mi5EHHYg")
        with sdk2.parameters.Output:
            output_resource = sdk2.parameters.Resource("Resource", required=True,
                                                       description="Ресурс, содержащий указанную папку/файл")

    class Context(sdk2.Context):
        generate_project_task_id = None
        build_task_id = None

    class Utils:
        vcs_helper = VcsHelper()
        gradle_executor = GradleExecutor()
        shell_executor = ShellExecutor()
        tar_resource_helper = TarResourceHelper(shell_executor)

    def on_save(self):
        super(UnityBuildTestsAgent, self).on_save()
        if self.Parameters.generate_project_task:
            self.on_save_as_proxy()
        else:
            self.on_save_as_build()

    def on_save_as_proxy(self):
        # simple task for run other tasks
        self.Requirements.client_tags = ctc.Tag.GENERIC
        self.Requirements.cores = 1
        self.Requirements.ram = 1024
        self.Requirements.disk_space = 1024
        self.Parameters.kill_timeout = 10 * 60

    def on_save_as_build(self):
        # linux
        if self.Parameters.host_type == "linux":
            self.Requirements.client_tags = ctc.Tag.Group.LINUX & (ctc.Tag.INTEL_E5_2650 | ctc.Tag.INTEL_E5_2660)
            if self.Parameters.cores:
                self.Requirements.cores = self.Parameters.cores
            if self.Parameters.ram:
                self.Requirements.ram = self.Parameters.ram
            if self.Parameters.container_resource:
                self.Requirements.container_resource = self.Parameters.container_resource
        if self.Parameters.host_type == "mac":
            self.Requirements.client_tags = ctc.Tag.MOBILE_MONOREPO & ctc.Tag.USER_MONOREPO & ctc.Tag.OSX_BIG_SUR
        # common
        if self.Parameters.time_to_kill:
            self.Parameters.kill_timeout = self.Parameters.time_to_kill
        if self.Parameters.client_tags:
            self.Requirements.client_tags = self.Parameters.client_tags
        if self.Parameters.disk_space:
            self.Requirements.disk_space = self.Parameters.disk_space

    def on_prepare(self):
        super(UnityBuildTestsAgent, self).on_prepare()
        if not self.Parameters.generate_project_task:
            self.on_prepare_as_build()

    def on_prepare_as_build(self):
        platform = shellexecuter.detect_platform()
        if self.Parameters.host_type == "linux":
            if self.Parameters.android_sdk_version:
                with sdk2.helpers.ProgressMeter("Prepare Android SDK ({})".format(self.Parameters.android_sdk_version)):
                    AndroidSdkEnvironment(self.Parameters.android_sdk_version).prepare(None, None, None)
        if self.Parameters.host_type == "mac":
            if self.Parameters.xcode_version:
                with sdk2.helpers.ProgressMeter("Prepare Xcode v{}".format(self.Parameters.xcode_version)):
                    Xcode(self.Parameters.xcode_version).prepare()
            if self.Parameters.jdk_version:
                with sdk2.helpers.ProgressMeter("Prepare JDK v{}".format(self.Parameters.jdk_version)):
                    JdkEnvironment(self.Parameters.jdk_version).prepare()
            with sdk2.helpers.ProgressMeter("Prepare Provision Profile"):
                ProvisionProfileEnvironment().prepare()
        if self.Parameters.rvm_plus_ruby_version:
            with sdk2.helpers.ProgressMeter("Prepare Rvm+Ruby v{}".format(self.Parameters.rvm_plus_ruby_version)):
                RvmPlusRubyEnvironment(self.Parameters.rvm_plus_ruby_version, platform).prepare()
        if self.Parameters.unity_version:
            with sdk2.helpers.ProgressMeter("Prepare Unity v{}".format(self.Parameters.unity_version)):
                unity_platform = "darwin" if self.Parameters.host_type == "mac" else self.Parameters.host_type
                UnityEnvironment(self.Parameters.unity_version, unity_platform).prepare()
        with sdk2.helpers.ProgressMeter("Clone repo"):
            self._repo = self.Utils.vcs_helper.clone_with_task(self)

    def on_execute(self):
        super(UnityBuildTestsAgent, self).on_execute()
        if self.Parameters.generate_project_task:
            self.on_execute_as_proxy()
        else:
            self.on_execute_as_build()

    def on_execute_as_proxy(self):
        self._run_generate_project_task()
        self._run_build_task()
        if self.Context.build_task_id:
            self.Parameters.output_resource = sdk2.Task[self.Context.build_task_id].Parameters.output_resource

    def on_execute_as_build(self):
        with self._repo:
            try:
                if self.Parameters.task_build_agent_group.tests_resource:
                    with sdk2.helpers.ProgressMeter("Extract tests resource"):
                        self.Utils.tar_resource_helper.extract_input_resource(
                            resource=self.Parameters.task_build_agent_group.tests_resource,
                            path=self._work_dir(self.Parameters.task_build_agent_group.resource_path),
                            task=self
                        )
                with sdk2.helpers.ProgressMeter("Run gradle task"):
                    self.Utils.gradle_executor.execute_gradle_with_failure(
                        path=self._work_dir(self.Parameters.task_gradle_group.gradle_base_dir),
                        tasks=[self.Parameters.task_gradle_group.gradle_log_level, "--stacktrace",
                               self.Parameters.build_task],
                        gradle_properties=self._get_gradle_properties(),
                        system_properties=self._get_system_gradle_properties(),
                        build_file=self.Parameters.task_gradle_group.build_file,
                        environment=self._get_env(),
                    )
            finally:
                with sdk2.helpers.ProgressMeter("Save built resource"):
                    self._save_to_resource()

    # for proxy

    def _run_generate_project_task(self):
        with self.memoize_stage.generate_project_wait_task:
            params = {}
            params.update(VcsParameters.get(self))
            params.update(GradleParameters.get(self))
            params.update(BuildAgentParameters.get(self))
            params.update({
                UnityBuildTestsAgent.Parameters.build_task.name: self.Parameters.generate_project_task,

                UnityBuildTestsAgent.Parameters.host_type.name: "linux",
                UnityBuildTestsAgent.Parameters.disk_space.name: self.Parameters.disk_space,
                UnityBuildTestsAgent.Parameters.cores.name: 4,
                UnityBuildTestsAgent.Parameters.ram.name: 12 * 1024,
                UnityBuildTestsAgent.Parameters.container_resource.name: 3368153307,
                UnityBuildTestsAgent.Parameters.rvm_plus_ruby_version.name: self.Parameters.rvm_plus_ruby_version,
                UnityBuildTestsAgent.Parameters.unity_version.name: self.Parameters.unity_version,

                sdk2.Task.Parameters.kill_timeout.name: self.Parameters.time_to_kill,
            })
            child = UnityBuildTestsAgent(self, description="Generate native project from Unity3D project", **params)
            child.enqueue()
            self.Context.generate_project_task_id = child.id
            raise sdk2.WaitTask(child.id, ctt.Status.Group.FINISH | ctt.Status.Group.BREAK)
        with self.memoize_stage.generate_project_check_status:
            if sdk2.Task[self.Context.generate_project_task_id].status not in ctt.Status.Group.SUCCEED:
                raise TaskFailure("Failed to generate native project. See task <a href=\"{}\">{}</a>.".format(
                    get_task_link(self.Context.generate_project_task_id), self.Context.generate_project_task_id
                ))

    def _run_build_task(self):
        with self.memoize_stage.build_wait_task:
            params = {}
            params.update(VcsParameters.get(self))
            params.update(GradleParameters.get(self))
            params.update(BuildAgentParameters.get(self))
            params.update({
                UnityBuildTestsAgent.Parameters.build_task.name: self.Parameters.build_task,
                BuildAgentParameters.tests_resource.name:
                    sdk2.Task[self.Context.generate_project_task_id].Parameters.output_resource,

                UnityBuildTestsAgent.Parameters.host_type.name: self.Parameters.host_type,
                UnityBuildTestsAgent.Parameters.client_tags.name: self.Parameters.client_tags,
                UnityBuildTestsAgent.Parameters.disk_space.name: self.Parameters.disk_space,
                UnityBuildTestsAgent.Parameters.cores.name: self.Parameters.cores,
                UnityBuildTestsAgent.Parameters.ram.name: self.Parameters.ram,
                UnityBuildTestsAgent.Parameters.container_resource.name: self.Parameters.container_resource,
                UnityBuildTestsAgent.Parameters.rvm_plus_ruby_version.name: self.Parameters.rvm_plus_ruby_version,
                UnityBuildTestsAgent.Parameters.android_sdk_version.name: self.Parameters.android_sdk_version,
                UnityBuildTestsAgent.Parameters.xcode_version.name: self.Parameters.xcode_version,
                UnityBuildTestsAgent.Parameters.jdk_version.name: self.Parameters.jdk_version,

                sdk2.Task.Parameters.kill_timeout.name: self.Parameters.time_to_kill,
            })
            child = UnityBuildTestsAgent(self, description="Build native project", **params)
            child.enqueue()
            self.Context.build_task_id = child.id
            raise sdk2.WaitTask(child.id, ctt.Status.Group.FINISH | ctt.Status.Group.BREAK)
        with self.memoize_stage.build_check_status:
            if sdk2.Task[self.Context.build_task_id].status not in ctt.Status.Group.SUCCEED:
                raise TaskFailure("Failed to build native project. See task <a href=\"{}\">{}</a>.".format(
                    get_task_link(self.Context.build_task_id), self.Context.build_task_id
                ))

    # for build

    def _work_dir(self, *path):
        return str(self.path("wd", *path))

    def _get_gradle_properties(self):
        gradle_properties = {}
        gradle_properties.update(
            {k: v for k, v in self.Parameters.task_gradle_group.gradle_parameters.iteritems() if v})
        gradle_properties.update(
            {k: sdk2.Vault.data(*v.split(':', 1)) for k, v in
             self.Parameters.task_gradle_group.secret_gradle_parameters.iteritems() if v})
        return gradle_properties

    def _get_system_gradle_properties(self):
        gradle_properties = {}
        gradle_properties.update(
            {k: v for k, v in self.Parameters.task_gradle_group.system_gradle_parameters.iteritems() if v})
        return gradle_properties

    def _get_env(self):
        env = dict(_.split("=", 1) for _ in sdk2.helpers.subprocess.check_output(
            ["/bin/bash", "-c", ". /etc/profile && printenv"]).splitlines())
        if self.Parameters.host_type == "mac":
            # certs for macos clients from arcadia/sandbox/deploy/layout/sandbox_macos_mobile/usr/local/etc/openssl
            # ssl cert
            env["SSL_CERT_FILE"] = "/usr/local/etc/openssl/allCAs.pem"
            # cert for slack
            env["WEBSOCKET_CLIENT_CA_BUNDLE"] = "/usr/local/etc/openssl/DigiCertGlobalRootCA.crt"
            env["SSL_CERT_DIR"] = "/usr/local/etc/openssl"
        return env

    @property
    def logger(self):
        try:
            return self._logger
        except AttributeError:
            self._logger = logging.getLogger("scenario")
        return self._logger

    def _save_to_resource(self):
        output_resource_path = self.path(self._work_dir(self.Parameters.task_build_agent_group.resource_path))
        self.Parameters.output_resource = self.Utils.tar_resource_helper.save_to_resource(
            task=self,
            description="Build Resource",
            current_dir=output_resource_path.parent,
            resource_dir_name=output_resource_path.name,
            ttl=1,
            task_dir=self.path(),
            backup=True
        )
