# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import json
import time

from nose.tools import eq_
from passport.backend.core.builders.blackbox.faker.blackbox import blackbox_get_track_response
from passport.backend.core.models.persistent_track import (
    generate_track_id,
    PersistentTrack,
)
from passport.backend.core.test.test_utils.utils import with_settings_hosts
from passport.backend.dbscripts.persistent_tracks_cleaner.cli import cleanup_persistent_tracks
from passport.backend.dbscripts.test.base import TestCase
from passport.backend.dbscripts.test.consts import PDD_UID_BOUNDARY


TEST_UID = 1
TEST_PDD_UID = PDD_UID_BOUNDARY + 1
TEST_PDD_UID_2 = PDD_UID_BOUNDARY + 2
TEST_TRACK_ID = '123456781234567890abcdef90abcdef'

TEST_CREATED_TIMESTAMP = int(time.time())
TEST_EXPIRED_DELTA = 1000
TEST_EXPIRED_TIMESTAMP = TEST_CREATED_TIMESTAMP + TEST_EXPIRED_DELTA

TEST_CONTENT = {'type': 1}


@with_settings_hosts()
class TestCleanupPersistentTracks(TestCase):
    def serialize_track(self, uid=TEST_UID, track_id=TEST_TRACK_ID, created=TEST_CREATED_TIMESTAMP,
                        expired=TEST_EXPIRED_TIMESTAMP, content=TEST_CONTENT):
        bb_response = json.loads(blackbox_get_track_response(
            uid,
            track_id,
            created=created,
            expired=expired,
            content=content,
        ))
        track = PersistentTrack().parse(bb_response)
        self._db_faker._serialize_to_eav(track)

    def test_no_tracks(self):
        cleanup_persistent_tracks(limit=1)

        for db in ('passportdbshard1', 'passportdbshard2'):
            eq_(len(self._db_faker.select('tracks', db=db)), 0)

    def test_multiple_iterations_all_tracks_deleted(self):
        for uid in (TEST_UID, TEST_PDD_UID, TEST_PDD_UID_2):
            for _ in range(4):
                self.serialize_track(uid, generate_track_id(), expired=int(time.time() - 1))

        cleanup_persistent_tracks(limit=3)

        for db in ('passportdbshard1', 'passportdbshard2'):
            eq_(len(self._db_faker.select('tracks', db=db)), 0)

        # В шарде 1 было 4 трека - с лимитом 3 нужно 2 запроса
        eq_(self._db_faker.query_count('passportdbshard1'), 2)
        # В шарде 2 было 8 треков - с лимитом 3 нужно 3 запроса
        eq_(self._db_faker.query_count('passportdbshard2'), 3)

    def test_multiple_iterations_with_mixed_tracks(self):
        for uid in (TEST_UID, TEST_PDD_UID):
            for _ in range(4):
                self.serialize_track(uid, generate_track_id(), expired=int(time.time() - 1))
                self.serialize_track(uid, generate_track_id())

        cleanup_persistent_tracks(limit=1)

        for db in ('passportdbshard1', 'passportdbshard2'):
            eq_(len(self._db_faker.select('tracks', db=db)), 4)

        # Число удаленных треков укладывается в лимит, поэтому
        # запросов на один больше чем удаленных треков
        eq_(self._db_faker.query_count('passportdbshard1'), 5)
        eq_(self._db_faker.query_count('passportdbshard2'), 5)
