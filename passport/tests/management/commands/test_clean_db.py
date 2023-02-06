# -*- coding: utf-8 -*-
from datetime import (
    datetime,
    timedelta,
)

from django.conf import settings
import mock
from nose.tools import eq_
from passport.backend.core.builders.blackbox.faker.blackbox import blackbox_userinfo_response
from passport.backend.core.test.test_utils.utils import OPEN_PATCH_TARGET
from passport.backend.oauth.api.api.management.commands.clean_db import (
    Command as CleanDBCommand,
    DELETE_OFFSET,
)
from passport.backend.oauth.core.db.client import Client
from passport.backend.oauth.core.db.eav import (
    CREATE,
    UPDATE,
)
from passport.backend.oauth.core.db.scope import Scope
from passport.backend.oauth.core.db.token import (
    issue_token,
    list_tokens_by_uid,
)
from passport.backend.oauth.core.test.base_test_data import TEST_UID
from passport.backend.oauth.core.test.framework import ManagementCommandTestCase
from passport.backend.oauth.core.test.utils import iter_eq
from passport.backend.utils.time import datetime_to_integer_unixtime


class TestCleanDB(ManagementCommandTestCase):
    command_class = CleanDBCommand
    default_command_kwargs = {
        'chunk_size': 10,
        'clean_tokens': False,
        'clean_requests': False,
        'use_pauses': False,
        'pause_length': 1.0,
        'retries': 2,
        'last_processed_id': None,
        'simplified': False,
        'glogouts_csv_filename': None,
    }
    logger_name = 'management.db_cleaner'

    def setUp(self):
        super(TestCleanDB, self).setUp()

        self.glogout_time = datetime.now() - timedelta(seconds=60)
        self.fake_blackbox.set_response_value(
            'userinfo',
            blackbox_userinfo_response(
                uid=TEST_UID,
                attributes={settings.BB_ATTR_GLOGOUT: datetime_to_integer_unixtime(self.glogout_time)},
            ),
        )

        with CREATE(Client.create(
            uid=TEST_UID,
            scopes=[Scope.by_keyword('test:foo'), Scope.by_keyword('test:bar')],
            default_title='test_app',
        )) as client:
            self.test_client = client

        with CREATE(Client.create(
            uid=TEST_UID,
            scopes=[Scope.by_keyword('test:foo')],
            default_title='test_other_app',
        )) as client:
            client.glogouted = datetime.now() + timedelta(seconds=60)
            self.test_glogouted_client = client

        self.valid_token = issue_token(
            uid=TEST_UID,
            client=self.test_client,
            grant_type='password',
            env=self.env,
            device_id='valid',
        )

        self.expired_token = issue_token(
            uid=TEST_UID,
            client=self.test_client,
            grant_type='password',
            env=self.env,
            device_id='expired',
        )
        with UPDATE(self.expired_token) as token:
            token.expires = datetime.now() - DELETE_OFFSET - timedelta(seconds=60)

        self.token_glogouted_by_user = issue_token(
            uid=TEST_UID,
            client=self.test_client,
            grant_type='password',
            env=self.env,
            device_id='glogouted_by_user',
        )
        with UPDATE(self.token_glogouted_by_user) as token:
            token.issued = self.glogout_time - DELETE_OFFSET - timedelta(seconds=60)

        self.token_glogouted_by_client = issue_token(
            uid=TEST_UID,
            client=self.test_glogouted_client,
            grant_type='password',
            env=self.env,
            device_id='glogouted_by_client',
        )

        iter_eq(
            set(list_tokens_by_uid(TEST_UID)),
            {self.valid_token, self.expired_token, self.token_glogouted_by_user, self.token_glogouted_by_client},
        )

    def test_nothing_to_do(self):
        self.run_command()

        iter_eq(
            set(list_tokens_by_uid(TEST_UID)),
            {self.valid_token, self.expired_token, self.token_glogouted_by_user, self.token_glogouted_by_client},
        )
        eq_(len(self.fake_blackbox.requests), 0)
        self.assert_log('Task complete. Dropped 0 tokens, 0 requests; 0 tokens set to expire soon', level='info')

    def test_tokens_full_ok(self):
        self.run_command(clean_tokens=True)

        iter_eq(
            set(list_tokens_by_uid(TEST_UID)),
            {self.valid_token},
        )
        eq_(len(self.fake_blackbox.requests), 1)
        self.assert_log('Task complete. Dropped 3 tokens, 0 requests; 0 tokens set to expire soon', level='info')

    def test_tokens_simplified_ok(self):
        self.run_command(clean_tokens=True, simplified=True)

        iter_eq(
            set(list_tokens_by_uid(TEST_UID)),
            {self.valid_token, self.token_glogouted_by_user, self.token_glogouted_by_client},
        )
        eq_(len(self.fake_blackbox.requests), 0)
        self.assert_log('Task complete. Dropped 1 tokens, 0 requests; 0 tokens set to expire soon', level='info')

    def test_tokens_simplified_with_glogouts_ok(self):
        with mock.patch(
            OPEN_PATCH_TARGET,
            mock.mock_open(
                read_data='%d,%d' % (TEST_UID, datetime_to_integer_unixtime(self.glogout_time)),
            ),
        ):
            self.run_command(clean_tokens=True, simplified=True, glogouts_csv_filename='glogouts.csv')

        self.assert_log('Task complete. Dropped 2 tokens, 0 requests; 0 tokens set to expire soon', level='info')
        iter_eq(
            set(list_tokens_by_uid(TEST_UID)),
            {self.valid_token, self.token_glogouted_by_client},
        )
        eq_(len(self.fake_blackbox.requests), 0)
        self.assert_log('Task complete. Dropped 2 tokens, 0 requests; 0 tokens set to expire soon', level='info')
