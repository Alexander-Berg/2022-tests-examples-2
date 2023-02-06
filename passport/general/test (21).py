# coding: utf-8

import allure
import unittest

import copy
import datetime
import inspect
import json
import os
import re
import subprocess
import sys
import time

import pytest
import requests
import yatest.common as yc
from yatest.common import network


def log(msg):
    sys.stdout.write('%s: %s\n' % (datetime.datetime.now(), msg))
    sys.stdout.flush()


TVMTOOL_BIN = yc.build_path('passport/infra/daemons/tvmtool/cmd/tvmtool')
env = os.environ.copy()
env['TVMTOOL_LOCAL_AUTHTOKEN'] = '27264bbd9d7524ea1f737c9aea73941a'

DEFAULT_TVMTOOL_CONFIG = {
    'BbEnvType': 1,
    'clients': {
        'me': {
            'secret': 'fake_secret',
            'self_tvm_id': 42,
            'dsts': {
                'he': {
                    'dst_id': 100500,
                },
                'she': {
                    'dst_id': 100501,
                },
            },
        },
    },
    'solomon': {
        'bind_host': '',
        'port': 8081,
        'stage_tvm_id': 200500,
        'solomon_tvm_id': 200501,
    },
}

VAILD_SOLOMON_SERVICE_TICKET = '3:serv:CBAQ__________9_IggItZ4MELSeDA:VJbWrZHQjmC_paU4uv6DdyXi5XxtlaUWZ_6gbyxNXWxenFuhJCFLGVK8jBhFbR-_CyA4qn7g5fEwwZdTldxSq6Oeuurn49WxupKkXc3uZ3DXpw6uCP40jyKfNJT0KhFjNN-FhtjyRKuLO1nDlBVlT8rNAiiMQ7dzxugr2d18XJ0'  # noqa
INVALID_SOLOMON_SERVICE_TICKET = '3:serv:CBAQ__________9_IgYItZ4MEAE:BpUMrszYVXmHv3IiXZJNdSLOA5Tr_oPIutOtoCPdKoPj1i_SkjCWK2TZpOzO5UCAOQ8CzgrA3HnazkXMkA6EseL30zgYJIKR0fuDmO83g1nkNPRhmMAPsXaNFRZi5GUO4bQtc6Jtvqn1Kq9Yj-aV7b7IDIyP7pCu3JSzKSZAOCM'  # noqa
LOG_INVALID_SOLOMON_SERVICE_TICKET = '3:serv:CBAQ__________9_IgYItZ4MEAE:'


class RegexpEqual(object):
    def __init__(self, regex):
        self.regex = regex

    def __repr__(self):
        return u'RegexpEqual({})'.format(repr(self.regex))

    def __eq__(self, other):
        return re.search(self.regex, other) is not None


class Anything(object):
    def __init__(self, validator=None, not_none=False):
        self.validator = validator
        self.not_none = not_none

    def __eq__(self, other):
        if self.not_none and other is None:
            return False
        if self.validator is not None:
            return self.validator(other)
        return True

    def __repr__(self):
        return u'Anything(not_none={}, validator={})'.format(
            self.not_none,
            inspect.getsource(self.validator).strip(),
        )


class TVMTool(object):
    def __init__(self, config=None, use_pipe=False):
        self.config = copy.deepcopy(config or DEFAULT_TVMTOOL_CONFIG)
        self.use_pipe = use_pipe

        self.port = network.PortManager().get_tcp_port(8080)

        if 'solomon' in self.config:
            self.solomon_port = network.PortManager().get_tcp_port(8081)
            self.solomon_url = 'http://localhost:{}'.format(self.solomon_port)
            self.config['solomon'].update(
                {
                    'port': self.solomon_port,
                    'bind_host': 'localhost',
                }
            )

        self.tvmtool_cfg = './tvmtool.conf'

        self.daemon = None
        self.url = 'http://localhost:{}'.format(self.port)

    def __enter__(self):
        with open(self.tvmtool_cfg, 'w') as f:
            json.dump(self.config, f)

        log('__enter__(): tvmtool is starting')
        self.daemon = subprocess.Popen(
            [
                TVMTOOL_BIN,
                '--unittest',
                '--port',
                str(self.port),
                '-c',
                self.tvmtool_cfg,
            ],
            env=env,
            stdout=subprocess.PIPE if self.use_pipe else sys.stdout,
            stderr=subprocess.PIPE if self.use_pipe else sys.stderr,
        )

        self._check_daemon_start()
        if 'solomon' in self.config:
            self._check_solomon_handle_start()

        log('__enter__(): tvmtool is started')

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        log('__exit__(): tvmtool is terminating')
        self.daemon.terminate()
        self.daemon.wait()
        log('__exit__(): tvmtool was terminated')

    def ping(self):
        log('ping(): started')
        resp = requests.get(self.url + '/tvm/ping', timeout=1)
        resp = requests.get(self.url + '/ping', timeout=1)
        log('ping(): finished')
        return resp.ok

    def _check_daemon_start(self):
        for _ in range(100):
            time.sleep(0.1)
            try:
                if self.ping():
                    return
            except requests.exceptions.RequestException as e:
                log('ping check: exception: %s' % e)

        assert self.daemon.poll() is None, 'Tvmtool was not started'

    def _check_solomon_handle_start(self):
        for _ in range(100):
            time.sleep(0.1)
            try:
                resp = requests.get(self.solomon_url, timeout=1)
                if resp.status_code == 404:
                    return
            except requests.exceptions.RequestException as e:
                log('solomon check: exception: %s' % e)

        assert self.daemon.poll() is None, 'Tvmtool was not started'


@allure.story('Запуск тестов через рецепт для tvmtool')
class TestTVMDaemon(unittest.TestCase):
    maxDiff = None

    def assert_solomon_metrics(self, response, expected):
        self.assertListEqual(
            sorted(
                response['metrics'],
                key=lambda x: sorted(
                    sorted(
                        x['labels'].items(),
                        key=lambda x: x[0],
                    ),
                ),
            ),
            expected,
        )

    def test_tvmtool_bad_config(self):
        """Случай невалидного конфига"""

        pytest.skip('skipping this test')  # TODO: PASSP-23049

        # Start tvmtool
        tvmtool_port = network.PortManager().get_tcp_port(8080)

        tvmtool_cfg = './tvmtool.conf'
        with open(tvmtool_cfg, 'w') as f:
            f.write('{"BbEnvType": 1, "clients": {  } }')

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
            stderr=subprocess.PIPE,
        )

        res = tvmtool.stderr.read()

        self.assertIn(b'No one client was found in config', res)
        self.assertEqual(tvmtool.wait(), 1)

    def test_tvmtool_solomon_server_start_ok(self):
        """Корректная работа solomon-интерфейса"""

        with TVMTool() as tvmtool:
            # Греем счетчик пингов
            tvmtool.ping()

            resp = requests.get(
                tvmtool.solomon_url + '/tvm/solomon',
                headers={
                    'X-Ya-Service-Ticket': VAILD_SOLOMON_SERVICE_TICKET,
                },
            )
            self.assertEqual(resp.status_code, 200)
            self.assert_solomon_metrics(
                resp.json(),
                [
                    {'type': 'RATE', 'labels': {'path': '/debug/pprof/', 'sensor': 'http.requests'}, 'value': 0},
                    {
                        'type': 'RATE',
                        'labels': {'path': '/ping', 'sensor': 'http.requests'},
                        'value': Anything(lambda x: int(x) > 0),
                    },
                    {
                        'type': 'RATE',
                        'labels': {'path': '/tvm/cache/force_update', 'sensor': 'http.requests'},
                        'value': 0,
                    },
                    {'type': 'RATE', 'labels': {'path': '/tvm/checksrv', 'sensor': 'http.requests'}, 'value': 0},
                    {'type': 'RATE', 'labels': {'path': '/tvm/checkusr', 'sensor': 'http.requests'}, 'value': 0},
                    {'type': 'RATE', 'labels': {'path': '/tvm/keys', 'sensor': 'http.requests'}, 'value': 0},
                    {
                        'type': 'RATE',
                        'labels': {'path': '/tvm/ping', 'sensor': 'http.requests'},
                        'value': Anything(lambda x: int(x) > 0),
                    },
                    {
                        'type': 'RATE',
                        'labels': {'path': '/tvm/private_api/__meta__', 'sensor': 'http.requests'},
                        'value': 0,
                    },
                    {
                        'type': 'RATE',
                        'labels': {'path': '/tvm/solomon', 'sensor': 'http.requests'},
                        'value': Anything(lambda x: int(x) > 0),
                    },
                    {'type': 'RATE', 'labels': {'path': '/tvm/tickets', 'sensor': 'http.requests'}, 'value': 0},
                    {'type': 'RATE', 'labels': {'path': '/v2/check', 'sensor': 'http.requests'}, 'value': 0},
                    {'type': 'RATE', 'labels': {'path': '/v2/keys', 'sensor': 'http.requests'}, 'value': 0},
                    {'type': 'RATE', 'labels': {'path': '/v2/roles', 'sensor': 'http.requests'}, 'value': 0},
                    {'type': 'RATE', 'labels': {'path': '/v2/tickets', 'sensor': 'http.requests'}, 'value': 0},
                    {
                        'type': 'DGAUGE',
                        'labels': {'sensor': 'process.goMaxProcs'},
                        'value': Anything(lambda x: int(x) > 0),
                    },
                    {
                        'type': 'DGAUGE',
                        'labels': {'sensor': 'process.memRssBytes'},
                        'value': Anything(lambda x: int(x) > 0),
                    },
                    {
                        'type': 'DGAUGE',
                        'labels': {'sensor': 'process.memVmsBytes'},
                        'value': Anything(lambda x: int(x) > 0),
                    },
                    {
                        'type': 'DGAUGE',
                        'labels': {'sensor': 'process.numThreads'},
                        'value': Anything(lambda x: int(x) > 0),
                    },
                    {
                        'type': 'DGAUGE',
                        'labels': {'sensor': 'version', 'version': RegexpEqual('^\\d+\\.\\d+\\.\\d+$')},
                        'value': 1,
                    },
                ],
            )

    def test_tvmtool_solomon_tvm_auth_failed(self):
        """Неуспешная авторизация в solomon-интерфейсе"""

        with TVMTool() as tvmtool:
            resp = requests.get(
                tvmtool.solomon_url + '/tvm/solomon',
                headers={
                    'X-Ya-Service-Ticket': INVALID_SOLOMON_SERVICE_TICKET,
                },
            )
            self.assertEqual(resp.status_code, 403)
            self.assertDictEqual(
                resp.json(),
                {
                    'debug_string': u'ticket_type=service;expiration_time=9223372036854775807;src=200501;dst=1;scope=;',
                    'error': u'Wrong ticket dst, expected 200500, got 1',
                    'logging_string': LOG_INVALID_SOLOMON_SERVICE_TICKET,
                },
            )

    def test_tvmtool_solomon_server_start_without_solomon(self):
        """Запуск без solomon-интерфейса"""

        config = copy.deepcopy(DEFAULT_TVMTOOL_CONFIG)
        del config['solomon']

        with TVMTool(config, use_pipe=True) as tvmtool:
            pass

        self.assertIn(b'Skip solomon interface', tvmtool.daemon.stdout.read())

    def test_tickets_v2(self):
        """Проверка поведения ручки /v2/tickets"""

        config = copy.deepcopy(DEFAULT_TVMTOOL_CONFIG)
        del config['solomon']

        with TVMTool() as tvmtool:
            resp = requests.get(
                tvmtool.url + '/v2/tickets',
                headers={'Authorization': env['TVMTOOL_LOCAL_AUTHTOKEN']},
            )
            assert resp.status_code == 400, resp.text
            assert json.loads(resp.text)['error'] == "missing parameter 'self'", resp.text

            resp = requests.get(
                tvmtool.url + '/v2/tickets?self=me',
                headers={'Authorization': env['TVMTOOL_LOCAL_AUTHTOKEN']},
            )
            assert resp.status_code == 400, resp.text
            assert json.loads(resp.text)['error'] == "missing parameter 'dsts'", resp.text

            resp = requests.get(
                tvmtool.url + '/v2/tickets?self=me&dsts=he,she',
                headers={'Authorization': env['TVMTOOL_LOCAL_AUTHTOKEN']},
            )
            assert resp.status_code == 200, resp.text
            assert "he" in json.loads(resp.text), resp.text
            assert "she" in json.loads(resp.text), resp.text
