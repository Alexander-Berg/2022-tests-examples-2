import logging
from ci.tasklet.common.proto import service_pb2 as ci
from metrika.tasklets.run_tests.proto import arcadia_tasklet

import metrika.pylib.tasklet

logger = logging.getLogger(__name__)


class RunArcadiaTestsImpl(metrika.pylib.tasklet.RunSandboxTaskMixin, arcadia_tasklet.RunArcadiaTestsBase):
    def run(self):
        logger.info("Input:\n" + str(self.input))

        task_id = self.start_sandbox_task(
            type="METRIKA_CORE_ARCADIA_TESTS_RUN",
            owner=self.input.sandbox.owner,
            params={
                "checkout_arcadia_from_url": "arcadia-arc:/#{}".format(self.input.context.target_revision.hash),
                "targets": ";".join(self.input.tests.targets)
            }
        )

        if self.wait_for_sandbox_task(task_id):
            self._report_progress(url="https://sandbox.yandex-team.ru/task/{}".format(task_id), status=ci.TaskletProgress.Status.SUCCESSFUL)
            output = self.get_output(task_id)
            self.output.result.is_success = output["test_results"]["failed"] == 0
            report_resource = self.sandbox_client.resource[output["report_resource"]].read()
            self._report_progress(id="allure", url="{}/index.html".format(report_resource["http"]["proxy"]),
                                  status=ci.TaskletProgress.Status.SUCCESSFUL if self.output.result.is_success else ci.TaskletProgress.Status.FAILED)
            if not self.output.result.is_success:
                raise Exception("Tests failed")

        else:
            self._report_progress(url="https://sandbox.yandex-team.ru/task/{}".format(task_id), status=ci.TaskletProgress.Status.FAILED)
            self.raise_on_sandbox_task(task_id)
