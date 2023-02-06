from __future__ import absolute_import, print_function, unicode_literals

import time
import itertools as it
import collections

import pytest

from sandbox.common import itertools

abc = getattr(collections, "abc", collections)


class TestItertools(object):

    class SleepMock(object):

        def __init__(self):
            self.ticks = []
            self.tick = 0
            self.slept = 0

        def __call__(self, wait_time):
            self.tick = wait_time
            self.slept += wait_time
            self.ticks.append(wait_time)

        def time(self):
            return self.slept

    @pytest.mark.parametrize(
        "tick, max_tick, max_wait, sleep_first",
        [
            (3, 10, 100, False),
            (3, 10, 100, True),
            (3, 10, float("inf"), False),
        ]
    )
    def test__progressive_yielder(self, monkeypatch, tick, max_tick, max_wait, sleep_first):

        sleeper = self.SleepMock()
        monkeypatch.setattr(time, "time", sleeper.time)

        yielder = itertools.progressive_yielder(tick, max_tick, max_wait, sleep_first=sleep_first, sleep_func=sleeper)
        assert isinstance(yielder, abc.Iterator)

        tick_limit = 1000
        list(it.islice(yielder, tick_limit))  # Avoid infinite loop

        m = -1
        for wait_time in sleeper.ticks[:-1]:  # the last one may be shorter due to `max_wait`
            assert m <= wait_time, "A non-decreasing sequence was expected!"
            m = wait_time

        assert max(sleeper.ticks) <= max_tick

        if max_wait == float("inf"):
            assert len(sleeper.ticks) <= tick_limit
        else:
            assert sum(sleeper.ticks) == max_wait

    class Checker(object):

        def __init__(self, n):
            self.i = 0
            self.n = n

        def __call__(self):
            if self.i == self.n:
                return 42
            else:
                self.i += 1
                return False

    @pytest.mark.parametrize("n, inverse", [(0, False), (3, False), (float("inf"), False), (10, True)])
    def test__progressive_waiter(self, monkeypatch, n, inverse):
        sleeper = self.SleepMock()
        monkeypatch.setattr(time, "time", sleeper.time)
        ret, slept = itertools.progressive_waiter(
            1, 10, 30, checker=self.Checker(n), sleep_first=False, sleep_func=sleeper, inverse=inverse
        )
        if inverse:
            assert not sleeper.ticks
        else:
            # Returned successfully OR stopped after `max_wait`
            assert len(sleeper.ticks) == n or ret is False

    COMMON_CHAIN_TESTS = [
        [(), []],
        [((),), []],
        [(1,), [1]],
        [(1, (2,)), [1, 2]],
        [(1, 2, 3), [1, 2, 3]],
        ["cba", ["c", "b", "a"]],
        [("abcdef",), ["abcdef"]],
        [(b"abcdef",), [b"abcdef"]],
        [("abc", [1], [], (2, 3), {b"foo": 42}), ["abc", 1, 2, 3, b"foo"]],
        [("abc", None, [0, 0.0], (False, )), ["abc", None, 0, 0.0, False]],
    ]
    NON_RECURSIVE_CHAIN_TESTS = [
        [(([],),), [[]]],
        [(("abc", (None, {})), [0, 0.0], (False, {1: 0})), ["abc", (None, {}), 0, 0.0, False, {1: 0}]],
    ]
    RECURSIVE_CHAIN_TESTS = [
        [(([],),), []],
        [(("abc", (None, {})), [0, 0.0], (False, {1: 0})), ["abc", None, 0, 0.0, False, 1]],
    ]

    @pytest.mark.parametrize(
        "args, recurse, expected",
        [[args, False, expected] for args, expected in COMMON_CHAIN_TESTS] +
        [[args, True, expected] for args, expected in COMMON_CHAIN_TESTS] +
        [[args, False, expected] for args, expected in NON_RECURSIVE_CHAIN_TESTS] +
        [[args, True, expected] for args, expected in RECURSIVE_CHAIN_TESTS]
    )
    def test__chain(self, args, recurse, expected):
        result = itertools.chain(*args, recurse=recurse)
        assert isinstance(result, abc.Iterator)
        assert list(result) == expected

    @pytest.mark.parametrize(
        "args, expected",
        [
            [(), []],
            [(1,), [1]],
            [(1, 2, 3), [1, 2, 3]],
            [("abcdef",), ["abcdef"]],
            [(b"abcdef",), [b"abcdef"]],
            [("abc", [1], [], (2, 3), {b"foo": 42}), ["abc", 1, 2, 3, b"foo"]],
            [("abc", None, [0, 0.0], (False, None)), ["abc", 0, 0.0, False]],
        ]
    )
    def test__as_list(self, args, expected):
        result = itertools.as_list(*args)
        assert isinstance(result, list)
        assert result == expected

    @pytest.mark.parametrize(
        "iterable, n, expected",
        [
            ([], 10, []),
            ([1, 2, 3, 4, 5], 1, [[1], [2], [3], [4], [5]]),
            ("ABCDEFG", 3, [["A", "B", "C"], ["D", "E", "F"], ["G"]]),
        ]
    )
    def test__grouper(self, iterable, n, expected):
        result = itertools.grouper(iterable, n)
        assert isinstance(result, abc.Iterator)
        assert list(result) == expected

    @pytest.mark.parametrize(
        "args, kwargs, expected",
        [
            [([1, 2, 3, 4, 5], 4), {}, [(1, 2, 3, 4), (5, None, None, None)]],
            [("ABCDE", 2), {"fillvalue": "x"}, [("A", "B"), ("C", "D"), ("E", "x")]],
        ]
    )
    def test__grouper_longest(self, args, kwargs, expected):
        result = itertools.grouper_longest(*args, **kwargs)
        assert isinstance(result, abc.Iterator)
        assert list(result) == expected

    @pytest.mark.parametrize(
        "data, size, expected",
        [
            ([], 10, []),
            ([1, 2, 3, 4, 5], 1, [[1], [2], [3], [4], [5]]),
            ([1, 2, 3, 4, 5], 3, [[1, 2, 3], [4, 5]]),
            ([1, 2, 3, 4, 5], 100, [[1, 2, 3, 4, 5]]),
            ("ABCDEFG", 3, ["ABC", "DEF", "G"]),
        ]
    )
    def test__grouper_chunker(self, data, size, expected):
        result = itertools.chunker(data, size)
        assert isinstance(result, abc.Iterator)
        assert list(result) == expected

    @pytest.mark.parametrize(
        "d1, d2, expected",
        [
            ({"a": 1}, 1, 1),
            (1, 2, 2),
            (1, {"b": 1}, 1),
            ({"a": 1, "b": 2}, {"c": 3, "d": 4}, {"a": 1, "b": 2, "c": 3, "d": 4}),
            (
                {"a": 1, "b": 2, "z": 100},
                {"a": 10, "b": 20, "c": 30},
                {"a": 10, "b": 20, "c": 30, "z": 100}),
            (
                {"a": {"b": 2, "c": 3}, "b": 2},
                {"a": {"b": 20, "d": 4}, "b": {"z": 100}},
                {"a": {"b": 20, "c": 3, "d": 4}, "b": {"z": 100}}
            ),
            (
                {"a": {"b": {"c": {"d": 1}}}},
                {"a": {"b": {"c": {"e": 2}}}},
                {"a": {"b": {"c": {"d": 1, "e": 2}}}},
            ),
        ]
    )
    def test__merge_dicts(self, d1, d2, expected):
        result = itertools.merge_dicts(d1, d2)
        assert result == expected

        if isinstance(result, dict):
            assert id(result) not in (id(d1), id(d2))  # ensure a copy is made

    def test__count(self):
        assert itertools.count([1, 2, 3]) == 3
        assert itertools.count(i for i in range(500)) == 500

        def gen():
            yield "hello"
            yield "world"

        assert itertools.count(gen()) == 2
