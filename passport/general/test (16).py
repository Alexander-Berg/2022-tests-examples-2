import base64
import json
import os
import re
import shutil
import subprocess
import sys
import time

import paramiko
import requests
from six import StringIO
import yatest.common as yc
from yatest.common import network


SHOOTER = yc.build_path() + '/passport/infra/daemons/shooting_gallery/shooter/cmd/shg-shooter'
CONFIG = './testing_out_stuff/shooter.conf'
env = os.environ.copy()

port_manager = network.PortManager()
PORT = port_manager.get_tcp_port(443)
URL = 'https://localhost:%d' % PORT
AMMO_DIR = './testing_out_stuff/ammo_dir'

SERVICE_TICKET = (
    '3:serv:CBAQ__________9_IggItYg9ELeIPQ:MbCQNQZ-hWTlrJukwbAewxq2WkONp6dk5w8NKZFpAjQGjN5L'
    'Y2Qy3mw3BcF4oARNtxzccs7HRtAM9W4EzD_qNzW9_Bsyi8dLXjM_CAr3439vH4oGqoQXrKPVahV-y9OJ3zoo-z'
    '7948y8baOGMlkxWS_bwnt7-bdfW_9FNmzGSiA'
)
TVM_HEADERS = {'X-Ya-Service-Ticket': SERVICE_TICKET}

with open(yc.source_path('passport/infra/daemons/shooting_gallery/shooter/ut/test_private.pem')) as f:
    PRIVATE_RSA_KEY = f.read()

requests.packages.urllib3.disable_warnings()


def _ssh_headers():
    pk = paramiko.RSAKey.from_private_key(
        StringIO(PRIVATE_RSA_KEY),
    )

    ts = str(int(time.time()))
    sign = base64.b64encode(pk.sign_ssh_data(ts.encode("utf-8")).asbytes()).decode("utf-8")

    return {
        'Authorization': 'my_robot %s %s' % (ts, sign),
    }


def _prepare_cfg():
    if os.path.isdir(AMMO_DIR):
        shutil.rmtree(AMMO_DIR)
    os.mkdir(AMMO_DIR)

    tvm_client_cache = './testing_out_stuff/tvmcache'
    if os.path.isdir(tvm_client_cache):
        shutil.rmtree(tvm_client_cache)
    os.mkdir(tvm_client_cache)

    with open("tvmapi.port") as f:
        tvmapi_port = int(f.read())

    tvm_client_config = './testing_out_stuff/tvmconfig.json'
    with open(tvm_client_config, 'wt') as out:
        out.write(json.dumps({'id': 1000503, 'secret': 'S3TyTYVqjlbsflVEwxj33w'}))

    config = {
        'http_common': {
            'port': PORT,
            'cert': yc.source_path('passport/infra/daemons/shooting_gallery/shooter/ut/cert/cert.pem'),
            'key': yc.source_path('passport/infra/daemons/shooting_gallery/shooter/ut/cert/key.pem'),
        },
        'http_unistat': {
            'port': port_manager.get_tcp_port(8080),
        },
        'logger': {
            'file': '_NOLOG_',
        },
        'shooter': {
            'access_log': './testing_out_stuff/shooter-access.log',
            'tvm': {
                'client': tvm_client_config,
                'cache_dir': tvm_client_cache,
                'allowed_tvm_id': [1000501],
                'staff_tvm_id': 1000502,
                'tvm_api_host': 'localhost',
                'tvm_api_port': tvmapi_port,
            },
            'ssh': {
                'staff_url': 'https://localhost:1',
                'staff_cache': yc.source_path('passport/infra/daemons/shooting_gallery/shooter/ut/staff_cache.json'),
                'allowed_ts_diff': 10,
                'allowed_logins': ['my_robot'],
            },
            'lock': {
                'max_duration': 3600,
            },
            'shooting': {
                'gor_path': yc.build_path()
                + '/passport/infra/daemons/shooting_gallery/shooter/ut/goreplay_mock/goreplay',
            },
            'ammo': {
                'dir': AMMO_DIR,
                'ttl': 3600,
                'min_duration': 5,
                'max_duration': 1200,
                'hosts': [
                    'pass-test-m1.passport.yandex.net',
                    'pass-test-s1.passport.yandex.net',
                ],
            },
        },
    }

    cfg = json.dumps(config)

    with open(CONFIG, 'wt') as out:
        out.write(cfg)


_prepare_cfg()


def _check_started(url, details, expected_code=200):
    i = 0
    while i < 150:
        i = i + 1
        try:
            r = requests.get(url, verify=False)
            assert r.status_code == expected_code
            print('check succed: %s' % details, file=sys.stderr)
            return
        except Exception as e:
            print('trying to check %s: %s' % (details, e), file=sys.stderr)
            time.sleep(0.1)

    assert False


def test_missing_config():
    p = subprocess.Popen(
        [
            SHOOTER,
            '-c',
            'missing_config',
        ],
        env=env,
        stdout=sys.stderr,
        stderr=sys.stderr,
    )
    assert p.wait() == 1


def test_ammo_create_and_delete():
    p = subprocess.Popen(
        [
            SHOOTER,
            '-c',
            CONFIG,
        ],
        env=env,
        stdout=sys.stderr,
        stderr=sys.stderr,
    )

    try:
        _check_started(URL + '/ping', 'shooter')

        # empty shooter
        r = requests.get(URL + '/cli/ammo/list', verify=False, headers=_ssh_headers())
        assert r.status_code == 200, r.text
        assert r.text == '{}'

        r = requests.get(
            URL + '/prospector/task?host=pass-test-s1.passport.yandex.net', verify=False, headers=_ssh_headers()
        )
        assert r.status_code == 200, r.text
        assert r.text == '{}'

        # lock
        r = requests.post(URL + '/cli/ammo/create', verify=False, headers=_ssh_headers())
        assert r.status_code == 400, r.text
        assert r.text == '{"error":"shooting gallery must be locked"}'

        r = requests.get(URL + '/cli/status', verify=False, headers=_ssh_headers())
        assert r.status_code == 200, r.text
        assert r.text == '{"status":"Idle"}'

        r = requests.post(URL + '/cli/lock', verify=False, headers=_ssh_headers())
        assert r.status_code == 200, r.text
        assert r.text == '{"status":"ok"}'

        r = requests.get(URL + '/cli/status', verify=False, headers=_ssh_headers())
        assert r.status_code == 200, r.text
        assert r.text == '{"status":"Locked","user":"my_robot"}'

        # errors in params
        r = requests.get(
            URL + '/cli/ammo/create?hosts=pass-s1.passport.yandex.net&duration=200',
            verify=False,
            headers=_ssh_headers(),
        )
        assert r.status_code == 400, r.text
        assert r.text == '{"error":"invalid HTTP method. Allowed: [POST]. Got: GET"}'

        r = requests.post(
            URL + '/cli/ammo/create?hosts=pass-s1.passport.yandex.net&duration=200',
            verify=False,
            headers=_ssh_headers(),
        )
        assert r.status_code == 400, r.text
        assert r.text == '{"error":"host is unknown: pass-s1.passport.yandex.net"}'

        r = requests.post(
            URL + '/cli/ammo/create?hosts=pass-test-s1.passport.yandex.net&duration=2',
            verify=False,
            headers=_ssh_headers(),
        )
        assert r.status_code == 400, r.text
        assert r.text == '{"error":"duration is too small: 2 vs 5 (cfg)"}'

        r = requests.post(
            URL + '/cli/ammo/create?hosts=pass-test-s1.passport.yandex.net&duration=200000000',
            verify=False,
            headers=_ssh_headers(),
        )
        assert r.status_code == 400, r.text
        assert r.text == '{"error":"duration is too large: 1200 (cfg) vs 200000000"}'

        # start creating ammo
        r = requests.post(
            URL + '/cli/ammo/create?hosts=pass-test-s1.passport.yandex.net&duration=20',
            verify=False,
            headers=_ssh_headers(),
        )
        assert r.status_code == 200, r.text
        ammo_pack_id = json.loads(r.text)['id']
        assert os.path.isdir(AMMO_DIR + '/' + ammo_pack_id)

        r = requests.get(
            URL + '/prospector/task?host=pass-test-s1.passport.yandex.net', verify=False, headers=_ssh_headers()
        )
        assert r.status_code == 200, r.text
        assert r.text == '{"id":"%s","duration":20}' % ammo_pack_id

        r = requests.post(
            URL + '/cli/ammo/create?hosts=pass-test-s1.passport.yandex.net&duration=20',
            verify=False,
            headers=_ssh_headers(),
        )
        assert r.status_code == 400, r.text
        assert r.text == '{"error":"shooter is not idle: creating_ammo"}'

        r = requests.get(URL + '/cli/ammo/list', verify=False, headers=_ssh_headers())
        assert r.status_code == 200, r.text
        assert r.text == '{"%s":{"hosts":null,"status":"InProgress","born":0,"size":0}}' % ammo_pack_id

        # Finish creating ammo
        with open('%s/%s/%s' % (AMMO_DIR, ammo_pack_id, 'pass-test-s1.passport.yandex.net.gz'), 'w') as f:
            f.write('qqqq')

        r = requests.get(URL + '/cli/ammo/list', verify=False, headers=_ssh_headers())
        assert r.status_code == 200, r.text
        assert (
            r.text
            == '{"%s":{"hosts":{"pass-test-s1.passport.yandex.net":{"status":"InProgress","born":0,"size":0}},"status":"InProgress","born":0,"size":0}}'
            % ammo_pack_id
        )

        with open('%s/%s/%s' % (AMMO_DIR, ammo_pack_id, 'pass-test-s1.passport.yandex.net.meta'), 'w') as f:
            f.write('{"status":"ok", "born":100500}')

        tries = 20
        while tries > 0:
            r = requests.get(URL + '/cli/ammo/list', verify=False, headers=_ssh_headers())
            assert r.status_code == 200, r.text
            if (
                r.text
                == '{"%s":{"hosts":{"pass-test-s1.passport.yandex.net":{"status":"Ready","born":100500,"size":4}},"status":"Ready","born":100500,"size":4}}'
                % ammo_pack_id
            ):
                break
            tries -= 1
            time.sleep(1)
        assert (
            r.text
            == '{"%s":{"hosts":{"pass-test-s1.passport.yandex.net":{"status":"Ready","born":100500,"size":4}},"status":"Ready","born":100500,"size":4}}'
            % ammo_pack_id
        )

        # delete it
        r = requests.post(URL + '/cli/ammo/delete?id=' + ammo_pack_id, verify=False, headers=_ssh_headers())
        assert r.status_code == 200, r.text
        assert r.text == '{"status":"ok"}'
        assert not os.path.isdir(AMMO_DIR + '/' + ammo_pack_id)

        r = requests.post(URL + '/cli/ammo/delete?id=' + ammo_pack_id, verify=False, headers=_ssh_headers())
        assert r.status_code == 400, r.text
        assert r.text == '{"error":"ammo is absent: %s"}' % ammo_pack_id

    finally:
        p.send_signal(2)

    assert p.wait() == 0


def test_ammo_create_and_cancel():
    p = subprocess.Popen(
        [
            SHOOTER,
            '-c',
            CONFIG,
        ],
        env=env,
        stdout=sys.stderr,
        stderr=sys.stderr,
    )

    try:
        _check_started(URL + '/ping', 'shooter')

        # empty shooter
        r = requests.get(URL + '/cli/ammo/list', verify=False, headers=_ssh_headers())
        assert r.status_code == 200, r.text
        assert r.text == '{}'

        r = requests.get(
            URL + '/prospector/task?host=pass-test-s1.passport.yandex.net', verify=False, headers=_ssh_headers()
        )
        assert r.status_code == 200, r.text
        assert r.text == '{}'

        r = requests.post(URL + '/cli/lock', verify=False, headers=_ssh_headers())
        assert r.status_code == 200, r.text
        assert r.text == '{"status":"ok"}'

        # start creating ammo
        r = requests.post(
            URL + '/cli/ammo/create?hosts=pass-test-s1.passport.yandex.net&duration=20',
            verify=False,
            headers=_ssh_headers(),
        )
        assert r.status_code == 200, r.text
        ammo_pack_id = json.loads(r.text)['id']
        assert os.path.isdir(AMMO_DIR + '/' + ammo_pack_id)

        r = requests.get(URL + '/cli/ammo/list', verify=False, headers=_ssh_headers())
        assert r.status_code == 200, r.text
        assert r.text == '{"%s":{"hosts":null,"status":"InProgress","born":0,"size":0}}' % ammo_pack_id

        r = requests.get(
            URL + '/prospector/task?host=pass-test-s1.passport.yandex.net', verify=False, headers=_ssh_headers()
        )
        assert r.status_code == 200, r.text
        assert r.text == '{"id":"%s","duration":20}' % ammo_pack_id

        # cancel
        r = requests.post(URL + '/cli/ammo/delete?id=' + ammo_pack_id, verify=False, headers=_ssh_headers())
        assert r.status_code == 200, r.text
        assert r.text == '{"extra_info":"task will stop soon","status":"ok"}'

        tries = 20
        while tries > 0:
            if not os.path.isdir(AMMO_DIR + '/' + ammo_pack_id):
                break
            tries -= 1
            time.sleep(1)
        assert not os.path.isdir(AMMO_DIR + '/' + ammo_pack_id)

    finally:
        p.send_signal(2)

    assert p.wait() == 0


def test_stateviewer_top():
    p = subprocess.Popen(
        [
            SHOOTER,
            '-c',
            CONFIG,
        ],
        env=env,
        stdout=sys.stderr,
        stderr=sys.stderr,
    )

    try:
        _check_started(URL + '/ping', 'shooter')

        ammo_pack_id = 'qwerty'
        if os.path.isdir(AMMO_DIR + '/' + ammo_pack_id):
            shutil.rmtree(AMMO_DIR + '/' + ammo_pack_id)
        os.mkdir(AMMO_DIR + '/' + ammo_pack_id)

        with open('%s/%s/%s' % (AMMO_DIR, ammo_pack_id, 'pass-test-s1.passport.yandex.net.gz'), 'w') as f:
            f.write('qqqq')
        with open('%s/%s/%s' % (AMMO_DIR, ammo_pack_id, 'pass-test-s1.passport.yandex.net.meta'), 'w') as f:
            f.write('{"status":"ok", "born":100500}')

        r = requests.post(URL + '/cli/lock', verify=False, headers=_ssh_headers())
        assert r.status_code == 200, r.text
        assert r.text == '{"status":"ok"}'

        # without shooting
        r = requests.get(URL + '/cli/state/top', verify=False, headers=_ssh_headers())
        assert r.status_code == 400, r.text
        assert r.text == '{"error":"there is no top in memory"}'

        r = requests.post(URL + '/stateviewer/top?timestamp=100500', data='qwerty', verify=False, headers=TVM_HEADERS)
        assert r.status_code == 200, r.text
        assert r.text == '{"status":"ok"}'

        r = requests.get(URL + '/cli/state/top', verify=False, headers=_ssh_headers())
        assert r.status_code == 200, r.text
        assert r.text == '{"output":"qwerty","timestamp":100500,"shooting":null}'

        # with shooting
        r = requests.post(
            URL + '/cli/shooting/start?ammo_id=qwerty&schema=https&rate=100500&instances=3',
            verify=False,
            headers=_ssh_headers(),
        )
        assert r.status_code == 200, r.text
        assert r.text == '{"status":"ok"}'

        r = requests.get(URL + '/cli/state/top', verify=False, headers=_ssh_headers())
        assert r.status_code == 200, r.text
        assert r.text == '{"output":"qwerty","timestamp":100500,"shooting":null}'

        r = requests.post(URL + '/stateviewer/top?timestamp=100501', data='asdfgh', verify=False, headers=TVM_HEADERS)
        assert r.status_code == 200, r.text
        assert r.text == '{"status":"ok"}'

        r = requests.get(URL + '/cli/state/top', verify=False, headers=_ssh_headers())
        assert r.status_code == 200, r.text
        resp = re.sub(r'"start_time":\d+,', '"start_time":xxxx,', r.text)
        assert (
            resp
            == '{"output":"asdfgh","timestamp":100501,"shooting":{"ammo_info":{"hosts":{"pass-test-s1.passport.yandex.net":{"status":"Ready","born":100500,"size":4}},"status":"Ready","born":100500,"size":4},"params":{"ammo_id":"qwerty","schema":"https","rate":100500,"instances":3,"duration":3600,"workers":128,"connection_close":false},"start_time":xxxx,"status":"Shooting"}}'  # noqa
        )

        # without again
        r = requests.post(URL + '/cli/shooting/stop', verify=False, headers=_ssh_headers())
        assert r.status_code == 200, r.text
        assert r.text == '{"status":"ok"}'

        r = requests.get(URL + '/cli/state/top', verify=False, headers=_ssh_headers())
        assert r.status_code == 200, r.text
        resp = re.sub(r'"start_time":\d+,', '"start_time":xxxx,', r.text)
        assert (
            resp
            == '{"output":"asdfgh","timestamp":100501,"shooting":{"ammo_info":{"hosts":{"pass-test-s1.passport.yandex.net":{"status":"Ready","born":100500,"size":4}},"status":"Ready","born":100500,"size":4},"params":{"ammo_id":"qwerty","schema":"https","rate":100500,"instances":3,"duration":3600,"workers":128,"connection_close":false},"start_time":xxxx,"status":"Shooting"}}'  # noqa
        )

        r = requests.post(URL + '/stateviewer/top?timestamp=100502', data='zxcvbn', verify=False, headers=TVM_HEADERS)
        assert r.status_code == 200, r.text
        assert r.text == '{"status":"ok"}'

        r = requests.get(URL + '/cli/state/top', verify=False, headers=_ssh_headers())
        assert r.status_code == 200, r.text
        assert r.text == '{"output":"zxcvbn","timestamp":100502,"shooting":null}'

    finally:
        p.send_signal(2)

    assert p.wait() == 0


def test_stateviewer_perf():
    p = subprocess.Popen(
        [
            SHOOTER,
            '-c',
            CONFIG,
        ],
        env=env,
        stdout=sys.stderr,
        stderr=sys.stderr,
    )

    try:
        _check_started(URL + '/ping', 'shooter')

        ammo_pack_id = 'qwerty'
        if os.path.isdir(AMMO_DIR + '/' + ammo_pack_id):
            shutil.rmtree(AMMO_DIR + '/' + ammo_pack_id)
        os.mkdir(AMMO_DIR + '/' + ammo_pack_id)

        with open('%s/%s/%s' % (AMMO_DIR, ammo_pack_id, 'pass-test-s1.passport.yandex.net.gz'), 'w') as f:
            f.write('qqqq')
        with open('%s/%s/%s' % (AMMO_DIR, ammo_pack_id, 'pass-test-s1.passport.yandex.net.meta'), 'w') as f:
            f.write('{"status":"ok", "born":100500}')

        r = requests.post(URL + '/cli/lock', verify=False, headers=_ssh_headers())
        assert r.status_code == 200, r.text
        assert r.text == '{"status":"ok"}'

        # without shooting
        # no task
        r = requests.get(URL + '/cli/state/perf', verify=False, headers=_ssh_headers())
        assert r.status_code == 400, r.text
        assert r.text == '{"error":"there is no perf data in memory"}'

        r = requests.get(URL + '/stateviewer/perf', verify=False, headers=TVM_HEADERS)
        assert r.status_code == 200, r.text
        assert r.text == '{"need_create":false,"frequency":0,"sleep":0}'

        # add task
        r = requests.post(URL + '/cli/state/perf', verify=False, headers=_ssh_headers())
        assert r.status_code == 200, r.text
        assert r.text == '{"status":"ok"}'

        r = requests.post(URL + '/cli/state/perf', verify=False, headers=_ssh_headers())
        assert r.status_code == 400, r.text
        assert r.text == '{"error":"perf is already being coollecting now"}'

        # check task
        r = requests.get(URL + '/cli/state/perf', verify=False, headers=_ssh_headers())
        assert r.status_code == 400, r.text
        assert r.text == '{"error":"perf data is still being collecting"}'

        r = requests.get(URL + '/stateviewer/perf', verify=False, headers=TVM_HEADERS)
        assert r.status_code == 200, r.text
        assert r.text == '{"need_create":true,"frequency":999,"sleep":30}'

        # finish task
        r = requests.post(URL + '/stateviewer/perf?timestamp=100500', data='qwerty', verify=False, headers=TVM_HEADERS)
        assert r.status_code == 200, r.text
        assert r.text == '{"status":"ok"}'

        r = requests.get(URL + '/cli/state/perf', verify=False, headers=_ssh_headers())
        assert r.status_code == 200, r.text
        assert r.text == '{"output":"qwerty","timestamp":100500,"shooting":null}'

        r = requests.get(URL + '/stateviewer/perf', verify=False, headers=TVM_HEADERS)
        assert r.status_code == 200, r.text
        assert r.text == '{"need_create":false,"frequency":0,"sleep":0}'

        # with shooting
        r = requests.post(
            URL + '/cli/shooting/start?ammo_id=qwerty&schema=https&rate=100500&instances=3',
            verify=False,
            headers=_ssh_headers(),
        )
        assert r.status_code == 200, r.text
        assert r.text == '{"status":"ok"}'

        # no task
        r = requests.get(URL + '/cli/state/perf', verify=False, headers=_ssh_headers())
        assert r.status_code == 200, r.text
        assert r.text == '{"output":"qwerty","timestamp":100500,"shooting":null}'

        r = requests.post(URL + '/stateviewer/perf?timestamp=100501', data='asdfgh', verify=False, headers=TVM_HEADERS)
        assert r.status_code == 200, r.text
        assert r.text == '{"status":"ok"}'

        r = requests.get(URL + '/cli/state/perf', verify=False, headers=_ssh_headers())
        assert r.status_code == 200, r.text
        resp = re.sub(r'"start_time":\d+,', '"start_time":xxxx,', r.text)
        assert (
            resp
            == '{"output":"asdfgh","timestamp":100501,"shooting":{"ammo_info":{"hosts":{"pass-test-s1.passport.yandex.net":{"status":"Ready","born":100500,"size":4}},"status":"Ready","born":100500,"size":4},"params":{"ammo_id":"qwerty","schema":"https","rate":100500,"instances":3,"duration":3600,"workers":128,"connection_close":false},"start_time":xxxx,"status":"Shooting"}}'  # noqa
        )

        # without again
        r = requests.post(URL + '/cli/shooting/stop', verify=False, headers=_ssh_headers())
        assert r.status_code == 200, r.text
        assert r.text == '{"status":"ok"}'

        r = requests.get(URL + '/cli/state/perf', verify=False, headers=_ssh_headers())
        assert r.status_code == 200, r.text
        resp = re.sub(r'"start_time":\d+,', '"start_time":xxxx,', r.text)
        assert (
            resp
            == '{"output":"asdfgh","timestamp":100501,"shooting":{"ammo_info":{"hosts":{"pass-test-s1.passport.yandex.net":{"status":"Ready","born":100500,"size":4}},"status":"Ready","born":100500,"size":4},"params":{"ammo_id":"qwerty","schema":"https","rate":100500,"instances":3,"duration":3600,"workers":128,"connection_close":false},"start_time":xxxx,"status":"Shooting"}}'  # noqa
        )

        r = requests.post(URL + '/stateviewer/perf?timestamp=100502', data='zxcvbn', verify=False, headers=TVM_HEADERS)
        assert r.status_code == 200, r.text
        assert r.text == '{"status":"ok"}'

        r = requests.get(URL + '/cli/state/perf', verify=False, headers=_ssh_headers())
        assert r.status_code == 200, r.text
        assert r.text == '{"output":"zxcvbn","timestamp":100502,"shooting":null}'

    finally:
        p.send_signal(2)

    assert p.wait() == 0


def test_stateviewer_perf_cancel():
    p = subprocess.Popen(
        [
            SHOOTER,
            '-c',
            CONFIG,
        ],
        env=env,
        stdout=sys.stderr,
        stderr=sys.stderr,
    )

    try:
        _check_started(URL + '/ping', 'shooter')

        ammo_pack_id = 'qwerty'
        if os.path.isdir(AMMO_DIR + '/' + ammo_pack_id):
            shutil.rmtree(AMMO_DIR + '/' + ammo_pack_id)
        os.mkdir(AMMO_DIR + '/' + ammo_pack_id)

        with open('%s/%s/%s' % (AMMO_DIR, ammo_pack_id, 'pass-test-s1.passport.yandex.net.gz'), 'w') as f:
            f.write('qqqq')
        with open('%s/%s/%s' % (AMMO_DIR, ammo_pack_id, 'pass-test-s1.passport.yandex.net.meta'), 'w') as f:
            f.write('{"status":"ok", "born":100500}')

        r = requests.post(URL + '/cli/lock', verify=False, headers=_ssh_headers())
        assert r.status_code == 200, r.text
        assert r.text == '{"status":"ok"}'

        # without shooting
        # no task
        r = requests.get(URL + '/cli/state/perf', verify=False, headers=_ssh_headers())
        assert r.status_code == 400, r.text
        assert r.text == '{"error":"there is no perf data in memory"}'

        r = requests.get(URL + '/stateviewer/perf', verify=False, headers=TVM_HEADERS)
        assert r.status_code == 200, r.text
        assert r.text == '{"need_create":false,"frequency":0,"sleep":0}'

        r = requests.post(URL + '/cli/state/perf_cancel', verify=False, headers=_ssh_headers())
        assert r.status_code == 400, r.text
        assert r.text == '{"error":"there is no perf task to cancel"}'

        # add task
        r = requests.post(URL + '/cli/state/perf', verify=False, headers=_ssh_headers())
        assert r.status_code == 200, r.text
        assert r.text == '{"status":"ok"}'

        # check task
        r = requests.get(URL + '/cli/state/perf', verify=False, headers=_ssh_headers())
        assert r.status_code == 400, r.text
        assert r.text == '{"error":"perf data is still being collecting"}'

        r = requests.get(URL + '/stateviewer/perf', verify=False, headers=TVM_HEADERS)
        assert r.status_code == 200, r.text
        assert r.text == '{"need_create":true,"frequency":999,"sleep":30}'

        # finish task
        r = requests.post(URL + '/cli/state/perf_cancel', verify=False, headers=_ssh_headers())
        assert r.status_code == 200, r.text
        assert r.text == '{"status":"ok"}'

        r = requests.post(URL + '/cli/state/perf_cancel', verify=False, headers=_ssh_headers())
        assert r.status_code == 400, r.text
        assert r.text == '{"error":"there is no perf task to cancel"}'

        r = requests.get(URL + '/cli/state/perf', verify=False, headers=_ssh_headers())
        assert r.status_code == 400, r.text
        assert r.text == '{"error":"there is no perf data in memory"}'

        r = requests.get(URL + '/stateviewer/perf', verify=False, headers=TVM_HEADERS)
        assert r.status_code == 200, r.text
        assert r.text == '{"need_create":false,"frequency":0,"sleep":0}'

    finally:
        p.send_signal(2)

    assert p.wait() == 0
