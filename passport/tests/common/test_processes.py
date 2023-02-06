# -*- coding: utf-8 -*-

import unittest

from nose.tools import ok_
from passport.backend.api.common.processes import is_process_allowed
from passport.backend.api.test.views import ViewsTestEnvironment
from passport.backend.core.test.test_utils.utils import with_settings_hosts
from passport.backend.core.tracks.track_manager import TrackManager


@with_settings_hosts()
class ProcessesTestCase(unittest.TestCase):
    def setUp(self):
        self.env = ViewsTestEnvironment()
        self.env.start()
        self.track_manager = TrackManager()
        self.track = self.track_manager.create('restore', 'passport')

    def tearDown(self):
        self.env.stop()
        del self.env
        del self.track_manager

    def test_process_allowed_with_no_track(self):
        """Трека нет - никаких ограничений не накладываем"""
        ok_(is_process_allowed(['process']))
        ok_(is_process_allowed(['process'], is_process_required=True))

    def test_process_allowed_with_no_process_name(self):
        """Имя процесса в треке не задано - никаких ограничений не накладываем"""
        ok_(is_process_allowed(['process'], track=self.track))
        ok_(is_process_allowed(['process'], track_id=self.track.track_id))

    def test_process_allowed_with_process_name(self):
        with self.track_manager.transaction(track=self.track).commit_on_error() as track:
            track.process_name = 'process 1'
        builtin_process_track = self.track_manager.create('restore', 'passport', process_name='process 2')

        ok_(is_process_allowed(['process 1', 'process 2'], track=self.track))
        ok_(is_process_allowed(['process 1', 'process 2'], track_id=self.track.track_id))
        ok_(is_process_allowed(['process 1', 'process 2'], track=builtin_process_track))

    def test_process_not_allowed_with_no_process_name_when_process_required(self):
        """Имя процесса в треке не задано, но выставлен флаг необходимости процесса"""
        ok_(not is_process_allowed(['process'], is_process_required=True, track=self.track))
        ok_(not is_process_allowed(['process'], is_process_required=True, track_id=self.track.track_id))

    def test_process_not_allowed(self):
        with self.track_manager.transaction(track=self.track).commit_on_error() as track:
            track.process_name = 'process 3'

        ok_(not is_process_allowed(['process 1', 'process 2'], track=self.track))
        ok_(not is_process_allowed([], track_id=self.track.track_id))
