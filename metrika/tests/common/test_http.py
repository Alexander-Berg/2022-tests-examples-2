import sys

from metrika.pylib.http import request, HTTPOAuth
from metrika.pylib.log import base_logger, init_logger
import pytest
from requests.exceptions import HTTPError, ConnectTimeout
from requests import Session
import requests_mock

logger = base_logger.manager.getLogger('metrika.pylib.http.tests')
init_logger('mtutils', stdout=True)
init_logger('urllib3', stdout=True)


def test_request():
    with requests_mock.Mocker() as m:
        m.get('http://a.a', status_code=200)
        r = request('http://a.a')
        assert r.status_code == 200


def test_request_exception():
    with requests_mock.Mocker() as m:
        m.get('http://a.a', status_code=404)
        with pytest.raises(HTTPError):
            logger.debug("Run test_request_exception")
            request('http://a.a')


def test_request_retry():
    with requests_mock.Mocker() as m:
        m.get('http://a.a', status_code=503)
        with pytest.raises(HTTPError):
            request('http://a.a', retry_if_http_error=True)

        assert m.call_count == 3


def test_request_without_exception():
    with requests_mock.Mocker() as m:
        m.get('http://a.a', status_code=401, json={'method': 'GET'})
        r = request('http://a.a', raise_for_status=False)
        assert r.status_code == 401
        assert r.request.method == 'GET'


def test_request_timeout():
    with requests_mock.Mocker() as m:
        m.get('http://a.a', exc=ConnectTimeout)
        with pytest.raises(ConnectTimeout):
            request('http://a.a', retry_if_http_error=False)

        assert m.call_count == 3


def test_post_request():
    with requests_mock.Mocker() as m:
        m.post('http://a.a?meta=false&status=203', status_code=203)
        r = request(
            'http://a.a',
            method='POST',
            params=dict(
                meta=False,
                status=203,
            ),
        )
        assert r.status_code == 203
        assert r.request.method == 'POST'


def test_session_request():
    with requests_mock.Mocker() as m:
        m.get('http://a.a', status_code=200, cookies={'sessioncookie': '123456789'})
        s = Session()
        r = request('http://a.a', session=s)
        assert r.status_code == 200
        assert r.request.headers.get('Cookie') is None

        s.cookies = r.cookies

        m.get('http://a.a/asd', status_code=200)
        r = request('http://a.a/asd', session=s)
        assert 'sessioncookie=123456789' in r.request.headers.get('Cookie', '')

        r = request('http://a.a/asd')
        assert r.request.headers.get('Cookie') is None

        s.headers.update({'x-test': 'true'})
        r = request('http://a.a/asd', headers={'x-test2': 'true'}, session=s)
        sent_headers = r.request.headers
        assert sent_headers.get('x-test') == 'true' and sent_headers.get('x-test2') == 'true'

        r = request('http://a.a/asd', session=s)
        sent_headers = r.request.headers
        assert sent_headers.get('x-test') == 'true' and sent_headers.get('x-test2') is None


def test_oauth():
    with requests_mock.Mocker() as m:
        def callback(request, context):
            context.headers['login'] = request.headers.get('Authorization', '')
            return 'OK'

        m.get('http://a.a', status_code=200, text=callback)

        r = request('http://a.a', oauth_token='asdqwe')
        assert r.headers.get('login') == 'OAuth asdqwe'

        r = request('http://a.a', auth=('test', 'test'))
        assert r.headers.get('login') == 'Basic dGVzdDp0ZXN0'

        r = request('http://a.a', auth=('test', 'test'), oauth_token='asdqwe')
        assert r.headers.get('login') == 'OAuth asdqwe'

        r = request('http://a.a')
        assert r.headers.get('login') == ''

        r = request('http://a.a', auth=HTTPOAuth('asdqwe'))
        assert r.headers.get('login') == 'OAuth asdqwe'


def test_default_user_agent():
    with requests_mock.Mocker() as m:
        m.get('http://a.a', status_code=200)
        r = request('http://a.a')
        if sys.version.startswith('2.'):
            agent = 'metrika.pylib.http py2_metrika-pylib-http-tests-common'
        else:
            agent = 'metrika.pylib.http metrika-pylib-http-tests-common'
        assert r.request.headers['User-Agent'].startswith(agent)


def test_user_agent_with_headers():
    with requests_mock.Mocker() as m:
        m.get('http://a.a', status_code=200)
        r = request('http://a.a', headers={'asd': 'qwe'})
        if sys.version.startswith('2.'):
            agent = 'metrika.pylib.http py2_metrika-pylib-http-tests-common'
        else:
            agent = 'metrika.pylib.http metrika-pylib-http-tests-common'
        assert r.request.headers['User-Agent'].startswith(agent)
        assert r.request.headers['asd'] == 'qwe'


def test_user_agent():
    with requests_mock.Mocker() as m:
        m.get('http://a.a', status_code=200)
        r = request('http://a.a', headers={'User-Agent': 'qwe'})
        assert r.request.headers['User-Agent'] == 'qwe'
