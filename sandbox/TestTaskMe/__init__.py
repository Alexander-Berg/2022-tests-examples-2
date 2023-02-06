import logging
import time
from sandbox import sdk2
from sandbox.projects.TeamcityAgentlessTask.AgentlessBase import AgentlessBase


class TestTaskMe(sdk2.Task, AgentlessBase):

    class Parameters(sdk2.Task.Parameters):
        branch = sdk2.parameters.String("Branch name")
        commit = sdk2.parameters.String("Commit id")

    @AgentlessBase.Decorators.agentless_create
    @AgentlessBase.Decorators.add_logger(logging.getLogger("agentless"))
    def on_execute(self):
        logger = logging.getLogger("agentless")
        with self.memoize_stage.first_step(commit_on_entrance=False):
            logger.info("In first time")
        logger.info("Starting Task!")
        res = sdk2.Resource['PLAIN_TEXT'](self, "Testing resource creation", "testfile.txt")
        res.path.write_bytes("Hello world!")
        res2 = sdk2.Resource['PLAIN_TEXT'](self, "Testing resource creation2", "testfile2.txt")
        res2.path.write_bytes("Hello world2!")
        sdk2.ResourceData(res).ready()
        sdk2.ResourceData(res2).ready()
        time.sleep(3)
        for i in range(100):
            logger.info(str(i) + "f" * 10)
        self._upload_resource(res)
        self._upload_resource(res2)
        logger.info("Task finished")
