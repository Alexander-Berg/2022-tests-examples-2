# coding=utf-8
import sandbox.common.types.task as ctt
from sandbox import sdk2

from sandbox.projects.metrika.mobile.sdk.generics.generic_ios_resource_builder import GenericIosResourceBuilder
from sandbox.projects.metrika.mobile.sdk.generics.generic_tests_ios_runner import GenericTestsIosRunner
from sandbox.projects.metrika.mobile.sdk.generics.generic_tests_launcher import GenericTestsLauncher
from sandbox.projects.metrika.mobile.sdk.helpers.AdvancedIosSimulatorConfigHelper import \
    AdvancedIosSimulatorConfigHelper, DEFAULT_SIMULATORS_LIST
from sandbox.projects.metrika.mobile.sdk.parameters.GradleParameters import GradleParameters
from sandbox.projects.metrika.mobile.sdk.parameters.IosParameters import IosBuildParameters, IosLauncherParameters, \
    IosRunnerParameters
from sandbox.projects.metrika.mobile.sdk.parameters.SplitParameters import SplitParameters
from sandbox.projects.metrika.mobile.sdk.parameters.TestParameters import TestParameters
from sandbox.projects.metrika.mobile.sdk.parameters.VcsParameters import VcsParameters


class GenericTestsIosLauncher(GenericTestsLauncher):
    """
    Запускает тесты на выбранных версиях iOS
    """

    class Utils(GenericTestsLauncher.Utils):
        advanced_ios_simulator_config_helper = AdvancedIosSimulatorConfigHelper()

    class Requirements(GenericTestsLauncher.Requirements):
        pass

    class Parameters(GenericTestsLauncher.Parameters):
        ios_launcher_parameters = IosLauncherParameters
        with sdk2.parameters.Group("Platform specific parameters") as platform_specific_parameters_group:
            with sdk2.parameters.CheckGroup("iOS Versions", required=True) as ios_versions:
                for sim in DEFAULT_SIMULATORS_LIST:
                    ios_versions.values[sim['version']] = ios_versions.Value(sim['name'], checked=sim['checked'])
            advanced_devices_config = sdk2.parameters.List(
                "Advanced devices configuration",
                description="Список устройств вида "
                            "OS_<Version>_<DeviceModel>_<XCodePath> или OS_<Version>_<DeviceModel>."
                            "Примеры: {OS_12.1_iPhone X}, {OS_12.1_iPhone X_/Applications/Xcode11.3.app}. "
                            "Если это поле заполнено, поле iOS Versions игнорируется. "
                            "При передаче с Teamcity разделять элементы списка следует точкой с запятой (;).")

        use_ssh_key_for_build_task = sdk2.parameters.Bool("Use SSH-key for build task",
                                                          description="Использовать SSH-ключ при сборке",
                                                          default=False)

    class Context(GenericTestsLauncher.Context):
        pass

    def _get_build_task(self):
        params = {}
        params.update(VcsParameters.get(self))
        params.update(GradleParameters.get(self))
        params.update(IosBuildParameters.get_from_launcher(self))
        params.update({
            GenericIosResourceBuilder.Parameters.build_target.name: self.Parameters.build_target,

            GenericIosResourceBuilder.Parameters.resource_path.name: self.Parameters.resource_path,
            GenericIosResourceBuilder.Parameters.use_ssh_key_for_build_task.name: self.Parameters.use_ssh_key_for_build_task,

            sdk2.Task.Parameters.kill_timeout.name: self.Parameters.time_to_kill,
            sdk2.Task.Parameters.tags.name: self.Parameters.tags,
        })
        return GenericIosResourceBuilder(
            self,
            description="Build tests resource using OSX client",
            priority=min(
                self.Parameters.priority,
                ctt.Priority(ctt.Priority.Class.SERVICE, ctt.Priority.Subclass.NORMAL)  # default API limitation
            ),
            **params
        )

    def _get_task(self, simulator_config):
        test_resource = self.Parameters.tests_resource
        if self.Context.build_task_id:
            test_resource = test_resource or sdk2.Task[self.Context.build_task_id].Parameters.output_resource
        params = {}
        params.update(TestParameters.get(self))
        params.update(VcsParameters.get(self))
        params.update(GradleParameters.get(self))
        params.update(SplitParameters.get(self))
        params.update(IosRunnerParameters.get_from_launcher(self, simulator_config))
        params.update({
            GenericTestsIosRunner.Parameters.tests_resource.name: test_resource,
            GenericTestsIosRunner.Parameters.resource_path.name: self.Parameters.resource_path,

            sdk2.Task.Parameters.kill_timeout.name: self.Parameters.time_to_kill,
            sdk2.Task.Parameters.tags.name: self.Parameters.tags,
        })
        return GenericTestsIosRunner(
            self,
            description="Run tests on {} with iOS version {}".format(simulator_config['device_model'],
                                                                     simulator_config['ios_version']),
            priority=min(
                self.Parameters.priority,
                ctt.Priority(ctt.Priority.Class.SERVICE, ctt.Priority.Subclass.NORMAL)  # default API limitation
            ),
            **params
        )

    def _get_tasks(self):
        advanced_devices_config = self.Parameters.advanced_devices_config
        if len(advanced_devices_config) == 1:  # workaround passing parameters from TC bug
            advanced_devices_config = advanced_devices_config[0].split(';')

        advanced_devices_config = [adc.strip() for adc in advanced_devices_config]

        if len(advanced_devices_config) > 0:
            return {
                adc: self._get_task(
                    self.Utils.advanced_ios_simulator_config_helper.get_simulator_config(adc)
                ) for adc in advanced_devices_config
            }
        else:
            # temporarily (https://st.yandex-team.ru/FRANKENSTEIN-1001)
            print("ios_versions: {}".format(self.Parameters.ios_versions))
            return {
                "iOS version: {}".format(ios_version): self._get_task(
                    self.Utils.advanced_ios_simulator_config_helper.get_simulator_config_by_ios_version(ios_version)
                ) for ios_version in self.Parameters.ios_versions if
                any([it["version"] == ios_version for it in DEFAULT_SIMULATORS_LIST])
            }
