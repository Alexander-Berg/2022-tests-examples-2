import pytest

from metrika.pylib.log import init_logger, base_logger
from metrika.pylib.auth import get_robot_oauth_token
from metrika.pylib.auth.exceptions import GetTokenError
from metrika.pylib.auth.ssh import get_token_from_ssh_key

logger = base_logger.getChild('auth.tests')
init_logger('mtutils', stdout=True)


cookie = dict(
    Session_id='asd',
    sessionid2='qwe',
)


def test_wrong_cookie_auth(wrong_auth):
    answer = wrong_auth.cookie_auth(cookie, '127.0.0.1', 'haha.yandex.com.tr')
    assert answer.status is False
    assert answer.login is None
    assert answer.reason == 'expired_token'


def test_success_cookie_auth(success_auth):
    answer = success_auth.cookie_auth(cookie, userip='83.220.237.106', host='metrika.yandex.ru')
    assert answer.status is True
    assert answer.login == 'robot-metrika-admin'


def test_wrong_token_auth(wrong_auth):
    answer = wrong_auth.token_auth(userip='127.0.0.1', token='asdQWEhgf')
    assert answer.status is False
    assert answer.login is None
    assert answer.reason == 'expired_token'


def test_success_token_auth(success_auth):
    answer = success_auth.token_auth(
        token='asdQWE',
        userip='136.243.43.151',
    )
    assert answer.status is True
    assert answer.login == 'robot-metrika-admin'

    answer = success_auth.token_auth(
        auth_header='OAuth gfdMZXL',
        userip='136.243.43.151',
    )
    assert answer.status is True
    assert answer.login == 'robot-metrika-admin'


def test_slow_auth(slow_auth):
    answer = slow_auth.cookie_auth(cookie, userip='83.220.237.106', host='metrika.yandex.ru')
    assert slow_auth.r_mock.call_count == 5

    logger.debug(answer.reason)
    assert answer.status is False
    assert answer.login is None
    assert "Timeout on" in answer.reason


def test_broken_auth(broken_auth):
    answer = broken_auth.cookie_auth(cookie, userip='83.220.237.106', host='metrika.yandex.ru')
    assert broken_auth.r_mock.call_count == 5

    logger.debug(answer.reason)
    assert answer.status is False
    assert answer.login is None
    assert "Error code" in answer.reason


def test_oauth(oauth_instance):
    token = oauth_instance.get_token_by_login_password('asd', 'qwe')
    assert token == 'qweasd'


class TestTokenFromFile:
    def test_failed(self):
        with pytest.raises(GetTokenError):
            get_robot_oauth_token(
                filename='/does/not/exist',
                env_variable='does_not_exist',
            )

    def test_success(self, oauth_file):
        token = get_robot_oauth_token(oauth_file, env_variable=None)
        assert isinstance(token, str)
        assert token == 'asd'

    def test_from_env(self, oauth_env_var):
        token = get_robot_oauth_token(env_variable=oauth_env_var)
        assert isinstance(token, str)
        assert token == 'qwe'

    def test_both_file_and_env(self, oauth_file, oauth_env_var):
        token = get_robot_oauth_token(filename=oauth_file, env_variable=oauth_env_var)
        assert isinstance(token, str)
        assert token == 'qwe'


def test_wrong_ssh_keys():
    assert get_token_from_ssh_key(keys='asd') is None
