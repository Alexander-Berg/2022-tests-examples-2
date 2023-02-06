from __future__ import absolute_import

import time
import threading as th

from rem_to_step import distributed

import pytest

NODES = 5
MAX_SEQUENCE = 1000


def _counter_loop(node, result):
    while True:
        i = node.version + 1
        try:
            node.version = i
            result.append(i)
        except node.NotLeader:
            time.sleep(1)
            continue
        finally:
            if i >= MAX_SEQUENCE or len(result) >= MAX_SEQUENCE:
                break


@pytest.mark.rem2step
def test__concurrency(port_manager):
    ports = [port_manager.get_port() for _ in xrange(NODES)]
    nodes_config = [{"id": i, "host": "localhost", "port": ports[i]} for i in xrange(NODES)]
    nodes = [distributed.Node(i, nodes_config) for i in xrange(len(nodes_config))]
    result = []

    map(distributed.Node.start, nodes)
    threads = [th.Thread(target=_counter_loop, args=(node, result)) for node in nodes]
    map(th.Thread.start, threads)
    map(th.Thread.join, threads)
    try:
        assert len(result) == MAX_SEQUENCE, result
        assert result == range(1, MAX_SEQUENCE + 1), result
    finally:
        map(distributed.Node.stop, nodes)
