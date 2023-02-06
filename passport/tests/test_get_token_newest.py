# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from datetime import (
    datetime,
    timedelta,
)
import json

from passport.backend.core import Undefined
from passport.backend.core.builders.blackbox.constants import (
    BLACKBOX_OAUTH_INVALID_STATUS,
    BLACKBOX_OAUTH_VALID_STATUS,
)
from passport.backend.core.builders.blackbox.faker.blackbox import (
    blackbox_oauth_response,
    FakeBlackbox,
)
from passport.backend.social.api.test import ApiV2TestCase
from passport.backend.social.common.builders.blackbox import BlackboxTemporaryError
from passport.backend.social.common.chrono import (
    datetime_to_unixtime,
    now,
)
from passport.backend.social.common.exception import (
    DatabaseError,
    NetworkProxylibError,
)
from passport.backend.social.common.misc import X_TOKEN_SCOPE
from passport.backend.social.common.profile import create_profile
from passport.backend.social.common.refresh_token.domain import RefreshToken
from passport.backend.social.common.refresh_token.utils import save_refresh_token
from passport.backend.social.common.test.consts import (
    APPLICATION_ID1,
    APPLICATION_NAME1,
    APPLICATION_SECRET1,
    APPLICATION_TOKEN1,
    APPLICATION_TOKEN2,
    APPLICATION_TOKEN3,
    APPLICATION_TOKEN4,
    APPLICATION_TOKEN5,
    APPLICATION_TOKEN6,
    APPLICATION_TOKEN7,
    APPLICATION_TOKEN8,
    APPLICATION_TOKEN_TTL1,
    EXTERNAL_APPLICATION_ID1,
    PROFILE_ID1,
    PROFILE_ID2,
    SIMPLE_USERID1,
    SIMPLE_USERID2,
    UID1,
    UNIXTIME1,
    USER_IP1,
    YANDEX_TOKEN1,
    YANDEXUID1,
)
from passport.backend.social.common.test.types import (
    ApproximateInteger,
    DatetimeNow,
    FakeResponse,
)
from passport.backend.social.common.token.domain import Token
from passport.backend.social.common.token.utils import save_token
from passport.backend.social.proxylib.test import google as google_test


APPLICATIONS_CONF = [
    dict(
        provider_id=5,
        application_id=52,
        application_name='google-oauth2',
        default='1',
        provider_client_id='xxx',
        secret='xxx',
    ),
    dict(
        provider_id=5,
        application_id=53,
        application_name='google-oauth2-en',
        provider_client_id='yyy',
        secret='yyy',
    ),
]


class GetTokenNewestTestCase(ApiV2TestCase):
    BUILD_DEFAULT_GRANTS = True

    def setUp(self):
        super(GetTokenNewestTestCase, self).setUp()

        if self.BUILD_DEFAULT_GRANTS:
            self.build_grants()

    def build_grants(
        self,
        consumer='dev',
        networks=['127.0.0.1'],
        grants=[
            'token-read',
            'no-cred-read-token-application:google-oauth2',
            'no-cred-read-token-application:' + APPLICATION_NAME1,
        ],
    ):
        self._fake_grants_config.add_consumer(consumer, networks=networks, grants=grants)

    def build_settings(self):
        settings = super(GetTokenNewestTestCase, self).build_settings()
        settings.update(
            dict(
                applications=APPLICATIONS_CONF,
            ),
        )
        return settings


class TestGetTokenNewest(GetTokenNewestTestCase):
    def setUp(self):
        super(TestGetTokenNewest, self).setUp()

        with self._fake_db.no_recording():
            db = self._fake_db.get_engine()
            save_token(self._create_token(APPLICATION_TOKEN1), db)
            save_token(self._create_token(APPLICATION_TOKEN2, created=datetime.fromtimestamp(UNIXTIME1 + 1)), db)
            save_token(self._create_token(APPLICATION_TOKEN3, scopes=['foo', 'bar']), db)
            # Следующие токены заведомо новее остальных, однако не подходят
            # из-за того что либо истёк срок жизники, либо не тот профиль, либо
            # не то приложение.
            save_token(self._create_token(APPLICATION_TOKEN4, created=datetime.fromtimestamp(UNIXTIME1 + 2), expired=datetime.fromtimestamp(UNIXTIME1)), db)
            save_token(self._create_token(APPLICATION_TOKEN5, created=datetime.fromtimestamp(UNIXTIME1 + 2), profile_id=PROFILE_ID2), db)
            save_token(self._create_token(APPLICATION_TOKEN6, created=datetime.fromtimestamp(UNIXTIME1 + 2), application_id=53), db)

            profile_info1 = {'provider': {'code': 'gg'}, 'userid': SIMPLE_USERID1}
            token7 = self._create_token(APPLICATION_TOKEN7, expired=datetime.fromtimestamp(UNIXTIME1), profile_id=None, created=None)
            profile_info2 = {'provider': {'code': 'gg'}, 'userid': SIMPLE_USERID2}
            token8 = self._create_token(APPLICATION_TOKEN8, scopes=['foo'], created=None, profile_id=None, expired=None)
            for profile_info, token, timestamp in [
                (profile_info1, token7, UNIXTIME1),
                (profile_info2, token8, UNIXTIME1 + 3),
            ]:
                create_profile(
                    mysql_read=db,
                    mysql_write=db,
                    uid=UID1,
                    profile_info=profile_info,
                    token=token,
                    timestamp=timestamp,
                    yandexuid=YANDEXUID1,
                )

    def _create_token(self, token_value, created=datetime.fromtimestamp(UNIXTIME1), scopes=None,
                      expired=Undefined, profile_id=PROFILE_ID1,
                      application_id=52):
        if scopes is None:
            scopes = ['foo']
        if expired is Undefined:
            expired = now() + timedelta(hours=1)
        return Token(
            uid=UID1,
            profile_id=profile_id,
            application_id=application_id,
            value=token_value,
            secret=None,
            scopes=scopes,
            expired=expired,
            created=created,
            verified=datetime.fromtimestamp(UNIXTIME1),
            confirmed=datetime.fromtimestamp(UNIXTIME1),
        )

    def _build_token(self,
                     token_id=2,
                     application_token=APPLICATION_TOKEN2,
                     scope='foo',
                     created=UNIXTIME1+1,
                     profile_id=PROFILE_ID1,
                     expired_in=timedelta(hours=1),
                     confirmed=UNIXTIME1,
                     verified=UNIXTIME1):

        if expired_in is not None:
            expired = DatetimeNow(convert_to_datetime=True) + expired_in
            expired_ts = ApproximateInteger(datetime_to_unixtime(now() + expired_in))
        else:
            expired = None
            expired_ts = None

        return {
            'token_id': token_id,
            'uid': UID1,
            'profile_id': profile_id,
            'application': 'google-oauth2',
            'value': application_token,
            'secret': None,
            'scope': scope,
            'expired': expired,
            'expired_ts': expired_ts,
            'created': str(datetime.fromtimestamp(created)),
            'created_ts': created,
            'confirmed': str(datetime.fromtimestamp(confirmed)),
            'confirmed_ts': confirmed,
            'verified': str(datetime.fromtimestamp(verified)),
            'verified_ts': verified,
        }

    def test_no_profile_id(self):
        rv = self._client.get(
            '/api/token/newest',
            query_string={'application_name': 'google-oauth2'},
        )
        self._assert_error_response(rv, 'profile_id-empty', status_code=400)

    def test_no_application_id(self):
        rv = self._client.get('/api/token/newest', query_string={'profile_id': PROFILE_ID1})
        self._assert_error_response(rv, 'application_id-empty', status_code=400)

    def test_unknown_application_name(self):
        rv = self._client.get(
            '/api/token/newest',
            query_string={
                'profile_id': PROFILE_ID1,
                'application_id': 'unknown',
            },
        )
        self._assert_error_response(rv, 'application-unknown', status_code=400)

    def test_newest_by_profile_id_and_application_id(self):
        rv = self._client.get(
            '/api/token/newest',
            query_string={'profile_id': PROFILE_ID1, 'application_id': '52'},
        )

        self._assert_ok_response(rv, {'token': self._build_token()})

    def test_newest_by_profile_id_and_application_name(self):
        rv = self._client.get(
            '/api/token/newest',
            query_string={'profile_id': PROFILE_ID1, 'application_name': 'google-oauth2'},
        )

        self._assert_ok_response(rv, {'token': self._build_token()})

    def test_newest_with_scopes(self):
        rv = self._client.get(
            '/api/token/newest',
            query_string={'profile_id': PROFILE_ID1, 'application_id': '52', 'scope': 'foo bar'},
        )

        self._assert_ok_response(
            rv,
            {
                'token': self._build_token(
                    token_id=3,
                    application_token=APPLICATION_TOKEN3,
                    scope='bar foo',
                    created=UNIXTIME1,
                ),
            },
        )

    def test_newest_by_uid(self):
        rv = self._client.get(
            '/api/token/newest',
            query_string={'uid': UID1, 'application_id': '52'},
        )

        self._assert_ok_response(
            rv,
            {
                'token': self._build_token(
                    token_id=8,
                    profile_id=PROFILE_ID2,
                    application_token=APPLICATION_TOKEN8,
                    expired_in=None,
                    created=UNIXTIME1 + 3,
                    confirmed=UNIXTIME1 + 3,
                    verified=UNIXTIME1 + 3,
                ),
            },
        )


class TestGetTokenNewestExpiredRefreshable(GetTokenNewestTestCase):
    def setUp(self):
        super(TestGetTokenNewestExpiredRefreshable, self).setUp()

        self._fake_google = google_test.FakeProxy()
        self._fake_google.start()

        with self._fake_db.no_recording():
            db = self._fake_db.get_engine()

            save_token(self._create_token(APPLICATION_TOKEN1), db)

            save_token(self._create_token(APPLICATION_TOKEN2, created=datetime.fromtimestamp(UNIXTIME1 - 1)), db)
            save_refresh_token(self._create_refresh_token(APPLICATION_TOKEN3, token_id=2), db)

            save_token(self._create_token(APPLICATION_TOKEN4, created=datetime.fromtimestamp(UNIXTIME1 - 2)), db)
            save_refresh_token(self._create_refresh_token(APPLICATION_TOKEN5, token_id=3), db)

    def tearDown(self):
        self._fake_google.stop()
        super(TestGetTokenNewestExpiredRefreshable, self).tearDown()

    def _create_token(self, token_value, created=datetime.fromtimestamp(UNIXTIME1)):
        return Token(
            uid=UID1,
            profile_id=PROFILE_ID1,
            application_id=52,
            value=token_value,
            secret=None,
            scopes=['foo'],
            expired=datetime.fromtimestamp(UNIXTIME1),
            created=created,
            verified=datetime.fromtimestamp(UNIXTIME1),
            confirmed=datetime.fromtimestamp(UNIXTIME1),
        )

    def _create_refresh_token(self, refresh_token_value, token_id):
        return RefreshToken(
            token_id=token_id,
            value=refresh_token_value,
            expired=None,
            scopes=['foo'],
        )

    def test_refresh_token_valid(self):
        self._fake_google.set_response_value(
            'refresh_token',
            google_test.GoogleApi.refresh_token(APPLICATION_TOKEN2),
        )

        rv = self._client.get(
            '/api/token/newest',
            query_string={'profile_id': PROFILE_ID1, 'application_id': '52'},
        )

        self._assert_ok_response(
            rv,
            {
                'token': {
                    'token_id': 2,
                    'uid': UID1,
                    'profile_id': PROFILE_ID1,
                    'application': 'google-oauth2',
                    'value': APPLICATION_TOKEN2,
                    'secret': None,
                    'scope': 'foo',
                    'expired': DatetimeNow(convert_to_datetime=True) + timedelta(seconds=APPLICATION_TOKEN_TTL1),
                    'expired_ts': ApproximateInteger(datetime_to_unixtime(now() + timedelta(seconds=APPLICATION_TOKEN_TTL1))),
                    'created': str(datetime.fromtimestamp(UNIXTIME1 - 1)),
                    'created_ts': UNIXTIME1 - 1,
                    'confirmed': str(datetime.fromtimestamp(UNIXTIME1)),
                    'confirmed_ts': UNIXTIME1,
                    'verified': str(datetime.fromtimestamp(UNIXTIME1)),
                    'verified_ts': UNIXTIME1,
                },
            },
        )

    def test_refresh_token_expired(self):
        self._fake_google.set_response_value(
            'refresh_token',
            google_test.GoogleApi.build_invalid_grant_error(),
        )

        rv = self._client.get(
            '/api/token/newest',
            query_string={'profile_id': PROFILE_ID1, 'application_id': '52'},
        )

        self._assert_error_response(rv, 'token-not-found', status_code=404)

    def test_refresh_token__network_failed(self):
        self._fake_google.set_response_value('refresh_token', NetworkProxylibError())

        rv = self._client.get(
            '/api/token/newest',
            query_string={'profile_id': PROFILE_ID1, 'application_id': '52'},
        )

        self._assert_error_response(rv, 'internal-exception', status_code=504)

    def test_refresh_token__google_failed(self):
        self._fake_google.set_response_value(
            'refresh_token',
            google_test.GoogleApi.build_internal_failure_error(),
        )

        rv = self._client.get(
            '/api/token/newest',
            query_string={'profile_id': PROFILE_ID1, 'application_id': '52'},
        )

        self._assert_error_response(rv, 'internal-exception', status_code=502)


class TestGetTokenNewestAllExpiredNoRefreshable(GetTokenNewestTestCase):
    def setUp(self):
        super(TestGetTokenNewestAllExpiredNoRefreshable, self).setUp()

        with self._fake_db.no_recording():
            db = self._fake_db.get_engine()

            save_token(self._create_token(APPLICATION_TOKEN1), db)

    def _create_token(self, token_value, created=datetime.fromtimestamp(UNIXTIME1)):
        return Token(
            uid=UID1,
            profile_id=PROFILE_ID1,
            application_id=52,
            value=token_value,
            secret=None,
            scopes=['foo'],
            expired=datetime.fromtimestamp(UNIXTIME1),
            created=created,
            verified=datetime.fromtimestamp(UNIXTIME1),
            confirmed=datetime.fromtimestamp(UNIXTIME1),
        )

    def test_ok(self):
        rv = self._client.get(
            '/api/token/newest',
            query_string={'profile_id': PROFILE_ID1, 'application_id': '52'},
        )

        self._assert_error_response(rv, 'token-not-found', status_code=404)


class TestGetTokenNewestDatabaseFailed(GetTokenNewestTestCase):
    def setUp(self):
        super(TestGetTokenNewestDatabaseFailed, self).setUp()
        self._fake_db.set_side_effect(DatabaseError())

    def test_ok(self):
        rv = self._client.get(
            '/api/token/newest',
            query_string={'profile_id': PROFILE_ID1, 'application_id': '52'},
        )

        self._assert_error_response(
            rv,
            'internal-exception',
            status_code=500,
            description='Database failed',
        )


class TestGetTokenNewestByOauth(GetTokenNewestTestCase):
    BUILD_DEFAULT_GRANTS = False

    def setUp(self):
        super(TestGetTokenNewestByOauth, self).setUp()

        self._fake_blackbox = FakeBlackbox()
        self._fake_blackbox.start()

        with self._fake_db.no_recording():
            db = self._fake_db.get_engine()
            save_token(self._create_token(APPLICATION_TOKEN1), db)
            save_token(self._create_token(APPLICATION_TOKEN2, created=datetime.fromtimestamp(UNIXTIME1 + 1)), db)
            save_token(self._create_token(APPLICATION_TOKEN3, scopes=['foo', 'bar']), db)
            # Следующие токены заведомо новее остальных, однако не подходят
            # из-за того что либо истёк срок жизники, либо не тот профиль, либо
            # не то приложение.
            save_token(self._create_token(APPLICATION_TOKEN4, created=datetime.fromtimestamp(UNIXTIME1 + 2), expired=datetime.fromtimestamp(UNIXTIME1)), db)
            save_token(self._create_token(APPLICATION_TOKEN5, created=datetime.fromtimestamp(UNIXTIME1 + 2), profile_id=PROFILE_ID2), db)
            save_token(self._create_token(APPLICATION_TOKEN6, created=datetime.fromtimestamp(UNIXTIME1 + 2), application_id=53), db)

            profile_info1 = {'provider': {'code': 'gg'}, 'userid': SIMPLE_USERID1}
            token7 = self._create_token(APPLICATION_TOKEN7, expired=datetime.fromtimestamp(UNIXTIME1), profile_id=None, created=None)
            profile_info2 = {'provider': {'code': 'gg'}, 'userid': SIMPLE_USERID2}
            token8 = self._create_token(APPLICATION_TOKEN8, scopes=['foo'], created=None, profile_id=None, expired=None)
            for profile_info, token, timestamp in [
                (profile_info1, token7, UNIXTIME1),
                (profile_info2, token8, UNIXTIME1 + 3),
            ]:
                create_profile(
                    mysql_read=db,
                    mysql_write=db,
                    uid=UID1,
                    profile_info=profile_info,
                    token=token,
                    timestamp=timestamp,
                    yandexuid=YANDEXUID1,
                )

    def tearDown(self):
        self._fake_blackbox.stop()

    def _setup_blackbox(self, uid=UID1, token_scope=Undefined, status=BLACKBOX_OAUTH_VALID_STATUS):
        if token_scope is Undefined:
            token_scope = X_TOKEN_SCOPE

        self._fake_blackbox.set_response_value(
            'oauth',
            blackbox_oauth_response(
                uid=uid,
                scope=token_scope or '',
                status=status,
            ),
        )

    def _create_token(self, token_value, created=datetime.fromtimestamp(UNIXTIME1), scopes=None,
                      expired=Undefined, profile_id=PROFILE_ID1,
                      application_id=52):
        if scopes is None:
            scopes = ['foo']
        if expired is Undefined:
            expired = now() + timedelta(hours=1)
        return Token(
            uid=UID1,
            profile_id=profile_id,
            application_id=application_id,
            value=token_value,
            secret=None,
            scopes=scopes,
            expired=expired,
            created=created,
            verified=datetime.fromtimestamp(UNIXTIME1),
            confirmed=datetime.fromtimestamp(UNIXTIME1),
        )

    def _build_token(self,
                     token_id=2,
                     application_token=APPLICATION_TOKEN2,
                     scope='foo',
                     created=UNIXTIME1+1,
                     profile_id=PROFILE_ID1,
                     expired_in=timedelta(hours=1),
                     confirmed=UNIXTIME1,
                     verified=UNIXTIME1):

        if expired_in is not None:
            expired = DatetimeNow(convert_to_datetime=True) + expired_in
            expired_ts = ApproximateInteger(datetime_to_unixtime(now() + expired_in))
        else:
            expired = None
            expired_ts = None

        return {
            'token_id': token_id,
            'uid': UID1,
            'profile_id': profile_id,
            'application': 'google-oauth2',
            'value': application_token,
            'secret': None,
            'scope': scope,
            'expired': expired,
            'expired_ts': expired_ts,
            'created': str(datetime.fromtimestamp(created)),
            'created_ts': created,
            'confirmed': str(datetime.fromtimestamp(confirmed)),
            'confirmed_ts': confirmed,
            'verified': str(datetime.fromtimestamp(verified)),
            'verified_ts': verified,
        }

    def test_ok(self):
        self.build_grants(grants=['token-read', 'has-cred-read-token-application:google-oauth2'])
        self._setup_blackbox()

        rv = self._client.get(
            '/api/token/newest',
            query_string={'application_id': '52'},
            headers={
                'Ya-Consumer-Authorization': 'Bearer %s' % YANDEX_TOKEN1,
                'Ya-Consumer-Client-Ip': USER_IP1,
            }
        )

        self._assert_ok_response(
            rv,
            {
                'token': self._build_token(
                    token_id=8,
                    profile_id=PROFILE_ID2,
                    application_token=APPLICATION_TOKEN8,
                    expired_in=None,
                    created=UNIXTIME1 + 3,
                    confirmed=UNIXTIME1 + 3,
                    verified=UNIXTIME1 + 3,
                ),
            },
        )

    def test_token_read_grant(self):
        self.build_grants(grants=['token-read', 'no-cred-read-token-application:google-oauth2'])
        self._setup_blackbox()

        rv = self._client.get(
            '/api/token/newest',
            query_string={'application_id': '52'},
            headers={
                'Ya-Consumer-Authorization': 'Bearer %s' % YANDEX_TOKEN1,
                'Ya-Consumer-Client-Ip': USER_IP1,
            }
        )

        self._assert_ok_response(
            rv,
            {
                'token': self._build_token(
                    token_id=8,
                    profile_id=PROFILE_ID2,
                    application_token=APPLICATION_TOKEN8,
                    expired_in=None,
                    created=UNIXTIME1 + 3,
                    confirmed=UNIXTIME1 + 3,
                    verified=UNIXTIME1 + 3,
                ),
            },
        )

    def test_application_grant(self):
        self.build_grants(grants=['token-read', 'has-cred-read-token-application:google-oauth2'])
        self._setup_blackbox()

        rv = self._client.get(
            '/api/token/newest',
            query_string={'application_id': '52'},
            headers={
                'Ya-Consumer-Authorization': 'Bearer %s' % YANDEX_TOKEN1,
                'Ya-Consumer-Client-Ip': USER_IP1,
            }
        )

        self._assert_ok_response(
            rv,
            {
                'token': self._build_token(
                    token_id=8,
                    profile_id=PROFILE_ID2,
                    application_token=APPLICATION_TOKEN8,
                    expired_in=None,
                    created=UNIXTIME1 + 3,
                    confirmed=UNIXTIME1 + 3,
                    verified=UNIXTIME1 + 3,
                ),
            },
        )

    def test_reject_request_for_oauth_grants_with_uid(self):
        self.build_grants(grants=['token-read', 'has-cred-read-token-application:google-oauth2'])
        self._setup_blackbox()

        rv = self._client.get(
            '/api/token/newest',
            query_string={
                'application_id': '52',
                'consumer': 'dev',
                'uid': YANDEXUID1,
            },
            headers={
                'Ya-Consumer-Authorization': 'Bearer %s' % YANDEX_TOKEN1,
                'Ya-Consumer-Client-Ip': USER_IP1,
            }
        )

        self._assert_error_response(
            rv,
            'access-denied',
            status_code=403,
            description='Missing grants [no-cred-read-token, no-cred-read-token-application:google-oauth2] '
                'from Consumer(ip = 127.0.0.1, name = dev, matching_consumers = dev)',
        )

    def test_reject_request_for_oauth_grants_with_profile_id(self):
        self.build_grants(grants=['token-read', 'has-cred-read-token-application:google-oauth2'])
        self._setup_blackbox()

        rv = self._client.get(
            '/api/token/newest',
            query_string={
                'application_id': '52',
                'consumer': 'dev',
                'profile_id': PROFILE_ID1,
            },
            headers={
                'Ya-Consumer-Authorization': 'Bearer %s' % YANDEX_TOKEN1,
                'Ya-Consumer-Client-Ip': USER_IP1,
            }
        )

        self._assert_error_response(
            rv,
            'access-denied',
            status_code=403,
            description='Missing grants [no-cred-read-token, no-cred-read-token-application:google-oauth2] '
                'from Consumer(ip = 127.0.0.1, name = dev, matching_consumers = dev)',
        )

    def test_invalid_application_grant(self):
        self.build_grants(grants=['token-read', 'has-cred-read-token-application:invalid-application'])
        self._setup_blackbox()

        rv = self._client.get(
            '/api/token/newest',
            query_string={
                'application_id': '52',
                'consumer': 'dev',
            },
            headers={
                'Ya-Consumer-Authorization': 'Bearer %s' % YANDEX_TOKEN1,
                'Ya-Consumer-Client-Ip': USER_IP1,
            }
        )

        self._assert_error_response(
            rv,
            'access-denied',
            status_code=403,
            description='Missing grants [has-cred-read-token-application:google-oauth2, no-cred-read-token, '
                'no-cred-read-token-application:google-oauth2] from Consumer(ip = 127.0.0.1, '
                'name = dev, matching_consumers = dev)',
        )

    def test_invalid_oauth_token(self):
        self.build_grants(grants=['token-read', 'has-cred-read-token-application:google-oauth2'])
        self._setup_blackbox(status=BLACKBOX_OAUTH_INVALID_STATUS)

        rv = self._client.get(
            '/api/token/newest',
            query_string={'application_id': '52'},
            headers={
                'Ya-Consumer-Authorization': 'Bearer %s' % YANDEX_TOKEN1,
                'Ya-Consumer-Client-Ip': USER_IP1,
            }
        )

        self._assert_error_response(
            rv,
            'invalid-oauth-token',
            status_code=400,
            description='Invalid OAuth token',
        )

    def test_authorization_header_without_bearer_scheme(self):
        self.build_grants(grants=['token-read', 'has-cred-read-token-application:google-oauth2'])
        self._setup_blackbox(status=BLACKBOX_OAUTH_INVALID_STATUS)

        rv = self._client.get(
            '/api/token/newest',
            query_string={'application_id': '52'},
            headers={
                'Ya-Consumer-Authorization': '%s' % YANDEX_TOKEN1,
                'Ya-Consumer-Client-Ip': USER_IP1,
            }
        )

        self._assert_error_response(
            rv,
            'profile_id-empty',
            status_code=400,
            description=u'GET argument `profile_id` or `uid` or Ya-Consumer-Authorization headers with bearer-scheme is required',
        )

    def test_blackbox_failed(self):
        self.build_grants(grants=['token-read', 'has-cred-read-token-application:google-oauth2'])
        self._fake_blackbox.set_response_side_effect(
            'oauth',
            BlackboxTemporaryError(),
        )

        rv = self._client.get(
            '/api/token/newest',
            query_string={'application_id': '52'},
            headers={
                'Ya-Consumer-Authorization': 'Bearer %s' % YANDEX_TOKEN1,
                'Ya-Consumer-Client-Ip': USER_IP1,
            }
        )

        self._assert_error_response(
            rv,
            'internal-exception',
            status_code=500,
            description='Blackbox failed',
        )


class TestGetTokenNewestApplicationOnlyToken(GetTokenNewestTestCase):
    def setUp(self):
        super(TestGetTokenNewestApplicationOnlyToken, self).setUp()

        with self._fake_db.no_recording():
            db = self._fake_db.get_engine()
            token = save_token(
                Token(
                    application_id=APPLICATION_ID1,
                    expired=now(),
                    uid=UID1,
                    value=APPLICATION_TOKEN1,
                ),
                db,
            )
            save_refresh_token(
                RefreshToken(
                    token_id=token.token_id,
                    value=APPLICATION_TOKEN1,
                ),
                db,
            )

    def build_settings(self):
        settings = super(TestGetTokenNewestApplicationOnlyToken, self).build_settings()
        settings.update(
            applications=[
                dict(
                    application_id=APPLICATION_ID1,
                    application_name=APPLICATION_NAME1,
                    provider_client_id=EXTERNAL_APPLICATION_ID1,
                    refresh_token_url='https://foo/refresh',
                    request_from_intranet_allowed=True,
                    secret=APPLICATION_SECRET1,
                ),
            ],
        )
        return settings

    def test_refresh_token__unhashable_error(self):
        self._fake_useragent.set_response_value(
            FakeResponse(json.dumps({'error': ['foo']}), status_code=200),
        )

        rv = self._client.get(
            '/api/token/newest',
            query_string={'application_name': APPLICATION_NAME1, 'uid': UID1},
        )

        self._assert_error_response(
            rv,
            'internal-exception',
            status_code=502,
            description='Unexpected provider response',
        )

    def test_refresh_token__not_dict_response(self):
        self._fake_useragent.set_response_value(
            FakeResponse(json.dumps(['error']), status_code=200),
        )

        rv = self._client.get(
            '/api/token/newest',
            query_string={'application_name': APPLICATION_NAME1, 'uid': UID1},
        )

        self._assert_error_response(
            rv,
            'internal-exception',
            status_code=502,
            description='Unexpected provider response',
        )

    def test_refresh_token__empty_response(self):
        self._fake_useragent.set_response_value(
            FakeResponse('', status_code=200),
        )

        rv = self._client.get(
            '/api/token/newest',
            query_string={'application_name': APPLICATION_NAME1, 'uid': UID1},
        )

        self._assert_error_response(
            rv,
            'internal-exception',
            status_code=502,
            description='Unexpected provider response',
        )

    def test_refresh_token__empty_dict(self):
        self._fake_useragent.set_response_value(
            FakeResponse(json.dumps(dict()), status_code=200),
        )

        rv = self._client.get(
            '/api/token/newest',
            query_string={'application_name': APPLICATION_NAME1, 'uid': UID1},
        )

        self._assert_error_response(
            rv,
            'internal-exception',
            status_code=502,
            description='Unexpected provider response',
        )
