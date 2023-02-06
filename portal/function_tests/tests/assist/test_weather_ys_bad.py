# -*- coding: utf-8 -*-
import logging

import allure
import pytest

from common.client import MordaClient
from common.geobase import Regions
from common.morda import DesktopMain
from common.http import Req

from requests import Session
from requests.exceptions import RequestException
from urlparse import urlparse, parse_qs
import re
import json

from pprint import PrettyPrinter
pp = PrettyPrinter(depth=4)

logger = logging.getLogger(__name__)
base_url = '{}/portal/api/search/2/weather'
common_params = {
    'webcard': 1,
    'cleanvars': '^block$',
    'app_platform': 'android',
    'app_version': 6050000,
    'os_version': '6.0',
    'dp': 2,
    'size': '1280x800',
}

test_arg_sets = [
    {
        'title': 'nowcast',
        'id': 'nowcast',
        'params': {
            'assist': 'nowcast',
            'lat': 55.345769,
            'lon': 37.188409
        },
        'search': ['url'],
        'expected': {
            'path': r'^/pogoda/213/nowcast$',
            'args': {'lat': r'^\d+\.\d+$', 'lon': r'^\d+\.\d+$', 'nowcast': r'^1$', 'appsearch_header': r'^1$'}
        },
        'skip_if': 'skip_nowcast'
    },
    {
        'title': 'weather_weekend_home',
        'id': 'weather_weekend',
        'params': {
            'assist': 'weather_weekend',
            'assist_weather_weekend': json.dumps({
                'forecast_type': 'weekend_days',
                'geo': 213,
                'text': 'Какой-то текст',
                'kind': '1234'
            }),
            'geo': 213
        },
        'search': ['forecast', '*', 'url'],
        'expected': {
            'path': r'^/pogoda/moscow$',
            'args': {'appsearch_header': r'^1$', 'appsearch_ys': r'^2$'},
            'hash': r'^d_\d+$'
        }
    },
    {
        'title': 'weather_weekend_too_far',
        'id': 'weather_weekend',
        'params': {
            'assist': 'weather_weekend',
            'assist_weather_weekend': json.dumps({
                'forecast_type': 'weekend_days',
                'geo': 2,
                'text': u'Какой-то текст',
                'kind': '1234'
            }),
            'geo': 213
        },
        'search': ['url'],
        'expected': {
            'path': r'^/pogoda/2$',
            'args': {'appsearch_header': r'^1$', 'appsearch_ys': r'^2$'}
        }
    },
    {
        'title': 'weather_alert_home',
        'id': 'weather_alert',
        'params': {
            'assist': 'weather_alert',
            'assist_weather_alert': json.dumps({
                'forecast_type': 'single_today',
                'geo': 213,
                'type': '1234',
                'text': u'Какой-то текст'
            }),
            'geo': 213
        },
        'search': ['single_forecast', '*', 'url'],
        'expected': {
            'path': r'^/pogoda/moscow$',
            'args': {'appsearch_header': r'^1$', 'appsearch_ys': r'^2$'},
            'hash': r'^d_\d+$'
        }
    },
    {
        'title': 'weather_alert_too_far',
        'id': 'weather_alert',
        'params': {
            'assist': 'weather_alert',
            'assist_weather_alert': json.dumps({
                'forecast_type': 'single_today',
                'geo': 2,
                'type': '1234',
                'text': u'Какой-то текст'
            }),
            'geo': 213
        },
        'search': ['url'],
        'expected': {
            'path': r'^/pogoda/2$',
            'args': {'appsearch_header': r'^1$', 'appsearch_ys': r'^2$'}
        }
    },
    {
        'title': 'weather_disaster',
        'id': 'weather_disaster',
        'params': {
            'assist': 'weather_disaster',
            'assist_weather_disaster': json.dumps({
                'provider': '1234',
                'geo': 213,
                'text': u'Какой-то текст'
            }),
            'geo': 213
        },
        'search': ['url'],
        'expected': {
            'path': r'^/pogoda/213$',
            'args': {'appsearch_header': r'^1$'}
        }
    }
]


class AssistException:
    def __init__(self, str):
        self.str = str


@allure.feature('assist')
class TestAssist(object):

    @allure.story('assist_weather_ys_bad')
    @pytest.mark.yasm(signal='assist_weather_ys_bad_{}_tttt')
    @pytest.mark.parametrize('args', test_arg_sets)
    def test_weather_ys_bad(self, yasm, args):
        if 'skip_if' in args and getattr(self, args['skip_if'])(args):
            return

        signal = 'assist_weather_ys_bad_tttt'

        try:
            self._weather_ys_bad(yasm, args)
            yasm.add_to_signal(signal, 0)
        except RequestException:
            yasm.add_to_signal('assist_weather_ys_bad_test_request_expection_tttt', 1)
            return
        except AssistException as e:
            yasm.add_to_signal('assist_weather_ys_bad_test_{}_tttt'.format(e.str), 1)
            yasm.add_to_signal(signal, 1)
            raise AssertionError(u'Проверка ys-сслыки в блоке assist провалена: ' + e.str)

    def _weather_ys_bad(self, yasm, args):
        morda = DesktopMain(region=Regions.MOSCOW)
        client = MordaClient(morda=morda)
        url = client.make_url(base_url)
        test_params = args['params'].copy()
        test_params.update(common_params)
        request = client.request(url=url, params=test_params)
        request.headers['X-Yandex-Autotests'] = 'assist'
        response = request.send()

        try:
            assist = next(x for x in response.json()['block'] if x['id'] == 'assist')
        except StopIteration:
            raise AssistException('no_assist')

        try:
            block = next(x for x in assist['data']['blocks'] if x['id'] == args['id'])
        except StopIteration:
            raise AssistException('no_block')

        data = [block['data']]

        try:
            for key in args['search']:
                if key == '*':
                    _list = []

                    for x in data:
                        _list.extend(x)

                    data = _list
                else:
                    data = [x[key] for x in data]
        except Exception:
            raise AssistException('bad_search')

        try:
            expected = args['expected']

            for item in data:
                url = urlparse(item)

                if url.scheme != 'yellowskin':
                    raise AssistException('schema')

                # разные версии urlparse парсят пустой путь по разному ((
                if url.path:
                    url = parse_qs(url.path).get('url')
                else:
                    url = parse_qs(url.query).get('url')

                if not isinstance(url, list):
                    raise AssistException('arg_url')

                url = urlparse(url[0])

                if url.scheme not in ['http', 'https']:
                    raise AssistException('schema')

                qs = parse_qs(url.query)

                if 'path' in expected and re.match(expected['path'], url.path) is None:
                    raise AssertionError('url_path')

                for key, regexp in expected['args'].iteritems():
                    value = qs.get(key)

                    if not isinstance(value, list) or re.match(regexp, value[0]) is None:
                        raise AssertionError('url_arg_' + key)

                if 'hash' in expected and re.match(expected['hash'], url.fragment) is None:
                    raise AssertionError('url_hash')

        except AssistException:
            raise
        except Exception:
            raise AssertionError('bad_url')

    # если нет осадков, то и нечего тестировать ((
    def skip_nowcast(self, params):
        session = Session()
        url = 'https://api.weather.yandex.ru/v1/alerts/nowcast'
        getargs = {
            'lat': params['params']['lat'],
            'lon': params['params']['lon'],
            'X-Yandex-API-Key': '6030567e-f2e6-4b0d-aa47-8afa1cf41fa1'
        }
        res = Req(session=session, url=url, params=getargs, allow_retry=True, retries=10).send()

        if not res.is_ok():
            return True

        data = res.json()

        if data.state in ['noprec', 'nodata', 'norule']:
            return True

        return False
