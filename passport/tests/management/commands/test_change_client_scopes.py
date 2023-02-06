# -*- coding: utf-8 -*-
import json

import mock
from nose.tools import (
    assert_raises,
    eq_,
)
from passport.backend.core.test.test_utils.utils import OPEN_PATCH_TARGET
from passport.backend.oauth.api.api.management.commands.change_client_scopes import Command as ChangeClientScopesCommand
from passport.backend.oauth.core.db.client import Client
from passport.backend.oauth.core.db.eav import (
    CREATE,
    DBTemporaryError,
    UPDATE,
)
from passport.backend.oauth.core.db.eav.dbmanager import get_dbm
from passport.backend.oauth.core.db.scope import Scope
from passport.backend.oauth.core.db.token import (
    issue_token,
    Token,
)
from passport.backend.oauth.core.test.framework import ManagementCommandTestCase


class TestChangeClientScopes(ManagementCommandTestCase):
    command_class = ChangeClientScopesCommand
    default_command_kwargs = {
        'chunk_size': 10,
        'client_display_id': None,
        'old_scopes': '',
        'new_scopes': '',
        'scopes_to_add': '',
        'config_file': None,
        'use_pauses': False,
        'pause_length': 1.0,
        'ignore_client_scopes': False,
        'ignore_token_scopes': False,
        'retries': 2,
        'last_processed_id': None,
        'skip_tokens': False,
    }

    def setUp(self):
        super(TestChangeClientScopes, self).setUp()

        with CREATE(Client.create(
            uid=1,
            scopes=[Scope.by_keyword('test:foo'), Scope.by_keyword('test:bar')],
            default_title='test_app',
        )) as client:
            self.test_client = client

        with CREATE(Client.create(
            uid=1,
            scopes=[Scope.by_keyword('test:foo')],
            default_title='test_other_app',
        )) as client:
            self.test_other_client = client

        self.token = issue_token(
            uid=1,
            client=self.test_client,
            grant_type='password',
            env=self.env,
        )
        self.other_token = issue_token(
            uid=1,
            client=self.test_other_client,
            grant_type='password',
            env=self.env,
        )

    def check_ok(self, first_client_scopes=None, second_client_scopes=None,
                 first_token_scopes=None, second_token_scopes=None):
        if first_client_scopes is None:
            first_client_scopes = self.test_client.scopes
        else:
            first_client_scopes = {Scope.by_keyword(kw) for kw in first_client_scopes}

        if second_client_scopes is None:
            second_client_scopes = self.test_other_client.scopes
        else:
            second_client_scopes = {Scope.by_keyword(kw) for kw in second_client_scopes}

        if first_token_scopes is not None:
            first_token_scopes = {Scope.by_keyword(kw) for kw in first_token_scopes}
        else:
            first_token_scopes = first_client_scopes

        if second_token_scopes is not None:
            second_token_scopes = {Scope.by_keyword(kw) for kw in second_token_scopes}
        else:
            second_token_scopes = second_client_scopes

        client = Client.by_display_id(self.test_client.display_id)
        eq_(client.scopes, first_client_scopes)
        eq_(
            sorted(client.services),
            sorted(set(scope.service_name for scope in first_client_scopes)),
        )

        other_client = Client.by_display_id(self.test_other_client.display_id)
        eq_(other_client.scopes, second_client_scopes)
        eq_(
            sorted(other_client.services),
            sorted(set(scope.service_name for scope in second_client_scopes)),
        )

        token = Token.by_id(self.token.id)
        eq_(token.scopes, first_token_scopes)

        other_token = Token.by_id(self.other_token.id)
        eq_(other_token.scopes, second_token_scopes)

    def test_ok(self):
        self.run_command(
            client_display_id=self.test_client.display_id,
            old_scopes='test:foo test:bar',
            new_scopes='test:foo test:bar test:ttl',
        )

        self.check_ok(
            first_client_scopes=['test:foo', 'test:bar', 'test:ttl'],
        )
        self.assert_log('Done.', level='info')

    def test_ok_with_scopes_to_add(self):
        self.run_command(
            client_display_id=self.test_client.display_id,
            old_scopes='test:foo test:bar',
            scopes_to_add='test:ttl',
        )

        self.check_ok(
            first_client_scopes=['test:foo', 'test:bar', 'test:ttl'],
        )
        self.assert_log('Done.', level='info')

    def test_ok_with_config(self):
        test_config = [
            {
                'client_display_id': self.test_client.display_id,
                'old_scopes': 'test:foo test:bar',
                'new_scopes': 'test:foo test:bar test:ttl',
            }
        ]
        with mock.patch(OPEN_PATCH_TARGET, mock.mock_open(read_data=json.dumps(test_config))):
            self.run_command(config_file='test.json')

        self.check_ok(
            first_client_scopes=['test:foo', 'test:bar', 'test:ttl'],
        )
        self.assert_log('Done.', level='info')

    def test_multiple_ok(self):
        test_config = [
            {
                'client_display_id': self.test_client.display_id,
                'old_scopes': 'test:foo test:bar',
                'new_scopes': 'test:foo test:bar test:ttl',
            }
        ]
        with mock.patch(OPEN_PATCH_TARGET, mock.mock_open(read_data=json.dumps(test_config))):
            self.run_command(
                config_file='test.json',
                client_display_id=self.test_other_client.display_id,
                old_scopes='test:foo',
                scopes_to_add='test:ttl',
            )

        self.check_ok(
            first_client_scopes=['test:foo', 'test:bar', 'test:ttl'],
            first_token_scopes=['test:foo', 'test:bar', 'test:ttl'],
            second_client_scopes=['test:foo', 'test:ttl'],
            second_token_scopes=['test:foo', 'test:ttl'],
        )
        self.assert_log('Done.', level='info')

    def test_ok_with_pauses(self):
        self.run_command(
            client_display_id=self.test_client.display_id,
            old_scopes='test:foo test:bar',
            scopes_to_add='test:ttl',
            use_pauses=True,
            pause_length=0,
        )

        self.check_ok(
            first_client_scopes=['test:foo', 'test:bar', 'test:ttl'],
        )
        self.assert_log('Done.', level='info')

    def test_invalid_args_error(self):
        with assert_raises(SystemExit):
            self.run_command(client_display_id=self.test_client.display_id)
        self.assert_log(
            'Incomplete config entry: %s' % {
                'client_display_id': self.test_client.display_id,
                'old_scopes': set(),
                'new_scopes': set(),
                'scopes_to_add': set(),
            },
        )

    def test_empty_config_error(self):
        with mock.patch(OPEN_PATCH_TARGET, mock.mock_open(read_data=json.dumps([]))):
            with assert_raises(SystemExit):
                self.run_command()

        self.check_ok()
        self.assert_log('No clients to process')

    def test_duplicate_client_ids_error(self):
        test_config = [
            {
                'client_display_id': self.test_client.display_id,
                'old_scopes': 'test:foo test:bar',
                'new_scopes': 'test:foo test:bar test:ttl',
            }
        ]
        with mock.patch(OPEN_PATCH_TARGET, mock.mock_open(read_data=json.dumps(test_config))):
            with assert_raises(SystemExit):
                self.run_command(
                    config_file='test.json',
                    client_display_id=self.test_client.display_id,
                    old_scopes='test:foo test:bar',
                    scopes_to_add='test:ttl',
                )

        self.check_ok()
        self.assert_log('Duplicate clients in config')

    def test_client_not_found_error(self):
        with assert_raises(SystemExit):
            self.run_command(
                client_display_id='foo',
                old_scopes='test:foo test:bar',
                scopes_to_add='test:ttl',
            )

        self.check_ok()
        self.assert_log('Client foo not found')

    def test_client_scope_mismatch_error(self):
        with assert_raises(SystemExit):
            self.run_command(
                client_display_id=self.test_client.display_id,
                old_scopes='test:foo',
                scopes_to_add='test:ttl',
            )

        self.check_ok()
        self.assert_log(
            "Client %s has unexpected scopes: test:bar,test:foo (instead of test:foo)" % (
                self.test_client.display_id,
            ),
        )

    def test_db_error_on_reading_clients(self):
        get_dbm('oauthdbcentral').execute.side_effect = DBTemporaryError('DB is down')
        with assert_raises(SystemExit):
            self.run_command(
                client_display_id=self.test_client.display_id,
                old_scopes='test:foo test:bar',
                scopes_to_add='test:ttl',
            )
        get_dbm('oauthdbcentral').execute.side_effect = None  # чтобы прошёл check_ok

        self.check_ok()
        self.assert_log('Unhandled error: DB is down')

    def test_db_error_on_reading_tokens(self):
        get_dbm('oauthdbshard1').execute.side_effect = DBTemporaryError('DB is down')
        with assert_raises(SystemExit):
            self.run_command(
                client_display_id=self.test_client.display_id,
                old_scopes='test:foo test:bar',
                scopes_to_add='test:ttl',
            )
        get_dbm('oauthdbshard1').execute.side_effect = None  # чтобы прошёл check_ok

        self.check_ok(
            first_client_scopes=['test:foo', 'test:bar', 'test:ttl'],
            first_token_scopes=['test:foo', 'test:bar'],
        )
        self.assert_log('Error while getting token chunk: DB is down')

    def test_db_error_on_updating_client(self):
        get_dbm('oauthdbcentral').transaction.side_effect = DBTemporaryError('DB is down')
        with assert_raises(SystemExit):
            self.run_command(
                client_display_id=self.test_client.display_id,
                old_scopes='test:foo test:bar',
                scopes_to_add='test:ttl',
            )

        self.check_ok()
        self.assert_log('Unable to edit client %s: DB is down' % self.test_client.display_id)

    def test_unable_to_edit_token(self):
        get_dbm('oauthdbshard1').transaction.side_effect = DBTemporaryError('DB is down')
        self.run_command(
            client_display_id=self.test_client.display_id,
            old_scopes='test:foo test:bar',
            scopes_to_add='test:ttl',
        )

        self.check_ok(
            first_client_scopes=['test:foo', 'test:bar', 'test:ttl'],
            first_token_scopes=['test:foo', 'test:bar'],
        )
        self.assert_log('Unable to edit token %s: DB is down' % self.token.id, level='warning')

    def test_nothing_changed(self):
        self.run_command(
            client_display_id=self.test_client.display_id,
            scopes_to_add='test:foo',
            ignore_client_scopes=True,
            ignore_token_scopes=True,
        )

        self.check_ok()
        self.assert_log('Done.', level='info')

    def test_unexpected_token_scopes_error(self):
        with UPDATE(self.token) as token:
            token.set_scopes([Scope.by_keyword('test:foo')])

        self.run_command(
            client_display_id=self.test_client.display_id,
            old_scopes='test:foo test:bar',
            scopes_to_add='test:ttl',
        )

        self.check_ok(
            first_client_scopes=['test:foo', 'test:bar', 'test:ttl'],
            first_token_scopes=['test:foo'],
        )
        self.assert_log(
            'Token %s has unexpected scopes: test:foo (instead of test:bar,test:foo)' % (
                self.token.id,
            ),
            level='warning',
        )

    def test_unexpected_token_scopes_shrink_error(self):
        with UPDATE(self.token) as token:
            token.set_scopes([Scope.by_keyword('test:ttl_refreshable')])

        self.run_command(
            client_display_id=self.test_client.display_id,
            old_scopes='test:foo test:bar',
            new_scopes='test:foo test:bar test:ttl',
            ignore_token_scopes=True,
        )

        self.check_ok(
            first_client_scopes=['test:foo', 'test:bar', 'test:ttl'],
            first_token_scopes=['test:ttl_refreshable'],
        )
        self.assert_log(
            'Unable to shrink token %s scopes(current: test:ttl_refreshable, desired: test:bar,test:foo,test:ttl)' % (
                self.token.id,
            ),
            level='warning',
        )

    def test_unexpected_token_scopes_extend_ok(self):
        with UPDATE(self.token) as token:
            token.set_scopes([Scope.by_keyword('test:foo')])

        self.run_command(
            client_display_id=self.test_client.display_id,
            old_scopes='test:foo test:bar',
            new_scopes='test:foo test:bar test:ttl',
            ignore_token_scopes=True,
        )

        self.check_ok(
            first_client_scopes=['test:foo', 'test:bar', 'test:ttl'],
        )
        self.assert_log('Done.', level='info')

    def test_update_client_only(self):
        self.run_command(
            client_display_id=self.test_client.display_id,
            old_scopes='test:foo test:bar',
            scopes_to_add='lunapark:use',
            skip_tokens=True,
        )

        self.check_ok(
            first_client_scopes=['test:foo', 'test:bar', 'lunapark:use'],
            first_token_scopes=['test:foo', 'test:bar'],
        )
        self.assert_log('Done.', level='info')
