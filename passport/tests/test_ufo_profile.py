# -*- coding: utf-8 -*-
import base64
from datetime import (
    datetime,
    timedelta,
)
import unittest
import uuid

from nose.tools import (
    assert_is_none,
    eq_,
    ok_,
)
from passport.backend.core.builders.ufo_api.faker import (
    encode_ufo_data,
    TEST_FRESH_ITEM,
    TEST_TIMEUUID,
    ufo_api_profile_item,
)
from passport.backend.core.env_profile import (
    EnvDistance,
    EnvProfileV1,
)
from passport.backend.core.env_profile.helpers import make_profile_from_raw_data
from passport.backend.core.env_profile.loader import repack_ydb_to_ufo
from passport.backend.core.env_profile.profiles import UfoProfile
from passport.backend.core.env_profile.tests.base_test_data import (
    TEST_COUNTRY_ID,
    TEST_ENV_PROFILE_KWARGS,
    UATRAITS_SETTINGS,
)
from passport.backend.core.test.test_utils import with_settings
from passport.backend.core.ydb.faker.stubs import ydb_profile_item
from passport.backend.utils.time import (
    datetime_to_integer_unixtime,
    timeuuid_to_timestamp,
)


TEST_FULL_PROFILE = {'factor1': 1, 'factor2': 2}
TEST_FULL_PROFILE_WITH_MOBILE_INFO = dict(
    TEST_FULL_PROFILE,
    it_device_id_freq_6m=[('device_id1', 1), ('device_id2', 100500)],
    it_cloud_token_freq_6m=[('cloud_token1', 1), ('cloud_token2', 100500)],
)
TEST_FRESH_ITEM_WITH_MOBILE_INFO = dict(
    TEST_FRESH_ITEM,
    device_id='device_id3',
    cloud_token='cloud_token3',
)


@with_settings(
    YDB_PERCENTAGE=100,
    TRY_USE_YDB=True,
    **UATRAITS_SETTINGS
)
class TestUfoProfileInYdb(unittest.TestCase):
    def test_init_with_full_profile_only(self):
        full_profile = ydb_profile_item(set_full_profile_flag=True)
        items = repack_ydb_to_ufo([
            full_profile,
        ])
        profile = UfoProfile(items, data_decoder=lambda x: x)

        eq_(profile.full_profile, full_profile)
        fresh_profiles = list(profile.fresh_profiles)
        eq_(len(fresh_profiles), 0)

    def test_init_with_fresh_profile_only(self):
        fresh_profile = ydb_profile_item()
        items = repack_ydb_to_ufo([
            fresh_profile,
        ])
        profile = UfoProfile(items, data_decoder=lambda x: x)

        fresh_profiles = list(profile.fresh_profiles)
        eq_(len(fresh_profiles), 1)
        eq_(profile.full_profile, None)
        eq_(
            str(list(profile.fresh_profiles)[0]),
            '<EnvProfileV1 ts=1446212433 uuid=cae45e80-7f0b-11e5-8000-000000000000>',
        )

    def test_init_with_full_and_fresh_profiles(self):
        full_profile = ydb_profile_item(set_full_profile_flag=True)
        fresh_profile = ydb_profile_item()
        items = repack_ydb_to_ufo([
            full_profile,
            fresh_profile,
        ])
        profile = UfoProfile(items, data_decoder=lambda x: x)

        fresh_profiles = list(profile.fresh_profiles)
        eq_(len(fresh_profiles), 1)
        eq_(profile.full_profile, full_profile)
        eq_(
            str(list(profile.fresh_profiles)[0]),
            '<EnvProfileV1 ts=1446212433 uuid=cae45e80-7f0b-11e5-8000-000000000000>',
        )

    def test_repack_ydb_to_ufo_with_date_filter_empty_response(self):
        # все профили имеют таймстемп час назад, а глогаут был только что, вернется пустой список профилей
        now = datetime.today()
        timestamp_now = datetime_to_integer_unixtime(now)
        timestamp_hour_ago = datetime_to_integer_unixtime(now - timedelta(hours=1))
        full_profile = ydb_profile_item(set_full_profile_flag=True, timestamp=timestamp_hour_ago)
        fresh_profile = ydb_profile_item(timestamp=timestamp_hour_ago)
        items = repack_ydb_to_ufo([
            full_profile,
            fresh_profile,
        ],
            glogout_timestamp=timestamp_now,
        )
        eq_(len(items), 0)

    def test_repack_ydb_to_ufo_with_date_filter(self):
        # все профили имеют таймстемп текущий, а глогаут был час назад, вернутся все профили
        now = datetime.today()
        timestamp_now = datetime_to_integer_unixtime(now)
        timestamp_hour_ago = datetime_to_integer_unixtime(now - timedelta(hours=1))
        full_profile = ydb_profile_item(set_full_profile_flag=True, timestamp=timestamp_now)
        fresh_profile = ydb_profile_item(timestamp=timestamp_now)
        items = repack_ydb_to_ufo([
            full_profile,
            fresh_profile,
        ],
            glogout_timestamp=timestamp_hour_ago,
        )
        eq_(len(items), 2)


@with_settings(**UATRAITS_SETTINGS)
class TestUfoProfileBase(unittest.TestCase):
    def test_init_with_empty_profiles(self):
        profile = UfoProfile([])

        assert_is_none(profile.full_profile)
        eq_(profile._fresh_profiles_cache, [])
        eq_(list(profile.fresh_profiles), [])

    def test_init_with_full_profile(self):
        items = [
            ufo_api_profile_item(UfoProfile.PROFILE_FAKE_UUID, TEST_FULL_PROFILE),
            ufo_api_profile_item(),
        ]
        profile = UfoProfile(items)

        eq_(profile._full_profile, encode_ufo_data(TEST_FULL_PROFILE))
        eq_(profile.full_profile, TEST_FULL_PROFILE)

        fresh_profiles = list(profile.fresh_profiles)
        eq_(len(fresh_profiles), 1)
        eq_(fresh_profiles[0], EnvProfileV1(**TEST_ENV_PROFILE_KWARGS))

    def test_fresh_profiles_generator_retry(self):
        uuids = [uuid.uuid1() for _ in range(5)]
        items = [ufo_api_profile_item(timeuuid=timeuuid.hex) for timeuuid in uuids]
        profile = UfoProfile(items)

        # В первый раз используем генератор не полностью
        gen_1 = profile.fresh_profiles
        profiles_1 = [next(gen_1) for _ in range(3)]
        for i in range(3):
            eq_(profiles_1[i].timeuuid, uuids[i].bytes)
        # Убеждаемся что в кеше только часть профилей
        eq_(profile._fresh_profiles_cache, profiles_1)

        # Во второй раз достаем все fresh-профили
        profiles_2 = list(profile.fresh_profiles)
        eq_(len(profiles_2), 5)
        for i in range(5):
            eq_(profiles_2[i].timeuuid, uuids[i].bytes)
        eq_(profile._fresh_profiles_cache, profiles_2)

    def test_fresh_profiles_invalid_items(self):
        items = [
            {'id': '1234', 'data': base64.b64encode(b'not-json')},
            ufo_api_profile_item(),
            {'id': '1234', 'data': 'not-a-base64'},
        ]
        profile = UfoProfile(items)
        eq_(list(profile.fresh_profiles), [EnvProfileV1(**TEST_ENV_PROFILE_KWARGS)])

    def test_full_profile_parsing(self):
        encoded_decoded_values = (
            (base64.b64encode(b'not-json'), None),
            ('not-a-base64', None),
            (encode_ufo_data(TEST_FULL_PROFILE), TEST_FULL_PROFILE),
        )
        for encoded_value, expected_value in encoded_decoded_values:
            item = {'id': UfoProfile.PROFILE_FAKE_UUID, 'data': encoded_value}
            profile = UfoProfile([item])
            eq_(profile.full_profile, expected_value)

    def test_trusted_device_ids(self):
        items = [
            ufo_api_profile_item(UfoProfile.PROFILE_FAKE_UUID, data=TEST_FULL_PROFILE_WITH_MOBILE_INFO),
            ufo_api_profile_item(data=TEST_FRESH_ITEM_WITH_MOBILE_INFO),
            ufo_api_profile_item(data=TEST_FRESH_ITEM),
        ]
        profile = UfoProfile(items)
        eq_(
            profile.trusted_device_ids,
            {'device_id1', 'device_id2', 'device_id3'},
        )

    def test_trusted_cloud_tokens(self):
        items = [
            ufo_api_profile_item(UfoProfile.PROFILE_FAKE_UUID, data=TEST_FULL_PROFILE_WITH_MOBILE_INFO),
            ufo_api_profile_item(data=TEST_FRESH_ITEM_WITH_MOBILE_INFO),
            ufo_api_profile_item(data=TEST_FRESH_ITEM),
        ]
        profile = UfoProfile(items)
        eq_(
            profile.trusted_cloud_tokens,
            {'cloud_token1', 'cloud_token2', 'cloud_token3'},
        )

    def test_has_no_full_profile(self):
        # нет полного профиля, список довереных устройств должен верно собираться из фреш профиля
        items = [
            ufo_api_profile_item(data=TEST_FRESH_ITEM_WITH_MOBILE_INFO),
        ]
        profile = UfoProfile(items)
        eq_(
            profile.trusted_device_ids,
            {'device_id3'},
        )
        eq_(
            profile.trusted_cloud_tokens,
            {'cloud_token3'},
        )


@with_settings(**UATRAITS_SETTINGS)
class TestUfoProfileFindClosest(unittest.TestCase):
    def test_find_closest_exact_match(self):
        items = [
            ufo_api_profile_item(),
            ufo_api_profile_item(data={
                'ip': '1.1.1.1',
                'yandexuid': None,
                'user_agent_info': {},
            }),
        ]
        profile = UfoProfile(items)
        new_env_profile = EnvProfileV1(**TEST_ENV_PROFILE_KWARGS)

        closest_env_profile, distance = profile.find_closest(new_env_profile)

        eq_(distance, EnvDistance.Min)
        eq_(new_env_profile, closest_env_profile)
        # Убеждаемся, что распарсили только один элемент
        eq_(len(profile._fresh_profiles_cache), 1)
        eq_(len(list(profile.fresh_profiles)), 2)

    def test_find_closest_max_distance(self):
        items = [
            ufo_api_profile_item(data={
                'ip': '1.1.1.1',
                'yandexuid': '123456',
                'user_agent_info': {},
            }),
            ufo_api_profile_item(data={
                'ip': '1.1.1.1',
                'yandexuid': None,
                'user_agent_info': {},
            }),
        ]
        profile = UfoProfile(items)
        new_env_profile = EnvProfileV1(**TEST_ENV_PROFILE_KWARGS)

        closest_env_profile, distance = profile.find_closest(new_env_profile)

        eq_(distance, EnvDistance.Max)
        ok_(closest_env_profile is not None)

    def test_find_closest_with_no_items(self):
        profile = UfoProfile([])
        new_env_profile = EnvProfileV1(**TEST_ENV_PROFILE_KWARGS)

        closest_env_profile, distance = profile.find_closest(new_env_profile)

        eq_(distance, EnvDistance.Max)
        assert_is_none(closest_env_profile)

    def test_find_closest_with_full_scan(self):
        items = [
            ufo_api_profile_item(data={
                'ip': '1.1.1.1',
                'yandexuid': None,
                'user_agent_info': {},
            }),
            ufo_api_profile_item(),
        ]
        profile = UfoProfile(items)
        new_env_profile = EnvProfileV1(**TEST_ENV_PROFILE_KWARGS)

        closest_env_profile, distance = profile.find_closest(new_env_profile)

        eq_(distance, EnvDistance.Min)
        eq_(new_env_profile, closest_env_profile)
        # Убеждаемся, что распарсили все элементы
        eq_(len(profile._fresh_profiles_cache), 2)

    def test_find_closest_medium_distance(self):
        items = [
            ufo_api_profile_item(data={
                'ip': '1.1.1.1',
                'yandexuid': None,
                'user_agent_info': {},
            }),
            ufo_api_profile_item(),
        ]
        profile = UfoProfile(items)
        new_env_profile = EnvProfileV1(
            AS_list=[],
            country_id=TEST_COUNTRY_ID,
            city_id=None,
        )

        closest_env_profile, distance = profile.find_closest(new_env_profile)

        eq_(distance, (EnvDistance.Medium + EnvDistance.High) / 2)
        ok_(new_env_profile != closest_env_profile)


@with_settings(**UATRAITS_SETTINGS)
class TestUfoProfileProcessNewProfile(unittest.TestCase):
    def test_new_profile(self):
        items = [
            ufo_api_profile_item(data={
                'ip': '1.1.1.1',
                'yandexuid': None,
                'user_agent_info': {},
            }),
        ]
        profile = UfoProfile(items)
        new_env_profile = EnvProfileV1(**TEST_ENV_PROFILE_KWARGS)

        result = profile.process_new_profile(new_env_profile)

        # Проверяем, что данные в объекте не изменились
        timeuuid = uuid.UUID(hex=TEST_TIMEUUID)
        eq_(
            list(profile.fresh_profiles),
            [
                make_profile_from_raw_data(
                    '1.1.1.1',
                    None,
                    {},
                    timeuuid=timeuuid.bytes,
                    timestamp=timeuuid_to_timestamp(timeuuid),
                ),
            ],
        )
        # Проверяем результат
        eq_(result.closest_distance, EnvDistance.Max)
        eq_(result.profile, new_env_profile)

    def test_new_profile_with_all_fields(self):
        items = [
            ufo_api_profile_item(data={
                'ip': '1.1.1.1',
                'yandexuid': 'yu',
                'user_agent_info': {},
                'is_mobile': True,
                'device_id': 'device-id',
                'am_version': 'am-version',
                'cloud_token': 'cloud-token',
            }),
        ]
        profile = UfoProfile(items)
        new_env_profile = EnvProfileV1(**TEST_ENV_PROFILE_KWARGS)

        profile.process_new_profile(new_env_profile)

        timeuuid = uuid.UUID(hex=TEST_TIMEUUID)
        eq_(
            list(profile.fresh_profiles),
            [
                make_profile_from_raw_data(
                    ip='1.1.1.1',
                    yandexuid='yu',
                    user_agent_info={},
                    is_mobile=True,
                    device_id='device-id',
                    am_version='am-version',
                    cloud_token='cloud-token',
                    timeuuid=timeuuid.bytes,
                    timestamp=timeuuid_to_timestamp(timeuuid),
                ),
            ],
        )

    def test_update_profile(self):
        other_timeuuid = uuid.uuid1()
        items = [
            ufo_api_profile_item(),
        ]
        profile = UfoProfile(items)
        new_env_profile = EnvProfileV1(**dict(TEST_ENV_PROFILE_KWARGS, timeuuid=other_timeuuid.bytes))

        result = profile.process_new_profile(new_env_profile)

        # Проверяем, что данные в объекте не изменились
        eq_(
            list(profile.fresh_profiles),
            [
                new_env_profile,
            ],
        )
        # Проверяем результат
        eq_(result.closest_distance, EnvDistance.Min)
        eq_(result.profile, new_env_profile)
        # Проверяем, что timeuuid в новом профиле обновился
        eq_(new_env_profile.timeuuid, uuid.UUID(hex=TEST_TIMEUUID).bytes)
