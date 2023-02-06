from __future__ import absolute_import, print_function

import os
import gc
import time
import uuid
import pytest
import random
import gevent
import msgpack
import itertools as it
import collections

from sandbox.common import system
from sandbox.common import context
from sandbox.common import itertools

import sandbox.common.types.task as ctt
import sandbox.common.types.client as ctc

import sandbox.serviceq.state as qstate
import sandbox.serviceq.types as qtypes
import sandbox.serviceq.errors as qerrors

from sandbox.serviceq.tests.server import utils as server_utils


def get_jobs(qserver, host, host_info=None, jobs_ids=()):
    if host_info is None:
        host_info = qtypes.HostInfo(
            capabilities=qtypes.ComputingResources(disk_space=1),
            free=qtypes.ComputingResources(),
        )
    task_to_execute = qserver.task_to_execute(host, host_info)
    task_to_execute_it = qserver.task_to_execute_it(host, host_info)
    jobs = []
    try:
        next(task_to_execute)
    except StopIteration:
        pass
    else:
        result = None
        jids = list(jobs_ids)
        it_result = None
        while jids:
            try:
                item = task_to_execute_it.send(result)
            except StopIteration as ex:
                it_result = ex.message
                item = None
            if item is None:
                break
            tid, score = item
            result = task_to_execute.send((tid, jids[0]))
            if result != qtypes.QueueIterationResult.ACCEPTED:
                continue
            result = qtypes.QueueIterationResult.NEXT_TASK
            jobs.append((tid, jids.pop(0)))
        else:
            try:
                task_to_execute_it.send(qtypes.QueueIterationResult.ACCEPTED)
            except StopIteration as ex:
                it_result = ex.message
        assert it_result is not None
        task_to_execute.send((None, None))
        try:
            task_to_execute.send(it_result)
        except StopIteration:
            pass
    return jobs


class TestServer(object):
    def test__queue(self, qserver_with_data):
        queue = list(qserver_with_data.queue())
        assert queue == [
            (2, 3, [[3, 2], [2, 1], [1, 0]], 2, (None, None, 1, 1, 101, 0, None), None),
            (3, 2, [[2, 0], [1, 1]], 3, (None, None, 2, 2, 102, 0, None), None),
            (4, 2, [[2, 1], [1, 0]], 4, (None, None, 3, 3, 103, 0, None), None),
            (1, 1, [[3, 0], [2, 1], [1, 2]], 1, (None, None, 0, 0, 100, 0, None), None),
            None,
            ["host1", "host2", "host3"],
            ["O1", "O2", "O3", "O4"],
            ["T1", "T2", "T3", "T4"],
            []
        ]

    def test__queue_by_host(self, qserver_with_data):
        queue = qserver_with_data.queue_by_host("non_existent_host")
        assert queue == []

        queue = qserver_with_data.queue_by_host("host1")
        assert queue == [
            (2, -1, 4, 4),
            (2, -2, 3, 3),
            (3, -1, 2, 2),
            (1, -3, 1, 1)
        ]

        queue = qserver_with_data.queue_by_host("host2")
        assert queue == [
            (2, -2, 4, 4),
            (2, -1, 3, 3),
            (3, -2, 2, 2),
            (1, -2, 1, 1)
        ]

        queue = qserver_with_data.queue_by_host("host3")
        assert queue == [
            (3, -3, 2, 2),
            (1, -1, 1, 1)
        ]

    def test__change_priority(self, qserver_with_quotas, monkeypatch):
        qpop = server_utils.qpop
        qcommit = server_utils.qcommit
        monkeypatch.setattr(qstate, "EXTERNAL_SCALE", 1000)
        DQ = qtypes.DEFAULT_QUOTA
        monkeypatch.setattr(qtypes, "DEFAULT_QUOTA", DQ * 1000)
        monkeypatch.setattr(qstate, "UNLIMITED_OWNER_MINIMUM_PRIORITY", 20)
        host_info = qtypes.HostInfo(
            capabilities=qtypes.ComputingResources(0, [], 32, 128 << 10),
            free=qtypes.ComputingResources()
        )
        qserver_with_quotas.push(
            1, 10, [[0, "host"]], task_info=qtypes.TaskInfo(None, None, "T", "O1", 0, 20000)
        )
        qserver_with_quotas.push(
            2, 11, [[0, "host"]], task_info=qtypes.TaskInfo(None, None, "T", "O2", 0, 20000)
        )
        assert qserver_with_quotas.owners_rating() == [
            ["O2", qtypes.OwnersRatingItem(0, DQ, 0, 0, DQ, 0, 1, True)],
            ["O1", qtypes.OwnersRatingItem(0, DQ, 0, 0, DQ, 0, 1, True)]
        ]
        qserver_with_quotas.push(1, 11, None)

        gen = qpop(qserver_with_quotas, "host", host_info=host_info, job_id=uuid.uuid4().hex)
        assert next(gen) == [2, 0]
        qcommit(gen)
        qserver_with_quotas.calculate_consumptions()
        assert qserver_with_quotas.owners_rating() == [
            ["O1", qtypes.OwnersRatingItem(0, DQ, 0, 0, DQ, 0, 1, True)],
            ["O2", qtypes.OwnersRatingItem(2589, -3928, 0, 6400, DQ, 1, 0, True)]
        ]

        gen = qpop(qserver_with_quotas, "host", host_info=host_info, job_id=uuid.uuid4().hex)
        assert next(gen) == [1, 0]
        qcommit(gen)
        qserver_with_quotas.calculate_consumptions()
        assert qserver_with_quotas.owners_rating() == [
            ["O1", qtypes.OwnersRatingItem(2589, -3928, 0, 6400, DQ, 1, 0, True)],
            ["O2", qtypes.OwnersRatingItem(2589, -3928, 0, 6400, DQ, 1, 0, True)]
        ]

    def test__quota_credit(self, qserver_with_quotas, monkeypatch):
        qpop = server_utils.qpop
        qcommit = server_utils.qcommit
        monkeypatch.setattr(qstate, "EXTERNAL_SCALE", 1000)
        DQ = qtypes.DEFAULT_QUOTA
        monkeypatch.setattr(qtypes, "DEFAULT_QUOTA", DQ * 1000)
        monkeypatch.setattr(qstate, "UNLIMITED_OWNER_MINIMUM_PRIORITY", 20)
        current_time = int(time.time())
        monkeypatch.setattr(time, "time", lambda: current_time)
        host_info = qtypes.HostInfo(
            capabilities=qtypes.ComputingResources(0, [], 32, 128 << 10),
            free=qtypes.ComputingResources()
        )
        qserver_with_quotas.push(
            1, 11, [[0, "host"]], task_info=qtypes.TaskInfo(None, None, "T", "O1", 0, 0)
        )
        qserver_with_quotas.push(
            2, 12, [[0, "host"]], task_info=qtypes.TaskInfo(None, None, "T", "O2", 0, 20000)
        )
        qserver_with_quotas.push(
            3, 12, [[0, "host"]], task_info=qtypes.TaskInfo(None, None, "T", "O3", 0, 15450)
        )
        qserver_with_quotas.push(
            4, 12, [[0, "host"]], task_info=qtypes.TaskInfo(None, None, "T", "O4", 0, 12875)
        )
        qserver_with_quotas.push(
            5, 12, [[0, "host"]], task_info=qtypes.TaskInfo(None, None, "T", "O5", 0, 10300)
        )
        assert qserver_with_quotas.owners_rating() == [
            ["O5", qtypes.OwnersRatingItem(0, DQ, 0, 0, DQ, 0, 1, True)],
            ["O4", qtypes.OwnersRatingItem(0, DQ, 0, 0, DQ, 0, 1, True)],
            ["O3", qtypes.OwnersRatingItem(0, DQ, 0, 0, DQ, 0, 1, True)],
            ["O2", qtypes.OwnersRatingItem(0, DQ, 0, 0, DQ, 0, 1, True)],
            ["O1", qtypes.OwnersRatingItem(0, DQ, 0, 0, DQ, 0, 1, True)]
        ]

        gen = qpop(qserver_with_quotas, "host", host_info=host_info, job_id=uuid.uuid4().hex)
        assert next(gen) == [5, 0]
        qcommit(gen)
        qserver_with_quotas.calculate_consumptions()
        assert qserver_with_quotas.owners_rating() == [
            ["O4", qtypes.OwnersRatingItem(0, DQ, 0, 0, DQ, 0, 1, True)],
            ["O3", qtypes.OwnersRatingItem(0, DQ, 0, 0, DQ, 0, 1, True)],
            ["O2", qtypes.OwnersRatingItem(0, DQ, 0, 0, DQ, 0, 1, True)],
            ["O1", qtypes.OwnersRatingItem(0, DQ, 0, 0, DQ, 0, 1, True)],
            ["O5", qtypes.OwnersRatingItem(1334, -824, 0, 3296, DQ, 1, 0, True)]
        ]
        gen = qpop(qserver_with_quotas, "host", host_info=host_info, job_id=uuid.uuid4().hex)
        assert next(gen) == [4, 0]
        qcommit(gen)
        qserver_with_quotas.calculate_consumptions()
        assert qserver_with_quotas.owners_rating() == [
            ["O3", qtypes.OwnersRatingItem(0, DQ, 0, 0, DQ, 0, 1, True)],
            ["O2", qtypes.OwnersRatingItem(0, DQ, 0, 0, DQ, 0, 1, True)],
            ["O1", qtypes.OwnersRatingItem(0, DQ, 0, 0, DQ, 0, 1, True)],
            ["O5", qtypes.OwnersRatingItem(1334, -824, 0, 3296, DQ, 1, 0, True)],
            ["O4", qtypes.OwnersRatingItem(1667, -1648, 0, 4120, DQ, 1, 0, True)]
        ]
        gen = qpop(qserver_with_quotas, "host", host_info=host_info, job_id=uuid.uuid4().hex)
        assert next(gen) == [3, 0]
        qcommit(gen)
        qserver_with_quotas.calculate_consumptions()
        assert qserver_with_quotas.owners_rating() == [
            ["O2", qtypes.OwnersRatingItem(0, DQ, 0, 0, DQ, 0, 1, True)],
            ["O1", qtypes.OwnersRatingItem(0, DQ, 0, 0, DQ, 0, 1, True)],
            ["O5", qtypes.OwnersRatingItem(1334, -824, 0, 3296, DQ, 1, 0, True)],
            ["O4", qtypes.OwnersRatingItem(1667, -1648, 0, 4120, DQ, 1, 0, True)],
            ["O3", qtypes.OwnersRatingItem(2000, -DQ, 0, 4944, DQ, 1, 0, True)]
        ]
        gen = qpop(qserver_with_quotas, "host", host_info=host_info, job_id=uuid.uuid4().hex)
        assert next(gen) == [2, 0]
        qcommit(gen)
        qserver_with_quotas.calculate_consumptions()
        assert qserver_with_quotas.owners_rating() == [
            ["O1", qtypes.OwnersRatingItem(0, DQ, 0, 0, DQ, 0, 1, True)],
            ["O5", qtypes.OwnersRatingItem(1334, -824, 0, 3296, DQ, 1, 0, True)],
            ["O4", qtypes.OwnersRatingItem(1667, -1648, 0, 4120, DQ, 1, 0, True)],
            ["O3", qtypes.OwnersRatingItem(2000, -DQ, 0, 4944, DQ, 1, 0, True)],
            ["O2", qtypes.OwnersRatingItem(2589, -3928, 0, 6400, DQ, 1, 0, True)]
        ]

        qserver_with_quotas.push(
            10, 10, [[0, "host"]], task_info=qtypes.TaskInfo(None, None, "T", "O5", 0, 0)
        )
        qserver_with_quotas.push(
            11, 10, [[0, "host"]], task_info=qtypes.TaskInfo(None, None, "T", "O4", 0, 0)
        )
        qserver_with_quotas.push(
            12, 10, [[0, "host"]], task_info=qtypes.TaskInfo(None, None, "T", "O3", 0, 0)
        )
        qserver_with_quotas.push(
            13, 10, [[0, "host"]], task_info=qtypes.TaskInfo(None, None, "T", "O2", 0, 0)
        )

        gen = qpop(qserver_with_quotas, "host", host_info=host_info, job_id=uuid.uuid4().hex)
        assert list(gen) == [[1, 0], [10, 0], [11, 0], [12, 0], [13, 0]]

        qserver_with_quotas.push(10, 20, None)
        qserver_with_quotas.push(11, 20, None)
        qserver_with_quotas.push(12, 20, None)
        qserver_with_quotas.push(13, 20, None)
        gen = qpop(qserver_with_quotas, "host", host_info=host_info, job_id=uuid.uuid4().hex)
        assert list(gen) == [[10, 0], [1, 0], [10, 0], [11, 0], [12, 0], [13, 0]]

        qserver_with_quotas.push(11, 21, None)
        qserver_with_quotas.push(12, 21, None)
        qserver_with_quotas.push(13, 21, None)
        gen = qpop(qserver_with_quotas, "host", host_info=host_info, job_id=uuid.uuid4().hex)
        assert list(gen) == [[11, 0], [10, 0], [1, 0], [10, 0], [11, 0], [12, 0], [13, 0]]

        qserver_with_quotas.push(12, 22, None)
        qserver_with_quotas.push(13, 22, None)
        gen = qpop(qserver_with_quotas, "host", host_info=host_info, job_id=uuid.uuid4().hex)
        assert list(gen) == [[12, 0], [11, 0], [10, 0], [1, 0], [10, 0], [11, 0], [12, 0], [13, 0]]

    def test__quota_parent_owner(self, qserver_with_quotas, monkeypatch):
        qpop = server_utils.qpop
        qcommit = server_utils.qcommit
        monkeypatch.setattr(qstate, "EXTERNAL_SCALE", 1000)
        monkeypatch.setattr(qtypes, "DEFAULT_QUOTA", qtypes.DEFAULT_QUOTA * 1000)
        monkeypatch.setattr(qstate, "UNLIMITED_OWNER_MINIMUM_PRIORITY", 20)

        task_info = lambda owner: qtypes.TaskInfo(None, None, "T", owner, 0, 20000)

        qserver_with_quotas.push(1, 10, [[0, "host"]], task_info=task_info("O1"))
        qserver_with_quotas.push(11, 10, [[0, "host"]], task_info=task_info("O11"))
        qserver_with_quotas.push(12, 10, [[0, "host"]], task_info=task_info("O12"))
        qserver_with_quotas.push(2, 10, [[0, "host"]], task_info=task_info("O2"))
        qserver_with_quotas.push(21, 10, [[0, "host"]], task_info=task_info("O21"))
        qserver_with_quotas.push(22, 10, [[0, "host"]], task_info=task_info("O22"))

        qserver_with_quotas.set_quota("O1", 0)
        qserver_with_quotas.set_quota("O2", 0)

        qserver_with_quotas.set_parent_owner("O11", "O1")
        qserver_with_quotas.set_parent_owner("O12", "O1")
        qserver_with_quotas.set_parent_owner("O21", "O2")
        qserver_with_quotas.set_parent_owner("O22", "O2")

        with pytest.raises(ValueError):
            qserver_with_quotas.set_parent_owner("UNKNOWN", "O1")

        with pytest.raises(ValueError):
            qserver_with_quotas.set_parent_owner("O11", "UNKNOWN")

        with pytest.raises(ValueError):
            qserver_with_quotas.set_parent_owner("O1", "O2")

        with pytest.raises(ValueError):
            qserver_with_quotas.set_parent_owner("O22", "O11")

        qserver_with_quotas.set_quota("O11", 50)
        qserver_with_quotas.set_quota("O12", 50)
        qserver_with_quotas.set_quota("O21", 100)
        qserver_with_quotas.set_quota("O22", 100)

        with pytest.raises(ValueError):
            qserver_with_quotas.set_quota("O1", 100)

        with pytest.raises(ValueError):
            qserver_with_quotas.set_quota("O11", None)

        assert qserver_with_quotas.owners_rating() == [
            ["O22", qtypes.OwnersRatingItem(0, 200, 0, 0, 100, 0, 1, False)],
            ["O21", qtypes.OwnersRatingItem(0, 200, 0, 0, 100, 0, 1, False)],
            ["O2", qtypes.OwnersRatingItem(0, 200, 0, 0, 200, 0, 1, False)],
            ["O12", qtypes.OwnersRatingItem(0, 100, 0, 0, 50, 0, 1, False)],
            ["O11", qtypes.OwnersRatingItem(0, 100, 0, 0, 50, 0, 1, False)],
            ["O1", qtypes.OwnersRatingItem(0, 100, 0, 0, 100, 0, 1, False)],
        ]

        qserver_with_quotas.set_quota("O11", 75)

        assert qserver_with_quotas.owners_rating() == [
            ["O22", qtypes.OwnersRatingItem(0, 200, 0, 0, 100, 0, 1, False)],
            ["O21", qtypes.OwnersRatingItem(0, 200, 0, 0, 100, 0, 1, False)],
            ["O2", qtypes.OwnersRatingItem(0, 200, 0, 0, 200, 0, 1, False)],
            ["O11", qtypes.OwnersRatingItem(0, 125, 0, 0, 75, 0, 1, False)],
            ["O12", qtypes.OwnersRatingItem(0, 125, 0, 0, 50, 0, 1, False)],
            ["O1", qtypes.OwnersRatingItem(0, 125, 0, 0, 125, 0, 1, False)],
        ]

        qserver_with_quotas.set_quota("O11", 160)

        assert qserver_with_quotas.owners_rating() == [
            ["O11", qtypes.OwnersRatingItem(0, 210, 0, 0, 160, 0, 1, False)],
            ["O12", qtypes.OwnersRatingItem(0, 210, 0, 0, 50, 0, 1, False)],
            ["O1", qtypes.OwnersRatingItem(0, 210, 0, 0, 210, 0, 1, False)],
            ["O22", qtypes.OwnersRatingItem(0, 200, 0, 0, 100, 0, 1, False)],
            ["O21", qtypes.OwnersRatingItem(0, 200, 0, 0, 100, 0, 1, False)],
            ["O2", qtypes.OwnersRatingItem(0, 200, 0, 0, 200, 0, 1, False)],
        ]

        qserver_with_quotas.set_quota("O22", 25)

        assert qserver_with_quotas.owners_rating() == [
            ["O11", qtypes.OwnersRatingItem(0, 210, 0, 0, 160, 0, 1, False)],
            ["O12", qtypes.OwnersRatingItem(0, 210, 0, 0, 50, 0, 1, False)],
            ["O1", qtypes.OwnersRatingItem(0, 210, 0, 0, 210, 0, 1, False)],
            ["O21", qtypes.OwnersRatingItem(0, 125, 0, 0, 100, 0, 1, False)],
            ["O22", qtypes.OwnersRatingItem(0, 125, 0, 0, 25, 0, 1, False)],
            ["O2", qtypes.OwnersRatingItem(0, 125, 0, 0, 125, 0, 1, False)],
        ]

        qserver_with_quotas.set_parent_owner("O22", "O1")

        assert qserver_with_quotas.owners_rating() == [
            ["O11", qtypes.OwnersRatingItem(0, 235, 0, 0, 160, 0, 1, False)],
            ["O12", qtypes.OwnersRatingItem(0, 235, 0, 0, 50, 0, 1, False)],
            ["O22", qtypes.OwnersRatingItem(0, 235, 0, 0, 25, 0, 1, False)],
            ["O1", qtypes.OwnersRatingItem(0, 235, 0, 0, 235, 0, 1, False)],
            ["O21", qtypes.OwnersRatingItem(0, 100, 0, 0, 100, 0, 1, False)],
            ["O2", qtypes.OwnersRatingItem(0, 100, 0, 0, 100, 0, 1, False)],
        ]

        qserver_with_quotas.set_parent_owner("O22", None)

        assert qserver_with_quotas.owners_rating() == [
            ["O11", qtypes.OwnersRatingItem(0, 210, 0, 0, 160, 0, 1, False)],
            ["O12", qtypes.OwnersRatingItem(0, 210, 0, 0, 50, 0, 1, False)],
            ["O1", qtypes.OwnersRatingItem(0, 210, 0, 0, 210, 0, 1, False)],
            ["O21", qtypes.OwnersRatingItem(0, 100, 0, 0, 100, 0, 1, False)],
            ["O2", qtypes.OwnersRatingItem(0, 100, 0, 0, 100, 0, 1, False)],
            ["O22", qtypes.OwnersRatingItem(0, 25, 0, 0, 25, 0, 1, False)],
        ]

        qserver_with_quotas.set_parent_owner("O22", "O1")

        assert qserver_with_quotas.owners_rating() == [
            ["O11", qtypes.OwnersRatingItem(0, 235, 0, 0, 160, 0, 1, False)],
            ["O12", qtypes.OwnersRatingItem(0, 235, 0, 0, 50, 0, 1, False)],
            ["O22", qtypes.OwnersRatingItem(0, 235, 0, 0, 25, 0, 1, False)],
            ["O1", qtypes.OwnersRatingItem(0, 235, 0, 0, 235, 0, 1, False)],
            ["O21", qtypes.OwnersRatingItem(0, 100, 0, 0, 100, 0, 1, False)],
            ["O2", qtypes.OwnersRatingItem(0, 100, 0, 0, 100, 0, 1, False)],
        ]

        qserver_with_quotas.set_quota("O11", 350)

        assert qserver_with_quotas.owners_rating() == [
            ["O11", qtypes.OwnersRatingItem(0, 425, 0, 0, 350, 0, 1, False)],
            ["O12", qtypes.OwnersRatingItem(0, 425, 0, 0, 50, 0, 1, False)],
            ["O22", qtypes.OwnersRatingItem(0, 425, 0, 0, 25, 0, 1, False)],
            ["O1", qtypes.OwnersRatingItem(0, 425, 0, 0, 425, 0, 1, False)],
            ["O21", qtypes.OwnersRatingItem(0, 100, 0, 0, 100, 0, 1, False)],
            ["O2", qtypes.OwnersRatingItem(0, 100, 0, 0, 100, 0, 1, False)],
        ]

        host_info = qtypes.HostInfo(
            capabilities=qtypes.ComputingResources(0, [], 32, 128 << 10),
            free=qtypes.ComputingResources()
        )
        job_id = uuid.uuid4().hex
        gen = qpop(qserver_with_quotas, "host", host_info=host_info, job_id=job_id)
        assert next(gen) == [11, 0]
        qcommit(gen)
        qserver_with_quotas.calculate_consumptions()

        assert qserver_with_quotas.owners_rating() == [
            ["O21", qtypes.OwnersRatingItem(0, 100, 0, 0, 100, 0, 1, False)],
            ["O2", qtypes.OwnersRatingItem(0, 100, 0, 0, 100, 0, 1, False)],
            ["O12", qtypes.OwnersRatingItem(15059, -5975, 0, 0, 50, 0, 1, False)],
            ["O22", qtypes.OwnersRatingItem(15059, -5975, 0, 0, 25, 0, 1, False)],
            ["O11", qtypes.OwnersRatingItem(15059, -5975, 0, 6400, 350, 1, 0, False)],
            ["O1", qtypes.OwnersRatingItem(15059, -5975, 0, 6400, 425, 1, 1, False)],
        ]

        saved_time = time.time
        now = time.time()
        monkeypatch.setattr(time, "time", lambda: now + 3600)
        qserver_with_quotas.execution_completed(job_id)
        qserver_with_quotas.calculate_consumptions()
        monkeypatch.setattr(time, "time", saved_time)

        assert qserver_with_quotas.owners_rating() == [
            ["O21", qtypes.OwnersRatingItem(0, 100, 0, 0, 100, 0, 1, False)],
            ["O2", qtypes.OwnersRatingItem(0, 100, 0, 0, 100, 0, 1, False)],
            ["O12", qtypes.OwnersRatingItem(2711, -727, 0, 0, 50, 0, 1, False)],
            ["O22", qtypes.OwnersRatingItem(2711, -727, 0, 0, 25, 0, 1, False)],
            ["O11", qtypes.OwnersRatingItem(2711, -727, 1152, 0, 350, 0, 0, False)],
            ["O1", qtypes.OwnersRatingItem(2711, -727, 1152, 0, 425, 0, 1, False)],
        ]

    def test__queue_by_host_with_quotas(self, qserver_with_data):
        dq = qtypes.DEFAULT_QUOTA
        assert qserver_with_data.owners_rating() == [
            ["O4", qtypes.OwnersRatingItem(0, dq, 0, 0, dq, 0, 1, True)],
            ["O3", qtypes.OwnersRatingItem(0, dq, 0, 0, dq, 0, 1, True)],
            ["O2", qtypes.OwnersRatingItem(0, dq, 0, 0, dq, 0, 1, True)],
            ["O1", qtypes.OwnersRatingItem(0, dq, 0, 0, dq, 0, 1, True)]
        ]

        queue = qserver_with_data.queue_by_host("host1")
        assert queue == [
            (2, -1, 4, 4),
            (2, -2, 3, 3),
            (3, -1, 2, 2),
            (1, -3, 1, 1)
        ]

        queue = qserver_with_data.queue_by_host("host2")
        assert queue == [
            (2, -2, 4, 4),
            (2, -1, 3, 3),
            (3, -2, 2, 2),
            (1, -2, 1, 1)
        ]

        queue = qserver_with_data.queue_by_host("host3")
        assert queue == [
            (3, -3, 2, 2),
            (1, -1, 1, 1)
        ]

        qserver_with_data.set_quota("O2", 100)
        qserver_with_data.set_quota("O3", 80)
        qserver_with_data.set_quota("O4", 90)
        qserver_with_data.set_quota("O1", 70)
        assert qserver_with_data.owners_rating() == [
            ["O2", qtypes.OwnersRatingItem(0, 100, 0, 0, 100, 0, 1, False)],
            ["O4", qtypes.OwnersRatingItem(0, 90, 0, 0, 90, 0, 1, False)],
            ["O3", qtypes.OwnersRatingItem(0, 80, 0, 0, 80, 0, 1, False)],
            ["O1", qtypes.OwnersRatingItem(0, 70, 0, 0, 70, 0, 1, False)]
        ]

        queue = qserver_with_data.queue_by_host("host1")
        assert queue == [
            (3, -1, 2, 2),
            (2, -1, 4, 4),
            (2, -2, 3, 3),
            (1, -3, 1, 1)
        ]

        queue = qserver_with_data.queue_by_host("host2")
        assert queue == [
            (3, -2, 2, 2),
            (2, -2, 4, 4),
            (2, -1, 3, 3),
            (1, -2, 1, 1)
        ]

        qserver_with_data.set_quota("O3", 95)
        assert qserver_with_data.owners_rating() == [
            ["O2", qtypes.OwnersRatingItem(0, 100, 0, 0, 100, 0, 1, False)],
            ["O3", qtypes.OwnersRatingItem(0, 95, 0, 0, 95, 0, 1, False)],
            ["O4", qtypes.OwnersRatingItem(0, 90, 0, 0, 90, 0, 1, False)],
            ["O1", qtypes.OwnersRatingItem(0, 70, 0, 0, 70, 0, 1, False)]
        ]

        queue = qserver_with_data.queue_by_host("host1")
        assert queue == [
            (3, -1, 2, 2),
            (2, -2, 3, 3),
            (2, -1, 4, 4),
            (1, -3, 1, 1)
        ]

        queue = qserver_with_data.queue_by_host("host2")
        assert queue == [
            (3, -2, 2, 2),
            (2, -1, 3, 3),
            (2, -2, 4, 4),
            (1, -2, 1, 1)
        ]

    def test__queue_by_task(self, qserver_with_data):
        queue = qserver_with_data.queue_by_task(666)
        assert queue == (None, None)

        queue = qserver_with_data.queue_by_task(1)
        assert queue == (
            ["host1", "host2", "host3"],
            (1, 1, [[3, 0], [2, 1], [1, 2]], 1, (None, None, 0, 0, 100, 0, None), None),
        )

        queue = qserver_with_data.queue_by_task(2)
        assert queue == (
            ["host1", "host2", "host3"],
            (2, 3, [[3, 2], [2, 1], [1, 0]], 2, (None, None, 1, 1, 101, 0, None), None),
        )

        queue = qserver_with_data.queue_by_task(3)
        assert queue == (
            ["host1", "host2", "host3"],
            (3, 2, [[2, 0], [1, 1]], 3, (None, None, 2, 2, 102, 0, None), None),
        )

        queue = qserver_with_data.queue_by_task(4)
        assert queue == (
            ["host1", "host2", "host3"],
            (4, 2, [[2, 1], [1, 0]], 4, (None, None, 3, 3, 103, 0, None), None),
        )

    def test__pop_0(self, qserver_with_data):
        qpop = server_utils.qpop
        assert not list(qpop(qserver_with_data, "non_existent"))

    def test__pop_1(self, qserver_with_data):
        qpop = server_utils.qpop
        qcommit = server_utils.qcommit
        assert list(qpop(qserver_with_data, "host1")) == [[4, 1], [3, 2], [2, 1], [1, 3]]
        gen = qpop(qserver_with_data, "host1")
        assert next(gen) == [4, 1]
        gen = qpop(qserver_with_data, "host1", job_id=uuid.uuid4().hex)
        assert next(gen) == [4, 1]
        qcommit(gen)
        gen = qpop(qserver_with_data, "host1")
        assert next(gen) == [3, 2]
        assert next(gen) == [2, 1]
        gen = qpop(qserver_with_data, "host1", job_id=uuid.uuid4().hex)
        assert next(gen) == [3, 2]
        qcommit(gen)
        gen = qpop(qserver_with_data, "host1", job_id=uuid.uuid4().hex)
        assert next(gen) == [2, 1]
        qcommit(gen)
        gen = qpop(qserver_with_data, "host1", job_id=uuid.uuid4().hex)
        assert next(gen) == [1, 3]
        qcommit(gen)
        assert not list(qpop(qserver_with_data, "host1"))

    def test__pop_1_with_quotas(self, qserver_with_data, test_queue):
        qpop = server_utils.qpop
        qcommit = server_utils.qcommit
        dq = qtypes.DEFAULT_QUOTA
        assert qserver_with_data.owners_rating() == [
            ["O4", qtypes.OwnersRatingItem(0, dq, 0, 0, dq, 0, 1, True)],
            ["O3", qtypes.OwnersRatingItem(0, dq, 0, 0, dq, 0, 1, True)],
            ["O2", qtypes.OwnersRatingItem(0, dq, 0, 0, dq, 0, 1, True)],
            ["O1", qtypes.OwnersRatingItem(0, dq, 0, 0, dq, 0, 1, True)]
        ]
        assert list(qpop(qserver_with_data, "host1")) == [[4, 1], [3, 2], [2, 1], [1, 3]]
        gen = qpop(qserver_with_data, "host1")
        assert next(gen) == [4, 1]
        gen = qpop(qserver_with_data, "host1", job_id=uuid.uuid4().hex)
        assert next(gen) == [4, 1]
        qcommit(gen)
        gen = qpop(qserver_with_data, "host1")
        assert next(gen) == [3, 2]
        assert next(gen) == [2, 1]
        gen = qpop(qserver_with_data, "host1", job_id=uuid.uuid4().hex)
        assert next(gen) == [3, 2]
        qcommit(gen)
        gen = qpop(qserver_with_data, "host1", job_id=uuid.uuid4().hex)
        assert next(gen) == [2, 1]
        qcommit(gen)
        gen = qpop(qserver_with_data, "host1", job_id=uuid.uuid4().hex)
        assert next(gen) == [1, 3]
        qcommit(gen)
        del gen
        assert not list(qpop(qserver_with_data, "host1"))

        server_utils.qserver_with_data_factory(qserver_with_data, test_queue)
        qserver_with_data.set_quota("O2", 100)
        qserver_with_data.set_quota("O3", 90)
        qserver_with_data.set_quota("O4", 80)
        qserver_with_data.set_quota("O1", 70)
        assert qserver_with_data.owners_rating() == [
            ["O2", qtypes.OwnersRatingItem(0, 100, 0, 0, 100, 0, 1, False)],
            ["O3", qtypes.OwnersRatingItem(0, 90, 0, 0, 90, 0, 1, False)],
            ["O4", qtypes.OwnersRatingItem(0, 80, 0, 0, 80, 0, 1, False)],
            ["O1", qtypes.OwnersRatingItem(0, 70, 0, 0, 70, 0, 1, False)]
        ]
        assert list(qpop(qserver_with_data, "host1")) == [[2, 1], [3, 2], [4, 1], [1, 3]]
        gen = qpop(qserver_with_data, "host1")
        assert next(gen) == [2, 1]
        gen = qpop(qserver_with_data, "host1", job_id=uuid.uuid4().hex)
        assert next(gen) == [2, 1]
        qcommit(gen)
        gen = qpop(qserver_with_data, "host1")
        assert next(gen) == [3, 2]
        assert next(gen) == [4, 1]
        gen = qpop(qserver_with_data, "host1", job_id=uuid.uuid4().hex)
        assert next(gen) == [3, 2]
        qcommit(gen)
        gen = qpop(qserver_with_data, "host1", job_id=uuid.uuid4().hex)
        assert next(gen) == [4, 1]
        qcommit(gen)
        gen = qpop(qserver_with_data, "host1", job_id=uuid.uuid4().hex)
        assert next(gen) == [1, 3]
        qcommit(gen)
        assert not list(qpop(qserver_with_data, "host1"))

    def test__quota_pools(self, qserver_with_data, test_queue, monkeypatch):
        qpop = server_utils.qpop
        qcommit = server_utils.qcommit
        dq = qtypes.DEFAULT_QUOTA

        clear_pools_cache = lambda: qserver_with_data._Server__state.quota_pools._QuotaPools__quota_pool_cache.clear()

        assert qtypes.QuotaPools.decode(qserver_with_data.quota_pools()) == qtypes.QuotaPools()
        qserver_with_data.add_quota_pool("POOL1", ["TAG1"])
        qserver_with_data.add_quota_pool("POOL2", ["TAG2"])

        default_rating = [
            ["O4", qtypes.OwnersRatingItem(0, dq, 0, 0, dq, 0, 1, True)],
            ["O3", qtypes.OwnersRatingItem(0, dq, 0, 0, dq, 0, 1, True)],
            ["O2", qtypes.OwnersRatingItem(0, dq, 0, 0, dq, 0, 1, True)],
            ["O1", qtypes.OwnersRatingItem(0, dq, 0, 0, dq, 0, 1, True)],
        ]

        default_rating_with_zero_quota = [
            ["O4", qtypes.OwnersRatingItem(qstate.inf, 0, 0, 0, 0, 0, 1, True)],
            ["O3", qtypes.OwnersRatingItem(qstate.inf, 0, 0, 0, 0, 0, 1, True)],
            ["O2", qtypes.OwnersRatingItem(qstate.inf, 0, 0, 0, 0, 0, 1, True)],
            ["O1", qtypes.OwnersRatingItem(qstate.inf, 0, 0, 0, 0, 0, 1, True)],
        ]

        assert qserver_with_data.owners_rating() == default_rating

        for pool in ("POOL1", "POOL2"):
            assert qserver_with_data.owners_rating(pool=pool) == []

        for owner in ("O1", "O2", "O3", "O4"):
            for pool in ("POOL1", "POOL2"):
                qserver_with_data.set_quota(owner, None, pool)
        assert qserver_with_data.owners_rating() == default_rating, pool
        for pool in ("POOL1", "POOL2"):
            assert qserver_with_data.owners_rating(pool=pool) == default_rating_with_zero_quota

        for tag in ("TAG", "TAG1", "TAG2"):
            host_info = qtypes.HostInfo(
                capabilities=qtypes.ComputingResources(disk_space=1),
                free=qtypes.ComputingResources(),
                tags=[tag]
            )
            clear_pools_cache()
            assert list(qpop(qserver_with_data, "host1", host_info=host_info)) == [[4, 1], [3, 2], [2, 1], [1, 3]]

        for owner, quota in ("O2", 100), ("O3", 90), ("O4", 80), ("O1", 70):
            qserver_with_data.set_quota(owner, quota, "POOL1")
        assert qserver_with_data.owners_rating() == default_rating
        assert qserver_with_data.owners_rating(pool="POOL2") == default_rating_with_zero_quota
        assert qserver_with_data.owners_rating(pool="POOL1") == [
            ["O2", qtypes.OwnersRatingItem(0, 100, 0, 0, 100, 0, 1, False)],
            ["O3", qtypes.OwnersRatingItem(0, 90, 0, 0, 90, 0, 1, False)],
            ["O4", qtypes.OwnersRatingItem(0, 80, 0, 0, 80, 0, 1, False)],
            ["O1", qtypes.OwnersRatingItem(0, 70, 0, 0, 70, 0, 1, False)],
        ]
        for owner, quota in ("O1", 100), ("O3", 90), ("O4", 80), ("O2", 70):
            qserver_with_data.set_quota(owner, quota, "POOL2")
        assert qserver_with_data.owners_rating(pool="POOL2") == [
            ["O1", qtypes.OwnersRatingItem(0, 100, 0, 0, 100, 0, 1, False)],
            ["O3", qtypes.OwnersRatingItem(0, 90, 0, 0, 90, 0, 1, False)],
            ["O4", qtypes.OwnersRatingItem(0, 80, 0, 0, 80, 0, 1, False)],
            ["O2", qtypes.OwnersRatingItem(0, 70, 0, 0, 70, 0, 1, False)],
        ]
        assert qserver_with_data.owners_rating() == default_rating

        for tag in "TAG", "TAG1", "TAG2":
            host_info = qtypes.HostInfo(
                capabilities=qtypes.ComputingResources(disk_space=1),
                free=qtypes.ComputingResources(),
                tags=[tag]
            )
            clear_pools_cache()
            assert list(qpop(qserver_with_data, "host1", host_info=host_info)) == [[4, 1], [3, 2], [2, 1], [1, 3]], tag

        monkeypatch.setattr(qserver_with_data._Server__quotas_config, "use_pools", True)
        for tag, queue in (
            ("TAG", [[4, 1], [3, 2], [2, 1], [1, 3]]),
            ("TAG1", [[2, 1], [3, 2], [4, 1], [1, 3]]),
            ("TAG2", [[1, 3], [3, 2], [4, 1], [2, 1]]),
        ):
            host_info = qtypes.HostInfo(
                capabilities=qtypes.ComputingResources(disk_space=1),
                free=qtypes.ComputingResources(),
                tags=[tag]
            )
            clear_pools_cache()
            assert list(qpop(qserver_with_data, "host1", host_info=host_info)) == queue, tag

        now = int(time.time())
        monkeypatch.setattr(time, "time", lambda: now)
        jobs = []
        for tag, item, cores in ("TAG", [4, 1], 1), ("TAG1", [2, 1], 2), ("TAG2", [1, 3], 3):
            host_info = qtypes.HostInfo(
                capabilities=qtypes.ComputingResources(disk_space=1, cores=cores),
                free=qtypes.ComputingResources(),
                tags=[tag]
            )
            clear_pools_cache()
            job_id = uuid.uuid4().hex
            gen = qpop(qserver_with_data, "host1", host_info=host_info, job_id=job_id)
            assert next(gen) == item
            qcommit(gen)
            jobs.append(job_id)
        a_bit_later = now + 10
        monkeypatch.setattr(time, "time", lambda: a_bit_later)
        qserver_with_data.execution_completed(jobs)
        qserver_with_data.calculate_consumptions()
        assert qserver_with_data.owners_rating() == [
            ["O3", qtypes.OwnersRatingItem(0, dq, 0, 0, dq, 0, 1, True)],
            ["O4", qtypes.OwnersRatingItem(41, dq - 100, 100, 0, dq, 0, 0, True)],
            ["O2", qtypes.OwnersRatingItem(81, dq - 200, 200, 0, dq, 0, 0, True)],
            ["O1", qtypes.OwnersRatingItem(122, dq - 300, 300, 0, dq, 0, 0, True)],
        ]
        assert qserver_with_data.owners_rating(pool="POOL1") == [
            ["O3", qtypes.OwnersRatingItem(0, 90, 0, 0, 90, 0, 1, False)],
            ["O4", qtypes.OwnersRatingItem(0, 80, 0, 0, 80, 0, 0, False)],
            ["O1", qtypes.OwnersRatingItem(0, 70, 0, 0, 70, 0, 0, False)],
            ["O2", qtypes.OwnersRatingItem(2000, -100, 200, 0, 100, 0, 0, False)],
        ]
        assert qserver_with_data.owners_rating(pool="POOL2") == [
            ["O3", qtypes.OwnersRatingItem(0, 90, 0, 0, 90, 0, 1, False)],
            ["O4", qtypes.OwnersRatingItem(0, 80, 0, 0, 80, 0, 0, False)],
            ["O2", qtypes.OwnersRatingItem(0, 70, 0, 0, 70, 0, 0, False)],
            ["O1", qtypes.OwnersRatingItem(3000, -200, 300, 0, 100, 0, 0, False)],
        ]

        qserver_with_data.update_quota_pool("POOL2", default=1000)
        _, (priority, hosts, task_info) = next(test_queue.iteritems())
        task_info = task_info._replace(owner="O5")
        hosts = sorted((h for h in hosts), key=lambda _: -_[0])
        qserver_with_data.push(5, priority, hosts, task_info)
        assert qserver_with_data.owners_rating(pool="POOL2") == [
            ["O5", qtypes.OwnersRatingItem(0, 1000, 0, 0, 1000, 0, 1, True)],
            ["O3", qtypes.OwnersRatingItem(0, 90, 0, 0, 90, 0, 1, False)],
            ["O4", qtypes.OwnersRatingItem(0, 80, 0, 0, 80, 0, 0, False)],
            ["O2", qtypes.OwnersRatingItem(0, 70, 0, 0, 70, 0, 0, False)],
            ["O1", qtypes.OwnersRatingItem(3000, -200, 300, 0, 100, 0, 0, False)],
        ]

        monkeypatch.setattr(qserver_with_data._Server__quotas_config, "use_pools", True)
        clear_pools_cache()
        host_info = host_info._replace(tags=["TAG1"])
        task_info = task_info._replace(owner="O6")
        assert list(qpop(qserver_with_data, "host1", host_info=host_info)) == [[3, 2], [5, 3]]
        qserver_with_data.push(6, priority, hosts, task_info)
        assert qserver_with_data.owners_rating(pool="POOL1") == [
            ["O3", qtypes.OwnersRatingItem(0, 90, 0, 0, 90, 0, 1, False)],
            ["O4", qtypes.OwnersRatingItem(0, 80, 0, 0, 80, 0, 0, False)],
            ["O1", qtypes.OwnersRatingItem(0, 70, 0, 0, 70, 0, 0, False)],
            ["O2", qtypes.OwnersRatingItem(2000, -100, 200, 0, 100, 0, 0, False)],
            ["O6", qtypes.OwnersRatingItem(qstate.inf, 0, 0, 0, 0, 0, 1, True)],
            ["O5", qtypes.OwnersRatingItem(qstate.inf, 0, 0, 0, 0, 0, 1, True)],
        ]
        assert list(qpop(qserver_with_data, "host1", host_info=host_info)) == [[3, 2], [6, 3], [5, 3]]
        qserver_with_data.update_quota_pool("POOL1", default=2000)
        task_info = task_info._replace(owner="O7")
        qserver_with_data.push(7, priority, hosts, task_info)
        assert qserver_with_data.owners_rating(pool="POOL1") == [
            ["O7", qtypes.OwnersRatingItem(0, 2000, 0, 0, 2000, 0, 1, True)],
            ["O3", qtypes.OwnersRatingItem(0, 90, 0, 0, 90, 0, 1, False)],
            ["O4", qtypes.OwnersRatingItem(0, 80, 0, 0, 80, 0, 0, False)],
            ["O1", qtypes.OwnersRatingItem(0, 70, 0, 0, 70, 0, 0, False)],
            ["O2", qtypes.OwnersRatingItem(2000, -100, 200, 0, 100, 0, 0, False)],
            ["O6", qtypes.OwnersRatingItem(qstate.inf, 0, 0, 0, 0, 0, 1, True)],
            ["O5", qtypes.OwnersRatingItem(qstate.inf, 0, 0, 0, 0, 0, 1, True)],
        ]
        assert list(qpop(qserver_with_data, "host1", host_info=host_info)) == [[7, 3], [3, 2], [6, 3], [5, 3]]

    def test__pop_2(self, qserver_with_data):
        qpop = server_utils.qpop
        qcommit = server_utils.qcommit
        for sample in ([4, 2], [3, 1], [2, 2], [1, 2]):
            gen = qpop(qserver_with_data, "host2", job_id=uuid.uuid4().hex)
            assert next(gen) == sample
            qcommit(gen)
        assert not list(qpop(qserver_with_data, "host2"))

    def test__pop_3(self, qserver_with_data):
        qpop = server_utils.qpop
        qcommit = server_utils.qcommit
        for sample in ([2, 3], [1, 1]):
            gen = qpop(qserver_with_data, "host3", job_id=uuid.uuid4().hex)
            assert next(gen) == sample
            qcommit(gen)
        assert not list(qpop(qserver_with_data, "host3"))

    def test__pop_4(self, qserver_with_data):
        qpop = server_utils.qpop
        qcommit = server_utils.qcommit
        for host, sample in (("host1", [4, 1]), ("host2", [3, 1]), ("host3", [2, 3]), ("host1", [1, 3])):
            gen = qpop(qserver_with_data, host, job_id=uuid.uuid4().hex)
            assert next(gen) == sample
            qcommit(gen)
        for host in ("host1", "host2", "host3"):
            assert not list(qpop(qserver_with_data, host))

    def test__push(self, qserver, test_queue):
        queue = list(qserver.queue())
        assert queue == [None, [], [], [], []]

        for task_id, (priority, hosts, task_info) in test_queue.iteritems():
            qserver.push(task_id, priority, sorted((h for h in hosts), key=lambda _: -_[0]), task_info)

        queue = list(qserver.queue())
        assert queue == [
            (2, 3, [[3, 2], [2, 1], [1, 0]], 2, (None, None, 1, 1, 101, 0, None), None),
            (3, 2, [[2, 0], [1, 1]], 3, (None, None, 2, 2, 102, 0, None), None),
            (4, 2, [[2, 1], [1, 0]], 4, (None, None, 3, 3, 103, 0, None), None),
            (1, 1, [[3, 0], [2, 1], [1, 2]], 1, (None, None, 0, 0, 100, 0, None), None),
            None,
            ["host1", "host2", "host3"],
            ["O1", "O2", "O3", "O4"],
            ["T1", "T2", "T3", "T4"],
            []
        ]

    def test__push_single_score(self, qserver, test_queue_with_single_score):
        queue = list(qserver.queue())
        assert queue == [None, [], [], [], []]

        tasks_host_bits = {}
        for task_id, (priority, hosts, task_info, score) in test_queue_with_single_score.items():
            all_hosts = qtypes.IndexedList.decode(qserver.add_hosts(hosts))
            bits = all_hosts.make_bits(hosts)[0]
            tasks_host_bits[task_id] = bits
            qserver.push(task_id, priority, bits, task_info, score)

        queue = list(qserver.queue())
        assert queue == [
            (2, 3, tasks_host_bits[2], 2, (None, None, 1, 1, 101, 0, None), 2),
            (3, 2, tasks_host_bits[3], 3, (None, None, 2, 2, 102, 0, None), 3),
            (4, 2, tasks_host_bits[4], 4, (None, None, 3, 3, 103, 0, None), 4),
            (1, 1, tasks_host_bits[1], 1, (None, None, 0, 0, 100, 0, None), 1),
            None,
            ["host1", "host2", "host3"],
            ["O1", "O2", "O3", "O4"],
            ["T1", "T2", "T3", "T4"],
            []
        ]

    def test__push_without_priority(self, qserver, test_queue):
        task_id, (priority, hosts, task_info) = next(test_queue.iteritems())
        hosts = sorted((h for h in hosts), key=lambda _: -_[0])
        qserver.push(task_id, priority, hosts, task_info)
        for _ in range(2):
            qserver.push(task_id, None, hosts, task_info)
            queue = qserver.queue_by_task(task_id)[1]
            assert queue[:3] == (task_id, priority, [[3, 0], [2, 1], [1, 2]])

    def test__pop_same_task_simultaneously(self, qserver_with_data, test_queue):
        qpop = server_utils.qpop
        qcommit = server_utils.qcommit
        assert list(qpop(qserver_with_data, "host1")) == [[4, 1], [3, 2], [2, 1], [1, 3]]
        assert list(qpop(qserver_with_data, "host2")) == [[4, 2], [3, 1], [2, 2], [1, 2]]

        gen1 = qpop(qserver_with_data, "host1", job_id=uuid.uuid4().hex)
        gen2 = qpop(qserver_with_data, "host2", job_id=uuid.uuid4().hex)

        assert next(gen1) == [4, 1]
        assert next(gen2) == [4, 2]

        assert qcommit(gen1) == qtypes.QueueIterationResult.ACCEPTED
        assert qcommit(gen2) == [3, 1]

    def test__validate(self, qserver_with_data):
        qpop = server_utils.qpop
        qcommit = server_utils.qcommit
        task_ids, jobs_ids = map(sorted, qserver_with_data.validate())
        assert task_ids, jobs_ids == [[1, 2, 3, 4], []]
        jobs_ids = [uuid.uuid4().hex for _ in task_ids]

        gen = qpop(qserver_with_data, "host1", job_id=jobs_ids[0])
        next(gen)
        qcommit(gen)
        assert sorted(qserver_with_data.validate()[0]) == [1, 2, 3]

        gen = qpop(qserver_with_data, "host2", job_id=jobs_ids[1])
        next(gen)
        qcommit(gen)
        assert sorted(qserver_with_data.validate()[0]) == [1, 2]

        gen = qpop(qserver_with_data, "host3", job_id=jobs_ids[2])
        next(gen)
        qcommit(gen)
        assert sorted(qserver_with_data.validate()[0]) == [1]

        gen = qpop(qserver_with_data, "host1", job_id=jobs_ids[3])
        next(gen)
        qcommit(gen)
        assert map(sorted, qserver_with_data.validate()) == [[], sorted(jobs_ids)]

    def test__lock_jobs(self, qserver_with_data):
        task_ids, jobs_ids = map(sorted, qserver_with_data.validate())
        assert task_ids, jobs_ids == [[1, 2, 3, 4], []]
        jobs_ids = [uuid.uuid4().hex for _ in task_ids]
        jobs_lock = qserver_with_data.lock_jobs(jobs_ids)
        next(jobs_lock)
        jobs = get_jobs(qserver_with_data, "host1", jobs_ids=jobs_ids)
        assert [_[0] for _ in jobs] == [4, 3, 2, 1]
        assert sorted(_[1] for _ in jobs) == sorted(jobs_ids)
        assert qserver_with_data.validate() == ([], [])

        jobs_lock.send(jobs[0][1])
        assert qserver_with_data.validate() == ([], [jobs[0][1]])

        jobs_lock.send(jobs[1][1])
        assert map(sorted, qserver_with_data.validate()) == [[], sorted([jobs[0][1], jobs[1][1]])]

        with pytest.raises(StopIteration):
            jobs_lock.send(None)
        assert map(sorted, qserver_with_data.validate()) == [[], sorted(_[1] for _ in jobs)]

    def test__ping(self, qserver):
        value = random.randint(1, 100)
        assert qserver.ping(value) == value

    def test__resources(self, qserver, test_queue):
        assert qserver.resources() == []
        all_resources = list(set(random.randint(0, 100) for _ in range(100)))
        task_resources = {tid: {random.choice(all_resources): 0 for _ in range(10)} for tid in range(1, 5)}
        used_resources = list(set(it.chain.from_iterable(task_resources.itervalues())))
        for task_id, (priority, hosts, task_info) in test_queue.iteritems():
            resources = task_resources[task_id]
            qserver.push(
                task_id,
                priority,
                sorted((qtypes.TaskQueueHostsItem(*h) for h in hosts), key=lambda _: -_.score),
                task_info=task_info._replace(requirements=qtypes.ComputingResources(resources=resources))
            )
        assert qserver.resources() == used_resources

    @pytest.mark.xfail(run=False)  # FIXME: SANDBOX-4737: Disk usage calculation has been disabled
    def test__requirements__disk_space(self, qserver, test_queue):
        qpop = server_utils.qpop
        disk_reqs = {1: 10, 2: 20, 3: 30}
        for task_id, (priority, hosts, task_info) in test_queue.iteritems():
            disk_req = disk_reqs.get(task_id)
            if disk_req is not None:
                qserver.push(
                    task_id,
                    priority,
                    sorted((qtypes.TaskQueueHostsItem(*h) for h in hosts), key=lambda _: -_.score),
                    task_info=task_info._replace(requirements=qtypes.ComputingResources(disk_req))
                )
        assert list(qpop(qserver, "host1")) == [[2, 1], [3, 2], [1, 3]]
        assert list(qpop(qserver, "host1", qtypes.ComputingResources())) == [[2, 1], [3, 2], [1, 3]]

        for disk_cap in range(0, 10):
            assert list(qpop(qserver, "host1", qtypes.ComputingResources(disk_cap))) == []
            assert list(qpop(qserver, "host1")) == []

        qserver.push(1, test_queue[1][0], None)
        assert list(qpop(qserver, "host1")) == []

        for disk_cap in range(10, 20):
            assert list(qpop(qserver, "host1", qtypes.ComputingResources(disk_cap))) == [[1, 3]]
            assert list(qpop(qserver, "host1")) == [[1, 3]]

        for disk_cap in range(20, 30):
            assert list(qpop(qserver, "host1", qtypes.ComputingResources(disk_cap))) == [[2, 1], [1, 3]]
            assert list(qpop(qserver, "host1")) == [[2, 1], [1, 3]]

        for disk_cap in range(30, 40):
            assert list(qpop(qserver, "host1", qtypes.ComputingResources(disk_cap))) == [[2, 1], [3, 2], [1, 3]]
            assert list(qpop(qserver, "host1")) == [[2, 1], [3, 2], [1, 3]]

        task_id = 4
        priority, hosts, task_info = test_queue[task_id]
        disk_req = 40
        qserver.push(
            task_id,
            priority,
            sorted((qtypes.TaskQueueHostsItem(*h) for h in hosts), key=lambda _: -_.score),
            task_info=task_info._replace(requirements=qtypes.ComputingResources(disk_req))
        )
        assert list(qpop(qserver, "host1")) == [[2, 1], [3, 2], [1, 3]]
        assert list(qpop(qserver, "host2")) == [[2, 2], [4, 2], [3, 1], [1, 2]]
        assert list(
            qpop(qserver, "host1", qtypes.ComputingResources(disk_req))
        ) == [[2, 1], [3, 2], [4, 1], [1, 3]]
        qserver.push(task_id, None, None)
        assert list(qpop(qserver, "host1")) == [[2, 1], [3, 2], [1, 3]]
        qserver.push(
            task_id,
            priority,
            sorted((qtypes.TaskQueueHostsItem(*h) for h in hosts), key=lambda _: -_.score),
            task_info=task_info._replace(requirements=qtypes.ComputingResources(disk_req))
        )
        assert list(qpop(qserver, "host1")) == [[2, 1], [3, 2], [4, 1], [1, 3]]

    @pytest.mark.xfail(run=False)  # FIXME: SANDBOX-4737: Disk usage calculation has been disabled
    def test__requirements__resources(self, qserver, test_queue):
        qpop = server_utils.qpop

        def push(task_resources, disk_space=None):
            for task_id, (priority, hosts) in test_queue.iteritems():
                qserver.push(
                    task_id,
                    priority,
                    sorted((qtypes.TaskQueueHostsItem(0, h[1]) for h in hosts), key=lambda _: -_.score),
                    requirements=qtypes.ComputingResources(
                        resources=task_resources.get(task_id), disk_space=disk_space
                    )
                )

        regular_pop_sequence = [[2, 0], [3, 0], [4, 0], [1, 0]]
        altered_pop_sequence = [[2, 0], [4, 0], [3, 0], [1, 0]]
        res = {1: 10, 2: 15, 3: 20, 4: 30}  # {<resource id>: <resource size>}

        push({})

        assert list(qpop(qserver, "host1")) == regular_pop_sequence

        for rids in it.chain.from_iterable(it.combinations(res, _) for _ in range(1, len(res) + 1)):
            req = qtypes.ComputingResources(resources={_: res[_] for _ in rids})
            assert list(qpop(qserver, "host1", req)) == regular_pop_sequence

        push({3: {_: res[_] for _ in (4,)}, 4: {_: res[_] for _ in (1, 2, 3)}})

        for rids in ([1], [2], [1, 2], [1, 3], [2, 3, 4]):
            req = qtypes.ComputingResources(resources={_: res[_] for _ in rids})
            assert list(qpop(qserver, "host1", req)) == altered_pop_sequence
            assert list(qpop(qserver, "host1")) == altered_pop_sequence

        for rids in ([4], [1, 4], [2, 4], [3, 4], [1, 2, 4], [1, 3, 4]):
            req = qtypes.ComputingResources(resources={_: res[_] for _ in rids})
            assert list(qpop(qserver, "host1", req)) == regular_pop_sequence
            assert list(qpop(qserver, "host1")) == regular_pop_sequence

        assert list(qpop(qserver, "host2")) == regular_pop_sequence

        push({})
        req = qtypes.ComputingResources(resources={_: res[_] for _ in [2, 3, 4]})
        assert list(qpop(qserver, "host1", req)) == regular_pop_sequence
        push({3: {_: res[_] for _ in (4,)}, 4: {_: res[_] for _ in (1, 2, 3)}})
        assert list(qpop(qserver, "host1")) == altered_pop_sequence

        k10 = 10 << 10
        k20 = 20 << 10
        k30 = 30 << 10

        qserver.sync(
            [
                [1, 0, [[0, "host1"]], qtypes.ComputingResources(disk_space=0, resources={1: k10})],
                [2, 1, [[0, "host1"]], qtypes.ComputingResources(disk_space=0, resources={2: k20})],
                [3, 2, [[0, "host1"]], qtypes.ComputingResources(disk_space=0, resources={3: k30})],
            ],
            reset=True
        )

        assert list(qpop(qserver, "host1")) == [[3, 0], [2, 0], [1, 0]]

        assert list(
            qpop(qserver, "host1", qtypes.ComputingResources(disk_space=0, resources={1: k10}))
        ) == [[1, 0]]
        assert list(
            qpop(qserver, "host1", qtypes.ComputingResources(disk_space=10, resources={1: k10}))
        ) == [[1, 0]]
        assert list(
            qpop(qserver, "host1", qtypes.ComputingResources(disk_space=20, resources={1: k10}))
        ) == [[2, 0], [1, 0]]
        assert list(
            qpop(qserver, "host1", qtypes.ComputingResources(disk_space=30, resources={1: k10}))
        ) == [[3, 0], [2, 0], [1, 0]]

        assert list(
            qpop(qserver, "host1", qtypes.ComputingResources(disk_space=0, resources={1: k10, 2: k20}))
        ) == [[2, 0], [1, 0]]
        assert list(
            qpop(qserver, "host1", qtypes.ComputingResources(disk_space=10, resources={1: k10, 2: k20}))
        ) == [[2, 0], [1, 0]]
        assert list(
            qpop(qserver, "host1", qtypes.ComputingResources(disk_space=20, resources={1: k10, 2: k20}))
        ) == [[2, 0], [1, 0]]
        assert list(
            qpop(qserver, "host1", qtypes.ComputingResources(disk_space=30, resources={1: k10, 2: k20}))
        ) == [[3, 0], [2, 0], [1, 0]]

        assert list(
            qpop(qserver, "host1", qtypes.ComputingResources(disk_space=0, resources={1: k10, 2: k20, 3: k30}))
        ) == [[3, 0], [2, 0], [1, 0]]

    def test__snapshot(self, qserver, monkeypatch):
        operations = [(_, 0, [], qtypes.TaskInfo(owner=0)) for _ in range(1, 5)]
        encode = qstate.PersistentState.encode
        monkeypatch.setattr(
            qstate.PersistentState,
            encode.__name__,
            lambda *_: (gevent.sleep(2), encode(*_))[1]
        )
        monkeypatch.setattr(qstate, "MAX_OPLOG_SIZE", len(operations) - 1)
        result = []
        pid = os.getpid()
        greenlet = gevent.spawn(lambda: map(result.append, qserver.snapshot()))
        gevent.sleep(1)
        if pid == os.getpid():
            qserver._Server__state.owners.append(0)
            qserver._Server__state.quotas[0] = {0: [0, 0, 0]}
            for operation in operations[:-1]:
                qserver.push(*operation)
        greenlet.join()
        snapshot1_id = result[0][0]
        assert snapshot1_id == 1
        unpacker = msgpack.Unpacker()
        unpacker.feed("".join(result[1:]))
        operation_id, snapshot = list(unpacker)
        assert list(encode(qstate.PersistentState())) == snapshot
        assert operation_id == 0
        oplog_gen1 = qserver.oplog(snapshot1_id, None)
        operation_id, oplog = next(oplog_gen1)
        assert operation_id == len(operations) - 1
        for i, operation in enumerate(oplog):
            assert operation.operation_id == i + 1
            assert operation.args == [
                (arg.encode() if isinstance(arg, qtypes.Serializable) else arg) for arg in operations[i]
            ] + [None]
        gen = qserver.snapshot()
        snapshot2_id = next(gen)[0]
        assert snapshot2_id == 2
        unpacker = msgpack.Unpacker()
        unpacker.feed("".join(gen))
        assert [0, list(encode(qstate.PersistentState()))] == list(unpacker)
        assert next(qserver.oplog(snapshot2_id, None))[0] == len(operations) - 1
        qserver.push(*operations[-1])
        operation_id, oplog = next(oplog_gen1)
        oplog_gen1.close()
        assert operation_id == len(operations)
        operations_checksum = None
        for i, operation in enumerate(oplog, len(operations) - 1):
            operations_checksum = operation.checksum
            assert operation.operation_id == i + 1
            assert operation.args == [
                (arg.encode() if isinstance(arg, qtypes.Serializable) else arg) for arg in operations[i]
            ] + [None]
        with pytest.raises(qerrors.QOutdated):
            next(qserver.oplog(snapshot2_id, None))
        gen = qserver.snapshot()
        snapshot3_id = next(gen)[0]
        assert snapshot3_id == 3
        unpacker = msgpack.Unpacker()
        unpacker.feed("".join(gen))
        snapshot_operation_id, snapshot = list(unpacker)
        assert snapshot_operation_id == operation_id
        task_queue_item = msgpack.loads(msgpack.dumps(qtypes.TaskInfo(owner=0)))
        assert snapshot == [
            len(operations),
            {0: [[_, 0, [], _, task_queue_item, None] for _ in range(1, len(operations) + 1)]},
            {}, [], {}, {}, {}, [], {}, [0], [], {0: {0: 0}}, {}, {}, [], [],
            {}, {}, [], {}, [], {}, operations_checksum, None, {}, [[], {}, {}]
        ]

    def test__stalled_snapshot(self, qserver, monkeypatch):
        def make_snapshot():
            gevent.sleep(2)
            return "fake data"

        operations = [(_, 0, [], qtypes.TaskInfo(owner=0)) for _ in range(1, 9)]
        monkeypatch.setattr(qserver, "_Server__make_snapshot", make_snapshot)
        monkeypatch.setattr(qstate, "MAX_OPLOG_SIZE", 3)
        monkeypatch.setattr(qstate.LocalState, "SNAPSHOT_WATCHDOG_TIMEOUT", 3)
        state = qserver._Server__state
        state.owners.append(0)
        state.quotas[0] = {0: [0, 0, 0]}
        for operation in operations[:3]:
            qserver.push(*operation)
        assert [op.operation_id for op in state.common_oplog] == [1, 2, 3]

        greenlet = gevent.spawn(lambda: list(qserver.snapshot()))
        gevent.sleep(1)
        qserver.push(*operations[3])
        assert [op.operation_id for op in state.common_oplog] == [2, 3, 4]
        for operation in operations[4:-1]:
            qserver.push(*operation)
        greenlet.join()
        assert [op.operation_id for op in state.common_oplog] == [4, 5, 6, 7]

        gen = qserver.snapshot(1, state.operations_checksum)
        snapshot_id = next(gen)[0]
        assert snapshot_id == 2

        gevent.sleep(qstate.LocalState.SNAPSHOT_WATCHDOG_TIMEOUT + 1)
        qserver.push(*operations[-1])
        assert [op.operation_id for op in state.common_oplog] == [6, 7, 8]

    def test__task_wait_semaphore(self, qserver):
        qpop = server_utils.qpop
        qcommit = server_utils.qcommit
        owner = "OWNER"
        host = "host"
        semaphores = ctt.Semaphores(acquires=[ctt.Semaphores.Acquire(name="test_sem", capacity=1)])
        tids = [1, 2]
        for tid in tids:
            qserver.push(
                tid, 0, [qtypes.TaskQueueHostsItem(0, host)],
                task_info=qtypes.TaskInfo(semaphores=semaphores, owner=owner)
            )
        tids.append(3)
        qserver.push(
            3, 0, [qtypes.TaskQueueHostsItem(0, host)],
            task_info=qtypes.TaskInfo(owner=owner)
        )
        assert qserver.queue_by_host(host) == [(0, 0, tid, tid) for tid in tids]
        gen = qpop(qserver, host, job_id=uuid.uuid4().hex)
        assert next(gen) == [1, 0]
        qcommit(gen)
        assert qserver.queue_by_host(host) == [(0, 0, tid, tid) for tid in tids[1:]]
        host_info = qtypes.HostInfo(
            capabilities=qtypes.ComputingResources(disk_space=1),
            free=qtypes.ComputingResources(),
        )
        gen = qserver.task_to_execute_it(host, host_info)
        assert next(gen) == [3, 0]
        with pytest.raises(StopIteration) as summary:
            next(gen)
        blockers = collections.defaultdict(dict)
        blockers[2] = {1: 1}
        assert summary.value.message == [
            blockers,
            {
                "skipped_due_disk_space": 0,
                "skipped_due_cores": 0,
                "skipped_due_ram": 0,
                "blocked_by_semaphores": 1,
            },
            17
        ]

        g = qpop(qserver, host, job_id=uuid.uuid4().hex)
        assert next(g) == [3, 0]
        assert qserver.semaphore_waiters(tids) == []
        qcommit(g)
        assert qserver.semaphore_waiters(tids) == [2]

    def test__task_wait_semaphore_after_reenqueue(self, qserver):
        qpop = server_utils.qpop
        qcommit = server_utils.qcommit
        owner = "OWNER"
        host = "host"
        tid1 = 1
        tid2 = 2
        sid = 1
        semaphores = ctt.Semaphores(acquires=[ctt.Semaphores.Acquire(name="test_sem", capacity=1)])
        qserver.push(
            tid2, 0, [qtypes.TaskQueueHostsItem(0, host)],
            task_info=qtypes.TaskInfo(semaphores=semaphores, owner=owner)
        )

        sems = {sid: (sem.value, sem.tasks) for sid, sem in qserver.semaphores()}
        assert sems == {sid: (0, {})}

        job_id = uuid.uuid4().hex
        gen = qpop(qserver, host, job_id=job_id)
        assert next(gen) == [tid2, 0]
        qcommit(gen)

        sems = {sid: (sem.value, sem.tasks) for sid, sem in qserver.semaphores()}
        assert sems == {sid: (1, {tid2: 1})}

        qserver.execution_completed(job_id)
        for tid in (tid1, tid2):
            qserver.push(
                tid, 0, [qtypes.TaskQueueHostsItem(0, host)],
                task_info=qtypes.TaskInfo(semaphores=semaphores, owner=owner)
            )

        sems = {sid: (sem.value, sem.tasks) for sid, sem in qserver.semaphores()}
        assert sems == {sid: (1, {tid2: 1})}

        host_info = qtypes.HostInfo(
            capabilities=qtypes.ComputingResources(disk_space=1),
            free=qtypes.ComputingResources(),
        )
        gen = qserver.task_to_execute_it(host, host_info)
        assert next(gen) == [tid2, 0]
        with pytest.raises(StopIteration) as summary:
            next(gen)
        blockers = collections.defaultdict(dict, {tid1: {sid: 1}})
        assert summary.value.message == [
            blockers,
            {
                "skipped_due_disk_space": 0,
                "skipped_due_cores": 0,
                "skipped_due_ram": 0,
                "blocked_by_semaphores": 1,
            },
            19
        ]

    def test__getting_tasks_while_releasing_semaphore(self, qserver):
        qpop = server_utils.qpop
        qcommit = server_utils.qcommit
        owner = "OWNER"
        host = "host"
        semaphores = ctt.Semaphores(acquires=[ctt.Semaphores.Acquire(name="test_sem", capacity=1)])
        tids = [1, 2]
        for tid in tids:
            qserver.push(
                tid, 0, [qtypes.TaskQueueHostsItem(0, host)],
                task_info=qtypes.TaskInfo(semaphores=semaphores, owner=owner)
            )
        tids.append(3)
        qserver.push(
            3, 0, [qtypes.TaskQueueHostsItem(0, host)],
            task_info=qtypes.TaskInfo(owner=owner)
        )

        gen = qpop(qserver, host, job_id=uuid.uuid4().hex)
        assert next(gen) == [1, 0]
        qcommit(gen)
        assert qserver.semaphore_waiters(tids) == []

        gen = qpop(qserver, host, job_id=uuid.uuid4().hex)
        assert next(gen) == [3, 0]
        assert qserver.release_semaphores(1, ctt.Status.SUCCESS, ctt.Status.SUCCESS)
        qcommit(gen)
        assert qserver.semaphore_waiters(tids) == [2]
        gen = qpop(qserver, host)
        assert next(gen) == [2, 0]
        assert qserver.semaphore_waiters(tids) == [2]
        qcommit(gen)
        assert qserver.semaphore_waiters(tids) == []

    def test__semaphore_blockers(self, qserver):
        qpop = server_utils.qpop
        qcommit = server_utils.qcommit
        owner = "OWNER"
        host = "host"
        samples = {
            1: ctt.Semaphores(acquires=[ctt.Semaphores.Acquire(name="test_sem", capacity=2)]),
            2: None,
            3: ctt.Semaphores(acquires=[ctt.Semaphores.Acquire(name="test_sem")]),
            4: ctt.Semaphores(acquires=[ctt.Semaphores.Acquire(name="test_sem", weight=2)]),
            5: ctt.Semaphores(acquires=[ctt.Semaphores.Acquire(name="test_sem", weight=3)]),
            6: ctt.Semaphores(acquires=[ctt.Semaphores.Acquire(name="test_sem")]),
            7: ctt.Semaphores(acquires=[ctt.Semaphores.Acquire(name="test_sem")]),
        }
        tids = samples.keys()
        for tid, sem in samples.items():
            qserver.push(
                tid, 0, [qtypes.TaskQueueHostsItem(0, host)],
                task_info=qtypes.TaskInfo(semaphores=sem, owner=owner)
            )
        qserver.push(
            8, 0, [qtypes.TaskQueueHostsItem(0, host)],
            task_info=qtypes.TaskInfo(
                semaphores=ctt.Semaphores(acquires=[ctt.Semaphores.Acquire(name="test_sem", weight=3)]),
                owner=owner,
                requirements=qtypes.ComputingResources(disk_space=100500),
            )
        )
        tids.append(8)
        assert qserver._Server__state.semaphore_blockers.size(1) == 0
        assert list(qpop(qserver, host, job_id=uuid.uuid4().hex)) == [[1, 0], [2, 0], [3, 0], [4, 0], [6, 0], [7, 0]]
        assert sorted(qserver.semaphore_waiters(tids)) == [5, 8]
        assert qserver._Server__state.semaphore_blockers.size(1) == 6

        for tid in (1, 2, 3):
            gen = qpop(qserver, host, job_id=uuid.uuid4().hex)
            assert next(gen) == [tid, 0]
            qcommit(gen)
            assert sorted(qserver.semaphore_waiters(tids)) == [5, 8]
            assert qserver._Server__state.semaphore_blockers.size(1) == 6

        assert list(qpop(qserver, host, job_id=uuid.uuid4().hex)) == []
        qcommit(gen)
        assert sorted(qserver.semaphore_waiters(tids)) == [4, 5, 6, 7, 8]
        assert qserver._Server__state.semaphore_blockers.size(1) == 10

        qserver.push(7, None, None)
        assert list(qpop(qserver, host, job_id=uuid.uuid4().hex)) == []
        qcommit(gen)
        assert sorted(qserver.semaphore_waiters(tids)) == [4, 5, 6, 8]
        assert qserver._Server__state.semaphore_blockers.size(1) == 9

        qserver.update_semaphore(1, dict(capacity=3))
        assert sorted(qserver.semaphore_waiters(tids)) == [4, 5, 6, 8]
        assert qserver._Server__state.semaphore_blockers.size(1) == 9
        gen = qpop(qserver, host, job_id=uuid.uuid4().hex)
        assert next(gen) == [6, 0]
        qcommit(gen)
        assert sorted(qserver.semaphore_waiters(tids)) == [4, 5, 8]
        assert qserver._Server__state.semaphore_blockers.size(1) == 8

        assert list(qpop(qserver, host, job_id=uuid.uuid4().hex)) == []
        assert sorted(qserver.semaphore_waiters(tids)) == [4, 5, 8]
        assert qserver._Server__state.semaphore_blockers.size(1) == 8

        host_info = qtypes.HostInfo(
            capabilities=qtypes.ComputingResources(disk_space=100500),
            free=qtypes.ComputingResources(),
        )
        qserver.update_semaphore(1, dict(capacity=6))
        gen = qpop(qserver, host, job_id=uuid.uuid4().hex, host_info=host_info)

        assert list(gen) == [[4, 0]]
        assert sorted(qserver.semaphore_waiters(tids)) == [4, 5, 8]
        assert qserver._Server__state.semaphore_blockers.size(1) == 8

    def test__reenqueue_task_with_removed_semaphores(self, qserver):
        qpop = server_utils.qpop
        qcommit = server_utils.qcommit
        owner = "OWNER"
        host = "host"
        semaphores = ctt.Semaphores(acquires=[ctt.Semaphores.Acquire(name="test_sem", capacity=1)])
        tids = (1, 2)
        for tid in tids:
            qserver.push(
                tid, 0, [qtypes.TaskQueueHostsItem(0, host)],
                task_info=qtypes.TaskInfo(semaphores=semaphores, owner=owner)
            )
        qserver.push(1, None, None)
        gen = qpop(qserver, host, job_id=uuid.uuid4().hex)
        assert next(gen) == [2, 0]
        qcommit(gen)
        assert qserver.semaphore_waiters(tids) == []
        qserver.push(
            1, 0, [qtypes.TaskQueueHostsItem(0, host)],
            task_info=qtypes.TaskInfo(semaphores=None, owner=owner)
        )
        assert list(qpop(qserver, host)) == [[1, 0]]
        assert qserver.semaphore_waiters(tids) == []
        qserver.push(2, None, None)
        assert qserver.release_semaphores(2, ctt.Status.SUCCESS, ctt.Status.SUCCESS)
        assert qserver.semaphore_waiters(tids) == []
        assert list(qpop(qserver, host)) == [[1, 0]]
        assert qserver.semaphore_waiters(tids) == []

    def test__rerun_task_with_changed_semaphores(self, qserver):
        qpop = server_utils.qpop
        qcommit = server_utils.qcommit
        owner = "OWNER"
        host = "host"
        tid = 1
        sid1 = 1
        sid2 = 2
        sids = [sid1, sid2]
        semaphores1 = ctt.Semaphores(
            acquires=[
                ctt.Semaphores.Acquire(name="test_sem1", capacity=1),
                ctt.Semaphores.Acquire(name="test_sem2", capacity=1)
            ]
        )
        semaphores2 = ctt.Semaphores(
            acquires=[
                ctt.Semaphores.Acquire(name="test_sem1", capacity=1)
            ]
        )
        qserver.push(
            tid, 0, [qtypes.TaskQueueHostsItem(0, host)],
            task_info=qtypes.TaskInfo(semaphores=semaphores1, owner=owner)
        )
        assert dict(qserver.semaphore_wanting(sids)) == {sid1: [tid], sid2: [tid]}

        job_id = uuid.uuid4().hex
        gen = qpop(qserver, host, job_id=job_id)
        assert next(gen) == [tid, 0]
        qcommit(gen)
        sems = {sid: (sem.value, sem.tasks) for sid, sem in qserver.semaphores()}
        assert sems == {sid1: (1, {tid: 1}), sid2: (1, {tid: 1})}
        assert dict(qserver.semaphore_wanting(sids)) == {}

        qserver.execution_completed(job_id)
        qserver.push(
            tid, 0, [qtypes.TaskQueueHostsItem(0, host)],
            task_info=qtypes.TaskInfo(semaphores=semaphores2, owner=owner)
        )
        sems = {sid: (sem.value, sem.tasks) for sid, sem in qserver.semaphores()}
        assert sems == {sid1: (0, {}), sid2: (0, {})}
        assert dict(qserver.semaphore_wanting(sids)) == {sid1: [tid]}

    def test__rerun_task_with_removed_semaphores(self, qserver):
        qpop = server_utils.qpop
        qcommit = server_utils.qcommit
        owner = "OWNER"
        host = "host"
        semaphores = ctt.Semaphores(acquires=[ctt.Semaphores.Acquire(name="test_sem", capacity=1)])
        qserver.push(
            1, 0, [qtypes.TaskQueueHostsItem(0, host)],
            task_info=qtypes.TaskInfo(semaphores=semaphores, owner=owner)
        )
        job_id = uuid.uuid4().hex
        gen = qpop(qserver, host, job_id=job_id)
        assert next(gen) == [1, 0]
        qcommit(gen)

        sems = dict(qserver.semaphores())
        assert len(sems) == 1
        sem = sems.values()[0]
        assert sem.value == 1
        assert sem.tasks == {1: 1}

        assert qserver.semaphore_waiters(1) == []
        qserver.execution_completed(job_id)

        sems = dict(qserver.semaphores())
        assert len(sems) == 1
        sem = sems.values()[0]
        assert sem.value == 1
        assert sem.tasks == {1: 1}

        qserver.push(
            1, 0, [qtypes.TaskQueueHostsItem(0, host)],
            task_info=qtypes.TaskInfo(semaphores=None, owner=owner)
        )

        sems = dict(qserver.semaphores())
        assert len(sems) == 1
        sem = sems.values()[0]
        assert sem.value == 0
        assert sem.tasks == {}

        assert list(qpop(qserver, host)) == [[1, 0]]
        assert qserver.semaphore_waiters(1) == []

        sems = dict(qserver.semaphores())
        assert len(sems) == 1
        sem = sems.values()[0]
        assert sem.value == 0
        assert sem.tasks == {}

    def test__repeat_semaphore_acquiring(self, qserver):
        qpop = server_utils.qpop
        qcommit = server_utils.qcommit
        task_owner = "OWNER"
        task_id = 1
        task_priority = 0
        task_semaphores = ctt.Semaphores(acquires=[ctt.Semaphores.Acquire(name="test_sem", capacity=1)])
        # with semaphores
        qserver.push(
            task_id,
            task_priority,
            [qtypes.TaskQueueHostsItem(0, "host")],
            task_info=qtypes.TaskInfo(semaphores=task_semaphores, owner=task_owner)
        )
        sem_waiting = dict(qserver.semaphore_wanting())
        assert len(sem_waiting) == 1
        sem_ids = sem_waiting.keys()
        assert dict(qserver.semaphore_wanting(sem_ids)) == {sem_ids[0]: [task_id]}
        # update of the task in queue should not reset semaphores
        qserver.push(
            task_id,
            task_priority,
            None
        )
        assert dict(qserver.semaphore_wanting(sem_ids)) == {sem_ids[0]: [task_id]}
        job_id = uuid.uuid4().hex
        gen = qpop(qserver, "host", job_id=job_id)
        assert next(gen) == [task_id, 0]
        qcommit(gen)
        assert qserver.semaphore_values(sem_ids) == [1]
        qserver.release_semaphores(task_id, ctt.Status.SUCCESS, ctt.Status.SUCCESS)
        assert qserver.semaphore_values(sem_ids) == [0]
        qserver.execution_completed(job_id)

        # without semaphores
        qserver.push(
            task_id,
            task_priority,
            [qtypes.TaskQueueHostsItem(0, "host")],
            task_info=qtypes.TaskInfo(owner=task_owner)
        )
        gen = qpop(qserver, "host", job_id=uuid.uuid4().hex)
        assert next(gen) == [task_id, 0]
        qcommit(gen)
        assert qserver.semaphore_values(sem_ids) == [0]

    def test__semaphore_acquiring_with_job_conflict(self, qserver):
        qpop = server_utils.qpop
        qcommit = server_utils.qcommit
        task_owner = "OWNER"
        task_priority = 0
        task_id = 1

        qserver.push(
            task_id,
            task_priority,
            [qtypes.TaskQueueHostsItem(0, "host")],
            task_info=qtypes.TaskInfo(owner=task_owner)
        )
        task_job_id = uuid.uuid4().hex
        gen = qpop(qserver, "host", job_id=task_job_id)
        assert next(gen) == [task_id, 0]
        qcommit(gen)

        task_with_sem_id = 2
        task_with_sem_semaphores = ctt.Semaphores(
            acquires=[ctt.Semaphores.Acquire(name="test_sem", capacity=1)]
        )
        qserver.push(
            task_with_sem_id,
            task_priority,
            [qtypes.TaskQueueHostsItem(0, "host")],
            task_info=qtypes.TaskInfo(semaphores=task_with_sem_semaphores, owner=task_owner)
        )
        task_with_sem_job_id = uuid.uuid4().hex
        gen = qpop(qserver, "host", job_id=task_with_sem_job_id)
        assert next(gen) == [task_with_sem_id, 0]
        qcommit(gen)
        sems = dict(qserver.semaphores())
        assert len(sems) == 1
        assert sems.values()[0].value == 1
        sem_ids = sems.keys()
        assert qserver.semaphore_values(sem_ids) == [1]
        qserver.execution_completed(task_with_sem_job_id)

        task_with_sem_job_id2 = uuid.uuid4().hex
        qserver.push(
            task_with_sem_id,
            task_priority,
            [qtypes.TaskQueueHostsItem(0, "host")],
            task_info=qtypes.TaskInfo(semaphores=task_with_sem_semaphores, owner=task_owner)
        )
        assert qserver.semaphore_values(sem_ids) == [1]
        gen = qpop(qserver, "host", job_id=task_with_sem_job_id2)
        assert next(gen) == [task_with_sem_id, 0]
        qcommit(gen)
        assert qserver.semaphore_values(sem_ids) == [1]

        qserver.execution_completed(task_with_sem_job_id2)
        qserver.release_semaphores(task_with_sem_id, None, None)
        assert qserver.semaphore_values(sem_ids) == [0]

        qserver.push(
            task_with_sem_id,
            task_priority,
            [qtypes.TaskQueueHostsItem(0, "host")],
            task_info=qtypes.TaskInfo(semaphores=task_with_sem_semaphores, owner=task_owner)
        )
        assert qserver.semaphore_values(sem_ids) == [0]
        gen = qpop(qserver, "host", job_id=task_job_id)
        assert next(gen) == [task_with_sem_id, 0]
        qcommit(gen)
        assert qserver.semaphore_values(sem_ids) == [0]
        gen = qpop(qserver, "host", job_id=task_job_id)
        assert next(gen) == [task_with_sem_id, 0]  # task stays in queue due of job conflict
        assert qserver.semaphore_values(sem_ids) == [0]

    def test__reuse_job_id(self, qserver, monkeypatch):
        qpop = server_utils.qpop
        qcommit = server_utils.qcommit
        ttl = 1
        monkeypatch.setattr(qstate, "RECENTLY_EXECUTED_JOBS_TTL", ttl)
        owner1 = "OWNER1"
        owner2 = "OWNER2"
        for i in range(1, 4):
            qserver.push(
                i, 0, [qtypes.TaskQueueHostsItem(0, "host")],
                task_info=qtypes.TaskInfo(owner=owner1 if i == 1 else owner2)
            )
        qserver.set_quota(owner1, 2)
        qserver.set_quota(owner2, 1)

        job_id1 = uuid.uuid4().hex
        job_id2 = uuid.uuid4().hex

        gen = qpop(qserver, "host", job_id=job_id1)
        assert next(gen) == [1, 0]
        qcommit(gen)

        gen = qpop(qserver, "host", job_id=job_id2)
        assert next(gen) == [2, 0]
        qcommit(gen)

        gen = qpop(qserver, "host", job_id=job_id1)
        assert next(gen) == [3, 0]
        qcommit(gen)
        gen = qpop(qserver, "host", job_id=job_id1)
        assert next(gen) == [3, 0]  # task stays in queue due of job conflict

        qserver.execution_completed(job_id1)
        gen = qpop(qserver, "host", job_id=job_id1)
        assert next(gen) == [3, 0]
        qcommit(gen)
        gen = qpop(qserver, "host", job_id=job_id1)
        assert next(gen) == [3, 0]  # task stays in queue due of job conflict

        time.sleep(ttl)
        gen = qpop(qserver, "host", job_id=job_id1)
        assert next(gen) == [3, 0]
        qcommit(gen)

    def test__get_multiple_tasks_at_once(self, qserver):
        owner = "OWNER"
        host = "host"
        tids = list(range(1, 5))
        for tid in tids:
            qserver.push(tid, 0, [(0, host)], task_info=qtypes.TaskInfo(owner=owner))

        jobs_ids = [uuid.uuid4().hex for _ in range(len(tids))]
        jobs = get_jobs(qserver, host, host_info=None, jobs_ids=jobs_ids)
        assert [tid for tid, jid in jobs] == tids
        assert [jid for tid, jid in jobs] == jobs_ids

    def test__get_multiple_tasks_at_once_less_jobs_ids(self, qserver):
        owner = "OWNER"
        host = "host"
        tids = list(range(1, 5))
        for tid in tids:
            qserver.push(tid, 0, [(0, host)], task_info=qtypes.TaskInfo(owner=owner))

        jobs_ids = [uuid.uuid4().hex for _ in range(len(tids) - 2)]
        jobs = get_jobs(qserver, host, host_info=None, jobs_ids=jobs_ids)
        assert [tid for tid, jid in jobs] == tids[:len(jobs_ids)]
        assert [jid for tid, jid in jobs] == jobs_ids

    def test__get_multiple_tasks_at_once_less_tasks(self, qserver):
        owner = "OWNER"
        host = "host"
        tids = list(range(1, 3))
        for tid in tids:
            qserver.push(tid, 0, [(0, host)], task_info=qtypes.TaskInfo(owner=owner))

        jobs_ids = [uuid.uuid4().hex for _ in range(len(tids) + 2)]
        jobs = get_jobs(qserver, host, host_info=None, jobs_ids=jobs_ids)
        assert [tid for tid, jid in jobs] == tids
        assert [jid for tid, jid in jobs] == jobs_ids[:len(tids)]

    def test__get_multiple_tasks_at_once_with_disk_space(self, qserver):
        owner = "OWNER"
        host = "host"
        tids = list(range(1, 5))
        host_disk_space = 100
        task_disk_space = 30
        host_info = qtypes.HostInfo(
            capabilities=qtypes.ComputingResources(disk_space=host_disk_space),
            free=qtypes.ComputingResources()
        )
        for tid in tids:
            qserver.push(
                tid, 0, [(0, host)],
                task_info=qtypes.TaskInfo(
                    owner=owner,
                    requirements=qtypes.ComputingResources(disk_space=task_disk_space)
                )
            )

        jobs_ids = [uuid.uuid4().hex for _ in range(len(tids))]
        jobs = get_jobs(qserver, host, host_info=host_info, jobs_ids=jobs_ids)
        jobs_limit = host_disk_space // task_disk_space
        assert [tid for tid, jid in jobs] == tids[:jobs_limit]
        assert [jid for tid, jid in jobs] == jobs_ids[:jobs_limit]

    def test__get_tasks_for_multislot(self, qserver):
        owner = "OWNER"
        host = "host"
        total_cores = 32
        total_ram = 256 << 10
        free_cores = 8
        free_ram = 64 << 10
        host_info = qtypes.HostInfo(
            tags=[ctc.Tag.MULTISLOT],
            capabilities=qtypes.ComputingResources(cores=total_cores, ram=total_ram, disk_space=0),
            free=qtypes.ComputingResources(cores=free_cores, ram=free_ram)
        )
        tids = []
        push_task = lambda task_id, cores=1, ram=1: (
            qserver.push(
                task_id, 0, [(0, host)],
                task_info=qtypes.TaskInfo(
                    owner=owner,
                    requirements=qtypes.ComputingResources(disk_space=0, cores=cores, ram=ram)
                )
            ),
            tids.append(task_id)
        )
        jobs_ids = lambda: [uuid.uuid4().hex for _ in range(len(tids))]

        push_task(1, cores=free_cores + 1)
        push_task(2, ram=free_ram + 1)
        push_task(3, cores=free_cores)
        push_task(4, ram=free_ram)
        push_task(5, cores=free_cores // 2, ram=free_ram // 2)
        push_task(6, cores=free_cores // 2, ram=free_ram // 2)
        push_task(7, cores=free_cores - 1, ram=free_ram - 1)
        push_task(8, cores=2)
        push_task(9, ram=2)
        push_task(10, cores=1)
        push_task(11, ram=1)
        push_task(12, cores=free_cores - 6)
        push_task(13, ram=free_ram - 6)
        push_task(14)
        push_task(15)

        for expected_tids in [[3], [4], [5, 6], [7, 10], [8, 9, 11, 12, 13, 14]]:
            jobs = get_jobs(qserver, host, host_info=host_info, jobs_ids=jobs_ids())
            assert [tid for tid, _ in jobs] == expected_tids, ([tid for tid, _ in jobs], expected_tids)

    def test__set_quota(self, qserver):
        owner = "OWNER"
        qserver.push(
            1, 0, [qtypes.TaskQueueHostsItem(0, "host")],
            task_info=qtypes.TaskInfo(owner=owner)
        )
        assert qserver.quota("OWNER") == qtypes.DEFAULT_QUOTA
        qserver.set_quota("OWNER", 1000)
        assert qserver.quota("OWNER") == 1000
        qserver.set_quota("OWNER", 0)
        assert qserver.quota("OWNER") == 0
        qserver.set_quota("OWNER", -1000)
        assert qserver.quota("OWNER") == -1000
        qserver.set_quota("OWNER", None)
        assert qserver.quota("OWNER") == qtypes.DEFAULT_QUOTA

    @pytest.mark.skipif(not system.inside_the_binary(), reason="Binary required")
    def test__no_gc_objects(self):
        from sandbox.serviceq import queues

        s = qtypes.Serializable()
        r = qtypes.TaskRef(1)
        e = qtypes.Execution("0" * 16, 0, 0, 0, 0, 0, 0, 0, 0)
        c = qtypes.Consumption()
        i = qtypes.HostQueueItem(0, 1, r)
        q = queues.HostQueue()
        m = queues.MergeQueue([q])

        for o in (s, r, e, c, i, q, m):
            assert not gc.is_tracked(o)

    @staticmethod
    def _create_queue_items(queue_size):
        refs = {i: qtypes.TaskRef(i) for i in range(1, queue_size + 1)}
        ordered_items = [qtypes.HostQueueItem(10, i, refs[i]) for i in range(1, queue_size + 1)]
        items = list(ordered_items)
        random.shuffle(items)
        return refs, ordered_items, items

    def test__host_queue(self):
        queue_size = 100

        queue = qstate.HostQueue()
        assert list(queue) == []

        refs, ordered_items, items = self._create_queue_items(queue_size)
        for item in items:
            queue.push(item)
        assert list(queue) == ordered_items

        tid = queue_size + 100
        ref = qtypes.TaskRef(tid)
        item = qtypes.HostQueueItem(1, tid, ref)
        queue.push(item)
        assert next(iter(queue)) == qtypes.HostQueueItem(1, tid, ref)
        assert next(iter(queue)) == qtypes.HostQueueItem(1, tid, ref)
        ref.clear()
        assert next(iter(queue)) == qtypes.HostQueueItem(10, 1, refs[1])

        for item in queue:
            item.task_ref.clear()
        assert list(queue) == []

        queue = qstate.HostQueue()
        ref1 = qtypes.TaskRef(1)
        ref2 = qtypes.TaskRef(1)
        item1 = qtypes.HostQueueItem(1, 1, ref1)
        item2 = qtypes.HostQueueItem(1, 1, ref2)
        queue.push(item1)
        assert list(queue) == [item1]
        queue.push(item2)
        assert list(queue) == [item2]

    def test__merge_queue(self):
        queue_size = 1000
        chunk_size = 100

        refs, ordered_items, items = self._create_queue_items(queue_size)
        host_queue = qstate.HostQueue()
        for item in items:
            host_queue.push(item)

        merge_queue = qstate.MergeQueue([host_queue])
        assert list(merge_queue) == ordered_items
        refs[1].clear()
        refs[queue_size].clear()
        assert list(merge_queue) == ordered_items[1:-1]

        refs, ordered_items, items = self._create_queue_items(queue_size)
        host_queues = []
        with context.Timer() as timer:
            with timer["push"]:
                for chunk in itertools.chunker(items, chunk_size):
                    host_queue = qstate.HostQueue()
                    for item in chunk:
                        host_queue.push(item)
                    host_queues.append(host_queue)
            with timer["merge"]:
                merge_queue = qstate.MergeQueue(host_queues)
            with timer["iterate"]:
                assert map(lambda _: _.task_id, merge_queue) == map(lambda _: _.task_id, ordered_items)
        print(timer)


class TestApiQuotas(object):
    def test__primary_api_consumption(self, qserver_with_api_quotas):
        timestamp = int(time.time())
        qserver_with_api_quotas.set_api_quota("test_user_1", 7)
        qserver_with_api_quotas.set_api_quota("test_user_2", 7)
        qserver_with_api_quotas.set_web_api_quota(8)
        assert qserver_with_api_quotas.get_web_api_quota() == 8

        delta = [
            ("test_user_1", timestamp, 1, 2),
            ("test_user_2", timestamp + 2, 2, 3),
            ("test_user_1", timestamp, 2, 3),
            ("test_user_2", timestamp + 2, 5, 6),
            ("test_user_1", timestamp + 1, 3, 4),
            ("test_user_3", timestamp + 3, 3, 4),
        ]

        baned_users, web_banned_users = msgpack.loads(qserver_with_api_quotas.push_api_quota(delta))
        assert qserver_with_api_quotas.get_api_consumption("test_user_1") == (6, 7)
        assert qserver_with_api_quotas.get_api_consumption("test_user_2") == (7, 7)
        assert tuple(baned_users) == ("test_user_2", )
        assert qserver_with_api_quotas.get_web_api_consumption("test_user_1") == (9, 8)
        assert qserver_with_api_quotas.get_web_api_consumption("test_user_2") == (9, 8)
        assert tuple(sorted(web_banned_users)) == ("test_user_1", "test_user_2")

    def test__set_api_consumption(self, qserver_with_api_quotas):
        quota = 2500
        user = "test_user"
        assert qserver_with_api_quotas.set_api_quota(user, quota) == quota
        assert qserver_with_api_quotas.get_api_quota(user) == quota


class TestReasourceLocks(object):
    def test__resource_lock(self, qserver):
        res_id = 1
        host1 = "test_host1"
        host2 = "test_host2"
        assert qserver.acquire_resource_lock(res_id, host1)
        assert not qserver.acquire_resource_lock(res_id, host2)
        assert qserver.release_resource_lock(res_id, host1)
        assert qserver.acquire_resource_lock(res_id, host2)

    def test__resource_locks_cleaner(self):
        resource_locks = qtypes.ResourceLocks()
        resource_locks.acquire(1, "test_host", 0)
        assert resource_locks.encode() == {1: ("test_host", 0)}
        resource_locks.clean_resource_locks(resource_locks.LOCK_TTL - 1)
        assert resource_locks.encode() == {1: ("test_host", 0)}
        resource_locks.clean_resource_locks(resource_locks.LOCK_TTL)
        assert len(resource_locks.encode()) == 0


class TestIndexedList(object):
    def test__make_bits(self):
        indexed_list = qtypes.IndexedList()
        assert indexed_list.encode() == []

        bits, unknown_items = indexed_list.make_bits([])
        assert bits == b"\x00\x00\x00\x00", repr(bits)
        assert unknown_items == set()
        assert indexed_list.indexes_from_bits(bits) == []

        bits, unknown_items = indexed_list.make_bits(["item1"])
        assert bits == b"\x00\x00\x00\x00", repr(bits)
        assert unknown_items == {"item1"}

        index = indexed_list.append("item1")
        assert index == 0, index
        assert indexed_list.encode() == ["item1"]

        bits, unknown_items = indexed_list.make_bits(["item1"])
        assert bits == b"\x00\x00\x00\x01", repr(bits)
        assert unknown_items == set(), unknown_items
        assert indexed_list.indexes_from_bits(bits) == [indexed_list.index[_] for _ in ["item1"]]

        index = indexed_list.append("item2")
        assert index == 1, index
        assert indexed_list.encode() == ["item1", "item2"]

        bits, unknown_items = indexed_list.make_bits(["item1"])
        assert bits == b"\x00\x00\x00\x01", repr(bits)
        assert unknown_items == set(), unknown_items

        bits, unknown_items = indexed_list.make_bits(["item2"])
        assert bits == b"\x00\x00\x00\x02", repr(bits)
        assert unknown_items == set()
        assert indexed_list.indexes_from_bits(bits) == [indexed_list.index[_] for _ in ["item2"]]

        bits, unknown_items = indexed_list.make_bits(["item1", "item2"])
        assert bits == b"\x00\x00\x00\x03", repr(bits)
        assert unknown_items == set()
        assert indexed_list.indexes_from_bits(bits) == [indexed_list.index[_] for _ in ["item1", "item2"]]

        bits, unknown_items = indexed_list.make_bits(["item2", "item1"])
        assert bits == b"\x00\x00\x00\x03", repr(bits)
        assert unknown_items == set(), unknown_items
        assert indexed_list.indexes_from_bits(bits) == [indexed_list.index[_] for _ in ["item1", "item2"]]

        bits, unknown_items = indexed_list.make_bits(["item3"])
        assert bits == b"\x00\x00\x00\x00", repr(bits)
        assert unknown_items == {"item3"}

        bits, unknown_items = indexed_list.make_bits(["item1", "item3"])
        assert bits == b"\x00\x00\x00\x01", repr(bits)
        assert unknown_items == {"item3"}

        bits, unknown_items = indexed_list.make_bits(["item1", "item2", "item3"])
        assert bits == b"\x00\x00\x00\x03", repr(bits)
        assert unknown_items == {"item3"}, unknown_items

        index = indexed_list.append("item3")
        assert index == 2, index
        bits, unknown_items = indexed_list.make_bits(["item1", "item2", "item3"])
        assert bits == b"\x00\x00\x00\x07", repr(bits)
        assert unknown_items == set(), unknown_items
        assert indexed_list.indexes_from_bits(bits) == [indexed_list.index[_] for _ in ["item1", "item2", "item3"]]

        indexed_list = qtypes.IndexedList()
        items = []
        for i in range(32 * 3):
            item = "item{}".format(i)
            index = indexed_list.append(item)
            items.append(item)
            assert index == i
            bits = indexed_list.make_bits(items)[0]
            assert indexed_list.indexes_from_bits(bits) == [indexed_list.index[_] for _ in items]

        bits, _ = indexed_list.make_bits(items)
        assert bits == b"\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff"
        bits, _ = indexed_list.make_bits(items[:32])
        assert bits == b"\xff\xff\xff\xff"
        bits, _ = indexed_list.make_bits(items[32:64])
        assert bits == b"\xff\xff\xff\xff\x00\x00\x00\x00"
        bits, _ = indexed_list.make_bits(items[:32] + items[64:])
        assert bits == b"\xff\xff\xff\xff\x00\x00\x00\x00\xff\xff\xff\xff"
