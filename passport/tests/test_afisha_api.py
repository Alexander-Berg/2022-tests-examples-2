# -*- coding: utf-8 -*-
import json
import unittest

import mock
from nose.tools import (
    assert_raises,
    eq_,
    ok_,
)
from passport.backend.core.builders.afisha import AfishaApi
from passport.backend.core.builders.afisha.exceptions import (
    AfishaApiInvalidResponseError,
    AfishaApiPermanentError,
)
from passport.backend.core.builders.afisha.faker.fake_afisha_api import (
    error_response,
    events_response,
    events_schedules_response,
    FakeAfishaApi,
)
from passport.backend.core.test.test_utils import with_settings


TEST_UID = 1
TEST_EVENT_ID = 'abc123'
TEST_EVENT_ID_OTHER = '123abc'
TEST_CITY_ID = 213


@with_settings(
    AFISHA_API_URL='http://afisha-api/',
    AFISHA_API_TIMEOUT=0.5,
    AFISHA_API_RETRIES=2,
)
class TestAfishaApiCommon(unittest.TestCase):
    def setUp(self):
        self.afisha_api = AfishaApi()
        self.afisha_api.useragent = mock.Mock()

        self.response = mock.Mock()
        self.afisha_api.useragent.request.return_value = self.response
        self.afisha_api.useragent.request_error_class = self.afisha_api.temporary_error_class
        self.response.content = json.dumps({})
        self.response.status_code = 200

    def tearDown(self):
        del self.afisha_api
        del self.response

    def test_failed_to_parse_response(self):
        self.response.status_code = 200
        self.response.content = b'not a json'
        with assert_raises(AfishaApiPermanentError):
            self.afisha_api.events_schedules(city_id=TEST_CITY_ID, event_ids=TEST_EVENT_ID)

    def test_server_error(self):
        self.response.status_code = 503
        self.response.content = error_response(503)
        with assert_raises(AfishaApiPermanentError):
            self.afisha_api.events(uid=TEST_UID)

    def test_bad_status_code(self):
        self.response.status_code = 418
        self.response.content = error_response(418)
        with assert_raises(AfishaApiPermanentError):
            self.afisha_api.events_schedules(city_id=TEST_CITY_ID, event_ids=TEST_EVENT_ID)

    def test_bad_response(self):
        self.response.status_code = 200
        self.response.content = json.dumps({'status': 200, 'paging': {}}).encode('utf-8')
        with assert_raises(AfishaApiInvalidResponseError):
            self.afisha_api.events_schedules(city_id=TEST_CITY_ID, event_ids=TEST_EVENT_ID)

    def test_not_found(self):
        self.response.status_code = 404
        self.response.content = error_response(404)
        eq_(self.afisha_api.events(uid=TEST_UID), {'events': []})

    def test_by_geo_id_not_found(self):
        self.response.status_code = 400
        self.response.content = error_response(status_code=400, message=u'You need to specify city')
        ok_(not self.afisha_api.events_schedules(city_id=TEST_CITY_ID, event_ids=TEST_EVENT_ID))


@with_settings(
    AFISHA_API_URL='http://afisha-api/',
    AFISHA_API_TIMEOUT=0.5,
    AFISHA_API_RETRIES=2,
)
class TestAfishaApiMethods(unittest.TestCase):
    def setUp(self):
        self.fake_afisha_api = FakeAfishaApi()
        self.fake_afisha_api.start()

        self.afisha_api = AfishaApi()

    def tearDown(self):
        self.fake_afisha_api.stop()
        del self.fake_afisha_api

    def test_events_ok(self):
        expected_resp = events_response()
        self.fake_afisha_api.set_response_value('events', expected_resp)
        response = self.afisha_api.events(uid=TEST_UID)
        eq_(
            response,
            json.loads(expected_resp)['data'],
        )
        eq_(len(self.fake_afisha_api.requests), 1)
        self.fake_afisha_api.requests[0].assert_url_starts_with(
            'http://afisha-api/3.x/users/%s/favourites/events/' % TEST_UID,
        )
        self.fake_afisha_api.requests[0].assert_query_equals({})

    def test_events_with_params_ok(self):
        events_data = [
            {
                'title': 'Test event',
                'id_': TEST_EVENT_ID,
                'url': '/url-to-event',
            },
        ]
        expected_resp = events_response(events_data)
        self.fake_afisha_api.set_response_value('events', expected_resp)
        response = self.afisha_api.events(uid=TEST_UID, tags=['comedy', 'drama'])
        eq_(
            response,
            json.loads(expected_resp)['data'],
        )
        eq_(len(self.fake_afisha_api.requests), 1)
        self.fake_afisha_api.requests[0].assert_url_starts_with(
            'http://afisha-api/3.x/users/%s/favourites/events/' % TEST_UID,
        )
        self.fake_afisha_api.requests[0].assert_query_equals({
            'tags': ['comedy', 'drama'],
        })

    def test_events_schedules_ok(self):
        expected_resp = events_schedules_response()
        self.fake_afisha_api.set_response_value(
            'events_schedules',
            events_schedules_response(),
        )
        resp = self.afisha_api.events_schedules(city_id=TEST_CITY_ID, event_ids=TEST_EVENT_ID)
        eq_(resp, json.loads(expected_resp)['data'])
        eq_(len(self.fake_afisha_api.requests), 1)
        self.fake_afisha_api.requests[0].assert_url_starts_with(
            'http://afisha-api/3.x/cities/%s/schedule_info' % TEST_CITY_ID,
        )
        self.fake_afisha_api.requests[0].assert_query_equals({
            'event_id': TEST_EVENT_ID,
        })

    def test_events_schedules_with_params_and_pagination(self):
        event_data = [
            {
                'schedule': {
                    'single_place': True,
                    'single_date': True,
                },
                'event': {
                    'title': 'My first event',
                    'id_': TEST_EVENT_ID,
                    'url': '/url-to-event',
                    'is_visited': True,
                },
            },
            {
                'schedule': {
                    'single_place': False,
                    'single_date': False,
                    'places_total': 1000,
                },
                'event': {
                    'title': 'My last event',
                    'id_': TEST_EVENT_ID_OTHER,
                    'url': '/url-to-event-other',
                    'is_visited': False,
                },
            },
        ]
        expected_resp = events_schedules_response(event_data)
        self.fake_afisha_api.set_response_value('events_schedules', expected_resp)
        resp = self.afisha_api.events_schedules(
            city_id=TEST_CITY_ID,
            event_ids=[TEST_EVENT_ID, TEST_EVENT_ID_OTHER],
            limit=5,
            offset=20,
            is_sale_available=True,
            date='2017-10-20',
            period=7,
            tags='comedy',
            place_id=1,
        )
        eq_(resp, json.loads(expected_resp)['data'])
        eq_(len(self.fake_afisha_api.requests), 1)
        self.fake_afisha_api.requests[0].assert_url_starts_with(
            'http://afisha-api/3.x/cities/%s/schedule_info' % TEST_CITY_ID,
        )
        self.fake_afisha_api.requests[0].assert_query_equals({
            'limit': '5',
            'offset': '20',
            'event_id': [TEST_EVENT_ID, TEST_EVENT_ID_OTHER],
            'sale_available': 'True',
            'date': '2017-10-20',
            'period': '7',
            'tag': 'comedy',
            'place_id': '1',
        })
