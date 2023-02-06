import allure
import unittest

from yatest.common import network
from ticket_parser2.exceptions import NonRetriableException
from ticket_parser2 import (
    TvmApiClientSettings,
    TvmToolClientSettings,
    TvmClient,
    TvmClientStatus,
)
from ticket_parser2.low_level import ServiceContext
import json
import logging
import os
import pytest
import re
import requests
import subprocess
import sys
import ticket_parser2.unittest as tp2u
import time
import yatest.common as yc


YLAST_BIN = yc.build_path() + '/passport/infra/tools/ylast/ylast'

TEST_DATA = yc.source_path() + '/library/recipes/tvmapi/data/'
LAST_TESTS = yc.source_path() + '/passport/infra/daemons/tvmapi/last-tests/'

YLAST_CONFIG_PATH = './last.conf'
env = os.environ.copy()

TVM_HOST = 'http://localhost'
with open('tvmapi.port') as f:
    TVM_PORT = int(f.read())

TVM_URL = '%s:%d' % (TVM_HOST, TVM_PORT)

TVMTOOL_BIN = yc.build_path('passport/infra/daemons/tvmtool/cmd/tvmtool')


def _gen_last_config():
    f = open(yc.source_path('passport/infra/daemons/tvmapi/ut_py/data/last.conf'))
    cfg = f.read()

    cfg = cfg.replace('{secret.key}', TEST_DATA + 'secret.key')

    data_path = yc.source_path('passport/infra/daemons/tvmapi/ut_py/data/')
    cfg = re.sub(r'\{(secret_[0-9]+\.secret)\}', data_path + r'/\1', cfg)

    cfg = cfg.replace('{tvm_host}', TVM_HOST)
    cfg = cfg.replace('{tvm_port}', str(TVM_PORT))

    f = open(YLAST_CONFIG_PATH, 'wt')
    f.write(cfg)


def _check_started_tvmtool(url):
    i = 0
    while i < 150:
        i = i + 1
        try:
            r = requests.get(url + "/tvm/ping")
            assert r.text == 'OK'
            assert r.status_code == 200
            return
        except Exception:
            time.sleep(0.1)

    assert False


@allure.story('Запуск ylast тестов')
class YlastTests(unittest.TestCase):
    def test_ylast(self):
        """Неизменность простых ответов"""

        _gen_last_config()

        # TVM 2.0
        last = subprocess.Popen(
            [
                YLAST_BIN,
                LAST_TESTS + 'tvm2.xml',
                '-q',
                '-N',
                '-j',
                '6',
                '-c',
                YLAST_CONFIG_PATH,
                '-U',
                TVM_URL,
            ],
            env=env,
            stdout=sys.stderr,
            stderr=open('./testing_out_stuff/last.stderr', 'w'),
        )
        assert last.wait() == 0


@allure.story('Запуск тестов на интеграцию клиента и tvmapi')
class ClientTests(unittest.TestCase):
    def test_client(self):
        """Базовые сценарии клиента"""

        logfile = './my.log'
        if os.path.isfile(logfile):
            os.remove(logfile)
        l = logging.getLogger('TVM')
        handler = logging.FileHandler(logfile, 'a')
        handler.setLevel(logging.DEBUG)
        l.addHandler(handler)

        try:
            s = TvmApiClientSettings(
                self_client_id=123,
                enable_service_ticket_checking=True,
                self_secret='TNMsfcyRIAGpcHk4Ta5L-g',
                dsts=[27],
            )
            getattr(s, '__set_localhost')(TVM_PORT)
            with pytest.raises(NonRetriableException):
                TvmClient(s)

            s = TvmApiClientSettings(
                self_client_id=39,
                enable_service_ticket_checking=True,
                self_secret='TNMsfcyRIAGpcHk4Ta5L-g',
                dsts=[11],
            )
            getattr(s, '__set_localhost')(TVM_PORT)
            with pytest.raises(NonRetriableException):
                TvmClient(s)

            s = TvmApiClientSettings(
                self_client_id=39,
                enable_service_ticket_checking=True,
                self_secret='aaa',
                dsts={'dest': 27},
            )
            getattr(s, '__set_localhost')(TVM_PORT)
            with pytest.raises(NonRetriableException):
                TvmClient(s)

            s = TvmApiClientSettings(
                self_client_id=39,
                enable_service_ticket_checking=True,
                self_secret='TNMsfcyRIAGpcHk4Ta5L-g',
                dsts={'dest_27': 27},
            )
            getattr(s, '__set_localhost')(TVM_PORT)
            c = TvmClient(s)
            assert c.status == TvmClientStatus.Ok

            s2 = TvmApiClientSettings(
                self_client_id=27,
                enable_service_ticket_checking=True,
                self_secret='2LN58F3JHFD3dv4u6NlDbg',
                dsts={'dest_39': 39},
            )
            getattr(s2, '__set_localhost')(TVM_PORT)

            c2 = TvmClient(s2)
            assert c2.status == TvmClientStatus.Ok

            assert c2.check_service_ticket(c.get_service_ticket_for(client_id=27))
            assert c.check_service_ticket(c2.get_service_ticket_for('dest_39'))
            c2.stop()
            c.stop()
        except:
            sys.stderr.write(open(logfile, 'r').read() + '\n')
            raise


def default_checks(tvmtool_url, authtoken):
    # Check service ticket
    service_ticket_src_100500_dst_27 = (
        '3:serv:CBAQ__________9_IgYIlJEGEBs:VCbVoA45fvSKmyAYSW7Eo'
        'tfX-5nRz9yGmqqZQ4WHJPby3Ofn6ZzwRQpvgQG4OwFBjpNXqJyIS0OR_CD48P74Ey_yBD0ho5fL9Fa92M_ip0BR'
        'sNIRrf7yEkmLUrye0a5I014G3A5CgooQ9QTXYU2HRy93qp8r_05ec5h0zSkq9I8'
    )
    r = requests.get(
        tvmtool_url + '/tvm/checksrv',
        headers={'X-Ya-Service-Ticket': service_ticket_src_100500_dst_27, 'Authorization': authtoken},
    )
    assert r.status_code == 200
    assert (
        r.text == '{"src":100500,"dst":27,"scopes":null,'
        '"debug_string":"ticket_type=service;expiration_time=9223372036854775807;src=100500;dst=27;scope=;",'
        '"logging_string":"3:serv:CBAQ__________9_IgYIlJEGEBs:","issuer_uid":null}\n'
    )

    r = requests.get(
        tvmtool_url + '/tvm/checksrv',
        headers={'X-Ya-Service-Ticket': service_ticket_src_100500_dst_27[:-1], 'Authorization': authtoken},
    )
    assert r.status_code == 403
    assert (
        r.text == '{"error":"internalApply(). invalid signature format - 4",'
        '"debug_string":"ticket_type=service;expiration_time=9223372036854775807;src=100500;dst=27;scope=;",'
        '"logging_string":"3:serv:CBAQ__________9_IgYIlJEGEBs:"}\n'
    )

    service_ticket_src_100500_dst_42 = (
        '3:serv:CBAQ__________9_IgYIlJEGECo:M6np37QmjcrOr4nohxN-O'
        'xlKjPZ3_BJDAhe79ahZIQnLURVWdmPG1yM_Nm-QwnvOX7_-AcS09wpgsmNH7UFrekwk9m3H91Kf32PMw4xappDi'
        'RUL8h3cYt52wKIouvCGFBTGAwX1HJTj905HVrPHQ7m4gj4xkmyhRX9swPk0QicY'
    )
    r = requests.get(
        tvmtool_url + '/tvm/checksrv',
        headers={'X-Ya-Service-Ticket': service_ticket_src_100500_dst_42, 'Authorization': authtoken},
    )
    assert r.status_code == 403
    assert (
        r.text == '{"error":"Wrong ticket dst, expected 27, got 42",'
        '"debug_string":"ticket_type=service;expiration_time=9223372036854775807;src=100500;dst=42;scope=;",'
        '"logging_string":"3:serv:CBAQ__________9_IgYIlJEGECo:"}\n'
    )

    # Check user ticket
    # ok
    user_ticket_test = (
        '3:user:CA0Q__________9_GhIKBAiZkQYQmZEGINKF2MwEKAE:JHND5-2nKoBevSzwtVklV'
        'sQAq5cSEhVMBjf6pP4PLx-415DklyakIAbJgx7ufCeO0opRKIclKULQLkJFXGdZPFf2N63nUhTWB6UtwKFtMjcp'
        'mW_wo8oOY6yhFc4IJnKFirLQIC56qW7WPYX9D9bjL7bdF9zcb2YvEhQ1a_cH4qQ'
    )
    r = requests.get(
        tvmtool_url + '/tvm/checkusr', headers={'X-Ya-User-Ticket': user_ticket_test, 'Authorization': authtoken}
    )
    assert r.status_code == 200
    assert (
        r.text == '{"default_uid":100505,"uids":[100505],"scopes":null,'
        '"debug_string":"ticket_type=user;expiration_time=9223372036854775807;scope=;default_uid=100505;uid=100505;env=Test;",'
        '"logging_string":"3:user:CA0Q__________9_GhIKBAiZkQYQmZEGINKF2MwEKAE:"}\n'
    )

    # bad overriden env for good ticket
    r = requests.get(
        tvmtool_url + '/tvm/checkusr?override_env=testyateam',
        headers={'X-Ya-User-Ticket': user_ticket_test, 'Authorization': authtoken},
    )
    assert r.status_code == 403
    assert (
        r.text == '{"error":"user ticket is accepted from wrong blackbox enviroment. Env expected=Test, got=Test",'
        '"debug_string":"ticket_type=user;expiration_time=9223372036854775807;scope=;default_uid=100505;uid=100505;env=Test;",'
        '"logging_string":"3:user:CA0Q__________9_GhIKBAiZkQYQmZEGINKF2MwEKAE:"}\n'
    )

    # bad sign
    r = requests.get(
        tvmtool_url + '/tvm/checkusr', headers={'X-Ya-User-Ticket': user_ticket_test[:-1], 'Authorization': authtoken}
    )
    assert r.status_code == 403
    assert (
        r.text == '{"error":"internalVerifyPSSR(). invalid signature format - 3",'
        '"debug_string":"ticket_type=user;expiration_time=9223372036854775807;scope=;default_uid=100505;uid=100505;env=Test;",'
        '"logging_string":"3:user:CA0Q__________9_GhIKBAiZkQYQmZEGINKF2MwEKAE:"}\n'
    )

    # bad env
    user_ticket_prod = (
        '3:user:CAsQ__________9_GhIKBAiZkQYQmZEGINKF2MwEKAA:ASLBEirLBKGXhGXeZ9nO2'
        'KOxzGKJ3sDDzpzuuwElBAbnauvtQ2r6ElcniF2EZJkAlDHSTbk8YMhDlaL6yC04RoASfl-Ba7WgHN-fj1AOCzqV'
        'Q2rBZpZuenUkDyHrFaNrtNtme2eVLDTjedJNdWGC1mdKppN72Tm6g5DQpOOUPfk'
    )
    r = requests.get(
        tvmtool_url + '/tvm/checkusr', headers={'X-Ya-User-Ticket': user_ticket_prod, 'Authorization': authtoken}
    )
    assert r.status_code == 403
    assert (
        r.text == '{"error":"user ticket is accepted from wrong blackbox enviroment. Env expected=Test, got=Prod",'
        '"debug_string":"ticket_type=user;expiration_time=9223372036854775807;scope=;default_uid=100505;uid=100505;env=Prod;",'
        '"logging_string":"3:user:CAsQ__________9_GhIKBAiZkQYQmZEGINKF2MwEKAA:"}\n'
    )

    # ok overriden env for good ticket
    r = requests.get(
        tvmtool_url + '/tvm/checkusr?override_env=prod',
        headers={'X-Ya-User-Ticket': user_ticket_prod, 'Authorization': authtoken},
    )
    assert r.status_code == 200
    assert (
        r.text == '{"default_uid":100505,"uids":[100505],"scopes":null,"debug_string":'
        '"ticket_type=user;expiration_time=9223372036854775807;scope=;default_uid=100505;uid=100505;env=Prod;",'
        '"logging_string":"3:user:CAsQ__________9_GhIKBAiZkQYQmZEGINKF2MwEKAA:"}\n'
    )

    user_ticket_testyateam = (
        '3:user:CA4Q__________9_GhIKBAiZkQYQmZEGINKF2MwEKAM:IoUkXsJTNeuKShk'
        'Vfyl6qs3Z7yIB7wrTYbpXPn7dfv9iuPz1ATUEt--qE5mj6D2OfNU7ImreHhHyRH_v1WTxsGOV-JKaibqb3BnmfQ'
        'gSOz-RlmKj9MuWG8h3_Z_XnEMQeppv7KVPWzKWQg9HqxHuKiKsPgmZMtExx9tcdXcz6EE'
    )
    r = requests.get(
        tvmtool_url + '/tvm/checkusr?override_env=testyateam',
        headers={'X-Ya-User-Ticket': user_ticket_testyateam, 'Authorization': authtoken},
    )
    assert r.status_code == 200
    assert (
        r.text == '{"default_uid":100505,"uids":[100505],"scopes":null,'
        '"debug_string":"ticket_type=user;expiration_time=9223372036854775807;scope=;default_uid=100505;uid=100505;env=TestYateam;",'
        '"logging_string":"3:user:CA4Q__________9_GhIKBAiZkQYQmZEGINKF2MwEKAM:"}\n'
    )


@allure.story('Запуск тестов на интеграцию tvmtool и tvmapi')
class TvmtoolTests(unittest.TestCase):
    def test_tvmtool(self):
        """Проверка связки: клиент + tvmtool + tvmapi - проверка и выписка тикетов"""

        # Start tvmtool
        tvmtool_port = network.PortManager().get_tcp_port(8080)

        tvmtool_cfg = './tvmtool.conf'
        with open(tvmtool_cfg, 'w') as f:
            json.dump(
                {
                    "BbEnvType": 1,
                    "backends": {
                        "tvm_url": TVM_URL,
                    },
                    "clients": {
                        "me": {
                            "secret": "2LN58F3JHFD3dv4u6NlDbg",
                            "self_tvm_id": 27,
                            "dsts": {"he": {"dst_id": 29}, "she": {"dst_id": 35}},
                        }
                    },
                },
                f,
            )

        tvmtool_url = 'http://localhost:%d' % tvmtool_port
        authtoken = 'da9e6e7e74de980a28b95accadecf916'
        env['QLOUD_TVM_TOKEN'] = authtoken
        tvmtool = subprocess.Popen(
            [
                TVMTOOL_BIN,
                '--port',
                str(tvmtool_port),
                '-c',
                tvmtool_cfg,
            ],
            env=env,
            stdout=sys.stderr,
            stderr=sys.stderr,
        )
        _check_started_tvmtool(tvmtool_url)

        # Test tvmtool
        # TvmClient for tvmtool
        c = TvmClient(TvmToolClientSettings(self_alias='me', auth_token=authtoken, port=tvmtool_port))
        assert c.status == TvmClientStatus.Ok

        # Tickets with src=27 with ok-dst
        r = requests.get(tvmtool_url + '/tvm/tickets?src=27&dsts=he,she', headers={'Authorization': authtoken})
        assert r.status_code == 200
        assert ServiceContext(29, None, tp2u.TVMKNIFE_PUBLIC_KEYS).check(json.loads(r.text)['he']['ticket'])
        assert json.loads(r.text)['he']['tvm_id'] == 29
        assert ServiceContext(35, None, tp2u.TVMKNIFE_PUBLIC_KEYS).check(json.loads(r.text)['she']['ticket'])
        assert json.loads(r.text)['she']['tvm_id'] == 35
        assert len(json.loads(r.text)) == 2

        # Tickets with src=27 with bad-dst
        r = requests.get(tvmtool_url + '/tvm/tickets?src=27&dsts=100500', headers={'Authorization': authtoken})
        assert r.status_code == 400
        assert r.text == "can't find in config destination tvmid for src = 27, dstparam = 100500 (by number)"

        # Tickets with bad-src
        r = requests.get(tvmtool_url + '/tvm/tickets?src=100501&dsts=100500', headers={'Authorization': authtoken})
        assert r.status_code == 400
        assert (
            r.text == "can't find in config destination tvmid for src = 27, dstparam = 100500 (by number)"
        )  # TODO PASSP-21139

        default_checks(tvmtool_url, authtoken)

        c.stop()
        # Stoping
        tvmtool.send_signal(2)
        assert tvmtool.wait() == 0

    def test_tvmtool_only_check(self):
        """Проверка связки: клиент + tvmtool + tvmapi - только проверка тикетов"""

        # Start tvmtool
        tvmtool_port = network.PortManager().get_tcp_port(8080)

        tvmtool_cfg = './tvmtool.conf'
        with open(tvmtool_cfg, 'w') as f:
            json.dump({"BbEnvType": 1, "backends": {"tvm_url": TVM_URL}, "clients": {"me": {"self_tvm_id": 27}}}, f)

        tvmtool_url = 'http://localhost:%d' % tvmtool_port
        authtoken = 'da9e6e7e74de980a28b95accadecf916'
        env['QLOUD_TVM_TOKEN'] = authtoken
        tvmtool = subprocess.Popen(
            [
                TVMTOOL_BIN,
                '--port',
                str(tvmtool_port),
                '-c',
                tvmtool_cfg,
            ],
            env=env,
            stdout=sys.stderr,
            stderr=sys.stderr,
        )
        _check_started_tvmtool(tvmtool_url)

        # Test tvmtool
        # TvmClient for tvmtool
        c = TvmClient(TvmToolClientSettings(self_alias='me', auth_token=authtoken, port=tvmtool_port))
        assert c.status == TvmClientStatus.Ok

        # No tickets Tickets
        r = requests.get(tvmtool_url + '/tvm/tickets?src=27&dsts=he', headers={'Authorization': authtoken})
        assert r.status_code == 400
        assert r.text == "can't find in config destination tvmid for src = 27, dstparam = he (strconv)"

        default_checks(tvmtool_url, authtoken)

        # Stoping
        c.stop()
        tvmtool.send_signal(2)
        assert tvmtool.wait() == 0
