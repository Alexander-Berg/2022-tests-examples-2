import pytest

from noc.grad.grad.lib.fns import FNS, format_fn_args
from noc.grad.grad.lib.structures import FrozenDict


class TestFNS:
    @pytest.fixture
    def fns(self):
        keys = ("counter1", "counter2", "counter3")
        res = FNS(keys)
        res.add_all("all_fn", 1)
        res.add_all("all_fn2", 1)
        res.add("counter1", "counter1_fn")
        res.add("counter2", "counter1_fn")
        res.add("counter3", "counter3_fn")
        return res

    def test_group_by_fn(self, fns):
        assert fns.group_by_fn() == {
            ('all_fn2', 'all_fn', 'counter3_fn'): ['counter3'],
            ('all_fn2', 'all_fn', 'counter1_fn'): ['counter1', 'counter2'],
        }

    def test_group_by_stage(self, fns):
        assert fns.group_by_stage() == {
            'stage1': ['all_fn2', 'all_fn'],
            'stage2': {('counter1_fn',): ['counter1', 'counter2'], ('counter3_fn',): ['counter3']},
        }

    def test_group_by_stage_only_2(self):
        keys = ("counter1", "counter2")
        fns = FNS(keys)
        fns.add_all("all_fn", 1)
        fns.add_all("all_fn2", 1)
        assert fns.group_by_stage() == {
            'stage1': ['all_fn2', 'all_fn'],
            'stage2': {},
        }

        fns = FNS(keys)
        fns.add("counter1", ["fn1", "fn2"])
        fns.add("counter2", "fn1")
        assert fns.group_by_stage() == {"stage1": ["fn1"], "stage2": {("fn2",): ["counter1"]}}


def test_format_fn_args_immutables():
    sample_period = 31
    fn = ('resampler_repeat', FrozenDict({'max_delta': 1200, 'period': '{sample_period}'}))
    fmt = {'sample_period': sample_period}
    format_type = {'period': int}
    res = format_fn_args(fn, fmt, format_type)
    assert res == ('resampler_repeat', FrozenDict({'period': sample_period, 'max_delta': 1200}))


def test_format_fn_args_long():
    sample_period = 31
    fn = ('resampler_repeat', FrozenDict({'max_delta': 1200, 'resample': '{sample_period}'}))
    fmt = {'sample_period': sample_period}
    format_type = {'resample': int}
    res = format_fn_args(fn, fmt, format_type)
    assert res == ('resampler_repeat', FrozenDict({'resample': sample_period, 'max_delta': 1200}))
