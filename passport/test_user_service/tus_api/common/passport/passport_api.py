# -*- coding: utf-8 -*-
import logging

from passport.backend.qa.test_user_service.tus_api.common.xunistater import request_time
from passport.backend.qa.test_user_service.tus_api.exceptions import (
    PassportBindPhoneFailed,
    ResponseParsingError,
    TemporarilyUnavailableError,
)
from passport.backend.qa.test_user_service.tus_api.request_id import get_request_id
from passport.backend.qa.test_user_service.tus_api.settings import (
    IP_WITHOUT_REGISTRATION_LIMITS,
    passport_config,
    PASSPORT_CONSUMER,
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

USER_AGENT_HEADER = 'Mozilla/5.0 TUS'


def _get_tvm_passport_ticket(env):
    tvm_destination = passport_config[env]['passport_api']['tvmtool_dst']
    return get_tvm_service_tickets(tvm_destination)


class PassportApiRequest:

    def __init__(self, env):
        self.env = env
        self.consumer = PASSPORT_CONSUMER
        self.api_host = passport_config[env]['passport_api']['host']

    @rename_exception_decorator((ConnectionError,), TemporarilyUnavailableError)
    @retry_decorator(exception=(ConnectionError,))
    @request_time(signal_name='passport')
    def post(self, api_handle, form_params, headers):
        return requests.post(
            'https://{passport_api_host}{passport_api_handle}?consumer={passport_consumer}&req_id={request_id}'.format(
                passport_api_host=self.api_host,
                passport_api_handle=api_handle,
                passport_consumer=self.consumer,
                request_id=get_request_id(),
            ),
            data=form_params,
            headers=headers,
            verify=SSL_CA_CERT,
        )

    @rename_exception_decorator((ConnectionError,), TemporarilyUnavailableError)
    @retry_decorator(exception=(ConnectionError,))
    @request_time(signal_name='passport')
    def get(self, api_handle, parameters, headers):
        return requests.get(
            'https://{passport_api_host}{passport_api_handle}?consumer={passport_consumer}&req_id={request_id}'.format(
                passport_api_host=self.api_host,
                passport_api_handle=api_handle,
                passport_consumer=self.consumer,
                request_id=get_request_id(),
            ),
            params=parameters,
            headers=headers,
            verify=SSL_CA_CERT,
        )

    def call_passport_registration(self, account_data):
        headers = {
            'Ya-Consumer-Client-Ip': IP_WITHOUT_REGISTRATION_LIMITS,
            'Ya-Client-User-Agent': USER_AGENT_HEADER,
            'X-Ya-Service-Ticket': _get_tvm_passport_ticket(self.env)
        }
        return self.post(
            '/1/bundle/account/register/',
            form_params=account_data,
            headers=headers
        )

    def call_confirm_and_bind_phone(self, uid, password, number, secure=True):
        request_form = {
            'uid': uid,
            'password': password,
            'number': number,
            'secure': secure,
        }
        headers = {
            'Ya-Consumer-Client-Ip': IP_WITHOUT_REGISTRATION_LIMITS,
            'Ya-Client-User-Agent': USER_AGENT_HEADER,
            'X-Ya-Service-Ticket': _get_tvm_passport_ticket(self.env)
        }
        return self.post(
            '/1/bundle/test/confirm_and_bind_phone/',
            form_params=request_form,
            headers=headers
        )

    def call_test_track(self, track_id):
        params = {
            'track_id': track_id,
        }
        headers = {
            'Ya-Consumer-Client-Ip': IP_WITHOUT_REGISTRATION_LIMITS,
            'X-Ya-Service-Ticket': _get_tvm_passport_ticket(self.env)
        }
        return self.get(
            '/1/bundle/test/track/',
            parameters=params,
            headers=headers
        )


def call_account_registration(account_data, env):
    passport_response = PassportApiRequest(env).call_passport_registration(account_data)
    data = passport_response.json()
    if 'errors' in data:
        return data['errors']
    if 'uid' in data:
        account_data['uid'] = str(data['uid'])
        return None
    raise ResponseParsingError('Failed parsing Passport API response: {}'.format(passport_response.text))


def bind_phone(uid, password, number, secure, env):
    confirm_and_bind_phone = PassportApiRequest(env).call_confirm_and_bind_phone(uid, password, number, secure)
    confirm_and_bind_phone.raise_for_status()
    bind_phone_response = confirm_and_bind_phone.json()
    if 'status' in bind_phone_response:
        if bind_phone_response.get('status') == 'ok':
            log.info('Number {number} was successfully bound to user with uid {uid}'.format(number=number, uid=uid))
        elif bind_phone_response.get('status') == 'error':
            raise PassportBindPhoneFailed(', '.join(bind_phone_response.get('errors')))
        else:
            raise PassportBindPhoneFailed('Failed to bind phone: {}'.format(confirm_and_bind_phone.text))
    else:
        raise ResponseParsingError('Failed parsing Passport API response: {}'.format(bind_phone_response))
