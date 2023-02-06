import datetime

import freezegun
import pytest

from infranaim import config
from infranaim.models import configs as conf


def set_configs():
    config.CONFIGS['URL'] = 'http://test.ru'
    config.USE_CONFIG_SERVICE = 1


def unset_configs():
    config.USE_CONFIG_SERVICE = 0


def test_login_deactivated(
        flask_client, log_user_in, mongodb):
    data = {
        'login': 'deactivated_scout',
        'password': 'scout_pass'
    }
    res = log_user_in(data)
    assert res.status_code == 403


def test_login_non_existent(flask_client, log_user_in, mongodb):
    data = {
        'login': 'scout_non_existent',
        'password': 'scout_pass'
    }
    res = log_user_in(data)
    assert res.status_code == 400


def test_login_invalid_pass(
        flask_client, log_user_in, mongodb):
    data = {
        'login': 'scout',
        'password': 'invalid_pass'
    }
    res = log_user_in(data)
    assert res.status_code == 400


def test_login_invalid_csrf(
        flask_client, log_user_in):
    data = {
        'login': 'scout',
        'password': 'scout_pass',
        'csrf_token': 'ijijij'
    }
    res = log_user_in(data)
    assert res.status_code == 403


def test_login_valid(
        flask_client, log_user_in,
        log_user_out, find_ticket):
    data = {
        'login': 'scout',
        'password': 'scout_pass'
    }
    res = log_user_in(data)
    assert res.status_code == 200

    headers = res.headers
    res = log_user_out(headers)
    assert res.status_code == 200

    res = find_ticket(123, headers=headers)
    assert res.status_code == 401


def test_logout(
        log_user_in,
        log_user_out,
        flask_client,
):
    response = log_user_in({'login': 'scout', 'password': 'scout_pass'})
    assert response.status_code == 200
    headers = response.headers

    response = flask_client.get(
        '/tickets',
        headers=headers,
    )
    assert response.status_code == 200

    response = log_user_out(headers=headers)
    assert response.status_code == 200

    response = flask_client.get(
        '/tickets',
    )
    assert response.status_code == 401


@pytest.mark.parametrize(
    'user_doc, session_expires, tick_delay, external_config, del_expires_at',
    [
        (
                {'login': 'scout', 'password': 'scout_pass'},
                False,
                20,
                {
                    'configs':
                        {
                            'HIRING_SCOUTS_ROLE_EXPIRED_RULES': {
                                '__default__': {'__default__': 60 * 15},
                                'scout': {'__default__': 60 * 60 * 3}
                            }
                        }
                },
                False
        ),
        (
                {'login': 'agent', 'password': 'agent_pass'},
                True,
                20,
                {
                    'configs':
                        {
                            'HIRING_SCOUTS_ROLE_EXPIRED_RULES': {
                                '__default__': {'__default__': 60 * 15},
                                'scout': {'__default__': 60 * 60 * 3}
                            }
                        }
                },
                False
        ),
        (
                {'login': 'scout', 'password': 'scout_pass'},
                True,
                301,
                {
                    'configs':
                        {
                            'HIRING_SCOUTS_ROLE_EXPIRED_RULES': {
                                '__default__': {'__default__': 60 * 15},
                                'scout': {'__default__': 60 * 60 * 3}
                            }
                        }
                },
                False
        ),
        (
                {'login': 'scout', 'password': 'scout_pass'},
                True,
                301,
                {
                    'configs':
                        {
                            'HIRING_SCOUTS_ROLE_EXPIRED_RULES': {
                                '__default__': {'__default__': 60 * 15},
                                'scout': {'__default__': 60 * 60 * 3}
                            }
                        }
                },
                False
        ),
        (
                {'login': 'scout', 'password': 'scout_pass'},
                False,
                10,
                {
                    'configs':
                        {
                            'HIRING_SCOUTS_ROLE_EXPIRED_RULES': {
                                '__default__': {'__default__': 60 * 15},
                                'scout': {'__default__': 60 * 60 * 3}
                            }
                        }
                },
                True
        ),
        (
                {'login': 'agent', 'password': 'agent_pass'},
                True,
                10,
                {
                    'configs':
                        {
                            'HIRING_SCOUTS_ROLE_EXPIRED_RULES': {
                                '__default__': {'__default__': 60 * 15},
                                'agent': {
                                    '__default__': 60 * 60 * 3,
                                    'physical_person': 1
                                }
                            }
                        }
                },
                False
        ),
    ],
)
def test_expiration(
        log_user_in,
        flask_client,
        requests_mock,
        user_doc, session_expires, tick_delay, external_config, del_expires_at
):
    with freezegun.freeze_time('2019-10-04T14:00:00Z') as frozen_time:
        conf.external_config._updated_at = None
        set_configs()
        requests_mock.post(
            '{}/{}'.format(config.CONFIGS['URL'], 'configs/values'),
            json=external_config
        )
        response = log_user_in(user_doc)
        assert response.status_code == 200
        headers = response.headers
        response = flask_client.get(
            '/tickets',
            headers=headers,
        )
        assert response.status_code == 200

        frozen_time.tick(delta=datetime.timedelta(minutes=tick_delay))
        if del_expires_at:
            flask_client.delete_cookie('localhost.local', 'expires_at')
        response = flask_client.get(
            '/tickets',
            headers=headers,
        )
        assert response.status_code == (401 if session_expires else 200)
        response = flask_client.get(
            '/tickets',
            headers=headers,
        )
        assert response.status_code == (401 if session_expires else 200)
        unset_configs()


def test_auto_refresh_expiration_time(
        log_user_in,
        flask_client,
):
    def _request(code=200):
        resp = flask_client.get(
            '/tickets',
        )
        assert resp.status_code == code

    with freezegun.freeze_time('2019-10-04T14:00:00Z') as frozen_time:
        response = log_user_in({'login': 'agent', 'password': 'agent_pass'})
        assert response.status_code == 200
        _request()

        # 3 hours (default expire time) minus one minute
        step_min = 3 * 60 - 1
        for _ in range(5):
            frozen_time.tick(delta=datetime.timedelta(minutes=step_min))
            _request()
        frozen_time.tick(delta=datetime.timedelta(minutes=step_min+2))
        _request(code=401)


def test_cookie_validation_skip_paths(
        flask_client,
        log_user_in,
):
    with freezegun.freeze_time('2019-10-04T14:00:00Z') as frozen_time:
        response = log_user_in({'login': 'scout', 'password': 'scout_pass'})
        assert response.status_code == 200
        headers = response.headers

        # expire cookie
        frozen_time.tick(delta=datetime.timedelta(minutes=100500))

        response = flask_client.get(
            '/get_token',
            headers=headers,
        )
        assert response.status_code == 200
