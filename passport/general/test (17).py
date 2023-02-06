import yatest.common as yc
import json
import os
import requests
import time
import yt.wrapper
from passport.infra.recipes.common import log, start_daemon
from yatest.common import network
from base64 import b64decode, b64encode


ROLES_TABLE = '//home/roles'
MAPPING_TABLE = '//home/mapping'

SERVICE_TICKET = '3:serv:CBAQ__________9_IggIvog9ELWIPQ:FyfxWijRXIk1dRTTtTBBTSizjHSEKPQVLVf_tQ3ooF_HBhY9FZFsTWsE8lB17PsqFQdEvq-g4qcXfokbemqD2sbcLUZaKnXkRZgvTy20tirPBWkc8HgLj0UMxUHJsWsyXCFm780OThC5vmGzA0CENpRTOr-WOGI4yx9QPO3AmUE'  # noqa
TICKET_INVALID = 'ticket'
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


class TestTirole:
    @classmethod
    def setup_class(cls):
        os.environ['TZ'] = 'Europe/Moscow'
        time.tzset()

        createTables()
        log('Starting Tirole test')
        cls.pm = network.PortManager()

        config_path = yc.output_path('tirole.conf')
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
                    "force_down_file": yc.output_path("tirole_force_down"),
                    "access_log": yc.output_path("access.log"),
                },
                "tvm": {
                    "self_tvm_id": 1000501,
                    "disk_cache_dir": tvm_cache_dir,
                    "check_service_tickets": True,
                    "tvm_host": "http://127.0.0.1",
                    "tvm_port": tvm_port,
                },
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
            yc.build_path('passport/infra/daemons/tirole/cmd/tirole'),
            '-c',
            config_path,
        ]

        cls.process = start_daemon(command, os.environ.copy(), cls.http_port, 300)

    @classmethod
    def teardown_class(cls):
        log('Closing Tirole test')
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

        force_down_file = yc.output_path("tirole_force_down")
        with open(force_down_file, 'w') as f:
            f.write("down")

        r = requests.get(url, headers={"X-Ya-Service-Ticket": SERVICE_TICKET})
        assert r.status_code == 503
        assert r.text == "Service is forced down"

        os.remove(force_down_file)

        r = requests.get(url, headers={"X-Ya-Service-Ticket": SERVICE_TICKET})
        assert r.status_code == 200
        assert r.text == ""

    def test_get_actual_roles(self):
        url = 'http://127.0.0.1:%d/v1/get_actual_roles' % self.http_port

        r = requests.post(url)
        assert r.status_code == 405
        assert '"error":"Method Not Allowed.' in r.text

        r = requests.get(url)
        assert r.status_code == 401
        assert '"error":"missing service ticket.' in r.text

        r = requests.get(url, headers={"X-Ya-Service-Ticket": TICKET_INVALID})
        assert r.status_code == 401
        assert '"error":"service ticket is invalid.' in r.text

        r = requests.get(url, headers={"X-Ya-Service-Ticket": TICKET_BAD_DST})
        assert r.status_code == 401
        assert 'tvm: invalid ticket: InvalidDst; expected dst is 1000501.' in r.text

        r = requests.get(url, headers={"X-Ya-Service-Ticket": SERVICE_TICKET})
        assert r.status_code == 400
        assert '"error":"invalid param: missing \'system_slug\'.' in r.text

        r = requests.get(url + "?system_slug=test_service", headers={"X-Ya-Service-Ticket": SERVICE_TICKET})
        assert r.status_code == 403
        assert '"error":"system_slug \'test_service\' is not mapped to tvmid=1000510' in r.text

        yt.wrapper.insert_rows(MAPPING_TABLE, [{"slug": "test_service", "tvm_id": 1000510}], format="json")

        r = requests.get(url + "?system_slug=test_service", headers={"X-Ya-Service-Ticket": SERVICE_TICKET})
        assert r.status_code == 400
        assert '"error":"Failed to get revision for tvmid=1000510: There are no roles for slug=test_service.' in r.text

        BLOB1 = b"G0gAAATCduTPk4WzKOCu6wKqSVewGzjkgP3YvC3BAPSwMXaNxgmkBjcKRuulIrhlrQ1TRLhvY4EW/cdG4CfC/U7OzAQ="

        yt.wrapper.insert_rows(
            ROLES_TABLE,
            [
                {
                    "slug": "test_service",
                    "reversed_revision": 9223372036854775707,
                    "meta": {
                        "unixtime": 1111,
                        "codec": "brotli",
                        "decoded_size": 73,
                        "decoded_sha256": "5C43CF1E2D5A4C30DC645A4495826B753B00D3BF6C9604E93A3041264B839203",
                        "encoded_hmac": "1:ff5c3db23fe137a50b79c478e56627bf118a6899988f305518e52c58b4756d22",
                        "revision_external": "GY2A",
                        "revision_original": 100,
                        "born_date": "1970-01-01 03:18:31 +0300 MSK",
                    },
                    "blob": b64decode(BLOB1[4:]),  # broken blob, sign mismatch
                }
            ],
            format="json",
        )

        r = requests.get(url + "?system_slug=test_service", headers={"X-Ya-Service-Ticket": SERVICE_TICKET})
        assert r.status_code == 500
        assert (
            '"error":"Sign check failed, slug \'test_service\', revision GY2A: encoded_hmac check mismatch.' in r.text
        )

        yt.wrapper.insert_rows(
            ROLES_TABLE,
            [
                {
                    "slug": "test_service",
                    "reversed_revision": 9223372036854775707,
                    "meta": {
                        "unixtime": 1111,
                        "codec": "brotli",
                        "decoded_size": 73,
                        "decoded_sha256": "5C43CF1E2D5A4C30DC645A4495826B753B00D3BF6C9604E93A3041264B839203",
                        "encoded_hmac": "1:ff5c3db23fe137a50b79c478e56627bf118a6899988f305518e52c58b4756d22",
                        "revision_external": "GY2A",
                        "revision_original": 100,
                        "born_date": "1970-01-01 03:18:31 +0300 MSK",
                    },
                    "blob": b64decode(BLOB1),
                }
            ],
            format="json",
        )

        r = requests.get(url + "?system_slug=test_service", headers={"X-Ya-Service-Ticket": SERVICE_TICKET})
        assert r.status_code == 200
        assert b64encode(r.content) == BLOB1

        r = requests.get(
            url + "?system_slug=test_service", headers={"X-Ya-Service-Ticket": SERVICE_TICKET, "If-None-Match": "GY2A"}
        )
        assert r.status_code == 400
        assert '"error":"invalid header: \'If-None-Match\' contains incorrect revision \'GY2A\'. ' in r.text

        r = requests.get(
            url + "?system_slug=test_service",
            headers={"X-Ya-Service-Ticket": SERVICE_TICKET, "If-None-Match": "\"GY2A\""},
        )
        assert r.status_code == 304
        assert r.text == ""

        BLOB2 = b"G48AAASibaZ++YuPGD4rgkUMJhlra8MyVuR1csD838KgreURxRSmltvYUukXCNU2Dm88MGqJefQ2Efaz27GxkLgI3/9ih1A8RGGr80XxywWNOs5nbyl9AgFKO0xN3B0="

        yt.wrapper.insert_rows(
            ROLES_TABLE,
            [
                {
                    "slug": "test_service",
                    "reversed_revision": 9223372036854675307,
                    "meta": {
                        "unixtime": 1616161616,
                        "codec": "brotli",
                        "decoded_size": 144,
                        "decoded_sha256": "92E0A099037924BB3A734FF963A11F3C7129887AE5006304A2799BD91A656485",
                        "encoded_hmac": "1:ab636192e5cb05a70686c6c046837ca0ed9d5de818d43f87f9b24b7533a1f488",
                        "revision_external": "GE4DQOJU",
                        "revision_original": 100500,
                        "born_date": "2021-03-19 16:46:56 +0300 MSK",
                    },
                    "blob": b64decode(BLOB2),
                }
            ],
            format="json",
        )

        r = requests.get(
            url + "?system_slug=test_service",
            headers={"X-Ya-Service-Ticket": SERVICE_TICKET, "If-None-Match": "\"GY2A\""},
        )
        assert r.status_code == 200
        assert b64encode(r.content) == BLOB2

        r = requests.get(
            url + "?system_slug=test_service",
            headers={"X-Ya-Service-Ticket": SERVICE_TICKET, "If-None-Match": "\"100\""},
        )
        assert r.status_code == 200
        assert b64encode(r.content) == BLOB2

        r = requests.get(url + "?system_slug=test_service", headers={"X-Ya-Service-Ticket": SERVICE_TICKET})
        assert r.status_code == 200
        assert b64encode(r.content) == BLOB2

        r = requests.get(
            url + "?system_slug=test_service",
            headers={"X-Ya-Service-Ticket": SERVICE_TICKET, "If-None-Match": "\"GE4DQOJU\""},
        )
        assert r.status_code == 304
        assert r.text == ""
