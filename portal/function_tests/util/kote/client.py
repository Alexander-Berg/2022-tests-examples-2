# -*- coding: utf-8 -*-

import os
import logging
import json

from requests import Session
from portal.function_tests.util.common.env import morda_env
from portal.function_tests.util.common.http import Req
from portal.function_tests.util.common.morda import Morda, DesktopMain

import portal.function_tests.util.kote.const as const
from portal.function_tests.util.kote.yaml_parser import get_params
import portal.function_tests.util.kote.kote_exceptions as kote_exceptions
import yatest.common

logger = logging.getLogger(__name__)


class URLClient(object):
    def __init__(self, morda=None, env=None, config=None, params=None):
        if env is None:
            env = morda_env()
        self.env = env
        self._session = Session()
        if morda is None:
            morda = DesktopMain()
        self._morda = morda
        self.uri = '/'
        if config is None:
            config = {}
        if 'path' in config:
            self.uri = config['path']
        self.domain = 'ru'
        if 'domain' in config:
            self.domain = config['domain']
        self.base_url = Morda.get_origin(env=self.env, domain=self.domain, no_prefix=True)
        if params is None:
            params = {}
        self.params = params
        self.headers = {'X-Yandex-Autotests': '1', 'User-Agent': 'Kote-Autotests-Bot-1.0'}
        if 'headers' in config:
            for header in config['headers']:
                self.headers[header] = config['headers'][header]
        self.method = 'GET'
        self.data = None
        if 'request_body' in config:
            self.method = 'POST'
            self.data = json.dumps(config['request_body'])

    def prepare_request(self, params):
        uri = self.uri

        if 'uri' in params:
            uri = params['uri']

        for param in self.params:
            if param not in params:
                params[param] = self.params[param]

        return Req('{}{}'.format(self.base_url, uri), method=self.method, data=self.data, params=params,
                   headers=self.headers, session=self._session, allow_retry=True, retries=10)

    # геттер для словаря респонза
    @staticmethod
    def get_json(reqresult):
        return reqresult.json()

    # геттер для контента респонза
    @staticmethod
    def get_content(reqresult):
        return reqresult.content()

    # отправка запроса
    @staticmethod
    def send(req):
        return req.send()


# клиент для моков
class MockClient():
    def __init__(self, path):
        self.path = path
        self.data = None

    def prepare_request(self, _):
        mock_path = yatest.common.source_path(os.path.join(const.KOTE_MOCK_PREFIX, self.path))
        with open(mock_path) as f:
            self.data = json.load(f)
        f.close()

        return self.data

    # то, что дальше нужно, чтобы не вносить изменений в test_run_tests.py
    def send(self, _):
        return self.data

    def get_json(self, _):
        return self.data


def load_client(client=None):
    client_path = yatest.common.source_path(os.path.join(const.KOTE_CLIENTS_PREFIX, client))
    params = get_params(client_path)
    if isinstance(params, list):
        params = params.pop()

    return params


def choose_client(config):
    if 'client' not in config:
        raise ValueError('Client missing!')

    if config['client'] == 'mock':
        if 'path' in config:

            return MockClient(config['path'])

        else:
            raise ValueError('Missing path')

    elif config['client'] == 'url':
        if 'path' not in config:
            raise ValueError('Missing path')
        return URLClient(config=config)

    else:
        try:
            client_params = load_client(client=config['client']+'.yaml')
        except Exception as exc:
            raise kote_exceptions.BadClient(exc, config['test_path'], config['client']) from exc

        if isinstance(client_params, dict):
            if 'config' in client_params:
                for conf in client_params['config']:
                    if conf not in config:
                        config[conf] = client_params['config'][conf]
                    elif conf == 'headers':
                        # Заменяем заголовки в описании клиента значениями, указанными в тесте
                        headers = client_params['config']['headers'].copy()
                        headers.update(config['headers'])
                        config['headers'] = headers
            params = {}
            if 'get_params' in client_params:
                params = client_params['get_params']
            return URLClient(config=config, params=params)

        else:
            raise ValueError('Unknown client: `{}`'.format(config['client']))
