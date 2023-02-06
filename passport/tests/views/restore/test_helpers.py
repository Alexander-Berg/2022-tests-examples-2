# -*- coding: utf-8 -*-

from datetime import datetime
from unittest import TestCase

from nose.tools import eq_
from passport.backend.adm_api.tests.views.restore.data import *
from passport.backend.adm_api.views.restore.helpers import (
    AttemptVersion2Formatter,
    AttemptVersionMultiStep3Formatter,
    AttemptVersionMultiStep4Formatter,
    unixtime_to_utc_datetime,
)
from passport.backend.core.builders.historydb_api.faker.historydb_api import (
    events_info_interval_point,
    TEST_YANDEXUID,
)
from passport.backend.core.builders.social_api.faker.social_api import (
    profile_item,
    social_api_person_item,
    task_data_response,
)
from passport.backend.core.compare.dates import LOOSE_DATE_THRESHOLD_FACTOR
from passport.backend.core.compare.equality.comparator import ALLOWED_DISTANCE_THRESHOLD
from pytz import utc


def test_unixtime_to_utc_datetime():
    eq_(unixtime_to_utc_datetime(1), datetime(1970, 1, 1, second=1, tzinfo=utc))


def _set_factor_value(factor, attr_name, value):
    for attr in factor:
        if attr_name == attr[0]:
            attr[1] = value
            break


class TestFormatNamesFactorVersion2(TestCase):
    def setUp(self):
        self.formatter = AttemptVersion2Formatter(can_show_answers=True)
        self._factor = {
            u'lastname': [
                [u'initial_equal', 1],
                [u'symbol_shrink', -1],
                [u'distance', -1],
                [u'xlit_used', -1],
                [u'aggressive_shrink', -1],
                [u'aggressive_equal', -1],
            ],
            u'firstname': [
                [u'initial_equal', 1],
                [u'symbol_shrink', -1],
                [u'distance', -1],
                [u'xlit_used', -1],
                [u'aggressive_shrink', -1],
                [u'aggressive_equal', -1],
            ],
        }

    def test_match(self):
        _set_factor_value(self._factor[u'lastname'], u'initial_equal', 1)
        eq_(self.formatter._format_names_factor(self._factor), u'match')

    def test_inexact_match(self):
        _set_factor_value(self._factor[u'lastname'], u'initial_equal', 0)
        _set_factor_value(
            self._factor[u'lastname'],
            u'distance',
            ALLOWED_DISTANCE_THRESHOLD,
        )
        _set_factor_value(self._factor[u'firstname'], u'initial_equal', 0)
        _set_factor_value(self._factor[u'firstname'], u'distance', 0)

        eq_(self.formatter._format_names_factor(self._factor), u'inexact_match')

    def test_no_match(self):
        _set_factor_value(self._factor[u'lastname'], u'initial_equal', 0)
        _set_factor_value(self._factor[u'lastname'], u'distance', 0)
        _set_factor_value(self._factor[u'firstname'], u'initial_equal', 0)
        _set_factor_value(self._factor[u'firstname'], u'distance', 0)

        eq_(self.formatter._format_names_factor(self._factor), u'no_match')


class TestFormatStringFactorVersion2(TestCase):
    def setUp(self):
        self.formatter = AttemptVersion2Formatter(can_show_answers=True)
        self._factor = [
            [u'initial_equal', -1],
            [u'symbol_shrink', -1],
            [u'distance', -1],
            [u'xlit_used', -1],
        ]

    def test_match(self):
        _set_factor_value(self._factor, u'initial_equal', 1)
        eq_(self.formatter._format_string_factor(self._factor), u'match')

    def test_inexact_match(self):
        _set_factor_value(self._factor, u'initial_equal', 0)
        _set_factor_value(self._factor, u'distance', ALLOWED_DISTANCE_THRESHOLD)
        eq_(self.formatter._format_string_factor(self._factor), u'inexact_match')

    def test_no_match(self):
        _set_factor_value(self._factor, u'initial_equal', 0)
        _set_factor_value(self._factor, u'distance', 0)
        eq_(self.formatter._format_string_factor(self._factor), u'no_match')


class TestFormatLooseDateFactor(TestCase):
    def setUp(self):
        self.formatter = AttemptVersion2Formatter(can_show_answers=True)

    def test_match(self):
        eq_(self.formatter._format_loose_date_factor(1), u'match')

    def test_inexact_match(self):
        eq_(self.formatter._format_loose_date_factor(LOOSE_DATE_THRESHOLD_FACTOR), u'inexact_match')

    def test_no_match(self):
        eq_(self.formatter._format_loose_date_factor(0), u'no_match')


class TestSummarizeFactors(TestCase):
    def setUp(self):
        self.formatter = AttemptVersion2Formatter(can_show_answers=True)

    def test_match(self):
        eq_(
            self.formatter._summarize_factors({
                u'foo': u'no_match',
                u'bar': u'no_match',
                u'spam': u'match',
            }),
            u'match',
        )

    def test_inexact_match(self):
        eq_(
            self.formatter._summarize_factors({
                u'foo': u'no_match',
                u'bar': u'no_match',
                u'spam': u'inexact_match',
            }),
            u'inexact_match',
        )

    def test_no_match(self):
        eq_(
            self.formatter._summarize_factors({
                u'foo': u'no_match',
                u'bar': u'no_match',
                u'spam': u'no_match',
            }),
            u'no_match',
        )


class TestFormatPasswordFactorVersionMultistep3(TestCase):
    def setUp(self):
        self.formatter = AttemptVersionMultiStep3Formatter(can_show_answers=True)

    def test_no_match_auth_not_found(self):
        formatted_factor = self.formatter._format_password_factor(
            {
                'entered_count': 1,
                'auth_found': [0, -1, -1],
                'auth_date': [-1, -1, -1],
            },
        )
        eq_(
            formatted_factor,
            {
                'auth_date_0': 'not_calculated',
                'auth_found_0': 'no_match',
                'auth_date_1': 'not_calculated',
                'auth_found_1': 'not_calculated',
                'auth_date_2': 'not_calculated',
                'auth_found_2': 'not_calculated',
            },
        )

    def test_match_auth_found_auth_date_not_found(self):
        formatted_factor = self.formatter._format_password_factor(
            {
                'entered_count': 1,
                'auth_found': [1, -1, -1],
                'auth_date': [0, -1, -1],
            },
        )
        eq_(
            formatted_factor,
            {
                'auth_date_0': 'no_match',
                'auth_found_0': 'match',
                'auth_date_1': 'not_calculated',
                'auth_found_1': 'not_calculated',
                'auth_date_2': 'not_calculated',
                'auth_found_2': 'not_calculated',
            },
        )

    def test_match_multiple_passwords(self):
        formatted_factor = self.formatter._format_password_factor(
            {
                'entered_count': 3,
                'auth_found': [1, 0, 1],
                'auth_date': [0, -1, 0.8],
            },
        )
        eq_(
            formatted_factor,
            {
                'auth_date_0': 'no_match',
                'auth_found_0': 'match',
                'auth_date_1': 'not_calculated',
                'auth_found_1': 'no_match',
                'auth_date_2': 'inexact_match',
                'auth_found_2': 'match',
            },
        )


class TestTransformNamesVersionMultistep3(TestCase):
    def setUp(self):
        self.formatter = AttemptVersionMultiStep3Formatter(can_show_answers=True)

    def test_single_names(self):
        formatted_names = self.formatter._transform_entered_names(
            dict(
                firstnames=['ivan'],
                lastnames=['ivanov'],
            ),
        )
        eq_(
            formatted_names,
            [
                dict(firstname='ivan', lastname='ivanov'),
            ],
        )

    def test_multiple_firstnames_one_lastname(self):
        formatted_names = self.formatter._transform_entered_names(
            dict(
                firstnames=['ivan', u'ваня'],
                lastnames=['ivanov'],
            ),
        )
        eq_(
            formatted_names,
            [
                dict(firstname='ivan', lastname='ivanov'),
                dict(firstname=u'ваня', lastname='ivanov'),
            ],
        )

    def test_multiple_firstnames_lastnames(self):
        formatted_names = self.formatter._transform_entered_names(
            dict(
                firstnames=['ivan', u'ваня'],
                lastnames=['ivanov', u'иванов'],
            ),
        )
        eq_(
            formatted_names,
            [
                dict(firstname='ivan', lastname='ivanov'),
                dict(firstname=u'ваня', lastname=u'иванов'),
            ],
        )


class TestFormatIntervalsVersionMultistep3(TestCase):
    def setUp(self):
        self.formatter = AttemptVersionMultiStep3Formatter(can_show_answers=True)

    def test_with_single_interval(self):
        formatted_intervals = self.formatter._format_intervals(
            [
                {
                    'start': {'user_ip': TEST_IP, 'timestamp': 1},
                    'end': {'user_ip': TEST_IP, 'timestamp': 2},
                },
            ],
        )
        eq_(
            formatted_intervals,
            [
                {
                    'start': {'user_ip': TEST_IP, 'datetime': DATETIME_FOR_TS_1},
                    'end': {'user_ip': TEST_IP, 'datetime': DATETIME_FOR_TS_2},
                },
            ],
        )

    def test_with_empty_interval_point_fields(self):
        formatted_intervals = self.formatter._format_intervals(
            [
                {
                    'start': {'user_ip': None, 'timestamp': 1},
                    'end': {'user_ip': TEST_IP, 'timestamp': None},
                },
                {
                    'start': {'user_ip': None, 'timestamp': None},
                    'end': None,
                },
            ],
        )
        eq_(
            formatted_intervals,
            [
                {
                    'start': {'user_ip': None, 'datetime': DATETIME_FOR_TS_1},
                    'end': {'user_ip': TEST_IP, 'datetime': None},
                },
                {
                    'start': {'user_ip': None, 'datetime': None},
                    'end': None,
                },
            ],
        )

    def test_with_missing_start_end(self):
        formatted_intervals = self.formatter._format_intervals(
            [
                {
                    'start': {'user_ip': TEST_IP, 'timestamp': 1},
                    'end': None,
                },
                {
                    'start': None,
                    'end': None,
                },
            ],
        )
        eq_(
            formatted_intervals,
            [
                {
                    'start': {'user_ip': TEST_IP, 'datetime': DATETIME_FOR_TS_1},
                    'end': None,
                },
                {
                    'start': None,
                    'end': None,
                },
            ],
        )


class TestFormatOriginInfoVersionMultistep4(TestCase):
    def setUp(self):
        self.formatter = AttemptVersionMultiStep4Formatter(can_show_answers=True)

    def test_with_none_timestamp(self):
        formatted = self.formatter._format_origin_info(
            events_info_interval_point(
                timestamp=None,
                user_ip=None,
                yandexuid=None,
            ),
        )
        eq_(
            formatted,
            {'user_ip': None, 'datetime': None},
        )

    def test_with_only_yandexuid(self):
        formatted = self.formatter._format_origin_info(
            events_info_interval_point(
                yandexuid=TEST_YANDEXUID,
                user_ip=TEST_IP,
            ),
        )
        eq_(
            formatted,
            {
                'user_ip': TEST_IP,
                'datetime': DATETIME_FOR_TS_1,
                'user_agent': 'yandexuid/%s' % TEST_YANDEXUID,
            },
        )

    def test_with_only_user_agent(self):
        formatted = self.formatter._format_origin_info(
            events_info_interval_point(
                yandexuid=None,
                user_agent='ua',
                user_ip=TEST_IP,
            ),
        )
        eq_(
            formatted,
            {
                'user_ip': TEST_IP,
                'datetime': DATETIME_FOR_TS_1,
                'user_agent': 'ua',
            },
        )

    def test_with_user_agent_and_yandexuid(self):
        formatted = self.formatter._format_origin_info(
            events_info_interval_point(
                yandexuid=TEST_YANDEXUID,
                user_agent='ua',
                user_ip=TEST_IP,
            ),
        )
        eq_(
            formatted,
            {
                'user_ip': TEST_IP,
                'datetime': DATETIME_FOR_TS_1,
                'user_agent': 'ua yandexuid/%s' % TEST_YANDEXUID,
            },
        )


class TestFormatSocialProfilesVersionMultistep4(TestCase):
    def setUp(self):
        self.formatter = AttemptVersionMultiStep4Formatter(can_show_answers=True)

    def test_with_one_matching_profile(self):
        task_data = task_data_response(task_id=TEST_SOCIAL_TASK_ID)
        profile = profile_item(uid=TEST_PDD_UID)

        # сырые данные соц. брокера всегда выводятся как есть, тестируем один раз
        eq_(
            self.formatter._format_incoming_social_profiles([task_data['profile']]),
            [
                {
                    'lastname': 'Lastname',
                    'birthday': None,
                    'addresses': ['https://plus.google.com/118320684662584130204'],
                    'firstname': 'Firstname',
                },
            ],
        )
        eq_(
            self.formatter._format_trusted_social_profiles([profile], [profile]),
            [
                {
                    'birthday': None,
                    'belongs_to_account': True,
                    'addresses': [
                        'http://www.facebook.com/profile.php?id=%(userid)s',
                        'http://www.facebook.com/some.user',
                    ],
                    'firstname': None,
                    'is_matched': True,
                    'lastname': None,
                },
            ],
        )

    def test_with_no_entered_profiles(self):
        profile = profile_item(uid=TEST_PDD_UID)
        eq_(
            self.formatter._format_trusted_social_profiles([], [profile]),
            [
                {
                    'belongs_to_account': True,
                    'is_matched': False,
                    'birthday': None,
                    'addresses': [
                        'http://www.facebook.com/profile.php?id=%(userid)s',
                        'http://www.facebook.com/some.user',
                    ],
                    'firstname': None,
                    'lastname': None,
                },
            ],
        )

    def test_with_entered_profiles_with_no_account_profiles(self):
        profile = profile_item(uid=TEST_PDD_UID)
        eq_(
            self.formatter._format_trusted_social_profiles([profile], []),
            [
                {
                    'belongs_to_account': False,
                    'other_uids': str(TEST_PDD_UID),
                    'birthday': None,
                    'addresses': [
                        'http://www.facebook.com/profile.php?id=%(userid)s',
                        'http://www.facebook.com/some.user',
                    ],
                    'firstname': None,
                    'lastname': None,
                },
            ],
        )

    def test_with_entered_profiles_with_account_profiles(self):
        profile1 = profile_item(profile_id=1, uid=TEST_PDD_UID)
        profile2 = profile_item(profile_id=2, person=social_api_person_item(), userid='2', uid=TEST_PDD_UID)
        profile3 = profile_item(profile_id=3, uid=TEST_UID)
        profile4 = profile_item(profile_id=4, addresses=['http://test'], uid=TEST_UID, userid='3')
        profile5 = profile_item(profile_id=5, addresses=['http://test'], uid=TEST_SUPPORT_UID, userid='3')
        eq_(
            self.formatter._format_trusted_social_profiles(
                # Профили 1 и 3 соответствуют одному соц. аккаунту, но профиль 3 не соответствует аккаунту,
                # к которому восстанавливается доступ. Правильно выставляем флаг is_matched.
                [profile1, profile4, profile5, profile3],
                [profile2, profile1],
            ),
            [
                {
                    'belongs_to_account': True,
                    'is_matched': True,
                    'birthday': None,
                    'addresses': [
                        'http://www.facebook.com/profile.php?id=%(userid)s',
                        'http://www.facebook.com/some.user',
                    ],
                    'firstname': None,
                    'lastname': None,
                    'other_uids': str(TEST_UID),
                },
                {
                    'belongs_to_account': True,
                    'is_matched': False,
                    'birthday': '1989-12-28',
                    'addresses': [
                        'http://www.facebook.com/profile.php?id=%(userid)s',
                        'http://www.facebook.com/some.user',
                    ],
                    'firstname': 'Firstname',
                    'lastname': 'Lastname',
                },
                {
                    'belongs_to_account': False,
                    'other_uids': '1, 183',
                    'birthday': None,
                    'addresses': ['http://test'],
                    'firstname': None,
                    'lastname': None,
                },
            ],
        )

    def test_with_different_address_order_on_same_profile(self):
        profile1 = profile_item(profile_id=1, addresses=['http://test1', 'http://test2'], uid=TEST_UID)
        profile2 = profile_item(profile_id=1, addresses=['http://test2', 'http://test1'], uid=TEST_UID)
        eq_(
            self.formatter._format_trusted_social_profiles(
                [profile1],
                [profile2],
            ),
            [
                {
                    'birthday': None,
                    'belongs_to_account': True,
                    'is_matched': True,
                    'addresses': ['http://test2', 'http://test1'],
                    'firstname': None,
                    'lastname': None,
                },
            ],
        )
