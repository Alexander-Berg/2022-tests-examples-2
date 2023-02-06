import os
import time

from passport.infra.recipes.common import log

import passport.infra.daemons.lbcbck.ut_medium.schemes as schemes
import passport.infra.daemons.lbcbck.ut_medium.logbroker as lb

from passport.infra.daemons.lbcbck.ut_medium.lbcbck import LbcbckFixture


class TestLbcbckBasic:
    lbcbck = None

    start_time = None
    prev_day = None
    curr_day = None
    next_day = None

    @classmethod
    def setup_class(cls):
        os.environ['TZ'] = 'Europe/Moscow'
        time.tzset()

        log('Starting lbcbck basic test')

        cls.start_time = time.time()
        cls.curr_day = schemes.DailyTable(cls.start_time)
        cls.prev_day = cls.curr_day.prev()
        cls.next_day = cls.curr_day.next()

        cls.prepare_topics_data()

        schemes.prepare_yt()
        # Создаем таблицы сами, что бы не ждать ~минуту, пока их нагенерирует lbcbck
        schemes.create_tables()

        cls.lbcbck = LbcbckFixture()

    @classmethod
    def prepare_topics_data(cls):
        logbroker = lb.TestLogbroker()

        logbroker.skip_data_for(LbcbckFixture.logbroker_client_id)

        cls.write_blackbox_log(logbroker)
        cls.write_oauth_log(logbroker)

        logbroker.stop()

    @classmethod
    def teardown_class(cls):
        log('Closing lbcbck basic test')
        cls.lbcbck.stop()

    def test_ping(self):
        self.lbcbck.ping()

    @classmethod
    def write_blackbox_log(cls, lb_writer):
        def write(timestamp, row):
            lb_writer.write(lb.TopicType.BLACKBOX_LOG, row.format(unixtime=timestamp))

        write(
            cls.curr_day.ts() - 1,
            "tskv\ttskv_format=blackbox-log\tunixtime={unixtime}\taction=sescheck\tuids=70498,70500\tdef_uid=70500"
            + "\tuserip=95.108.132.35\thost=yandex.ru\treq_id=057b0a02ee3704ba\tauthid=1234567890987:AQAAfw:fe"
            + "\tuser_port=10129\t__consumer=1:passport_dev:2\t__consumer_ip=2a02:6b8:c0e:998:8000:611:0:6",
        )

    @classmethod
    def write_oauth_log(cls, lb_writer):
        def write(timestamp, row):
            lb_writer.write(lb.TopicType.OAUTH_LOG, row.format(unixtime=timestamp))

        write(
            cls.curr_day.ts(),
            "tskv\ttskv_format=oauth-log\tunixtime={unixtime}\tstatus=OK\tuid=70500\tuser_ip=95.108.132.35\tclient_id=5e8656ef62914d738a9865ebf1e999b9"
            + "\treq_id=9589e012ef8e849f\tmode=verify_token\tfull_check=1\tby_alias=0\ttoken_id=163767468312370500\tscopes=test:limited\tcreate_time=2021-11-23 16:38:03\tissue_time=2021-11-23 16:38:03\texpire_time=2021-11-23 17:38:03\tneeds_refresh=0\t__consumer=1:passport_dev:2\t__consumer_ip=2a02:6b8:c0e:998:8000:611:0:6",  # noqa
        )

    def test_tables_content(self):
        self.lbcbck.check_yt_content(
            content={
                self.prev_day.path(schemes.TABLES_DIR): [
                    {
                        "user_ip": "95.108.132.35",
                        "host_client": "yandex.ru",
                        "unixtime": self.curr_day.ts() - 1,
                        "def_uid": 70500,
                        "uids": "70498",
                        "user_port": 10129,
                        "dummy": None,
                    },
                ],
                self.curr_day.path(schemes.TABLES_DIR): [
                    {
                        "user_ip": "95.108.132.35",
                        "host_client": "5e8656ef62914d738a9865ebf1e999b9",
                        "unixtime": self.curr_day.ts(),
                        "def_uid": 70500,
                        "uids": "",
                        "user_port": None,
                        "dummy": None,
                    },
                ],
                self.next_day.path(schemes.TABLES_DIR): [],
            },
        )
