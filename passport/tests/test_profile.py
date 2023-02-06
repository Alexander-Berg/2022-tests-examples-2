# -*- coding: utf-8 -*-
import json
import unittest
import uuid

from nose.tools import (
    assert_is_none,
    eq_,
    ok_,
    raises,
)
from passport.backend.core.env_profile import EnvProfileV1
from passport.backend.core.env_profile.tests.base_test_data import (
    TEST_AS_LIST,
    TEST_BROWSER_ID,
    TEST_CITY_ID,
    TEST_COUNTRY_ID,
    TEST_ENV_PROFILE_KWARGS,
    TEST_ENVIRONMENT_TIMESTAMP,
    TEST_ENVIRONMENT_TIMEUUID,
    TEST_ENVIRONMENT_VERSION,
    TEST_OS_ID,
    TEST_YANDEXUID_TIMESTAMP,
)
from passport.backend.core.test.time_utils.time_utils import (
    TimeNow,
    TimeSpan,
)


class TestEnvProfile(unittest.TestCase):
    def test_profile_create_ok(self):
        env_profile = EnvProfileV1(**TEST_ENV_PROFILE_KWARGS)
        eq_(env_profile.version, TEST_ENVIRONMENT_VERSION)
        eq_(env_profile.age + TEST_ENVIRONMENT_TIMESTAMP, TimeNow())
        eq_(env_profile.AS_list, TEST_AS_LIST)
        eq_(env_profile.country_id, TEST_COUNTRY_ID)
        eq_(env_profile.city_id, TEST_CITY_ID)
        eq_(env_profile.browser_id, TEST_BROWSER_ID)
        eq_(env_profile.os_id, TEST_OS_ID)
        eq_(env_profile.yandexuid_timestamp, TEST_YANDEXUID_TIMESTAMP)
        eq_(env_profile.is_mobile, None)

    def test_profile_create_mobile_ok(self):
        env_profile = EnvProfileV1(is_mobile=True, **TEST_ENV_PROFILE_KWARGS)
        eq_(env_profile.version, TEST_ENVIRONMENT_VERSION)
        eq_(env_profile.age + TEST_ENVIRONMENT_TIMESTAMP, TimeNow())
        eq_(env_profile.AS_list, TEST_AS_LIST)
        eq_(env_profile.country_id, TEST_COUNTRY_ID)
        eq_(env_profile.city_id, TEST_CITY_ID)
        eq_(env_profile.browser_id, TEST_BROWSER_ID)
        eq_(env_profile.os_id, TEST_OS_ID)
        eq_(env_profile.yandexuid_timestamp, TEST_YANDEXUID_TIMESTAMP)
        eq_(env_profile.is_mobile, True)

    def test_profile_create_empty_ok(self):
        env_profile = EnvProfileV1()
        eq_(env_profile.version, 1)
        eq_(env_profile.age, TimeSpan(0))
        assert_is_none(env_profile.AS_list)
        assert_is_none(env_profile.country_id)
        assert_is_none(env_profile.city_id)
        assert_is_none(env_profile.browser_id)
        assert_is_none(env_profile.os_id)
        assert_is_none(env_profile.yandexuid_timestamp)

    def test_profile_create_ok_with_raw_env(self):
        env_profile = EnvProfileV1(raw_env={'a': 'b'}, **TEST_ENV_PROFILE_KWARGS)
        eq_(env_profile.version, TEST_ENVIRONMENT_VERSION)
        eq_(env_profile.age + TEST_ENVIRONMENT_TIMESTAMP, TimeNow())
        eq_(env_profile.AS_list, TEST_AS_LIST)
        eq_(env_profile.country_id, TEST_COUNTRY_ID)
        eq_(env_profile.city_id, TEST_CITY_ID)
        eq_(env_profile.browser_id, TEST_BROWSER_ID)
        eq_(env_profile.os_id, TEST_OS_ID)
        eq_(env_profile.yandexuid_timestamp, TEST_YANDEXUID_TIMESTAMP)
        eq_(env_profile.raw_env, {'a': 'b'})

    @raises(ValueError)
    def test_profile_create_unknown_field_error(self):
        EnvProfileV1(foo='bar')

    def test_as_dict(self):
        env_profile = EnvProfileV1(**TEST_ENV_PROFILE_KWARGS)
        eq_(
            env_profile.as_dict,
            {
                'timeuuid': str(TEST_ENVIRONMENT_TIMEUUID),
                'timestamp': TEST_ENVIRONMENT_TIMESTAMP,
                'city_id': TEST_CITY_ID,
                'browser_id': TEST_BROWSER_ID,
                'country_id': TEST_COUNTRY_ID,
                'os_id': TEST_OS_ID,
                'AS_list': TEST_AS_LIST,
                'yandexuid_timestamp': TEST_YANDEXUID_TIMESTAMP,
                'is_mobile': None,
                'am_version': None,
                'device_id': None,
                'cloud_token': None,
            },
        )

    def test_as_json(self):
        env_profile = EnvProfileV1(**TEST_ENV_PROFILE_KWARGS)
        eq_(
            env_profile.as_json,
            json.dumps(env_profile.as_dict),
        )

    def test_eq(self):
        uuid_bytes = uuid.uuid1().bytes
        profile1 = EnvProfileV1(**TEST_ENV_PROFILE_KWARGS)
        profile2 = EnvProfileV1(timestamp=100, timeuuid=uuid_bytes)
        profile3 = EnvProfileV1(timestamp=100, timeuuid=uuid_bytes)
        profile4 = EnvProfileV1()
        profile5 = EnvProfileV1(timestamp=100, timeuuid=uuid.uuid1().bytes)
        profile6 = EnvProfileV1(is_mobile=True, **TEST_ENV_PROFILE_KWARGS)
        ok_(profile1 != 42)
        ok_(profile1 != profile2)
        ok_(profile1 != profile3)
        ok_(profile1 != profile4)
        ok_(profile1 != profile6)
        ok_(profile2 != profile4)
        eq_(profile2, profile3)
        ok_(profile2 != profile5)

    def test_repr(self):
        env_profile = EnvProfileV1(**TEST_ENV_PROFILE_KWARGS)
        eq_(
            repr(env_profile),
            '<EnvProfileV1 ts=%s uuid=%s>' % (
                TEST_ENVIRONMENT_TIMESTAMP,
                TEST_ENVIRONMENT_TIMEUUID,
            ),
        )
