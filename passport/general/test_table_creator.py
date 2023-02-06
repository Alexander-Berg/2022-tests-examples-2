import os
import time

from passport.infra.recipes.common import log

import passport.infra.daemons.lbchdb.ut_medium.common.schemes as schemes
import passport.infra.daemons.lbchdb.ut_medium.logbroker as lb

from passport.infra.daemons.lbchdb.ut_medium.lbchdb import LbchdbFixture


class TestLbchdbTableCreator:
    lbchdb = None

    start_time = None
    prev_month = None
    curr_month = None
    next_month = None

    @classmethod
    def setup_class(cls):
        os.environ['TZ'] = 'Europe/Moscow'
        time.tzset()

        log('Starting lbchdb table creator test')

        cls.start_time = time.time()
        cls.curr_month = schemes.MonthlyTable(cls.start_time)
        cls.prev_month = cls.curr_month.prev()
        cls.next_month = cls.curr_month.next()

        lb.skip_data_for(LbchdbFixture.logbroker_client_id)

        schemes.prepare_yt()

        cls.lbchdb = LbchdbFixture(check_period__msec=100)

    @classmethod
    def teardown_class(cls):
        log('Closing lbchdb table creator test')
        cls.lbchdb.stop()

    def test_push(self):
        self.lbchdb.check_yt_content(
            content={
                self.prev_month.path(schemes.PUSH_TABLE_DIR): [],
                self.curr_month.path(schemes.PUSH_TABLE_DIR): [],
                self.next_month.path(schemes.PUSH_TABLE_DIR): [],
            },
        )

        self.lbchdb.check_yt_content(
            content={
                self.prev_month.path(schemes.PUSH_BY_UID_TABLE_DIR): [],
                self.curr_month.path(schemes.PUSH_BY_UID_TABLE_DIR): [],
                self.next_month.path(schemes.PUSH_BY_UID_TABLE_DIR): [],
            },
        )

        self.lbchdb.check_yt_content(
            content={
                self.prev_month.path(schemes.PUSH_BY_APP_ID_TABLE_DIR): [],
                self.curr_month.path(schemes.PUSH_BY_APP_ID_TABLE_DIR): [],
                self.next_month.path(schemes.PUSH_BY_APP_ID_TABLE_DIR): [],
            },
        )

        self.lbchdb.check_yt_content(
            content={
                self.prev_month.path(schemes.PUSH_BY_DEVICE_ID_TABLE_DIR): [],
                self.curr_month.path(schemes.PUSH_BY_DEVICE_ID_TABLE_DIR): [],
                self.next_month.path(schemes.PUSH_BY_DEVICE_ID_TABLE_DIR): [],
            },
        )

    def test_users_history(self):
        self.lbchdb.check_yt_content(
            content={
                self.prev_month.path(schemes.USERS_HISTORY_TABLE_DIR): [],
                self.curr_month.path(schemes.USERS_HISTORY_TABLE_DIR): [],
                self.next_month.path(schemes.USERS_HISTORY_TABLE_DIR): [],
            },
        )

        self.lbchdb.check_yt_content(
            content={
                self.prev_month.path(schemes.CORP_USERS_HISTORY_TABLE_DIR): [],
                self.curr_month.path(schemes.CORP_USERS_HISTORY_TABLE_DIR): [],
                self.next_month.path(schemes.CORP_USERS_HISTORY_TABLE_DIR): [],
            },
        )

    def test_auths(self):
        self.lbchdb.check_yt_content(
            content={
                self.prev_month.path(schemes.AUTHS_TABLE_DIR): [],
                self.curr_month.path(schemes.AUTHS_TABLE_DIR): [],
                self.next_month.path(schemes.AUTHS_TABLE_DIR): [],
            },
        )
