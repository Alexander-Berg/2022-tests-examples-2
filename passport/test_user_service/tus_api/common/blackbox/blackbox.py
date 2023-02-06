# -*- coding: utf-8 -*-
import logging

from passport.backend.qa.test_user_service.tus_api.common.xunistater import request_time
from passport.backend.qa.test_user_service.tus_api.exceptions import (
    AccountNotFoundError,
    BlackboxAccountPasswordNotMatchLogin,
    BlackboxAccountUidNotMatchLogin,
    BlackboxOAuthTokenIsNotValid,
    ResponseParsingError,
    TemporarilyUnavailableError,
)
from passport.backend.qa.test_user_service.tus_api.fillers import normalize_login
from passport.backend.qa.test_user_service.tus_api.settings import (
    OAUTH_TUS_CLIENT_ID,
    passport_config,
    REQUIRED_OAUTH_SCOPE,
    SSL_CA_CERT,
)
from passport.backend.qa.test_user_service.tus_api.tvm import get_tvm_service_tickets
from passport.backend.qa.test_user_service.tus_api.utils import (
    rename_exception_decorator,
    retry_decorator,
)
import requests
from requests import ConnectionError


log = logging.getLogger(__name__)


def _get_tvm_blackbox_ticket(env):
    tvm_destination = passport_config[env]['blackbox']['tvmtool_dst']
    return get_tvm_service_tickets(tvm_destination)


class BlackboxApiRequest:

    def __init__(self, env):
        self.env = env
        self.host = passport_config[env]['blackbox']['host']

    @rename_exception_decorator((ConnectionError,), TemporarilyUnavailableError)
    @retry_decorator(exception=(ConnectionError,))
    @request_time(signal_name='blackbox')
    def get(self, parameters, headers=None):
        return requests.get(
            'https://{blackbox_host}/blackbox'.format(blackbox_host=self.host),
            params=parameters,
            headers=headers,
            verify=SSL_CA_CERT,
        )

    @rename_exception_decorator((ConnectionError,), TemporarilyUnavailableError)
    @retry_decorator(exception=(ConnectionError,))
    @request_time(signal_name='blackbox')
    def post(self, data, headers=None):
        return requests.post(
            'https://{blackbox_host}/blackbox'.format(blackbox_host=self.host),
            data=data,
            headers=headers,
            verify=SSL_CA_CERT,
        )

    def get_userinfo_by_uid(self, uid, user_ip):
        data = {
            'method': 'userinfo',
            'format': 'json',
            'userip': user_ip,
            'uid': uid,
        }
        headers = {
            'X-Ya-Service-Ticket': _get_tvm_blackbox_ticket(self.env),
        }
        response = self.post(data=data, headers=headers)
        response.raise_for_status()
        return response.json()

    def get_userinfo_by_login(self, login, user_ip):
        data = {
            'method': 'userinfo',
            'format': 'json',
            'userip': user_ip,
            'login': login,
        }
        headers = {
            'X-Ya-Service-Ticket': _get_tvm_blackbox_ticket(self.env),
        }
        response = self.post(data=data, headers=headers)
        response.raise_for_status()
        return response.json()

    def call_blackbox_validate_password(self, login, password, user_ip):
        data = {
            'method': 'login',
            'format': 'json',
            'userip': user_ip,
            'login': login,
            'password': password
        }
        headers = {
            'X-Ya-Service-Ticket': _get_tvm_blackbox_ticket(self.env),
        }
        response = self.post(data=data, headers=headers)
        response.raise_for_status()
        return response.json()

    def call_blackbox_validate_oauth_token(self, oauth_token, user_ip):
        parameters = {
            'method': 'oauth',
            'format': 'json',
            'userip': user_ip
        }
        headers = {
            'X-Ya-Service-Ticket': _get_tvm_blackbox_ticket(self.env),
            'Authorization': 'OAuth {token}'.format(token=oauth_token)
        }
        response = self.get(parameters, headers)
        response.raise_for_status()
        return response.json()

    def call_blackbox_loginoccupation(self, login, user_ip):
        data = {
            'method': 'loginoccupation',
            'format': 'json',
            'userip': user_ip,
            'logins': [login]
        }
        headers = {
            'X-Ya-Service-Ticket': _get_tvm_blackbox_ticket(self.env),
        }
        response = self.post(data, headers)
        response.raise_for_status()
        return response.json()


def get_userinfo_by_uid(uid, user_ip, env):
    bb_response = BlackboxApiRequest(env).get_userinfo_by_uid(uid, user_ip)
    log.debug("Blackbox 'userinfo' method was called with uid")
    if 'users' in bb_response and len(bb_response['users']) == 1:
        return bb_response
    raise ResponseParsingError('Failed parsing Blackbox response: {}'.format(bb_response))


def get_userinfo_by_login(login, user_ip, env):
    bb_response = BlackboxApiRequest(env).get_userinfo_by_login(login, user_ip)
    log.debug("Blackbox 'userinfo' method was called with login")
    if 'users' in bb_response and len(bb_response['users']) == 1:
        return bb_response
    raise ResponseParsingError('Failed parsing Blackbox response: {}'.format(bb_response))


def get_login_by_uid(uid, user_ip, env):
    userinfo = get_userinfo_by_uid(uid, user_ip, env)
    if 'login' in userinfo['users'][0]:
        return userinfo['users'][0]['login']
    raise AccountNotFoundError(
        'No account with uid {uid} found in Passport {env} environment'.format(uid=uid, env=env))


def get_uid_by_login(login, user_ip, env):
    userinfo = get_userinfo_by_login(login, user_ip, env)
    if 'id' in userinfo['users'][0] and userinfo['users'][0]['id']:
        return int(userinfo['users'][0]['id'])
    raise AccountNotFoundError(
        'No account with login {login} found in Passport {env} environment'.format(login=login, env=env))


def validate_oauth_token(oauth_token, user_ip):
    # Для валидации токена используется только TEAM окружение BB
    bb_response = BlackboxApiRequest('TEAM').call_blackbox_validate_oauth_token(oauth_token, user_ip)
    log.debug("Blackbox OAuth method was called")
    log.debug('user ip: {0}; \n response={1}'.format(user_ip, bb_response))
    if 'status' in bb_response:
        token_status = bb_response['status']['value']
        if token_status == 'VALID':
            scopes = bb_response['oauth']['scope'].split(' ')
            if REQUIRED_OAUTH_SCOPE in scopes:
                user_info = {
                    'uid': bb_response['uid']['value'],
                    'login': bb_response['login'],
                }
                return user_info
            raise BlackboxOAuthTokenIsNotValid(
                'Permission denied. OAuth token is not valid. Please create new token: '
                'https://oauth.yandex-team.ru/authorize?response_type=token&client_id={client_id}'.format(
                    client_id=OAUTH_TUS_CLIENT_ID,
                )
            )
        else:
            raise BlackboxOAuthTokenIsNotValid(bb_response['error'])
    else:
        raise ResponseParsingError('Failed parsing Blackbox response: {}'.format(bb_response))


def validate_password_for_login(login, password, user_ip, env):
    bb_response = BlackboxApiRequest(env).call_blackbox_validate_password(login, password, user_ip)
    log.debug("Blackbox 'login' method was called")
    if 'status' in bb_response:
        status = bb_response['status']['value']
        if status != 'VALID':
            raise BlackboxAccountPasswordNotMatchLogin(
                'Login and password validation failed with status {status} and error {error}'.format(
                    status=status, error=bb_response['error']
                )
            )
        log.debug('Blackbox: password for login {login} in env {env} is valid'.format(login=login, env=env))
    else:
        raise ResponseParsingError('Failed parsing Blackbox response: {}'.format(bb_response))


def is_login_free(login, user_ip, env):
    bb_response = BlackboxApiRequest(env).call_blackbox_loginoccupation(login, user_ip)
    log.debug("Blackbox 'loginoccupation' method was called")
    if 'logins' in bb_response:
        is_free = bb_response['logins'][login] == 'free'
        return is_free
    else:
        raise ResponseParsingError('Failed parsing Blackbox response: {}'.format(bb_response))


def check_uid_matches_login(uid, login, user_ip, env):
    actual_login = get_login_by_uid(uid, user_ip, env)
    if normalize_login(login) != normalize_login(actual_login):
        raise BlackboxAccountUidNotMatchLogin(
            'Received login does not match account login with uid {uid}'.format(uid=uid))
    log.debug('Blackbox: uid {uid} matches login {login}')
