import datetime
import os
import time

from passport.infra.recipes.common import log

import passport.infra.daemons.lbchdb.ut_medium.common.schemes as schemes
import passport.infra.daemons.lbchdb.ut_medium.logbroker as lb

from passport.infra.daemons.lbchdb.ut_medium.helpers import reverse_timestamp
from passport.infra.daemons.lbchdb.ut_medium.lbchdb import LbchdbFixture


class TestLbchdbBasic:
    lbchdb = None

    start_time = None
    prev_month = None
    curr_month = None
    next_month = None

    @classmethod
    def setup_class(cls):
        os.environ['TZ'] = 'Europe/Moscow'
        time.tzset()

        log('Starting lbchdb basic test')

        cls.start_time = time.time()
        cls.curr_month = schemes.MonthlyTable(cls.start_time)
        cls.prev_month = cls.curr_month.prev()
        cls.next_month = cls.curr_month.next()

        cls.prepare_topics_data()

        schemes.prepare_yt()
        # Создаем таблицы сами, что бы не ждать ~минуту, пока их нагенерирует lbchdb
        schemes.create_push_tables()
        schemes.create_users_history_tables()
        schemes.create_auths_tables()

        cls.lbchdb = LbchdbFixture()

    @classmethod
    def prepare_topics_data(cls):
        logbroker = lb.TestLogbroker()

        logbroker.skip_data_for(LbchdbFixture.logbroker_client_id)

        cls.write_push(logbroker)
        cls.write_push_subscription(logbroker)
        cls.write_users_history(logbroker)
        cls.write_sendr(logbroker)
        cls.write_auth(logbroker)
        cls.write_bb_auth(logbroker)
        cls.write_restore(logbroker)
        cls.write_yasms_private(logbroker)

        logbroker.stop()

    @classmethod
    def teardown_class(cls):
        log('Closing lbchdb basic test')
        cls.lbchdb.stop()

    def test_healthcheck(self):
        self.lbchdb.healthcheck()

    @classmethod
    def write_push(cls, lb_writer):
        def write(timestamp, row):
            lb_writer.write(lb.TopicType.PUSH, row.format(unixtime=timestamp))

        write(
            cls.curr_month.ts() - 1,
            'tskv\tuid=129\tunixtime={unixtime}\tpush_id=push_129\tsubscription_id=sub_129_first'
            + '\tapp_id=app_129\tdevice_id=dev_129'
            + '\tpush_service=foo\tpush_event=bar\tcontext=full row\tstatus=some status\tdetails=some details',
        )
        write(
            cls.curr_month.ts(),
            'tskv\tuid=129\tunixtime={unixtime}\tpush_id=push_129\tsubscription_id=sub_129_second\tcontext=the only data field',
        )
        write(
            cls.curr_month.ts() + 1,
            'tskv\tuid=17\tunixtime={unixtime}\tpush_id=push_17\tsubscription_id=n/a\tapp_id=app_17',
        )
        write(
            cls.curr_month.ts() + 2,
            'tskv\tuid=100500\tunixtime={unixtime}\tpush_id=push_100500\tsubscription_id=n/a\tdevice_id=dev_100500',
        )

    def test_push(self):
        self.lbchdb.check_yt_content(
            content={
                self.prev_month.path(schemes.PUSH_TABLE_DIR): [
                    {
                        "push_id": "push_129",
                        "subscription_id": "sub_129_first",
                        "uid": 129,
                        "device_id": "dev_129",
                        "app_id": "app_129",
                        "unixtime": self.curr_month.ts() - 1,
                        "data": {
                            "details": "some details",
                            "push_service": "foo",
                            "push_event": "bar",
                            "status": "some status",
                            "context": "full row",
                        },
                    },
                ],
                self.curr_month.path(schemes.PUSH_TABLE_DIR): [
                    {
                        "push_id": "push_129",
                        "subscription_id": "sub_129_second",
                        "uid": 129,
                        "device_id": "",
                        "app_id": "",
                        "unixtime": self.curr_month.ts(),
                        "data": {
                            "context": "the only data field",
                        },
                    },
                    {
                        "push_id": "push_17",
                        "subscription_id": "n/a",
                        "uid": 17,
                        "device_id": "",
                        "app_id": "app_17",
                        "unixtime": self.curr_month.ts() + 1,
                        "data": {},
                    },
                    {
                        "push_id": "push_100500",
                        "subscription_id": "n/a",
                        "uid": 100500,
                        "device_id": "dev_100500",
                        "app_id": "",
                        "unixtime": self.curr_month.ts() + 2,
                        "data": {},
                    },
                ],
                self.next_month.path(schemes.PUSH_TABLE_DIR): [],
            },
        )

        self.lbchdb.check_yt_content(
            content={
                self.prev_month.path(schemes.PUSH_BY_UID_TABLE_DIR): [
                    {
                        "uid": 129,
                        "reversed_timestamp": reverse_timestamp(self.curr_month.ts() - 1),
                        "push_id": "push_129",
                        "subscription_id": "sub_129_first",
                        "dummy": None,
                    },
                ],
                self.curr_month.path(schemes.PUSH_BY_UID_TABLE_DIR): [
                    {
                        "uid": 129,
                        "reversed_timestamp": reverse_timestamp(self.curr_month.ts()),
                        "push_id": "push_129",
                        "subscription_id": "sub_129_second",
                        "dummy": None,
                    },
                    {
                        "uid": 17,
                        "reversed_timestamp": reverse_timestamp(self.curr_month.ts() + 1),
                        "push_id": "push_17",
                        "subscription_id": "n/a",
                        "dummy": None,
                    },
                    {
                        "uid": 100500,
                        "reversed_timestamp": reverse_timestamp(self.curr_month.ts() + 2),
                        "push_id": "push_100500",
                        "subscription_id": "n/a",
                        "dummy": None,
                    },
                ],
                self.next_month.path(schemes.PUSH_BY_UID_TABLE_DIR): [],
            },
        )

        self.lbchdb.check_yt_content(
            content={
                self.prev_month.path(schemes.PUSH_BY_APP_ID_TABLE_DIR): [
                    {
                        "uid": 129,
                        "app_id": "app_129",
                        "reversed_timestamp": reverse_timestamp(self.curr_month.ts() - 1),
                        "push_id": "push_129",
                        "subscription_id": "sub_129_first",
                        "dummy": None,
                    },
                ],
                self.curr_month.path(schemes.PUSH_BY_APP_ID_TABLE_DIR): [
                    {
                        "uid": 17,
                        "app_id": "app_17",
                        "reversed_timestamp": reverse_timestamp(self.curr_month.ts() + 1),
                        "push_id": "push_17",
                        "subscription_id": "n/a",
                        "dummy": None,
                    },
                ],
                self.next_month.path(schemes.PUSH_BY_APP_ID_TABLE_DIR): [],
            },
        )

        self.lbchdb.check_yt_content(
            content={
                self.prev_month.path(schemes.PUSH_BY_DEVICE_ID_TABLE_DIR): [
                    {
                        "device_id": "dev_129",
                        "reversed_timestamp": reverse_timestamp(self.curr_month.ts() - 1),
                        "push_id": "push_129",
                        "subscription_id": "sub_129_first",
                        "dummy": None,
                    },
                ],
                self.curr_month.path(schemes.PUSH_BY_DEVICE_ID_TABLE_DIR): [
                    {
                        "device_id": "dev_100500",
                        "reversed_timestamp": reverse_timestamp(self.curr_month.ts() + 2),
                        "push_id": "push_100500",
                        "subscription_id": "n/a",
                        "dummy": None,
                    },
                ],
                self.next_month.path(schemes.PUSH_BY_DEVICE_ID_TABLE_DIR): [],
            },
        )

    @classmethod
    def write_push_subscription(cls, lb_writer):
        def write(row):
            lb_writer.write(lb.TopicType.PUSH_SUBSCRIPTION, row)

        write('tskv\tuid=129\tunixtime=1600000000\tapp_id=app1\tdevice_id=dev1')
        write('tskv\tuid=129\tunixtime=1600003333\tapp_id=app1\tdevice_id=dev1')
        write('tskv\tuid=129\tunixtime=1600006666\tapp_id=app1\tdevice_id=dev1')
        write('tskv\tuid=129\tunixtime=1600010000\tapp_id=app1\tdevice_id=dev1')
        write('tskv\tuid=129\tunixtime=1600005000\tapp_id=app2\tdevice_id=dev1')
        write('tskv\tuid=129\tunixtime=1600005000\tapp_id=app1\tdevice_id=dev2')
        write('tskv\tuid=17\tunixtime=1600005000\tapp_id=app1\tdevice_id=dev1')

    def test_push_subscription(self):
        self.lbchdb.check_yt_content(
            content={
                schemes.PUSH_SUBSCRIPTION_TABLE: [
                    {
                        "uid": 129,
                        "app_id": "app1",
                        "device_id": "dev1",
                        "timestamp": 1600000000,
                        "count": 3,
                    },
                    {
                        "uid": 129,
                        "app_id": "app1",
                        "device_id": "dev1",
                        "timestamp": 1600010000,
                        "count": 1,
                    },
                    {
                        "uid": 129,
                        "app_id": "app2",
                        "device_id": "dev1",
                        "timestamp": 1600000000,
                        "count": 1,
                    },
                    {
                        "uid": 129,
                        "app_id": "app1",
                        "device_id": "dev2",
                        "timestamp": 1600000000,
                        "count": 1,
                    },
                    {
                        "uid": 17,
                        "app_id": "app1",
                        "device_id": "dev1",
                        "timestamp": 1600000000,
                        "count": 1,
                    },
                ],
            },
        )

    users_history_fields_to_store = [
        "abuseType",
        "affected",
        "browser.name",
        "browser.version",
        "condition",
        "destFid",
        "deviceType",
        "emailFrom",
        "fid",
        "filterIds",
        "folder_symbol",
        "ftype",
        "hidden",
        "internetProvider",
        "ip",
        "lids",
        "lidText",
        "mid",
        "msgStatus",
        "operationSystem.name",
        "operationSystem.version",
        "regionId",
        "spam_type",
        "state",
        "target",
        "view_date",
    ]
    all_users_history_fields = {field: field + '_value' for field in users_history_fields_to_store}

    @classmethod
    def write_users_history(cls, lb_writer):
        def write(timestamp, row, **extra_data_fields):
            extra_data_fields = tuple(key + '=' + value for key, value in extra_data_fields.items())
            lb_writer.write(
                lb.TopicType.MAIL_USER_JOURNAL,
                '\t'.join((row.format(timestamp=timestamp * 1000),) + extra_data_fields),
            )

        write(
            cls.curr_month.ts() - 1,
            'tskv\tuid=1291\tdate={timestamp}\tv=2',
        )
        write(
            cls.curr_month.ts() - 1,
            'tskv\tuid=171\tdate={timestamp}\tv=2\ttableName=corp_users_history',
        )
        write(
            cls.curr_month.ts(),
            'tskv\tuid=1292\tdate={timestamp}\tv=2\ttableName=users_history\toperation=registration\tmodule=sharpei'
            + '\tsome_random_field=some_random_value',
            **cls.all_users_history_fields,
        )
        write(
            cls.curr_month.ts(),
            'tskv\tuid=172\tdate={timestamp}\tv=2\ttableName=corp_users_history\toperation=delete\tmodule=mailbox_oper'
            + '\tsome_random_field=some_random_value',
            **cls.all_users_history_fields,
        )
        write(
            cls.curr_month.ts() + 1,
            'tskv\tuid=1293\tdate={timestamp}\tv=2\ttableName=some_random_table_name',
            target='a' * 100,
            state='b' * 101,
        )
        write(
            cls.curr_month.ts() + 1,
            'tskv\tuid=173\tdate={timestamp}\tv=2\ttableName=corp_users_history',
            target='c' * 100,
            state='d' * 101,
        )

    def test_users_history(self):
        self.lbchdb.check_yt_content(
            preproc=self.lbchdb.users_history_preproc(),
            content={
                self.prev_month.path(schemes.USERS_HISTORY_TABLE_DIR): [
                    {
                        "uid": 1291,
                        "reversed_unixtime": reverse_timestamp(self.curr_month.ts() * 1000 - 1000),
                        "operation": "",
                        "module": "",
                        "data": {},
                    },
                ],
                self.curr_month.path(schemes.USERS_HISTORY_TABLE_DIR): [
                    {
                        "uid": 1292,
                        "reversed_unixtime": reverse_timestamp(self.curr_month.ts() * 1000),
                        "operation": "registration",
                        "module": "sharpei",
                        "data": self.all_users_history_fields,
                    },
                    {
                        "uid": 1293,
                        "reversed_unixtime": reverse_timestamp(self.curr_month.ts() * 1000 + 1000),
                        "operation": "",
                        "module": "",
                        "data": {
                            "target": 'a' * 100,
                            "state": 'b' * 101,
                            "_compressed": ["state"],
                        },
                    },
                ],
                self.next_month.path(schemes.USERS_HISTORY_TABLE_DIR): [],
            },
        )

        self.lbchdb.check_yt_content(
            preproc=self.lbchdb.users_history_preproc(),
            content={
                self.prev_month.path(schemes.CORP_USERS_HISTORY_TABLE_DIR): [
                    {
                        "uid": 171,
                        "reversed_unixtime": reverse_timestamp(self.curr_month.ts() * 1000 - 1000),
                        "operation": "",
                        "module": "",
                        "data": {},
                    },
                ],
                self.curr_month.path(schemes.CORP_USERS_HISTORY_TABLE_DIR): [
                    {
                        "uid": 172,
                        "reversed_unixtime": reverse_timestamp(self.curr_month.ts() * 1000),
                        "operation": "delete",
                        "module": "mailbox_oper",
                        "data": self.all_users_history_fields,
                    },
                    {
                        "uid": 173,
                        "reversed_unixtime": reverse_timestamp(self.curr_month.ts() * 1000 + 1000),
                        "operation": "",
                        "module": "",
                        "data": {
                            "target": 'c' * 100,
                            "state": 'd' * 101,
                            "_compressed": ["state"],
                        },
                    },
                ],
                self.next_month.path(schemes.CORP_USERS_HISTORY_TABLE_DIR): [],
            },
        )

    @classmethod
    def write_sendr(cls, lb_writer):
        def write(row):
            lb_writer.write(lb.TopicType.SENDR, row)

        write('tskv\tunixtime=100500\trecepient=vasya@kek.lol\tstatus=something\taccount=nonexisting')
        write('tskv\tunixtime=100500\trecepient=vasya@kek.lol\tstatus=something\taccount=blocked')
        write('tskv\tunixtime=100501\trecepient=vasya@kek.lol\tstatus=0\taccount=afisha')
        write('tskv\tunixtime=100502\trecepient=vasya@kek.lol\tstatus=0\taccount=afisha')
        write('tskv\tunixtime=100503\trecepient=jorik@foo.bar\tstatus=0\taccount=afisha')
        write('tskv\tunixtime=100504\trecepient=jorik@foo.bar\tstatus=0\taccount=kinopoisk')
        write('tskv\tunixtime=100505\trecepient=babushka@balalaika\tstatus=0\taccount=kinopoisk')
        write('tskv\tunixtime=100506\trecepient=vasya@kek.lol\tstatus=0\taccount=kinopoisk')

    def test_sendr(self):
        self.lbchdb.check_yt_content(
            content={
                schemes.SENDR_TABLE_NAME: [
                    {
                        "uid": 129,
                        "unsibscribe_list": 10,
                        "timestamp": 100502,
                    },
                    {
                        "uid": 17,
                        "unsibscribe_list": 10,
                        "timestamp": 100503,
                    },
                    {
                        "uid": 100500,
                        "unsibscribe_list": 10,
                        "timestamp": 100503,
                    },
                    {
                        "uid": 100500,
                        "unsibscribe_list": 42,
                        "timestamp": 100504,
                    },
                    {
                        "uid": 17,
                        "unsibscribe_list": 42,
                        "timestamp": 100505,
                    },
                    {
                        "uid": 666,
                        "unsibscribe_list": 42,
                        "timestamp": 100505,
                    },
                    {
                        "uid": 129,
                        "unsibscribe_list": 42,
                        "timestamp": 100506,
                    },
                ],
            },
        )

    @classmethod
    def write_auth(cls, lb_writer):
        def write(date, row):
            lb_writer.write(
                lb.TopicType.AUTH,
                row.format(time=date.strftime("%Y-%m-%dT%H:%M:%S.%f+03")),
            )

        write(
            cls.prev_month.date() + datetime.timedelta(0, 1, 111111),
            '1 {time} 88 passport 100500 kek@lol.ru 951 web ses_update'
            + ' - 172.31.20.176 5.45.203.81 4793281479032874 - -'
            + ' `Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.85 YaBrowser/21.11.3.954 (beta) Yowser/2.5 Safari/537.36`',
        )

    @classmethod
    def write_bb_auth(cls, lb_writer):
        def write(seconds, row):
            date = cls.curr_month.date() + datetime.timedelta(seconds=seconds)
            lb_writer.write(
                lb.TopicType.BB_AUTH,
                row.format(time=date.strftime("%Y-%m-%dT%H:%M:%S.%f+03")),
            )

        write(-60, '1 {time} 7F bb 129 - - oauthcheck failed tokid=77;context=check_failed_1_1 127.0.0.1 - - - - -')
        write(-50, '1 {time} 7F bb 129 - - oauthcreate successful tokid=77;context=create_ss_1_1 127.0.0.1 - - - - -')
        write(-40, '1 {time} 7F bb 129 - - oauthcheck successful tokid=77;context=check_ss_1_1 127.0.0.1 - - - - -')

        write(-30, '1 {time} 7F bb 129 - - oauthcheck failed tokid=77;context=check_failed_1_2 127.0.0.1 - - - - -')
        write(-20, '1 {time} 7F bb 129 - - oauthcreate successful tokid=77;context=create_ss_1_2 127.0.0.1 - - - - -')
        write(-10, '1 {time} 7F bb 129 - - oauthcheck successful tokid=77;context=check_ss_1_2 127.0.0.1 - - - - -')

        write(10, '1 {time} 7F bb 129 - - oauthcheck successful tokid=77;context=check_ss_2_1 127.0.0.1 - - - - -')
        write(20, '1 {time} 7F bb 129 - - oauthcheck successful tokid=77;context=check_ss_2_2 127.0.0.1 - - - - -')

        write(3600, '1 {time} 7F bb 129 - - oauthcheck successful tokid=77;context=check_ss_3_1 127.0.0.1 - - - - -')
        write(3610, '1 {time} 7F bb 17 - - oauthcheck successful tokid=666;context=check_ss_3_2 127.0.0.1 - - - - -')

    def test_lastauth(self):
        self.lbchdb.check_yt_content(
            content={
                schemes.LASTAUTH_TABLE_NAME: [
                    {
                        "uid": 100500,
                        "authtype": "web",
                        "timestamp": self.prev_month.ts() * 1000000 + 1111111,
                    },
                    {
                        "uid": 129,
                        "authtype": "oauthcheck",
                        "timestamp": (self.curr_month.ts() + 3600) * 1000000,
                    },
                    {
                        "uid": 129,
                        "authtype": "oauthcreate",
                        "timestamp": (self.curr_month.ts() - 20) * 1000000,
                    },
                    {
                        "uid": 17,
                        "authtype": "oauthcheck",
                        "timestamp": (self.curr_month.ts() + 3610) * 1000000,
                    },
                ],
            },
        )

    def test_failed_auths(self):
        self.lbchdb.check_yt_content(
            content={
                schemes.FAILED_AUTHS_TABLE_NAME: [
                    {
                        "uid": 129,
                        "reversed_timestamp": reverse_timestamp((self.curr_month.ts() - 60) * 1000000),
                        "unique_part": "127",
                        "type": "oauthcheck",
                        "status": "failed",
                        "client_name": "bb",
                        "data": {
                            "host_id": "127",
                            "user_ip": "127.0.0.1",
                            "comment": "tokid=77;context=check_failed_1_1",
                        },
                    },
                    {
                        "uid": 129,
                        "reversed_timestamp": reverse_timestamp((self.curr_month.ts() - 30) * 1000000),
                        "unique_part": "127",
                        "type": "oauthcheck",
                        "status": "failed",
                        "client_name": "bb",
                        "data": {
                            "host_id": "127",
                            "user_ip": "127.0.0.1",
                            "comment": "tokid=77;context=check_failed_1_2",
                        },
                    },
                ],
            },
        )

    def test_auths(self):
        self.lbchdb.check_yt_content(
            content={
                self.prev_month.path(schemes.AUTHS_TABLE_DIR): [
                    {
                        "uid": 100500,
                        "reversed_timestamp": reverse_timestamp(self.prev_month.ts() * 1000000 + 1111111),
                        "unique_part": "136",
                        "type": "web",
                        "status": "ses_update",
                        "client_name": "passport",
                        "data": {
                            "host_id": "136",
                            "login": "kek@lol.ru",
                            "sid": "951",
                            "yandexuid": "4793281479032874",
                            "user_ip": "5.45.203.81",
                            "ip.is_yandex": "1",
                            "browser.name": "YandexBrowser",
                            "browser.version": "21.11.3.954",
                            "os.family": "Linux",
                        },
                    },
                    {
                        "uid": 129,
                        "reversed_timestamp": reverse_timestamp((self.curr_month.ts() - 50) * 1000000),
                        "unique_part": "127",
                        "type": "oauthcreate",
                        "status": "successful",
                        "client_name": "bb",
                        "data": {
                            "host_id": "127",
                            "user_ip": "127.0.0.1",
                            "comment": "tokid=77;context=create_ss_1_1",
                        },
                    },
                    {
                        "uid": 129,
                        "reversed_timestamp": reverse_timestamp((self.curr_month.ts() - 40) * 1000000),
                        "unique_part": "oauthcheck/77",
                        "type": "oauthcheck",
                        "status": "successful",
                        "client_name": "bb",
                        "data": {
                            "host_id": "127",
                            "user_ip": "127.0.0.1",
                            "comment": "tokid=77;context=check_ss_1_1",
                        },
                    },
                    {
                        "uid": 129,
                        "reversed_timestamp": reverse_timestamp((self.curr_month.ts() - 20) * 1000000),
                        "unique_part": "127",
                        "type": "oauthcreate",
                        "status": "successful",
                        "client_name": "bb",
                        "data": {
                            "host_id": "127",
                            "user_ip": "127.0.0.1",
                            "comment": "tokid=77;context=create_ss_1_2",
                        },
                    },
                ],
                self.curr_month.path(schemes.AUTHS_TABLE_DIR): [
                    {
                        "uid": 129,
                        "reversed_timestamp": reverse_timestamp((self.curr_month.ts() + 10) * 1000000),
                        "unique_part": "oauthcheck/77",
                        "type": "oauthcheck",
                        "status": "successful",
                        "client_name": "bb",
                        "data": {
                            "host_id": "127",
                            "user_ip": "127.0.0.1",
                            "comment": "tokid=77;context=check_ss_2_1",
                        },
                    },
                    {
                        "uid": 129,
                        "reversed_timestamp": reverse_timestamp((self.curr_month.ts() + 3600) * 1000000),
                        "unique_part": "oauthcheck/77",
                        "type": "oauthcheck",
                        "status": "successful",
                        "client_name": "bb",
                        "data": {
                            "host_id": "127",
                            "user_ip": "127.0.0.1",
                            "comment": "tokid=77;context=check_ss_3_1",
                        },
                    },
                    {
                        "uid": 17,
                        "reversed_timestamp": reverse_timestamp((self.curr_month.ts() + 3610) * 1000000),
                        "unique_part": "oauthcheck/666",
                        "type": "oauthcheck",
                        "status": "successful",
                        "client_name": "bb",
                        "data": {
                            "host_id": "127",
                            "user_ip": "127.0.0.1",
                            "comment": "tokid=666;context=check_ss_3_2",
                        },
                    },
                ],
                self.next_month.path(schemes.AUTHS_TABLE_DIR): [],
            },
        )

    @classmethod
    def write_restore(cls, lb_writer):
        def write(row):
            lb_writer.write(lb.TopicType.RESTORE, row)

        write(
            '2 restore_semi_auto_request_129 2022-07-01T12:34:21.129129+03 129'
            + ' 7E,16680,1418639484.15,3,5c7c2f476e5de0f9556d817aeb82d5757e'
            + ' Y6GG+SB8HCvf/AOT:hweVYqhveYXpVEuRBrio02Kk9IOr5pilkmOhxQ36nl67aWVLcgZZOmd+HK4=:key_number=666:dahgCSlze92XKHZIS5M5zQ==',
        )
        write(
            '2 restore_semi_auto_request_17 2022-07-01T14:45:52.171717+03 17'
            + ' 9,479462,1493830962.23,2000034286,7686633d6931e5130281eeeda55fb9c709'
            + ' ToNPYOfoanP+NuIO:Z2GaP46T2jydCoAyuHNPbjNBbhd5RxtUln4RU9z5tpV9A8RatcGr4/AhwbMX/nWVwUHHtTyS358FyC0MtLX0Q95n7I96+tnLnplOj5rCl6B3/q0Yz0ywRXh4OpXPXYZ0RQE6njU=:key_number=666:0VeEwRsWxsM+FzStitei8Q==',  # noqa
        )

    def test_restore(self):
        self.lbchdb.check_yt_content(
            preproc=self.lbchdb.restore_preproc(),
            content={
                schemes.RESTORE_TABLE_NAME: [
                    {
                        "uid": 129,
                        "reversed_timestamp": 9221715368793646678,
                        "data": {
                            "action": "restore_semi_auto_request_129",
                            "restore_id": "7E,16680,1418639484.15,3,5c7c2f476e5de0f9556d817aeb82d5757e",
                            "data_json": "{\"some\":\"json_data\",\"with\":\"various_fields\"}",
                        },
                    },
                    {
                        "uid": 17,
                        "reversed_timestamp": 9221715360902604090,
                        "data": {
                            "action": "restore_semi_auto_request_17",
                            "restore_id": "9,479462,1493830962.23,2000034286,7686633d6931e5130281eeeda55fb9c709",
                            "data_json": "{\"key\":\"xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx\"}",
                        },
                        "__compressed_fields": ["data_json"],
                    },
                ],
            },
        )

    @classmethod
    def write_yasms_private(cls, lb_writer):
        def write(row):
            lb_writer.write(lb.TopicType.YASMS_PRIVATE, row)

        write('tskv\terror=kek\tsms=1\tunixtimef=1658321111.111\tglobal_smsid=1\taction=enqueued\tnumber=+88005553535')
        write(
            'tskv\ttskv_format=yasms-log\tsms=1\tunixtime=1658322222\tunixtimef=1658322222.222\tuid=100500'
            + '\tglobal_smsid=222400000327\taction=enqueued\tnumber=+88005553535\tmasked_number=+8800555****'
            + '\tencryptedtext=jqDX/Urd4sAEIT3L:iRxW6W573reCQMUBbCcBr2Oj2p2oRNYz0r2qnkIrCoKrK6X2u1xt6/kxJYTjVVQ7zWp+OI4DdSwxAmkA+HqDBIY06yU=:key_number=666:ktKCwzvxMnbVXZNrtXz4FQ=='
            + '\tcaller=\tchars=69\tconsumer_ip=127.0.0.1\tencoding=gsm0338\tgate=666\tidentity=confirm\tlocal_smsid=746831832\trule=some_rule\tsegments=1\tsender=-\tuser_agent=some_user_agent\tuser_ip=127.0.0.1'  # noqa
        )
        write('tskv\tsms=1\tunixtimef=1658323333.333\tglobal_smsid=222400000327\taction=delivered\tnumber=+88005553535')
        write('tskv\tsms=1\tunixtimef=1658324444.444\tglobal_smsid=100500\taction=delivered\tnumber=+88000790250')

    def test_yasms_private(self):
        self.lbchdb.check_yt_content(
            preproc=self.lbchdb.yasms_sms_history_preproc(),
            content={
                schemes.YASMS_SMS_HISTORY_TABLE: [
                    {
                        "global_sms_id": "222400000327",
                        "action": "enqueued",
                        "unixtime": 1658322222222000,
                        "phone": 88005553535,
                        "uid": 100500,
                        "data": {
                            "encrypted_text": "Your confirmation code is 540870. Please enter it in the text field.",
                            "extra": {
                                "chars": "69",
                                "consumer_ip": "127.0.0.1",
                                "encoding": "gsm0338",
                                "gate": "666",
                                "identity": "confirm",
                                "local_smsid": "746831832",
                                "rule": "some_rule",
                                "segments": "1",
                                "user_agent": "some_user_agent",
                                "user_ip": "127.0.0.1",
                                "masked_number": "+8800555****",
                            },
                        },
                    },
                    {
                        "global_sms_id": "222400000327",
                        "action": "delivered",
                        "unixtime": 1658323333333000,
                        "phone": 88005553535,
                        "uid": None,
                        "data": {"extra": {}},
                    },
                    {
                        "global_sms_id": "100500",
                        "action": "delivered",
                        "unixtime": 1658324444444000,
                        "phone": 88000790250,
                        "uid": None,
                        "data": {"extra": {}},
                    },
                ],
            },
        )

        self.lbchdb.check_yt_content(
            content={
                schemes.YASMS_SMS_HISTORY_BY_PHONE_TABLE: [
                    {
                        "phone": 88005553535,
                        "reversed_timestamp": 9221713714632553807,
                        "global_sms_id": "222400000327",
                        "action": "enqueued",
                        "dummy": None,
                    },
                    {
                        "phone": 88005553535,
                        "reversed_timestamp": 9221713713521442807,
                        "global_sms_id": "222400000327",
                        "action": "delivered",
                        "dummy": None,
                    },
                    {
                        "phone": 88000790250,
                        "reversed_timestamp": 9221713712410331807,
                        "global_sms_id": "100500",
                        "action": "delivered",
                        "dummy": None,
                    },
                ],
                schemes.YASMS_SMS_HISTORY_BY_UID_TABLE: [
                    {
                        "uid": 100500,
                        "reversed_timestamp": 9221713714632553807,
                        "global_sms_id": "222400000327",
                        "action": "enqueued",
                        "dummy": None,
                    },
                ],
            },
        )
