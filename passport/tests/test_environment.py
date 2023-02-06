# -*- coding: utf-8 -*-
import unittest

from nose.tools import (
    assert_is_none,
    eq_,
)
from passport.backend.core.env import Environment
from passport.backend.core.env_profile.tests.base_test_data import (
    TEST_AS_LIST,
    TEST_BROWSER_ID,
    TEST_CITY_ID,
    TEST_COUNTRY_ID,
    TEST_ENVIRONMENT_VERSION,
    TEST_OS_ID,
    TEST_YANDEXUID_TIMESTAMP,
    UATRAITS_SETTINGS,
)
from passport.backend.core.test.test_utils import with_settings
from passport.backend.core.test.time_utils.time_utils import TimeNow
from passport.backend.core.types.ip.ip import IP


TEST_IP = '5.45.207.254'
TEST_USER_AGENT = 'Opera/9.80 (J2ME/MIDP; Opera Mini/6.5.26955/27.1573; U; ru) Presto/2.8.119 Version/11.10'
TEST_UATRAITS_INFO = {
    'OSFamily': 'Java',
    'BrowserEngine': 'Presto',
    'isBrowser': True,
    'BrowserVersion': '6.5',
    'BrowserName': 'OperaMini',
    'BrowserEngineVersion': '2.8.119',
    'J2ME': True,
    'isMobile': True,
}
TEST_OTHER_USER_AGENT = 'Mozilla/5.0 (Linux; Android 4.4.4; Nexus 4 Build/KTU84P) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/38.0.2125.102 Mobile Safari/537.36'
TEST_DUMMY_USER_AGENT = 'curl/7.22.0'
TEST_YANDEXUID = '3281059040000000099'


@with_settings(
    **UATRAITS_SETTINGS
)
class TestEnvironment(unittest.TestCase):
    def test_make_profile_ok(self):
        env = Environment(
            cookies={'yandexuid': TEST_YANDEXUID},
            consumer_ip='8.8.8.8',
            user_ip=TEST_IP,
            user_agent=TEST_USER_AGENT,
            host='yandex.ru',
            accept_language=None,
            referer=None,
        )
        profile = env.make_profile()
        eq_(profile.version, TEST_ENVIRONMENT_VERSION)
        eq_(profile.timestamp, TimeNow())
        eq_(profile.AS_list, TEST_AS_LIST)
        eq_(profile.country_id, TEST_COUNTRY_ID)
        eq_(profile.city_id, TEST_CITY_ID)
        eq_(profile.browser_id, TEST_BROWSER_ID)
        eq_(profile.os_id, TEST_OS_ID)
        eq_(profile.yandexuid_timestamp, TEST_YANDEXUID_TIMESTAMP)
        eq_(
            profile.raw_env,
            {
                'ip': TEST_IP,
                'yandexuid': TEST_YANDEXUID,
                'user_agent_info': TEST_UATRAITS_INFO,
            },
        )

    def test_make_profile_unknown_os_version(self):
        env = Environment(
            cookies={'yandexuid': 'hello'},
            consumer_ip='8.8.8.8',
            user_ip='127.0.0.1',
            user_agent=TEST_OTHER_USER_AGENT,
            host='yandex.ru',
            accept_language=None,
            referer=None,
        )
        profile = env.make_profile()
        eq_(profile.os_id, 107)

    def test_make_profile_unknown_user_agent(self):
        env = Environment(
            cookies={'yandexuid': 'hello'},
            consumer_ip='8.8.8.8',
            user_ip='127.0.0.1',
            user_agent=TEST_DUMMY_USER_AGENT,
            host='yandex.ru',
            accept_language=None,
            referer=None,
        )
        profile = env.make_profile()
        eq_(profile.AS_list, [])
        eq_(profile.country_id, None)
        eq_(profile.city_id, None)
        eq_(profile.browser_id, None)
        eq_(profile.os_id, None)
        eq_(profile.yandexuid_timestamp, None)
        eq_(
            profile.raw_env,
            {
                'ip': '127.0.0.1',
                'yandexuid': 'hello',
                'user_agent_info': {},
            },
        )

    def test_make_profile_no_data(self):
        env = Environment(
            cookies={'yandexuid': 'hello'},
            consumer_ip='8.8.8.8',
            user_ip='127.0.0.1',
            user_agent=None,
            host='yandex.ru',
            accept_language=None,
            referer=None,
        )
        profile = env.make_profile()
        eq_(profile.version, TEST_ENVIRONMENT_VERSION)
        eq_(profile.timestamp, TimeNow())
        eq_(profile.AS_list, [])
        assert_is_none(profile.country_id)
        assert_is_none(profile.city_id)
        assert_is_none(profile.browser_id)
        assert_is_none(profile.os_id)
        assert_is_none(profile.yandexuid_timestamp)

    def test_session_id(self):
        env = Environment(
            cookies={'Session_id': '0:sesid'},
        )
        eq_(env.session_id, '0:sesid')

    def test_sslsession_id(self):
        env = Environment(
            cookies={'sessionid2': '0:sslsesid'},
        )
        eq_(env.ssl_session_id, '0:sslsesid')

    def test_request_id(self):
        env = Environment(
            request_id='id1',
        )
        eq_(env.request_id, 'id1')

    def test_user_ip_defined(self):
        env = Environment(user_ip=TEST_IP)
        eq_(env.user_ip, IP(TEST_IP))

    def test_user_ip_not_defined(self):
        env = Environment()
        assert_is_none(env.user_ip, None)

    def test_request_path(self):
        assert Environment().request_path is None

        request_path = '/1/2'
        env = Environment(request_path=request_path)
        assert env.request_path == request_path
