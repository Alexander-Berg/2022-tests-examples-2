# coding=utf-8
import sandbox.common.types.task as ctt
from sandbox import sdk2

from sandbox.projects.metrika.mobile.sdk.generics.generic_tests_android_launcher import GenericTestsAndroidLauncher
from sandbox.projects.metrika.mobile.sdk.parameters.BuildAgentParameters import BuildAgentParameters
from sandbox.projects.metrika.mobile.sdk.parameters.GradleParameters import GradleParameters
from sandbox.projects.metrika.mobile.sdk.parameters.VcsParameters import VcsParameters
from sandbox.projects.metrika.mobile.unity.autotests.unity_build_tests_agent import UnityBuildTestsAgent


class UnityTestsAndroidLauncher(GenericTestsAndroidLauncher):
    class Requirements(GenericTestsAndroidLauncher.Requirements):
        pass

    class Parameters(GenericTestsAndroidLauncher.Parameters):
        with sdk2.parameters.Group("Build parameters"):
            build_generate_project_task = sdk2.parameters.String("Generate project gradle task",
                                                                 description="Gradle task to generate project from Unity3D")
        with sdk2.parameters.Group("Build host parameters") as build_host_parameters:
            with sdk2.parameters.RadioGroup("Build host type") as build_host_type:
                build_host_type.values.linux = build_host_type.Value("Linux", default=True)
                build_host_type.values.mac = build_host_type.Value("MacOS")
            build_tags = sdk2.parameters.String("Build client tags")
            build_disk_space = sdk2.parameters.Integer("Build required disk space", default=None)
            with build_host_type.value.linux:
                build_cores = sdk2.parameters.Integer("Build required CPU cores", default=None)
                build_ram = sdk2.parameters.Integer("Build required RAM size", default=None)
                build_container_resource = sdk2.parameters.Integer("Build resource with LXC container", default=None)
        with sdk2.parameters.Group("Build Environment") as build_environment:
            build_rvm_plus_ruby_version = sdk2.parameters.String("Build Rvm+Ruby version",
                                                                 description="https://nda.ya.ru/t/kP42LAg15EHHBY")
            build_unity_version = sdk2.parameters.String("Build Unity version", required=True,
                                                         description="https://nda.ya.ru/t/U9Hjyy3V5EHHAj")
            with build_host_type.value.linux:
                build_android_sdk_version = sdk2.parameters.String("Build Android SDK version",
                                                                   description="https://nda.ya.ru/t/AuYmfTmo5EHHqc")
            with build_host_type.value.mac:
                build_xcode_version = sdk2.parameters.String("Build Xcode version",
                                                             description="https://nda.ya.ru/t/9_Kdb0_y3mKvk7")
                build_jdk_version = sdk2.parameters.String("Build JDK version",
                                                           description="https://nda.ya.ru/t/vzG7R0mi5EHHYg")

    class Context(GenericTestsAndroidLauncher.Context):
        pass

    def _get_build_task(self):
        params = {}
        params.update(VcsParameters.get(self))
        params.update(GradleParameters.get(self))
        params.update(BuildAgentParameters.get(self))
        params.update({
            UnityBuildTestsAgent.Parameters.build_task.name: self.Parameters.generic.build_target[0],
            UnityBuildTestsAgent.Parameters.generate_project_task.name: self.Parameters.build_generate_project_task,

            UnityBuildTestsAgent.Parameters.host_type.name: self.Parameters.build_host_type,
            UnityBuildTestsAgent.Parameters.client_tags.name: self.Parameters.build_tags,
            UnityBuildTestsAgent.Parameters.disk_space.name: self.Parameters.build_disk_space,
            UnityBuildTestsAgent.Parameters.cores.name: self.Parameters.build_cores,
            UnityBuildTestsAgent.Parameters.ram.name: self.Parameters.build_ram,
            UnityBuildTestsAgent.Parameters.container_resource.name: self.Parameters.build_container_resource,
            UnityBuildTestsAgent.Parameters.rvm_plus_ruby_version.name: self.Parameters.build_rvm_plus_ruby_version,
            UnityBuildTestsAgent.Parameters.unity_version.name: self.Parameters.build_unity_version,
            UnityBuildTestsAgent.Parameters.android_sdk_version.name: self.Parameters.build_android_sdk_version,
            UnityBuildTestsAgent.Parameters.xcode_version.name: self.Parameters.build_xcode_version,
            UnityBuildTestsAgent.Parameters.jdk_version.name: self.Parameters.build_jdk_version,

            UnityBuildTestsAgent.Parameters.time_to_kill.name: self.Parameters.time_to_kill,
        })
        return UnityBuildTestsAgent(
            self,
            description="Build tests resource",
            priority=min(
                self.Parameters.priority,
                ctt.Priority(ctt.Priority.Class.SERVICE, ctt.Priority.Subclass.NORMAL)  # default API limitation
            ),
            **params
        )
