import base64
import json
import jsondiff
import os
import requests
import time

import yt.wrapper

from passport.infra.recipes.common import log

import passport.infra.daemons.lbchdb.ut_medium.common.schemes as schemes

from passport.infra.daemons.historydb_api2.ut.common import (
    HistoryDBApi2Fixture,
    deep_sorted,
    pretty_json,
    reverse_timestamp,
)
from passport.infra.daemons.historydb_api2.ut.push import PushTestFixture

# tvmknife unittest service -s 1000503 -d 1000501
SERVICE_TICKET = '3:serv:CBAQ__________9_IggIt4g9ELWIPQ:Uwax1YvW8a58VIgysUAQ16lEp-vdsdj-yHi8Y9n2hc4NR9Cp2E6g3ThfLHCN0utIfXDnrL7STiOBu74d2k4qKCSmSkUf6Y21tIJK88mRNaOZWBXK_RAcnDg-0g2P6mNfoeHzjyTARCBxF7QpGpxawuu1N4hMHOytKV2ep02fpEw'  # noqa
TICKET_INVALID = 'invalid_ticket'

# tvmknife unittest service -s 1000502 -d 1000501
TICKET_BAD_SRC = '3:serv:CBAQ__________9_IggItog9ELWIPQ:ECCePa8cNRjwL51DvTDYpq5CXti29B1n6nlw6D0Nr_FRcr2y2wh2a6KtxAxmdPI_SG21wQZOWs2ztIQwUpUCdK4DM-VaaigyO_J1MC5vWdnD0l7pZE8h5pcxewZ5JLo0vXNBxOy_tWTl9du80qy2B4R_1MmYyAF1kzWTaOQRM-0'  # noqa

# tvmknife unittest service -s 1000503 -d 1000502
TICKET_BAD_DST = '3:serv:CBAQ__________9_IggIt4g9ELaIPQ:WzXCUWX6LNTvi594Q4CnBirw6VexpATjlvjSFDfq0DwcIWe0CJiVxc8f1xOGQ1_Nkf3mj5L42I1je4t6vhmViTu5UnS8IaG3TZNtFeGpKO3pdvySU_u3un5nEFX2kNqx5yD3X35Um5YBQXtGHzhGu9AY0deCHpdfwJ_FvFarWK0'  # noqa


def prepare_lastauth_table():
    schemes.create_lastauth_table()
    yt.wrapper.insert_rows(
        schemes.LASTAUTH_TABLE_NAME,
        [
            {"uid": 200, "authtype": "web", "timestamp": 1643469310498216},
            {"uid": 300, "authtype": "oauthcheck", "timestamp": 1643468685194514},
            {"uid": 300, "authtype": "oauthcreate", "timestamp": 1643468685018894},
        ],
        atomicity="none",
    )


def prepare_restore_table():
    schemes.create_restore_table()
    yt.wrapper.insert_rows(
        schemes.RESTORE_TABLE_NAME,
        [
            {
                "uid": 129,
                "reversed_timestamp": 9221708175479989317,  # 1663861374.786490
                "data": {
                    "action": "restore_semi_auto_request",
                    "restore_id": "8E,1545,1439452892.13,1130000000036391,3506cd38f02aa5c0aab307fd3f42f4510a",
                    "data_json": {
                        "v": 1,
                        "keyid": 1,
                        "iv": base64.b64decode("XicaYk6VkP+oAfMo"),
                        # {"key":"value","other":{"key":"other value"}}"
                        "text": base64.b64decode("iXAL8FWDYmyhc4CLAyv6uEEFhdRnFPWJs5fOs7IoQwqVXaNp9O3/QS8RrLJSXg=="),
                        "tag": base64.b64decode("ejeoO+hRTJqb/QVm+lzCYA=="),
                    },
                },
            },
            {
                "uid": 100500,
                "reversed_timestamp": 9221632402667989305,  # 1739634186.786502
                "data": {
                    "action": "some_action",
                    "restore_id": "7E,18088,1425562596.0,3000386169,7fee24744865b7c278e26b160f7d3ed07e",
                    "data_json": {
                        "v": 1,
                        "keyid": 1,
                        "iv": base64.b64decode("iH+Z2iiFuBs4KaeK"),
                        # {"key":"value","other":{"key":"other value"}}"
                        "text": base64.b64decode(
                            "89D9FuKIwuM/lLxCS9lwD/a7ZozU78Qt4VSQTCgJpMcxb+FzgIhUasdeAe4PiJCDSCuWNXVMjfXu"
                        ),
                        "tag": base64.b64decode("Zve4NpuFiu/WhbFjBBdROw=="),
                        "size": 46,
                        "codec": "gzip",
                    },
                },
            },
            {
                "uid": 100500,
                "reversed_timestamp": 9221632422667989305,  # 1739614186.786502
                "data": {
                    "action": "blah",
                    "restore_id": "kek",
                    "data_json": {
                        "v": 1,
                        "keyid": 1,
                        "iv": base64.b64decode("DAXjkmuIFkvWMkoL"),
                        "text": base64.b64decode("Qsi29HknMQcLVJ/zy8B0Ig=="),  # {"some":"data"}"
                        "tag": base64.b64decode("F8WBIioQDpp9dTXBbVJ5Mg=="),
                    },
                },
            },
        ],
        atomicity="none",
    )


def prepare_push_subscription_table(now=time.time()):
    now = int(now)

    schemes.create_push_subscription_table()
    yt.wrapper.insert_rows(
        schemes.PUSH_SUBSCRIPTION_TABLE,
        [
            {"uid": 214062827, "app_id": "kek", "device_id": "a", "timestamp": now, "count": 1},
            {"uid": 214062827, "app_id": "kek", "device_id": "b", "timestamp": now - 86400, "count": 2},
            {"uid": 214062827, "app_id": "kek", "device_id": "c", "timestamp": now - 2 * 86400, "count": 3},
            {"uid": 214062827, "app_id": "kek", "device_id": "d", "timestamp": now - 3 * 86400, "count": 4},
            {"uid": 214062827, "app_id": "kek", "device_id": "e", "timestamp": now - 4 * 86400, "count": 5},
            {"uid": 214062827, "app_id": "kek", "device_id": "lol", "timestamp": now - 5 * 86400, "count": 6},
            {"uid": 214062827, "app_id": "kek", "device_id": "lol", "timestamp": now - 6 * 86400, "count": 7},
            {"uid": 214062826, "app_id": "kek", "device_id": "lol", "timestamp": now, "count": 7},
        ],
        atomicity="none",
    )


class TestHistoryDBApi2:
    @classmethod
    def setup_class(cls):
        os.environ['TZ'] = 'Europe/Moscow'
        time.tzset()

        log('Starting HistoryDBApi2 test')

        cls.start_time = time.time()
        cls.curr_month = schemes.MonthlyTable(cls.start_time)
        cls.prev_month = cls.curr_month.prev()
        cls.next_month = cls.curr_month.next()

        cls.prepare_yt_tables()

        cls.hdbapi2 = HistoryDBApi2Fixture(os.environ["YT_PROXY"], auths_yt_threshold=cls.prev_month.ts() + 1)

    @classmethod
    def teardown_class(cls):
        log('Closing HistoryDBApi2 test')
        cls.hdbapi2.stop()

    @classmethod
    def prepare_yt_tables(cls):
        schemes.create_users_history_tables()
        schemes.create_sendr_table()

        cls.push = PushTestFixture()
        cls.prepare_auths_tables()
        cls.prepare_failed_auths_table()
        prepare_lastauth_table()
        prepare_restore_table()
        prepare_push_subscription_table()
        cls.prepare_yasms_sms_history_tables()

    def test_ping(self):
        url = 'http://127.0.0.1:%d/ping' % self.hdbapi2.http_port

        res = requests.get(url)
        assert res.status_code == 200, res.text
        assert res.text == "Pong"

    @staticmethod
    def check_tvm_grants(url, grant, is_tvm_required=True):
        res = requests.get(url)
        assert res.status_code == 403
        assert "Access denied for ip: 127.0.0.1" in res.text
        assert "missing 'consumer' in request" in res.text

        res = requests.get(url, params={"consumer": "localhost"})
        if is_tvm_required:
            assert res.status_code == 403, res.text
            assert "consumer 'localhost' is not allowed (TVM required)" in res.text
        else:
            assert res.status_code == 200, res.text

        res = requests.get(url, params={"consumer": "with_tvm"})
        assert res.status_code == 403
        assert "Access denied for ip: 127.0.0.1" in res.text
        assert "missing service ticket" in res.text

        res = requests.get(url, params={"consumer": "with_tvm"}, headers={"X-Ya-Service-Ticket": TICKET_INVALID})
        assert res.status_code == 403
        assert "Access denied for ip: 127.0.0.1" in res.text
        assert "service ticket is invalid" in res.text

        res = requests.get(url, params={"consumer": "with_tvm"}, headers={"X-Ya-Service-Ticket": TICKET_BAD_SRC})
        assert res.status_code == 403
        assert "Access denied for ip: 127.0.0.1" in res.text
        assert "service ticket from client_id 1000502 does not match consumer with_tvm" in res.text

        res = requests.get(url, params={"consumer": "with_tvm"}, headers={"X-Ya-Service-Ticket": TICKET_BAD_DST})
        assert res.status_code == 403
        assert "Access denied for ip: 127.0.0.1" in res.text
        assert "service ticket is invalid" in res.text
        assert "expected dst is 1000501" in res.text

        consumer_wo_grant = "wo_grants"
        if is_tvm_required:
            consumer_wo_grant = "wo_grants_with_tvm"
        res = requests.get(url, params={"consumer": consumer_wo_grant}, headers={"X-Ya-Service-Ticket": SERVICE_TICKET})
        assert "Access denied for ip: 127.0.0.1" in res.text
        assert "consumer '%s' missing required grant: %s" % (consumer_wo_grant, grant) in res.text

        res = requests.get(url, params={"consumer": "with_tvm"}, headers={"X-Ya-Service-Ticket": SERVICE_TICKET})
        assert res.status_code == 200

    @staticmethod
    def check_json_response(url, params, expected_resp, expected_code=200, sorted=False, preproc=lambda x: x):
        res = requests.get(
            url, params={"consumer": "with_tvm", **params}, headers={"X-Ya-Service-Ticket": SERVICE_TICKET}
        )
        assert res.status_code == expected_code, res.text

        actual_resp = preproc(res.json())
        if sorted:
            expected_resp = deep_sorted(expected_resp)
            actual_resp = deep_sorted(actual_resp)
        assert expected_resp == actual_resp, "%s:\nGOT: %s\nEXP: %s\nDIFF: %s\n" % (
            url + '?' + '&'.join((key + '=' + str(value) for key, value in params.items())),
            json.dumps(actual_resp, indent=2),
            json.dumps(expected_resp, indent=2),
            pretty_json(jsondiff.diff(expected_resp, actual_resp, dump=True)),
        )

    @staticmethod
    def check_push_requests(url, reqs, sorted=False):
        for case in reqs:
            TestHistoryDBApi2.check_json_response(
                url,
                case["params"],
                {"status": "ok", "items": case["items"]},
                sorted=sorted,
            )

    @staticmethod
    def check_required_params(url, params):
        for param in params:
            TestHistoryDBApi2.check_json_response(
                url,
                {key: value for key, value in params.items() if key != param},
                {"status": "error", "errors": {param: ["error.required"]}},
            )

    def test_push_by_push_id(self):
        url = 'http://127.0.0.1:%d/push/2/by_push_id/' % self.hdbapi2.http_port

        self.check_tvm_grants(url, "push.base")

        self.check_json_response(url, {}, {"status": "error", "errors": {"push": ["error.required"]}})

        self.check_push_requests(url, self.push.by_push_id_requests(), True)

    def test_push_by_fields(self):
        url = 'http://127.0.0.1:%d/push/2/by_fields/' % self.hdbapi2.http_port

        self.check_tvm_grants(url, "push.base")

        self.check_json_response(
            url,
            {"from_ts": 1, "to_ts": 2},
            {"status": "error", "errors": {"uid/device": ["error.required"]}},
        )
        self.check_json_response(
            url,
            {"uid": "123", "to_ts": 2},
            {"status": "error", "errors": {"from_ts": ["error.required"]}},
        )
        self.check_json_response(
            url,
            {"uid": "123", "from_ts": 2},
            {"status": "error", "errors": {"to_ts": ["error.required"]}},
        )

        self.check_push_requests(url, self.push.by_uid_requests())
        self.check_push_requests(url, self.push.by_device_id_requests())
        self.check_push_requests(url, self.push.by_app_id_requests())

    @classmethod
    def prepare_auths_tables(cls):
        def makeBasicEntry(uid, type, status, ts):
            return {
                "uid": int(uid),
                "reversed_timestamp": reverse_timestamp(ts * 1000000),
                "unique_part": "-",
                "type": str(type),
                "status": str(status),
                "client_name": "bb",
                "data": {},
            }

        schemes.create_auths_tables(3)
        yt.wrapper.insert_rows(
            cls.prev_month.path(schemes.AUTHS_TABLE_DIR),
            [
                {
                    "uid": 100500,
                    "reversed_timestamp": reverse_timestamp(1500000000 * 1000000),
                    "unique_part": "-",
                    "data": {"comment": "entry long before yt threshold"},
                },
                makeBasicEntry(17, "kek", "successful", 1500000000),
                {
                    "uid": 100500,
                    "reversed_timestamp": reverse_timestamp(cls.prev_month.ts() * 1000000 + 999999),
                    "unique_part": "-",
                    "data": {"comment": "entry on yt threshold"},
                },
                makeBasicEntry(17, "kek", "successful", cls.prev_month.ts() + 10799),
                {
                    "uid": 100500,
                    "reversed_timestamp": reverse_timestamp(cls.prev_month.ts() * 1000000 + 1000000),
                    "unique_part": "-",
                    "type": "oauthcreate",
                    "status": "successful",
                    "client_name": "bb",
                    "data": {},
                },
                makeBasicEntry(17, "kek", "successful", cls.prev_month.ts() + 10800),
                makeBasicEntry(17, "web", "successful", cls.curr_month.ts() + 10900),
                makeBasicEntry(17, "web", "lol", cls.curr_month.ts() + 11000),
                makeBasicEntry(17, "kek", "lol", cls.curr_month.ts() + 11100),
                makeBasicEntry(17, "kek", "successful", cls.curr_month.ts() - 100),
            ],
            atomicity="none",
        )
        yt.wrapper.insert_rows(
            cls.curr_month.path(schemes.AUTHS_TABLE_DIR),
            [
                {
                    "uid": 100500,
                    "reversed_timestamp": reverse_timestamp(cls.curr_month.ts() * 1000000 + 10111111),
                    "unique_part": "-",
                    "type": "oauthcheck",
                    "status": "successful",
                    "client_name": "bb",
                    "data": {},
                },
                {
                    "uid": 129,
                    "reversed_timestamp": reverse_timestamp(cls.curr_month.ts() * 1000000 + 20222222),
                    "unique_part": "136",
                    "type": "web",
                    "status": "ses_update",
                    "client_name": "passport",
                    "data": {
                        "host_id": "136",
                        "login": "kek@lol.ru",
                        "sid": "951",
                        "yandexuid": "4793281479032874",
                        "comment": "full entry",
                        "user_ip": "5.45.203.81",
                        "ip.geoid": "666",
                        "ip.as_list": "AS7152",
                        "ip.is_yandex": "1",
                        "browser.name": "YandexBrowser",
                        "browser.version": "21.11.3.954",
                        "os.name": "Windows",
                        "os.family": "Linux",
                        "os.version": "MacOS",
                    },
                },
                makeBasicEntry(17, "kek", "ses_create", cls.curr_month.ts() + 100),
                makeBasicEntry(17, "kek", "ses_update", cls.curr_month.ts() + 200),
                makeBasicEntry(17, "kek", "successful", cls.curr_month.ts() + 300),
            ],
            atomicity="none",
        )

    def test_auths(self):
        url = 'http://127.0.0.1:%d/2/auths/' % self.hdbapi2.http_port

        self.check_tvm_grants(url, "account.auths", is_tvm_required=False)
        self.check_required_params(url, {"uid": 1, "from_ts": 1539614186, "to_ts": 1839614186})

        from_oldapi_100500 = {
            "timestamp": 1555555555.555555,
            "type": "web",
            "status": "failed",
            "client_name": "bb",
        }
        oauthcreate_100500 = {
            "timestamp": self.prev_month.ts() + 1.0,
            "type": "oauthcreate",
            "status": "successful",
            "client_name": "bb",
        }
        oauthcheck_100500 = {
            "timestamp": self.curr_month.ts() + 10.111111,
            "type": "oauthcheck",
            "status": "successful",
            "client_name": "bb",
        }
        web_ses_update_129 = {
            "timestamp": self.curr_month.ts() + 20.222222,
            "type": "web",
            "status": "ses_update",
            "client_name": "passport",
            "host_id": "136",
            "login": "kek@lol.ru",
            "sid": "951",
            "yandexuid": "4793281479032874",
            "comment": "full entry",
            "user_ip": "5.45.203.81",
            "ip.geoid": "666",
            "ip.as_list": "AS7152",
            "ip.is_yandex": "1",
            "browser.name": "YandexBrowser",
            "browser.version": "21.11.3.954",
            "os.name": "Windows",
            "os.family": "Linux",
            "os.version": "MacOS",
        }

        cases = [
            {
                "params": {"uid": 1, "from_ts": 0, "to_ts": 20000000000},
                "auths": [],
            },
            {
                "params": {"uid": 129, "from_ts": 0, "to_ts": 20000000000},
                "auths": [web_ses_update_129],
            },
            {
                "params": {
                    "uid": 129,
                    "from_ts": 0,
                    "to_ts": 20000000000,
                    "type": "web,oauth",
                    "status": "failed,ses_update",
                    "client_name": "bb,passport",
                },
                "auths": [web_ses_update_129],
            },
            {
                "params": {
                    "uid": 129,
                    "from_ts": 0,
                    "to_ts": 20000000000,
                    "type": "oauth",
                    "status": "failed,ses_update",
                    "client_name": "bb,passport",
                },
                "auths": [],
            },
            {
                "params": {
                    "uid": 129,
                    "from_ts": 0,
                    "to_ts": 20000000000,
                    "type": "web,oauth",
                    "status": "failed",
                    "client_name": "bb,passport",
                },
                "auths": [],
            },
            {
                "params": {
                    "uid": 129,
                    "from_ts": 0,
                    "to_ts": 20000000000,
                    "type": "web,oauth",
                    "status": "failed,ses_update",
                    "client_name": "bb",
                },
                "auths": [],
            },
            {
                "params": {"uid": 100500, "from_ts": 0, "to_ts": 20000000000},
                "auths": [oauthcheck_100500, oauthcreate_100500, from_oldapi_100500],
            },
            {
                "params": {"uid": 100500, "from_ts": 0, "to_ts": 20000000000, "order_by": "asc"},
                "auths": [from_oldapi_100500, oauthcreate_100500, oauthcheck_100500],
            },
            {
                "params": {"uid": 100500, "from_ts": 0, "to_ts": 20000000000, "limit": 1},
                "auths": [oauthcheck_100500],
            },
            {
                "params": {"uid": 100500, "from_ts": 0, "to_ts": 20000000000, "order_by": "asc", "limit": 1},
                "auths": [oauthcheck_100500],
            },
            {
                "params": {"uid": 100500, "from_ts": 0, "to_ts": self.curr_month.ts()},
                "auths": [oauthcreate_100500, from_oldapi_100500],
            },
            {
                "params": {"uid": 100500, "from_ts": self.curr_month.ts(), "to_ts": 20000000000},
                "auths": [oauthcheck_100500],
            },
        ]

        for testcase in cases:
            self.check_json_response(
                url,
                testcase["params"],
                {
                    "status": "ok",
                    "uid": testcase["params"]["uid"],
                    "auths": testcase["auths"],
                },
            )

    def test_auths_aggregated_runtime(self):
        url = 'http://127.0.0.1:%d/2/auths/aggregated/runtime/' % self.hdbapi2.http_port

        self.check_tvm_grants(url, "account.auths", is_tvm_required=False)
        self.check_required_params(url, {"uid": 1, "from_ts": 1539614186, "to_ts": 1839614186})

        def makeBasicEntry(type, status):
            return {
                "authtype": type,
                "status": status,
                "browser": {},
                "ip": {},
                "os": {},
            }

        hbaseEntry = {
            "timestamp": 1555545600,
            "auths": [
                {"count": 666, "auth": makeBasicEntry("hbase", "successful")},
            ],
        }

        cases = [
            {
                "params": {"uid": 1, "from_ts": 0, "to_ts": 20000000000},
                "history": (),
            },
            {
                "params": {"uid": 129, "from_ts": 0, "to_ts": 20000000000},
                "history": (
                    {
                        "timestamp": self.curr_month.ts() - 75600,
                        "auths": [
                            {
                                "count": 1,
                                "auth": {
                                    "authtype": "web",
                                    "status": "ses_update",
                                    "browser": {
                                        "name": "YandexBrowser",
                                        "version": "21.11.3.954",
                                        "yandexuid": "4793281479032874",
                                    },
                                    "ip": {
                                        "AS": 7152,
                                        "geoid": 666,
                                        "ip": "5.45.203.81",
                                    },
                                    "os": {
                                        "name": "Windows",
                                        "version": "MacOS",
                                    },
                                },
                            },
                        ],
                    },
                ),
            },
            {
                "params": {"uid": 17, "from_ts": 0, "to_ts": 20000000000},
                "history": (
                    {
                        "timestamp": self.curr_month.ts() - 75600,
                        "auths": [
                            {"count": 2, "auth": makeBasicEntry("kek", "successful")},
                            {"count": 1, "auth": makeBasicEntry("kek", "ses_create")},
                            {"count": 1, "auth": makeBasicEntry("kek", "ses_update")},
                        ],
                    },
                    {
                        "timestamp": self.prev_month.ts() + 10800,
                        "auths": [
                            {"count": 1, "auth": makeBasicEntry("kek", "successful")},
                        ],
                    },
                    hbaseEntry,
                ),
            },
            {
                "params": {"uid": 17, "from_ts": 0, "to_ts": 20000000000, "limit": 2},
                "history": (
                    {
                        "timestamp": self.curr_month.ts() - 75600,
                        "auths": [
                            {"count": 1, "auth": makeBasicEntry("kek", "successful")},
                            {"count": 1, "auth": makeBasicEntry("kek", "ses_update")},
                        ],
                    },
                    hbaseEntry,
                ),
            },
            {
                "params": {"uid": 17, "from_ts": 0, "to_ts": self.curr_month.ts()},
                "history": (
                    {
                        "timestamp": self.curr_month.ts() - 75600,
                        "auths": [
                            {"count": 1, "auth": makeBasicEntry("kek", "successful")},
                        ],
                    },
                    {
                        "timestamp": self.prev_month.ts() + 10800,
                        "auths": [
                            {"count": 1, "auth": makeBasicEntry("kek", "successful")},
                        ],
                    },
                    hbaseEntry,
                ),
            },
            {
                "params": {"uid": 17, "from_ts": self.curr_month.ts(), "to_ts": 20000000000},
                "history": (
                    {
                        "timestamp": self.curr_month.ts() - 75600,
                        "auths": [
                            {"count": 1, "auth": makeBasicEntry("kek", "successful")},
                            {"count": 1, "auth": makeBasicEntry("kek", "ses_create")},
                            {"count": 1, "auth": makeBasicEntry("kek", "ses_update")},
                        ],
                    },
                ),
            },
        ]

        def preproc(res_json):
            res_json["history"] = tuple(res_json["history"])
            return res_json

        for testcase in cases:
            self.check_json_response(
                url,
                testcase["params"],
                {
                    "status": "ok",
                    "uid": testcase["params"]["uid"],
                    "history": testcase["history"],
                },
                sorted=True,
                preproc=preproc,
            )

    @classmethod
    def prepare_failed_auths_table(cls):
        schemes.create_auths_tables(failed=True)
        yt.wrapper.insert_rows(
            schemes.FAILED_AUTHS_TABLE_NAME,
            [
                {
                    "uid": 100500,
                    "reversed_timestamp": reverse_timestamp(1600000000 * 1000000),
                    "unique_part": "-",
                    "type": "web",
                    "status": "failed",
                    "client_name": "bb",
                    "data": {},
                },
                {
                    "uid": 100500,
                    "reversed_timestamp": reverse_timestamp(1600000010 * 1000000 + 111111),
                    "unique_part": "-",
                    "type": "imap",
                    "status": "blocked",
                    "client_name": "bb",
                    "data": {},
                },
                {
                    "uid": 129,
                    "reversed_timestamp": reverse_timestamp(1600000020 * 1000000 + 222222),
                    "unique_part": "136",
                    "type": "web",
                    "status": "failed",
                    "client_name": "passport",
                    "data": {
                        "host_id": "136",
                        "login": "kek@lol.ru",
                        "sid": "951",
                        "yandexuid": "4793281479032874",
                        "comment": "full entry",
                        "user_ip": "5.45.203.81",
                        "ip.geoid": "666",
                        "ip.as_list": "AS7152",
                        "ip.is_yandex": "1",
                        "browser.name": "YandexBrowser",
                        "browser.version": "21.11.3.954",
                        "os.name": "Windows",
                        "os.family": "Linux",
                        "os.version": "MacOS",
                    },
                },
            ],
            atomicity="none",
        )

    def test_failed_auths(self):
        url = 'http://127.0.0.1:%d/2/auths/failed/' % self.hdbapi2.http_port

        self.check_tvm_grants(url, "account.auths", is_tvm_required=False)
        self.check_required_params(url, {"uid": 1, "from_ts": 1539614186, "to_ts": 1839614186})

        web_failed_100500 = {
            "timestamp": 1600000000.0,
            "type": "web",
            "status": "failed",
            "client_name": "bb",
        }
        imap_blocked_100500 = {
            "timestamp": 1600000010.111111,
            "type": "imap",
            "status": "blocked",
            "client_name": "bb",
        }
        web_failed_129 = {
            "timestamp": 1600000020.222222,
            "type": "web",
            "status": "failed",
            "client_name": "passport",
            "host_id": "136",
            "login": "kek@lol.ru",
            "sid": "951",
            "yandexuid": "4793281479032874",
            "comment": "full entry",
            "user_ip": "5.45.203.81",
            "ip.geoid": "666",
            "ip.as_list": "AS7152",
            "ip.is_yandex": "1",
            "browser.name": "YandexBrowser",
            "browser.version": "21.11.3.954",
            "os.name": "Windows",
            "os.family": "Linux",
            "os.version": "MacOS",
        }

        cases = [
            {
                "params": {"uid": 1, "from_ts": 0, "to_ts": 20000000000},
                "auths": [],
            },
            {
                "params": {"uid": 129, "from_ts": 0, "to_ts": 20000000000},
                "auths": [web_failed_129],
            },
            {
                "params": {
                    "uid": 129,
                    "from_ts": 0,
                    "to_ts": 20000000000,
                    "type": "web,oauth",
                    "status": "failed,ses_check",
                    "client_name": "bb,passport",
                },
                "auths": [web_failed_129],
            },
            {
                "params": {
                    "uid": 129,
                    "from_ts": 0,
                    "to_ts": 20000000000,
                    "type": "oauth",
                    "status": "failed,ses_check",
                    "client_name": "bb,passport",
                },
                "auths": [],
            },
            {
                "params": {
                    "uid": 129,
                    "from_ts": 0,
                    "to_ts": 20000000000,
                    "type": "web,oauth",
                    "status": "ses_check",
                    "client_name": "bb,passport",
                },
                "auths": [],
            },
            {
                "params": {
                    "uid": 129,
                    "from_ts": 0,
                    "to_ts": 20000000000,
                    "type": "web,oauth",
                    "status": "failed,ses_check",
                    "client_name": "bb",
                },
                "auths": [],
            },
            {
                "params": {"uid": 100500, "from_ts": 0, "to_ts": 20000000000},
                "auths": [imap_blocked_100500, web_failed_100500],
            },
            {
                "params": {"uid": 100500, "from_ts": 0, "to_ts": 20000000000, "order_by": "asc"},
                "auths": [web_failed_100500, imap_blocked_100500],
            },
            {
                "params": {"uid": 100500, "from_ts": 0, "to_ts": 20000000000, "limit": 1},
                "auths": [imap_blocked_100500],
            },
            {
                "params": {"uid": 100500, "from_ts": 0, "to_ts": 20000000000, "order_by": "asc", "limit": 1},
                "auths": [imap_blocked_100500],
            },
            {
                "params": {"uid": 100500, "from_ts": 0, "to_ts": 1600000000},
                "auths": [],
            },
            {
                "params": {"uid": 100500, "from_ts": 1600000000, "to_ts": 20000000000},
                "auths": [imap_blocked_100500, web_failed_100500],
            },
        ]

        for testcase in cases:
            self.check_json_response(
                url,
                testcase["params"],
                {
                    "status": "ok",
                    "uid": testcase["params"]["uid"],
                    "auths": testcase["auths"],
                },
            )

    def test_lastauth(self):
        url = 'http://127.0.0.1:%d/2/lastauth/' % self.hdbapi2.http_port

        self.check_tvm_grants(url, "account.lastauth", is_tvm_required=False)

        self.check_json_response(
            url,
            {},
            {"status": "error", "errors": {"uid": ["error.required"]}},
        )
        self.check_json_response(
            url,
            {"uid": "100"},
            {"status": "ok", "uid": 100, "lastauth": {}},
        )
        self.check_json_response(
            url,
            {"uid": "200"},
            {"status": "ok", "uid": 200, "lastauth": {"timestamp": 1643469310.498216, "type": "web"}},
        )
        self.check_json_response(
            url,
            {"uid": "300"},
            {"status": "ok", "uid": 300, "lastauth": {"timestamp": 1643468685.194514, "type": "oauthcheck"}},
        )

    def test_lastauth_bulk(self):
        url = 'http://127.0.0.1:%d/2/lastauth/bulk/' % self.hdbapi2.http_port

        self.check_tvm_grants(url, "account.lastauth", is_tvm_required=False)

        self.check_json_response(
            url,
            {"uids": "100,2oo,300"},
            {"status": "error", "errors": {"uids": ["error.number"]}},
        )
        self.check_json_response(
            url,
            {},
            {"status": "ok", "lastauth": {}},
        )
        self.check_json_response(
            url,
            {"uids": "100"},
            {"status": "ok", "lastauth": {"100": {}}},
        )
        self.check_json_response(
            url,
            {"uids": "200"},
            {"status": "ok", "lastauth": {"200": {"timestamp": 1643469310.498216}}},
        )
        self.check_json_response(
            url,
            {"uids": "300"},
            {"status": "ok", "lastauth": {"300": {"timestamp": 1643468685.194514}}},
        )
        self.check_json_response(
            url,
            {"uids": "200,100,300"},
            {
                "status": "ok",
                "lastauth": {
                    "100": {},
                    "200": {"timestamp": 1643469310.498216},
                    "300": {"timestamp": 1643468685.194514},
                },
            },
        )

    def test_events_restore(self):
        url = 'http://127.0.0.1:%d/2/events/restore/' % self.hdbapi2.http_port

        self.check_tvm_grants(url, "account.events", is_tvm_required=False)

        self.check_json_response(
            url,
            {"from_ts": 1539614186, "to_ts": 1839614186},
            {"status": "error", "errors": {"uid": ["error.required"]}},
        )
        self.check_json_response(
            url,
            {"uid": 1, "to_ts": 1839614186},
            {"status": "error", "errors": {"from_ts": ["error.required"]}},
        )
        self.check_json_response(
            url,
            {"uid": 1, "from_ts": 1539614186},
            {"status": "error", "errors": {"to_ts": ["error.required"]}},
        )
        self.check_json_response(
            url,
            {"uid": 1, "from_ts": 1539614186, "to_ts": 1839614186, "order_by": "invalid"},
            {"status": "error", "errors": {"order_by": ["error.unknown"]}},
        )

        event_129 = {
            "action": "restore_semi_auto_request",
            "restore_id": "8E,1545,1439452892.13,1130000000036391,3506cd38f02aa5c0aab307fd3f42f4510a",
            "timestamp": 1663861374.786490,
            "data_json": '{"key":"value","other":{"key":"other value"}}"',
        }
        event_100500_first = {
            "action": "blah",
            "restore_id": "kek",
            "timestamp": 1739614186.786502,
            "data_json": '{"some":"data"}"',
        }
        event_100500_last = {
            "action": "some_action",
            "restore_id": "7E,18088,1425562596.0,3000386169,7fee24744865b7c278e26b160f7d3ed07e",
            "timestamp": 1739634186.786502,
            "data_json": '{"key":"value","other":{"key":"other value"}}"',
        }

        cases = [
            {
                "params": {"uid": 1, "from_ts": 1539614186, "to_ts": 1839614186},
                "events": [],
            },
            {
                "params": {"uid": 129, "from_ts": 1539614186, "to_ts": 1839614186},
                "events": [event_129],
            },
            {
                "params": {"uid": 100500, "from_ts": 1539614186, "to_ts": 1839614186},
                "events": [event_100500_last, event_100500_first],
            },
            {
                "params": {"uid": 100500, "from_ts": 1539614186, "to_ts": 1839614186, "order_by": "asc"},
                "events": [event_100500_first, event_100500_last],
            },
            {
                "params": {"uid": 100500, "from_ts": 1539614186, "to_ts": 1839614186, "limit": 1},
                "events": [event_100500_last],
            },
            {
                "params": {"uid": 100500, "from_ts": 1539614186, "to_ts": 1839614186, "order_by": "asc", "limit": 1},
                "events": [event_100500_last],
            },
            {
                "params": {"uid": 100500, "from_ts": 1739630000, "to_ts": 1839614186},
                "events": [event_100500_last],
            },
        ]

        for testcase in cases:
            self.check_json_response(
                url,
                testcase["params"],
                {
                    "status": "ok",
                    "uid": testcase["params"]["uid"],
                    "restore_events": testcase["events"],
                },
            )

    def test_push_subscription(self):
        url = 'http://127.0.0.1:%d/push_subscription/2/actual/' % self.hdbapi2.http_port

        self.check_tvm_grants(url, "push_subscription.base", is_tvm_required=True)

        self.check_json_response(
            url,
            {},
            {"status": "error", "errors": {"uid": ["error.required"]}},
        )

        cases = [
            {
                "params": {"uid": 100},
                "items": [],
            },
            {
                "params": {"uid": 214062826},
                "items": [
                    {"app_id": "kek", "device_id": "lol", "count": 7},
                ],
            },
            {
                "params": {"uid": 214062827},
                "items": [
                    {'app_id': 'kek', 'device_id': 'lol', 'count': 13},
                    {'app_id': 'kek', 'device_id': 'e', 'count': 5},
                    {'app_id': 'kek', 'device_id': 'd', 'count': 4},
                    {'app_id': 'kek', 'device_id': 'c', 'count': 3},
                    {'app_id': 'kek', 'device_id': 'b', 'count': 2},
                    {'app_id': 'kek', 'device_id': 'a', 'count': 1},
                ],
            },
            {
                "params": {"uid": 214062827, "max_age": 3 * 86400},
                "items": [
                    {'app_id': 'kek', 'device_id': 'd', 'count': 4},
                    {'app_id': 'kek', 'device_id': 'c', 'count': 3},
                    {'app_id': 'kek', 'device_id': 'b', 'count': 2},
                    {'app_id': 'kek', 'device_id': 'a', 'count': 1},
                ],
            },
            {
                "params": {"uid": 214062827, "limit": 3},
                "items": [
                    {'app_id': 'kek', 'device_id': 'lol', 'count': 13},
                    {'app_id': 'kek', 'device_id': 'e', 'count': 5},
                    {'app_id': 'kek', 'device_id': 'd', 'count': 4},
                ],
            },
            {
                "params": {"uid": 214062827, "limit": 3, "max_age": 3 * 86400},
                "items": [
                    {'app_id': 'kek', 'device_id': 'd', 'count': 4},
                    {'app_id': 'kek', 'device_id': 'c', 'count': 3},
                    {'app_id': 'kek', 'device_id': 'b', 'count': 2},
                ],
            },
        ]

        for testcase in cases:
            self.check_json_response(
                url,
                testcase["params"],
                {
                    "status": "ok",
                    "uid": testcase["params"]["uid"],
                    "items": testcase["items"],
                },
            )

    @classmethod
    def prepare_yasms_sms_history_tables(cls):
        schemes.create_yasms_sms_history_tables()
        yt.wrapper.insert_rows(
            schemes.YASMS_SMS_HISTORY_TABLE,
            [
                {
                    "global_sms_id": "222400000327",
                    "action": "enqueued",
                    "unixtime": 1658322222222000,
                    "phone": 88005553535,
                    "uid": 100500,
                    "data": {
                        "encrypted_text": {
                            "v": 1,
                            "keyid": 1,
                            "iv": base64.b64decode("CP+IZLjDqeBq4AyG"),
                            # Some important text.
                            "text": base64.b64decode("IOZ13rRXNTwGnJITTSRAxKq6F38="),
                            "tag": base64.b64decode("A68GBi74ZSMxLGMDTp5rng=="),
                        },
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
                    "unixtime": 1658322333333000,
                    "phone": 88005553535,
                    "uid": 100500,
                },
                {
                    "global_sms_id": "100500",
                    "action": "delivered",
                    "unixtime": 1658322444444000,
                    "phone": 88000790250,
                },
                {
                    "global_sms_id": "222400000328",
                    "action": "enqueued",
                    "unixtime": 1658322555555000,
                    "phone": 88005553535,
                },
            ],
            atomicity="none",
        )

        yt.wrapper.insert_rows(
            schemes.YASMS_SMS_HISTORY_BY_PHONE_TABLE,
            [
                {
                    "phone": 88005553535,
                    "reversed_timestamp": 9221713714632553807,
                    "global_sms_id": "222400000327",
                    "action": "enqueued",
                },
                {
                    "phone": 88005553535,
                    "reversed_timestamp": 9221713714521442807,
                    "global_sms_id": "222400000327",
                    "action": "delivered",
                },
                {
                    "phone": 88000790250,
                    "reversed_timestamp": 9221713714410331807,
                    "global_sms_id": "100500",
                    "action": "delivered",
                },
                {
                    "phone": 88005553535,
                    "reversed_timestamp": 9221713714299220807,
                    "global_sms_id": "222400000328",
                    "action": "enqueued",
                },
            ],
            atomicity="none",
        )

        yt.wrapper.insert_rows(
            schemes.YASMS_SMS_HISTORY_BY_UID_TABLE,
            [
                {
                    "uid": 100500,
                    "reversed_timestamp": 9221713714632553807,
                    "global_sms_id": "222400000327",
                    "action": "enqueued",
                },
                {
                    "uid": 100500,
                    "reversed_timestamp": 9221713714521442807,
                    "global_sms_id": "222400000327",
                    "action": "delivered",
                },
            ],
            atomicity="none",
        )

        cls.yasms_sms_222400000327_enqueued_base = {
            "global_smsid": "222400000327",
            "action": "enqueued",
            "timestamp": 1658322222.222,
        }
        cls.yasms_sms_222400000327_enqueued = {
            **cls.yasms_sms_222400000327_enqueued_base,
            "number": "+88005553535",
            "uid": "100500",
            "text": "Some important text.",
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
        }

        cls.yasms_sms_222400000327_delivered_base = {
            "global_smsid": "222400000327",
            "action": "delivered",
            "timestamp": 1658322333.333,
        }
        cls.yasms_sms_222400000327_delivered = {
            **cls.yasms_sms_222400000327_delivered_base,
            "number": "+88005553535",
            "uid": "100500",
        }

        cls.yasms_sms_100500_delivered_base = {
            "global_smsid": "100500",
            "action": "delivered",
            "timestamp": 1658322444.444,
        }
        cls.yasms_sms_100500_delivered = {
            **cls.yasms_sms_100500_delivered_base,
            "number": "+88000790250",
        }

        cls.yasms_sms_222400000328_enqueued_base = {
            "global_smsid": "222400000328",
            "action": "enqueued",
            "timestamp": 1658322555.555,
        }
        cls.yasms_sms_222400000328_enqueued = {
            **cls.yasms_sms_222400000328_enqueued_base,
            "number": "+88005553535",
        }

    def test_yasms_sms_by_globalid(self):
        url = 'http://127.0.0.1:%d/yasms/2/sms/by_globalid/' % self.hdbapi2.http_port

        self.check_tvm_grants(url, "yasms.sms_history", is_tvm_required=False)
        self.check_required_params(url, {"global_smsid": 1})

        cases = [
            {
                "params": {"global_smsid": "1"},
                "items": [],
            },
            {
                "params": {"global_smsid": "222400000327"},
                "items": [self.yasms_sms_222400000327_delivered, self.yasms_sms_222400000327_enqueued],
            },
            {
                "params": {"global_smsid": "100500"},
                "items": [self.yasms_sms_100500_delivered],
            },
        ]

        for testcase in cases:
            self.check_json_response(
                url,
                testcase["params"],
                {
                    "status": "ok",
                    "global_smsid": testcase["params"]["global_smsid"],
                    "items": testcase["items"],
                },
            )

    def test_yasms_sms_by_phone(self):
        url = 'http://127.0.0.1:%d/yasms/2/sms/by_phone/' % self.hdbapi2.http_port

        self.check_tvm_grants(url, "yasms.sms_history", is_tvm_required=False)
        self.check_required_params(url, {"phone": 1})

        cases = [
            {
                "params": {"phone": "+12345"},
                "items": {},
            },
            {
                "params": {"phone": "88000790250"},
                "items": {
                    "100500": [self.yasms_sms_100500_delivered],
                },
            },
            {
                "params": {"phone": "88005553535"},
                "items": {
                    "222400000327": [self.yasms_sms_222400000327_delivered, self.yasms_sms_222400000327_enqueued],
                    "222400000328": [self.yasms_sms_222400000328_enqueued],
                },
            },
            {
                "params": {"phone": "88005553535", "from_ts": 1658322333},
                "items": {
                    "222400000327": [self.yasms_sms_222400000327_delivered],
                    "222400000328": [self.yasms_sms_222400000328_enqueued],
                },
            },
            {
                "params": {"phone": "88005553535", "to_ts": 1658322333},
                "items": {
                    "222400000327": [self.yasms_sms_222400000327_enqueued],
                },
            },
        ]

        for testcase in cases:
            self.check_json_response(
                url,
                testcase["params"],
                {
                    "status": "ok",
                    "number": testcase["params"]["phone"],
                    "items": testcase["items"],
                },
            )

    def test_yasms_sms_laststatus(self):
        url = 'http://127.0.0.1:%d/yasms/2/sms/laststatus/by_globalid/' % self.hdbapi2.http_port

        self.check_tvm_grants(url, "yasms.sms_laststatus", is_tvm_required=False)
        self.check_required_params(url, {"global_smsid": 1})

        cases = [
            {
                "params": {"global_smsid": "1"},
                "laststatus": None,
            },
            {
                "params": {"global_smsid": "222400000327"},
                "laststatus": self.yasms_sms_222400000327_delivered_base,
            },
            {
                "params": {"global_smsid": "222400000328"},
                "laststatus": self.yasms_sms_222400000328_enqueued_base,
            },
            {
                "params": {"global_smsid": "100500"},
                "laststatus": self.yasms_sms_100500_delivered_base,
            },
        ]

        for testcase in cases:
            self.check_json_response(
                url,
                testcase["params"],
                {
                    "status": "ok",
                    "global_smsid": testcase["params"]["global_smsid"],
                    "laststatus": testcase["laststatus"],
                },
            )
