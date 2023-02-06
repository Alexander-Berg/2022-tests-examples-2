import pytest

from sandbox.projects.yabs.qa.tasks.YabsServerB2BFuncShootCmp.utils.analyze_logs import (
    Agg, GroupBy, Func,
    _get_iterable_by_groupby, _get_iterable_by_tuple,
    _get_iterable_by_function, _build_aggregated, aggregate_statistics,
    hitlogid_bannerid_eventcost_rank, hitlogid_bannerid_billcost_rank,
    hitlogid_bannerid_clicks, hitlogid_bannerid_shows,
    merge_dict_pair, merge_dicts,
)
from sandbox.projects.yabs.qa.tasks.YabsServerB2BFuncShootCmp.utils.operations import avg, size


@pytest.fixture
def log_dict():
    return {
        'HitLogID': [1, 1, 2, 2, 3],
        'BannerID': [4, 4, 5, 6, 7],
        'EventCost': [0, 10, 11, 12, 13],
        'BillCost': [0, 8, 9, 9, 10],
        'Rank': [100, 100, 100, 100, 100],
        'CounterType': [1, 1, 1, 2, 2],
    }


def test_get_iterable_by_groupby(log_dict):
    field = GroupBy(('HitLogID', 'BannerID'), Agg('EventCost', 'max'), '')
    result = _get_iterable_by_groupby(log_dict, field)
    assert list(result) == [10, 11, 12, 13]
    field = GroupBy(('HitLogID', 'BannerID'), (Agg('EventCost', 'max'), ), '')
    result = _get_iterable_by_groupby(log_dict, field)
    assert list(result) == [10, 11, 12, 13]


def test_get_iterable_by_tuple(log_dict):
    field = (GroupBy(('HitLogID', 'BannerID'), Agg('EventCost', 'max'), ''), GroupBy(('HitLogID', 'BannerID'), Agg('Rank', 'max'), ''))
    result = _get_iterable_by_tuple(log_dict, field)
    assert list(result) == [1000, 1100, 1200, 1300]


def test_get_iterable_by_function(log_dict):
    def hitlogid_bannerid_eventcost(d):
        aggregated = _build_aggregated(d, GroupBy(('HitLogID', 'BannerID'), (Agg('EventCost', 'max'), Agg('Rank', 'max')), ''))
        return aggregated['EventCost']['max'] * aggregated['Rank']['max']
    result = _get_iterable_by_function(log_dict, Func(hitlogid_bannerid_eventcost, 'some_name', tuple()))
    assert list(result) == [1000, 1100, 1200, 1300]


def test_aggregate_statistics_simple(log_dict):
    statistics = {
        'data': {
            'event': log_dict
        },
        'counts': {
            'event': 5
        }
    }
    config = {
        'event': {
            'EventCost': [sum, avg],
            ('EventCost', 'Rank'): [sum, avg],
            'Rank': [avg],
            GroupBy(by=('HitLogID', 'BannerID'), aggs=Agg('EventCost', 'max'), name='MaxEventCost'): [sum, avg],
            Func(function=hitlogid_bannerid_eventcost_rank, name='dot(MaxEventCost, MaxRank)', used_fields=tuple()): [sum, avg],
            Func(function=hitlogid_bannerid_billcost_rank, name='dot(MaxBillCost, MaxRank)', used_fields=tuple()): [sum, avg],
            Func(function=hitlogid_bannerid_clicks, name='Clicks', used_fields=tuple()): [size],
            Func(function=hitlogid_bannerid_shows, name='Shows', used_fields=tuple()): [size],
        }
    }
    result = aggregate_statistics(statistics, config)
    assert dict(result) == {
        'event': {
            'EventCost.avg': 9.2,
            'EventCost.sum': 46,
            'dot(EventCost, Rank).avg': 920.0,
            'dot(EventCost, Rank).sum': 4600,
            'dot(MaxEventCost, MaxRank).sum': 4600,
            'dot(MaxEventCost, MaxRank).avg': 1150.0,
            'dot(MaxBillCost, MaxRank).avg': 900.0,
            'dot(MaxBillCost, MaxRank).sum': 3600,
            'MaxEventCost.avg': 11.5,
            'MaxEventCost.sum': 46,
            'Rank.avg': 100.0,
            'size': 5,
            'Shows.size': 2,
            'Clicks.size': 2
        }
    }


class TestMergeDicts(object):
    @pytest.mark.parametrize(('a', 'b', 'expected_merge_result'), (
        ({}, {}, {}),
        ({'a': 1}, {}, {'a': 1}),
        ({'a': 1}, {'b': 2}, {'a': 1, 'b': 2}),
        ({'a': {'b': 2}}, {'a': {'c': 3}}, {'a': {'c': 3, 'b': 2}}),
        ({'a': ['b']}, {'a': ['c']}, {'a': ['b', 'c']}),
    ))
    def test_merge_pair(self, a, b, expected_merge_result):
        assert expected_merge_result == merge_dict_pair(a, b)

    @pytest.mark.parametrize(('a', 'b'), (
        ({'a': 1}, {'a': 2}),
        ({'a': {'b': 2}}, {'a': ['c']}),
    ))
    def test_merge_pair_exception(self, a, b):
        with pytest.raises(TypeError):
            merge_dict_pair(a, b)

    @pytest.mark.parametrize(('dicts', 'expected_merge_result'), (
        ([], {}),  # empty
        ([{'a': [1]}], {'a': [1]}),  # single dict
        ([{'a': [1]}, {'a': [2]}, {'a': [3]}], {'a': [1, 2, 3]}),  # odd amount of dicts
    ))
    def test_merge_dicts(self, dicts, expected_merge_result):
        assert expected_merge_result == merge_dicts(*dicts)
