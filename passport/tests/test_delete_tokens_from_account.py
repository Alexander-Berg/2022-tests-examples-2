# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from passport.backend.social.common.chrono import now
from passport.backend.social.common.misc import build_dict_from_standard
from passport.backend.social.common.providers.Apple import Apple
from passport.backend.social.common.refresh_token.domain import RefreshToken
from passport.backend.social.common.refresh_token.utils import (
    find_refresh_token_by_token_id,
    save_refresh_token,
)
from passport.backend.social.common.test.consts import (
    APPLICATION_GROUP_NAME1,
    APPLICATION_ID1,
    APPLICATION_ID2,
    APPLICATION_NAME1,
    APPLICATION_NAME2,
    APPLICATION_TOKEN1,
    APPLICATION_TOKEN2,
    EXTERNAL_APPLICATION_ID1,
    EXTERNAL_APPLICATION_ID2,
    UID1,
    UID2,
)
from passport.backend.social.common.token.domain import Token
from passport.backend.social.common.token.utils import (
    find_token_by_token_id,
    save_token,
)
from passport.backend.social.proxylib.test import apple as apple_test

from .common import TestApiViewsCase


APPLICATIONS_CONF = [
    {
        'application_id': APPLICATION_ID1,
        'application_name': APPLICATION_NAME1,
        'provider_client_id': EXTERNAL_APPLICATION_ID1,
        'group_id': APPLICATION_GROUP_NAME1,
    },
    {
        'application_id': APPLICATION_ID2,
        'provider_client_id': EXTERNAL_APPLICATION_ID2,
        'application_name': APPLICATION_NAME2,
    },
]


class BaseDeleteTokensFromAccountTestCase(TestApiViewsCase):
    def setUp(self):
        super(BaseDeleteTokensFromAccountTestCase, self).setUp()
        self.grants_config.add_consumer(
            'dev',
            networks=['127.0.0.1'],
            grants=[
                'token-delete',
                'no-cred-update-token-application:' + APPLICATION_NAME1,
                'no-cred-update-token-application:' + APPLICATION_NAME2,
            ],
        )

    def build_settings(self):
        settings = super(BaseDeleteTokensFromAccountTestCase, self).build_settings()
        settings.update(
            dict(
                applications=APPLICATIONS_CONF,
            ),
        )
        return settings

    def _make_request(self, query_string=None, data=None):
        data = build_dict_from_standard(
            standard=dict(
                uid=UID1,
                application_name=APPLICATION_NAME1,
            ),
            values=data or dict(),
        )
        return self.app_client.post('/api/token/delete_from_account', data=data)

    def _build_token(self,
                     uid=UID1,
                     application_id=APPLICATION_ID1,
                     token_value=APPLICATION_TOKEN1):
        return Token(
            uid=uid,
            application_id=application_id,
            profile_id=None,
            value=token_value,
            secret=None,
            scopes=None,
            expired=None,
            created=now(),
            verified=now(),
            confirmed=now(),
        )

    def _assert_ok_response(self, rv):
        self.assertEqual(rv.status_code, 200)
        self.assertEqual(rv.data, '')

    def _assert_no_token(self, token_id=1):
        token = find_token_by_token_id(token_id, self._fake_db.get_engine())
        self.assertIsNone(token)

    def _assert_token_exists(self, token_id=1):
        token = find_token_by_token_id(token_id, self._fake_db.get_engine())
        self.assertIsNotNone(token)


class TestDeleteTokensFromAccount(BaseDeleteTokensFromAccountTestCase):
    def setUp(self):
        super(TestDeleteTokensFromAccount, self).setUp()
        with self._fake_db.no_recording() as db:
            save_token(self._build_token(), db)

    def test_no_uid(self):
        rv = self._make_request(data=dict(uid=None))

        self._assert_error_response(rv, 'uid-empty', status_code=400)

    def test_no_application_name(self):
        rv = self._make_request(data=dict(application_name=None))

        self._assert_error_response(rv, 'application_name-empty', status_code=400)

    def test_unknown_application(self):
        rv = self._make_request(data=dict(application_name='unknown'))

        self._assert_error_response(rv, 'application-unknown', status_code=400)

    def test_ok(self):
        self._assert_token_exists()

        rv = self._make_request()

        self._assert_ok_response(rv)
        self._assert_no_token()

    def test_no_tokens(self):
        rv = self._make_request(data=dict(application_name=APPLICATION_NAME2))

        self._assert_ok_response(rv)
        self._assert_token_exists()


class TestDeleteTokensFromAccountOtherUid(BaseDeleteTokensFromAccountTestCase):
    def setUp(self):
        super(TestDeleteTokensFromAccountOtherUid, self).setUp()
        with self._fake_db.no_recording() as db:
            save_token(self._build_token(uid=UID1), db)
            save_token(self._build_token(uid=UID2), db)

    def test_ok(self):
        rv = self._make_request(data=dict(uid=UID2))

        self._assert_ok_response(rv)
        self._assert_token_exists(token_id=1)
        self._assert_no_token(token_id=2)


class TestDeleteTokensFromAccountOtherApplication(BaseDeleteTokensFromAccountTestCase):
    def setUp(self):
        super(TestDeleteTokensFromAccountOtherApplication, self).setUp()
        with self._fake_db.no_recording() as db:
            save_token(self._build_token(application_id=APPLICATION_ID1), db)
            save_token(self._build_token(application_id=APPLICATION_ID2), db)

    def test_ok(self):
        rv = self._make_request(data=dict(application_name=APPLICATION_NAME2))

        self._assert_ok_response(rv)
        self._assert_token_exists(token_id=1)
        self._assert_no_token(token_id=2)


class TestDeleteTokensFromAccountGrants(BaseDeleteTokensFromAccountTestCase):
    need_fake_grants_config = True

    def setUp(self):
        super(TestDeleteTokensFromAccountGrants, self).setUp()

    def _assert_access_denied(self, rv):
        self._assert_error_response(rv, 'access-denied', status_code=403)

    def _assign_grants(self, grants):
        self.grants_config.add_consumer('dev', networks=['127.0.0.1'], grants=grants)

    def test_no_grants(self):
        self._assign_grants([])
        rv = self._make_request()
        self._assert_access_denied(rv)

    def test_token_delete(self):
        self._assign_grants(['token-delete'])
        rv = self._make_request()
        self._assert_access_denied(rv)

    def test_token_delete_app(self):
        self._assign_grants(['token-delete', 'no-cred-update-token-application:' + APPLICATION_NAME1])
        rv = self._make_request(data=dict(application_name=APPLICATION_NAME1))
        self._assert_ok_response(rv)

    def test_token_delete_app__other_app(self):
        self._assign_grants(['token-delete', 'no-cred-update-token-application:' + APPLICATION_NAME1])
        rv = self._make_request(data=dict(application_name=APPLICATION_NAME2))
        self._assert_access_denied(rv)

    def test_token_delete_app_group(self):
        self._assign_grants(['token-delete', 'no-cred-update-token-application-group:' + APPLICATION_GROUP_NAME1])
        rv = self._make_request(data=dict(application_name=APPLICATION_NAME1))
        self._assert_ok_response(rv)

    def test_token_delete_app_group__other_app(self):
        self._assign_grants(['token-delete', 'no-cred-update-token-application-group:' + APPLICATION_GROUP_NAME1])
        rv = self._make_request(data=dict(application_name=APPLICATION_NAME2))
        self._assert_access_denied(rv)


class TestDeleteTokensFromAccountRefreshToken(BaseDeleteTokensFromAccountTestCase):
    def setUp(self):
        super(TestDeleteTokensFromAccountRefreshToken, self).setUp()
        with self._fake_db.no_recording() as db:
            save_token(self._build_token(), db)
            save_refresh_token(
                RefreshToken(
                    token_id=1,
                    value=APPLICATION_TOKEN2,
                    expired=None,
                    scopes=None,
                ),
                db,
            )

    def _assert_no_refresh_token(self):
        refresh_token = find_refresh_token_by_token_id(token_id=1, db=self._fake_db.get_engine())
        self.assertIsNone(refresh_token)

    def test_ok(self):
        rv = self._make_request()

        self._assert_ok_response(rv)
        self._assert_no_token()
        self._assert_no_refresh_token()


class TestDeleteTokensFromAccountManyTokens(BaseDeleteTokensFromAccountTestCase):
    def setUp(self):
        super(TestDeleteTokensFromAccountManyTokens, self).setUp()
        with self._fake_db.no_recording() as db:
            save_token(self._build_token(token_value=APPLICATION_TOKEN1), db)
            save_token(self._build_token(token_value=APPLICATION_TOKEN2), db)

    def test_ok(self):
        self._assert_token_exists(token_id=1)
        self._assert_token_exists(token_id=2)

        rv = self._make_request()

        self._assert_ok_response(rv)
        self._assert_no_token(token_id=1)
        self._assert_no_token(token_id=2)


class TestDeleteTokensApple(BaseDeleteTokensFromAccountTestCase):
    def setUp(self):
        super(TestDeleteTokensApple, self).setUp()

        self.fake_proxy = apple_test.FakeProxy().start()

        with self._fake_db.no_recording() as db:
            save_token(self._build_token(application_id=APPLICATION_ID1), db)
            save_token(
                self._build_token(
                    application_id=APPLICATION_ID2,
                    token_value=APPLICATION_TOKEN2,
                ),
                db,
            )

    def tearDown(self):
        self.fake_proxy.stop()
        super(TestDeleteTokensApple, self).tearDown()

    def build_settings(self):
        settings = super(TestDeleteTokensApple, self).build_settings()

        settings['social_config'].update(
            apple_jwt_certificate_id=apple_test.APPLE_JSON_WEB_KEY1['kid'],
            apple_team_id=apple_test.APPLE_TEAM_ID1,
        )
        settings['social_config'].update({
            'apple_jwt_certificate_' + apple_test.APPLE_JSON_WEB_KEY1['kid']: apple_test.APPLE_PRIVATE_KEY1,
        })

        settings.update(
            dict(
                providers=[
                    {
                        'id': Apple.id,
                        'code': Apple.code,
                        'name': 'apple',
                        'timeout': 1,
                        'retries': 1,
                        'display_name': {
                            'default': 'Apple',
                        },
                    },
                ],
                applications=[
                    {
                        'application_id': APPLICATION_ID1,
                        'application_name': APPLICATION_NAME1,
                        'provider_client_id': EXTERNAL_APPLICATION_ID1,
                        'provider_id': Apple.id,
                    },
                    {
                        'application_id': APPLICATION_ID2,
                        'provider_client_id': EXTERNAL_APPLICATION_ID2,
                        'provider_id': Apple.id,
                        'application_name': APPLICATION_NAME2,
                    },
                ],
            ),
        )
        return settings

    def test_by_provider(self):
        self._assert_token_exists(token_id=1)
        self._assert_token_exists(token_id=2)

        rv = self._make_request(data=dict(provider_name='apl', application_name=None))

        self._assert_ok_response(rv)
        self._assert_no_token(token_id=1)
        self._assert_no_token(token_id=2)

    def test_revoke(self):
        self.fake_proxy.set_response_value(
            'revoke_token',
            apple_test.AppleApi.revoke_token(),
        )

        rv = self._make_request(data=dict(revoke='1'))

        self._assert_ok_response(rv)

        assert len(self.fake_proxy.requests) == 1
        assert self.fake_proxy.requests[0]['url'] == 'https://appleid.apple.com/auth/revoke'
        assert self.fake_proxy.requests[0]['data']['token'] == APPLICATION_TOKEN1
