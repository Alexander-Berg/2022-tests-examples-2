# -*- coding: utf-8 -*-
import json
from unittest import TestCase

from nose.tools import (
    assert_raises,
    eq_,
    ok_,
)
from passport.backend.core.builders.afisha import (
    AfishaApi,
    AfishaApiInvalidResponseError,
    BaseAfishaApiError,
)
from passport.backend.core.builders.afisha.faker.fake_afisha_api import (
    events_response,
    events_schedules_response,
    FakeAfishaApi,
)
from passport.backend.core.builders.base.faker.fake_builder import assert_builder_requested
from passport.backend.core.test.test_utils import with_settings


TEST_UID = 1
TEST_CITY_ID = 213


@with_settings(
    AFISHA_API_URL='http://afisha-api/',
    AFISHA_API_TIMEOUT=1,
    AFISHA_API_RETRIES=2,
)
class FakeAfishaApiTestCase(TestCase):
    def setUp(self):
        self.faker = FakeAfishaApi()
        self.faker.start()
        self.afisha_api = AfishaApi()

    def tearDown(self):
        self.faker.stop()
        del self.faker

    def test_set_response_side_effect(self):
        ok_(not self.faker._mock.request.called)

        builder = AfishaApi()
        self.faker.set_response_side_effect(
            'events',
            AfishaApiInvalidResponseError,
        )
        with assert_raises(BaseAfishaApiError):
            builder.events(uid=TEST_UID)
        assert_builder_requested(self.faker, times=1)

    def test_set_events_response_value(self):
        ok_(not self.faker._mock.request.called)

        builder = AfishaApi()
        expected_resp = events_response()
        self.faker.set_response_value('events', expected_resp)
        resp = builder.events(uid=TEST_UID)
        eq_(resp, json.loads(expected_resp)['data'])
        assert_builder_requested(self.faker, times=1)

    def test_set_events_schedules_response_value(self):
        ok_(not self.faker._mock.request.called)

        builder = AfishaApi()
        expected_resp = events_schedules_response()
        self.faker.set_response_value('events_schedules', expected_resp)
        resp = builder.events_schedules(city_id=TEST_CITY_ID, event_ids=[1, 2])
        eq_(resp, json.loads(expected_resp)['data'])
        assert_builder_requested(self.faker, times=1)
