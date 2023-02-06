from __future__ import unicode_literals

import Queue

import pytest
from sandbox.projects.sandbox.common import computation_graph


@pytest.mark.parametrize("jobs_graph", [
    [],
    [[]] * 42,
    [[], [0], [1], [2], [3], [4]],
    [[], [], [], [0, 1, 2], [3], [0], [1], [2], []],
])
def test__simple_computation_graph(jobs_graph):
    queue = Queue.Queue()
    for _ in range(3):  # repeat for increasing probability of flapping test detection
        graph = computation_graph.SimpleComputationGraph()
        for job_ind, wait_jobs in enumerate(jobs_graph):
            graph.add_job(queue.put, args=(job_ind,), wait_jobs=wait_jobs)
        graph.run()
        results = [queue.get() for _ in jobs_graph]
        for job_ind, wait_jobs in enumerate(jobs_graph):
            previous_jobs = results[:results.index(job_ind)]
            assert all(child_job in previous_jobs for child_job in wait_jobs)


def test__simple_computation_graph__invalid_graph():
    queue = Queue.Queue()

    graph = computation_graph.SimpleComputationGraph()
    job_id = graph.add_job(queue.put, args=(1,))
    job_id = graph.add_job(queue.put, args=(2,), wait_jobs=[job_id])
    with pytest.raises(ValueError):
        graph.add_job(queue.put, args=(3,), wait_jobs=[-1])
    with pytest.raises(ValueError):
        graph.add_job(queue.put, args=(3,), wait_jobs=[job_id + 1])
    with pytest.raises(ValueError):
        graph.add_job(queue.put, args=(4,), wait_jobs=[job_id + 2])
    graph.run()

    assert 1 == queue.get()
    assert 2 == queue.get()
