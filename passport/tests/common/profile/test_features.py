# -*- coding: utf-8 -*-
from datetime import datetime
import unittest

import mock
from nose.tools import (
    eq_,
    ok_,
)
from passport.backend.api.common.profile.features import (
    FeaturesBuilderProfileV1,
    FeaturesBuilderProfileV2,
    FeaturesBuilderProfileV3,
)
from passport.backend.core.builders.ufo_api.faker import TEST_UATRAITS_INFO
from passport.backend.core.env_profile.helpers import make_profile_from_raw_data
from passport.backend.core.test.test_utils.utils import (
    iterdiff,
    with_settings_hosts,
)
from passport.backend.utils.time import (
    datetime_to_integer_unixtime,
    Weekday,
)


eq_ = iterdiff(eq_)


def get_v1_empty_features():
    now = datetime.now()
    return {
        'as_list': '',
        'as_list_prob_1d': 0,
        'as_list_prob_1m': 0,
        'as_list_prob_1w': 0,
        'browser': 'None None',
        'browser_grouped_prob_1d': 0,
        'browser_grouped_prob_1m': 0,
        'browser_grouped_prob_1w': 0,
        'browser_name': None,
        'browser_name_count_1d': 0,
        'browser_name_count_1m': 0,
        'browser_name_count_1w': 0,
        'browser_name_prob_1d': 0,
        'browser_name_prob_1m': 0,
        'browser_name_prob_1w': 0,
        'browser_os': 'None None - None',
        'browser_os_prob_1d': 0,
        'browser_os_prob_1m': 0,
        'browser_os_prob_1w': 0,
        'browser_prob_1d': 0,
        'browser_prob_1m': 0,
        'browser_prob_1w': 0,
        'browser_version': None,
        'captcha_passed_1d': 0,
        'captcha_passed_1m': 0,
        'captcha_passed_1w': 0,
        'city': 0,
        'city_count_1d': 0,
        'city_count_1m': 0,
        'city_count_1w': 0,
        'city_prob_1d': 0,
        'city_prob_1m': 0,
        'city_prob_1w': 0,
        'country': 0,
        'country_count_1d': 0,
        'country_count_1m': 0,
        'country_count_1w': 0,
        'country_prob_1d': 0,
        'country_prob_1m': 0,
        'country_prob_1w': 0,
        'day_part': now.hour // 6,
        'day_part_prob_1d': 0,
        'day_part_prob_1m': 0,
        'day_part_prob_1w': 0,
        'geo_id': -1,
        'hour': now.hour,
        'ip': '127.0.0.1',
        'ip_prob_1d': 0,
        'ip_prob_1m': 0,
        'ip_prob_1w': 0,
        'is_black_ip': 0,
        'is_mobile': 0,
        'is_weekend': int(now.isoweekday() in {Weekday.SATURDAY, Weekday.SUNDAY}),
        'is_yandexuid_ts_future': -1,
        'month': now.month,
        'os_family': None,
        'os_family_prob_1d': 0,
        'os_family_prob_1m': 0,
        'os_family_prob_1w': 0,
        'os_name': None,
        'os_name_count_1d': 0,
        'os_name_count_1m': 0,
        'os_name_count_1w': 0,
        'os_name_prob_1d': 0,
        'os_name_prob_1m': 0,
        'os_name_prob_1w': 0,
        'os_version': None,
        'referer_host_2': None,
        'referer_host_2_prob_1d': 0,
        'referer_host_2_prob_1m': 0,
        'referer_host_2_prob_1w': 0,
        'referer_host_3': None,
        'referer_host_3_count_1d': 0,
        'referer_host_3_count_1m': 0,
        'referer_host_3_count_1w': 0,
        'referer_host_3_prob_1d': 0,
        'referer_host_3_prob_1m': 0,
        'referer_host_3_prob_1w': 0,
        'retpath_host_2': None,
        'retpath_host_2_prob_1d': 0,
        'retpath_host_2_prob_1m': 0,
        'retpath_host_2_prob_1w': 0,
        'retpath_host_3': None,
        'retpath_host_3_count_1d': 0,
        'retpath_host_3_count_1m': 0,
        'retpath_host_3_count_1w': 0,
        'retpath_host_3_prob_1d': 0,
        'retpath_host_3_prob_1m': 0,
        'retpath_host_3_prob_1w': 0,
        'succ_auth_count_1d': 0,
        'succ_auth_count_1m': 0,
        'succ_auth_count_1w': 0,
        'weekday': now.isoweekday(),
        'weekday_prob_1d': 0,
        'weekday_prob_1m': 0,
        'weekday_prob_1w': 0,
        'yandexuid': None,
        'yandexuid_count_1d': 0,
        'yandexuid_count_1m': 0,
        'yandexuid_count_1w': 0,
        'yandexuid_prob_1d': 0,
        'yandexuid_prob_1m': 0,
        'yandexuid_prob_1w': 0,
        'yandexuid_ts': None,
        'yandexuid_ts_freshness': -1,
    }


class BaseFeaturesBuilderTestCase(unittest.TestCase):
    def assert_features_present(self, all_features, expected_features):
        for key, value in expected_features.items():
            ok_(key in all_features, (key, all_features))
        eq_(expected_features, dict([(key, all_features[key]) for key in expected_features]))


@with_settings_hosts()
class AuthFeaturesBuilderV1TestCase(BaseFeaturesBuilderTestCase):
    def test_extract_unixtime_features(self):
        dt = datetime(2016, 1, 16, hour=16)  # суббота
        timestamp = datetime_to_integer_unixtime(dt)
        fresh_profile = make_profile_from_raw_data('127.0.0.1', None, {}, timestamp=timestamp)

        features_dict = FeaturesBuilderProfileV1().extract_features(fresh_profile, {})

        self.assert_features_present(
            features_dict,
            {
                'day_part': 2,
                'weekday': Weekday.SATURDAY,
                'is_weekend': 1,
                'hour': 16,
                'month': 1,
            },
        )

    def test_extract_geo_features(self):
        fresh_profile = make_profile_from_raw_data('37.9.101.188', None, {})

        features_dict = FeaturesBuilderProfileV1().extract_features(fresh_profile, {})

        self.assert_features_present(
            features_dict,
            {
                'is_black_ip': 0,
                'geo_id': 9999,
                'country': 225,
                'city': 213,
                'as_list': 'AS13238',
            },
        )

    def test_extract_user_agent_features(self):
        fresh_profile = make_profile_from_raw_data('127.0.0.1', None, TEST_UATRAITS_INFO)

        features_dict = FeaturesBuilderProfileV1().extract_features(fresh_profile, {})

        self.assert_features_present(
            features_dict,
            {
                'browser': 'OperaMini 6.5',
                'browser_name': 'OperaMini',
                'browser_os': 'OperaMini 6.5 - Java',
                'browser_version': '6.5',
                'is_mobile': 1,
                'os_family': 'Java',
                'os_name': 'Java',
                'os_version': None,
            },
        )

    def test_extract_profile_count_features(self):
        fresh_profile = make_profile_from_raw_data('127.0.0.1', None, {})

        features_dict = FeaturesBuilderProfileV1().extract_features(
            fresh_profile,
            {
                'succ_auth_count_1w': 100400,
                'succ_auth_count_1m': 100500,
            },
        )

        self.assert_features_present(
            features_dict,
            {
                'succ_auth_count_1d': 0,
                'succ_auth_count_1w': 100400,
                'succ_auth_count_1m': 100500,
            },
        )

    def test_extract_profile_probability_based_features(self):
        fresh_profile = make_profile_from_raw_data('127.0.0.1', None, TEST_UATRAITS_INFO)

        features_dict = FeaturesBuilderProfileV1().extract_features(
            fresh_profile,
            {
                u'browser_freq_1m': [
                    [u'YandexBrowser 15.10.2454.3865', 1],
                    [u'OperaMini 6.5', 2],
                    [u'OperaMini 6.7', 1],
                ],
                u'browser_name_freq_1m': [
                    [u'YandexBrowser', 1],
                    [u'OperaMini', 3],
                ],
                u'browser_os_freq_1m': [
                    [u'YandexBrowser 15.10.2454.3865 - Windows 7', 1],
                    [u'OperaMini 6.5 - Java', 2],
                    [u'OperaMini 6.7 - Java', 1],
                ],
                u'os_name_freq_1m': [[u'Windows 7', 1], ['Java', 3]],
            },
        )

        self.assert_features_present(
            features_dict,
            {
                'browser_grouped_prob_1d': 0,
                'browser_grouped_prob_1m': 0.5,
                'browser_name_prob_1d': 0,
                'browser_name_prob_1m': 0.75,
                'browser_os_prob_1m': 0.5,
                'browser_prob_1d': 0,
                'browser_prob_1m': 0.5,
                'os_name_prob_1d': 0,
                'os_name_prob_1m': 0.75,
            },
        )

    def test_extract_as_list_features(self):
        region_mock = mock.Mock()
        region_mock.AS_list = ['AS1', 'AS2', 'AS3']
        region_mock.country = {}
        region_mock.city = {}
        with mock.patch('passport.backend.core.env_profile.helpers.Region', lambda ip, geobase=None: region_mock):
            fresh_profile = make_profile_from_raw_data('127.0.0.1', None, {})

        full_profile = {
            'as_list_freq_1m': [
                ['AS1', 1],
                ['AS2', 4],
                ['AS4', 5],
            ],
        }
        with mock.patch('passport.backend.api.common.profile.features.Region', lambda ip, geobase=None: region_mock):
            features_dict = FeaturesBuilderProfileV1().extract_features(fresh_profile, full_profile)

        self.assert_features_present(
            features_dict,
            {
                'as_list': 'AS1,AS2,AS3',
                'as_list_prob_1m': 0.5,
            },
        )

    def test_extract_referer_retpath_features(self):
        fresh_profile = make_profile_from_raw_data('127.0.0.1', None, {})

        features_dict = FeaturesBuilderProfileV1().extract_features(
            fresh_profile,
            {},
            referer='http://referer.yandex.ru:8080',
            retpath='https://abcd.efg.okna.ru/100500',
        )

        self.assert_features_present(
            features_dict,
            {
                'retpath_host_2': 'okna.ru',
                'retpath_host_3': 'efg.okna.ru',
                'referer_host_2': 'yandex.ru',
                'referer_host_3': 'referer.yandex.ru',
            },
        )

    def test_extract_features_from_empty_data(self):
        """Извлекаем факторы на пустых данных - проверяем полученные граничные значения"""
        fresh_profile = make_profile_from_raw_data('127.0.0.1', None, {})

        features_dict = FeaturesBuilderProfileV1().extract_features(fresh_profile, {})

        eq_(
            features_dict,
            get_v1_empty_features(),
        )


@with_settings_hosts()
class AuthFeaturesBuilderV2TestCase(BaseFeaturesBuilderTestCase):
    def test_extract_su_features(self):
        region_mock = mock.Mock()
        region_mock.AS_list = ['AS1', 'AS2', 'AS3']
        region_mock.city = {'id': 213}
        region_mock.country = {'id': 255}

        dt = datetime(2016, 1, 16, hour=16)  # суббота
        timestamp = datetime_to_integer_unixtime(dt)
        with mock.patch('passport.backend.core.env_profile.helpers.Region', lambda ip, geobase=None: region_mock):
            fresh_profile = make_profile_from_raw_data('95.47.182.98', None, TEST_UATRAITS_INFO, timestamp=timestamp)

        full_profile = {
            u'su_as_list_freq_6m': [  # эта фича не должна ни на что влиять
                ['AS1', 2],
                ['AS2', 10],
                ['AS4', 28],
            ],
            u'su_as_list_freq_3m': [
                ['AS1', 1],
                ['AS2', 5],
                ['AS4', 14],
            ],
            u'su_browser_freq_6m': [  # эта фича не должна ни на что влиять
                [u'YandexBrowser 15.10.2454.3865', 2],
                [u'OperaMini 6.5', 4],
                [u'OperaMini 6.7', 2],
            ],
            u'su_browser_freq_1m': [
                [u'YandexBrowser 15.10.2454.3865', 1],
                [u'OperaMini 6.5', 2],
                [u'OperaMini 6.7', 1],
            ],
            u'su_browser_name_freq_3m': [
                [u'YandexBrowser', 1],
                [u'OperaMini', 3],
            ],
            u'su_browser_os_freq_3m': [
                [u'YandexBrowser 15.10.2454.3865 - Windows 7', 1],
                [u'OperaMini 6.5 - Java', 2],
                [u'OperaMini 6.7 - Java', 1],
            ],
            u'su_city_freq_3m': [
                [213, 23],
            ],
            u'su_country_freq_1d': [
                [255, 1],
            ],
            u'su_day_part_freq_1m': [
                [0, 1],
                [2, 4],
            ],
            u'su_ip_freq_3m': [
                [
                    '95.47.182.98',
                    5,
                ],
                [
                    '127.0.0.1',
                    5,
                ],
            ],
            u'su_weekday_freq_3m': [
                [1, 5],
                [2, 5],
                [3, 3],
                [4, 5],
                [5, 3],
                [7, 2],
            ],
            u'su_is_mobile_freq_3m': [
                [0, 23],
                [1, 27],
            ],
        }
        with mock.patch('passport.backend.api.common.profile.features.Region', lambda ip, geobase=None: region_mock):
            features_dict = FeaturesBuilderProfileV2().extract_features(fresh_profile, full_profile)

        self.assert_features_present(
            features_dict,
            {
                'su_as_list_prob_1m': 0,
                'su_as_list_prob_3m': 0.3,
                'su_browser_prob_1m': 0.5,
                'su_browser_name_prob_3m': 0.75,
                'su_browser_os_prob_3m': 0.5,
                'su_city_prob_3m': 1,
                'su_country_prob_1d': 1,
                'su_day_part_prob_1m': 0.8,
                'su_ip_prob_3m': 0.5,
                'su_weekday_prob_3m': 0,
                'su_is_mobile_prob_3m': 0.54,
            },
        )

    def test_extract_features_from_empty_data(self):
        """Извлекаем факторы на пустых данных - проверяем полученные граничные значения"""
        fresh_profile = make_profile_from_raw_data('127.0.0.1', None, {})

        features_dict = FeaturesBuilderProfileV2().extract_features(fresh_profile, {})

        eq_(
            features_dict,
            dict(
                get_v1_empty_features(),
                as_list_prob_3m=0,
                browser_grouped_prob_3m=0,
                browser_name_prob_3m=0,
                browser_os_prob_3m=0,
                browser_prob_3m=0,
                city_prob_3m=0,
                country_prob_3m=0,
                day_part_prob_3m=0,
                ip_prob_3m=0,
                os_family_prob_3m=0,
                os_name_prob_3m=0,
                referer_host_2_prob_3m=0,
                referer_host_3_prob_3m=0,
                retpath_host_2_prob_3m=0,
                retpath_host_3_prob_3m=0,
                weekday_prob_3m=0,
                yandexuid_prob_3m=0,
                su_as_list_prob_1d=0,
                su_as_list_prob_1m=0,
                su_as_list_prob_1w=0,
                su_as_list_prob_3m=0,
                su_browser_name_prob_1d=0,
                su_browser_name_prob_1m=0,
                su_browser_name_prob_1w=0,
                su_browser_name_prob_3m=0,
                su_browser_os_prob_1d=0,
                su_browser_os_prob_1m=0,
                su_browser_os_prob_1w=0,
                su_browser_os_prob_3m=0,
                su_browser_prob_1d=0,
                su_browser_prob_1m=0,
                su_browser_prob_1w=0,
                su_browser_prob_3m=0,
                su_city_prob_1d=0,
                su_city_prob_1m=0,
                su_city_prob_1w=0,
                su_city_prob_3m=0,
                su_country_prob_1d=0,
                su_country_prob_1m=0,
                su_country_prob_1w=0,
                su_country_prob_3m=0,
                su_day_part_prob_1d=0,
                su_day_part_prob_1m=0,
                su_day_part_prob_1w=0,
                su_day_part_prob_3m=0,
                su_ip_prob_1d=0,
                su_ip_prob_1m=0,
                su_ip_prob_1w=0,
                su_ip_prob_3m=0,
                su_is_mobile_prob_1d=0,
                su_is_mobile_prob_1m=0,
                su_is_mobile_prob_1w=0,
                su_is_mobile_prob_3m=0,
                su_weekday_prob_1d=0,
                su_weekday_prob_1m=0,
                su_weekday_prob_1w=0,
                su_weekday_prob_3m=0,
            ),
        )


@with_settings_hosts()
class AuthFeaturesBuilderV3TestCase(BaseFeaturesBuilderTestCase):
    def test_extract_su_features(self):
        region_mock = mock.Mock()
        region_mock.AS_list = ['AS1', 'AS2', 'AS3']
        region_mock.city = {'id': 213}
        region_mock.country = {'id': 255}

        dt = datetime(2016, 1, 16, hour=16)  # суббота
        timestamp = datetime_to_integer_unixtime(dt)
        with mock.patch('passport.backend.core.env_profile.helpers.Region', lambda ip, geobase=None: region_mock):
            fresh_profile = make_profile_from_raw_data('95.47.182.98', None, TEST_UATRAITS_INFO, timestamp=timestamp)

        full_profile = {
            u'su_as_list_freq_6m': [
                ['AS1', 2],
                ['AS2', 10],
                ['AS4', 28],
            ],
            u'su_as_list_freq_3m': [
                ['AS1', 1],
                ['AS2', 5],
                ['AS4', 14],
            ],
            u'su_browser_freq_6m': [
                [u'YandexBrowser 15.10.2454.3865', 2],
                [u'OperaMini 6.5', 4],
                [u'OperaMini 6.7', 2],
            ],
            u'su_browser_freq_1m': [
                [u'YandexBrowser 15.10.2454.3865', 1],
                [u'OperaMini 6.5', 2],
                [u'OperaMini 6.7', 1],
            ],
            u'su_browser_name_freq_6m': [
                [u'YandexBrowser', 2],
                [u'OperaMini', 6],
            ],
            u'su_browser_name_freq_3m': [
                [u'YandexBrowser', 1],
                [u'OperaMini', 3],
            ],
            u'su_browser_os_freq_6m': [
                [u'YandexBrowser 15.10.2454.3865 - Windows 7', 2],
                [u'OperaMini 6.5 - Java', 4],
                [u'OperaMini 6.7 - Java', 2],
            ],
            u'su_browser_os_freq_3m': [
                [u'YandexBrowser 15.10.2454.3865 - Windows 7', 1],
                [u'OperaMini 6.5 - Java', 2],
                [u'OperaMini 6.7 - Java', 1],
            ],
            u'su_city_freq_6m': [
                [213, 46],
            ],
            u'su_city_freq_3m': [
                [213, 23],
            ],
            u'su_country_freq_1d': [
                [255, 1],
            ],
            u'su_day_part_freq_6m': [
                [0, 2],
                [2, 8],
            ],
            u'su_day_part_freq_1m': [
                [0, 1],
                [2, 4],
            ],
            u'su_ip_freq_6m': [
                [
                    '95.47.182.98',
                    10,
                ],
                [
                    '127.0.0.1',
                    10,
                ],
            ],
            u'su_ip_freq_3m': [
                [
                    '95.47.182.98',
                    5,
                ],
                [
                    '127.0.0.1',
                    5,
                ],
            ],
            u'su_weekday_freq_6m': [
                [1, 10],
                [2, 10],
                [3, 6],
                [4, 10],
                [5, 6],
                [7, 4],
            ],
            u'su_weekday_freq_3m': [
                [1, 5],
                [2, 5],
                [3, 3],
                [4, 5],
                [5, 3],
                [7, 2],
            ],
            u'su_is_mobile_freq_6m': [
                [0, 46],
                [1, 54],
            ],
            u'su_is_mobile_freq_3m': [
                [0, 23],
                [1, 27],
            ],
        }

        with mock.patch('passport.backend.api.common.profile.features.Region', lambda ip, geobase=None: region_mock):
            features_dict = FeaturesBuilderProfileV3().extract_features(fresh_profile, full_profile)

        self.assert_features_present(
            features_dict,
            {
                'su_as_list_prob_6m': 0.3,
                'su_browser_prob_6m': 0.5,
                'su_browser_name_prob_6m': 0.75,
                'su_browser_os_prob_6m': 0.5,
                'su_city_prob_6m': 1,
                'su_country_prob_1d': 1,
                'su_day_part_prob_6m': 0.8,
                'su_ip_prob_6m': 0.5,
                'su_weekday_prob_6m': 0,
                'su_is_mobile_prob_6m': 0.54,
            },
        )

    def test_extract_features_from_empty_data(self):
        """Извлекаем факторы на пустых данных - проверяем полученные граничные значения"""
        fresh_profile = make_profile_from_raw_data('127.0.0.1', None, {})

        features_dict = FeaturesBuilderProfileV3().extract_features(fresh_profile, {})

        expected_features = {
            k: v for k, v in dict(
                get_v1_empty_features(),
                as_list_prob_6m=0,
                browser_grouped_prob_6m=0,
                browser_name_prob_6m=0,
                browser_os_prob_6m=0,
                browser_prob_6m=0,
                city_prob_6m=0,
                country_prob_6m=0,
                day_part_prob_6m=0,
                ip_prob_6m=0,
                os_family_prob_6m=0,
                os_name_prob_6m=0,
                referer_host_2_prob_6m=0,
                referer_host_3_prob_6m=0,
                retpath_host_2_prob_6m=0,
                retpath_host_3_prob_6m=0,
                weekday_prob_6m=0,
                yandexuid_prob_6m=0,
                su_as_list_prob_1d=0,
                su_as_list_prob_6m=0,
                su_browser_name_prob_1d=0,
                su_browser_name_prob_6m=0,
                su_browser_os_prob_1d=0,
                su_browser_os_prob_6m=0,
                su_browser_prob_1d=0,
                su_browser_prob_6m=0,
                su_city_prob_1d=0,
                su_city_prob_6m=0,
                su_country_prob_1d=0,
                su_country_prob_6m=0,
                su_day_part_prob_1d=0,
                su_day_part_prob_6m=0,
                su_ip_prob_1d=0,
                su_ip_prob_6m=0,
                su_is_mobile_prob_1d=0,
                su_is_mobile_prob_6m=0,
                su_weekday_prob_1d=0,
                su_weekday_prob_6m=0,
            ).items() if not k.endswith('_1m') and not k.endswith('_1w')
        }

        eq_(
            features_dict,
            expected_features,
        )
