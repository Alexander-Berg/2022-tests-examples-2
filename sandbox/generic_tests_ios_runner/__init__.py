# coding=utf-8
import sandbox.common.types.task as ctt

from sandbox import sdk2
from sandbox.projects.metrika.mobile.sdk.generics.generic_tests_runner import GenericTestsRunner
from sandbox.projects.metrika.mobile.sdk.helpers.IosHelper import IosHelper
from sandbox.projects.metrika.mobile.sdk.parameters.BuildAgentParameters import BuildAgentParameters
from sandbox.projects.metrika.mobile.sdk.parameters.GradleParameters import GradleParameters
from sandbox.projects.metrika.mobile.sdk.parameters.IosParameters import IosRunnerParameters
from sandbox.projects.metrika.mobile.sdk.parameters.SplitParameters import SplitParameters
from sandbox.projects.metrika.mobile.sdk.parameters.TestParameters import TestParameters
from sandbox.projects.metrika.mobile.sdk.parameters.VcsParameters import VcsParameters


class GenericTestsIosRunner(GenericTestsRunner):
    """
    Запускает тесты на одной версии iOS
    """

    class Utils(GenericTestsRunner.Utils):
        ios_helper = IosHelper()

    class Requirements(GenericTestsRunner.Requirements):
        disk_space = 50 * 1024

    class Parameters(GenericTestsRunner.Parameters):
        ios_param = IosRunnerParameters

    class Context(GenericTestsRunner.Context):
        pass

    def on_save(self):
        super(GenericTestsIosRunner, self).on_save()
        self.Utils.ios_helper.on_save(self)

    def on_prepare(self):
        super(GenericTestsIosRunner, self).on_prepare()
        self.Utils.ios_helper.on_prepare(self)

    def _run(self):
        with self.repo:
            try:
                with sdk2.helpers.ProgressMeter("Build"):
                    self._build(self._get_gradle_properties())
                with sdk2.helpers.ProgressMeter("Prepare additional info"):
                    self._prepare_additional_info()
                with sdk2.helpers.ProgressMeter("Run tests"):
                    self._prepare_custom_logs_resource(backup=True)
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

    def _get_gradle_properties(self):
        gradle_properties = super(GenericTestsIosRunner, self)._get_gradle_properties()
        gradle_properties.update({
            "build.api.level": self.Parameters.device_os,
            "xcodeTestDevice": self.Parameters.device_model,
            "xcodeTestOS": self.Parameters.device_os,
            "xcodePath": self.Utils.ios_helper.get_xcode_path(self),
        })

        return gradle_properties

    def _get_task_with_additional_params(self, caption, additional_params):
        params = {}
        params.update(TestParameters.get(self))
        params.update(VcsParameters.get(self))
        params.update(GradleParameters.get(self))
        params.update(BuildAgentParameters.get(self))
        params.update(SplitParameters.get(self))
        params.update(IosRunnerParameters.get(self))
        params.update({
            GenericTestsIosRunner.Parameters.get_config_target.name: [],
            GenericTestsIosRunner.Parameters.report_target.name: [],
            GenericTestsIosRunner.Parameters.additional_params.name: additional_params,

            sdk2.Task.Parameters.kill_timeout.name: self.Parameters.kill_timeout,
            sdk2.Task.Parameters.tags.name: self.Parameters.tags,
        })
        return GenericTestsIosRunner(
            self,
            description="{} : {}".format(self.Parameters.description, caption),
            priority=min(
                self.Parameters.priority,
                ctt.Priority(ctt.Priority.Class.SERVICE, ctt.Priority.Subclass.NORMAL)  # default API limitation
            ),
            **params
        )

    @property
    def env(self):
        try:
            return self._env
        except AttributeError:
            self._env = self.Utils.shell_executor.default_env
            self.Utils.ios_helper.prepare_env(self, self._env)
            GradleParameters.prepare_env(self, self._env)
        return self._env
