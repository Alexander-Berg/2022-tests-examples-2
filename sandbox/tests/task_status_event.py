import sandbox.common.types.task as ctt

from sandbox.yasandbox.database import mapping
from sandbox.yasandbox.controller import task as task_controller
from sandbox.yasandbox.controller import task_status_event


class TestTaskStatusEvent(object):
    def test__simple(self):
        task = mapping.Task()
        task.host = "host"
        task.author = task.owner = "unspecified-author"
        task.type = "TEST_TASK_2"
        wrapper = task_controller.TaskWrapper(task)
        wrapper.create()

        controller = task_status_event.TaskStatusEvent()
        entity_ids = controller.create(task, ctt.Status.DRAFT)
        assert entity_ids and len(entity_ids) == 1
