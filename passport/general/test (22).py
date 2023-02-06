from yatest.common import network

import json
import os
import requests
import subprocess
import sys
import time
import yatest.common as yc


XUNISTATER_BIN = yc.build_path() + '/passport/infra/daemons/xunistater/daemon/xunistater'
TEST_DATA = yc.source_path() + '/passport/infra/daemons/xunistater/ut_py/'

CONFIG_PATH = './testing_out_stuff/cfg.conf'
FILE_1 = './testing_out_stuff/in.log.1'
FILE_2 = './testing_out_stuff/in.log.2'
FILE_3 = './testing_out_stuff/in.log.3'
FILE_4 = './testing_out_stuff/in.log.4'
FILE_5 = './testing_out_stuff/in.log.5'
FILE_6 = './testing_out_stuff/in.log.6'
FILE_100500 = './testing_out_stuff/in.log.100500'
ENV = os.environ.copy()


def _gen_config():
    with open(TEST_DATA + 'config_template.xml') as f:
        cfg = f.read()

    port = network.PortManager().get_tcp_port(8080)
    port_self = network.PortManager().get_tcp_port(8081)

    cfg = cfg.replace('{http-port}', str(port))
    cfg = cfg.replace('{http-port2}', str(port_self))

    with open(CONFIG_PATH, 'wt') as f:
        f.write(cfg)

    return port, port_self


def _clear_files():
    if os.path.isfile(FILE_1):
        os.remove(FILE_1)
    if os.path.isfile(FILE_2):
        os.remove(FILE_2)
    if os.path.isfile(FILE_3):
        os.remove(FILE_3)
    if os.path.isfile(FILE_4):
        os.remove(FILE_4)
    if os.path.isfile(FILE_5):
        os.remove(FILE_5)


def _check_started_xunistater(url, expected_code=200):
    i = 0
    while i < 150:
        i = i + 1
        try:
            r = requests.get(url + "/ping")
            assert r.status_code == expected_code
            return
        except Exception as e:
            print(e, file=sys.stderr)
            time.sleep(0.1)

    assert False


HTTP_PORT, HTTP_PORT_SELF = _gen_config()
URL = 'http://localhost:%d' % HTTP_PORT


def test_no_file():
    _clear_files()

    xunistater = subprocess.Popen(
        [
            XUNISTATER_BIN,
            '-c',
            CONFIG_PATH,
        ],
        env=ENV,
        stdout=sys.stderr,
        stderr=sys.stderr,
    )

    try:
        _check_started_xunistater(url=URL, expected_code=500)
        _check_started_xunistater(url=URL + "/self_unistat", expected_code=500)
    finally:
        xunistater.send_signal(2)
        assert xunistater.wait() == 0


def test_files():
    _clear_files()

    f1 = open(FILE_1, 'w')
    f2 = open(FILE_2, 'w')
    f3 = open(FILE_3, 'w')
    f4 = open(FILE_4, 'w')
    f5 = open(FILE_5, 'w')

    xunistater = subprocess.Popen(
        [
            XUNISTATER_BIN,
            '-c',
            CONFIG_PATH,
        ],
        env=ENV,
        stdout=sys.stderr,
        stderr=sys.stderr,
    )

    try:
        _check_started_xunistater(URL)

        r = requests.get(URL + "/path1")
        assert (
            r.text
            == '[["upstream_answer_time_dhhh",[[0,0],[1,0],[3,0],[5,0],[10,0],[20,0],[50,0],[100,0],[250,0],[1000,0],[3000,0]]],["full_answer_time_dhhh",[[0,0],[1,0],[3,0],[5,0],[10,0],[20,0],[50,0],[100,0],[250,0],[1000,0],[3000,0]]],["25_dec_dmmm",0],["rps_dmmm",0],["mda0_dmmm",0]]'  # noqa
        )
        assert r.status_code == 200

        r = requests.get(URL + "/path2")
        assert (
            r.text
            == '[["upstream_answer_time_dhhh",[[0,0],[1,0],[3,0],[5,0],[10,0],[20,0],[50,0],[100,0],[250,0],[1000,0],[3000,0]]],["codes_5XX_dmmm",0],["rps_dmmm",0],["sessionid_dmmm",0],["__errors.parsing_dmmm",0]]'  # noqa
        )
        assert r.status_code == 200

        r = requests.get(URL + "/path3")
        assert (
            r.text
            == '[["codes_5XX_dmmm",0],["badsessionid_dmmm",0],["sessionid_dmmm",0],["requests_localhost_all_accounts_dmmx",0],["__errors.parsing_dmmm",0]]'
        )
        assert r.status_code == 200

        r = requests.get(URL + "/path4")
        assert (
            r.text
            == '[["rps_dhhh",0],["full_answer_time_dhhh",[[0,0],[1,0],[2,0],[3,0],[4,0],[5,0],[6,0],[7,0],[8,0],[9,0],[10,0],[12,0],[15,0],[17,0],[20,0],[25,0],[30,0],[35,0],[40,0],[45,0],[50,0],[60,0],[70,0],[80,0],[90,0],[100,0],[125,0],[150,0],[175,0],[200,0],[225,0],[250,0],[275,0],[300,0],[400,0],[500,0],[750,0],[1000,0],[2000,0],[3000,0]]],["upstream_answer_time_dhhh",[[0,0],[1,0],[3,0],[5,0],[10,0],[20,0],[50,0],[100,0],[250,0],[1000,0],[3000,0]]],["code.404_dhhh",0],["code.499_dhhh",0],["__errors.parsing_dmmm",0]]'  # noqa
        )
        assert r.status_code == 200

        r = requests.get(URL + "/path5")
        assert (
            r.text
            == '[["rps_dmmm",0],["mode_verify_dmmm",0],["needs_refresh_dmmm",0],["subrequests_dmmm",0.0],["__errors.parsing_dmmm",0]]'
        )
        assert r.status_code == 200

        r = requests.get(URL + "/path6")
        assert r.text == '[["rps_dmmm",0],["__errors.parsing_dmmm",0]]'
        assert r.status_code == 200

        r = requests.get(URL + "/path7")
        assert r.text == '[["__errors.storing_dmmm",0]]'
        assert r.status_code == 200

        r = requests.get(URL + "/path8")
        assert r.text == '[["__errors.storing_dmmm",0]]'
        assert r.status_code == 200

        r = requests.get(URL + "/path9")
        assert r.text == '[["rps_l1_dmmm",0],["rps_l5_dmmm",0],["__errors.parsing_dmmm",0],["__errors.storing_dmmm",0]]'
        assert r.status_code == 200

        r = requests.get(URL + "/path10")
        assert r.status_code == 404

        f6 = open(FILE_6, 'w')

        f1.write(
            '2a02:6b8:c04:202:8000:611:0:89 [25/Dec/2018:01:02:01 +0300] 0.001 0.002 "200" http pass-load.sezam.yandex.net "ace0b0244cd846d1c30efe9e04485edb"\n'
        )
        f1.write(
            '2a02:6b8:c04:202:8000:611:0:88 [25/Dec/2018:01:02:01 +0300] 0.003 0.004 "500" http pass-load.sezam.yandex.net "f29b4d3bca6e34f68f676178d57f4d25"\n'
        )
        f1.close()

        f2.write(
            '2a02:6b8:c02:500:8000:611:0:1d - api.cerevra-dev-xenial.passport.yandex.net - [08/Oct/2018:11:54:28 +0300] '
            'api.cerevra-dev-xenial.passport.yandex.net:443 0.001 0.001 120 "GET /suggested_accounts/?multi=yes HTTP/1.1" '
            '"200" 15 "-" "-" "-" "" "-" "2ca4f81c21b7449bef3a490ecb2ea4e1"\n'
        )
        f2.write(
            '2a02:6b8:c02:500:8000:611:0:1d - api.cerevra-dev-xenial.passport.yandex.net.yandex.ru - [11/Dec/2018:12:21:50 +0300] '
            'api.cerevra-dev-xenial.passport.yandex.net:443 0.009 0.009 219 "POST /all_accounts/ HTTP/1.0" "200" 159 "-" "-" "-" '
            '"Session_id=3:1544520101.2.0.1544519111111:AQAAfw:127.0|113.-1.0|1:300778.9383.XXXXXXXXXXXXXXXXXXXXXXXXXXX" "-" "f7fae6a7e36485fd7fd5a51faa6b85f1"\n'
        )
        f2.close()

        f3.write(
            '2a02:6b8:c02:500:8000:611:0:1d - api.cerevra-dev-xenial.passport.yandex.net - [08/Oct/2018:11:54:28 +0300] '
            'api.cerevra-dev-xenial.passport.yandex.net:443 0.001 0.001 120 "GET /suggested_accounts/?multi=yes HTTP/1.1" '
            '"200" 15 "-" "-" "-" "" "-" "2ca4f81c21b7449bef3a490ecb2ea4e1"\n'
        )
        f3.write(
            '2a02:6b8:c02:500:8000:611:0:1d - api.cerevra-dev-xenial.passport.yandex.net.yandex.ru - [11/Dec/2018:12:21:50 +0300] '
            'api.cerevra-dev-xenial.passport.yandex.net:443 0.009 0.009 219 "POST /all_accounts/ HTTP/1.1" "500" 159 "-" "-" "-" '
            '"Session_id=3:1544520101.2.0.1544519111111:AQAAfw:127.0|113.-1.0|1:300778.9383.XXXXXXXXXXXXXXXXXXXXXXXXXXX" "-" "f7fae6a7e36485fd7fd5a51faa6b85f1"\n'
        )
        f3.close()

        f4.write(
            '[2019-02-01 +0300] kek 100.500 178.501 17 lol /ping?key=value foo "499" 700 bar "some mega string" hu "GET"\n'
        )
        f4.write(
            '[2019-02-01 +0300] kek 17.500 32.501 17 lol /ping?key=value foo "502" 700 bar "some mega string" hu "POST"\n'
        )
        f4.close()

        f5.write('tskv	\n')
        f5.write('tskv	mode=verify_token	by_alias=1	needs_refresh=1	reason=kek	__consumer=1:passport:2\n')
        f5.write(
            'tskv	mode=verify_token	by_alias=0	needs_refresh=1	reason="kek2_scopes.wrong"	subreqs=10	__consumer=1:passport:4\n'
        )
        f5.write('tskv	mode=verify_token	by_alias=0	needs_refresh=0	reason="kek3"	subreqs=18\n')
        f5.write('tskv	mode=verify_token	by_alias=2	needs_refresh=0	reason="kek3"	subreqs=18\n')
        f5.close()

        f6.write('lol\n')
        f6.close()

        time.sleep(5)

        r = requests.get(URL + "/path1")
        assert (
            r.text
            == '[["upstream_answer_time_dhhh",[[0,0],[1,1],[3,1],[5,0],[10,0],[20,0],[50,0],[100,0],[250,0],[1000,0],[3000,0]]],["full_answer_time_dhhh",[[0,0],[1,1],[3,1],[5,0],[10,0],[20,0],[50,0],[100,0],[250,0],[1000,0],[3000,0]]],["25_dec_dmmm",2],["rps_dmmm",2],["code.200_dmmm",1],["code.500_dmmm",1],["mda0_dmmm",1],["load.on.net_2a02:6b8:c04:202:8000:611:0:89_response_time_dhhh",[[0,0],[1,0],[2,1],[3,0],[4,0],[5,0],[6,0],[7,0],[8,0],[9,0],[10,0],[12,0],[15,0],[17,0],[20,0],[25,0],[30,0],[35,0],[40,0],[45,0],[50,0],[60,0],[70,0],[80,0],[90,0],[100,0],[125,0],[150,0],[175,0],[200,0],[225,0],[250,0],[275,0],[300,0],[400,0],[500,0],[750,0],[1000,0],[2000,0],[3000,0]]],["load.on.net_2a02:6b8:c04:202:8000:611:0:88_response_time_dhhh",[[0,0],[1,0],[2,0],[3,0],[4,1],[5,0],[6,0],[7,0],[8,0],[9,0],[10,0],[12,0],[15,0],[17,0],[20,0],[25,0],[30,0],[35,0],[40,0],[45,0],[50,0],[60,0],[70,0],[80,0],[90,0],[100,0],[125,0],[150,0],[175,0],[200,0],[225,0],[250,0],[275,0],[300,0],[400,0],[500,0],[750,0],[1000,0],[2000,0],[3000,0]]]]'  # noqa
        )
        assert r.status_code == 200

        r = requests.get(URL + "/path2")
        assert (
            r.text
            == '[["upstream_answer_time_dhhh",[[0,0],[1,1],[3,0],[5,1],[10,0],[20,0],[50,0],[100,0],[250,0],[1000,0],[3000,0]]],'
            '["codes_5XX_dmmm",0],'
            '["rps_dmmm",2],'
            '["method.GET_dmmm",1],'
            '["method.POST_dmmm",1],'
            '["method_filtered.GET_dmmm",1],'
            '["http_version.1.lol.0_dmmm",1],'
            '["http_version.1.lol.1_dmmm",1],'
            '["sessionid_dmmm",1],["__errors.parsing_dmmm",0]]'
        )
        assert r.status_code == 200

        r = requests.get(URL + "/path3")
        assert (
            r.text
            == '[["codes_5XX_dmmm",1],["badsessionid_dmmm",0],["sessionid_dmmm",1],["requests_localhost_all_accounts_dmmx",0],["requests_api.cerevra-dev-xenial.passport.yandex.net_all_accounts_dmmx",0],["requests_localhost_suggested_accounts_dmmx",0],["requests_api.cerevra-dev-xenial.passport.yandex.net_suggested_accounts_dmmx",1],["requests_api.cerevra-dev-xenial.passport.yandex.net.yandex.ru_all_accounts_dmmx",1],["__errors.parsing_dmmm",0]]'  # noqa
        )
        assert r.status_code == 200

        r = requests.get(URL + "/path4")
        assert (
            r.text
            == '[["rps_dhhh",2],["full_answer_time_dhhh",[[0,0],[1,0],[2,0],[3,0],[4,0],[5,0],[6,0],[7,0],[8,0],[9,0],[10,0],'
            '[12,0],[15,0],[17,0],[20,0],[25,0],[30,0],[35,0],[40,0],[45,0],[50,0],[60,0],[70,0],[80,0],[90,0],[100,0],[125,0],[150,0],'
            '[175,0],[200,0],[225,0],[250,0],[275,0],[300,0],[400,0],[500,0],[750,0],[1000,0],[2000,0],[3000,2]]],'
            '["upstream_answer_time_dhhh",[[0,0],[1,0],[3,0],[5,0],[10,0],[20,0],[50,0],[100,0],[250,0],[1000,0],[3000,2]]],'
            '["path.\\/ping_dhhh",2],["code.404_dhhh",0],["code.499_dhhh",1],["code.502_dhhh",1],["method_filtered.GET_dhhh",1],["__errors.parsing_dmmm",0]]'
        )
        assert r.status_code == 200

        r = requests.get(URL + "/path5")
        assert (
            r.text
            == '[["rps_dmmm",2],["mode_verify_dmmm",2],["needs_refresh_dmmm",1],["reason.kek3_dmmm",1],["subrequests_dmmm",28.0],["oauth.mode_verify_token.consumer_passport.needs_refresh_dmmm",1.0],["oauth.mode_verify_token.needs_refresh_dmmm",0.0],["oauth.by_alias.true_dmmm",1],["oauth.by_alias.false_dmmm",2],["oauth.by_alias.WTF_dmmm",1],["__errors.parsing_dmmm",1]]'  # noqa
        )
        assert r.status_code == 200

        r = requests.get(URL + "/path6")
        assert r.text == '[["rps_dmmm",1],["__errors.parsing_dmmm",0]]'
        assert r.status_code == 200

        r = requests.get(URL + "/path7")
        assert r.text == '[["__errors.storing_dmmm",0]]'
        assert r.status_code == 200

        r = requests.get(URL + "/path8")
        assert r.text == '[["__errors.storing_dmmm",0]]'
        assert r.status_code == 200

        r = requests.post(URL + "/path9", '{"rps_m_dmmm":{"value":100500}}')
        assert r.status_code == 200
        r = requests.get(URL + "/path9")
        assert (
            r.text
            == '[["rps_l1_dmmm",2],["rps_l5_dmmm",4],["rps_m_dmmm",100500.0],["__errors.parsing_dmmm",1],["__errors.storing_dmmm",0]]'
        )
        assert r.status_code == 200

        r = requests.get(URL + "/path10")
        assert r.status_code == 404

        r = requests.get('http://localhost:%d/self_unistat/' % HTTP_PORT_SELF)
        assert '["errors.parsing_dmmm",2],["errors.storing_dmmm",0]' in r.text
        assert r.status_code == 200

    finally:
        xunistater.send_signal(2)
        assert xunistater.wait() == 0


def test_logrotate():
    _clear_files()
    open(FILE_1, 'w').close()
    open(FILE_2, 'w').close()
    open(FILE_3, 'w').close()
    open(FILE_4, 'w').close()
    open(FILE_5, 'w').close()
    open(FILE_100500, 'w').close()

    xunistater = subprocess.Popen(
        [
            XUNISTATER_BIN,
            '-c',
            CONFIG_PATH,
        ],
        env=ENV,
        stdout=sys.stderr,
        stderr=sys.stderr,
    )

    try:
        _check_started_xunistater(URL)

        os.rename(FILE_2, FILE_2 + '.old')
        os.remove(FILE_100500)  # for tryReopenFile()

        r = requests.get(URL + "/path2")
        assert (
            r.text
            == '[["upstream_answer_time_dhhh",[[0,0],[1,0],[3,0],[5,0],[10,0],[20,0],[50,0],[100,0],[250,0],[1000,0],[3000,0]]],'
            '["codes_5XX_dmmm",0],["rps_dmmm",0],["sessionid_dmmm",0],["__errors.parsing_dmmm",0]]'
        )
        assert r.status_code == 200

        f2 = open(FILE_2, 'w')

        f2.write(
            '2a02:6b8:c02:500:8000:611:0:1d - api.cerevra-dev-xenial.passport.yandex.net - [08/Oct/2018:11:54:28 +0300] '
            'api.cerevra-dev-xenial.passport.yandex.net:443 0.001 0.001 120 "GET /suggested_accounts/?multi=yes HTTP/1.1" '
            '"200" 15 "-" "-" "-" "" "-" "2ca4f81c21b7449bef3a490ecb2ea4e1"\n'
        )
        f2.write(
            '2a02:6b8:c02:500:8000:611:0:1d - api.cerevra-dev-xenial.passport.yandex.net.yandex.ru - [11/Dec/2018:12:21:50 +0300] '
            'api.cerevra-dev-xenial.passport.yandex.net:443 0.009 0.009 219 "POST /all_accounts/ HTTP/1.1" "200" 159 "-" "-" "-" '
            '"Session_id=3:1544520101.2.0.1544519111111:AQAAfw:127.0|113.-1.0|1:300778.9383.XXXXXXXXXXXXXXXXXXXXXXXXXXX" "-" "f7fae6a7e36485fd7fd5a51faa6b85f1"\n'
        )
        f2.close()

        time.sleep(5)

        r = requests.get(URL + "/path2")
        assert (
            r.text
            == '[["upstream_answer_time_dhhh",[[0,0],[1,1],[3,0],[5,1],[10,0],[20,0],[50,0],[100,0],[250,0],[1000,0],[3000,0]]],'
            '["codes_5XX_dmmm",0],'
            '["rps_dmmm",2],'
            '["method.GET_dmmm",1],'
            '["method.POST_dmmm",1],'
            '["method_filtered.GET_dmmm",1],'
            '["http_version.1.lol.1_dmmm",2],'
            '["sessionid_dmmm",1],["__errors.parsing_dmmm",0]]'
        )
        assert r.status_code == 200

        xunistater.send_signal(1)
    finally:
        xunistater.send_signal(2)
        assert xunistater.wait() == 0


def test_mem_storage():
    _clear_files()

    open(FILE_1, 'w')
    open(FILE_2, 'w')
    open(FILE_3, 'w')
    open(FILE_4, 'w')
    open(FILE_5, 'w')

    xunistater = subprocess.Popen(
        [
            XUNISTATER_BIN,
            '-c',
            CONFIG_PATH,
        ],
        env=ENV,
        stdout=sys.stderr,
        stderr=sys.stderr,
    )

    try:
        _check_started_xunistater(URL)

        r = requests.post(URL + "/path7", "{}")
        assert r.text == '{"status":"OK"}\n'
        assert r.status_code == 200

        r = requests.post(URL + "/path7", "{{}")
        assert json.loads(r.text)["status"] == "ERROR"
        assert (
            json.loads(r.text)["error"]
            == "passport/infra/daemons/xunistater/src/storage/request_parser.cpp:14: invalid json object: '{{}'"
        )
        assert r.status_code == 400

        r = requests.get(URL + "/path7")
        assert r.text == '[["__errors.storing_dmmm",1]]'
        assert r.status_code == 200

        r = requests.get(URL + "/path8")
        assert r.text == '[["__errors.storing_dmmm",0]]'
        assert r.status_code == 200

        r = requests.post(
            URL + "/path7",
            '{"key1_dmmm":{"value":100},"key1_dmmm":{"value":100.0625},"key2_ammm":{"value":80},"key2_ammm":{"value":20}}',
        )
        assert r.text == '{"status":"OK"}\n'
        assert r.status_code == 200

        r = requests.post(URL + "/path8", '{"key1_dmmm":{"value":18},"key2_ammm":{"value":3}}')
        assert r.text == '{"status":"OK"}\n'
        assert r.status_code == 200

        r = requests.get(URL + "/path7")
        assert r.text == '[["key1_dmmm",200.0625],["key2_ammm",20.0],["__errors.storing_dmmm",1]]'
        assert r.status_code == 200

        r = requests.get(URL + "/path8")
        assert r.text == '[["key1_dmmm",18.0],["key2_ammm",3.0],["__errors.storing_dmmm",0]]'
        assert r.status_code == 200

        r = requests.get(URL + "/path8")
        assert r.text == '[["key1_dmmm",18.0],["key2_ammm",3.0],["__errors.storing_dmmm",0]]'
        assert r.status_code == 200

        r = requests.put(URL + "/path8")
        assert r.text == 'unknown method: PUT'
        assert r.status_code == 404

        r = requests.post(URL + "/path100500", '{}')
        assert r.text == 'unknown path in POST: /path100500'
        assert r.status_code == 404

    finally:
        xunistater.send_signal(2)
        assert xunistater.wait() == 0
