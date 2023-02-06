# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from datetime import timedelta

from passport.backend.core import Undefined
from passport.backend.core.builders.blackbox.constants import BLACKBOX_OAUTH_INVALID_STATUS
from passport.backend.core.builders.blackbox.faker.blackbox import (
    blackbox_oauth_response,
    blackbox_userinfo_response_multiple,
)
from passport.backend.core.builders.passport.faker import passport_ok_response
from passport.backend.core.test.time_utils.time_utils import TimeNow
from passport.backend.social.broker.test import InternalBrokerHandlerV1TestCase
from passport.backend.social.common.chrono import now
from passport.backend.social.common.db.schemas import (
    person_table,
    profile_table,
)
from passport.backend.social.common.misc import X_TOKEN_SCOPE
from passport.backend.social.common.providers.Google import Google
from passport.backend.social.common.providers.Vkontakte import Vkontakte
from passport.backend.social.common.providers.Yandex import Yandex
from passport.backend.social.common.refresh_token.utils import find_refresh_token_by_token_id
from passport.backend.social.common.test.consts import (
    APPLICATION_TOKEN1,
    APPLICATION_TOKEN_TTL1,
    CONSUMER1,
    CONSUMER2,
    CONSUMER_IP2,
    EXTERNAL_APPLICATION_ID1,
    FRONTEND_URL1,
    GOOGLE_APPLICATION_ID1,
    PHONISH_LOGIN1,
    REFRESH_TOKEN1,
    RETPATH1,
    SIMPLE_USERID1,
    TASK_ID1,
    UID1,
    UID2,
    USER_IP1,
    USERNAME1,
    YANDEX_TOKEN1,
    YANDEX_TOKEN2,
)
from passport.backend.social.common.test.fake_passport import FakePassport
from passport.backend.social.common.test.types import DatetimeNow
from passport.backend.social.common.token.utils import find_token_by_value_for_account
from passport.backend.social.proxylib.test import (
    google as google_test,
    vkontakte as vkontakte_test,
    yandex as yandex_test,
)
from passport.backend.utils.common import deep_merge
from sqlalchemy import (
    and_ as sql_and,
    select as sql_select,
)


class BaseBindByTokenTestCase(InternalBrokerHandlerV1TestCase):
    REQUEST_HTTP_METHOD = 'POST'
    REQUEST_URL = '/bind_by_token'
    REQUEST_HEADERS = {
        'X-Real-Ip': CONSUMER_IP2,
        'Ya-Consumerid': CONSUMER2,
    }

    def setUp(self):
        super(BaseBindByTokenTestCase, self).setUp()
        self._fake_generate_task_id.set_retval(TASK_ID1)
        self._fake_grants_config.add_consumer(CONSUMER2, [CONSUMER_IP2], ['bind-by-token'])
        self._fake_passport = FakePassport()
        self._fake_passport.set_response_value(
            'send_account_modification_notifications',
            passport_ok_response(),
        )
        self._fake_passport.start()

    def tearDown(self):
        self._fake_passport.stop()
        super(BaseBindByTokenTestCase, self).tearDown()

    def build_settings(self):
        settings = super(BaseBindByTokenTestCase, self).build_settings()
        settings['social_config'].update(
            dict(
                passport_api_consumer='socialism',
                passport_api_retries=1,
                passport_api_timeout=1,
                passport_api_url='https://passport-internal.yandex.ru',
            ),
        )
        return settings

    def _assert_bind_by_token_ok_response(self, rv, retpath=RETPATH1):
        self._assert_ok_response(rv, skip=['cookies', 'location'])
        self._assert_response_burns_session(rv)
        self._assert_response_forwards_to_url(
            rv,
            self._build_ok_retpath(url=retpath, task_id=TASK_ID1),
        )

    def _assert_bind_by_token_error_response(self, rv, error, provider=Yandex, retpath=RETPATH1):
        if provider is Yandex:
            provider = {
                'id': Yandex.id,
                'code': Yandex.code,
                'name': 'yandex',
            }
        elif provider is Vkontakte:
            provider = {
                'id': Vkontakte.id,
                'code': Vkontakte.code,
                'name': 'vkontakte',
            }
        else:
            raise NotImplementedError()  # pragma: no cover

        self._assert_error_response(
            rv,
            [error],
            retpath,
            {
                'provider': provider,
            },
        )

    def _build_portal_yandex_account(self, uid=UID1):
        return dict(
            userinfo=dict(uid=uid),
            oauth=dict(
                scope=X_TOKEN_SCOPE,
                client_id=EXTERNAL_APPLICATION_ID1,
            ),
        )

    def _build_phonish_yandex_account(self, uid):
        return dict(
            userinfo=dict(
                uid=uid,
                aliases=dict(phonish=PHONISH_LOGIN1),
                display_name={'name': USERNAME1},
            ),
            oauth=dict(
                scope=X_TOKEN_SCOPE,
                client_id=EXTERNAL_APPLICATION_ID1,
            ),
        )

    def _build_not_existent_account(self):
        return dict(
            userinfo=dict(uid=None),
            oauth=dict(status=BLACKBOX_OAUTH_INVALID_STATUS),
        )

    def _assert_binding_exists(self, uid, provider, userid, username):
        bindings = self._find_bindings(uid, provider, userid)
        self.assertEqual(len(bindings), 1)
        binding = bindings[0]

        self.assertEqual(binding.allow_auth, 0)
        self.assertEqual(binding.username, username)
        self.assertEqual(binding.created, DatetimeNow())
        self.assertEqual(binding.verified, DatetimeNow())
        self.assertEqual(binding.confirmed, DatetimeNow())
        self.assertEqual(binding.yandexuid, '')

    def _find_bindings(self, uid, provider, userid):
        with self._fake_db.no_recording() as db:
            query = (
                sql_select([profile_table])
                .where(
                    sql_and(
                        profile_table.c.uid == uid,
                        profile_table.c.provider_id == provider.id,
                        profile_table.c.userid == userid,
                    ),
                )
            )
            return db.execute(query).fetchall()

    def _assert_token_exists(self, uid, app_id, token, refresh_token):
        with self._fake_db.no_recording() as db:
            token = find_token_by_value_for_account(uid, app_id, token, db)
        self.assertIsNotNone(token)
        self.assertIsNone(token.secret)
        self.assertEqual(
            token.scopes,
            {
                'https://www.googleapis.com/auth/userinfo.profile',
                'https://www.googleapis.com/auth/userinfo.email',
            },
        )
        self.assertEqual(token.created, DatetimeNow())
        self.assertEqual(token.verified, DatetimeNow())
        self.assertEqual(token.confirmed, DatetimeNow())
        self.assertEqual(
            token.expired,
            DatetimeNow(timestamp=now() + timedelta(seconds=APPLICATION_TOKEN_TTL1)),
        )

        with self._fake_db.no_recording() as db:
            refresh_token = find_refresh_token_by_token_id(token.token_id, db)
        self.assertIsNotNone(refresh_token)
        self.assertEqual(refresh_token.value, REFRESH_TOKEN1)
        self.assertIsNone(refresh_token.expired)

    def _assert_person_exists(self):
        persons = self._find_persons()
        self.assertEqual(len(persons), 1)
        person = persons[0]

        self.assertEqual(person.firstname, 'Andrey')
        self.assertEqual(person.lastname, 'Isaev')
        self.assertEqual(person.email, 'ololo@gmail.com')
        self.assertEqual(person.gender, 'm')

    def _assert_notification_sent(self, hostname, user_ip, uid, event_name):
        requests = self._fake_passport.get_requests_by_method('send_account_modification_notifications')
        assert len(requests) == 1
        request = requests[0]
        request.assert_post_data_equals(dict(
            event_name=event_name,
            mail_enabled='1',
            push_enabled='1',
            social_provider='vkontakte',
            uid=uid,
        ))
        request.assert_headers_contain({
            'Ya-Client-Host': hostname,
            'Ya-Consumer-Client-Ip': user_ip,
        })

    def _find_persons(self):
        with self._fake_db.no_recording() as db:
            query = (
                sql_select([person_table])
                .where(person_table.c.profile_id == 1)
            )
            return db.execute(query).fetchall()


class TestBindByTokenFromExternalProvider(BaseBindByTokenTestCase):
    REQUEST_QUERY = {
        'consumer': CONSUMER1,
        'retpath': RETPATH1,
        'provider': Vkontakte.code,
    }
    REQUEST_DATA = {
        'frontend_url': FRONTEND_URL1,
        'user_ip': USER_IP1,
        'token': YANDEX_TOKEN1,
        'provider_token': APPLICATION_TOKEN1,
    }

    def setUp(self):
        super(TestBindByTokenFromExternalProvider, self).setUp()
        self._fake_vkontakte_proxy = vkontakte_test.FakeProxy().start()

    def tearDown(self):
        self._fake_vkontakte_proxy.stop()
        super(TestBindByTokenFromExternalProvider, self).tearDown()

    def build_settings(self):
        settings = super(TestBindByTokenFromExternalProvider, self).build_settings()
        return settings

    def _setup_blackbox(self, master, slave=Undefined):
        self._fake_blackbox.set_response_side_effect(
            'oauth',
            [
                blackbox_oauth_response(**deep_merge(master['userinfo'], master['oauth'])),
            ],
        )

    def _setup_vkontakte_proxy(self, userid, username):
        self._fake_vkontakte_proxy.set_response_value(
            'apps.get',
            vkontakte_test.VkontakteApi.apps_get([dict()]),
        )
        self._fake_vkontakte_proxy.set_response_value(
            'account.getAppPermissions',
            vkontakte_test.VkontakteApi.account_get_app_permissions(0),
        )
        self._fake_vkontakte_proxy.set_response_value(
            'users.get',
            vkontakte_test.VkontakteApi.users_get({
                'id': userid,
                'domain': username,
            }),
        )

    def _assert_avatar_logged(self, uid, avatar_url):
        self._fake_avatars_logger.assert_has_written([
            self._fake_avatars_logger.entry(
                'base',
                uid=str(uid),
                avatar_to_upload=avatar_url,
                mode='upload_by_url',
                unixtime=TimeNow(),
                user_ip='127.0.0.1',
                skip_if_set='1',
            ),
        ])

    def test_ok(self):
        self._setup_blackbox(self._build_portal_yandex_account(uid=UID1))
        self._setup_vkontakte_proxy(userid=SIMPLE_USERID1, username=USERNAME1)

        rv = self._make_request()

        self._assert_bind_by_token_ok_response(rv)
        self._assert_binding_exists(
            UID1,
            Vkontakte,
            SIMPLE_USERID1,
            username=USERNAME1,
        )
        self._assert_avatar_logged(
            uid=UID1,
            avatar_url=vkontakte_test.USER_AVATAR1,
        )
        self._assert_notification_sent(
            hostname='social.yandex.ru',
            user_ip=USER_IP1,
            uid=UID1,
            event_name='social_add',
        )


class TestBindByTokenFromExternalProviderWithRefreshToken(BaseBindByTokenTestCase):
    REQUEST_QUERY = {
        'consumer': CONSUMER1,
        'retpath': RETPATH1,
        'provider': Google.code,
    }
    REQUEST_DATA = {
        'frontend_url': FRONTEND_URL1,
        'user_ip': USER_IP1,
        'token': YANDEX_TOKEN1,
        'provider_token': APPLICATION_TOKEN1,
    }

    def setUp(self):
        super(TestBindByTokenFromExternalProviderWithRefreshToken, self).setUp()
        self._fake_google_proxy = google_test.FakeProxy().start()

    def tearDown(self):
        self._fake_google_proxy.stop()
        super(TestBindByTokenFromExternalProviderWithRefreshToken, self).tearDown()

    def _setup_blackbox(self, master, slave=Undefined):
        self._fake_blackbox.set_response_side_effect(
            'oauth',
            [
                blackbox_oauth_response(**deep_merge(master['userinfo'], master['oauth'])),
            ],
        )

    def _setup_google_proxy(self, userid):
        self._fake_google_proxy.set_response_value(
            'exchange_authorization_code_to_token',
            google_test.GoogleApi.exchange_auth_code_to_token(
                access_token=APPLICATION_TOKEN1,
                refresh_token=REFRESH_TOKEN1,
            ),
        )
        self._fake_google_proxy.set_response_value(
            'get_token_info',
            google_test.GoogleApi.get_token_info(
                {
                    'expires_in': str(APPLICATION_TOKEN_TTL1),
                },
            ),
        )
        self._fake_google_proxy.set_response_value(
            'get_profile',
            google_test.GoogleApi.get_profile(
                dict(
                    sub=userid,
                    email='ololo@gmail.com',
                    email_verified='true',
                    given_name='Andrey',
                    family_name='Isaev',
                    gender='male',
                ),
            ),
        )

    def test(self):
        self._setup_blackbox(self._build_portal_yandex_account(uid=UID1))
        self._setup_google_proxy(userid=SIMPLE_USERID1)

        rv = self._make_request()

        self._assert_bind_by_token_ok_response(rv)
        self._assert_binding_exists(
            UID1,
            Google,
            SIMPLE_USERID1,
            username='ololo',
        )
        self._assert_token_exists(
            UID1,
            GOOGLE_APPLICATION_ID1,
            APPLICATION_TOKEN1,
            REFRESH_TOKEN1,
        )
        self._assert_person_exists()


class TestBindByTokenMordaRetpath(BaseBindByTokenTestCase):
    REQUEST_QUERY = {
        'consumer': CONSUMER1,
        'provider': Vkontakte.code,
    }
    REQUEST_DATA = {
        'frontend_url': FRONTEND_URL1,
        'user_ip': USER_IP1,
        'token': YANDEX_TOKEN1,
        'provider_token': APPLICATION_TOKEN1,
    }

    def setUp(self):
        super(TestBindByTokenMordaRetpath, self).setUp()
        self._fake_vkontakte_proxy = vkontakte_test.FakeProxy().start()

    def tearDown(self):
        self._fake_vkontakte_proxy.stop()
        super(TestBindByTokenMordaRetpath, self).tearDown()

    def build_settings(self):
        settings = super(TestBindByTokenMordaRetpath, self).build_settings()
        settings['social_config'].update(
            dict(
                broker_retpath_grammars=[
                    """
                    domain = 'yandex.' yandex_tld | 'www.yandex.' yandex_tld
                    """,
                ],
            ),
        )
        return settings

    def _setup_blackbox(self, master, slave=Undefined):
        self._fake_blackbox.set_response_side_effect(
            'oauth',
            [
                blackbox_oauth_response(**deep_merge(master['userinfo'], master['oauth'])),
            ],
        )

    def _setup_vkontakte_proxy(self, userid, username):
        self._fake_vkontakte_proxy.set_response_value(
            'apps.get',
            vkontakte_test.VkontakteApi.apps_get([dict()]),
        )
        self._fake_vkontakte_proxy.set_response_value(
            'account.getAppPermissions',
            vkontakte_test.VkontakteApi.account_get_app_permissions(0),
        )
        self._fake_vkontakte_proxy.set_response_value(
            'users.get',
            vkontakte_test.VkontakteApi.users_get({
                'id': userid,
                'domain': username,
            }),
        )

    def test_yandex_ru(self):
        self._setup_blackbox(self._build_portal_yandex_account(uid=UID1))
        self._setup_vkontakte_proxy(userid=SIMPLE_USERID1, username=USERNAME1)

        rv = self._make_request(query=dict(retpath='https://yandex.ru/'))

        self._assert_bind_by_token_ok_response(rv, retpath='https://yandex.ru/')

    def test_yandex_com(self):
        self._setup_blackbox(self._build_portal_yandex_account(uid=UID1))
        self._setup_vkontakte_proxy(userid=SIMPLE_USERID1, username=USERNAME1)

        rv = self._make_request(query=dict(retpath='https://yandex.com/?foo=1'))

        self._assert_bind_by_token_ok_response(rv, retpath='https://yandex.com/?foo=1&redirect=0')

    def test_yandex_com__fail(self):
        self._setup_blackbox(self._build_not_existent_account())
        self._setup_vkontakte_proxy(userid=SIMPLE_USERID1, username=USERNAME1)

        rv = self._make_request(query=dict(retpath='https://yandex.com/'))

        self._assert_bind_by_token_error_response(
            rv,
            'AuthorizationRequiredError',
            retpath='https://yandex.com/?redirect=0',
            provider=Vkontakte,
        )


class BaseBindByTokenFromYandexTestCase(BaseBindByTokenTestCase):
    REQUEST_QUERY = {
        'consumer': CONSUMER1,
        'retpath': RETPATH1,
        'provider': Yandex.code,
    }
    REQUEST_DATA = {
        'frontend_url': FRONTEND_URL1,
        'user_ip': USER_IP1,
        'token': YANDEX_TOKEN1,
        'provider_token': YANDEX_TOKEN2,
    }

    def setUp(self):
        super(BaseBindByTokenFromYandexTestCase, self).setUp()
        self._fake_yandex_proxy = yandex_test.FakeProxy().start()

    def tearDown(self):
        self._fake_yandex_proxy.stop()
        super(BaseBindByTokenFromYandexTestCase, self).tearDown()

    def build_settings(self):
        settings = super(BaseBindByTokenFromYandexTestCase, self).build_settings()
        settings['social_config'].update(
            dict(
                yandex_get_profile_url='https://login.yandex.ru/info',
                yandex_avatar_url_template='https://avatars.mds.yandex.net/get-yapic/%s/',
            ),
        )
        return settings

    def _setup_blackbox(self, master, slave):
        self._fake_blackbox.set_response_side_effect(
            'oauth',
            [
                blackbox_oauth_response(**deep_merge(master['userinfo'], master['oauth'])),
                blackbox_oauth_response(**deep_merge(slave['userinfo'], slave['oauth'])),
            ],
        )
        self._setup_blackbox_batch_response_about_master_and_slave(master, slave)

    def _setup_blackbox_batch_response_about_master_and_slave(self, master, slave):
        if master is None:
            master = self._build_not_existent_account()

        self._fake_blackbox.set_response_side_effect(
            'userinfo',
            [
                blackbox_userinfo_response_multiple([master['userinfo'], slave['userinfo']]),
            ],
        )

    def _setup_proxy(self, slave=Undefined):
        self._fake_yandex_proxy.set_response_value(
            'get_profile',
            yandex_test.YandexApi.get_profile(),
        )


class TestBindByTokenFromYandexSingleAccount(BaseBindByTokenFromYandexTestCase):
    def setUp(self):
        super(TestBindByTokenFromYandexSingleAccount, self).setUp()

        portal = self._build_portal_yandex_account()
        self._setup_blackbox(master=portal, slave=portal)
        self._setup_proxy(portal)

    def test_single_account(self):
        rv = self._make_request()
        self._assert_bind_by_token_error_response(rv, 'ProfileNotAllowedError')


class TestBindByTokenFromYandexRaceAccountNotFound(BaseBindByTokenFromYandexTestCase):
    def setUp(self):
        super(TestBindByTokenFromYandexRaceAccountNotFound, self).setUp()

        portal = self._build_portal_yandex_account(uid=UID1)
        self._setup_blackbox(master=portal, slave=self._build_phonish_yandex_account(uid=UID2))
        self._setup_proxy(portal)

    def _setup_blackbox_batch_response_about_master_and_slave(self, master, slave):
        super(TestBindByTokenFromYandexRaceAccountNotFound, self)._setup_blackbox_batch_response_about_master_and_slave(None, slave)

    def test(self):
        rv = self._make_request()
        self._assert_bind_by_token_error_response(rv, 'SessionInvalidError')
