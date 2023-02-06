import uuid

from sandbox.serviceq import types as qtypes


def qcommit(gen):
    try:
        return gen.send(True)
    except StopIteration:
        pass


def qpop(qclient, host, host_info=None, job_id=None):
    if job_id is None:
        job_id = uuid.uuid4().hex
    if host_info is None:
        host_info = qtypes.HostInfo(
            capabilities=qtypes.ComputingResources(disk_space=1),
            free=qtypes.ComputingResources(),
        )
    task_to_execute = qclient.task_to_execute(host, host_info)
    task_to_execute_it = qclient.task_to_execute_it(host, host_info)
    task_to_execute.next()
    result = None
    while True:
        item = task_to_execute_it.send(result)
        if item is None:
            task_to_execute.send((None, None))
            task_to_execute.send(task_to_execute_it.wait())
            break
        task_id, score = item
        accepted = yield [task_id, score]
        if accepted is not None:
            result = task_to_execute.send((task_id, job_id))
            if result == qtypes.QueueIterationResult.SKIP_JOB:
                break
            if result != qtypes.QueueIterationResult.ACCEPTED:
                continue
            task_to_execute_it.send(result)
            task_to_execute.send((None, None))
            task_to_execute.send(task_to_execute_it.wait())
            yield result
            break
