from sandbox.serviceq import types as qtypes


def qserver_with_data_factory(qserver, test_queue):
    sorted_hosts = lambda hosts: sorted(hosts, key=lambda _: -_[0])
    qserver.sync(
        [[task_id, item[0], sorted_hosts(item[1]), item[2]] for task_id, item in test_queue.iteritems()],
        reset=True
    )
    return qserver


def qcommit(gen):
    try:
        return gen.send(True)
    except StopIteration:
        pass


def qpop(qserver, host, host_info=None, job_id=None):
    if host_info is None:
        host_info = qtypes.HostInfo(
            capabilities=qtypes.ComputingResources(disk_space=1),
            free=qtypes.ComputingResources(),
        )
    task_to_execute = qserver.task_to_execute(host, host_info)
    task_to_execute_it = qserver.task_to_execute_it(host, host_info)
    next(task_to_execute)
    result = None
    while True:
        try:
            task_id, score = task_to_execute_it.send(result)
        except StopIteration as ex:
            it_result = ex.message
            try:
                task_to_execute.send((None, None))
                task_to_execute.send(it_result)
            except StopIteration:
                pass
            break
        accepted = yield [task_id, score]
        it_result = None
        if accepted is not None:
            result = task_to_execute.send((task_id, job_id))
            if result == qtypes.QueueIterationResult.SKIP_JOB:
                break
            if result != qtypes.QueueIterationResult.ACCEPTED:
                continue
            try:
                task_to_execute_it.send(result)
            except StopIteration as ex:
                it_result = ex.message
            try:
                task_to_execute.send((None, None))
                task_to_execute.send(it_result)
            except StopIteration:
                pass
            yield result
            break
