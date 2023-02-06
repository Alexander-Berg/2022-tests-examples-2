from typing import Any

from taxi.stq import async_worker_ng


def task_info(
        queue: str = 'any', id_: Any = None, exec_tries: int = 0,
) -> async_worker_ng.TaskInfo:
    return async_worker_ng.TaskInfo(
        id=id_, exec_tries=exec_tries, reschedule_counter=0, queue=queue,
    )
