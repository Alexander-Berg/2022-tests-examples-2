import uuid
import pytest
import random
import itertools as it

import sandbox.serviceq.types as qtypes
import sandbox.serviceq.errors as qerrors

from sandbox.serviceq.tests.client import utils as client_utils


def get_jobs(qclient, host, host_info=None, jobs_ids=()):
    if host_info is None:
        host_info = qtypes.HostInfo(
            capabilities=qtypes.ComputingResources(disk_space=1),
            free=qtypes.ComputingResources(),
        )
    task_to_execute = qclient.task_to_execute(host, host_info)
    task_to_execute_it = qclient.task_to_execute_it(host, host_info)
    jobs = []
    task_to_execute.next()
    result = None
    jids = list(jobs_ids)
    while jids:
        item = task_to_execute_it.send(result)
        if item is None:
            break
        tid, score = item
        result = task_to_execute.send((tid, jids[0]))
        if result != qtypes.QueueIterationResult.ACCEPTED:
            continue
        result = qtypes.QueueIterationResult.NEXT_TASK
        jobs.append((tid, jids.pop(0)))
    else:
        task_to_execute_it.send(qtypes.QueueIterationResult.ACCEPTED)
        task_to_execute.send((None, None))
        task_to_execute.send(task_to_execute_it.wait())
    return jobs


class TestClient(object):
    def test__client_queue0(self, serviceq):
        assert serviceq.queue() == []

    @pytest.mark.usefixtures("qserver_with_data_proc")
    def test__client_queue1(self, qclient):
        assert qclient.queue() == [
            qtypes.TaskQueueItem(task_id=2, priority=3, hosts=[
                qtypes.TaskQueueHostsItem(score=3, host="host3"),
                qtypes.TaskQueueHostsItem(score=2, host="host2"),
                qtypes.TaskQueueHostsItem(score=1, host="host1")
            ], task_ref=None, task_info=qtypes.TaskInfo(type="T2", owner="O2", enqueue_time=101), score=None),
            qtypes.TaskQueueItem(task_id=3, priority=2, hosts=[
                qtypes.TaskQueueHostsItem(score=2, host="host1"),
                qtypes.TaskQueueHostsItem(score=1, host="host2")
            ], task_ref=None, task_info=qtypes.TaskInfo(type="T3", owner="O3", enqueue_time=102), score=None),
            qtypes.TaskQueueItem(task_id=4, priority=2, hosts=[
                qtypes.TaskQueueHostsItem(score=2, host="host2"),
                qtypes.TaskQueueHostsItem(score=1, host="host1")
            ], task_ref=None, task_info=qtypes.TaskInfo(type="T4", owner="O4", enqueue_time=103), score=None),
            qtypes.TaskQueueItem(task_id=1, priority=1, hosts=[
                qtypes.TaskQueueHostsItem(score=3, host="host1"),
                qtypes.TaskQueueHostsItem(score=2, host="host2"),
                qtypes.TaskQueueHostsItem(score=1, host="host3")
            ], task_ref=None, task_info=qtypes.TaskInfo(type="T1", owner="O1", enqueue_time=100), score=None)
        ]

    @pytest.mark.usefixtures("qserver_with_data_proc")
    def test__queue_by_host(self, qclient):
        assert qclient.queue_by_host("non_existent_host") == []
        assert qclient.queue_by_host("host1") == [
            (4, 2, 1),
            (3, 2, 2),
            (2, 3, 1),
            (1, 1, 3)
        ]
        assert qclient.queue_by_host("host2") == [
            (4, 2, 2),
            (3, 2, 1),
            (2, 3, 2),
            (1, 1, 2)
        ]
        assert qclient.queue_by_host("host3") == [
            (2, 3, 3),
            (1, 1, 1)
        ]

    @pytest.mark.usefixtures("qserver_with_data_proc")
    def test__queue_by_task_id(self, qclient):
        assert qclient.queue_by_task(666) == (None, [])
        assert qclient.queue_by_task(1) == (1, [(3, "host1"), (2, "host2"), (1, "host3")])
        assert qclient.queue_by_task(2) == (3, [(3, "host3"), (2, "host2"), (1, "host1")])
        assert qclient.queue_by_task(3) == (2, [(2, "host1"), (1, "host2")])
        assert qclient.queue_by_task(4) == (2, [(2, "host2"), (1, "host1")])

    @pytest.mark.usefixtures("qserver_with_data_proc")
    def test__multiple_owners_quota(self, qclient):
        owners = ["guest", "no_such_user"]
        quota = qclient.multiple_owners_quota(owners)
        assert quota == [
            ["guest", qtypes.QuotaItem(0, 0, 0)],
            ["no_such_user", qtypes.QuotaItem(0, 0, 0)],
        ]

    @pytest.mark.usefixtures("qserver_with_data_proc")
    def test__pop_0(self, qclient):
        qpop = client_utils.qpop
        assert not list(qpop(qclient, "non_existent"))

    @pytest.mark.usefixtures("qserver_with_data_proc")
    def test__pop_1(self, qclient):
        qpop = client_utils.qpop
        qcommit = client_utils.qcommit
        assert list(qpop(qclient, "host1")) == [[4, 1], [3, 2], [2, 1], [1, 3]]
        gen = qpop(qclient, "host1")
        assert gen.next() == [4, 1]
        list(gen)
        gen = qpop(qclient, "host1")
        assert gen.next() == [4, 1]
        qcommit(gen)
        gen = qpop(qclient, "host1")
        assert gen.next() == [3, 2]
        assert gen.next() == [2, 1]
        list(gen)
        gen = qpop(qclient, "host1")
        assert gen.next() == [3, 2]
        qcommit(gen)
        gen = qpop(qclient, "host1")
        assert gen.next() == [2, 1]
        qcommit(gen)
        gen = qpop(qclient, "host1")
        assert gen.next() == [1, 3]
        qcommit(gen)
        assert not list(qpop(qclient, "host1"))

    @pytest.mark.usefixtures("qserver_with_data_proc")
    def test__pop_2(self, qclient):
        qpop = client_utils.qpop
        qcommit = client_utils.qcommit
        assert qclient.queue()
        for sample in ([4, 2], [3, 1], [2, 2], [1, 2]):
            gen = qpop(qclient, "host2")
            assert gen.next() == sample
            qcommit(gen)
        assert not list(qpop(qclient, "host2"))

    @pytest.mark.usefixtures("qserver_with_data_proc")
    def test__pop_3(self, qclient):
        qpop = client_utils.qpop
        qcommit = client_utils.qcommit
        assert qclient.queue()
        for sample in ([2, 3], [1, 1]):
            gen = qpop(qclient, "host3")
            assert gen.next() == sample
            qcommit(gen)
        assert not list(qpop(qclient, "host3"))

    @pytest.mark.usefixtures("qserver_with_data_proc")
    def test__pop_4(self, qclient):
        qpop = client_utils.qpop
        qcommit = client_utils.qcommit
        assert qclient.queue()
        for host, sample in (("host1", [4, 1]), ("host2", [3, 1]), ("host3", [2, 3]), ("host1", [1, 3])):
            gen = qpop(qclient, host)
            assert gen.next() == sample
            qcommit(gen)
        for host in ("host1", "host2", "host3"):
            assert not list(qpop(qclient, host))

    def test__push(self, serviceq, test_queue):
        assert serviceq.queue() == []

        for task_id, item in test_queue.iteritems():
            serviceq.push(task_id, *item)

        assert serviceq.queue() == [
            qtypes.TaskQueueItem(task_id=2, priority=3, hosts=[
                qtypes.TaskQueueHostsItem(score=3, host="host3"),
                qtypes.TaskQueueHostsItem(score=2, host="host2"),
                qtypes.TaskQueueHostsItem(score=1, host="host1")
            ], task_ref=None, task_info=qtypes.TaskInfo(type="T2", owner="O2", enqueue_time=101), score=None),
            qtypes.TaskQueueItem(task_id=3, priority=2, hosts=[
                qtypes.TaskQueueHostsItem(score=2, host="host1"),
                qtypes.TaskQueueHostsItem(score=1, host="host2")
            ], task_ref=None, task_info=qtypes.TaskInfo(type="T3", owner="O3", enqueue_time=102), score=None),
            qtypes.TaskQueueItem(task_id=4, priority=2, hosts=[
                qtypes.TaskQueueHostsItem(score=2, host="host2"),
                qtypes.TaskQueueHostsItem(score=1, host="host1")
            ], task_ref=None, task_info=qtypes.TaskInfo(type="T4", owner="O4", enqueue_time=103), score=None),
            qtypes.TaskQueueItem(task_id=1, priority=1, hosts=[
                qtypes.TaskQueueHostsItem(score=3, host="host1"),
                qtypes.TaskQueueHostsItem(score=2, host="host2"),
                qtypes.TaskQueueHostsItem(score=1, host="host3")
            ], task_ref=None, task_info=qtypes.TaskInfo(type="T1", owner="O1", enqueue_time=100), score=None)
        ]

    @pytest.mark.usefixtures("qserver_with_data_proc")
    def test__validate(self, qclient):
        qpop = client_utils.qpop
        qcommit = client_utils.qcommit
        task_ids, jobs_ids = map(sorted, qclient.validate())
        assert task_ids, jobs_ids == [[1, 2, 3, 4], []]
        jobs_ids = [uuid.uuid4().hex for _ in task_ids]

        gen = qpop(qclient, "host1", job_id=jobs_ids[0])
        gen.next()
        qcommit(gen)
        assert sorted(qclient.validate()[0]) == [1, 2, 3]

        gen = qpop(qclient, "host2", job_id=jobs_ids[1])
        gen.next()
        qcommit(gen)
        assert sorted(qclient.validate()[0]) == [1, 2]

        gen = qpop(qclient, "host3", job_id=jobs_ids[2])
        gen.next()
        qcommit(gen)
        assert sorted(qclient.validate()[0]) == [1]

        gen = qpop(qclient, "host1", job_id=jobs_ids[3])
        gen.next()
        qcommit(gen)
        assert map(sorted, qclient.validate()) == [[], sorted(jobs_ids)]

    @pytest.mark.usefixtures("qserver_with_data_proc")
    def test__lock_jobs(self, qclient):
        task_ids, jobs_ids = map(sorted, qclient.validate())
        assert task_ids, jobs_ids == [[1, 2, 3, 4], []]
        jobs_ids = [uuid.uuid4().hex for _ in task_ids]
        jobs_lock = qclient.lock_jobs(jobs_ids)
        jobs = get_jobs(qclient, "host1", jobs_ids=jobs_ids)
        assert [_[0] for _ in jobs] == [4, 3, 2, 1]
        assert sorted(_[1] for _ in jobs) == sorted(jobs_ids)
        assert qclient.validate() == [[], []]

        jobs_lock.send(jobs[0][1])
        assert qclient.validate() == [[], [jobs[0][1]]]

        jobs_lock.send(jobs[1][1])
        assert map(sorted, qclient.validate()) == [[], sorted([jobs[0][1], jobs[1][1]])]

        del jobs_lock
        assert map(sorted, qclient.validate()) == [[], sorted(_[1] for _ in jobs)]

    def test__ping(self, serviceq):
        value = random.randint(1, 100)
        assert serviceq.ping(value) == value

    def test__resources(self, serviceq, test_queue):
        assert serviceq.resources() == []
        all_resources = list(set(random.randint(0, 100) for _ in xrange(100)))
        task_resources = {tid: {random.choice(all_resources): 0 for _ in xrange(10)} for tid in xrange(1, 5)}
        used_resources = list(set(it.chain.from_iterable(task_resources.itervalues())))
        for task_id, (priority, hosts, task_info) in test_queue.iteritems():
            resources = task_resources[task_id]
            serviceq.push(
                task_id,
                priority,
                sorted((qtypes.TaskQueueHostsItem(*h) for h in hosts), key=lambda _: -_.score),
                task_info._replace(requirements=qtypes.ComputingResources(resources=resources))
            )
        assert serviceq.resources() == used_resources

    @pytest.mark.xfail(run=False)  # FIXME: SANDBOX-4737: Disk usage calculation has been disabled
    def test__requirements__disk_space(self, serviceq, test_queue):
        qpop = client_utils.qpop
        disk_reqs = {1: 10, 2: 20, 3: 30}
        for task_id, (priority, hosts, task_info) in test_queue.iteritems():
            disk_req = disk_reqs.get(task_id)
            if disk_req is not None:
                serviceq.push(
                    task_id,
                    priority,
                    sorted((qtypes.TaskQueueHostsItem(*h) for h in hosts), key=lambda _: -_.score),
                    task_info._replace(requirements=qtypes.ComputingResources(disk_req))
                )
        assert list(qpop(serviceq, "host1")) == [[2, 1], [3, 2], [1, 3]]
        assert list(qpop(serviceq, "host1", qtypes.ComputingResources())) == [[2, 1], [3, 2], [1, 3]]

        for disk_cap in xrange(0, 10):
            assert list(qpop(serviceq, "host1", qtypes.ComputingResources(disk_cap))) == []
            assert list(qpop(serviceq, "host1")) == []

        serviceq.push(1, test_queue[1][0], None)
        assert list(qpop(serviceq, "host1")) == []

        for disk_cap in xrange(10, 20):
            assert list(qpop(serviceq, "host1", qtypes.ComputingResources(disk_cap))) == [[1, 3]]
            assert list(qpop(serviceq, "host1")) == [[1, 3]]

        for disk_cap in xrange(20, 30):
            assert list(qpop(serviceq, "host1", qtypes.ComputingResources(disk_cap))) == [[2, 1], [1, 3]]
            assert list(qpop(serviceq, "host1")) == [[2, 1], [1, 3]]

        for disk_cap in xrange(30, 40):
            assert list(qpop(serviceq, "host1", qtypes.ComputingResources(disk_cap))) == [[2, 1], [3, 2], [1, 3]]
            assert list(qpop(serviceq, "host1")) == [[2, 1], [3, 2], [1, 3]]

        task_id = 4
        priority, hosts, task_info = test_queue[task_id]
        disk_req = 40
        serviceq.push(
            task_id,
            priority,
            sorted((qtypes.TaskQueueHostsItem(*h) for h in hosts), key=lambda _: -_.score),
            task_info._replace(requirements=qtypes.ComputingResources(disk_req))
        )
        assert list(qpop(serviceq, "host1")) == [[2, 1], [3, 2], [1, 3]]
        assert list(qpop(serviceq, "host2")) == [[2, 2], [4, 2], [3, 1], [1, 2]]
        assert (
            list(qpop(serviceq, "host1", qtypes.ComputingResources(disk_req))) ==
            [[2, 1], [3, 2], [4, 1], [1, 3]]
        )
        serviceq.push(task_id, None, None)
        assert list(qpop(serviceq, "host1")) == [[2, 1], [3, 2], [1, 3]]
        serviceq.push(
            task_id,
            priority,
            sorted((qtypes.TaskQueueHostsItem(*h) for h in hosts), key=lambda _: -_.score),
            task_info._replace(requirements=qtypes.ComputingResources(disk_req))
        )
        assert list(qpop(serviceq, "host1")) == [[2, 1], [3, 2], [4, 1], [1, 3]]

    @pytest.mark.xfail(run=False)  # FIXME: SANDBOX-4737: Disk usage calculation has been disabled
    def test__requirements__resources(self, serviceq, test_queue):
        qpop = client_utils.qpop

        def push(task_resources):
            for task_id, (priority, hosts, task_info) in test_queue.iteritems():
                serviceq.push(
                    task_id,
                    priority,
                    sorted((qtypes.TaskQueueHostsItem(0, h[1]) for h in hosts), key=lambda _: -_.score),
                    task_info._replace(requirements=qtypes.ComputingResources(resources=task_resources.get(task_id)))
                )

        regular_pop_sequence = [[2, 0], [3, 0], [4, 0], [1, 0]]
        altered_pop_sequence = [[2, 0], [4, 0], [3, 0], [1, 0]]
        res = {1: 10, 2: 15, 3: 20, 4: 30}  # {<resource id>: <resource size>}

        push({})

        assert list(qpop(serviceq, "host1")) == regular_pop_sequence

        for rids in it.chain.from_iterable(it.combinations(res, _) for _ in xrange(1, len(res) + 1)):
            req = qtypes.ComputingResources(resources={_: res[_] for _ in rids})
            assert list(qpop(serviceq, "host1", req)) == regular_pop_sequence

        push({3: {_: res[_] for _ in (4,)}, 4: {_: res[_] for _ in (1, 2, 3)}})

        for rids in ([1], [2], [1, 2], [1, 3], [2, 3, 4]):
            req = qtypes.ComputingResources(resources={_: res[_] for _ in rids})
            assert list(qpop(serviceq, "host1", req)) == altered_pop_sequence
            assert list(qpop(serviceq, "host1")) == altered_pop_sequence

        for rids in ([4], [1, 4], [2, 4], [3, 4], [1, 2, 4], [1, 3, 4]):
            req = qtypes.ComputingResources(resources={_: res[_] for _ in rids})
            assert list(qpop(serviceq, "host1", req)) == regular_pop_sequence
            assert list(qpop(serviceq, "host1")) == regular_pop_sequence

        assert list(qpop(serviceq, "host2")) == regular_pop_sequence

        push({})
        req = qtypes.ComputingResources(resources={_: res[_] for _ in [2, 3, 4]})
        assert list(qpop(serviceq, "host1", req)) == regular_pop_sequence
        push({3: {_: res[_] for _ in (4,)}, 4: {_: res[_] for _ in (1, 2, 3)}})
        assert list(qpop(serviceq, "host1")) == altered_pop_sequence

        k10 = 10 << 10
        k20 = 20 << 10
        k30 = 30 << 10

        serviceq.sync(
            [
                [1, 0, [[0, "host1"]], qtypes.ComputingResources(disk_space=0, resources={1: k10})],
                [2, 1, [[0, "host1"]], qtypes.ComputingResources(disk_space=0, resources={2: k20})],
                [3, 2, [[0, "host1"]], qtypes.ComputingResources(disk_space=0, resources={3: k30})],
            ],
            reset=True
        )

        assert list(qpop(serviceq, "host1")) == [[3, 0], [2, 0], [1, 0]]

        assert list(
            qpop(serviceq, "host1", qtypes.ComputingResources(disk_space=0, resources={1: k10}))
        ) == [[1, 0]]
        assert list(
            qpop(serviceq, "host1", qtypes.ComputingResources(disk_space=10, resources={1: k10}))
        ) == [[1, 0]]
        assert list(
            qpop(serviceq, "host1", qtypes.ComputingResources(disk_space=20, resources={1: k10}))
        ) == [[2, 0], [1, 0]]
        assert list(
            qpop(serviceq, "host1", qtypes.ComputingResources(disk_space=30, resources={1: k10}))
        ) == [[3, 0], [2, 0], [1, 0]]

        assert list(
            qpop(serviceq, "host1", qtypes.ComputingResources(disk_space=0, resources={1: k10, 2: k20}))
        ) == [[2, 0], [1, 0]]
        assert list(
            qpop(serviceq, "host1", qtypes.ComputingResources(disk_space=10, resources={1: k10, 2: k20}))
        ) == [[2, 0], [1, 0]]
        assert list(
            qpop(serviceq, "host1", qtypes.ComputingResources(disk_space=20, resources={1: k10, 2: k20}))
        ) == [[2, 0], [1, 0]]
        assert list(
            qpop(serviceq, "host1", qtypes.ComputingResources(disk_space=30, resources={1: k10, 2: k20}))
        ) == [[3, 0], [2, 0], [1, 0]]

        assert list(
            qpop(serviceq, "host1", qtypes.ComputingResources(disk_space=0, resources={1: k10, 2: k20, 3: k30}))
        ) == [[3, 0], [2, 0], [1, 0]]

    @pytest.mark.usefixtures("qserver_with_data_proc")
    def test__lock(self, qclient):
        test_lock = "test_clock"
        with qclient.lock(test_lock):
            pass

        with pytest.raises(TypeError):
            with qclient.lock(5):
                pass

        with qclient.lock(test_lock):
            with pytest.raises(qerrors.QAcquireError):
                with qclient.lock(test_lock):
                    pass
