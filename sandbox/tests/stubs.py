import uuid
from datetime import datetime
from typing import List, Optional

from ott.drm.library.python.packager_task.clients import PackagerTasksApiClient
from ott.drm.library.python.packager_task.models import (
    Notification,
    PackagerOutputStatus,
    PackagerOutput,
    TaskExecutionState,
    TaskError,
    PackagerTask,
    TaskStatus
)


class PackagerTasksApiClientStub(PackagerTasksApiClient):
    def __init__(self):
        self._tasks = {}

    def get_tasks(self, status: TaskStatus, nirvana_quota: str = None, vod_providers : Optional[List[str]] = None,
                  limit: int = 100) -> List[PackagerTask]:
        def is_matched(task: PackagerTask):
            if task.status != status:
                return False

            if nirvana_quota:
                return task.nirvana_quota == nirvana_quota

            return True

        tasks = [task for task in self._tasks.values() if is_matched(task)]
        return tasks[:limit]

    def get_task(self, task_id: uuid.UUID) -> PackagerTask:
        raise NotImplementedError()

    def count(self, statuses: List[TaskStatus], nirvana_quota: str = None, vod_providers : Optional[List[str]] = None,
              parallel_encoding: bool = None, update_time_lower_bound: datetime = None) -> int:
        def is_matched(task: PackagerTask):
            if task.status not in statuses:
                return False

            if nirvana_quota:
                return task.nirvana_quota == nirvana_quota

            return True

        tasks = [task for task in self._tasks.values() if is_matched(task)]

        return len(tasks)

    def create(self, task: PackagerTask) -> uuid.UUID:
        task.task_id = uuid.uuid4()
        self._tasks[task.task_id] = task

        return task.task_id

    def update(self, task: PackagerTask, execution_state: TaskExecutionState, error: TaskError = None):
        self._tasks[task.task_id] = task

    def create_packager_outputs(self, task_id: uuid.UUID, packager_outputs: List[PackagerOutput]):
        raise NotImplementedError()

    def update_packager_output(self, packager_output: PackagerOutput):
        raise NotImplementedError()

    def get_packager_outputs(self, status: PackagerOutputStatus) -> List[PackagerOutput]:
        raise NotImplementedError()

    def add_notification_to_queue(self, notification: Notification):
        raise NotImplementedError()

    def remove_notification_from_queue(self, notification: Notification):
        raise NotImplementedError()

    def get_notifications(self) -> List[Notification]:
        raise NotImplementedError()
