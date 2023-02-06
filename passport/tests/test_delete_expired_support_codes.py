# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import mock
from passport.backend.core.test.test_utils.utils import with_settings_hosts
from passport.backend.core.test.time_utils.time_utils import TimeNow
from passport.backend.core.ydb.processors.support_code import DeleteSupportCodesExpiredBeforeTimestampYdbQuery
import passport.backend.core.ydb_client as ydb
from passport.backend.dbscripts.delete_expired_support_codes.cli import Main
from passport.backend.dbscripts.test.base import TestCase


@with_settings_hosts(
    YDB_RETRIES=2,
)
class TestDeleteExpiredSupportCodes(TestCase):
    def test_ok(self):
        Main().run(0)

        self.fake_ydb.assert_queries_executed(
            [
                DeleteSupportCodesExpiredBeforeTimestampYdbQuery(TimeNow()),
            ],
        )

    def test_ydb_timeout(self):
        self.fake_ydb.set_execute_side_effect(ydb.Timeout(''))

        with self.assertRaises(SystemExit):
            Main().run(0)

    def test_script_disabled_in_intranet(self):
        yenv = mock.Mock()
        yenv.name = 'intranet'

        with mock.patch('passport.backend.dbscripts.utils.yenv', yenv):
            assert not Main().is_allowed_env()
