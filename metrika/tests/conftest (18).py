import os
import time
import pytest
import requests_mock
from requests.exceptions import ReadTimeout

import metrika.pylib.auth.lib as auth_lib
from metrika.pylib.auth import Auth, OAuth


# class FakeHosts(auth_lib.Hosts):
#     production = 'http://fake.bb/blackbox'
#     internal = 'http://fake.bb/internal'
#
#
# @pytest.fixture
# def mock_hosts(monkeypatch):
#     monkeypatch.setattr(auth_lib, 'Hosts', FakeHosts)

class FakeReadTimeout(ReadTimeout):
    def __init__(self, *args, **kwargs):
        time.sleep(2)
        super(FakeReadTimeout, self).__init__(*args, **kwargs)


@pytest.fixture()
def auth_instance():
    yield Auth('mimino')


@pytest.fixture
def slow_auth():
    with requests_mock.Mocker() as m:
        m.get(auth_lib.Hosts.production, exc=FakeReadTimeout)
        a = Auth('production')
        setattr(a, 'r_mock', m)
        yield a


@pytest.fixture
def broken_auth():
    with requests_mock.Mocker() as m:
        m.get(auth_lib.Hosts.production, status_code=503)
        a = Auth('production')
        setattr(a, 'r_mock', m)
        yield a


@pytest.fixture
def wrong_auth():
    with requests_mock.Mocker() as m:
        response = {u'status': {u'id': 5, u'value': u'INVALID'}, u'error': u'expired_token'}
        m.get(auth_lib.Hosts.production, json=response)
        yield Auth('production')


@pytest.fixture
def success_auth():
    with requests_mock.Mocker() as m:
        response = {
            u'status': {
                u'id': 0,
                u'value': u'VALID'
            },
            u'karma_status': {
                u'value': 0
            },
            u'have_password': True,
            u'uid': {
                u'lite': False,
                u'value': u'1120000000024771',
                u'hosted': False
            },
            u'have_hint': False,
            u'connection_id': u't:257553',
            u'karma': {
                u'value': 0
            },
            u'error': u'OK',
            u'oauth': {
                u'xtoken_id': u'',
                u'is_ttl_refreshable': False,
                u'ctime': u'2018-02-08 19:04:48',
                u'client_name': u'conductor-client',
                u'client_homepage': u'',
                u'client_ctime': u'2012-09-05 14:09:29',
                u'device_name': u'',
                u'client_icon': u'',
                u'client_is_yandex': False,
                u'meta': u'',
                u'issue_time': u'2018-02-08 19:04:48',
                u'client_id': u'eb3c509c74b649cd8411ffc154543fe0',
                u'scope': u'conductor:use startrek:write',
                u'expire_time': None,
                u'token_id': u'257553',
                u'device_id': u'',
                u'uid': u'1120000000024771'
            },
            u'login': u'robot-metrika-admin'
        }
        m.get(auth_lib.Hosts.production, json=response)
        yield Auth('production')


@pytest.fixture(scope='session')
def oauth_instance():
    with requests_mock.Mocker() as m:
        response = {'access_token': 'qweasd'}
        m.post(auth_lib.HostsOAuth.production.internal + '/token', json=response)
        yield OAuth('production', 'asd', 'qwe')


@pytest.fixture(scope='session')
def oauth_file():
    f_name = os.path.abspath('.123oauth')
    with open(f_name, 'w') as f:
        f.write('token: asd\n')

    yield f_name
    if os.path.isfile(f_name):
        os.unlink(f_name)


@pytest.fixture(scope='session')
def oauth_env_var():
    var_name = 'BLAHBLAHTOKEN'
    os.environ[var_name] = 'qwe'
    yield var_name
    os.environ.pop(var_name)
