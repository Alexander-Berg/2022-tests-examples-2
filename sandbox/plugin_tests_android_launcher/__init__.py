# coding=utf-8
import sandbox.common.types.task as ctt
from sandbox import sdk2
from sandbox.projects.metrika.mobile.sdk.generics.generic_ios_resource_builder import GenericIosResourceBuilder
from sandbox.projects.metrika.mobile.sdk.generics.generic_tests_android_launcher import GenericTestsAndroidLauncher
from sandbox.projects.metrika.mobile.sdk.parameters.VcsParameters import VcsParameters
from sandbox.projects.metrika.mobile.sdk.parameters.GradleParameters import GradleParameters


class PluginTestsAndroidLauncher(GenericTestsAndroidLauncher):
    """
    Запускает тесты на выбранных API Level'ах
    """

    class Requirements(GenericTestsAndroidLauncher.Requirements):
        pass

    class Parameters(GenericTestsAndroidLauncher.Parameters):
        use_ssh_key_for_build_task = sdk2.parameters.Bool("Use SSH-key for build task",
                                                          description="Использовать SSH-ключ при сборке",
                                                          default=False)

    class Context(GenericTestsAndroidLauncher.Context):
        pass

    def _get_build_task(self):
        params = {
            GenericIosResourceBuilder.Parameters.build_target.name: self.Parameters.build_target,

            GenericIosResourceBuilder.Parameters.resource_path.name: self.Parameters.resource_path,
            GenericIosResourceBuilder.Parameters.use_ssh_key_for_build_task.name: self.Parameters.use_ssh_key_for_build_task,

            sdk2.Task.Parameters.kill_timeout.name: self.Parameters.time_to_kill,
            sdk2.Task.Parameters.tags.name: self.Parameters.tags,
        }
        params.update(VcsParameters.get(self))
        params.update(GradleParameters.get(self))
        return GenericIosResourceBuilder(
            self,
            description="Plugins tests for Android",
            priority=min(
                self.Parameters.priority,
                ctt.Priority(ctt.Priority.Class.SERVICE, ctt.Priority.Subclass.NORMAL)  # default API limitation
            ),
            **params
        )
