import os
import re
import shutil
import subprocess
import sys
import time

from passport.infra.recipes.common import log
import requests
import yatest.common as yc
from yatest.common import network
from yatest.common import process


port_manager = network.PortManager()

output_path = yc.output_path()
tests_path = yc.source_path('passport/infra/daemons/sezamapi/last-tests')
ylast_config = yc.output_path('last.conf')
sezamapi_bin = yc.build_path() + '/passport/infra/daemons/sezamapi/daemon/sezamapi'

tvm_host = 'http://127.0.0.1'

try:
    with open('./tvmapi.port') as f:
        tvm_port = f.read()
except IOError:
    log('Could not find tvm port file: ./tvmapi.port')

# check that blackbox is running
blackbox_port = os.environ['RECIPE_BLACKBOX_PORT']

# get other ports
mysql_port = os.environ['RECIPE_MYSQL_PORT']

# prepare nginx config
nginx_port = port_manager.get_tcp_port(8080)
log('nginx_port: %d' % nginx_port)

# prepare SEZAMAPI config
sezamapi_port = port_manager.get_tcp_port(80)
log('sezamapi_port: %d' % sezamapi_port)

SECRET = './testing_out_stuff/tvm.secret'
TVM_CACHE = './testing_out_stuff'

sezamapi_config = './testing_out_stuff/sezamapi.daemon'
with open(sezamapi_config, 'wt') as f:
    process.py_execute(
        [
            yc.source_path('passport/infra/daemons/sezamapi/config/prepare_sezamapi.py'),
            yc.source_path('passport/infra/daemons/sezamapi/config/template-sezamapi.conf'),
            'autotest',
            '',
        ],
        stdout=f,
    )

with open(sezamapi_config) as f:
    config = f.read()
    config = config.replace('<port>10085</port>', '<port>%s</port>' % sezamapi_port)
    config = config.replace('<port>10185</port>', '<port>%s</port>' % port_manager.get_tcp_port(10185))
    config = config.replace(
        '<monitor_port>3338</monitor_port>', '<monitor_port>%s</monitor_port>' % port_manager.get_tcp_port(10185)
    )
    config = config.replace('<db_port>80</db_port>', '<db_port>%s</db_port>' % nginx_port)
    config = config.replace('<get_timeout>100</get_timeout>', '<get_timeout>10000</get_timeout>')
    config = config.replace('<query_timeout>1000</query_timeout>', '<query_timeout>20000</query_timeout>')
    config = config.replace('<connect_timeout>500</connect_timeout>', '<connect_timeout>50000</connect_timeout>')
    config = config.replace('/var/log/yandex/passport-sezam-api/', './testing_out_stuff/')
    config = config.replace('/var/run/passport/', './testing_out_stuff/')
    config = config.replace('/etc/yandex/passport-sezam-api/tvm.secret', SECRET)
    config = config.replace('/var/cache/yandex/passport-sezamapi', TVM_CACHE)
    config = config.replace('<host>https://tvm-api.yandex.net</host>', '<host>{}</host>'.format(tvm_host))
    config = config.replace('<port>443</port>', '<port>{}</port>'.format(tvm_port))
    config = config.replace(
        '<geobase>/var/cache/geobase/geodata4.bin</geobase>',
        '<geobase>%s/test-geodata.bin</geobase>' % yc.work_path(),
    )

    with open(sezamapi_config, 'wt') as out:
        out.write(config)


# prepare LAST config

with open(yc.source_path('passport/infra/daemons/sezamapi/last-tests/last.conf')) as f:
    config = f.read()
    config = config.replace('<port>3306</port>', '<port>%s</port>' % mysql_port)
    config = config.replace('<host>cnt-dbm-test.passport.yandex.net</host>', '<host>127.0.0.1</host>')
    blackbox_host_finder = re.compile('(?P<head><blackbox_host>)[^<]+(?P<tail></blackbox_host>)')
    config = blackbox_host_finder.sub(r'\g<head>localhost\g<tail>', config)
    gamma_keeper_finder = re.compile('(?P<head><gamma id="1">)[^<]+(?P<tail></gamma>)')
    config = gamma_keeper_finder.sub(
        r'\g<head>wUdYkYEMhuzoGeNB42QeaGgYzcfpRGe6ct/QUjCdSM2q86cWjTOv1Q9r8SFBFcT2JuP47GnPs49+FRDC7bWjOQ==\g<tail>',
        config,
    )

    with open(ylast_config, 'wt') as out:
        out.write(config)


def _check_started(url, details, expected_code=200):
    i = 0
    while i < 150:
        i = i + 1
        try:
            r = requests.get(url)
            assert r.status_code == expected_code
            print('check succed: %s' % details, file=sys.stderr)
            return
        except Exception as e:
            print('trying to check %s: %s' % (details, e), file=sys.stderr)
            time.sleep(0.1)

    assert False


def test_basic():
    nginx = None
    sezamapi = None
    try:
        nginx = subprocess.Popen(
            [
                yc.build_path() + '/passport/infra/daemons/sezamapi/ut_last/nginx_mock/nginx_mock',
                str(nginx_port),
                str(blackbox_port),
                str(sezamapi_port),
            ],
            env=os.environ.copy(),
            stdout=open('./testing_out_stuff/nginx_mock.log', 'w'),
            stderr=sys.stderr,
        )
        _check_started('http://localhost:%d/ping' % nginx_port, 'nginx_mock')

        shutil.copy(yc.source_path('passport/infra/daemons/sezamapi/ut_last/tvm.secret'), SECRET)

        sezamapi = subprocess.Popen(
            [
                sezamapi_bin,
                '-c',
                sezamapi_config,
            ],
            env=os.environ.copy(),
            stdout=sys.stderr,
            stderr=sys.stderr,
        )
        _check_started('http://localhost:%d/ping' % sezamapi_port, 'sezamapi')

        subprocess.check_call(
            [
                # fmt: off
                yc.build_path('passport/infra/tools/ylast/ylast'),
                '-q',
                '-c', ylast_config,
                '-j', '4',
                '-U', 'http://localhost:%d' % nginx_port,
                'lah-accounts.xml',
                'lah-cors.xml',
                'lah-suggested-accounts.xml',
                'lah-reg-completion.xml'
                # fmt: on
            ],
            cwd=tests_path,
            env=os.environ.copy(),
            stdout=sys.stderr,
            stderr=open('./testing_out_stuff/ylast.stdout', 'w'),
        )
    finally:
        log('finally start')

        if sezamapi is not None:
            sezamapi.send_signal(15)
            assert sezamapi.wait() == 0

        if nginx is not None:
            nginx.terminate()

        log('finally finish')
