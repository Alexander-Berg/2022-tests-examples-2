# -*- coding: utf-8 -*-
from datetime import (
    datetime,
    timedelta,
)
import json
import time
import unittest

import mock
from nose.tools import eq_
from passport.backend.core.builders.blackbox.faker.blackbox import blackbox_get_track_response
from passport.backend.core.db.faker.db import FakeDB
from passport.backend.core.db.faker.db_utils import eq_eav_queries
from passport.backend.core.db.schemas import tracks_table as tt
from passport.backend.core.db.utils import (
    delete_with_limit,
    encode_params_for_db,
)
from passport.backend.core.dbmanager.manager import find_sharded_dbm
from passport.backend.core.differ import diff
from passport.backend.core.models.persistent_track import PersistentTrack
from passport.backend.core.processor import run_eav
from passport.backend.core.serializers.persistent_track import (
    PersistentTrackCleanupQuery,
    PersistentTrackSerializer,
)
from passport.backend.core.serializers.runner import run_persistent_tracks_cleanup_query
from passport.backend.core.test.time_utils.time_utils import DatetimeNow
from passport.backend.utils.common import merge_dicts
from passport.backend.utils.time import unixtime_to_datetime


TEST_UID = 1
TEST_TRACK_ID = '123456781234567890abcdef90abcdef'
TEST_TRACK_ID_2 = '432156781234567890abcdef90abcdef'

TEST_EXPIRED_DELTA = 1000

TEST_CONTENT = {'type': 1}


class TestTrackSerializer(unittest.TestCase):
    def setUp(self):
        self.db = FakeDB()
        self.db.start()
        self.serializer = PersistentTrackSerializer()
        self.created_timestamp = int(time.time())
        self.blackbox_response = json.loads(blackbox_get_track_response(
            TEST_UID,
            TEST_TRACK_ID,
            created=self.created_timestamp,
            expired=self.created_timestamp + TEST_EXPIRED_DELTA,
            content=TEST_CONTENT,
        ))
        self.model_data = {
            'uid': TEST_UID,
            'track_id': TEST_TRACK_ID,
            'created': unixtime_to_datetime(self.created_timestamp),
            'expired': unixtime_to_datetime(self.created_timestamp + TEST_EXPIRED_DELTA),
            'content': json.dumps(TEST_CONTENT),
        }

    def tearDown(self):
        self.db.stop()
        del self.db

    def test_no_action_required(self):
        track = PersistentTrack().parse(self.blackbox_response)
        s1 = track.snapshot()
        queries = self.serializer.serialize(
            s1,
            track,
            diff(s1, track),
        )

        eq_eav_queries(queries, [])

    def test_create(self):
        track = PersistentTrack().parse(self.blackbox_response)

        queries = self.serializer.serialize(
            None,
            track,
            diff(None, track),
        )

        eq_eav_queries(
            queries,
            [
                tt.insert().values(**encode_params_for_db(self.model_data)),
            ],
        )

        run_eav(None, track, diff(None, track))

        self.db.check('tracks', 'track_id', TEST_TRACK_ID, db='passportdbshard1', **self.model_data)

    def test_create_with_helper(self):
        with mock.patch('passport.backend.core.models.persistent_track.generate_track_id', lambda: TEST_TRACK_ID):
            track = PersistentTrack.create(TEST_UID, 1)

        queries = self.serializer.serialize(
            None,
            track,
            diff(None, track),
        )

        expected_data = dict(
            self.model_data,
            created=DatetimeNow(),
            expired=DatetimeNow(),
        )
        eq_eav_queries(
            queries,
            [
                tt.insert().values(**encode_params_for_db(expected_data)),
            ],
        )

        run_eav(None, track, diff(None, track))

        self.db.check('tracks', 'track_id', TEST_TRACK_ID, db='passportdbshard1', **expected_data)

    def test_delete(self):
        track = PersistentTrack().parse(self.blackbox_response)
        queries = self.serializer.serialize(
            track,
            None,
            diff(track, None),
        )

        eq_eav_queries(
            queries,
            [
                tt.delete().where(tt.c.track_id == TEST_TRACK_ID.encode('utf8')),
            ],
        )

        self.db._serialize_to_eav(track)
        run_eav(track, None, diff(track, None))

        self.db.check_missing('tracks', track_id=TEST_TRACK_ID, db='passportdbshard1')

    def test_update_all_fields_ok(self):
        track = PersistentTrack().parse(self.blackbox_response)
        s1 = track.snapshot()
        track_id = s1.track_id

        track.uid = 2
        track.track_id = TEST_TRACK_ID_2
        track.created = unixtime_to_datetime(0)
        track.expired = unixtime_to_datetime(1)
        track.content = {}

        expected_params = {
            'uid': 2,
            'track_id': TEST_TRACK_ID_2,
            'created': unixtime_to_datetime(0),
            'expired': unixtime_to_datetime(1),
            'content': '{}',
        }

        queries = self.serializer.serialize(
            s1,
            track,
            diff(s1, track),
        )

        eq_eav_queries(
            queries,
            [
                tt.update().values(**encode_params_for_db(expected_params)).where(tt.c.track_id == track_id.encode('utf8')),
            ],
        )

        self.db._serialize_to_eav(s1)
        run_eav(s1, track, diff(s1, track))

        self.db.check_missing('tracks', track_id=TEST_TRACK_ID, db='passportdbshard1')
        self.db.check('tracks', 'track_id', TEST_TRACK_ID_2, db='passportdbshard1', **expected_params)

    def test_update_some_fields_ok(self):
        track = PersistentTrack().parse(self.blackbox_response)
        s1 = track.snapshot()
        track_id = track.track_id

        track.content = {'flag': 1, 'active': 0}
        track.expired = unixtime_to_datetime(1)

        expected_params = {
            'expired': unixtime_to_datetime(1),
            'content': '{"active": 0, "flag": 1}',
        }

        queries = self.serializer.serialize(
            s1,
            track,
            diff(s1, track),
        )

        eq_eav_queries(
            queries,
            [
                tt.update().values(**encode_params_for_db(expected_params)).where(tt.c.track_id == track_id.encode('utf8')),
            ],
        )

        self.db._serialize_to_eav(s1)
        run_eav(s1, track, diff(s1, track))

        self.db.check('tracks', 'track_id', TEST_TRACK_ID, db='passportdbshard1', **merge_dicts(self.model_data, expected_params))


def test_persistent_track_cleanup_query_without_offset():
    q = PersistentTrackCleanupQuery(limit=100)
    eq_eav_queries(
        [q],
        [
            delete_with_limit(tt, limit=100).where(tt.c.expired <= DatetimeNow()),
        ],
    )


def test_persistent_track_cleanup_query_with_offset():
    q = PersistentTrackCleanupQuery(limit=100, offset=60)
    eq_eav_queries(
        [q],
        [
            delete_with_limit(tt, limit=100).where(
                tt.c.expired <= DatetimeNow(timestamp=datetime.now() - timedelta(seconds=60)),
            ),
        ],
    )


class TestRunPersistentTracksCleanupQuery(unittest.TestCase):
    def setUp(self):
        self.db = FakeDB()
        self.db.start()
        self.created_timestamp = int(time.time())
        self.model_data = {
            'uid': TEST_UID,
            'track_id': TEST_TRACK_ID,
            'created': unixtime_to_datetime(self.created_timestamp),
            'expired': unixtime_to_datetime(self.created_timestamp + TEST_EXPIRED_DELTA),
            'content': json.dumps(TEST_CONTENT),
        }

    def tearDown(self):
        self.db.stop()
        del self.db

    def serialize_track(self, uid=TEST_UID, track_id=TEST_TRACK_ID, created=None,
                        expired=None, content=TEST_CONTENT):
        created = created or self.created_timestamp
        expired = expired or self.created_timestamp + TEST_EXPIRED_DELTA
        bb_response = json.loads(blackbox_get_track_response(
            uid,
            track_id,
            created=created,
            expired=expired,
            content=content,
        ))
        track = PersistentTrack().parse(bb_response)
        self.db._serialize_to_eav(track)

    def test_ok_track_not_expired(self):
        self.serialize_track()
        dbm = find_sharded_dbm(tt, TEST_UID)

        count = run_persistent_tracks_cleanup_query(dbm, 2)

        eq_(count, 0)
        self.db.check('tracks', 'track_id', TEST_TRACK_ID, db='passportdbshard1', **self.model_data)

    def test_ok_expired_track_removed(self):
        self.serialize_track(expired=self.created_timestamp - 1)
        self.serialize_track(track_id=TEST_TRACK_ID_2)
        dbm = find_sharded_dbm(tt, TEST_UID)

        count = run_persistent_tracks_cleanup_query(dbm, 2)

        eq_(count, 1)
        self.db.check_missing('tracks', track_id=TEST_TRACK_ID, db='passportdbshard1')
        self.db.check(
            'tracks',
            'track_id',
            TEST_TRACK_ID_2,
            db='passportdbshard1',
            **dict(self.model_data, track_id=TEST_TRACK_ID_2)
        )

    def test_ok_expired_track_not_removed_with_offset(self):
        semi_expired = self.created_timestamp - 2
        self.serialize_track(expired=semi_expired)
        self.serialize_track(track_id=TEST_TRACK_ID_2)
        dbm = find_sharded_dbm(tt, TEST_UID)

        count = run_persistent_tracks_cleanup_query(dbm, 2, offset=TEST_EXPIRED_DELTA / 2)

        eq_(count, 0)
        self.db.check(
            'tracks',
            'track_id',
            TEST_TRACK_ID,
            db='passportdbshard1',
            **dict(self.model_data, expired=unixtime_to_datetime(semi_expired))
        )
        self.db.check(
            'tracks',
            'track_id',
            TEST_TRACK_ID_2,
            db='passportdbshard1',
            **dict(self.model_data, track_id=TEST_TRACK_ID_2)
        )

    def test_ok_expired_track_not_removed_by_limit(self):
        self.serialize_track(expired=self.created_timestamp - 1)
        self.serialize_track(
            track_id=TEST_TRACK_ID_2,
            expired=self.created_timestamp - int(timedelta(hours=3, seconds=1).total_seconds()),
        )
        dbm = find_sharded_dbm(tt, TEST_UID)

        count = run_persistent_tracks_cleanup_query(dbm, 1)

        # Удалился один из треков, другой остался в базе
        eq_(count, 1)
        eq_(len(self.db.select('tracks', db='passportdbshard1')), 1)
