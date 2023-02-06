# coding=utf-8
import os
import tempfile

import jinja2

from sandbox import sdk2
from sandbox.common.types import resource
from sandbox.projects import resource_types

from sandbox.common.types.misc import DnsType
from sandbox.projects.metrika.mobile.sdk.generics.generic_tests_android_runner import GenericTestsAndroidRunner


class MapsandroidTestLauncher(GenericTestsAndroidRunner):
    """ Task which launch test on a particular lxc-container """

    class Utils(GenericTestsAndroidRunner.Utils):
        pass

    class Requirements(sdk2.Task.Requirements):
        dns = DnsType.DNS64
        privileged = True

    class Parameters(sdk2.Task.Parameters):
        # common parameters
        kill_timeout = 3 * 60 * 60

        container = sdk2.parameters.Container("Environment container resource", required=True)
        # custom parameters
        script = sdk2.parameters.String("Script to execute", required=True, multiline=True)
        report_relative_path = sdk2.parameters.String("Относительный путь к отчёту (внутри ./artifacts)",
                                                      description="Здесь указан относительный путь к html-файлу "
                                                                  "отчёта. Путь отсчитывается относительно каталога, "
                                                                  "переданного в предыдущем параметре.",
                                                      default="reports/html/index.html")

    def on_enqueue(self):
        self.Context.report_relative_path = self.Parameters.report_relative_path

    def on_execute(self):
        try:
            with self.Utils.emulator_helper.xvfb(self):
                with sdk2.helpers.ProgressMeter("Find AndroidSdk resource"):
                    self._find_android_sdk_resource()
                with sdk2.helpers.ProgressMeter("Executing script"):
                    self._execute_script()
        except Exception:
            self.logger.error("Exception in scenario", exc_info=True)
            raise
        finally:
            with sdk2.helpers.ProgressMeter("Report test results"):
                try:
                    self._report_test_results()
                except Exception:
                    self.logger.error("Exception in clean up. Continue.", exc_info=True)
            self._create_custom_logs_resource()

    def _prepare_environment(self):
        pass

    def _execute_script(self):
        with tempfile.NamedTemporaryFile() as script_file:
            script_file.write(self.Parameters.script)
            script_file.flush()
            with sdk2.helpers.ProcessLog(self, logger="script") as log:
                sdk2.helpers.subprocess.call(['/bin/bash', script_file.name],
                                             stdout=log.stdout,
                                             stderr=sdk2.helpers.process.subprocess.STDOUT)

    def _find_android_sdk_resource(self):

        android_sdk_resource = sdk2.Resource.find(
            resource_type=resource_types.OTHER_RESOURCE,
            state=resource.State.READY,
            attr_name="mapsandroid_android_sdk",
            attr_value="True"
        ).first()

        android_sdk_data = sdk2.ResourceData(android_sdk_resource)
        os.environ["ANDROID_HOME"] = str(android_sdk_data.path)
        os.environ["DISPLAY"] = ":1.0"
     #   os.environ["LD_LIBRARY_PATH"] = os.environ["ANDROID_HOME"] + "/emulator/lib64/:" + \
      #                                  os.environ["ANDROID_HOME"] + "/emulator/lib64/gles_mesa:" + \
       #                                 os.environ["ANDROID_HOME"] + "/emulator/lib64/qt/lib/:" # + \
#                                        os.environ["LD_LIBRARY_PATH"]

    @sdk2.header()
    def report(self):
        if self.Context.artifacts_resource_id is not None:
            template_context = {"resource_link": sdk2.Resource[self.Context.artifacts_resource_id].http_proxy,
                                "report_relative_path": self.Context.report_relative_path}
            return jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname(os.path.abspath(__file__))),
                                      extensions=['jinja2.ext.do']).get_template("header.html").render(template_context)
        else:
            return None
