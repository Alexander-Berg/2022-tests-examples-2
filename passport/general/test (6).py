from yatest.common import network

import os
import requests
import subprocess
import sys
import time
import yatest.common as yc


XUNISTATER_BIN = yc.build_path() + '/passport/infra/daemons/xunistater/daemon/xunistater'
A2H_BIN = yc.build_path() + '/passport/infra/daemons/blackbox/tools/auth2his_sampler/bin/auth2his_sampler'
A2H_CONFIG_TEMPLATE = yc.source_path() + '/passport/infra/daemons/blackbox/tools/auth2his_sampler/config/config.xml'

XUNISTATER_CONFIG_PATH = './testing_out_stuff/xuni_cfg.conf'
A2H_CONFIG_PATH = './testing_out_stuff/cfg.conf'
ENV = os.environ.copy()


def _gen_xuni_cfg(port):
    cfg = (
        """<?xml version="1.0"?>
<config>
    <pools>
        <pool name="work_pool" threads="1" queue="10" max-delay="1000"/>
    </pools>
    <http_daemon>
        <port>"""
        + str(port)
        + """</port>
    </http_daemon>
    <component>
        <logger>
            <file>./testing_out_stuff/xnui.log</file>
            <level>DEBUG</level>
            <print-level>yes</print-level>
            <time-format>_DEFAULT_</time-format>
        </logger>
        <mem_storage>
            <http_path>/auth2his_sampler</http_path>
        </mem_storage>
    </component>
</config>
"""
    )

    with open(XUNISTATER_CONFIG_PATH, 'wt') as f:
        f.write(cfg)


def _gen_a2h_config(port):
    with open(A2H_CONFIG_TEMPLATE) as f:
        cfg = f.read()

    cfg = cfg.replace(
        '<file>/var/log/yandex/passport-auth2his-sampler/error.log</file>',
        '<file>_NOLOG_</file>',
    )
    cfg = cfg.replace('<limit>10000000</limit>', '<limit>100</limit>')
    cfg = cfg.replace('<port>10280</port>', '<port>' + str(port) + '</port>')

    with open(A2H_CONFIG_PATH, 'wt') as f:
        f.write(cfg)


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


def test_common():
    port = network.PortManager().get_tcp_port(8080)
    _gen_xuni_cfg(port)
    _gen_a2h_config(port)
    XUNI_URL = 'http://localhost:%d' % port

    xunistater = subprocess.Popen(
        [
            XUNISTATER_BIN,
            '-c',
            XUNISTATER_CONFIG_PATH,
        ],
        env=ENV,
        stdout=sys.stderr,
        stderr=sys.stderr,
    )
    a2h = None
    try:
        _check_started_xunistater(XUNI_URL)

        a2h = subprocess.Popen(
            [
                A2H_BIN,
                '-c',
                A2H_CONFIG_PATH,
            ],
            env=ENV,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=sys.stderr,
        )

        a2h.stdin.write(b'x1;y1;z1;1 2119-09-04T19:35:44.315608+03 7F bb 4001096104 - - ')
        time.sleep(1)
        a2h.stdin.write(
            b'oauthcheck successful clid=5e8656ef62914d738a9865ebf1e999b9;tokid=15676149431234001096104;devid=ca2c4cfc56ed4465861356647d76865b;scope=test:limited; 0.0.13.0 - - - - -\n'
            + b'x2;y2;z2;1 2119-09-04T19:35:44.315608+03 7F bb 4001096104 - - oauthcheck successful clid=5e8656ef62914d738a9865ebf1e999b9;tokid=15676149431234001096104;devid=ca2c4cfc56ed4465861356647d76865b;scope=test:limited; 0.0.13.0 - - - - -\n'  # noqa
            + b'x3;y3;z3;1 2119-09-04T19:35:44.315608+03 7F bb 4001096104 - - oauthcheck successful clid=5e8656ef62914d738a9865ebf1e999b9;tokid=25676149431234001096104;devid=ca2c4cfc56ed4465861356647d76865b;scope=test:limited; 0.0.13.0 - - - - -'  # noqa
        )
        a2h.stdin.close()

        res = a2h.stdout.read()

        assert (
            b'x1;y1;z1;1 2119-09-04T19:35:44.315608+03 7F bb 4001096104 - - oauthcheck successful clid=5e8656ef62914d738a9865ebf1e999b9;tokid=15676149431234001096104;devid=ca2c4cfc56ed4465861356647d76865b;scope=test:limited; 0.0.13.0 - - - - -\n'  # noqa
            + b'x3;y3;z3;1 2119-09-04T19:35:44.315608+03 7F bb 4001096104 - - oauthcheck successful clid=5e8656ef62914d738a9865ebf1e999b9;tokid=25676149431234001096104;devid=ca2c4cfc56ed4465861356647d76865b;scope=test:limited; 0.0.13.0 - - - - -\n'  # noqa
            == res
        )
    finally:
        xunistater.send_signal(2)
        assert xunistater.wait() == 0
        if a2h is not None:
            a2h.stdin.close()
            assert a2h.wait() == 0
