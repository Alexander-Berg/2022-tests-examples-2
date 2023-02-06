import yatest.common as yc
import json
import os
import pytest
import requests
import time
import yt.wrapper
from passport.infra.recipes.common import log, start_daemon
from yatest.common import network
from base64 import b64encode
import tvmauth


ROLES_TABLE = '//home/roles'
MAPPING_TABLE = '//home/mapping'

SERVICE_TICKET = '3:serv:CBAQ__________9_IggIvog9ELWIPQ:FyfxWijRXIk1dRTTtTBBTSizjHSEKPQVLVf_tQ3ooF_HBhY9FZFsTWsE8lB17PsqFQdEvq-g4qcXfokbemqD2sbcLUZaKnXkRZgvTy20tirPBWkc8HgLj0UMxUHJsWsyXCFm780OThC5vmGzA0CENpRTOr-WOGI4yx9QPO3AmUE'  # noqa

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


class TestTiroleCombined:
    @classmethod
    def run_service(cls, name):
        config_path = yc.output_path(name + ".conf")

        http_port = cls.pm.get_tcp_port()
        unistat_port = cls.pm.get_tcp_port()

        tirole_config = {
            "http_common": {
                "listen_address": "localhost",
                "port": http_port,
                "cert": "",
                "key": "",
            },
            "http_unistat": {
                "listen_address": "localhost",
                "port": unistat_port,
            },
            "logger": {
                "file": yc.output_path(name + "_common.log"),
            },
            "service": {
                "common": {
                    "force_down_file": yc.output_path(name + "_force_down"),
                    "access_log": yc.output_path(name + "_access.log"),
                },
                "tvm": {
                    "self_tvm_id": 1000501,
                    "disk_cache_dir": cls.tvm_cache_dir,
                    "check_service_tickets": True,
                    "tvm_host": "http://127.0.0.1",
                    "tvm_port": cls.tvm_port,
                },
                "allowed_tvmid": [1000510],
                "yt": {
                    "cluster": yt_proxy,
                    "path": "//home",
                    "oauth_token_file": cls.oauth_token_path,
                    "timeout_ms": 30000,
                    "use_tls": False,
                },
                "key_map": {
                    "keys_file": cls.sign_keys_path,
                    "default_key": "1",
                },
            },
        }

        with open(config_path, 'w') as f:
            json.dump(tirole_config, f, indent=2)

        command = [
            yc.build_path('passport/infra/daemons/' + name + '/cmd/' + name),
            '-c',
            config_path,
        ]

        process = start_daemon(command, os.environ.copy(), http_port, 300)

        return process, http_port

    @classmethod
    def setup_class(cls):
        os.environ['TZ'] = 'Europe/Moscow'
        time.tzset()

        createTables()
        log('Starting Tirole combined test')
        cls.pm = network.PortManager()

        cls.tvm_cache_dir = yc.output_path('tvm_cache')
        cls.sign_keys_path = yc.output_path('sign.keys')
        cls.oauth_token_path = yc.output_path('yt.token')

        if not os.path.isdir(cls.tvm_cache_dir):
            os.mkdir(cls.tvm_cache_dir)

        try:
            with open('./tvmapi.port') as f:
                cls.tvm_port = int(f.read())
        except IOError:
            log('Could not find tvm port file: ./tvmapi.port')

        with open(cls.sign_keys_path, 'w') as f:
            f.write("{\"1\": \"733f9cdba433040287a4235247f8f31a326fee9e0f094d2987aac16d5eb0b883\"}")

        with open(cls.oauth_token_path, 'w') as f:
            f.write("")

        cls.tirole_process, cls.tirole_http_port = cls.run_service("tirole")
        cls.tirole_internal_process, cls.tirole_internal_http_port = cls.run_service("tirole_internal")

    @classmethod
    def teardown_class(cls):
        log('Closing Tirole-internal test')
        cls.pm.release()
        cls.tirole_process.terminate()
        cls.tirole_internal_process.terminate()

    def test_tirole(self):
        tirole_url = 'http://127.0.0.1:%d/v1/get_actual_roles' % self.tirole_http_port
        tirole_internal_url = 'http://127.0.0.1:%d/v1/' % self.tirole_internal_http_port

        r = requests.get(tirole_url + "?system_slug=test", headers={"X-Ya-Service-Ticket": SERVICE_TICKET})
        assert r.status_code == 403
        assert '"error":"system_slug \'test\' is not mapped to tvmid=1000510' in r.text

        r = requests.post(
            tirole_internal_url + 'manage_slug',
            headers={"X-Ya-Service-Ticket": SERVICE_TICKET},
            json={"system_slug": "test", "tvmid": [1, 1000510]},
        )
        assert r.status_code == 200
        assert '{"status":"ok"}' in r.text

        r = requests.get(tirole_url + "?system_slug=test", headers={"X-Ya-Service-Ticket": SERVICE_TICKET})
        assert r.status_code == 400
        assert '"error":"Failed to get revision for tvmid=1000510: There are no roles for slug=test.' in r.text

        BLOB1 = b"G0gAAATCduTPk4WzKOCu6wKqSVewGzjkgP3YvC3BAPSwMXaNxgmkBjcKRuulIrhlrQ1TRLhvY4EW/cdG4CfC/U7OzAQ="

        request = {
            "system_slug": "test",
            "roles": {"revision": 100, "born_date": 1111, "tvm": {"1": {"role": [{"one": "two"}]}}},
        }
        r = requests.post(
            tirole_internal_url + 'upload_roles', headers={"X-Ya-Service-Ticket": SERVICE_TICKET}, json=request
        )
        assert r.status_code == 200
        assert '{"status":"ok"}' in r.text

        r = requests.get(tirole_url + "?system_slug=test", headers={"X-Ya-Service-Ticket": SERVICE_TICKET})
        assert r.status_code == 200
        assert b64encode(r.content) == BLOB1

        BLOB2 = b"G5kAAAT+XVvqLy/cjtPwsyJYxGASsdnkiljGdHKaa4g96vOAWgIBp5YFdcNSLotVChk/gzM+iGVu076tB8Z8vDs28pFpfP+LgmeVAYZ1XOgMnt4RQpPKK61MewmHFXPXPSA2nkw="

        request = {
            "system_slug": "test",
            "roles": {
                "revision": 100500,
                "born_date": 1616161616,
                "tvm": {"1000510": {"role": [{"1": "2"}]}, "1000505": {"role": [{"foo": "bar"}]}},
                "user": {"1": {"role": [{"1": "2"}]}},
            },
        }
        r = requests.post(
            tirole_internal_url + 'upload_roles', headers={"X-Ya-Service-Ticket": SERVICE_TICKET}, json=request
        )
        assert r.status_code == 200
        assert '{"status":"ok"}' in r.text

        r = requests.get(tirole_url + "?system_slug=test", headers={"X-Ya-Service-Ticket": SERVICE_TICKET})
        assert r.status_code == 200
        assert b64encode(r.content) == BLOB2

        r = requests.get(
            tirole_url + "?system_slug=test",
            headers={"X-Ya-Service-Ticket": SERVICE_TICKET, "If-None-Match": "\"GE4DQOJU\""},
        )
        assert r.status_code == 304
        assert r.text == ""

        src_client = tvmauth.TvmClient(
            tvmauth.TvmApiClientSettings(
                self_tvm_id=1000505,
                self_secret="z5oaXOjgB5nV5gycBpzZ-A",
                dsts={"dst": 1000510},
                localhost_port=self.tvm_port,
            )
        )

        dst_client = tvmauth.TvmClient(
            tvmauth.TvmApiClientSettings(
                self_tvm_id=1000510,
                self_secret="LUTTSCreg1f976_B_EHKzg",
                enable_service_ticket_checking=True,
                enable_user_ticket_checking=tvmauth.BlackboxEnv.ProdYateam,
                disk_cache_dir=self.tvm_cache_dir,
                localhost_port=self.tvm_port,
                fetch_roles_for_idm_system_slug='test',
                tirole_host="localhost",
                tirole_port=self.tirole_http_port,
                tirole_tvmid=1000501,
            )
        )

        st = src_client.get_service_ticket_for("dst")
        t = dst_client.check_service_ticket(st)

        assert not dst_client.get_roles().check_service_role(t, "bad_role")
        assert dst_client.get_roles().check_service_role(t, "role")

        assert dst_client.get_roles().check_service_role(t, "role", {"foo": "bar"})
        assert not dst_client.get_roles().check_service_role(t, "role", {"foo": "baz"})

        with pytest.raises(tvmauth.exceptions.TicketParsingException) as ex:
            dst_client.check_user_ticket(
                "3:user:CAwQ__________9_Gg4KAghkEGQg0oXYzAQoAg:E-jE0nxllNVMsogTAfNWT0c25p44l-EEg4SnQAyZxBa8eNnDrYKqZDLaVAlSBJRHPnJgD8PwfH8ZTCmgcm86xTfGcwzb7aI3gXxM2pRS1BQy_cuo8097XaTEiPnZn7KDeSDJSJvBCVlT8zCR5C7ny7k1TtOCy5Oehu0qTeGcOOw"  # noqa
            )
        assert ex.value.status == tvmauth.TicketStatus.NoRoles
        assert "Subject (src or defaultUid) does not have any roles in IDM" in ex.value.message

        t = dst_client.check_user_ticket(
            "3:user:CAwQ__________9_Gg4KAggBEAEg0oXYzAQoAg:HfOtQarAY2h92zTZUURgITOoM1NftdoJaji4P-NN6u6qgirl5Y0i9_UHMVnSiHnyXNHB6n3oo1K-zf-TwTXWyE3RHSrgtm-vbVWIGafsaoHehupj5HXYeSDUugs7gqOox9y2HM1Ptm78mG5vpbCuQTt5wtwN4jpIHIXfQ4JLABo"  # noqa
        )

        assert not dst_client.get_roles().check_user_role(t, "no_role")
        assert dst_client.get_roles().check_user_role(t, "role")

        with pytest.raises(tvmauth.exceptions.NonRetriableException) as ex:
            dst_client.get_roles().check_user_role(t, "role", 2, {"1": "2"})
        assert "selectedUid must be in user ticket but it's not: 2" in str(ex)

        assert dst_client.get_roles().check_user_role(t, "role", 1, {"1": "2"})
        assert not dst_client.get_roles().check_user_role(t, "role", 1, {"2": "1"})
