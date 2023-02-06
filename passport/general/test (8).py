import allure
import unittest

import yatest.common as yc
import os
import psutil
import subprocess
import time
from passport.infra.recipes.common import log, start_daemon
from passport.infra.recipes.kolmogor.common import check_started

log('Starting blackbox test')

totalcpu_count = psutil.cpu_count()
cpu_count = min(totalcpu_count, 4)
log('CPU count is %d, will run in %d jobs ' % (totalcpu_count, cpu_count))

output_path = yc.output_path()
tests_path = yc.source_path('passport/infra/daemons/blackbox/last-tests')
config_path = yc.output_path('last.conf')

# check that blackbox is running
log('Blackbox PID is ' + os.environ['RECIPE_BLACKBOX_PID'])
blackbox_port = os.environ['RECIPE_BLACKBOX_PORT']

# get other ports
mysql_port = os.environ['RECIPE_MYSQL_PORT']
tvm_host = 'http://127.0.0.1'

try:
    with open('./tvmapi.port') as f:
        tvm_port = f.read()
except IOError:
    log('Could not find tvm port file: ./tvmapi.port')

oauth_port = str(yc.network.PortManager().get_tcp_port())

# prepare environment
os.environ['BB_PASSPORTDB_USER_RW'] = 'root'
os.environ['BB_PASSPORTDB_PASSWD_RW'] = ''

# prepare LAST config
with open(yc.source_path('passport/infra/daemons/blackbox/ut_last/template-last.conf')) as f:
    config = f.read()
    config = config.replace('{mysql-port}', mysql_port)
    config = config.replace('{oauth-port}', oauth_port)
    config = config.replace('{config-dir}', output_path + '/available')
    config = config.replace('{work-dir}', yc.work_path())
    config = config.replace('{tvm-host}', tvm_host)
    config = config.replace('{tvm-port}', tvm_port)

    with open(config_path, 'wt') as out:
        out.write(config)


def run_last_tests(config_path, tests_path, blackbox_port, tests):
    command = [
        # fmt: off
        yc.build_path('passport/infra/tools/ylast/ylast'),
        '-q',
        '-c', config_path,
        '-j', str(cpu_count),
        '-U', 'http://localhost:' + blackbox_port,
        # fmt: on
    ]
    command.extend(tests)

    subprocess.check_call(command, cwd=tests_path)


@allure.story('Запуск ylast тестов')
class YlastTests(unittest.TestCase):
    def test_regression(self):
        """Неизменность простых ответов"""

        command = (
            yc.build_path('passport/infra/tools/ylast/ylast')
            + ' -q -V -c '
            + config_path
            + ' regression.xml'
            + ' -U http://localhost:'
            + blackbox_port
            + '| tail -n "+8" | head -n -6 '
            + '| grep -v -e "^Date: " -e "^Host: " -e "^Connection: " -e "^Content-type: " -e "^X-Request-Id: " -e "^XRTIQ: " -e "^XRTIH: "'
        )

        outfile = output_path + '/regression.txt'
        subprocess.check_call(command, cwd=tests_path, shell=True, stdout=open(outfile, 'w'))

        return [
            yc.canonical_file(outfile, local=True),
        ]

    def test_basic(self):
        """Получение пользовательских данных в базовых сценариях"""

        tests = [
            'blackbox.xml',
            'blackbox2.xml',
            'blackbox3.xml',
            'blackbox-addr.xml',
            'blackbox-extended.xml',
            'blackbox-pdd.xml',
        ]

        run_last_tests(config_path, tests_path, blackbox_port, tests)

    def test_grants(self):
        """Валидация грантов"""

        tests = [
            'blackbox-grants-service.xml',
            'blackbox-check-grants.xml',
        ]

        run_last_tests(config_path, tests_path, blackbox_port, tests)

    def test_passport(self):
        """Методы для Паспорта"""

        tests = [
            'blackbox-passport.xml',
            'blackbox-passport-simple.xml',
        ]

        run_last_tests(config_path, tests_path, blackbox_port, tests)

    def test_partitions(self):
        """Работа с партициями"""

        tests = ['blackbox-partitions.xml']

        run_last_tests(config_path, tests_path, blackbox_port, tests)

    def test_session(self):
        """Работа с сессионными куками"""

        tests = [
            'blackbox-decrease-sessionid-lifetime.xml',
            'blackbox-newsession.xml',
            'blackbox-session-ext.xml',
            'blackbox-session.xml',
            'blackbox-session2.xml',
            'blackbox-session3.xml',
            'blackbox-sessguard.xml',
            'blackbox-session-reg-complete.xml',
        ]

        run_last_tests(config_path, tests_path, blackbox_port, tests)

    def test_login(self):
        """Ввод логина-пароля"""

        # this test requires kolmogor up and running, so start kolmogor
        kolmogor_port = os.environ['RECIPE_KOLMOGOR_PORT']
        log('Starting kolmogor, port=' + kolmogor_port)

        command = [
            # fmt: off
            yc.build_path('passport/infra/daemons/kolmogor/daemon/kolmogor'),
            '-c', output_path + '/kolmogor.conf',
            # fmt: on
        ]

        process = start_daemon(command, os.environ.copy(), kolmogor_port, 600)
        check_started('http://localhost:%s' % kolmogor_port)

        # give time for dbpool to figure out that backend is up
        time.sleep(5)

        tests = ['blackbox-login.xml']

        try:
            run_last_tests(config_path, tests_path, blackbox_port, tests)
        finally:
            log('Stopping kolmogor')
            process.terminate()

    def test_oauth(self):
        """Работа с OAuth-токенами"""
        # some tests require LAST to create oauth tokens, lets run oauth API mock

        log('Starting oauth mock, port=' + oauth_port)

        command = [yc.build_path('passport/infra/daemons/blackbox/ut_last/oauth_mock/oauth_server'), oauth_port]

        process = start_daemon(command, os.environ.copy(), oauth_port, 600)

        tests = [
            'blackbox-debug-user-ticket.xml',
            'blackbox-oauth.xml',
            'blackbox-user-ticket.xml',
        ]

        try:
            run_last_tests(config_path, tests_path, blackbox_port, tests)
        finally:
            log('Stopping oauth')
            process.terminate()

    def test_sesskill(self):
        """Отзыв сессионых кук"""

        # this test requires sesskill up and running, lets run mock too

        sesskill_port = os.environ['RECIPE_SESSKILL_PORT']
        log('Starting sesskill mock, port=' + sesskill_port)

        command = [
            yc.build_path('passport/infra/daemons/blackbox/ut_last/sesskill_mock/sesskill_server'),
            sesskill_port,
        ]

        process = start_daemon(command, os.environ.copy(), sesskill_port, 600)

        # give time for dbpool to figure out that backend is up
        time.sleep(7)

        tests = ['blackbox-sesskill.xml']

        try:
            run_last_tests(config_path, tests_path, blackbox_port, tests)
        finally:
            log('Stopping sesskill')
            process.terminate()


@allure.story('Запуск тестов для 2FA-паролей')
class TotpTests(unittest.TestCase):
    def test_totp(self):
        """Работа с 2FA-паролями"""

        import test_check_rfc_totp
        import test_edit_totp
        import test_login
        from utils import clean_local_rfc_totp_check_time

        blackbox_host = 'localhost:' + blackbox_port
        test_login.check(blackbox_host)
        test_edit_totp.check(blackbox_host, output_path + '/available/blackbox_keys')

        clean_local_rfc_totp_check_time(int(mysql_port))
        test_check_rfc_totp.check(blackbox_host)
