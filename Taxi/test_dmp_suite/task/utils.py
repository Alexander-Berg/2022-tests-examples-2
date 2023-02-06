from collections import defaultdict

from dmp_suite.task.base import AbstractTask, LockStandardTypes

from dmp_suite.ctl.storage import DictStorage
from connection.ctl import WrapCtl


class fake_module:
    pass


class SimpleTask(AbstractTask):
    def __init__(self, *args, **kwargs):
        super(SimpleTask, self).__init__(*args, **kwargs)
        self._run_logger = defaultdict(list)

    def _run(self, args):
        self._run_logger[self.name].append(args)


def create_task(name, scheduler=None) -> AbstractTask:
    task = SimpleTask(name)

    if scheduler:
        task = task.set_scheduler(scheduler)

    return task


class WrapCtlMock(WrapCtl):
    def __init__(self):
        super().__init__(DictStorage())
