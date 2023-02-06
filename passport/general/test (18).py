import yatest.common as yc
import brotli
import datetime
import json
import os
import requests
import time
import yt.wrapper
from passport.infra.recipes.common import log, start_daemon
from yatest.common import network
from base64 import b32encode

ROLES_TABLE = '//home/roles'
MAPPING_TABLE = '//home/mapping'

SERVICE_TICKET = '3:serv:CBAQ__________9_IggIvog9ELWIPQ:FyfxWijRXIk1dRTTtTBBTSizjHSEKPQVLVf_tQ3ooF_HBhY9FZFsTWsE8lB17PsqFQdEvq-g4qcXfokbemqD2sbcLUZaKnXkRZgvTy20tirPBWkc8HgLj0UMxUHJsWsyXCFm780OThC5vmGzA0CENpRTOr-WOGI4yx9QPO3AmUE'  # noqa
TICKET_INVALID = 'ticket'
TICKET_BAD_SRC = '3:serv:CBAQ__________9_IggItYg9ELWIPQ:V6D8YG3EOiQ0gUxirTI292w5oaFKcvvbxJdowZ8nsKfNTUgJ4q7AEgOlHh4v1aOELvAFX9R3RZbJ9VOc2-m1-WwWlWwCGFvAy8DLf4P1vjQor58B-W1t4Z2KwtahRmbC-_4Kseq4ouHkCI-SNongDctK5_y4b8QGaR0vzS1YlV8'  # noqa
TICKET_BAD_DST = '3:serv:CBAQ__________9_IggItYg9ELaIPQ:UM8g1wEjdpI5a21MHAvI8REc0QYhKgFcc_xfPjzceoGre752PboyK6fr5saNFmI0OH8SnqSzMOeGCrkGnt_X_hfcJYh3t06g7ZFH72vYmzNnf4FW4xCzVfhRCHiCPR7FlkAQN3I_xEtyOWrcEw7xm-Md_f-D1Gdt-R4r_qY07mk'  # noqa

yt_proxy = os.environ["YT_PROXY"]


def createTables():
    yt.wrapper.config["proxy"]["url"] = yt_proxy
    yt.wrapper.config["proxy"]["enable_proxy_discovery"] = False

    if yt.wrapper.exists(ROLES_TABLE):
        yt.wrapper.remove(ROLES_TABLE)

    if yt.wrapper.exists(MAPPING_TABLE):
        yt.wrapper.remove(MAPPING_TABLE)

    roles_schema = [
        {
            "name": "slug",
            "required": True,
            "type_v3": "string",
            "sort_order": "ascending",
        },
        {
            "name": "reversed_revision",
            "required": True,
            "type_v3": "uint64",
            "sort_order": "ascending",
        },
        {
            "name": "meta",
            "required": False,
            "type_v3": {"type_name": "optional", "item": "yson"},
        },
        {
            "name": "blob",
            "required": True,
            "type_v3": "string",
        },
    ]

    mapping_schema = [
        {
            "name": "slug",
            "required": True,
            "type_v3": "string",
            "sort_order": "ascending",
        },
        {
            "name": "tvm_id",
            "required": True,
            "type_v3": "uint32",
            "sort_order": "ascending",
        },
        {
            "name": "dummy",
            "required": False,
            "type_v3": {"type_name": "optional", "item": "yson"},
        },
    ]

    yt.wrapper.create("table", ROLES_TABLE, attributes={"dynamic": True, "schema": roles_schema})
    yt.wrapper.create("table", MAPPING_TABLE, attributes={"dynamic": True, "schema": mapping_schema})

    yt.wrapper.mount_table(ROLES_TABLE)
    yt.wrapper.mount_table(MAPPING_TABLE)


class TestTiroleInternal:
    @classmethod
    def setup_class(cls):
        os.environ['TZ'] = 'Europe/Moscow'
        time.tzset()

        createTables()
        log('Starting Tirole-internal test')
        cls.pm = network.PortManager()

        config_path = yc.output_path('tirole_internal.conf')
        tvm_cache_dir = yc.output_path('tvm_cache')
        sign_keys_path = yc.output_path('sign.keys')
        oauth_token_path = yc.output_path('yt.token')

        if not os.path.isdir(tvm_cache_dir):
            os.mkdir(tvm_cache_dir)

        cls.http_port = cls.pm.get_tcp_port()
        cls.unistat_port = cls.pm.get_tcp_port()

        try:
            with open('./tvmapi.port') as f:
                tvm_port = int(f.read())
        except IOError:
            log('Could not find tvm port file: ./tvmapi.port')

        with open(sign_keys_path, 'w') as f:
            f.write("{\"1\": \"733f9cdba433040287a4235247f8f31a326fee9e0f094d2987aac16d5eb0b883\"}")

        with open(oauth_token_path, 'w') as f:
            f.write("")

        # prepare config
        tirole_config = {
            "http_common": {
                "listen_address": "localhost",
                "port": cls.http_port,
                "cert": "",
                "key": "",
            },
            "http_unistat": {
                "listen_address": "localhost",
                "port": cls.unistat_port,
            },
            "logger": {
                "file": yc.output_path("common.log"),
            },
            "service": {
                "common": {
                    "force_down_file": yc.output_path("tirole_internal_force_down"),
                    "access_log": yc.output_path("access.log"),
                },
                "tvm": {
                    "self_tvm_id": 1000501,
                    "disk_cache_dir": tvm_cache_dir,
                    "check_service_tickets": True,
                    "tvm_host": "http://127.0.0.1",
                    "tvm_port": tvm_port,
                },
                "allowed_tvmid": [1000510],
                "yt": {
                    "cluster": yt_proxy,
                    "path": "//home",
                    "oauth_token_file": oauth_token_path,
                    "timeout_ms": 30000,
                    "use_tls": False,
                },
                "key_map": {
                    "keys_file": sign_keys_path,
                    "default_key": "1",
                },
            },
        }

        with open(config_path, 'w') as f:
            json.dump(tirole_config, f, indent=2)

        command = [
            yc.build_path('passport/infra/daemons/tirole_internal/cmd/tirole_internal'),
            '-c',
            config_path,
        ]

        cls.process = start_daemon(command, os.environ.copy(), cls.http_port, 300)

    @classmethod
    def teardown_class(cls):
        log('Closing Tirole-internal test')
        cls.pm.release()
        cls.process.terminate()

    def test_ping(self):
        url = 'http://127.0.0.1:%d/ping' % self.http_port

        r = requests.get(url)
        assert r.status_code == 200
        assert r.text == ""

        r = requests.get(url, headers={"X-Ya-Service-Ticket": TICKET_INVALID})
        assert r.status_code == 200
        assert r.text == ""

        r = requests.get(url, headers={"X-Ya-Service-Ticket": SERVICE_TICKET})
        assert r.status_code == 200
        assert r.text == ""

        force_down_file = yc.output_path("tirole_internal_force_down")
        with open(force_down_file, 'w') as f:
            f.write("down")

        r = requests.get(url, headers={"X-Ya-Service-Ticket": SERVICE_TICKET})
        assert r.status_code == 503
        assert r.text == "Service is forced down"

        os.remove(force_down_file)

        r = requests.get(url, headers={"X-Ya-Service-Ticket": SERVICE_TICKET})
        assert r.status_code == 200
        assert r.text == ""

    @staticmethod
    def check_roles_row(row, slug, rev, born_ts, tvm=None, user=None):
        assert row["slug"] == slug
        assert row["reversed_revision"] == 0x7FFFFFFFFFFFFFFF - rev
        assert row["meta"]["unixtime"] == born_ts
        assert row["meta"]["codec"] == "brotli"
        assert row["meta"]["revision_original"] == rev
        ext_revision = b32encode(b"%x" % rev).replace(b"=", b"").decode('ascii')
        assert row["meta"]["revision_external"] == ext_revision

        str_date = str(datetime.datetime.fromtimestamp(born_ts))
        assert row["meta"]["born_date"].startswith(str_date)

        blob = json.loads(brotli.decompress(row["blob"]._bytes))
        assert blob["born_date"] == born_ts
        assert blob["revision"] == ext_revision

        if tvm:
            assert blob["tvm"] == tvm
        if user:
            assert blob["user"] == user

    def test_upload_roles(self):
        url = 'http://127.0.0.1:%d/v1/upload_roles' % self.http_port

        r = requests.get(url)
        assert r.status_code == 405
        assert '{"message":"Method Not Allowed"}' in r.text

        r = requests.post(url)
        assert r.status_code == 401
        assert '"error":"missing service ticket.' in r.text

        r = requests.post(url, headers={"X-Ya-Service-Ticket": TICKET_INVALID})
        assert r.status_code == 401
        assert '"error":"service ticket is invalid.' in r.text

        r = requests.post(url, headers={"X-Ya-Service-Ticket": TICKET_BAD_DST})
        assert r.status_code == 401
        assert 'tvm: invalid ticket: InvalidDst; expected dst is 1000501.' in r.text

        r = requests.post(url, headers={"X-Ya-Service-Ticket": TICKET_BAD_SRC})
        assert r.status_code == 401
        assert '"error":"SrcID 1000501 is not allowed.' in r.text

        r = requests.post(url, headers={"X-Ya-Service-Ticket": SERVICE_TICKET})
        assert r.status_code == 400
        assert '"error":"Only JSON allowed as request, got Content-Type: \'\'' in r.text

        r = requests.post(url, headers={"X-Ya-Service-Ticket": SERVICE_TICKET}, json={})
        assert r.status_code == 400
        assert '"error":"Failed to validate request body:' in r.text

        request = {
            "system_slug": "test_service",
            "roles": {"revision": 100, "born_date": 1111, "tvm": {"1": {"role": [{"one": "two"}]}}},
        }
        r = requests.post(url, headers={"X-Ya-Service-Ticket": SERVICE_TICKET}, json=request)
        assert r.status_code == 200
        assert '{"status":"ok"}' in r.text

        rows = [r for r in yt.wrapper.select_rows("* FROM [%s]" % ROLES_TABLE)]

        assert len(rows) == 1
        TestTiroleInternal.check_roles_row(rows[0], "test_service", 100, 1111, {"1": {"role": [{"one": "two"}]}})

        request = {
            "system_slug": "test_service",
            "roles": {
                "revision": 100500,
                "born_date": 1616161616,
                "tvm": {"1": {"role": [{"1": "2"}]}, "242": {"role": [{"foo": "bar"}]}},
                "user": {"1": {"role": [{"1": "2"}]}},
            },
        }
        r = requests.post(url, headers={"X-Ya-Service-Ticket": SERVICE_TICKET}, json=request)
        assert r.status_code == 200
        assert '{"status":"ok"}' in r.text

        rows = [r for r in yt.wrapper.select_rows("* FROM [%s]" % ROLES_TABLE)]
        assert len(rows) == 2
        TestTiroleInternal.check_roles_row(
            rows[0],
            "test_service",
            100500,
            1616161616,
            {"1": {"role": [{"1": "2"}]}, "242": {"role": [{"foo": "bar"}]}},
            {"1": {"role": [{"1": "2"}]}},
        )
        TestTiroleInternal.check_roles_row(rows[1], "test_service", 100, 1111, {"1": {"role": [{"one": "two"}]}})

    @staticmethod
    def check_mapping_row(row, slug, tvm_id):
        assert row["slug"] == slug
        assert row["tvm_id"] == tvm_id
        assert row["dummy"] is None

    def test_manage_slug(self):
        url = 'http://127.0.0.1:%d/v1/manage_slug' % self.http_port

        r = requests.get(url)
        assert r.status_code == 405
        assert '{"message":"Method Not Allowed"}' in r.text

        r = requests.post(url)
        assert r.status_code == 401
        assert '"error":"missing service ticket.' in r.text

        r = requests.post(url, headers={"X-Ya-Service-Ticket": TICKET_INVALID})
        assert r.status_code == 401
        assert '"error":"service ticket is invalid.' in r.text

        r = requests.post(url, headers={"X-Ya-Service-Ticket": TICKET_BAD_DST})
        assert r.status_code == 401
        assert 'tvm: invalid ticket: InvalidDst; expected dst is 1000501.' in r.text

        r = requests.post(url, headers={"X-Ya-Service-Ticket": TICKET_BAD_SRC})
        assert r.status_code == 401
        assert '"error":"SrcID 1000501 is not allowed.' in r.text

        r = requests.post(url, headers={"X-Ya-Service-Ticket": SERVICE_TICKET})
        assert r.status_code == 400
        assert '"error":"Only JSON allowed as request, got Content-Type: \'\'' in r.text

        r = requests.post(url, headers={"X-Ya-Service-Ticket": SERVICE_TICKET}, json={})
        assert r.status_code == 400
        assert '"error":"\'system_slug\' cannot be empty' in r.text

        r = requests.post(url, headers={"X-Ya-Service-Ticket": SERVICE_TICKET}, json={"system_slug": "foo", "tvmid": 2})
        assert r.status_code == 400
        assert (
            '"error":"Bad JSON body: code=400, message=Unmarshal type error: expected=[]tvm.ClientID, got=number, field=tvmid'
            in r.text
        )

        r = requests.post(
            url, headers={"X-Ya-Service-Ticket": SERVICE_TICKET}, json={"system_slug": "foo", "tvmid": [2, 3, 0]}
        )
        assert r.status_code == 400
        assert '"error":"Tvmid cannot be 0' in r.text

        r = requests.post(url, headers={"X-Ya-Service-Ticket": SERVICE_TICKET}, json={"system_slug": "test"})
        assert r.status_code == 200
        assert '{"status":"ok"}' in r.text

        rows = [r for r in yt.wrapper.select_rows("* FROM [%s]" % MAPPING_TABLE)]
        assert len(rows) == 0

        r = requests.post(
            url, headers={"X-Ya-Service-Ticket": SERVICE_TICKET}, json={"system_slug": "test", "tvmid": [1, 2, 100500]}
        )
        assert r.status_code == 200
        assert '{"status":"ok"}' in r.text

        rows = [r for r in yt.wrapper.select_rows("* FROM [%s]" % MAPPING_TABLE)]
        assert len(rows) == 3
        TestTiroleInternal.check_mapping_row(rows[0], "test", 1)
        TestTiroleInternal.check_mapping_row(rows[1], "test", 2)
        TestTiroleInternal.check_mapping_row(rows[2], "test", 100500)

        r = requests.post(
            url, headers={"X-Ya-Service-Ticket": SERVICE_TICKET}, json={"system_slug": "test_service", "tvmid": [100]}
        )
        assert r.status_code == 200
        assert '{"status":"ok"}' in r.text

        rows = [r for r in yt.wrapper.select_rows("* FROM [%s]" % MAPPING_TABLE)]
        assert len(rows) == 4
        TestTiroleInternal.check_mapping_row(rows[0], "test", 1)
        TestTiroleInternal.check_mapping_row(rows[1], "test", 2)
        TestTiroleInternal.check_mapping_row(rows[2], "test", 100500)
        TestTiroleInternal.check_mapping_row(rows[3], "test_service", 100)

        r = requests.post(
            url, headers={"X-Ya-Service-Ticket": SERVICE_TICKET}, json={"system_slug": "test", "tvmid": [3, 100]}
        )
        assert r.status_code == 200
        assert '{"status":"ok"}' in r.text

        rows = [r for r in yt.wrapper.select_rows("* FROM [%s]" % MAPPING_TABLE)]
        assert len(rows) == 3
        TestTiroleInternal.check_mapping_row(rows[0], "test", 3)
        TestTiroleInternal.check_mapping_row(rows[1], "test", 100)
        TestTiroleInternal.check_mapping_row(rows[2], "test_service", 100)


# simple test that uses YT in recipe
def test_yt():
    TABLE = '//tmp/table'

    yt.wrapper.config["proxy"]["url"] = yt_proxy
    yt.wrapper.config["proxy"]["enable_proxy_discovery"] = False

    assert not yt.wrapper.exists(TABLE)

    # create table
    yt.wrapper.create("table", TABLE)

    assert yt.wrapper.exists(TABLE)

    # table empty
    rows = [r for r in yt.wrapper.read_table(TABLE)]
    assert len(rows) == 0

    # write to table
    yt.wrapper.write_table(TABLE, [{"hello": "world"}], format="json")

    # read from table
    rows = [r for r in yt.wrapper.read_table(TABLE)]

    assert len(rows) == 1
    assert rows[0] == {"hello": "world"}
