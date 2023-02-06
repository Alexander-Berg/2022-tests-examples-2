# -*- coding: utf-8 -*-
from time import time

from nose.tools import (
    eq_,
    istest,
    ok_,
)
from passport.backend.core.builders.afisha import (
    AfishaApiNotFoundError,
    AfishaApiTemporaryError,
)
from passport.backend.core.builders.afisha.faker.fake_afisha_api import (
    error_response,
    events_response,
    events_schedules_response,
)
from passport.backend.core.builders.datasync_api.faker.fake_personality_api import passport_external_data_response
from passport.backend.core.test.test_utils.utils import with_settings_hosts

from .base import (
    BaseExternalDataTestCase,
    TEST_COOKIE_HEADERS,
    TEST_DATASYNC_API_URL,
    TEST_UID,
)


TEST_API_URL = 'https://afisha.api.net'
TEST_FRONT_URL = 'https://afisha.net'

TEST_MOSCOW_IP = '95.108.173.106'

TEST_EVENT_ID = u'583dc3b1cc1c72f66d531db1'
TEST_TITLE = u'Концерт Шостаковича для скрипки с оркестром'
TEST_URL = u'/moscow/concert/shostakvich'

TEST_IMAGE_URL = u'avatars.net/get-afishanew/group_id/image_id'
TEST_SINGLE_DATE = u'2017-09-24T20:00:00'
TEST_ONLY_PLACE = u'Главclub Green Concert'

TEST_EVENT_ID_OTHER = '58249810ca15c79c1296d783'
TEST_TITLE_OTHER = u'Шоу ужасов Рокки Хоррора'
TEST_URL_OTHER = u'/moscow/cinema/rocky-horror'

TEST_EVENT_ID_VISITED = '123'
TEST_CITY_ID = 213
TEST_TYPE = u'cinema'
TEST_TYPE_NAME = u'кино'
TEST_PLACES_TOTAL = 197
TEST_WEEK_PERIOD = 7

TEST_EVENTS_FAVOURITES_RESPONSE = [
    {
        'id': TEST_EVENT_ID,
        'title': TEST_TITLE,
        'url': TEST_FRONT_URL + TEST_URL,
        'type': TEST_TYPE,
        'type_name': TEST_TYPE_NAME,
        'image': TEST_IMAGE_URL,
        'single_date': TEST_SINGLE_DATE,
        'only_place': TEST_ONLY_PLACE,
    },
    {
        'id': TEST_EVENT_ID_OTHER,
        'title': TEST_TITLE_OTHER,
        'url': TEST_FRONT_URL + TEST_URL_OTHER,
        'type': TEST_TYPE,
        'type_name': TEST_TYPE_NAME,
        'image': TEST_IMAGE_URL,
        'places_total': TEST_PLACES_TOTAL,
        'date_end': u'2017-09-27',
    },
]


@istest
@with_settings_hosts(
    AFISHA_API_URL=TEST_API_URL,
    AFISHA_FRONT_URL=TEST_FRONT_URL,
    AFISHA_API_TIMEOUT=0.5,
    AFISHA_API_RETRIES=2,
    DATASYNC_API_URL=TEST_DATASYNC_API_URL,
)
class TestAfishaFavouritesTestCase(BaseExternalDataTestCase):
    default_url = '/1/bundle/account/external_data/afisha/favourites/'
    http_query_args = dict(
        consumer='dev',
    )

    def setUp(self):
        super(TestAfishaFavouritesTestCase, self).setUp()
        self.env.afisha_api.set_response_value(
            'events',
            events_response(),
        )
        self.env.afisha_api.set_response_value(
            'events_schedules',
            events_schedules_response(),
        )

    def test_no_events_ok(self):
        resp = self.make_request(headers=TEST_COOKIE_HEADERS)
        self.assert_ok_response(
            resp,
            event_favourites=[],
            next_page=None,
        )
        eq_(len(self.env.afisha_api.requests), 1)
        self.env.afisha_api.requests[0].assert_properties_equal(
            method='GET',
            url='%s/3.x/users/%s/favourites/events/' % (
                TEST_API_URL,
                TEST_UID,
            ),
        )

    def test_not_found_events_for_user_ok(self):
        self.env.afisha_api.set_response_side_effect(
            'events',
            AfishaApiNotFoundError(),
        )
        resp = self.make_request(headers=TEST_COOKIE_HEADERS)
        self.assert_ok_response(
            resp,
            event_favourites=[],
            next_page=None,
        )
        eq_(len(self.env.afisha_api.requests), 1)
        self.env.afisha_api.requests[0].assert_properties_equal(
            method='GET',
            url='%s/3.x/users/%s/favourites/events/' % (
                TEST_API_URL,
                TEST_UID,
            ),
        )

    def test_ok_with_none_image(self):
        events_data = [
            {
                'title': TEST_TITLE,
                'id_': TEST_EVENT_ID,
                'url': TEST_URL,
                'image': None,
            },
        ]
        event_schedules = [
            {
                'schedule': {
                    'single_place': True,
                    'single_date': TEST_SINGLE_DATE,
                },
                'event': events_data[0],
            },
        ]
        self.env.afisha_api.set_response_value(
            'events',
            events_response(events_data),
        )
        self.env.afisha_api.set_response_value(
            'events_schedules',
            events_schedules_response(event_schedules),
        )

        resp = self.make_request(
            headers=dict(
                user_ip=TEST_MOSCOW_IP,
                **TEST_COOKIE_HEADERS
            ),
        )
        self.assert_ok_response(
            resp,
            event_favourites=[
                {
                    'id': TEST_EVENT_ID,
                    'title': TEST_TITLE,
                    'url': TEST_FRONT_URL + TEST_URL,
                    'type': TEST_TYPE,
                    'type_name': TEST_TYPE_NAME,
                    'single_date': TEST_SINGLE_DATE,
                    'only_place': TEST_ONLY_PLACE,
                },
            ],
            next_page=None,
        )
        eq_(len(self.env.afisha_api.requests), 2)
        self.env.afisha_api.requests[0].assert_properties_equal(
            method='GET',
            url='%s/3.x/users/%s/favourites/events/' % (
                TEST_API_URL,
                TEST_UID,
            ),
        )
        self.env.afisha_api.requests[1].assert_properties_equal(
            method='GET',
            url='%s/3.x/cities/%s/schedule_info?event_id=%s&period=180' % (
                TEST_API_URL,
                TEST_CITY_ID,
                TEST_EVENT_ID,
            ),
        )

    def test_ok_with_events(self):
        events_data = [
            {
                'title': u'Концерт номер 1',
                'id_': u'583dc3b1cc1c72f66d531db2',
                'url': u'/moscow/concert/number-one',
                'is_visited': True,
            },
            {
                'title': TEST_TITLE,
                'id_': TEST_EVENT_ID,
                'url': TEST_URL,
            },
            {
                'title': TEST_TITLE_OTHER,
                'id_': TEST_EVENT_ID_OTHER,
                'url': TEST_URL_OTHER,
            },
        ]
        event_schedules = [
            {
                'schedule': {
                    'single_place': True,
                    'single_date': TEST_SINGLE_DATE,
                },
                'event': events_data[1],
            },
            {
                'schedule': {
                    'single_place': False,
                    'places_total': 197,
                },
                'event': events_data[2],
            },
        ]
        self.env.afisha_api.set_response_value(
            'events',
            events_response(events_data),
        )
        self.env.afisha_api.set_response_value(
            'events_schedules',
            events_schedules_response(event_schedules),
        )

        resp = self.make_request(
            headers=dict(
                user_ip=TEST_MOSCOW_IP,
                **TEST_COOKIE_HEADERS
            ),
        )
        self.assert_ok_response(
            resp,
            event_favourites=TEST_EVENTS_FAVOURITES_RESPONSE,
            next_page=None,
        )
        eq_(len(self.env.afisha_api.requests), 2)
        self.env.afisha_api.requests[0].assert_properties_equal(
            method='GET',
            url='%s/3.x/users/%s/favourites/events/' % (
                TEST_API_URL,
                TEST_UID,
            ),
        )
        self.env.afisha_api.requests[1].assert_properties_equal(
            method='GET',
            url='%s/3.x/cities/%s/schedule_info?event_id=%s&event_id=%s&period=180' % (
                TEST_API_URL,
                TEST_CITY_ID,
                TEST_EVENT_ID,
                TEST_EVENT_ID_OTHER,
            ),
        )

    def test_ok_with_pagination(self):
        sorted_events = sorted([u'583dc3b1cc1c72f66d531db2', TEST_EVENT_ID, TEST_EVENT_ID_OTHER], reverse=1)
        events_data = [
            {
                'title': u'Концерт номер 1',
                'id_': u'583dc3b1cc1c72f66d531db2',
                'url': u'/moscow/concert/number-one',
                'is_visited': True,
            },
            {
                'title': TEST_TITLE,
                'id_': sorted_events[0],
                'url': TEST_URL,
            },
            {
                'title': TEST_TITLE_OTHER,
                'id_': sorted_events[1],
                'url': TEST_URL_OTHER,
            },
        ]
        event_schedules = [
            {
                'schedule': {
                    'single_place': True,
                    'single_date': TEST_SINGLE_DATE,
                },
                'event': events_data[1],
            },
        ]
        self.env.afisha_api.set_response_value(
            'events',
            events_response(events_data),
        )
        self.env.afisha_api.set_response_value(
            'events_schedules',
            events_schedules_response(event_schedules),
        )

        resp = self.make_request(
            query_args=dict(
                page_size=1,
                period=TEST_WEEK_PERIOD,
            ),
            headers=dict(
                user_ip=TEST_MOSCOW_IP,
                **TEST_COOKIE_HEADERS
            ),
        )
        expected = TEST_EVENTS_FAVOURITES_RESPONSE[0].copy()
        expected['id'] = sorted_events[0]
        self.assert_ok_response(
            resp,
            event_favourites=[expected],
            next_page=2,
        )
        eq_(len(self.env.afisha_api.requests), 2)
        self.env.afisha_api.requests[0].assert_properties_equal(
            method='GET',
            url='%s/3.x/users/%s/favourites/events/' % (
                TEST_API_URL,
                TEST_UID,
            ),
        )
        self.env.afisha_api.requests[1].assert_properties_equal(
            method='GET',
            url='%s/3.x/cities/%s/schedule_info?event_id=%s&period=%s' % (
                TEST_API_URL,
                TEST_CITY_ID,
                sorted_events[0],
                TEST_WEEK_PERIOD,
            ),
        )

    def test_afisha_api_unavailable(self):
        self.env.afisha_api.set_response_side_effect(
            'events',
            AfishaApiTemporaryError,
        )
        resp = self.make_request(headers=TEST_COOKIE_HEADERS)
        eq_(len(self.env.afisha_api.requests), 2)
        self.assert_error_response(resp, ['backend.afisha_api_failed'])

    def test_geo_id_unknown_to_afisha(self):
        events_data = [
            {
                'title': u'Концерт номер 1',
                'id_': u'583dc3b1cc1c72f66d531db2',
                'url': u'/moscow/concert/number-one',
                'is_visited': True,
            },
            {
                'title': TEST_TITLE,
                'id_': TEST_EVENT_ID,
                'url': TEST_URL,
            },
            {
                'title': TEST_TITLE_OTHER,
                'id_': TEST_EVENT_ID_OTHER,
                'url': TEST_URL_OTHER,
            },
        ]
        self.env.afisha_api.set_response_value(
            'events',
            events_response(events_data),
        )
        self.env.afisha_api.set_response_value(
            'events_schedules',
            error_response(message=u'You need to specify city'),
        )
        resp = self.make_request(headers=TEST_COOKIE_HEADERS)
        self.assert_ok_response(resp, event_favourites=[], next_page=None)
        eq_(len(self.env.afisha_api.requests), 2)

    def test_no_region_id(self):
        resp = self.make_request(
            headers=dict(
                user_ip='127.0.0.1',
                **TEST_COOKIE_HEADERS
            ),
        )
        self.assert_ok_response(resp, event_favourites=[], next_page=None)
        ok_(not self.env.afisha_api.requests)

    def test_from_cache(self):
        self.env.personality_api.set_response_value(
            'passport_external_data_get',
            passport_external_data_response(
                item_id='afisha_favourite_events',
                modified_at=int(time()),
                data=dict(event_favourites=TEST_EVENTS_FAVOURITES_RESPONSE, next_page=None),
                meta={'params': {'page': 1, 'page_size': 10, 'period': 180}},
            ),
        )
        rv = self.make_request(headers=TEST_COOKIE_HEADERS)
        self.assert_ok_response(
            rv,
            event_favourites=TEST_EVENTS_FAVOURITES_RESPONSE,
            next_page=None,
        )

        eq_(len(self.env.personality_api.requests), 1)  # чтение из кэша
        eq_(len(self.env.afisha_api.requests), 0)
