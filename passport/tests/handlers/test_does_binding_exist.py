# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from passport.backend.core import Undefined
from passport.backend.core.builders.blackbox.constants import BLACKBOX_OAUTH_INVALID_STATUS
from passport.backend.core.builders.blackbox.faker.blackbox import (
    blackbox_oauth_response,
    blackbox_userinfo_response_multiple,
)
from passport.backend.social.broker.test import TestCase
from passport.backend.social.common.chrono import now
from passport.backend.social.common.db.schemas import profile_table
from passport.backend.social.common.misc import X_TOKEN_SCOPE
from passport.backend.social.common.providers.Vkontakte import Vkontakte
from passport.backend.social.common.providers.Yandex import Yandex
from passport.backend.social.common.test.consts import (
    ACCOUNT_BINDING_OFFER_DELAYS,
    APPLICATION_TOKEN1,
    APPLICATION_TOKEN2,
    CONSUMER1,
    CONSUMER_IP1,
    EXTERNAL_APPLICATION_ID1,
    MAILISH_LOGIN1,
    NEOPHONISH_LOGIN1,
    PHONISH_LOGIN1,
    UID1,
    UID2,
    UID3,
    USER_IP1,
    USERNAME1,
)
from passport.backend.social.proxylib.test import (
    vkontakte as vkontakte_test,
    yandex as yandex_test,
)
from passport.backend.utils.common import deep_merge


PORTAL_UID = UID1
PHONISH_UID = UID2
NEOPHONISH_UID = UID3


class DoesBindingExistByTokenTestCase(TestCase):
    REQUEST_HTTP_METHOD = 'POST'
    REQUEST_URL = '/does_profile_exist_by_token'
    REQUEST_HEADERS = {
        'Ya-Consumer-Authorization': 'Bearer %s' % APPLICATION_TOKEN1,
        'Ya-Consumer-Client-Ip': USER_IP1,
        'X-Real-Ip': CONSUMER_IP1,
    }
    REQUEST_DATA = {
        'consumer': CONSUMER1,
        'token': APPLICATION_TOKEN2,
        'provider': Yandex.code,
        'client_id': EXTERNAL_APPLICATION_ID1,
    }

    def setUp(self):
        super(DoesBindingExistByTokenTestCase, self).setUp()
        self._fake_yandex_proxy = yandex_test.FakeProxy()
        self._fake_yandex_proxy.start()
        self._fake_grants_config.add_consumer(
            CONSUMER1,
            networks=[CONSUMER_IP1],
            grants=['does-binding-exist-by-token'],
        )

    def tearDown(self):
        self._fake_yandex_proxy.stop()
        super(DoesBindingExistByTokenTestCase, self).tearDown()

    def _setup_blackbox(self, master=Undefined, slave=Undefined):
        if master is Undefined:
            master = self._build_portal_account()
        if slave is Undefined:
            slave = self._build_phonish_account()

        if master is None:
            master = self._build_not_existent_account()
        if slave is None:
            slave = self._build_not_existent_account()

        self._fake_blackbox.set_response_side_effect(
            'oauth',
            [
                blackbox_oauth_response(**deep_merge(master['oauth'], master['userinfo'])),
                blackbox_oauth_response(**deep_merge(slave['oauth'], slave['userinfo'])),
            ],
        )
        self._fake_blackbox.set_response_side_effect(
            'userinfo',
            [
                blackbox_userinfo_response_multiple([master['userinfo'], slave['userinfo']]),
            ],
        )

    def _setup_proxy(self, slave=Undefined):
        if slave is Undefined:
            slave = self._build_phonish_account()

        if slave is None:
            slave = self._build_not_existent_account()

        if slave['userinfo']['uid'] is not None:
            get_profile_response = yandex_test.YandexApi.get_profile(
                user=dict(
                    id=str(slave['userinfo']['uid']),
                    display_name=slave['userinfo'].get('display_name', {}).get('name'),
                ),
            )
        else:
            get_profile_response = yandex_test.YandexApi.build_error()
        self._fake_yandex_proxy.set_response_value('get_profile', get_profile_response)

    def _build_portal_account(self, uid=PORTAL_UID, **kwargs):
        return dict(
            userinfo=dict(
                uid=uid,
            ),
            oauth=self._build_oauth_token(**kwargs),
        )

    def _build_neophonish_account(self, uid=NEOPHONISH_UID, **kwargs):
        return dict(
            userinfo=dict(
                uid=uid,
                aliases=dict(neophonish=NEOPHONISH_LOGIN1),
            ),
            oauth=self._build_oauth_token(**kwargs),
        )

    def _build_phonish_account(self, uid=PHONISH_UID, **kwargs):
        return dict(
            userinfo=dict(
                uid=uid,
                aliases=dict(phonish=PHONISH_LOGIN1),
                display_name={'name': USERNAME1},
            ),
            oauth=self._build_oauth_token(**kwargs),
        )

    def _build_mailish_account(self, uid, **kwargs):
        return dict(
            userinfo=dict(
                uid=uid,
                aliases=dict(mailish=MAILISH_LOGIN1),
            ),
            oauth=self._build_oauth_token(**kwargs),
        )

    def _build_not_existent_account(self):
        return dict(
            userinfo=dict(uid=None),
            oauth=dict(status=BLACKBOX_OAUTH_INVALID_STATUS),
        )

    def _build_oauth_token(self, token_valid=True, token_client_id=EXTERNAL_APPLICATION_ID1, **kwargs):
        if not token_valid:
            return dict(status=BLACKBOX_OAUTH_INVALID_STATUS)

        return dict(
            scope=X_TOKEN_SCOPE,
            client_id=token_client_id,
        )

    def _create_binding(self, uid, provider, userid):
        with self._fake_db.no_recording() as db:
            query = profile_table.insert().values(
                uid=uid,
                provider_id=provider.id,
                userid=userid,
                username=USERNAME1,
                created=now(),
            )
            db.execute(query)

    def _assert_does_binding_exist_ok_response(self, rv, response=None,
                                               offer_delays=ACCOUNT_BINDING_OFFER_DELAYS):
        response = dict(
            response,
            offer_delays=offer_delays,
        )
        super(DoesBindingExistByTokenTestCase, self)._assert_ok_response(rv, response)

    def build_settings(self):
        settings = super(DoesBindingExistByTokenTestCase, self).build_settings()
        settings['social_config'].update(
            dict(
                account_binding_offer_delays=ACCOUNT_BINDING_OFFER_DELAYS,
                yandex_get_profile_url='https://login.yandex.ru/info',
                yandex_avatar_url_template='https://avatars.mds.yandex.net/get-yapic/%s/',
            ),
        )
        return settings


class TestDoesBindingExistByTokenTakesConstsFromConfig(DoesBindingExistByTokenTestCase):
    DELAYS = [12345, 123456, 1234567]

    def build_settings(self):
        settings = super(TestDoesBindingExistByTokenTakesConstsFromConfig, self).build_settings()
        settings['social_config'] = dict(
            settings['social_config'],
            account_binding_offer_delays=self.DELAYS,
        )
        return settings

    def setUp(self):
        super(TestDoesBindingExistByTokenTakesConstsFromConfig, self).setUp()
        self._setup_blackbox()
        self._setup_proxy()

    def test(self):
        rv = self._make_request()

        self._assert_does_binding_exist_ok_response(
            rv,
            {
                'is_account_bound': False,
                'is_possible': True,
            },
            offer_delays=self.DELAYS,
        )


class TestDoesBindingExistByTokenBindingExists(DoesBindingExistByTokenTestCase):
    def setUp(self):
        super(TestDoesBindingExistByTokenBindingExists, self).setUp()
        self._create_binding(PORTAL_UID, Yandex, PHONISH_UID)

        phonish = self._build_phonish_account()
        self._setup_blackbox(master=self._build_portal_account(), slave=phonish)
        self._setup_proxy(slave=phonish)

    def test(self):
        rv = self._make_request()

        self._assert_does_binding_exist_ok_response(
            rv,
            {
                'is_account_bound': True,
                'is_possible': True,
            },
        )


class TestDoesBindingExistByTokenBindingNotExist(DoesBindingExistByTokenTestCase):
    def setUp(self):
        super(TestDoesBindingExistByTokenBindingNotExist, self).setUp()

        phonish = self._build_phonish_account()
        self._setup_blackbox(master=self._build_portal_account(), slave=phonish)
        self._setup_proxy(slave=phonish)

    def test(self):
        rv = self._make_request()

        self._assert_does_binding_exist_ok_response(
            rv,
            {
                'is_account_bound': False,
                'is_possible': True,
            },
        )


class TestDoesBindingExistByTokenBindingMasterPhonish(DoesBindingExistByTokenTestCase):
    def setUp(self):
        super(TestDoesBindingExistByTokenBindingMasterPhonish, self).setUp()

        phonish = self._build_phonish_account(uid=UID1)
        self._setup_blackbox(master=self._build_phonish_account(uid=UID2), slave=phonish)
        self._setup_proxy(slave=phonish)

    def test(self):
        rv = self._make_request()

        self._assert_does_binding_exist_ok_response(
            rv,
            {
                'is_account_bound': False,
                'is_possible': False,
            },
        )


class TestDoesBindingExistByTokenBindingSlavePortal(DoesBindingExistByTokenTestCase):
    def setUp(self):
        super(TestDoesBindingExistByTokenBindingSlavePortal, self).setUp()

        portal = self._build_portal_account(uid=UID1)
        self._setup_blackbox(master=self._build_portal_account(uid=UID2), slave=portal)
        self._setup_proxy(slave=portal)

    def test(self):
        rv = self._make_request()

        self._assert_does_binding_exist_ok_response(
            rv,
            {
                'is_account_bound': False,
                'is_possible': False,
            },
        )


class TestDoesBindingExistByTokenClientIdUnknown(DoesBindingExistByTokenTestCase):
    def setUp(self):
        super(TestDoesBindingExistByTokenClientIdUnknown, self).setUp()

        phonish = self._build_phonish_account(token_client_id='unknown')
        self._setup_blackbox(slave=phonish)
        self._setup_proxy(slave=phonish)

    def test(self):
        rv = self._make_request()

        self._assert_does_binding_exist_ok_response(
            rv,
            {
                'is_account_bound': False,
                'is_possible': True,
            },
        )


class TestDoesBindingExistByTokenSingleAccount(DoesBindingExistByTokenTestCase):
    def setUp(self):
        super(TestDoesBindingExistByTokenSingleAccount, self).setUp()

        portal = self._build_portal_account()
        self._setup_blackbox(master=portal, slave=portal)
        self._setup_proxy(slave=portal)

    def test(self):
        rv = self._make_request()

        self._assert_does_binding_exist_ok_response(
            rv,
            {
                'is_account_bound': False,
                'is_possible': False,
            },
        )


class TestDoesBindingExistByTokenMasterNotFound(DoesBindingExistByTokenTestCase):
    def setUp(self):
        super(TestDoesBindingExistByTokenMasterNotFound, self).setUp()
        self._setup_blackbox(master=None)

    def test(self):
        rv = self._make_request()
        self._assert_error_response(rv, ['yandex_token.invalid'])


class TestDoesBindingExistByTokenSlaveNotFound(DoesBindingExistByTokenTestCase):
    def setUp(self):
        super(TestDoesBindingExistByTokenSlaveNotFound, self).setUp()
        self._setup_blackbox(slave=None)
        self._setup_proxy(slave=None)

    def test(self):
        rv = self._make_request()
        self._assert_error_response(rv, ['provider_token.invalid'])


class TestDoesBindingExistByTokenMasterMailish(DoesBindingExistByTokenTestCase):
    def setUp(self):
        super(TestDoesBindingExistByTokenMasterMailish, self).setUp()

        phonish = self._build_phonish_account(uid=UID1)
        self._setup_blackbox(
            master=self._build_mailish_account(uid=UID2),
            slave=phonish,
        )
        self._setup_proxy(slave=phonish)

    def test(self):
        rv = self._make_request()

        self._assert_does_binding_exist_ok_response(
            rv,
            {
                'is_account_bound': False,
                'is_possible': False,
            },
        )


class TestDoesBindingExistByTokenMasterNeophonish(DoesBindingExistByTokenTestCase):
    def setUp(self):
        super(TestDoesBindingExistByTokenMasterNeophonish, self).setUp()

        phonish = self._build_phonish_account(uid=UID1)
        self._setup_blackbox(
            master=self._build_neophonish_account(uid=NEOPHONISH_UID),
            slave=phonish,
        )
        self._setup_proxy(slave=phonish)

    def test(self):
        rv = self._make_request()

        self._assert_does_binding_exist_ok_response(
            rv,
            {
                'is_account_bound': False,
                'is_possible': True,
            },
        )


class TestDoesBindingExistByTokenMasterTokenInvalid(DoesBindingExistByTokenTestCase):
    def setUp(self):
        super(TestDoesBindingExistByTokenMasterTokenInvalid, self).setUp()

        self._setup_blackbox(master=self._build_portal_account(token_valid=False))

    def test(self):
        rv = self._make_request()
        self._assert_error_response(rv, ['yandex_token.invalid'])


class TestDoesBindingExistByTokenSlaveTokenInvalid(DoesBindingExistByTokenTestCase):
    def setUp(self):
        super(TestDoesBindingExistByTokenSlaveTokenInvalid, self).setUp()

        slave = self._build_phonish_account(token_valid=False)
        self._setup_blackbox(slave=slave)
        self._setup_proxy(slave=slave)

    def test(self):
        rv = self._make_request()
        self._assert_error_response(rv, ['provider_token.invalid'])


class TestDoesBindingExistByToken(DoesBindingExistByTokenTestCase):
    def setUp(self):
        super(TestDoesBindingExistByToken, self).setUp()
        self._setup_blackbox()

    def test_no_token(self):
        rv = self._make_request(exclude_data=['token'])
        self._assert_error_response(rv, ['token.empty'])

    def test_no_provider(self):
        rv = self._make_request(exclude_data=['provider'])
        self._assert_error_response(rv, ['provider.empty'])

    def test_no_client_id(self):
        rv = self._make_request(exclude_data=['client_id'])
        self._assert_error_response(rv, ['client_id.empty'])

    def test_no_consumer(self):
        rv = self._make_request(exclude_data=['consumer'])
        self._assert_error_response(rv, ['consumer.empty'])

    def test_no_authorization(self):
        rv = self._make_request(exclude_headers=['Ya-Consumer-Authorization'])
        self._assert_error_response(rv, ['yandex_token.invalid'])

    def test_unknown_authorization(self):
        rv = self._make_request(headers={'Ya-Consumer-Authorization': 'Hack xxx'})
        self._assert_error_response(rv, ['yandex_token.invalid'])

    def test_truncated_authorization(self):
        rv = self._make_request(headers={'Ya-Consumer-Authorization': 'Bearer '})
        self._assert_error_response(rv, ['yandex_token.invalid'])

    def test_no_userip(self):
        rv = self._make_request(exclude_headers=['Ya-Consumer-Client-Ip'])
        self._assert_error_response(rv, ['user_ip.empty'])

    def test_no_consumer_ip(self):
        rv = self._make_request(exclude_headers=['X-Real-Ip'])
        self._assert_error_response(rv, ['consumer_ip.empty'])

    def test_unknown_provider(self):
        rv = self._make_request(data={'provider': 'unknown'})
        self._assert_error_response(rv, ['application.unknown'])


class TestVkDoesBindingExistByTokenRateLimitsErrorTestCase(DoesBindingExistByTokenTestCase):
    REQUEST_DATA = {
        'consumer': CONSUMER1,
        'token': APPLICATION_TOKEN2,
        'provider': Vkontakte.code,
        'client_id': EXTERNAL_APPLICATION_ID1,
    }

    def setUp(self):
        super(TestVkDoesBindingExistByTokenRateLimitsErrorTestCase, self).setUp()
        self._setup_blackbox(master=self._build_portal_account(), slave=None)
        self._fake_vk_proxy = vkontakte_test.FakeProxy()
        self._fake_vk_proxy.start()
        self._fake_vk_proxy.set_response_value(
            'apps.get',
            vkontakte_test.VkontakteApi.build_rate_limit_exceeded_error(),
        )

    def tearDown(self):
        self._fake_vk_proxy.stop()
        super(TestVkDoesBindingExistByTokenRateLimitsErrorTestCase, self).tearDown()

    def test(self):
        rv = self._make_request()
        self._assert_error_response(rv, ['rate_limit.exceeded'])
