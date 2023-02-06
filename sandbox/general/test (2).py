#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys
import datetime

sys.path.append('../../')

from yt_runner import IntervalInfo, TolokaBudgetStrategy


def get_quantiles():
    return [{'quantile': 0.1, 'karma': 1.0},
        {'quantile': 0.2, 'karma': 1.0},
        {'quantile': 0.3, 'karma': 1.0},
        {'quantile': 0.4, 'karma': 2.0},
        {'quantile': 0.5, 'karma': 3.0},
        {'quantile': 0.6, 'karma': 4.0},
        {'quantile': 0.7, 'karma': 5.0},
        {'quantile': 0.8, 'karma': 6.0},
        {'quantile': 0.9, 'karma': 7.0},
        {'quantile': 1.0, 'karma': 8.0}]


def get_invervals():
    intervals = []
    date = datetime.datetime.strptime('2016-10-01 00:00', '%Y-%m-%d %H:%M')
    total = 0
    step = datetime.timedelta(days=1)
    for i in xrange(0, 20):
        delta = (1 + (i % 2)) * 100
        intervals.append(IntervalInfo(date + i * step, date + (i + 1) * step, total, total + delta))
        total += delta
    return intervals


class TestAutobudget(object):
    def setup_method(self, method):
        print 'setup'
        self.daily_limit = 100
        self.quantiles = get_quantiles()
        self.intervals = get_invervals()
        self.budget_strategy = TolokaBudgetStrategy(self.daily_limit, self.intervals, self.quantiles)
        self.segment_start = datetime.datetime.strptime('2016-10-09 00:00', '%Y-%m-%d %H:%M')
        self.segment_end = datetime.datetime.strptime('2016-10-10 00:00', '%Y-%m-%d %H:%M')

    def test_get_banners_count(self):
        result = self.budget_strategy.get_banners_count(self.segment_start, self.segment_end)
        assert result == 100

        segment_end = self.segment_start
        result = self.budget_strategy.get_banners_count(self.segment_start, segment_end)
        assert result == 0

        segment_end = self.segment_start + datetime.timedelta(hours=12)
        result = self.budget_strategy.get_banners_count(self.segment_start, segment_end)
        assert result == 50

        segment_start = self.segment_start - datetime.timedelta(days=1)
        segment_end = self.segment_start
        result = self.budget_strategy.get_banners_count(segment_start, segment_end)
        assert result == 200

    def test_compure_segment_limit(self):
        segment_start = self.segment_start
        segment_end = self.segment_end
        result = self.budget_strategy.compute_segment_limit(segment_start, segment_end)
        assert result == 100

        segment_start = self.segment_start
        segment_end = segment_start + datetime.timedelta(hours=6)
        result = self.budget_strategy.compute_segment_limit(segment_start, segment_end)
        assert result == 25

    def test_compute_expected_segment_count(self):
        result = self.budget_strategy.compute_expected_segment_count(self.segment_start, self.segment_end)
        assert result == 400

        segment_start = self.segment_end
        segment_end = segment_start + datetime.timedelta(days=1)
        result = self.budget_strategy.compute_expected_segment_count(segment_start, segment_end)
        assert result == 50

    def test_compute_quantile(self):
        assert self.budget_strategy.compute_quantile(10, 100) == 0.1
        assert self.budget_strategy.compute_quantile(25, 100) == 0.25

    def test_compute_karma_threshold(self):
        result = self.budget_strategy.compute_karma_threshold(self.segment_start, self.segment_end)
        assert result == {'threshold': 1, 'probability': 1}

    def test_get_karma_threshold(self):
        assert self.budget_strategy.get_karma_threshold(0.1) == {'threshold': 1, 'probability': 1.0/3}
        assert self.budget_strategy.get_karma_threshold(0.2) == {'threshold': 1, 'probability': 2.0/3}
        assert self.budget_strategy.get_karma_threshold(0.3) == {'threshold': 1, 'probability': 1}
        assert self.budget_strategy.get_karma_threshold(0.4) == {'threshold': 2, 'probability': 1}
        assert self.budget_strategy.get_karma_threshold(1.0) == {'threshold': 8, 'probability': 1}
