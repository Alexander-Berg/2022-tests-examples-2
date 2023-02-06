# -*- coding: utf-8 -*-
from datetime import (
    datetime,
    timedelta,
)

from django.urls import reverse_lazy
from nose.tools import assert_almost_equal
from passport.backend.oauth.core.db.eav import (
    DBTemporaryError,
    UPDATE,
)
from passport.backend.oauth.core.db.eav.dbmanager import get_dbm
from passport.backend.oauth.core.db.scope import Scope
from passport.backend.oauth.core.db.token import (
    issue_token,
    Token,
)
from passport.backend.oauth.core.test.base_test_data import (
    TEST_GRANT_TYPE,
    TEST_UID,
)
from passport.backend.oauth.core.test.framework.testcases.bundle_api_testcase import BundleApiTestCase


TIME_DELTA = timedelta(seconds=5)


class TestRefreshToken(BundleApiTestCase):
    default_url = reverse_lazy('api_refresh_token')
    http_method = 'POST'

    def setUp(self):
        super(TestRefreshToken, self).setUp()
        scope = Scope.by_keyword('test:ttl_refreshable')
        self.default_ttl = scope.ttl
        with UPDATE(self.test_client) as client:
            client.set_scopes([scope])

    def default_params(self):
        return {
            'consumer': 'dev',
        }

    def test_ok(self):
        token = issue_token(
            uid=TEST_UID,
            client=self.test_client,
            grant_type=TEST_GRANT_TYPE,
            env=self.env,
        )
        with UPDATE(token):
            token.expires = datetime.now() + timedelta(seconds=self.default_ttl / 3)

        rv = self.make_request(token_id=token.id)
        self.assert_status_ok(rv)

        token = Token.by_id(token.id)
        assert_almost_equal(
            token.expires,
            datetime.now() + timedelta(seconds=self.default_ttl),
            delta=TIME_DELTA,
        )

        self.check_statbox_entry(
            {
                'mode': 'refresh',
                'target': 'token',
                'status': 'ok',
                'token_id': str(token.id),
                'uid': str(TEST_UID),
            },
        )

    def test_needs_no_refresh(self):
        token = issue_token(
            uid=TEST_UID,
            client=self.test_client,
            grant_type=TEST_GRANT_TYPE,
            env=self.env,
        )
        with UPDATE(token):
            token.expires = datetime.now() + timedelta(seconds=self.default_ttl * 2 / 3)
        old_expire_time = token.expires

        rv = self.make_request(token_id=token.id)
        self.assert_status_ok(rv)

        token = Token.by_id(token.id)
        assert_almost_equal(
            token.expires,
            old_expire_time,
            delta=TIME_DELTA,
        )

    def test_not_refreshable(self):
        token = issue_token(
            uid=TEST_UID,
            client=self.test_client,
            grant_type=TEST_GRANT_TYPE,
            env=self.env,
        )
        with UPDATE(token):
            token.is_refreshable = False
        old_expire_time = token.expires

        rv = self.make_request(token_id=token.id)
        self.assert_status_ok(rv)

        token = Token.by_id(token.id)
        assert_almost_equal(
            token.expires,
            old_expire_time,
            delta=TIME_DELTA,
        )

    def test_refresh_failed(self):
        token = issue_token(
            uid=TEST_UID,
            client=self.test_client,
            grant_type=TEST_GRANT_TYPE,
            env=self.env,
        )
        with UPDATE(token):
            token.is_refreshable = True
            token.expires = datetime.now() + timedelta(seconds=60)
        old_expire_time = token.expires

        # чтение токена происходит одним запросом, а не транзакцией
        get_dbm('oauthdbshard1').transaction.side_effect = DBTemporaryError

        rv = self.make_request(token_id=token.id)
        self.assert_status_ok(rv)

        token = Token.by_id(token.id)
        assert_almost_equal(
            token.expires,
            old_expire_time,
            delta=TIME_DELTA,
        )

    def test_token_not_found(self):
        rv = self.make_request(token_id=123)
        self.assert_status_ok(rv)
        self.check_statbox_entries([])
