# coding=utf-8
import sandbox.common.types.misc as ctm
import sandbox.common.types.task as ctt
from sandbox import sdk2
from sandbox.common.types.client import Tag
from sandbox.projects.metrika.mobile.sdk.generics.generic_tests_runner import GenericTestsRunner
from sandbox.projects.metrika.mobile.sdk.helpers.EmulatorHelper import EmulatorHelper
from sandbox.projects.metrika.mobile.sdk.helpers.ShellExecutor import ShellExecutor
from sandbox.projects.metrika.mobile.sdk.parameters.BuildAgentParameters import BuildAgentParameters
from sandbox.projects.metrika.mobile.sdk.parameters.GradleParameters import GradleParameters
from sandbox.projects.metrika.mobile.sdk.parameters.OptimizationParameters import OptimizationParameters
from sandbox.projects.metrika.mobile.sdk.parameters.SplitParameters import SplitParameters
from sandbox.projects.metrika.mobile.sdk.parameters.TestParameters import TestParameters
from sandbox.projects.metrika.mobile.sdk.parameters.VcsParameters import VcsParameters


class GenericTestsAndroidRunner(GenericTestsRunner):
    """
    Запускает тесты на одном API Level'е
    """

    class Utils(GenericTestsRunner.Utils):
        emulator_helper = EmulatorHelper()

    class Requirements(GenericTestsRunner.Requirements):
        client_tags = Tag.GENERIC
        disk_space = 32768
        ramdrive = ctm.RamDrive(ctm.RamDriveType.TMPFS, 2048, None)
        ram = 99328

        class Caches(sdk2.Requirements.Caches):
            pass

    class Parameters(GenericTestsRunner.Parameters):
        optimization_parameters = OptimizationParameters
        with sdk2.parameters.Group("Platform specific parameters") as platform_specific_parameters_group:
            container = sdk2.parameters.Container("Environment container resource", required=True)
            display_config = sdk2.parameters.Dict("Display configuration", description="Конфигурация экрана эмулятора")
            launch_xvfb = sdk2.parameters.Bool("Launch Xvfb", description="Запустить демон Xvfb", required=False,
                                               default=True)
            delegate_emulator_launch = sdk2.parameters.Bool("Delegate emulator launch to user application",
                                                            description="Запускать эмуляторы из своего приложения",
                                                            required=True, default=False)

    class Context(GenericTestsRunner.Context):
        pass

    def on_enqueue(self):
        super(GenericTestsAndroidRunner, self).on_enqueue()
        if self.Parameters.multislot_type is None or self.Parameters.multislot_type == '2':
            self.Requirements.cores = 2
            self.Requirements.ram = 7 * 1024
        elif self.Parameters.multislot_type == '8':
            self.Requirements.cores = 8
            self.Requirements.ram = 31 * 1024
        elif self.Parameters.multislot_type == '16':
            self.Requirements.cores = 16
            self.Requirements.ram = 63 * 1024
        if self.Parameters.use_tmpfs:
            self.Requirements.ramdrive = ctm.RamDrive(ctm.RamDriveType.TMPFS, 1024, None)
        if self.Parameters.use_ssd:
            self.Requirements.client_tags &= Tag.SSD

    @property
    def env(self):
        try:
            return self._env
        except AttributeError:
            self._env = self.Utils.shell_executor.default_env
            GradleParameters.prepare_env(self, self._env)
            if 'JAVA_HOME' not in self._env:
                self._env['JAVA_HOME'] = '/usr/local/java8'

            tmpdir = self.ramdrive.path if self.Parameters.use_tmpfs else None
            ShellExecutor.prepare_java_options(self._env, tmpdir)
        return self._env

    def _run(self):
        try:
            with sdk2.helpers.ProgressMeter("Prepare logs resource"):
                self._prepare_custom_logs_resource()
            with sdk2.helpers.ProgressMeter("Prepare additional info"):
                self._prepare_additional_info()
            with sdk2.helpers.ProgressMeter("Build"):
                self._build(self._get_gradle_properties())
            with sdk2.helpers.ProgressMeter("Prepare emulator"):
                self.Utils.emulator_helper.prepare_emulator(self)
            with self.Utils.emulator_helper.logcat(self), self.Utils.emulator_helper.xvfb(self):
                with sdk2.helpers.ProgressMeter("Launch emulator"):
                    if not self.Parameters.delegate_emulator_launch:
                        self.Utils.emulator_helper.boot_emulators(self)
                with sdk2.helpers.ProgressMeter("Run tests"):
                    self._run_tests(self._get_gradle_properties())
        except Exception:
            self.logger.error("Exception in scenario", exc_info=True)
            raise
        finally:
            with sdk2.helpers.ProgressMeter("Report test results"):
                try:
                    self._report_test_results(self._get_gradle_properties())
                except Exception:
                    self.logger.error("Exception in clean up. Continue.", exc_info=True)
            self._add_artifacts_to_custom_logs_resource()

    def _get_task_with_additional_params(self, caption, additional_params):
        params = {}
        params.update(OptimizationParameters.get(self))
        params.update(TestParameters.get(self))
        params.update(VcsParameters.get(self))
        params.update(GradleParameters.get(self))
        params.update(BuildAgentParameters.get(self))
        params.update(SplitParameters.get(self))
        params.update({
            GenericTestsAndroidRunner.Parameters.get_config_target.name: [],
            GenericTestsAndroidRunner.Parameters.report_target.name: [],
            GenericTestsAndroidRunner.Parameters.additional_params.name: additional_params,

            GenericTestsAndroidRunner.Parameters.delegate_emulator_launch.name: self.Parameters.delegate_emulator_launch,
            GenericTestsAndroidRunner.Parameters.display_config.name: self.Parameters.display_config,
            GenericTestsAndroidRunner.Parameters.container.name: self.Parameters.container,
            GenericTestsAndroidRunner.Parameters.launch_xvfb.name: self.Parameters.launch_xvfb,

            sdk2.Task.Parameters.kill_timeout.name: self.Parameters.kill_timeout,
            sdk2.Task.Parameters.tags.name: self.Parameters.tags,
        })
        return GenericTestsAndroidRunner(
            self,
            description="{} : {}".format(self.Parameters.description, caption),
            priority=min(
                self.Parameters.priority,
                ctt.Priority(ctt.Priority.Class.SERVICE, ctt.Priority.Subclass.NORMAL)  # default API limitation
            ),
            **params
        )

    def _get_gradle_properties(self):
        gradle_properties = super(GenericTestsAndroidRunner, self)._get_gradle_properties()
        gradle_properties.update({
            "build.api.level": self.Parameters.container.emulator_description,
        })

        return gradle_properties
