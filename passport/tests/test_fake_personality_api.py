# -*- coding: utf-8 -*-
import json
from unittest import TestCase

import mock
from nose.tools import (
    eq_,
    ok_,
)
from passport.backend.core.builders.datasync_api.faker.fake_personality_api import (
    FakePersonalityApi,
    maps_bookmarks_response,
    passport_external_data_response,
    passport_external_data_response_multi,
    video_favorites_successful_response,
)
from passport.backend.core.builders.datasync_api.personality_api import PersonalityApi
from passport.backend.core.test.test_utils import with_settings


TEST_UID = 123


@with_settings(
    DATASYNC_API_URL='http://localhost/',
    DATASYNC_API_TIMEOUT=0.5,
    DATASYNC_API_RETRIES=2,
)
class FakePersonalityApiTestCase(TestCase):
    def setUp(self):
        self.faker = FakePersonalityApi()
        self.faker.start()
        self.personality_api = PersonalityApi(tvm_credentials_manager=mock.Mock())

    def tearDown(self):
        self.faker.stop()
        del self.faker
        del self.personality_api

    def test_video_favorites(self):
        self.faker.set_response_value(
            'video_favorites',
            video_favorites_successful_response(),
        )
        eq_(
            self.personality_api.video_favorites(uid=TEST_UID),
            json.loads(video_favorites_successful_response()).get('items'),
        )

    def test_maps_bookmarks(self):
        self.faker.set_response_value(
            'maps_bookmarks',
            maps_bookmarks_response(),
        )
        eq_(
            self.personality_api.maps_bookmarks(uid=TEST_UID),
            json.loads(maps_bookmarks_response()).get('items'),
        )

    def test_passport_external_data_get_all(self):
        self.faker.set_response_value(
            'passport_external_data_get_all',
            passport_external_data_response_multi(),
        )
        eq_(
            self.personality_api.passport_external_data_get_all(uid=TEST_UID),
            [
                {'id': 'test_id', 'modified_at': 100, 'data': 'test_data'},
            ],
        )

    def test_passport_external_data_get(self):
        self.faker.set_response_value(
            'passport_external_data_get',
            passport_external_data_response(),
        )
        eq_(
            self.personality_api.passport_external_data_get(uid=TEST_UID, object_id='test_id'),
            {'id': 'test_id', 'modified_at': 100, 'data': 'test_data'},
        )

    def test_passport_external_data_update(self):
        self.faker.set_response_value(
            'passport_external_data_update',
            passport_external_data_response(),
        )
        ok_(
            self.personality_api.passport_external_data_update(
                uid=TEST_UID,
                object_id='test_id',
                data='test_data',
            ) is None,
        )

    def test_passport_external_data_delete(self):
        self.faker.set_response_value(
            'passport_external_data_delete',
            '{}',
        )
        ok_(
            self.personality_api.passport_external_data_delete(uid=TEST_UID, object_id='test_id') is None,
        )
