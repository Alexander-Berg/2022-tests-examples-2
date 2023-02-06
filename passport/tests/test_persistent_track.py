# -*- coding: utf-8 -*-
from datetime import (
    datetime,
    timedelta,
)
import time
import unittest

from nose.tools import (
    eq_,
    ok_,
)
from passport.backend.core.builders.blackbox.faker.blackbox import (
    blackbox_get_track_response,
    get_parsed_blackbox_response,
)
from passport.backend.core.models.persistent_track import (
    PERSISTENT_TRACK_ID_BYTES_COUNT,
    PersistentTrack,
    TRACK_TYPE_RESTORATION_AUTO_EMAIL_LINK,
)
from passport.backend.core.test.time_utils.time_utils import DatetimeNow
from passport.backend.core.undefined import Undefined
from passport.backend.utils.time import unixtime_to_datetime


TEST_UID = 1
TEST_TRACK_ID = '90abcdef90abcdef1234567812345678'
TEST_TRACK_KEY = '%s%x' % (TEST_TRACK_ID, TEST_UID)


class TestTrack(unittest.TestCase):
    def test_create_with_minimal_data(self):
        track = PersistentTrack.create(TEST_UID, TRACK_TYPE_RESTORATION_AUTO_EMAIL_LINK)

        eq_(track.uid, TEST_UID)
        ok_(track.track_id)
        eq_(len(track.track_id), PERSISTENT_TRACK_ID_BYTES_COUNT * 2)
        eq_(track.created, DatetimeNow())
        eq_(track.expired, DatetimeNow())
        eq_(track.type, TRACK_TYPE_RESTORATION_AUTO_EMAIL_LINK)
        eq_(track.content, {'type': TRACK_TYPE_RESTORATION_AUTO_EMAIL_LINK})

    def test_create_with_full_data(self):
        expired = datetime.now() + timedelta(hours=1)
        track = PersistentTrack.create(
            TEST_UID,
            TRACK_TYPE_RESTORATION_AUTO_EMAIL_LINK,
            expires_after=3600,
            message='hello',
            opts={'a': 1, 'b': []},
        )

        eq_(track.uid, TEST_UID)
        ok_(track.track_id)
        eq_(len(track.track_id), PERSISTENT_TRACK_ID_BYTES_COUNT * 2)
        eq_(track.created, DatetimeNow())
        eq_(track.expired, DatetimeNow(timestamp=expired))
        eq_(track.type, TRACK_TYPE_RESTORATION_AUTO_EMAIL_LINK)
        eq_(
            track.content,
            {
                'message': 'hello',
                'opts': {'a': 1, 'b': []},
                'type': TRACK_TYPE_RESTORATION_AUTO_EMAIL_LINK,
            },
        )

    def test_uninitialized_content_read_type(self):
        track = PersistentTrack()

        ok_(track.type is Undefined)


class TestTrackParse(unittest.TestCase):
    def test_track_not_found(self):
        response = get_parsed_blackbox_response(
            'get_track',
            blackbox_get_track_response(TEST_UID, TEST_TRACK_ID, is_found=False),
        )
        track = PersistentTrack().parse(response)

        eq_(track.uid, TEST_UID)
        eq_(track.track_id, TEST_TRACK_ID)
        eq_(track.track_key, TEST_TRACK_KEY)
        eq_(track.exists, False)
        ok_(track.created is Undefined)
        ok_(track.expired is Undefined)
        ok_(track.content is Undefined)

    def test_track_invalid_json(self):
        """Трек найден, но в content лежит невалидный JSON"""
        response = get_parsed_blackbox_response(
            'get_track',
            blackbox_get_track_response(TEST_UID, TEST_TRACK_ID, content=None),
        )
        track = PersistentTrack().parse(response)

        eq_(track.uid, TEST_UID)
        eq_(track.track_id, TEST_TRACK_ID)
        eq_(track.track_key, TEST_TRACK_KEY)
        eq_(track.exists, False)  # Не совсем корректно, но пользователям модели не нужны лишние детали
        ok_(track.created)
        ok_(track.expired)
        ok_(track.content is Undefined)

    def test_track_invalid_content(self):
        """Трек найден, в content лежит валидный JSON, но структура не соответствует ожиданиям"""
        bad_content_values = (
            '',
            'string',
            ['value'],
            {},
            {'something': 1},
            10,
        )
        for content in bad_content_values:
            response = get_parsed_blackbox_response(
                'get_track',
                blackbox_get_track_response(TEST_UID, TEST_TRACK_ID, content=content),
            )
            track = PersistentTrack().parse(response)

            eq_(track.uid, TEST_UID)
            eq_(track.track_id, TEST_TRACK_ID)
            eq_(track.track_key, TEST_TRACK_KEY)
            eq_(track.exists, False)  # Не совсем корректно, но пользователям модели не нужны лишние детали
            ok_(track.created)
            ok_(track.expired)
            ok_(track.content is Undefined)

    def test_track_found_and_expired(self):
        response = get_parsed_blackbox_response(
            'get_track',
            blackbox_get_track_response(TEST_UID, TEST_TRACK_ID),
        )
        track = PersistentTrack().parse(response)

        eq_(track.uid, TEST_UID)
        eq_(track.track_id, TEST_TRACK_ID)
        eq_(track.track_key, TEST_TRACK_KEY)
        ok_(track.exists)
        ok_(track.created)
        ok_(track.expired)
        ok_(track.content)

        ok_(track.type)
        ok_(track.is_expired)

    def test_track_found_and_not_expired(self):
        created = int(time.time())
        expired = created + 1000
        response = get_parsed_blackbox_response(
            'get_track',
            blackbox_get_track_response(
                TEST_UID,
                TEST_TRACK_ID,
                created=created,
                expired=expired,
                content={'type': 20},
            ),
        )
        track = PersistentTrack().parse(response)

        eq_(track.uid, TEST_UID)
        eq_(track.track_id, TEST_TRACK_ID)
        eq_(track.track_key, TEST_TRACK_KEY)
        ok_(track.exists)
        eq_(track.created, unixtime_to_datetime(created))
        eq_(track.expired, unixtime_to_datetime(expired))
        eq_(track.content, {'type': 20})

        eq_(track.type, 20)
        ok_(not track.is_expired)

    def test_track_double_parse(self):
        response = get_parsed_blackbox_response(
            'get_track',
            blackbox_get_track_response(TEST_UID, TEST_TRACK_ID),
        )
        track = PersistentTrack().parse(response)
        track.parse({})

        eq_(track.uid, TEST_UID)
        eq_(track.track_id, TEST_TRACK_ID)
        eq_(track.track_key, TEST_TRACK_KEY)
        ok_(track.exists)
        ok_(track.created)
        ok_(track.expired)
        ok_(track.content)

        ok_(track.type)
        ok_(track.is_expired)
