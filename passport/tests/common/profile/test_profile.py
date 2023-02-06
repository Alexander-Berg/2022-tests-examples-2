# -*- coding: utf-8 -*-
import json
import uuid

from flask import request
from nose.tools import ok_
from passport.backend.api.common.profile.profile import process_env_profile
from passport.backend.api.env.env import APIEnvironment
from passport.backend.api.test.mixins import ProfileTestMixin
from passport.backend.api.test.views import (
    BaseTestViews,
    ViewsTestEnvironment,
)
from passport.backend.core.builders.ufo_api.faker import (
    ufo_api_profile_item,
    ufo_api_profile_response,
)
from passport.backend.core.models.account import Account
from passport.backend.core.test.test_utils.utils import (
    settings_context,
    with_settings_hosts,
)
from passport.backend.utils.time import timeuuid_to_timestamp
from werkzeug.datastructures import Headers
import yenv


TEST_YANDEXUID_TEMPLATE = '265232451%s'
TEST_YANDEXUID_TIMESTAMP = '1410531304'
TEST_YANDEXUID = TEST_YANDEXUID_TEMPLATE % TEST_YANDEXUID_TIMESTAMP

DEFAULT_HEADERS = [
    ('X-Real-Ip', '10.2.1.2'),
    ('User-Agent', 'MOZILLA'),
    ('Host', 'www.ya.ru'),
    ('Accept-Language', 'RU'),
    ('Referer', 'http://www.ya.ru'),
    ('Authorization', 'OAuth 123'),
    ('Ya-Consumer-Client-Ip', '172.1.1.1'),
    ('X-Real-Ip', '10.2.1.1'),
    ('Ya-Client-Cookie', 'yandexuid=%s;' % TEST_YANDEXUID),
    ('Ya-Client-User-Agent', 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:40.0) Gecko/20100101 Firefox/40.1'),
    ('Ya-Client-Host', 'www.yandex.ru'),
    ('Ya-Client-Accept-Language', 'EN'),
    ('Ya-Client-Referer', 'http://www.yandex.ru'),
    ('Ya-Consumer-Authorization', 'OAuth 123'),
    ('Ya-Client-X-Request-Id', 'abc'),
]


ENV_PROFILE_RAW_ENV = {
    'ip': '172.1.1.1',
    'yandexuid': TEST_YANDEXUID,
    'user_agent_info': {
        'OSFamily': 'Windows',
        'BrowserEngine': 'Gecko',
        'isBrowser': True,
        'BrowserVersion': '40.1',
        'OSName': 'Windows 7',
        'BrowserName': 'Firefox',
        'BrowserEngineVersion': '40.0',
        'x64': True,
        'OSVersion': '6.1',
        'CSP1Support': True,
        'historySupport': True,
        'localStorageSupport': True,
        'postMessageSupport': True,
        'SVGSupport': True,
    },
}


ENV_PROFILE_FIELDS = {
    'os_id': 33,
    'AS_list': ['AS7018'],
    'city_id': 103418,
    'browser_id': 3,
    'country_id': 84,
    'yandexuid_timestamp': 1410531304,
}


TEST_UFO_TIMEUUID = uuid.UUID('cb78b616-000b-11e5-b8cc-fc7bfc3c8e01')
TEST_ENVIRONMENT_TIMEUUID = uuid.UUID('cb78b616-7f0b-11e5-b8cc-fc7bfc3c8e01')
TEST_ENVIRONMENT_TIMESTAMP = timeuuid_to_timestamp(TEST_ENVIRONMENT_TIMEUUID)


def make_environ(headers, **kwargs):
    def make_env_key(key):
        return 'HTTP_' + key.upper().replace('-', '_')
    return dict(
        [(make_env_key(name), value) for name, value in headers],
        **kwargs
    )


class BaseProfileTestCase(BaseTestViews, ProfileTestMixin):
    def setUp(self):
        self.env = ViewsTestEnvironment()
        self.env.start()

        self.new_uuid1 = uuid.uuid1()
        self.setup_profile_patches()

    def tearDown(self):
        self.teardown_profile_patches()
        self.env.stop()
        del self.env

    def process_env_profile(self, account):
        cookies = {
            'yandexuid': TEST_YANDEXUID,
            'fuid00': 'f',
        }
        headers = dict(
            DEFAULT_HEADERS,
            cookie=';'.join('%s:%s' % (key, value) for (key, value) in cookies.items()),
        )
        params = {
            'environ_overrides': make_environ(DEFAULT_HEADERS, REMOTE_ADDR='10.2.2.2'),
            'headers': Headers(headers),
        }
        with self.env.client.application.test_request_context(**params):
            request.env = APIEnvironment.from_request(request)
            track_manager, track_id = self.env.track_manager.get_manager_and_trackid()
            process_env_profile(account, track=track_manager.read(track_id))


@with_settings_hosts(
    UFO_API_URL='http://localhost/',
    YDB_PERCENTAGE=0,
)
class TestProfile(BaseProfileTestCase):

    def test_process_ufo_profile_create_new(self):
        """Проверяем, что при отсутствии профилей новый будет записан в auth_challenge-лог"""
        self.env.ufo_api.set_response_value(
            'profile',
            json.dumps(
                ufo_api_profile_response(),
            ),
        )
        account = Account().parse({'uid': 1})

        self.process_env_profile(account)

        new_profile = self.make_user_profile(ENV_PROFILE_RAW_ENV)
        self.assert_profile_written_to_auth_challenge_log(new_profile)
        self.assert_ufo_api_called()

    def test_process_ufo_profile_update_existing(self):
        """Проверяем, что при обновлении профилей для определения ближайшего и записи в
        auth_challenge.log будут использоваться данные UfoApi; случай обновления существующего профиля"""
        # Изменяем yandexuid в тестовых данных для того, чтобы расстояние между профилями было ненулевым, но
        # меньшим порога Moderate
        old_yandexuid = TEST_YANDEXUID_TEMPLATE % (int(TEST_YANDEXUID_TIMESTAMP) - 1000)
        ufo_fresh_item = ufo_api_profile_item(
            timeuuid=str(TEST_UFO_TIMEUUID),
            data=dict(ENV_PROFILE_RAW_ENV, yandexuid=old_yandexuid),
        )
        self.env.ufo_api.set_response_value(
            'profile',
            json.dumps(
                ufo_api_profile_response(
                    items=[ufo_fresh_item],
                ),
            ),
        )
        # В аккаунте профилей нет - по логике микропрофилей, мы должны записать новый профиль, в том числе в
        # auth_challenge.log. Убеждаемся, что срабатывает логика ufo-профиля, и в auth_challenge.log
        # обновляется существующий профиль.
        account = Account().parse({'uid': 1})

        self.process_env_profile(account)

        new_profile = self.make_user_profile(ENV_PROFILE_RAW_ENV)
        existing_fresh_profile = self.make_existing_fresh_profile(ufo_fresh_item)
        ok_(new_profile.timeuuid != existing_fresh_profile.timeuuid)
        # Обновление существующего профиля в тесте заключается в изменении yandexuid, timestamp
        existing_fresh_profile.timestamp = new_profile.timestamp
        existing_fresh_profile.yandexuid_timestamp = new_profile.yandexuid_timestamp
        existing_fresh_profile.raw_env['yandexuid'] = TEST_YANDEXUID
        self.assert_profile_written_to_auth_challenge_log(existing_fresh_profile)
        self.assert_ufo_api_called()

    def test_process_ufo_profile_add_new(self):
        """Проверяем, что при обновлении профилей для определения ближайшего и записи в
        auth_challenge.log будут использоваться данные UfoApi; случай записи нового профиля в auth_challenge.log"""
        # Изменяем yandexuid в тестовых данных для того, чтобы расстояние между профилями было большим
        # порога Moderate
        old_yandexuid = TEST_YANDEXUID_TEMPLATE % (int(TEST_YANDEXUID_TIMESTAMP) + 1000)
        ufo_fresh_item = ufo_api_profile_item(
            timeuuid=str(TEST_UFO_TIMEUUID),
            data=dict(ENV_PROFILE_RAW_ENV, yandexuid=old_yandexuid),
        )
        self.env.ufo_api.set_response_value(
            'profile',
            json.dumps(
                ufo_api_profile_response(
                    items=[ufo_fresh_item],
                ),
            ),
        )
        account = Account().parse({'uid': 1})

        self.process_env_profile(account)

        new_profile = self.make_user_profile(ENV_PROFILE_RAW_ENV)
        self.assert_profile_written_to_auth_challenge_log(new_profile)
        self.assert_ufo_api_called()

    def test_process_ufo_profile_with_yenv_written_to_log(self):
        """Проверяем, что при выставленном флаге в auth_challenge.log записано текущее окружение"""
        self.env.ufo_api.set_response_value(
            'profile',
            json.dumps(
                ufo_api_profile_response(),
            ),
        )
        account = Account().parse({'uid': 1})

        with settings_context(
            UFO_API_URL='http://localhost/',
            YDB_PERCENTAGE=0,
            WRITE_YENV_TO_AUTH_CHALLENGE_LOG=True,
        ):
            self.process_env_profile(account)

        new_profile = self.make_user_profile(ENV_PROFILE_RAW_ENV)
        self.assert_profile_written_to_auth_challenge_log(new_profile, comment='env=%s' % yenv.type)
        self.assert_ufo_api_called()

    def test_process_ufo_profile_with_use_rc_flag(self):
        """Проверяем, что при выставленном флаге UFO_API_USE_RC мы передали в UfoApi соответствующий параметр"""
        self.env.ufo_api.set_response_value(
            'profile',
            json.dumps(
                ufo_api_profile_response(),
            ),
        )
        account = Account().parse({'uid': 1})

        with settings_context(
            UFO_API_URL='http://localhost/',
            YDB_PERCENTAGE=0,
            UFO_API_USE_RC=True,
        ):
            self.process_env_profile(account)

        new_profile = self.make_user_profile(ENV_PROFILE_RAW_ENV)
        self.assert_profile_written_to_auth_challenge_log(new_profile)
        self.assert_ufo_api_called(url='http://localhost/1/profile/?uid=1&use_rc=yes')
