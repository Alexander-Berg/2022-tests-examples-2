# -*- coding: utf-8 -*-
from datetime import datetime

import mock
from passport.backend.core.test.test_utils.utils import with_settings_hosts
from passport.backend.core.ydb.declarative import delete
from passport.backend.core.ydb.schemas import family_invites_table as fit
import passport.backend.core.ydb_client as ydb
from passport.backend.dbscripts.delete_expired_family_invites.cli import Main
from passport.backend.dbscripts.delete_expired_family_invites.settings import INVITE_EXPIRE_TIME
from passport.backend.dbscripts.test.base import TestCase


TEST_TIMESTAMP = 1586793497
TEST_TIMESTAMP_EXPIRE = TEST_TIMESTAMP - INVITE_EXPIRE_TIME


@with_settings_hosts(
    YDB_RETRIES=2,
)
class TestDeleteExpiredFamilyInvites(TestCase):
    def setUp(self):
        super(TestDeleteExpiredFamilyInvites, self).setUp()
        self.datetimeFaker = mock.patch(
            'passport.backend.dbscripts.delete_expired_family_invites.cli.datetime',
            mock.Mock(now=mock.Mock(return_value=datetime.fromtimestamp(TEST_TIMESTAMP))),
        )
        self.datetimeFaker.start()

    def _build_delete_query(self, timestamp=TEST_TIMESTAMP_EXPIRE):
        return delete(
            fit,
            fit.c.create_time <= timestamp,
            optimizer_index='create_time_index',
        ).compile()

    def tearDown(self):
        self.datetimeFaker.stop()
        del self.datetimeFaker

    def test_ok(self):
        Main().run(0)

        self.fake_ydb.assert_queries_executed([self._build_delete_query()])

    def test_ydb_timeout(self):
        self.fake_ydb.set_execute_side_effect(ydb.Timeout(''))

        with self.assertRaises(SystemExit):
            Main().run(0)

    def test_script_disabled_in_intranet(self):
        yenv = mock.Mock()
        yenv.name = 'intranet'

        with mock.patch('passport.backend.dbscripts.utils.yenv', yenv):
            assert not Main().is_allowed_env()
