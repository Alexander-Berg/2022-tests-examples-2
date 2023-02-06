# -*- coding: utf-8 -*-

from passport.backend.logbroker_client.core.consumers.distributed.worker import DistributedLogbrokerWorker


def test_partitioner_workers_less_than_partitions():
    members = ['hostname2-1', 'hostname2-2', 'hostname2-3', 'hostname2-4', 'hostname2-5',
               'hostname1-1', 'hostname1-2', 'hostname1-3', 'hostname1-4', 'hostname1-5',
               'hostname3-1']
    partitions = [11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    assert DistributedLogbrokerWorker._partitioner('hostname1-2', members, partitions) == [2, 13]
    assert DistributedLogbrokerWorker._partitioner('hostname3-1', members, partitions) == [11]


def test_partitioner_workers_more_than_partitions_equal_workers():
    members = ['hostname2-1', 'hostname2-2', 'hostname2-3', 'hostname2-4', 'hostname2-5',
               'hostname2-6', 'hostname2-7', 'hostname2-8', 'hostname2-9', 'hostname2-10',
               'hostname1-1', 'hostname1-2', 'hostname1-3', 'hostname1-4', 'hostname1-5',
               'hostname1-6', 'hostname1-7', 'hostname1-8', 'hostname1-9', 'hostname1-10',
               'hostname3-1', 'hostname3-2', 'hostname3-3', 'hostname3-4', 'hostname3-5',
               'hostname3-6', 'hostname3-7', 'hostname3-8', 'hostname3-9', 'hostname3-10']
    partitions = [10, 9, 8, 7, 6, 5, 4, 3, 2, 1]
    assert DistributedLogbrokerWorker._partitioner('hostname1-1', members, partitions) == [1]
    assert DistributedLogbrokerWorker._partitioner('hostname2-1', members, partitions) == [2]
    assert DistributedLogbrokerWorker._partitioner('hostname3-1', members, partitions) == [3]
    assert DistributedLogbrokerWorker._partitioner('hostname1-10', members, partitions) == [4]
    assert DistributedLogbrokerWorker._partitioner('hostname2-10', members, partitions) == [5]
    assert DistributedLogbrokerWorker._partitioner('hostname3-10', members, partitions) == [6]
    assert DistributedLogbrokerWorker._partitioner('hostname1-2', members, partitions) == [7]
    assert DistributedLogbrokerWorker._partitioner('hostname2-2', members, partitions) == [8]
    assert DistributedLogbrokerWorker._partitioner('hostname3-2', members, partitions) == [9]
    assert DistributedLogbrokerWorker._partitioner('hostname1-3', members, partitions) == [10]
    assert DistributedLogbrokerWorker._partitioner('hostname2-3', members, partitions) == []
    assert DistributedLogbrokerWorker._partitioner('hostname3-3', members, partitions) == []
    assert DistributedLogbrokerWorker._partitioner('hostname2-4', members, partitions) == []
    assert DistributedLogbrokerWorker._partitioner('hostname3-8', members, partitions) == []


def test_partitioner_workers_more_than_partitions_unequal_workers():
    members = ['hostname2-1', 'hostname2-2', 'hostname2-3', 'hostname2-4', 'hostname2-5',
               'hostname2-6', 'hostname2-7', 'hostname2-8', 'hostname2-9', 'hostname2-10',
               'hostname1-1', 'hostname1-2', 'hostname1-3', 'hostname1-4', 'hostname1-5',
               'hostname1-6', 'hostname1-7', 'hostname1-8', 'hostname1-9', 'hostname1-10',
               'hostname3-1', 'hostname3-2']
    partitions = [10, 9, 8, 7, 6, 5, 4, 3, 2, 1]
    assert DistributedLogbrokerWorker._partitioner('hostname1-1', members, partitions) == [1]
    assert DistributedLogbrokerWorker._partitioner('hostname2-1', members, partitions) == [2]
    assert DistributedLogbrokerWorker._partitioner('hostname3-1', members, partitions) == [3]
    assert DistributedLogbrokerWorker._partitioner('hostname1-10', members, partitions) == [4]
    assert DistributedLogbrokerWorker._partitioner('hostname2-10', members, partitions) == [5]
    assert DistributedLogbrokerWorker._partitioner('hostname3-2', members, partitions) == [6]
    assert DistributedLogbrokerWorker._partitioner('hostname1-2', members, partitions) == [7]
    assert DistributedLogbrokerWorker._partitioner('hostname2-2', members, partitions) == [8]
    assert DistributedLogbrokerWorker._partitioner('hostname1-3', members, partitions) == [9]
    assert DistributedLogbrokerWorker._partitioner('hostname2-3', members, partitions) == [10]

    assert DistributedLogbrokerWorker._partitioner('hostname1-4', members, partitions) == []
    assert DistributedLogbrokerWorker._partitioner('hostname2-4', members, partitions) == []
    assert DistributedLogbrokerWorker._partitioner('hostname1-5', members, partitions) == []
    assert DistributedLogbrokerWorker._partitioner('hostname2-5', members, partitions) == []
    assert DistributedLogbrokerWorker._partitioner('hostname1-6', members, partitions) == []
    assert DistributedLogbrokerWorker._partitioner('hostname2-6', members, partitions) == []
