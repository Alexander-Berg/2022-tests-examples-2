from sandbox import sdk2
from sandbox.common.types import task as ctt
from sandbox.projects.yabs.qa.tasks.TestChildTask import TestChildTask
from sandbox.projects.resource_types import OTHER_RESOURCE


class TestParentTask(sdk2.Task):
    class Requirements(sdk2.Requirements):
        cores = 1
        ram = 1024

        class Caches(sdk2.Requirements.Caches):
            pass

    def on_execute(self):
        if not self.Context.resource_id and not self.Context.subtask_id:
            resource = OTHER_RESOURCE(self, 'Resource will be filled by subtask', 'external_path.txt')
            self.Context.resource_id = resource.id
            self.Context.subtask_id = TestChildTask(
                self,
                resource_id=resource.id,
                __requirements__={'tasks_resource': self.Requirements.tasks_resource}
            ).enqueue().id
            self.Context.save()
            raise sdk2.WaitTask([self.Context.subtask_id], statuses=(ctt.Status.Group.FINISH + ctt.Status.Group.BREAK))
