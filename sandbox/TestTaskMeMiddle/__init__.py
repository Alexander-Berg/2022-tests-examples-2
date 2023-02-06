import logging
import sandbox.common.types.task as ctt
from sandbox import sdk2


class TestTaskMeMiddle(sdk2.Task):
    class Parameters(sdk2.Task.Parameters):
        branch = sdk2.parameters.String("Branch name")
        commit = sdk2.parameters.String("Commit id")

    def on_execute(self):
        with self.memoize_stage.first_step:
            parameters = [(k, v) for k, v in self.Context if not k.startswith("__") and not k.startswith("_")]
            parameters += [(k, v) for k, v in dict(self.Parameters).items() if not k.startswith("__")]
            child = sdk2.Task['TEST_TASK_ME'](
                self,
                description="Child of {}".format(self.id),
                owner=self.owner,
                **{k: v for k, v in parameters}
            ).enqueue()
            self.Context.child = child.id
            self.Context.save()
            logging.info("Starting wait")
            raise sdk2.WaitTask(child, ctt.Status.Group.FINISH, wait_all=True)
        logging.info("Middle task done!")
