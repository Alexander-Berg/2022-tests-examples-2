import time
import logging

from sandbox.sandboxsdk import task

from sandbox.projects.sandbox import test_task_2


# some sdk2 parameters are not supported in sdk1
EXCLUDE_PARAMETERS = ["client_tags", "json_parameter"]


class TestTask21(task.SandboxTask):
    """
    SDK1 task using parameters from TEST_TASK_2
    """

    type = "TEST_TASK_21"

    Parameters = test_task_2.TestTask2.Parameters
    input_parameters = list(p for p in Parameters if p.name not in EXCLUDE_PARAMETERS)

    def on_execute(self):
        logging.info("Executing")
        sleep = self.ctx[self.Parameters.live_time.name]
        if sleep:
            msg = "Sleeping for %.2fs" % sleep
            logging.info(msg)
            time.sleep(sleep)
