#!/usr/bin/env python3.7

import argparse
import asyncio
import contextlib
import datetime
import glob
import http.server
import os
import pathlib
import shutil
import socket
import subprocess
import sys
import tempfile
import threading
import time
import traceback
from typing import List
from typing import Optional
from xml.etree import ElementTree

import requests
import yaml

MAX_WAIT_TIME = 300
SLEEP_SECONDS = 1
REQUEST_TIMEOUT = 3
SITES_AVAILABLE = '/etc/nginx/sites-available/'
SITES_ENABLED = '/etc/nginx/sites-enabled/'

ROOT_CA_CRT_PATH = '/taxi/tools/rootCA.crt'
ROOT_CA_KEY_PATH = '/taxi/tools/rootCA.key'
EXT_FILENAME = 'v3.ext'
UPDATE_CERTS_COMMAND = ['update-ca-certificates']
GEN_SERV_KEY_COMMAND = [
    'openssl',
    'req',
    '-new',
    '-newkey',
    'rsa:1024',
    '-keyout',
    'server.key',
    '-out',
    'server.csr',
    '-nodes',
    '-subj',
    '/CN=Server',
]
SIGN_SERV_KEY_COMMAND = [
    'openssl',
    'x509',
    '-req',
    '-sha256',
    '-days',
    '7000',
    '-in',
    'server.csr',
    '-extfile',
    EXT_FILENAME,
    '-CA',
    'rootCA.crt',
    '-CAkey',
    'rootCA.key',
    '-CAcreateserial',
    '-out',
    'server.crt',
]
NGINX_CHECK_COMMAND = ['nginx', '-t']
NGINX_RUN_COMMAND = ['nginx', '-c', '/etc/nginx/nginx.conf']
NGINX_LOG_DEFAULTFORMAT = (
    'log_format custom_log_format '
    '\'[$time_local] $http_host $remote_addr '
    '"$request" $status "$http_referer" "$http_user_agent" '
    '"$http_cookie" $request_time $upstream_cache_status $bytes_sent '
    '"$upstream_response_time" $request_length $msec '
    '"$upstream_http_x_yareqfinish" '
    '"$sent_http_x_yauuid" '
    '"$upstream_http_x_yarequestid" '
    '"$upstream_http_x_yamisc" '
    '"$http_X_MSISDN_h121ZY615d623L631O2L3;$http_HW_3GPP_RAT_Type;'
    '$http_X_SGSN_IP;$http_X_MegaFon_IMSI"\';\n'
)
SYSLOG_COMMAND = [
    '/usr/sbin/syslog-ng',
    '--no-caps',
    '-F',
    '--control=/tmp/syslog-ng.ctl',
]
SYSLOG_CHECK_COMMAND = [
    '/usr/sbin/syslog-ng-ctl',
    'stats',
    '--control=/tmp/syslog-ng.ctl',
]
CONFIG_VARS_GLOB = '/etc/yandex/taxi/*/config_vars.production.yaml'
SED_CONFIG_VARS_COMMAND = [
    'sed',
    '-i',
    's/geobase_lock_memory: true/geobase_lock_memory: false/',
]
PRINT_PACKAGES_VERSIONS_COMMAND = ['dpkg', '-l']
FASTCGI_CONF_TPL = '/etc/fastcgi2/available/{}.conf'
LOG_FILE_TPL = '/taxi/logs/application-{}.log'
READ_ELF_COMMAND = ['readelf', '-n']
GDB_CORE_COLLECT_COMMAND = ['gdb', '-ex', 'bt', '-ex', 'q']

CORES_DIR = '/taxi/cores'
BACKTRACES_DIR = '/taxi/logs/backtraces'


def run_syslog():
    subprocess.Popen(SYSLOG_COMMAND)
    with open(os.devnull, 'wb') as fle:
        # syslog must be started first
        for _ in range(30):
            call_result = subprocess.call(
                SYSLOG_CHECK_COMMAND, stdout=fle, stderr=fle,
            )
            if call_result == 0:
                break
            time.sleep(1)
        else:
            subprocess.check_call(SYSLOG_CHECK_COMMAND)


def add_root_certificates():
    shutil.copy(ROOT_CA_CRT_PATH, '/usr/local/share/ca-certificates/')
    subprocess.check_call(UPDATE_CERTS_COMMAND)


def fixup_config_vars():
    files = glob.glob(CONFIG_VARS_GLOB)
    if files:
        subprocess.check_call(SED_CONFIG_VARS_COMMAND + files)


def make_https_certificates(hosts):
    # Run this function before run_nginx()
    old_dir = os.getcwd()
    cert_dir = tempfile.mkdtemp()

    try:
        os.chdir(cert_dir)

        shutil.copy(ROOT_CA_CRT_PATH, './')
        shutil.copy(ROOT_CA_KEY_PATH, './')
        subprocess.check_call(GEN_SERV_KEY_COMMAND)

        with open(EXT_FILENAME, 'wt') as f_inp:
            f_inp.write('subjectAltName = @alt_names\n\n[alt_names]\n')
            dns_line = 'DNS.%i=%s\n'
            for i, host in enumerate(hosts, 1):
                f_inp.write(dns_line % (i, host))

        subprocess.check_call(SIGN_SERV_KEY_COMMAND)

        shutil.copy('server.crt', '/etc/ssl/certs/')
        shutil.copy('server.key', '/etc/ssl/private/')
    finally:
        os.chdir(old_dir)


def run_nginx(configs, program_name):
    with open('/etc/nginx/logs', 'w') as log_conf:
        nginx_log = LOG_FILE_TPL.format('-'.join([program_name, 'nginx']))
        # make format like in production
        log_conf.write(NGINX_LOG_DEFAULTFORMAT)
        log_conf.write('error_log {};\n'.format(nginx_log))
        log_conf.write('access_log {} custom_log_format;\n'.format(nginx_log))

    touch_and_chmod_log(nginx_log)

    for name in os.listdir(SITES_ENABLED):
        os.remove(os.path.join(SITES_ENABLED, name))
    for config in configs:
        if not os.path.exists(os.path.join(SITES_AVAILABLE, config)):
            raise RuntimeError('nginx config not found: %s' % config)
        os.symlink(
            os.path.join(SITES_AVAILABLE, config),
            os.path.join(SITES_ENABLED, config),
        )
    subprocess.check_call(NGINX_CHECK_COMMAND)
    subprocess.check_call(NGINX_RUN_COMMAND)


def touch_and_chmod_log(log_path):
    open(log_path, 'a').close()
    os.chmod(log_path, 0o666)


def _override_cores_rules() -> None:
    with open('/proc/sys/kernel/core_pattern', 'w', encoding='ascii') as out:
        out.write(CORES_DIR + '/core-%e-%s-%u-%g-%p-%t' + '\n')
    os.makedirs(CORES_DIR, mode=0o777, exist_ok=True)
    os.makedirs(BACKTRACES_DIR, mode=0o777, exist_ok=True)


def _collect_backtraces(program_name: str) -> None:
    _, _, files = next(os.walk(CORES_DIR))
    for file in files:
        elf_output = _popen_with_capture_output(
            READ_ELF_COMMAND + [file], cwd=CORES_DIR,
        )
        binary_name = _get_binary_name_from_elf(elf_output)
        backtrace_path = os.path.join(
            BACKTRACES_DIR, program_name + ':' + file + '-backtrace.txt',
        )
        with open(backtrace_path, 'w') as backtrace:
            cmd = GDB_CORE_COLLECT_COMMAND + [binary_name, file]
            gdb_output = _popen_with_capture_output(cmd, cwd=CORES_DIR)
            backtrace.write(gdb_output)


def _get_binary_name_from_elf(elf_output: str) -> str:
    binary_name = None
    for line in elf_output.split('\n'):
        stripped = line.strip()
        if stripped.startswith('/'):
            binary_name = stripped
            break
    assert (
        binary_name is not None
    ), 'No binary name in core dump, backtrace could not be collected.'
    return binary_name


def _popen_with_capture_output(command: List[str], cwd: str) -> str:
    process = subprocess.Popen(
        command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=cwd,
    )
    stdout, stderr = process.communicate()
    stdout_decoded = stdout.decode(sys.getdefaultencoding())
    stderr_decoded = stderr.decode(sys.getdefaultencoding())
    _check_process(process, stdout_decoded, stderr_decoded)
    return stdout_decoded


def _check_process(
        process: subprocess.Popen,
        std_output: Optional[str] = None,
        err_output: Optional[str] = None,
) -> None:
    if process.returncode != 0:
        if std_output:
            print('%s output: %s', process.args, std_output)
        error_message = '%r exited with code %s' % (
            process.args[0],
            process.returncode,
        )
        if err_output:
            print('Error output is: \n %s' % error_message)
        assert False, 'Process exited with non zero code'


def _check_socket(host, port, family=socket.AF_INET):
    sock = socket.socket(family, socket.SOCK_STREAM)
    with contextlib.closing(sock):
        try:
            sock.settimeout(REQUEST_TIMEOUT)
            return sock.connect_ex((host, port)) == 0
        except socket.gaierror:
            return False


def _check_url_get(url):
    try:
        response = requests.get(url, timeout=REQUEST_TIMEOUT)
        return response.status_code == 200
    except requests.RequestException:
        return False


async def _check_postgresql(database: str) -> bool:
    # do not import if not needed
    import asyncpg

    connection: Optional[asyncpg.connection.Connection] = None
    try:
        connection = await asyncpg.connect(
            host='pgaas.mail.yandex.net',
            user='user',
            password='password',
            port='5432',
            database=database,
            timeout=REQUEST_TIMEOUT,
        )
        async with connection.transaction():
            cur = await connection.cursor('SELECT \'ping\'')
            row = await cur.fetchrow()
            assert row == ('ping',), row
            return True
    except:  # noqa: E722  # pylint: disable=bare-except
        traceback.print_exc()
        return False
    finally:
        if connection:
            await connection.close()


async def wait(services: List[str], timeout: int) -> None:
    end: datetime.datetime = datetime.datetime.now() + datetime.timedelta(
        seconds=timeout,
    )
    for service in services:
        while datetime.datetime.now() < end:
            if service.startswith('http'):
                if _check_url_get(service):
                    break
            elif service.startswith('postgresql:'):
                if await _check_postgresql(service.split(':', 1)[-1]):
                    break
            else:
                host, port = service.split(':')
                port_number = int(port)
                if _check_socket(host, port_number) or _check_socket(
                        host, port_number, socket.AF_INET6,
                ):
                    break
            print('Waiting for', service)
            sys.stdout.flush()
            await asyncio.sleep(SLEEP_SECONDS)
        else:
            raise RuntimeError('service not work: ' + service)


def _log_fastcgi_pools(port, interval, program_name):
    log_path = LOG_FILE_TPL.format('-'.join([program_name, 'fcgi-pools']))
    with open(log_path, 'a', buffering=1) as log_file:
        while True:
            message = []
            try:
                monitor_socket = socket.socket(
                    socket.AF_INET, socket.SOCK_STREAM,
                )
                monitor_socket.settimeout(0.25)
                monitor_socket.connect(('localhost', port))
                monitor_socket.send(b'i')

                message.append('fastcgi-pools-state: ')

                while True:
                    chunk = monitor_socket.recv(4096)
                    if not chunk:
                        break
                    message.append(chunk)

            except socket.error:
                time.sleep(1)
            log_file.write(
                '{}: {}\n'.format(
                    datetime.datetime.utcnow().isoformat(), ''.join(message),
                ),
            )
            time.sleep(interval)


def log_fastcgi_pools(port, interval, program_name):
    thread = threading.Thread(
        target=_log_fastcgi_pools, args=(port, interval, program_name),
    )
    thread.setDaemon(True)
    thread.start()


def fix_fastcgi_config(project_name, no_tests_control):
    config = FASTCGI_CONF_TPL.format(project_name)
    data = ElementTree.parse(config)
    components = data.find('./components')
    if (
            not data.find('./handlers/handler[@id="tests-control"]')
            and not no_tests_control
    ):
        tests_control = ElementTree.SubElement(
            components,
            'component',
            {
                'name': 'tests-control',
                'type': '{}:tests-control'.format(project_name),
            },
        )
        timeout = ElementTree.SubElement(
            tests_control, 'httpclient_timeout_ms',
        )
        timeout.text = '60000'
        handlers = data.find('./handlers')
        handler = ElementTree.SubElement(
            handlers,
            'handler',
            {
                'url': '/tests/control',
                'pool': 'work_pool',
                'id': 'tests-control',
            },
        )
        ElementTree.SubElement(handler, 'component', {'name': 'tests-control'})

    logger_component = components.find('./component[@name="logger-component"]')
    if logger_component is not None:
        output = logger_component.find('./output')
        if not output:
            output = ElementTree.SubElement(logger_component, 'output')
        output.text = 'console'

    clients_component = components.find('./component[@name="clients"]')
    if clients_component is not None:
        conductor_timeout = clients_component.find('./conductor_timeout')
        if not conductor_timeout:
            conductor_timeout = ElementTree.SubElement(
                clients_component, 'conductor_timeout',
            )
        conductor_timeout.text = '2000'

    data.write(config)


def fix_userver_config_http_client(cfg, timeout_value):
    config_path = pathlib.Path(cfg)
    if not config_path.exists():
        raise RuntimeError(f'{cfg} not exists')

    content = config_path.read_text()
    config = yaml.safe_load(content)

    http_client = config['components_manager']['components']['http-client']
    if http_client is None:
        http_client = {}
    http_client['testsuite-enabled'] = True
    http_client['testsuite-timeout'] = timeout_value or '60s'
    config['components_manager']['components']['http-client'] = http_client

    with config_path.open('w', encoding='utf-8') as fp:
        yaml.safe_dump(config, fp, default_flow_style=False)
        print(f'Config {config_path} was modified')


def print_packages_versions(program_name):
    log_name = '/taxi/logs/container-{}-installed-packages.txt'.format(
        program_name,
    )
    with open(log_name, 'w') as log_file:
        subprocess.check_call(PRINT_PACKAGES_VERSIONS_COMMAND, stdout=log_file)


def run_with_restart_service(command, stdout_to_log, port, program_name):
    restart_event = threading.Event()
    proc = None

    class Handler(http.server.BaseHTTPRequestHandler):
        # pylint: disable=invalid-name
        def do_GET(self):
            try:
                if proc is not None and restart_event.is_set():
                    restart_event.clear()
                    proc.kill()
                    if restart_event.wait(30):
                        self.send_response(200)
                    else:
                        self.send_response(409)
                else:
                    self.send_response(404)
            except:  # noqa: E722  # pylint: disable=bare-except
                traceback.print_exc()
                self.send_response(500)

    httpd = http.server.HTTPServer(('', port), Handler)
    thread = threading.Thread(target=httpd.serve_forever)
    thread.setDaemon(True)
    thread.start()
    while True:
        proc = run_process(command, stdout_to_log, program_name)
        restart_event.set()
        proc.wait()
        if restart_event.is_set():
            httpd.shutdown()
            thread.join(30)
            sys.exit(proc.returncode)
        print('Restart service')


def run_process(command, stdout_to_log, program_name):
    if stdout_to_log:
        stdout = open(LOG_FILE_TPL.format(program_name), 'a', buffering=1)
    else:
        stdout = None
    return subprocess.Popen(command, stdout=stdout, stderr=subprocess.STDOUT)


def run(command, stdout_to_log, restart_service, program_name):

    if restart_service:
        return run_with_restart_service(
            command, stdout_to_log, restart_service, program_name,
        )
    proc = run_process(command, stdout_to_log, program_name)
    exit_code = proc.wait()
    if exit_code != 0:
        _collect_backtraces(program_name)
    sys.exit(exit_code)


async def main() -> None:
    _override_cores_rules()
    os.umask(0o0000)
    program_name = os.getenv('program_name')
    print_packages_versions(program_name)
    args = parse_args()
    add_root_certificates()
    fixup_config_vars()
    if args.wait:
        await wait(args.wait, args.timeout)
    if args.syslog:
        run_syslog()
    if args.https_hosts:
        make_https_certificates(args.https_hosts)
    if args.nginx:
        run_nginx(args.nginx, program_name)
    if args.fix_fastcgi_config:
        fix_fastcgi_config(args.fix_fastcgi_config, args.no_tests_control)
    if args.log_fastcgi_pools:
        log_fastcgi_pools(
            args.log_fastcgi_pools, args.fastcgi_poll_interval, program_name,
        )
    if args.fix_userver_client_timeout:
        fix_userver_config_http_client(
            args.fix_userver_client_timeout,
            args.fix_userver_client_timeout_value,
        )
    if args.run:
        run(args.run, args.stdout_to_log, args.restart_service, program_name)


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--syslog', action='store_true')
    parser.add_argument('--stdout-to-log', action='store_true')
    parser.add_argument('--fix-fastcgi-config')
    parser.add_argument('--fix-userver-client-timeout', type=str)
    parser.add_argument('--fix-userver-client-timeout-value', type=str)
    parser.add_argument('--no-tests-control', action='store_true')
    parser.add_argument('--log-fastcgi-pools', type=int, default=0)
    parser.add_argument('--fastcgi-poll-interval', type=int, default=5)
    parser.add_argument('--nginx', nargs='+')
    parser.add_argument('--https-hosts', nargs='+')
    parser.add_argument('--timeout', type=int, default=MAX_WAIT_TIME)
    parser.add_argument('--wait', nargs='+')
    parser.add_argument('--restart-service', type=int, metavar='PORT')
    parser.add_argument('--run', nargs=argparse.REMAINDER)
    return parser.parse_args()


if __name__ == '__main__':
    asyncio.run(main())
