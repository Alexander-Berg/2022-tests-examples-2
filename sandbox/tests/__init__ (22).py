from __future__ import absolute_import

import random
import threading
import collections
import datetime as dt
import itertools as it

import six

from sandbox.common import rest
from sandbox.common import statistics
from sandbox.common import itertools as cit
from sandbox.common.types import statistics as ctst


class CustomHandler(statistics.SignalHandler):
    types = ("anything_goes", "test_signal")

    def handle(self, signal_type, signals):
        pass


class GeneralHandler(statistics.SignalHandler):
    types = (ctst.ALL_SIGNALS,)

    def handle(self, signal_type, signals):
        pass


class TestSignaler(object):
    def test__signaler(self, monkeypatch):
        values = []

        def handle(_, __, ss):
            with threading.RLock():
                values.extend(ss)

        for class_ in (CustomHandler, GeneralHandler):
            class_.handle = handle

        monkeypatch.setattr(statistics.Signaler(enabled=True), "enabled", True)
        statistics.Signaler().register(CustomHandler(), GeneralHandler())
        sigcount = 100
        stypes = [
            random.choice(CustomHandler.types + ("abcdef", "nonsense"))
            for _ in six.moves.range(sigcount)
        ]
        custom_count = cit.count(filter(lambda s: s in CustomHandler.types, stypes))

        for st in stypes:
            statistics.Signaler().push(dict(
                type=st,
                hitcount=1234,
                omg="wtf",
            ))
        statistics.Signaler().wait()
        assert len(values) == sigcount + custom_count


class TestAggregatingSignalHandler(object):
    def test__basic_aggregation(self, monkeypatch):
        processed = []

        def handle(_, __, data, *___, **____):
            processed.extend(data)

        timestamp_fields = ["date", "timestamp"]
        aggregate_by = ("optype", "opkind")
        sum_by = ("count", "duration")
        fixed_args = dict(
            fixed_arg=1234,
            another_arg=5678,
        )

        monkeypatch.setattr(rest.Client, "create", handle)
        handler = statistics.AggregatingClientSignalHandler(
            aggregate_by=aggregate_by,
            sum_by=sum_by,
            fixed_args=fixed_args
        )

        optypes, opkinds = ["abc", "def"], ["ghi", "jkl"]
        cnt = 1000
        values = [(1, random.randint(0, 100)) for _ in six.moves.range(cnt)]
        utcnow = dt.datetime.utcnow()

        signals = [
            dict(
                type=ctst.SignalType.TASK_OPERATION,
                optype=random.choice(optypes),
                opkind=random.choice(opkinds),
                count=values[i][0],
                duration=values[i][1],
                date=utcnow,
                timestamp=utcnow,
            )
            for i in six.moves.range(cnt)
        ]
        handler.handle(ctst.SignalType.TASK_OPERATION, signals)

        # all signals have the same datetime, which is also a string
        timestamps = set(it.chain.from_iterable(
            [
                processed_signal[ts_field]
                for ts_field in timestamp_fields
            ]
            for processed_signal in processed
        ))
        assert len(timestamps) == 1
        ts = next(iter(timestamps), None)
        assert isinstance(ts, six.string_types)

        # all signals have the same fixed arguments
        for argument in fixed_args.keys():
            assert all(
                _[argument] == fixed_args[argument]
                for _ in processed
            )

        # for every unique tuple of values to aggregate by, sums must be the same
        manually_aggregated_values = collections.defaultdict(collections.Counter)
        for signal in signals:
            key = tuple(map(signal.get, aggregate_by))
            for key_to_increase in sum_by:
                manually_aggregated_values[key][key_to_increase] += signal[key_to_increase]

        for processed_signal in processed:
            key = tuple(map(processed_signal.get, aggregate_by))
            for key_to_increase in sum_by:
                assert manually_aggregated_values[key][key_to_increase] == processed_signal[key_to_increase]
