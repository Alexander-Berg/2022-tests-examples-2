import json
import os
import sys

import MySQLdb
import pytest
import requests
import yatest.common as yc

from passport.infra.daemons.yasms_internal.ut.common import (
    YaSMSInternalFixture,
    make_gate_with_id,
    SERVICE_TICKET,
    USER_TICKET,
    AUTH_HEADERS,
)

from passport.infra.recipes.common import log


SERVICE_TICKET_INVALID = 'ticket'

# tvmknife unittest service -s 1000502 -d 1000510
SERVICE_TICKET_BAD_DST = '3:serv:CBAQ__________9_IggItog9EL6IPQ:FLFWEyQsLo3maImzApYL6mZ1KAVU8w6bNp-9hbTrWSN-ezAo90aPQMtUcN7YYrbq9sRkxsS45bUkFeUDFgSpgoYK97PMClUf7zaWvTrWKESeEEtmXc1-L1mROYDEkAc1mtoiUYPaiswGycXPZZtr4G9jTfajn5yRaXI8ySnK3A0'  # noqa

USER_TICKET_INVALID = 'ticket'

SERVICE_TICKETS = {
    "1000503": {
        "body": "3:serv:CBAQ__________9_IggIt4g9ELWIPQ:BuKHASo5RJhtjdAnoGGGPeDT7nMt5aB4Np8rCRVI06w00zD8MD4upoFvo0MzFE9nuyzfRwCrIYZhMY76xBBr0JKK1yOZdGJHXgQ-p4y3UHaDF1QGRxf6jgxyCbHc9G__I_qIrq1muTiiduDKT_w7IIHNyIlBxpebRqINFYxV_i4",  # noqa
        "methods": {},
    },
    "1000504": {
        "body": "3:serv:CBAQ__________9_IggIuIg9ELWIPQ:UVtjVToensNkDo_abls-c6RLg3gebts6veKDSLu7wFrl-_DTvSaJKo3VT11MpxCKqKFZSzrYKR0qNOjbG-kZu4wWgsT2tcvyq00WblYeDWQ7lGVv83_4rITn2Auq1SP9cVtLCCh9SDMZfoH0R0-Z20ZeqtpbmI1A_8wicHoiYJ8",  # noqa
        "methods": {"get": {"/1/routes", "/1/routes/enums"}},
    },
    "1000505": {
        "body": "3:serv:CBAQ__________9_IggIuYg9ELWIPQ:Q1SMdl26lYuCsuQN1jY96rPUNOgZPMHIR7e0Ol4b2_HvB5GDJCAh_oRMokxunS1hxgZCDwCQeIDC85r_3JSsNYnsg0BNftJzvYZoNkxVuXyw0LWMcumzvUDbbkBx8JodYnprxeBrSx8vBSDuRjXEjv0xBWD0EH1JuHxgtnB8rbw",  # noqa
        "methods": {"put": {"/1/gates"}},
    },
    "1000506": {
        "body": "3:serv:CBAQ__________9_IggIuog9ELWIPQ:HydLVH7jlr6VDJdFtffVk5MFDRKtk68nwdUYNwBSWp9HdS1jKNmHtGr_w51hSBwW6yKN_vHGlAydFFXHQr1DyeqrgdCJbxeGvfe-lCaoPzAMKF-WfZZFpWSAFgjR9AOLomLXDm8Zct-Aurnro6pwm8WlyVjBPjWcKWqcu9nAad0",  # noqa
        "methods": {"get": {"/1/service/routes"}},
    },
}
USER_TICKETS = {
    "1120000000000000": {
        "body": "3:user:CAwQ__________9_GhwKCQiAgJiRpdT-ARCAgJiRpdT-ASDShdjMBCgC:KPw-NJL5oHTwdHUp5N2qahXh9cdt4prATq33FJSYwa2X6HjQS1qyAO7NM5i9_kCDQSsYCcFeLghG8sCCqRBy5JdOkys78vUYX2_kLNrfJ2busnbWwtoCY_hn_aYkGzAW_Lf3Adu_Ds3jz5b1tny8lAVKJeM6x0INgvyT4yB51_4",  # noqa
        "methods": {"get": {"/1/user_roles"}},
    },
    "1120000000000002": {
        "body": "3:user:CAwQ__________9_GhwKCQiCgJiRpdT-ARCCgJiRpdT-ASDShdjMBCgC:ErawAVxfN2T6DloviPTDE7UK4pTbW-ULHKz_nf42AmdNdEZ6nisvIjnwibYZ9hi4778-wZbV_m5oZc9SH4i_Hcpc71NIEPzvXQWN1FoskI5HxyVdsucREq9RCjW4ldfiB8RxasyzdSdIfToVZKIfSGBM7OxrCZtg_oH6OKyv9Jg",  # noqa
        "methods": {"get": {"/1/user_roles", "/1/routes", "/1/routes/enums"}},
    },
    "1120000000000003": {
        "body": "3:user:CAwQ__________9_GhwKCQiDgJiRpdT-ARCDgJiRpdT-ASDShdjMBCgC:JN_n51AOp6j6Ma-vDFvLq2zEKlqe_kvgVLH9aSLjZz78ZkP3jIKEkR3PDue_OMhzGr6BkLNx_3Z-KG9eRzqqQ4p3Rt38B_LZV5CYpvwEGYoCnE3f8JOhsUZhokWWXKdZNdsqMgLHy9l75Bhwk4eCsoR9A-LjTUtk5IHZh6RFnts",  # noqa
        "methods": {"get": {"/1/user_roles"}, "put": {"/1/gates"}},
    },
}


class TestYaSMSInternalGeneral:
    yasms = None

    @classmethod
    def setup_class(cls):
        log('Starting YaSMS-internal general test')
        cls.yasms = YaSMSInternalFixture()

    @pytest.fixture(autouse=True)
    def reset_mysql(self):
        self.yasms.reset_mysql()

    @classmethod
    def teardown_class(cls):
        log('Closing YaSMS-internal general test')
        cls.yasms.stop()

    @classmethod
    def check_auth(cls, handle, method='get', with_user_ticket=True):
        def fail_message(message=""):
            return "failed auth check for '%s %s' : %s" % (method, handle, message)

        user_ticket_header = {}
        if with_user_ticket:
            user_ticket_header = {"X-Ya-User-Ticket": USER_TICKET}

        url = "{url}{handle}".format(url=cls.yasms.url, handle=handle)

        r = requests.request(method, url, headers={"X-Ya-Service-Ticket": SERVICE_TICKET, **user_ticket_header})
        assert r.status_code == 200 or r.status_code == 400

        r = requests.request(method, url, headers={**user_ticket_header})
        assert r.status_code == 401
        assert "Service ticket is missing" in r.text, fail_message()

        r = requests.request(method, url, headers={"X-Ya-Service-Ticket": SERVICE_TICKET_INVALID, **user_ticket_header})
        assert r.status_code == 401
        assert "tvm: invalid ticket: Malformed" in r.text, fail_message()

        r = requests.request(method, url, headers={"X-Ya-Service-Ticket": SERVICE_TICKET_BAD_DST, **user_ticket_header})
        assert r.status_code == 401
        assert "tvm: invalid ticket: InvalidDst" in r.text, fail_message()

        for ticket in SERVICE_TICKETS.values():
            r = requests.request(method, url, headers={"X-Ya-Service-Ticket": ticket['body'], **user_ticket_header})
            if handle in ticket['methods'].get(method, set()):
                assert r.status_code == 200 or r.status_code == 400, fail_message(ticket['body'])
            else:
                assert r.status_code == 403, fail_message(ticket['body'])
                assert "Service missing required IDM roles" in r.text, fail_message(ticket['body'])

        if not with_user_ticket:
            return

        r = requests.request(method, url, headers={"X-Ya-Service-Ticket": SERVICE_TICKET})
        assert r.status_code == 401
        assert "User ticket is missing" in r.text, fail_message()

        r = requests.request(
            method, url, headers={"X-Ya-Service-Ticket": SERVICE_TICKET, "X-Ya-User-Ticket": USER_TICKET_INVALID}
        )
        assert r.status_code == 401
        assert "tvm: invalid ticket: Malformed" in r.text, fail_message()

        for ticket in USER_TICKETS.values():
            r = requests.request(
                method, url, headers={"X-Ya-Service-Ticket": SERVICE_TICKET, "X-Ya-User-Ticket": ticket['body']}
            )
            if handle in ticket['methods'].get(method, set()):
                assert r.status_code == 200 or r.status_code == 400, fail_message(ticket['body'])
            else:
                assert r.status_code == 403, fail_message(ticket['body'])
                assert "User missing required IDM roles" in r.text, fail_message(ticket['body'])

    @classmethod
    def print_db_dump_debug(cls):
        db = MySQLdb.connect(host='127.0.0.1', port=cls.yasms.mysql_port, user='root', password='', database='sms')
        c = db.cursor()
        c.execute('select * from sms.smsrt')
        for d in c:
            print(d, file=sys.stderr)

    @classmethod
    def get_audit_log(cls, table_name, id_field):
        return cls.yasms.get_audit_log(table_name, id_field)

    @classmethod
    def check_routes_equal(cls, filename: str):
        response = requests.get(
            '{url}/1/routes?min={min}&limit={limit}'.format(url=cls.yasms.url, min="0", limit=300), headers=AUTH_HEADERS
        )
        assert response.status_code == 200
        cls.compare_json(response, filename)

    @classmethod
    def check_gates_equal(cls, filename: str):
        response = requests.get(
            '{url}/1/gates?min={min}&limit={limit}'.format(url=cls.yasms.url, min="0", limit=300), headers=AUTH_HEADERS
        )
        assert response.status_code == 200
        cls.compare_json(response, filename)

    @classmethod
    def check_fallbacks_equal(cls, filename: str):
        response = requests.get(
            '{url}/1/fallbacks?min={min}&limit={limit}'.format(url=cls.yasms.url, min="0", limit=300),
            headers=AUTH_HEADERS,
        )
        assert response.status_code == 200
        cls.compare_json(response, filename)

    @classmethod
    def check_blocked_phones_equal(cls, filename: str):
        response = requests.get(
            '{url}/1/blockedphones?min={min}&limit={limit}'.format(url=cls.yasms.url, min="0", limit=300),
            headers=AUTH_HEADERS,
        )
        assert response.status_code == 200
        cls.compare_json(response, filename)

    @staticmethod
    def compare_json(response: requests.Response, filename: str):
        actual = json.loads(response.content)

        def recurse_find_ts(data):
            if isinstance(data, list):
                for elem in data:
                    recurse_find_ts(elem)
            elif isinstance(data, dict):
                if 'audit_create' in data and 'audit_modify' in data:
                    data['audit_create']['ts'] = 'TS_HOLDER' if data['audit_create']['ts'] != 0 else 0
                    data['audit_modify']['ts'] = 'TS_HOLDER' if data['audit_modify']['ts'] != 0 else 0
                else:
                    for k, v in data.items():
                        recurse_find_ts(v)

        recurse_find_ts(actual)

        expected = json.load(
            open(os.path.join(yc.source_path('passport/infra/daemons/yasms_internal/ut'), filename), 'r')
        )
        assert actual == expected

    @staticmethod
    def make_gate(i: int):
        return {
            "aliase": "alias-{}".format(i),
            "fromname": "fromname-{}".format(i),
            "contractor": "contractor-{}".format(i),
            "consumer": "consumer-{}".format(i),
            "extra": {
                "extra": "extra-{}".format(i),
            },
        }

    @staticmethod
    def make_gate_with_id(gate_id: str, i: str):
        return make_gate_with_id(gate_id, i)

    def test_ping(self):
        url = '{url}/ping'.format(url=self.yasms.url)
        r = requests.get(url)
        assert r.status_code == 200
        assert r.text == ""

    def test_healthcheck(self):
        url = '{url}/healthcheck'.format(url=self.yasms.url)
        r = requests.get(url)
        assert r.status_code == 200
        assert r.text == "0;OK"

    def test_get_user_roles(self):
        url = '{url}/1/user_roles'.format(url=self.yasms.url)

        def check(uid, roles, ticket=None):
            if ticket is None:
                ticket = USER_TICKETS["%d" % uid]["body"]
            r = requests.get(url, headers={"X-Ya-Service-Ticket": SERVICE_TICKET, "X-Ya-User-Ticket": ticket})
            assert r.status_code == 200, r.text
            assert r.json() == {
                "uid": uid,
                "roles": roles,
            }

        check(
            1120000000000001,
            ticket=USER_TICKET,
            roles={
                "read": ["blockedphones", "regions", "fallbacks", "gates", "routes", "templates", "audit_info"],
                "write": ["blockedphones", "regions", "fallbacks", "gates", "routes", "templates"],
            },
        )
        check(
            1120000000000000,
            roles={
                "read": [],
                "write": [],
            },
        )
        check(
            1120000000000002,
            roles={
                "read": ["routes"],
                "write": [],
            },
        )
        check(
            1120000000000003,
            roles={
                "read": [],
                "write": ["gates"],
            },
        )

    def test_auth(self):
        self.check_auth(handle='/1/user_roles', method='get')

        self.check_auth(handle='/1/regions', method='get')
        self.check_auth(handle='/1/regions', method='put')

        self.check_auth(handle='/1/service/routes', with_user_ticket=False)
        self.check_auth(handle='/1/routes', method='get')
        self.check_auth(handle='/1/routes', method='put')

        self.check_auth(handle='/1/routes/enums', method='get')

        self.check_auth(handle='/1/service/gates', with_user_ticket=False)
        self.check_auth(handle='/1/gates', method='get')
        self.check_auth(handle='/1/gates', method='put')

        self.check_auth(handle='/1/service/blockedphones', with_user_ticket=False)
        self.check_auth(handle='/1/blockedphones', method='get')
        self.check_auth(handle='/1/blockedphones', method='put')

        self.check_auth(handle='/1/service/fallbacks', with_user_ticket=False)
        self.check_auth(handle='/1/fallbacks', method='get')
        self.check_auth(handle='/1/fallbacks', method='put')

        self.check_auth(handle='/1/service/templates', method='get', with_user_ticket=False)
        self.check_auth(handle='/1/templates', method='get')
        self.check_auth(handle='/1/templates', method='put')
        self.check_auth(handle='/1/templates_parse', method='post', with_user_ticket=False)

        self.check_auth(handle='/1/audit/bulk_info', method='get')
        self.check_auth(handle='/1/audit/change_info', method='get')

    def test_get_routes_sequential(self):
        url_template = '{url}/1/routes?min={min}&limit={limit}'
        next_url = url_template.format(url=self.yasms.url, min="0", limit=1)
        i = 0
        routes = ["4484", "4485", "4486"]

        while next_url != "":
            r = requests.get(next_url, headers=AUTH_HEADERS)
            assert r.status_code == 200
            data = json.loads(r.content)
            if i >= len(routes):
                assert data['next'] == '' and len(data['routes']) == 0
                break

            assert routes[i] == data['routes'][0]['rule_id']
            next_url = '{url}{path}'.format(url=self.yasms.url, path=data['next'])
            i += 1

    def test_get_routes_limit(self):
        url_template = '{url}/1/routes?min={min}&limit={limit}'
        for i in range(1, 3):
            r = requests.get(url_template.format(url=self.yasms.url, min="0", limit=i), headers=AUTH_HEADERS)

            assert r.status_code == 200
            data = json.loads(r.content)
            assert len(data['routes']) == i

        r = requests.get(url_template.format(url=self.yasms.url, min="0", limit=100), headers=AUTH_HEADERS)
        assert r.status_code == 200
        data = json.loads(r.content)
        assert len(data['routes']) == 3

    def test_get_routes_all(self):
        url_template = '{url}/1/routes?min={min}&limit={limit}'
        r = requests.get(url_template.format(url=self.yasms.url, min="4483", limit=100), headers=AUTH_HEADERS)
        assert r.status_code == 200
        self.compare_json(r, 'test-get-routes-all.json')

    def test_get_routes_with_filter(self):
        url_template = '{url}/1/routes?min={min}&limit={limit}'
        r = requests.get(
            url_template.format(url=self.yasms.url, min="4483", limit=3),
            headers=AUTH_HEADERS,
            params={
                "filter": json.dumps(
                    {
                        "logic_op": "AND",
                        "args": [
                            {
                                "field": "gateid",
                                "compare_op": "NOT_EQUAL",
                                "values": ["115"],
                            },
                            {
                                "field": "mode",
                                "compare_op": "STARTS_WITH",
                                "values": ["val"],
                            },
                        ],
                    }
                ),
            },
        )
        assert r.status_code == 200
        self.compare_json(r, 'test-get-routes-with-filter.json')

    def test_get_routes_failed(self):
        url_template = '{url}/1/routes?min={min}&limit={limit}'
        r = requests.get(url_template.format(url=self.yasms.url, min="4483", limit=0), headers=AUTH_HEADERS)
        assert r.status_code == 400
        r = requests.get(url_template.format(url=self.yasms.url, min="4483", limit=-100), headers=AUTH_HEADERS)
        assert r.status_code == 400
        r = requests.get(
            url_template.format(url=self.yasms.url, min="4483", limit=3),
            headers=AUTH_HEADERS,
            params={
                "filter": json.dumps(
                    {
                        "logic_op": "AND",
                        "args": [
                            {
                                "field": "some_random_field",
                                "compare_op": "NOT_EQUAL",
                                "values": ["115"],
                            },
                        ],
                    }
                ),
            },
        )
        assert r.status_code == 400

    def test_routes_enums(self):
        url_template = '{url}/1/routes/enums'
        r = requests.get(url_template.format(url=self.yasms.url), headers=AUTH_HEADERS)
        assert r.status_code == 200
        self.compare_json(r, 'test-get-routes-enums.json')

    def test_get_gates_sequential(self):
        url_template = '{url}/1/gates?min={min}&limit={limit}'
        next_url = url_template.format(url=self.yasms.url, min="0", limit=1)
        i = 0
        gates = ["113", "114", "115"]

        while next_url != "":
            r = requests.get(next_url, headers=AUTH_HEADERS)
            assert r.status_code == 200
            data = json.loads(r.content)
            if i >= len(gates):
                assert data['next'] == '' and len(data['gates']) == 0
                break

            assert gates[i] == data['gates'][0]['gateid']
            next_url = '{url}{path}'.format(url=self.yasms.url, path=data['next'])
            i += 1

    def test_get_gates_limit(self):
        url_template = '{url}/1/gates?min={min}&limit={limit}'
        for i in range(1, 3):
            r = requests.get(url_template.format(url=self.yasms.url, min="0", limit=i), headers=AUTH_HEADERS)

            assert r.status_code == 200
            data = json.loads(r.content)
            assert len(data['gates']) == i

        r = requests.get(url_template.format(url=self.yasms.url, min="0", limit=100), headers=AUTH_HEADERS)
        assert r.status_code == 200
        data = json.loads(r.content)
        assert len(data['gates']) == 3

    def test_get_gates_all(self):
        url_template = '{url}/1/gates?min={min}&limit={limit}'
        r = requests.get(url_template.format(url=self.yasms.url, min="0", limit=30), headers=AUTH_HEADERS)
        assert r.status_code == 200
        self.compare_json(r, 'test-get-gates-all.json')

    def test_get_fallbacks_sequential(self):
        url_template = '{url}/1/fallbacks?min={min}&limit={limit}'
        next_url = url_template.format(url=self.yasms.url, min="0", limit=1)
        i = 0
        fallbacks = ["33", "42"]

        while next_url != "":
            r = requests.get(next_url, headers=AUTH_HEADERS)
            assert r.status_code == 200
            data = json.loads(r.content)
            if i >= len(fallbacks):
                assert data['next'] == '' and len(data['fallbacks']) == 0
                break

            assert fallbacks[i] == data['fallbacks'][0]['id']
            next_url = '{url}{path}'.format(url=self.yasms.url, path=data['next'])
            i += 1

    def test_get_fallbacks_limit(self):
        url_template = '{url}/1/fallbacks?min={min}&limit={limit}'
        for i in range(1, 2):
            r = requests.get(url_template.format(url=self.yasms.url, min="0", limit=i), headers=AUTH_HEADERS)

            assert r.status_code == 200
            data = json.loads(r.content)
            assert len(data['fallbacks']) == i

        r = requests.get(url_template.format(url=self.yasms.url, min="0", limit=100), headers=AUTH_HEADERS)
        assert r.status_code == 200
        data = json.loads(r.content)
        assert len(data['fallbacks']) == 2

    def test_get_fallbacks_all(self):
        url_template = '{url}/1/fallbacks?min={min}&limit={limit}'
        r = requests.get(url_template.format(url=self.yasms.url, min="32", limit=100), headers=AUTH_HEADERS)
        assert r.status_code == 200
        self.compare_json(r, 'test-get-fallbacks-all.json')

    def test_get_fallbacks_failed(self):
        url_template = '{url}/1/fallbacks?min={min}&limit={limit}'
        r = requests.get(url_template.format(url=self.yasms.url, min="32", limit=0), headers=AUTH_HEADERS)
        assert r.status_code == 400
        r = requests.get(url_template.format(url=self.yasms.url, min="32", limit=-100), headers=AUTH_HEADERS)
        assert r.status_code == 400

    def test_delete_routes_simple(self):
        url_template = '{url}/1/routes'
        r = requests.put(
            url_template.format(url=self.yasms.url),
            json={
                "delete": ["4484", "4486"],
                "change_info": {"issue": ["PASSP-1"], "comment": "delete routes"},
            },
            headers=AUTH_HEADERS,
        )
        assert r.status_code == 200
        self.check_routes_equal('test-set-routes-delete.json')
        audit_bulk, audit_row, _ = self.get_audit_log('sms.smsrt', 'ruleid')
        assert audit_bulk == [(1, 'test_login', 'PASSP-1', 'delete routes')]
        assert audit_row == [(1, 1, 'smsrt', 'delete', '', 4484), (2, 1, 'smsrt', 'delete', '', 4486)]

    def test_delete_routes_failed(self):
        url_template = '{url}/1/routes'
        r = requests.put(
            url_template.format(url=self.yasms.url),
            json={
                "delete": [4484],
            },
            headers=AUTH_HEADERS,
        )
        assert r.status_code == 400

        r = requests.put(
            url_template.format(url=self.yasms.url),
            json={
                "delet": ["1"],
            },
            headers=AUTH_HEADERS,
        )
        assert r.status_code == 400

        r = requests.put(
            url_template.format(url=self.yasms.url),
            json={
                "delete": ["1", "2", "3", "4484", "4486"],
            },
            headers=AUTH_HEADERS,
        )
        assert r.status_code == 400
        self.check_routes_equal('test-get-routes-all.json')

    def test_update_routes_simple(self):
        url_template = '{url}/1/routes'
        r = requests.put(
            url_template.format(url=self.yasms.url),
            json={
                "update": [
                    {
                        "rule_id": "4484",
                        "destination": "+7912",
                        "weight": 2,
                        "gates": ["115", "114", "113"],
                        "mode": "default",
                    },
                    {"rule_id": "4484", "destination": "+79", "weight": 3, "gates": ["113", "115"], "mode": "validate"},
                    {
                        "rule_id": "4485",
                        "destination": "+7",
                        "weight": 4,
                        "gates": ["113", "115", "114"],
                        "mode": "default",
                    },
                ],
                "change_info": {"issue": ["PASSP-1", "PASSP-2"], "comment": "update routes"},
            },
            headers=AUTH_HEADERS,
        )
        assert r.status_code == 200
        self.check_routes_equal('test-set-routes-update.json')
        audit_bulk, audit_row, data_row = self.get_audit_log('sms.smsrt', 'ruleid')
        assert audit_bulk == [(1, 'test_login', 'PASSP-1,PASSP-2', 'update routes')]
        assert audit_row == [
            (1, 1, 'smsrt', 'update', 'destination=+7912,gates=[115 114 113],weight=2,mode=default', 4484),
            (2, 1, 'smsrt', 'update', 'destination=+79,gates=[113 115],weight=3,mode=validate', 4484),
            (3, 1, 'smsrt', 'update', 'destination=+7,gates=[113 115 114],weight=4,mode=default', 4485),
        ]
        assert data_row == [(4484, None, 2), (4485, None, 3), (4486, None, None)]

    def test_update_routes_failed(self):
        url_template = '{url}/1/routes'
        r = requests.put(
            url_template.format(url=self.yasms.url),
            json={
                "update": [
                    {"rule_id": "448", "destination": "+7912", "weight": 2, "gates": ["115", "114", "113"]},
                ],
            },
            headers=AUTH_HEADERS,
        )
        assert r.status_code == 400

        r = requests.put(
            url_template.format(url=self.yasms.url),
            json={
                "update": [
                    {"ruled": "4484", "destination": "+7912", "weight": 2, "gates": ["115", "114", "113"]},
                ],
            },
            headers=AUTH_HEADERS,
        )
        assert r.status_code == 400

        r = requests.put(
            url_template.format(url=self.yasms.url),
            json={
                "update": [
                    {"rule_id": "4484", "destination": "+7912", "weight": 2, "gates": ["1"]},
                ],
            },
            headers=AUTH_HEADERS,
        )
        assert r.status_code == 400
        self.check_routes_equal('test-get-routes-all.json')

    def test_create_routes_simple(self):
        url_template = '{url}/1/routes'
        r = requests.put(
            url_template.format(url=self.yasms.url),
            json={
                "create": [
                    {"destination": "+7912", "weight": 1, "gates": ["114", "113", "115"], "mode": "validate"},
                    {"destination": "+79", "weight": 10, "gates": ["113", "115"], "mode": "default"},
                    {"destination": "+7", "weight": 2, "gates": ["115"], "mode": "default"},
                ],
                "change_info": {"issue": ["PASSP-1"], "comment": "create routes"},
            },
            headers=AUTH_HEADERS,
        )
        assert r.status_code == 200
        self.check_routes_equal('test-set-routes-create.json')
        audit_bulk, audit_row, data_row = self.get_audit_log('sms.smsrt', 'ruleid')
        assert audit_bulk == [(1, 'test_login', 'PASSP-1', 'create routes')]
        assert audit_row == [
            (1, 1, 'smsrt', 'add', 'destination=+7912,gates=[114 113 115],weight=1,mode=validate', 4487),
            (2, 1, 'smsrt', 'add', 'destination=+79,gates=[113 115],weight=10,mode=default', 4488),
            (3, 1, 'smsrt', 'add', 'destination=+7,gates=[115],weight=2,mode=default', 4489),
        ]
        assert data_row == [
            (4484, None, None),
            (4485, None, None),
            (4486, None, None),
            (4487, 1, 1),
            (4488, 2, 2),
            (4489, 3, 3),
        ]

    def test_create_routes_no_change_info(self):
        url_template = '{url}/1/routes'
        r = requests.put(
            url_template.format(url=self.yasms.url),
            json={
                "create": [
                    {"destination": "+7912", "weight": 1, "gates": ["114", "113", "115"], "mode": "validate"},
                    {"destination": "+79", "weight": 10, "gates": ["113", "115"], "mode": "default"},
                    {"destination": "+7", "weight": 2, "gates": ["115"], "mode": "default"},
                ]
            },
            headers=AUTH_HEADERS,
        )
        assert r.status_code == 200
        self.check_routes_equal('test-set-routes-create.json')
        audit_bulk, audit_row, data_row = self.get_audit_log('sms.smsrt', 'ruleid')
        assert audit_bulk == [(1, 'test_login', '', '')]
        assert audit_row == [
            (1, 1, 'smsrt', 'add', 'destination=+7912,gates=[114 113 115],weight=1,mode=validate', 4487),
            (2, 1, 'smsrt', 'add', 'destination=+79,gates=[113 115],weight=10,mode=default', 4488),
            (3, 1, 'smsrt', 'add', 'destination=+7,gates=[115],weight=2,mode=default', 4489),
        ]
        assert data_row == [
            (4484, None, None),
            (4485, None, None),
            (4486, None, None),
            (4487, 1, 1),
            (4488, 2, 2),
            (4489, 3, 3),
        ]

    def test_create_routes_failed(self):
        url_template = '{url}/1/routes'
        r = requests.put(
            url_template.format(url=self.yasms.url),
            json={
                "create": [
                    {"destination": "+7912", "weight": 1, "gates": ["1"]},
                ],
            },
            headers=AUTH_HEADERS,
        )
        assert r.status_code == 400

        r = requests.put(
            url_template.format(url=self.yasms.url),
            json={
                "create": [
                    {"destinatin": "+7912", "weight": 1, "gates": ["113", "114", "115"]},
                ],
            },
            headers=AUTH_HEADERS,
        )
        assert r.status_code == 400
        self.check_routes_equal('test-get-routes-all.json')

    def test_set_routes_simple(self):
        url_template = '{url}/1/routes'
        r = requests.put(
            url_template.format(url=self.yasms.url),
            json={
                "delete": ["4484"],
                "update": [
                    {
                        "rule_id": "4485",
                        "destination": "+7912",
                        "weight": 9,
                        "gates": ["115", "114", "113"],
                        "mode": "default",
                    },
                ],
                "create": [
                    {"destination": "+874362", "weight": 11, "gates": ["114"], "mode": "validate"},
                ],
            },
            headers=AUTH_HEADERS,
        )
        assert r.status_code == 200
        self.check_routes_equal('test-set-routes-all.json')

    def test_set_routes_failed(self):
        url_template = '{url}/1/routes'
        r = requests.put(
            url_template.format(url=self.yasms.url),
            json={
                "delete": ["4484"],
                "update": [
                    {
                        "rule_id": "4484",
                        "destination": "+7912",
                        "weight": 9,
                        "gates": ["115", "114", "113"],
                        "mode": "default",
                    },
                ],
                "create": [
                    {"destination": "+874362", "weight": 11, "gates": ["114"], "mode": "default"},
                ],
            },
            headers=AUTH_HEADERS,
        )
        assert r.status_code == 400

        r = requests.put(
            url_template.format(url=self.yasms.url),
            json={
                "delete": ["4484"],
                "update": [
                    {
                        "rule_id": "4487",
                        "destination": "+7912",
                        "weight": 9,
                        "gates": ["115", "114", "113"],
                        "mode": "default",
                    },
                ],
                "create": [
                    {"destination": "+874362", "weight": 11, "gates": ["114"], "mode": "default"},
                ],
            },
            headers=AUTH_HEADERS,
        )
        assert r.status_code == 400

        r = requests.put(
            url_template.format(url=self.yasms.url),
            json={
                "delete": ["4484"],
                "update": [
                    {
                        "rule_id": "4487",
                        "destination": "+7912",
                        "weight": 9,
                        "gates": ["115", "114", "113"],
                        "mode": "default",
                    },
                ],
                "create": [
                    {"destination": "+874362", "weight": 11, "gates": ["114"], "mode": "default"},
                ],
            },
            headers=AUTH_HEADERS,
        )
        assert r.status_code == 400

        r = requests.put(
            url_template.format(url=self.yasms.url),
            json={
                "delete": ["4487"],
                "create": [
                    {"destination": "+874362", "weight": 11, "gates": ["114"], "mode": "default"},
                ],
            },
            headers=AUTH_HEADERS,
        )
        assert r.status_code == 400
        self.check_routes_equal('test-get-routes-all.json')

    def test_delete_gates_simple(self):
        url_template = '{url}/1/gates'
        r = requests.put(
            url_template.format(url=self.yasms.url),
            json={
                "delete": [],
                "create": [self.make_gate("0"), self.make_gate("1")],
                "change_info": {"issue": ["PASSP-1"], "comment": "create gates"},
            },
            headers=AUTH_HEADERS,
        )
        assert r.status_code == 200

        r = requests.put(
            url_template.format(url=self.yasms.url),
            json={
                "delete": ["116", "117"],
                "change_info": {"issue": ["PASSP-2"], "comment": "delete gates"},
            },
            headers=AUTH_HEADERS,
        )
        assert r.status_code == 200
        self.check_gates_equal('test-get-gates-all.json')
        audit_bulk, audit_row, _ = self.get_audit_log('sms.smsgates', 'gateid')
        assert audit_bulk == [
            (1, 'test_login', 'PASSP-1', 'create gates'),
            (2, 'test_login', 'PASSP-2', 'delete gates'),
        ]
        assert audit_row == [
            (
                1,
                1,
                'smsgates',
                'add',
                'aliase=alias-0,fromname=fromname-0,consumer=consumer-0,contractor=contractor-0,extra=map[extra:extra-0]',
                116,
            ),
            (
                2,
                1,
                'smsgates',
                'add',
                'aliase=alias-1,fromname=fromname-1,consumer=consumer-1,contractor=contractor-1,extra=map[extra:extra-1]',
                117,
            ),
            (3, 2, 'smsgates', 'delete', '', 116),
            (4, 2, 'smsgates', 'delete', '', 117),
        ]

    def test_delete_gates_failed(self):
        url_template = '{url}/1/gates'
        r = requests.put(
            url_template.format(url=self.yasms.url),
            json={
                "delete": ["113"],
            },
            headers=AUTH_HEADERS,
        )
        assert r.status_code == 400

        r = requests.put(
            url_template.format(url=self.yasms.url),
            json={
                "delet": ["1"],
            },
            headers=AUTH_HEADERS,
        )
        assert r.status_code == 400

        r = requests.put(
            url_template.format(url=self.yasms.url),
            json={
                "delete": ["113"],
            },
            headers=AUTH_HEADERS,
        )
        assert r.status_code == 400
        self.check_gates_equal('test-get-gates-all.json')

    def test_update_gates_simple(self):
        url_template = '{url}/1/gates'
        r = requests.put(
            url_template.format(url=self.yasms.url),
            json={
                "update": [
                    self.make_gate_with_id("115", "2"),
                    self.make_gate_with_id("113", "0"),
                    self.make_gate_with_id("114", "1"),
                ],
            },
            headers=AUTH_HEADERS,
        )
        assert r.status_code == 200
        self.check_gates_equal('test-set-gates-update.json')
        audit_bulk, audit_row, data_row = self.get_audit_log('sms.smsgates', 'gateid')
        # no change_info in request
        assert audit_bulk == [(1, 'test_login', '', '')]
        assert audit_row == [
            (
                1,
                1,
                'smsgates',
                'update',
                'aliase=alias-2,fromname=fromname-2,consumer=consumer-2,contractor=contractor-2,extra=map[extra:extra-2]',
                115,
            ),
            (
                2,
                1,
                'smsgates',
                'update',
                'aliase=alias-0,fromname=fromname-0,consumer=consumer-0,contractor=contractor-0,extra=map[extra:extra-0]',
                113,
            ),
            (
                3,
                1,
                'smsgates',
                'update',
                'aliase=alias-1,fromname=fromname-1,consumer=consumer-1,contractor=contractor-1,extra=map[extra:extra-1]',
                114,
            ),
        ]
        assert data_row == [(113, None, 2), (114, None, 3), (115, None, 1)]

    def test_update_gates_failed(self):
        url_template = '{url}/1/gates'
        r = requests.put(
            url_template.format(url=self.yasms.url),
            json={
                "update": [
                    self.make_gate_with_id("100500", "2"),
                ],
            },
            headers=AUTH_HEADERS,
        )
        assert r.status_code == 400

        r = requests.put(
            url_template.format(url=self.yasms.url),
            json={
                "update": [
                    {"gated": "113", "aliase": "asdf", "fromname": "asdf", "contractor": "asdf", "consumer": "asdf"},
                ],
            },
            headers=AUTH_HEADERS,
        )
        assert r.status_code == 400
        self.check_gates_equal('test-get-gates-all.json')

    def test_create_gates_simple(self):
        url_template = '{url}/1/gates'
        r = requests.put(
            url_template.format(url=self.yasms.url),
            json={
                "create": [self.make_gate("0"), self.make_gate("1"), self.make_gate("2")],
            },
            headers=AUTH_HEADERS,
        )
        assert r.status_code == 200
        self.check_gates_equal('test-set-gates-create.json')

    def test_create_gates_failed(self):
        url_template = '{url}/1/gates'
        r = requests.put(
            url_template.format(url=self.yasms.url),
            json={
                "create": [
                    {"gateid": "113", "aliase": "asdf", "fromname": "asdf", "contractor": "asdf", "consumer": "asdf"},
                    {"aliase": "asdf1", "fromname": "asdf1", "contractor": "asdf1", "consumer": "asdf1"},
                ],
            },
            headers=AUTH_HEADERS,
        )
        assert r.status_code == 400
        self.check_gates_equal('test-get-gates-all.json')

    def test_set_gates_simple(self):
        url_template = '{url}/1/gates'
        r = requests.put(
            url_template.format(url=self.yasms.url),
            json={
                "create": [self.make_gate("0"), self.make_gate("1")],
            },
            headers=AUTH_HEADERS,
        )
        assert r.status_code == 200
        r = requests.put(
            url_template.format(url=self.yasms.url),
            json={
                "delete": ["116"],
                "update": [
                    self.make_gate_with_id("113", "5"),
                ],
                "create": [
                    self.make_gate("2"),
                ],
            },
            headers=AUTH_HEADERS,
        )
        assert r.status_code == 200
        self.check_gates_equal('test-set-gates-all.json')

    def test_set_gates_failed(self):
        url_template = '{url}/1/gates'
        r = requests.put(
            url_template.format(url=self.yasms.url),
            json={
                "create": [self.make_gate("0"), self.make_gate("1"), self.make_gate("2")],
            },
            headers=AUTH_HEADERS,
        )
        assert r.status_code == 200

        r = requests.put(
            url_template.format(url=self.yasms.url),
            json={
                "delete": [116],
                "update": [
                    self.make_gate_with_id("116", "0"),
                ],
                "create": [
                    self.make_gate("3"),
                ],
            },
            headers=AUTH_HEADERS,
        )
        assert r.status_code == 400

        r = requests.put(
            url_template.format(url=self.yasms.url),
            json={
                "delete": [116],
                "update": [
                    self.make_gate_with_id("119", "0"),
                ],
                "create": [
                    self.make_gate("3"),
                ],
            },
            headers=AUTH_HEADERS,
        )
        assert r.status_code == 400

        self.check_gates_equal('test-set-gates-create.json')

    def test_delete_fallbacks_simple(self):
        url_template = '{url}/1/fallbacks'
        r = requests.put(
            url_template.format(url=self.yasms.url),
            json={
                "delete": ["42"],
                "change_info": {"issue": ["PASSP-2"], "comment": "delete fallbacks"},
            },
            headers=AUTH_HEADERS,
        )
        assert r.status_code == 200
        self.check_fallbacks_equal('test-set-fallbacks-delete.json')
        audit_bulk, audit_row, _ = self.get_audit_log('sms.fallbacks', 'id')
        assert audit_bulk == [(1, 'test_login', 'PASSP-2', 'delete fallbacks')]
        assert audit_row == [(1, 1, 'fallbacks', 'delete', '', 42)]

    def test_delete_fallbacks_failed(self):
        url_template = '{url}/1/fallbacks'
        r = requests.put(
            url_template.format(url=self.yasms.url),
            json={
                "delete": [33],
            },
            headers=AUTH_HEADERS,
        )
        assert r.status_code == 400
        r = requests.put(
            url_template.format(url=self.yasms.url),
            json={
                "delete": ["1", "33", "42"],
            },
            headers=AUTH_HEADERS,
        )
        assert r.status_code == 400
        self.check_fallbacks_equal('test-get-fallbacks-all.json')

    def test_update_fallbacks_simple(self):
        url_template = '{url}/1/fallbacks'
        r = requests.put(
            url_template.format(url=self.yasms.url),
            json={
                "update": [
                    {
                        "id": "33",
                        "srcgate": "infobip",
                        "srcname": "Yandex",
                        "dstgate": "m1",
                        "dstname": "Yandex",
                        "order": 1,
                    },
                    {
                        "id": "42",
                        "srcgate": "taxiauth",
                        "srcname": "Yango",
                        "dstgate": "dzinga",
                        "dstname": "Yango",
                        "order": 0,
                    },
                ],
                "change_info": {"issue": ["PASSP-2"], "comment": "update fallbacks"},
            },
            headers=AUTH_HEADERS,
        )
        assert r.status_code == 200, r.text
        self.check_fallbacks_equal('test-set-fallbacks-update.json')
        audit_bulk, audit_row, data_row = self.get_audit_log('sms.fallbacks', 'id')
        assert audit_bulk == [(1, 'test_login', 'PASSP-2', 'update fallbacks')]
        assert audit_row == [
            (1, 1, 'fallbacks', 'update', 'srcgate=infobip,srcname=Yandex,dstgate=Yandex,dstname=m1,order=1', 33),
            (
                2,
                1,
                'fallbacks',
                'update',
                'srcgate=taxiauth,srcname=Yango,dstgate=Yango,dstname=dzinga,order=0',
                42,
            ),
        ]
        assert data_row == [(33, None, 1), (42, None, 2)]

    def test_update_fallbacks_failed(self):
        url_template = '{url}/1/fallbacks'
        r = requests.put(
            url_template.format(url=self.yasms.url),
            json={
                "update": [
                    {
                        "id": "33",
                        "srcgate": "infobip",
                        "srcname": "Yandex",
                        "dstgate": "m1",
                        "dstname": "Yandex",
                        "order": 1,
                    },
                    {
                        "id": "1",
                        "srcgate": "taxiauth",
                        "srcname": "Yango",
                        "dstgate": "dzinga",
                        "dstname": "Yango",
                        "order": 0,
                    },
                ],
            },
            headers=AUTH_HEADERS,
        )
        assert r.status_code == 400
        self.check_fallbacks_equal('test-get-fallbacks-all.json')

    def test_create_fallbacks_simple(self):
        url_template = '{url}/1/fallbacks'
        r = requests.put(
            url_template.format(url=self.yasms.url),
            json={
                "create": [
                    {"srcgate": "infobip", "srcname": "Yandex", "dstgate": "m1", "dstname": "Yandex", "order": 1},
                    {"srcgate": "taxiauth", "srcname": "Yango", "dstgate": "dzinga", "dstname": "Yango", "order": 0},
                ],
            },
            headers=AUTH_HEADERS,
        )
        assert r.status_code == 200, r.text
        self.check_fallbacks_equal('test-set-fallbacks-create.json')

    def test_create_fallbacks_failed(self):
        url_template = '{url}/1/fallbacks'
        r = requests.put(
            url_template.format(url=self.yasms.url),
            json={
                "create": [
                    {"srcgate": "infobip", "srcname": "Yandex", "dstgate": "gms", "dstname": "Yandex", "order": 1},
                    {"srcgate": "taxiauth", "srcname": "Yango", "dstgate": "dzinga", "dstname": "Yango", "order": 0},
                ],
            },
            headers=AUTH_HEADERS,
        )
        assert r.status_code == 400
        self.check_fallbacks_equal('test-get-fallbacks-all.json')

    def test_set_fallbacks_simple(self):
        url_template = '{url}/1/fallbacks'
        r = requests.put(
            url_template.format(url=self.yasms.url),
            json={
                "delete": ["42"],
                "update": [
                    {
                        "id": "33",
                        "srcgate": "infobip",
                        "srcname": "Yandex",
                        "dstgate": "m1",
                        "dstname": "Yandex",
                        "order": 1,
                    },
                ],
                "create": [
                    {"srcgate": "taxiauth", "srcname": "Yango", "dstgate": "dzinga", "dstname": "Yango", "order": 0},
                ],
            },
            headers=AUTH_HEADERS,
        )
        assert r.status_code == 200
        self.check_fallbacks_equal('test-set-fallbacks-all.json')

    def test_set_fallbacks_failed(self):
        url_template = '{url}/1/fallbacks'
        r = requests.put(
            url_template.format(url=self.yasms.url),
            json={
                "delete": ["33"],
                "update": [
                    {
                        "id": "33",
                        "srcgate": "infobip",
                        "srcname": "Yandex",
                        "dstgate": "m1",
                        "dstname": "Yandex",
                        "order": 1,
                    },
                ],
                "create": [
                    {"srcgate": "taxiauth", "srcname": "Yango", "dstgate": "dzinga", "dstname": "Yango", "order": 0},
                ],
            },
            headers=AUTH_HEADERS,
        )
        assert r.status_code == 400

        r = requests.put(
            url_template.format(url=self.yasms.url),
            json={
                "delete": ["33"],
                "update": [
                    {
                        "id": "43",
                        "srcgate": "infobip",
                        "srcname": "Yandex",
                        "dstgate": "m1",
                        "dstname": "Yandex",
                        "order": 1,
                    },
                ],
                "create": [
                    {"srcgate": "taxiauth", "srcname": "Yango", "dstgate": "dzinga", "dstname": "Yango", "order": 0},
                ],
            },
            headers=AUTH_HEADERS,
        )
        assert r.status_code == 400

        r = requests.put(
            url_template.format(url=self.yasms.url),
            json={
                "delete": ["43"],
                "create": [
                    {"srcgate": "taxiauth", "srcname": "Yango", "dstgate": "dzinga", "dstname": "Yango", "order": 0},
                ],
            },
            headers=AUTH_HEADERS,
        )
        assert r.status_code == 400
        self.check_fallbacks_equal('test-get-fallbacks-all.json')

    def test_get_blocked_phones(self):
        self.check_blocked_phones_equal('test-get-blockedphones-all.json')
        url_template = '{url}/1/blockedphones?min={min}&limit={limit}'
        next_url = url_template.format(url=self.yasms.url, min="0", limit=1)
        i = 0
        blockedphones = ["54", "55"]

        while next_url != "":
            r = requests.get(next_url, headers=AUTH_HEADERS)
            assert r.status_code == 200
            data = json.loads(r.content)
            if i >= len(blockedphones):
                assert data['next'] == '' and len(data['blockedphones']) == 0
                break

            assert blockedphones[i] == data['blockedphones'][0]['blockid']
            next_url = '{url}{path}'.format(url=self.yasms.url, path=data['next'])
            i += 1

    def test_set_blocked_phones(self):
        url_template = '{url}/1/blockedphones'
        r = requests.put(
            url_template.format(url=self.yasms.url),
            json={
                "delete": ["55"],
                "create": [{"phone": "+12345678", "blocktype": "permanent", "blocktill": "2030-01-12T14:03:56Z"}],
                "update": [
                    {
                        "blockid": "54",
                        "phone": "+87654321",
                        "blocktype": "permanent",
                        "blocktill": "2015-11-30T07:02:43Z",
                    }
                ],
                "change_info": {"issue": ["PASSP-2"], "comment": "set blockedphones"},
            },
            headers=AUTH_HEADERS,
        )
        assert r.status_code == 200
        self.check_blocked_phones_equal('test-get-blockedphones-updated.json')
        audit_bulk, audit_row, data_row = self.get_audit_log('sms.blockedphones', 'blockid')
        assert audit_bulk == [(1, 'test_login', 'PASSP-2', 'set blockedphones')]
        assert audit_row == [
            (1, 1, 'blockedphones', 'delete', '', 55),
            (
                2,
                1,
                'blockedphones',
                'update',
                'phone=+87654321,blocktype=permanent,blocktill=2015-11-30 07:02:43 +0000 UTC',
                54,
            ),
            (
                3,
                1,
                'blockedphones',
                'add',
                'phone=+12345678,blocktype=permanent,blocktill=2030-01-12 14:03:56 +0000 UTC',
                56,
            ),
        ]
        assert data_row == [(54, None, 2), (56, 3, 3)]

    def test_get_gates_with_filter(self):
        url_template = '{url}/1/gates?min={min}&limit={limit}'
        r = requests.get(
            url_template.format(url=self.yasms.url, min="0", limit=100),
            headers=AUTH_HEADERS,
            params={
                "filter": json.dumps(
                    {
                        "logic_op": "AND",
                        "args": [
                            {
                                "field": "gateid",
                                "compare_op": "NOT_EQUAL",
                                "values": ["115"],
                            },
                            {
                                "field": "aliase",
                                "compare_op": "STARTS_WITH",
                                "values": ["mi"],
                            },
                        ],
                    }
                ),
            },
        )
        assert r.status_code == 200
        self.compare_json(r, 'test-get-gates-with-filter.json')

    def test_get_gates_failed(self):
        url_template = '{url}/1/gates?min={min}&limit={limit}'
        r = requests.get(url_template.format(url=self.yasms.url, min="0", limit=0), headers=AUTH_HEADERS)
        assert r.status_code == 400
        r = requests.get(url_template.format(url=self.yasms.url, min="0", limit=-100), headers=AUTH_HEADERS)
        assert r.status_code == 400
        r = requests.get(
            url_template.format(url=self.yasms.url, min="0", limit=3),
            headers=AUTH_HEADERS,
            params={
                "filter": json.dumps(
                    {
                        "logic_op": "AND",
                        "args": [
                            {
                                "field": "some_random_field",
                                "compare_op": "NOT_EQUAL",
                                "values": ["115"],
                            },
                        ],
                    }
                ),
            },
        )
        assert r.status_code == 400

    def test_get_blocked_phones_with_filter(self):
        url_template = '{url}/1/blockedphones?min={min}&limit={limit}'
        r = requests.get(
            url_template.format(url=self.yasms.url, min="0", limit=100),
            headers=AUTH_HEADERS,
            params={
                "filter": json.dumps(
                    {
                        "logic_op": "AND",
                        "args": [
                            {
                                "field": "blockid",
                                "compare_op": "NOT_EQUAL",
                                "values": ["54"],
                            },
                            {
                                "field": "blocktill",
                                "compare_op": "MORE",
                                "values": ["2025-12-29T16:19:31Z"],
                            },
                        ],
                    }
                ),
            },
        )
        assert r.status_code == 200
        self.compare_json(r, 'test-get-blocked-phones-with-filter.json')

    def test_get_blocked_phones_failed(self):
        url_template = '{url}/1/blockedphones?min={min}&limit={limit}'
        r = requests.get(url_template.format(url=self.yasms.url, min="0", limit=0), headers=AUTH_HEADERS)
        assert r.status_code == 400
        r = requests.get(url_template.format(url=self.yasms.url, min="0", limit=-100), headers=AUTH_HEADERS)
        assert r.status_code == 400
        r = requests.get(
            url_template.format(url=self.yasms.url, min="0", limit=3),
            headers=AUTH_HEADERS,
            params={
                "filter": json.dumps(
                    {
                        "logic_op": "AND",
                        "args": [
                            {
                                "field": "blocktype",
                                "compare_op": "NOT_EQUAL",
                                "values": ["lalala"],
                            },
                        ],
                    }
                ),
            },
        )
        assert r.status_code == 400

    def test_get_fallbacks_with_filter(self):
        url_template = '{url}/1/fallbacks?min={min}&limit={limit}'
        r = requests.get(
            url_template.format(url=self.yasms.url, min="0", limit=100),
            headers=AUTH_HEADERS,
            params={
                "filter": json.dumps(
                    {
                        "logic_op": "AND",
                        "args": [
                            {
                                "field": "id",
                                "compare_op": "NOT_EQUAL",
                                "values": ["33"],
                            },
                            {
                                "field": "order",
                                "compare_op": "MORE",
                                "values": ["0"],
                            },
                        ],
                    }
                ),
            },
        )
        assert r.status_code == 200
        self.compare_json(r, 'test-get-fallbacks-with-filter.json')

    def test_get_fallbacks_with_failed(self):
        url_template = '{url}/1/fallbacks?min={min}&limit={limit}'
        r = requests.get(url_template.format(url=self.yasms.url, min="0", limit=0), headers=AUTH_HEADERS)
        assert r.status_code == 400
        r = requests.get(url_template.format(url=self.yasms.url, min="0", limit=-100), headers=AUTH_HEADERS)
        assert r.status_code == 400
        r = requests.get(
            url_template.format(url=self.yasms.url, min="0", limit=3),
            headers=AUTH_HEADERS,
            params={
                "filter": json.dumps(
                    {
                        "logic_op": "AND",
                        "args": [
                            {
                                "field": "some_random_field",
                                "compare_op": "NOT_EQUAL",
                                "values": ["115"],
                            },
                        ],
                    }
                ),
            },
        )
        assert r.status_code == 400
