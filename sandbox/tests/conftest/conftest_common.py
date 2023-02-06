import pytest

import sandbox.serviceq.types as qtypes

__all__ = ["test_queue", "test_queue_with_single_score"]


@pytest.fixture(scope="session")
def test_queue():
    return {
        1: [1, [[3, "host1"], [2, "host2"], [1, "host3"]], qtypes.TaskInfo(type="T1", owner="O1", enqueue_time=100)],
        2: [3, [[1, "host1"], [2, "host2"], [3, "host3"]], qtypes.TaskInfo(type="T2", owner="O2", enqueue_time=101)],
        3: [2, [[2, "host1"], [1, "host2"]], qtypes.TaskInfo(type="T3", owner="O3", enqueue_time=102)],
        4: [2, [[1, "host1"], [2, "host2"]], qtypes.TaskInfo(type="T4", owner="O4", enqueue_time=103)]
    }


@pytest.fixture(scope="session")
def test_queue_with_single_score():
    return {
        1: [1, ["host1", "host2", "host3"], qtypes.TaskInfo(type="T1", owner="O1", enqueue_time=100), 1],
        2: [3, ["host1", "host2", "host3"], qtypes.TaskInfo(type="T2", owner="O2", enqueue_time=101), 2],
        3: [2, ["host1", "host2"], qtypes.TaskInfo(type="T3", owner="O3", enqueue_time=102), 3],
        4: [2, ["host1", "host2"], qtypes.TaskInfo(type="T4", owner="O4", enqueue_time=103), 4]
    }
