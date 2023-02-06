# -*- coding: utf-8 -*-

from unittest import TestCase

from nose.tools import (
    assert_raises,
    eq_,
    ok_,
)
from passport.backend.core.test.consts import (
    TEST_TRACK_ID1,
    TEST_TRACK_ID2,
)
from passport.backend.core.test.test_utils import with_settings_hosts
from passport.backend.core.tracks.faker import FakeTrackIdGenerator
from passport.backend.core.tracks.utils import create_track_id


@with_settings_hosts()
class TestFakeTrackIdGenerator(TestCase):
    def setUp(self):
        super(TestFakeTrackIdGenerator, self).setUp()
        self._faker = FakeTrackIdGenerator()

    def tearDown(self):
        del self._faker
        super(TestFakeTrackIdGenerator, self).tearDown()

    def test_patch_not_started(self):
        track_id1 = create_track_id()
        track_id2 = create_track_id()
        ok_((track_id1, track_id2) != (TEST_TRACK_ID1, TEST_TRACK_ID1))

    def test_set_return_value(self):
        self._faker.start()
        try:
            self._faker.set_return_value(TEST_TRACK_ID1)
            eq_(create_track_id(), TEST_TRACK_ID1)
            eq_(create_track_id(), TEST_TRACK_ID1)
        finally:
            self._faker.stop()

    def test_set_side_effect(self):
        self._faker.start()
        try:
            self._faker.set_side_effect([TEST_TRACK_ID1, TEST_TRACK_ID2])
            eq_(create_track_id(), TEST_TRACK_ID1)
            eq_(create_track_id(), TEST_TRACK_ID2)
        finally:
            self._faker.stop()

    def test_unable_to_start_twice(self):
        self._faker.start()
        with assert_raises(RuntimeError):
            self._faker.start()
        self._faker.stop()

    def test_unable_to_stop_nonstarted(self):
        with assert_raises(RuntimeError):
            self._faker.stop()
