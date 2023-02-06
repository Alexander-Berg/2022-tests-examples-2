# coding=utf-8
import sandbox.common.types.task as ctt
from sandbox import sdk2
from sandbox.projects.metrika.mobile.sdk.android_gradle_runner import AndroidGradleRunner
from sandbox.projects.metrika.mobile.sdk.generics.generic_tests_android_runner import GenericTestsAndroidRunner
from sandbox.projects.metrika.mobile.sdk.generics.generic_tests_launcher import GenericTestsLauncher
from sandbox.projects.metrika.mobile.sdk.parameters.VcsParameters import VcsParameters
from sandbox.projects.metrika.mobile.sdk.parameters.GradleParameters import GradleParameters
from sandbox.projects.metrika.mobile.sdk.parameters.OptimizationParameters import OptimizationParameters
from sandbox.projects.metrika.mobile.sdk.parameters.SplitParameters import SplitParameters
from sandbox.projects.metrika.mobile.sdk.parameters.TestParameters import TestParameters
from sandbox.projects.metrika.mobile.sdk.helpers.AndroidContainerFinder import AndroidContainerFinder
from sandbox.projects.metrika.mobile.sdk.helpers.AdvancedEmulatorConfigHelper import AdvancedEmulatorConfigHelper

API_LEVELS = [
    "17_google_apis",
    "19_google_apis",
    "22_google_apis",
    "22_default",
    "23_google_apis",
    "23_default",
    "24_google_apis",
    "24_default",
    "25_google_apis",
    "25_default",
    "26_google_apis",
    "26_default",
    "27_google_apis",
    "27_default",
    "28_google_apis",
    "28_default",
    "29_google_apis",
    "29_default",
    "30_google_apis",
    "31_google_apis",
    "32_google_apis",
    "33_google_apis",
]


class GenericTestsAndroidLauncher(GenericTestsLauncher):
    """
    Запускает тесты на выбранных API Level'ах
    """

    class Utils(GenericTestsLauncher.Utils):
        android_container_finder = AndroidContainerFinder()
        advanced_emulator_config_helper = AdvancedEmulatorConfigHelper()

    class Requirements(GenericTestsLauncher.Requirements):
        pass

    class Parameters(GenericTestsLauncher.Parameters):
        optimization_parameters = OptimizationParameters
        with sdk2.parameters.Group("Platform specific parameters") as platform_specific_parameters_group:
            with sdk2.parameters.CheckGroup("API Levels", required=True) as api_levels:
                for api_level in API_LEVELS:
                    api_levels.values[api_level] = api_levels.Value(api_level, checked=True)
            advanced_devices_config = sdk2.parameters.List(
                "Advanced devices configuration",
                description="Список устройств. Каждый элемент имеет вид "
                            "API<api_level>_<densityDpi>_<screenWpixels>x<screenHpixels> "
                            "или "
                            "API<api_level;platform;api;>_<densityDpi>_<screenWpixels>x<screenHpixels>, "
                            "где platform = x86_64|x86, api=default|google_api. "
                            "Например API25_240_480x800 или API25;x86;google_apis; или API25;x86;default;_240_480x800. "
                            "Если это поле заполнено, поле API Levels игнорируется.")
            launch_xvfb = sdk2.parameters.Bool("Launch Xvfb",
                                               description="Запустить демон Xvfb",
                                               required=False,
                                               default=True)
            delegate_emulator_launch = sdk2.parameters.Bool("Delegate emulator launch to user application",
                                                            description="Запускать эмуляторы из своего приложения",
                                                            required=True,
                                                            default=False)

    class Context(GenericTestsLauncher.Context):
        pass

    def _get_build_task(self):
        params = {}
        params.update(VcsParameters.get(self))
        params.update(GradleParameters.get(self))
        params.update({
            AndroidGradleRunner.Parameters.container.name:
                self.Utils.android_container_finder.get_build_container(self.Parameters.container_version),
            AndroidGradleRunner.Parameters.run_target.name: self.Parameters.build_target,

            AndroidGradleRunner.Parameters.output_resource_path.name: self.Parameters.resource_path,
            AndroidGradleRunner.Parameters.output_resource_ttl.name: 1,

            sdk2.Task.Parameters.kill_timeout.name: self.Parameters.time_to_kill,
            sdk2.Task.Parameters.tags.name: self.Parameters.tags,
        })
        return AndroidGradleRunner(
            self,
            description="Build tests resource using gradle for android",
            priority=min(
                self.Parameters.priority,
                ctt.Priority(ctt.Priority.Class.SERVICE, ctt.Priority.Subclass.NORMAL)  # default API limitation
            ),
            **params
        )

    def _get_task(self, emulator_config, display_config={}):
        test_resource = self.Parameters.tests_resource
        if self.Context.build_task_id:
            test_resource = test_resource or sdk2.Task[self.Context.build_task_id].Parameters.output_resource
        params = {}
        params.update(OptimizationParameters.get(self))
        params.update(TestParameters.get(self))
        params.update(VcsParameters.get(self))
        params.update(GradleParameters.get(self))
        params.update(SplitParameters.get(self))
        params.update({
            GenericTestsAndroidRunner.Parameters.delegate_emulator_launch.name: self.Parameters.delegate_emulator_launch,
            GenericTestsAndroidRunner.Parameters.display_config.name: display_config,
            GenericTestsAndroidRunner.Parameters.container.name:
                self.Utils.android_container_finder.get_container(self.Parameters.container_version, **emulator_config),
            GenericTestsAndroidRunner.Parameters.tests_resource.name: test_resource,
            GenericTestsAndroidRunner.Parameters.resource_path.name: self.Parameters.resource_path,
            GenericTestsAndroidRunner.Parameters.launch_xvfb.name: self.Parameters.launch_xvfb,

            sdk2.Task.Parameters.kill_timeout.name: self.Parameters.time_to_kill,
            sdk2.Task.Parameters.tags.name: self.Parameters.tags,
        })
        return GenericTestsAndroidRunner(
            self,
            description="Run tests on Android emulator {}: {}".format(emulator_config, display_config),
            priority=min(
                self.Parameters.priority,
                ctt.Priority(ctt.Priority.Class.SERVICE, ctt.Priority.Subclass.NORMAL)  # default API limitation
            ),
            **params
        )

    def _get_tasks(self):
        advanced_devices_config = [adc.strip() for adc in self.Parameters.advanced_devices_config]
        if len(advanced_devices_config) == 1:  # workaround passing parameters from TC bug
            advanced_devices_config = advanced_devices_config[0].split()

        if len(advanced_devices_config) > 0:
            return {adc: self._get_task(
                emulator_config=self.Utils.advanced_emulator_config_helper.get_emulator_config(adc),
                display_config=self.Utils.advanced_emulator_config_helper.get_display_config(adc)
            ) for adc in advanced_devices_config}
        else:
            return {"API Level: {}".format(api_level): self._get_task(
                emulator_config=self.Utils.advanced_emulator_config_helper.get_emulator_config_by_launcher_value(api_level)
            ) for api_level in self.Parameters.api_levels}

    def _get_report_task(self):
        task = super(GenericTestsAndroidLauncher, self)._get_report_task()
        task.Parameters.container = self.Utils.android_container_finder.get_build_container(
            self.Parameters.container_version
        )
        return task
