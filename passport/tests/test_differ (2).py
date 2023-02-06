# -*- coding: utf-8 -*-
import unittest

import mock
from nose.tools import eq_
from passport.backend.core.differ import (
    Diff,
    EmptyDiff,
)
from passport.backend.core.test.test_utils import iterdiff
from passport.backend.core.tracks.differ import (
    differ,
    TrackDiff,
)


eq_ = iterdiff(eq_)


class TestDiffer(unittest.TestCase):
    def make_track(self, data=None, counters=None, lists=None):
        track = mock.Mock()
        track._data = data or {}
        track._counters = counters or {}
        track._lists = lists or {}
        return track

    def make_diff(self, added=None, changed=None, deleted=None):
        return Diff(
            added=added or {},
            changed=changed or {},
            deleted=deleted or {},
        )

    def test_data_diff(self):
        eq_(
            differ(
                self.make_track(data={'foo': '1', 'bar': '2', 'abc': ''}),
                self.make_track(data={'bar': '3', 'zar': '4', 'abc': None}),
            ),
            TrackDiff(
                data_diff=self.make_diff(
                    added={'zar': '4'},
                    changed={'bar': '3'},
                    deleted={'foo': None, 'abc': None},
                ),
                counter_diff=EmptyDiff,
                list_diff=EmptyDiff,
            ),
        )

    def test_counter_diff(self):
        eq_(
            differ(
                self.make_track(counters={'foo': 1, 'bar': 2, 'zar': 3, 'spam': '4'}),
                self.make_track(counters={'foo': 2, 'bar': 2, 'zar': 2}),
            ),
            TrackDiff(
                data_diff=EmptyDiff,
                counter_diff=self.make_diff(
                    changed={'foo': 1, 'zar': -1},
                    deleted={'spam': None},
                ),
                list_diff=EmptyDiff,
            ),
        )

    def test_list_append_diff(self):
        eq_(
            differ(
                self.make_track(lists={'foo': ['1', '2'], 'bar': ['4']}),
                self.make_track(lists={'foo': ['1', '2', '3'], 'bar': ['4']}),
            ),
            TrackDiff(
                data_diff=EmptyDiff,
                counter_diff=EmptyDiff,
                list_diff=self.make_diff(
                    added={'foo': ['3']},
                ),
            ),
        )

    def test_list_change_diff(self):
        eq_(
            differ(
                self.make_track(lists={'foo': ['1', '2']}),
                self.make_track(lists={'foo': ['2', '3']}),
            ),
            TrackDiff(
                data_diff=EmptyDiff,
                counter_diff=EmptyDiff,
                list_diff=self.make_diff(
                    added={'foo': ['2', '3']},
                    deleted={'foo': None},
                ),
            ),
        )

    def test_diff_with_none(self):
        eq_(
            differ(
                None,
                self.make_track(
                    data={'foo': '1', 'bar': '2'},
                    counters={'foo': 1, 'bar': 2, 'zar': 3},
                    lists={'foo': ['1', '2'], 'bar': []},
                ),
            ),
            TrackDiff(
                data_diff=self.make_diff(
                    added={'foo': '1', 'bar': '2'},
                ),
                counter_diff=self.make_diff(
                    added={'foo': 1, 'bar': 2, 'zar': 3},
                ),
                list_diff=self.make_diff(
                    added={'foo': ['1', '2'], 'bar': []},
                ),
            ),
        )
