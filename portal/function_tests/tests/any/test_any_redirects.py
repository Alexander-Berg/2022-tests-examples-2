# -*- coding: utf-8 -*-
import logging
from urlparse import urlparse

import allure
import pytest
from furl import furl
from hamcrest import equal_to, assert_that

from common.client import MordaClient
from common.http import Req, resolve_dns

logger = logging.getLogger(__name__)

_SAMPLE_PATH = ['a', 'b', 'c']
_SAMPLE_QUERY = 'q1=v1&q2=v2'


def _normalize(url, scheme):
    if url.startswith('//'):
        return '{}:{}'.format(scheme, url)
    return url


def get_x404_redirects(client):

    return []

    res = client.export('x404_redirects', no_allure=1, rh=1).send()
    assert res.is_ok(), 'Failed to get export'

    export = res.json()

    if 'export' in export:
        export = export['export']
    assert 'data' in export and 'all' in export['data'] and len(export['data']['all']) > 0, 'Failed to get export data'
    return [e for e in export['data']['all'] if e.get('skip_test', '0') != '1']


def get_any_cases(dns=False):
    client = MordaClient()
    data = get_x404_redirects(client)
    cases = []

    for case in data:
        from_url = case['from_url']
        to_url = case['to_url']

        if dns and not resolve_dns(from_url):
            continue

        if from_url.startswith('//'):
            cases.append((_normalize(from_url, 'http'), _normalize(to_url, 'http')))
            cases.append((_normalize(from_url, 'https'), _normalize(to_url, 'https')))
        else:
            scheme = urlparse(from_url).scheme
            cases.append((from_url, _normalize(to_url, scheme)))

    return cases


def prepare_urls(from_url, to_url):
    random_rid = Req.get_random_rid()
    parsed_from = furl(from_url)
    parsed_to = furl(to_url)

    if parsed_from.path and str(parsed_from.path)[-1] == '*':
        parsed_from.path.set(str(parsed_from.path)[:-1])
        parsed_from.path.segments.extend(_SAMPLE_PATH)

    if '$request_uri' in str(parsed_to.path):
        if not from_url.endswith('*'):
            parsed_from.path.segments.extend(_SAMPLE_PATH)
        parsed_to.path.set(str(parsed_to.path).replace('$request_uri', ''))
        parsed_to.path.add(_SAMPLE_PATH)

    if '$args' in str(parsed_to.path):
        parsed_to.add(args=_SAMPLE_QUERY)
        parsed_from.add(args=_SAMPLE_QUERY)
        parsed_to.path.set(str(parsed_to.path).replace('$args', ''))
        parsed_to.args['test_request_id'] = random_rid

    parsed_from.path.normalize()
    parsed_to.path.normalize()
    parsed_from.args['test_request_id'] = random_rid

    return parsed_from.url, parsed_to.url


@allure.step('Check correct redirect')
def check_redirect(res, to_url):
    assert res.is_ok(equal_to(301)) or res.is_ok(equal_to(302)), 'Failed to send any request'
    location = res.response.headers['Location']
    logger.debug('Expecting location: ' + to_url)
    logger.debug('Got location      : ' + location)
    assert_that(location, equal_to(to_url))


@allure.feature('any')
class TestAnyRedirects(object):
    @pytest.mark.yasm(signal='redirect_any_{}_tttt')
    @allure.story('any')
    @pytest.mark.skip('Тесты сломаны, т.к. половина редиректов переехала в балансер?')
    @pytest.mark.parametrize('from_url,to_url', get_any_cases())
    def test_any_redirects(self, from_url, to_url):
        client = MordaClient()
        from_url, to_url = prepare_urls(from_url, to_url)
        res = client.any(from_url).send()
        check_redirect(res, to_url)

    @pytest.mark.yasm(signal='redirect_any_plain_{}_tttt')
    @allure.story('plain')
    @pytest.mark.skip('Тесты сломаны, т.к. половина редиректов переехала в балансер?')
    @pytest.mark.parametrize('from_url,to_url', get_any_cases(True))
    def test_plain_redirects(self, from_url, to_url):
        from_url, to_url = prepare_urls(from_url, to_url)
        res = Req(from_url, allow_redirects=False, allow_retry=True, retries=10).send()
        check_redirect(res, to_url)
