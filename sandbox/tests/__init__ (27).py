# coding: utf-8
from __future__ import absolute_import

import os
import time
import socket
import pytest
import threading
import responses

import six

from sandbox.common import utils
from sandbox.common import itertools as cit


@pytest.fixture()
def free_port():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('127.0.0.1', 0))
    addr, port = s.getsockname()
    s.close()
    return port


class TestUtils(object):
    def test__lock_on_port(self, free_port):
        sock = utils.lock_on_port(free_port)
        assert sock
        pytest.raises(socket.error, utils.lock_on_port, free_port)


@pytest.fixture()
def mocked_checker_fetcher():
    def wrapped(data, **kwargs):
        url = "http://foo.bar"
        with responses.RequestsMock() as rsps:
            rsps.add(responses.GET, url, body=data)
            return list(utils.checker_fetcher(url, **kwargs))
    return wrapped


class TestCheckerFetcher(object):
    DATA = b"aaaabbbbccccdddd"
    CHECKSUM = "e2a36397b7788625a6da6c7215a83a04"

    def test__failed_checksum(self, mocked_checker_fetcher):
        with pytest.raises(ValueError):
            mocked_checker_fetcher(self.DATA, md5="FAIL")

    @pytest.mark.parametrize("kwargs", [
        {"chunk_size": 1},
        {"chunk_size": 1, "md5": CHECKSUM},
        {"md5": CHECKSUM},
    ])
    def test__checker_fetcher(self, mocked_checker_fetcher, kwargs):
        result = mocked_checker_fetcher(data=self.DATA, **kwargs)
        assert b"".join(result) == self.DATA


class TestLocks(object):

    @staticmethod
    def try_lock(lock):
        if isinstance(lock, six.string_types):
            lock = utils.RFLock(lock)
        with lock:
            time.sleep(1)

    @staticmethod
    def start_and_wait_threads(threads, ttl):
        start = time.time()
        cit.count(map(lambda _: _.start(), threads))
        cit.count(map(lambda _: _.join(), threads))
        assert ttl < time.time() - start < ttl + 1

    def test__rflock(self, tmpdir):
        lock_path = os.path.join(str(tmpdir), "lock")
        lock = utils.RFLock(lock_path)

        for arg in (lock, lock_path):
            threads = [threading.Thread(target=self.try_lock, args=(arg,)) for _ in range(3)]
            self.start_and_wait_threads(threads, len(threads))

    def test__rflock_recursively(self, tmpdir):
        lock = utils.RFLock(os.path.join(str(tmpdir), "lock"))

        def recursive_lock(depth=2):
            with lock:
                if depth:
                    recursive_lock(depth - 1)

        recursive_lock()

    def test__nonblocking(self, tmpdir):
        fname = os.path.join(str(tmpdir), "lock")
        utils.FLock(fname).acquire(False)
        with pytest.raises(IOError):
            utils.FLock(fname).acquire(False)


@pytest.mark.parametrize(
    ("start", "current", "finish", "expected"),
    [
        (0, 5, 100, 5),
        (0, 0, 0, 100),
        (1, 3, 5, 50),
        (1, 7, 5, 100),
        (1, 2, 4, 33),
    ]
)
def test__progress(start, current, finish, expected):
    assert utils.progress(start, current, finish) == expected


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("AMD EPYC 7351 16-Core Processor", "AMD"),

        ("Intel(R) Xeon(R) CPU           E5645  @ 2.40GHz", "E5645"),
        ("Intel(R) Xeon(R) CPU E5-2650 v2 @ 2.60GHz", "E5-2650 v2"),
        ("Intel(R) Xeon(R) CPU E5-2660 0 @ 2.20GHz", "E5-2660 0"),
        ("Intel(R) Xeon(R) CPU E5-2660 v4 @ 2.00GHz", "E5-2660 v4"),
        ("Intel(R) Xeon(R) CPU E5-2683 v4 @ 2.10GHz", "E5-2683 v4"),
        ("Intel(R) Xeon(R) CPU E5-2667 v2 @ 3.30GHz", "E5-2667 v2"),
        ("Intel(R) Xeon(R) CPU E5-2667 v4 @ 3.20GHz", "E5-2667 v4"),
        ("Intel(R) Xeon(R) Gold 6230 CPU @ 2.10GHz", "Gold 6230"),

        ("Intel(R) Core(TM) i5-4278U CPU @ 2.60GHz", "i5-4278U"),
        ("Intel(R) Core(TM) i7-3720QM CPU @ 2.60GHz", "i7-3720QM"),
        ("Intel(R) Core(TM) i7-4578U CPU @ 3.00GHz", "i7-4578U"),
        ("Intel(R) Core(TM) i7-8700B CPU @ 3.20GHz", "i7-8700B"),
    ]
)
def test__cpu_parsing(raw, expected):
    parsed = utils.CPU.parse_cpu_model(raw)
    assert parsed and parsed == expected
