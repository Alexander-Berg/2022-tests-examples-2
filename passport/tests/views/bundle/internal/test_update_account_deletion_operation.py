# -*- coding: utf-8 -*-

from passport.backend.api.test.views import (
    BaseBundleTestViews,
    ViewsTestEnvironment,
)
from passport.backend.core.models.account import ACCOUNT_DISABLED_ON_DELETION
from passport.backend.core.models.phones.faker import build_account
from passport.backend.core.test.consts import *
from passport.backend.core.test.test_utils.utils import with_settings_hosts
from passport.backend.utils.time import datetime_to_integer_unixtime as to_unixtime


@with_settings_hosts()
class TestUpdateAccountDeletionOperation(BaseBundleTestViews):
    def setUp(self):
        super(TestUpdateAccountDeletionOperation, self).setUp()

        self.env = ViewsTestEnvironment()
        self.env.start()

        self.env.grants.set_grants_return_value({
            'dev': {
                'networks': ['127.0.0.1'],
                'grants': {'internal': ['update_account_deletion_operation']},
            },
        })

    def tearDown(self):
        self.env.stop()
        del self.env
        super(TestUpdateAccountDeletionOperation, self).tearDown()

    def _build_account(self, operation_exists=True):
        userinfo = dict(
            uid=TEST_UID1,
            attributes={'account.is_disabled': ACCOUNT_DISABLED_ON_DELETION},
        )
        if operation_exists:
            userinfo['attributes'].update({'account.deletion_operation_started_at': to_unixtime(TEST_DATETIME1)})
        return dict(userinfo=userinfo)

    def _setup_account(self, account):
        build_account(
            db_faker=self.env.db,
            blackbox_faker=self.env.blackbox,
            **account['userinfo']
        )

    def _assert_operation_attrs_equal(self, updated_attrs):
        attrs = dict(started_at=TEST_DATETIME1)
        attrs.update(updated_attrs)

        self.env.db.check_db_attr(
            TEST_UID1,
            'account.deletion_operation_started_at',
            str(to_unixtime(attrs['started_at'])),
        )
        self.env.db.check(
            'account_deletion_operations',
            'started_at',
            attrs['started_at'],
            uid=TEST_UID1,
            db='passportdbshard1',
        )

    def _assert_operation_not_exist(self):
        self.env.db.check_db_attr_missing(TEST_UID1, 'account.deletion_operation_started_at')
        self.env.db.check_missing('account_deletion_operations', uid=TEST_UID1, db='passportdbshard1')

    def _assert_operation_updated_in_history(self, attrs):
        entries = {
            'action': 'update_account_deletion_operation',
            'deletion_operation': 'updated',
            'consumer': 'dev',
        }
        for attr in attrs:
            name = 'deletion_operation.%s' % attr
            entries.update({name: str(attrs[attr])})
        self.env.event_logger.assert_events_are_logged(entries)

    def _make_request(self, args=None):
        args = args or {}

        defaults = dict(uid=TEST_UID1, started_at=to_unixtime(TEST_DATETIME1))

        for arg in defaults:
            args.setdefault(arg, defaults[arg])

        return self.env.client.post('/1/bundle/test/update_account_deletion_operation/', query_string=dict(consumer='dev'), data=args)

    def test_update_started_at(self):
        self._setup_account(self._build_account())

        rv = self._make_request(dict(started_at=to_unixtime(TEST_DATETIME2)))

        self.assert_ok_response(rv)
        self._assert_operation_attrs_equal(dict(started_at=TEST_DATETIME2))

        self._assert_operation_updated_in_history(dict(started_at=TEST_DATETIME2))
        self.env.statbox.assert_has_written([])

    def test_request_deletion_operation(self):
        self._setup_account(self._build_account())

        rv = self._make_request()

        self.assert_ok_response(rv)

        self.env.blackbox.requests[0].assert_contains_attributes({
            'account.is_disabled',
            'account.deletion_operation_started_at',
        })

    def test_operation_not_found(self):
        self._setup_account(self._build_account(operation_exists=False))

        rv = self._make_request()

        self.assert_error_response(rv, ['account_deletion_operation.not_found'])
        self._assert_operation_not_exist()

    def test_no_started_at(self):
        self._setup_account(self._build_account())

        rv = self._make_request(dict(started_at=None))

        self.assert_ok_response(rv)
        self._assert_operation_attrs_equal(dict(started_at=TEST_DATETIME1))

        self.env.event_logger.assert_events_are_logged({})

    def test_no_uid(self):
        self._setup_account(self._build_account())

        rv = self._make_request(dict(uid=None))

        self.assert_error_response(rv, ['uid.empty'])
