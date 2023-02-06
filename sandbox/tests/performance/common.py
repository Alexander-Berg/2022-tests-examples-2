from __future__ import print_function

import os
import time
import uuid
import random

import six
# noinspection PyUnresolvedReferences
import psutil
import msgpack

from sandbox.common import context, system, format, console
from sandbox.common import data as common_data
from sandbox.serviceq import state as qstate
from sandbox.serviceq import types as qtypes


class BaseTestPerformance(object):
    LIST_TESTS_DURATION = 10

    def _test_data(self):
        try:
            # noinspection PyUnresolvedReferences
            return type(self).__test_data
        except AttributeError:
            with context.Timer() as timer:
                snapshot_filename = "serviceq.16.snapshot"
                snapshot_path = (
                    snapshot_filename
                    if system.inside_the_binary() else
                    os.path.join(os.path.dirname(__file__), snapshot_filename)
                )
                with open(snapshot_path) as f:
                    unpacker = common_data.msgpack_unpacker()
                    unpacker.feed(f.read())
                    _, data = list(unpacker)
                type(self).__test_data = qstate.PersistentState.decode(data)
            snapshot_size = format.size2str(os.path.getsize(snapshot_path))
            print("\nLoaded test data from {} ({}) by {}".format(snapshot_path, snapshot_size, timer))
            # noinspection PyUnresolvedReferences
            return self.__test_data

    @staticmethod
    def __test_dump(qapi):
        qapi.calculate_consumptions()
        state = qapi._Server__state
        with context.Timer() as timer:
            assert qapi.dump_snapshot()
            # noinspection PyProtectedMember
            snapshot_size = format.size2str(os.path.getsize(qapi._Server__snapshot_path_to_save))
            print("\nDumping state to disk: {} ({})".format(timer, snapshot_size))
        qapi._Server__state = qstate.PersistentState()
        with context.Timer() as timer:
            qapi.load_snapshot()
            print("\nLoading state from disk: {} ({})".format(timer, snapshot_size))
        for field in state.__slots__:
            if field == "task_queue":
                for prio, queue in state.task_queue.iteritems():
                    assert queue == qapi._Server__state.task_queue.get(prio, [])
            elif field == "queue_size_by_owners":
                for owner, size in state.queue_size_by_owners.iteritems():
                    assert size == qapi._Server__state.queue_size_by_owners.get(owner, 0)
            elif field == "owners_rating_index":
                assert len(state.owners_rating_index) == len(qapi._Server__state.owners_rating_index)
            elif field == "db_operations":
                assert {
                    k: state.db_operations[k].queue
                    for k in state.db_operations.queues
                } == {
                    k: qapi._Server__state.db_operations[k].queue
                    for k in qapi._Server__state.db_operations.queues
                }
            elif field in ("common_oplog", "recently_executed_jobs", "hosts_cache"):
                continue
            else:
                assert getattr(state, field) == getattr(qapi._Server__state, field), field

    @staticmethod
    def __memory_usage(prev_mem=None):
        proc = psutil.Process(os.getpid())
        mem = getattr(proc, "memory_info", getattr(proc, "get_memory_info", None))()
        print("\nMemory usage: {} RSS, {} VMS".format(
            format.size2str(mem.rss),
            format.size2str(mem.vms)
        ))
        if prev_mem:
            print("Memory consumption: {} RSS, {} VMS".format(
                format.size2str(mem.rss - prev_mem.rss),
                format.size2str(mem.vms - prev_mem.vms)
            ))
        return mem

    @staticmethod
    def _collect_garbage(qapi):
        with context.Timer() as timer:
            # noinspection PyProtectedMember
            qapi._collect_garbage()
            print("\nGarbage collected in {}.".format(timer))
            # noinspection PyProtectedMember
            print("Statistics: {}".format(qapi._Server__state.stats))

    def run_test(self, qapi, utils, test_snapshot=False, test_encode_decode=False):
        import logging
        logging.root.setLevel(logging.ERROR)

        tasks = set()
        test_data = self._test_data()

        cz = console.AnsiColorizer()

        # prepare operations
        all_hosts = qtypes.IndexedList.decode(qapi.add_hosts(test_data.hosts.encode()))
        hosts_cache = {}
        operations = []
        for priority, queue_by_priority in test_data.task_queue.iteritems():
            for item in queue_by_priority:
                if not item:
                    continue
                hosts = []
                scores = set()
                if isinstance(item.hosts, list):
                    common_score = None
                    for score, host in item.hosts:
                        hosts.append([-score, test_data.hosts[host]])
                        scores.add(score)
                    if len(scores) == 1:
                        common_score = scores.pop()
                        import hashlib
                        hosts_hash = hashlib.sha1(" ".join(host for _, host in hosts))
                        cached_hosts = hosts_cache.get(hosts_hash)
                        if cached_hosts is None:
                            bits, unknown_hosts = all_hosts.make_bits([host for _, host in hosts])
                            assert not unknown_hosts
                            hosts = hosts_cache[hosts_hash] = bits
                        else:
                            hosts = cached_hosts
                else:
                    common_score = item.score
                    hosts = item.hosts
                operations.append((
                    (item.task_id, priority, hosts),
                    dict(
                        task_info=qtypes.TaskInfo(
                            requirements=qtypes.ComputingResources(
                                resources=item.task_info.requirements.resources,
                                disk_space=item.task_info.requirements.disk_space,
                                cores=item.task_info.requirements.cores,
                                ram=item.task_info.requirements.ram,
                            ),
                            type=test_data.task_types[item.task_info.type],
                            owner=test_data.owners[item.task_info.owner]
                        ),
                        score=common_score
                    )
                ))

        starting_mem = self.__memory_usage()
        with context.Timer() as timer:
            first = None
            last = 0
            min_ = float("inf")
            max_ = 0
            for args, kws in operations:
                last = time.time()
                qapi.push(*args, **kws)
                last = time.time() - last
                if first is None:
                    first = last
                min_ = min(min_, last)
                max_ = max(max_, last)
                tasks.add(args[0])
            rate = len(tasks) / float(timer)
            print(cz.green((
                "\n{} push operations for {} hosts processed in {}.\n"
                "Average rate is {:.4f}, first: {:.6f}, last: {:.6f}, min: {:.6f}, max: {:.6f}"
            ).format(len(tasks), len(test_data.hosts), timer, rate, first, last, min_, max_)))

        self.__memory_usage(starting_mem)
        self._collect_garbage(qapi)
        self.__memory_usage(starting_mem)

        with context.Timer() as timer:
            iterations = 0
            for priority, queue_by_priority in test_data.task_queue.iteritems():
                for item in queue_by_priority:
                    if not item.task_ref:
                        continue
                    qapi.queue_by_task(item.task_id)
                    iterations += 1
                    if float(timer) >= self.LIST_TESTS_DURATION:
                        break
            rate = iterations / float(timer)
            print(cz.green((
                "\n{} lists for {} hosts and 1 task processed in {}.\n"
                "Average rate is {:.4f}"
            ).format(iterations, len(test_data.hosts), timer, rate)))

        with context.Timer() as timer:
            iterations = 0
            for host in test_data.hosts:
                qapi.queue_by_host(host)
                iterations += 1
                if float(timer) >= self.LIST_TESTS_DURATION:
                    break
            rate = iterations / float(timer)
            print(cz.green((
                "\n{} lists for 1 host and {} tasks processed in {}.\n"
                "Average rate is {:.4f}"
            ).format(iterations, len(tasks), timer, rate)))

        if test_snapshot:
            self.__memory_usage(starting_mem)
            self.__test_dump(qapi)
            self.__memory_usage(starting_mem)
            if test_encode_decode:
                with context.Timer() as timer:
                    # noinspection PyProtectedMember
                    state = qapi._Server__state
                    data = state.encode()
                    print("\nEncoding state: {}".format(timer))
                self.__memory_usage(starting_mem)
                with context.Timer() as timer:
                    raw_data = msgpack.dumps(
                        data,
                        default=lambda _: _.encode() if isinstance(_, qtypes.Serializable) else _
                    )
                    print("\nPacking state ({}): {}".format(format.size2str(len(raw_data)), timer))
                del data
                self.__memory_usage(starting_mem)
                with context.Timer() as timer:
                    data = msgpack.loads(raw_data)
                    print("\nUnpacking state ({}): {}".format(format.size2str(len(raw_data)), timer))
                del raw_data
                self.__memory_usage(starting_mem)
                with context.Timer() as timer:
                    with timer["decoding"]:
                        restored_state = type(state).decode(data)
                    with timer["testing"]:
                        for field in state.__slots__:
                            if field in ("db_operations",):
                                continue
                            if field == "owners_rating_index":
                                assert len(state.owners_rating_index) == len(restored_state.owners_rating_index)
                            else:
                                assert getattr(state, field) == getattr(restored_state, field), field
                    print("\nDecoding state: {}".format(timer))
                del restored_state
                self.__memory_usage(starting_mem)

        self._collect_garbage(qapi)
        self.__memory_usage(starting_mem)

        total_tasks = len(tasks)
        with context.Timer() as timer:
            success_pops = 0
            first = None
            last = 0
            min_ = float("inf")
            max_ = 0
            i = -1
            hosts = list(test_data.hosts)
            job_ids = []
            for i in six.moves.range(total_tasks):
                while hosts:
                    host = random.choice(hosts)
                    with context.Timer() as last:
                        host_capabilities = test_data.host_capabilities.get(test_data.hosts.index[host])
                        if host_capabilities is None:
                            hosts.remove(host)
                            continue
                        job_id = uuid.uuid4().hex
                        gen = utils.qpop(
                            qapi,
                            host,
                            host_info=qtypes.HostInfo(
                                capabilities=qtypes.ComputingResources(
                                    resources=host_capabilities.resources,
                                    disk_space=host_capabilities.disk_space,
                                    cores=host_capabilities.cores,
                                    ram=host_capabilities.ram,
                                ),
                                free=qtypes.ComputingResources(),
                            ),
                            job_id=job_id
                        )
                        for task_id, score in gen:
                            success_pops += 1
                            assert task_id in tasks
                            tasks.remove(task_id)
                            utils.qcommit(gen)
                            job_ids.append(job_id)
                            break
                        else:
                            hosts.remove(host)
                            continue
                        break
                last = float(last)
                if first is None:
                    first = last
                min_ = min(min_, last)
                max_ = max(max_, last)
            rate = total_tasks / float(timer)
            print(cz.green((
                "\n{} pop operations ({} task ids returned) for {} hosts processed in {}.\n"
                "Average rate is {:.4f}, first: {:.6f}, last: {:.6f}, min: {:.6f}, max: {:.6f}"
            ).format(i + 1, success_pops, len(test_data.hosts), timer, rate, first, last, min_, max_)))

        if test_snapshot:
            self.__memory_usage(starting_mem)
            self._collect_garbage(qapi)
            self.__memory_usage(starting_mem)
            self.__test_dump(qapi)

        self.__memory_usage(starting_mem)

        total_jobs = len(job_ids)
        with context.Timer() as timer:
            first = None
            last = 0
            min_ = float("inf")
            max_ = 0
            for job_id in job_ids:
                qapi.execution_completed(job_id)
                last = float(last)
                if first is None:
                    first = last
                min_ = min(min_, last)
                max_ = max(max_, last)
            rate = total_tasks / float(timer)
            print(cz.green((
                "\n{} execution_completed operations processed in {}.\n"
                "Average rate is {:.4f}, first: {:.6f}, last: {:.6f}, min: {:.6f}, max: {:.6f}"
            ).format(total_jobs, timer, rate, first, last, min_, max_)))

        if test_snapshot:
            self.__memory_usage(starting_mem)
            self._collect_garbage(qapi)
            self.__memory_usage(starting_mem)
            self.__test_dump(qapi)

        self.__memory_usage(starting_mem)
