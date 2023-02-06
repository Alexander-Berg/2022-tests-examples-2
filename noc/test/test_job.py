from unittest.mock import patch

from noc.grad.grad.lib.scheduler import Job
from noc.grad.grad.lib.structures import FrozenDict


def make_job(interval, scattering_percent=0):
    job = Job(
        name="olo_unique in SNMP poller",
        key_data=FrozenDict(interval=interval),
        aux_data={},
        afterburn=0,
        job_type="unique",
        scattering_percent=scattering_percent,
    )
    return job


@patch("noc.grad.grad.lib.scheduler.time")
def test_scheduler(time):
    time.return_value = 10
    job = make_job(interval=10)
    res = job.next_start()
    assert res == 10
    job.last_done = 10
    # the same time
    time.return_value = 10
    next_start = job.next_start()
    assert next_start == 20


@patch("noc.grad.grad.lib.scheduler.time")
def test_scheduler_scattering(time):
    time.return_value = 30
    job = make_job(interval=30, scattering_percent=50)
    # offset == 14
    res = job.next_start()
    assert res == 30
    job.last_done = 30
    # the same time
    time.return_value = 30
    res = job.next_start()
    assert res == 74
    job.last_done = 74
    time.return_value = 74
    res = job.next_start()
    assert res == 104
