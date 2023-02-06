# -*- coding: utf-8 -*-
import logging

from passport.backend.qa.test_user_service.tus_api.common.idm.idm_settings import (
    admin_name,
    admin_role_name,
    IDM_OAUTH_TOKEN,
    IDM_ROLE_REQUEST_PATH_PATTERN,
    IDM_SYSTEM,
    prefix,
    role_name,
    user_name,
    user_role_name,
)
from passport.backend.qa.test_user_service.tus_api.exceptions import TemporarilyUnavailableError
from passport.backend.qa.test_user_service.tus_api.request_id import get_request_id
from passport.backend.qa.test_user_service.tus_api.settings import (
    IDM_ENV,
    SSL_CA_CERT,
    TUS_ENV,
)
from passport.backend.qa.test_user_service.tus_api.utils import (
    rename_exception_decorator,
    retry_decorator,
)
import requests
from requests import ConnectionError


log = logging.getLogger(__name__)


class IdmApiRequest:

    def __init__(self):
        self.api_host = IDM_ENV[TUS_ENV]['host']

    @rename_exception_decorator((ConnectionError,), TemporarilyUnavailableError)
    @retry_decorator(exception=(ConnectionError,))
    def get(self, api_handle, parameters, headers):
        return requests.get(
            'https://{idm_api_host}{prefix}/{idm_api_handle}/'.format(
                idm_api_host=self.api_host,
                prefix=prefix,
                idm_api_handle=api_handle,
            ),
            params=parameters,
            headers=headers,
            verify=SSL_CA_CERT,
        )

    @rename_exception_decorator((ConnectionError,), TemporarilyUnavailableError)
    @retry_decorator(exception=(ConnectionError,))
    def post(self, api_handle, json_data, headers):
        return requests.post(
            'https://{idm_api_host}{prefix}/{idm_api_handle}/'.format(
                idm_api_host=self.api_host,
                prefix=prefix,
                idm_api_handle=api_handle,
            ),
            json=json_data,
            headers=headers,
            verify=SSL_CA_CERT,
        )

    def call_idm_rolenodes(self, parent, slug, name, responsibilities=None):
        data = {
            'system': IDM_SYSTEM,
            'parent': parent,
            'slug': slug,
            'name': name,
        }
        if responsibilities:
            data['responsibilities'] = responsibilities

        headers = {
            'X-System-Request-Id': get_request_id(),
            'Content-Type': 'application/json',
            'Authorization': 'OAuth {token}'.format(token=IDM_OAUTH_TOKEN)
        }
        response = self.post(api_handle='rolenodes', json_data=data, headers=headers)
        response.raise_for_status()
        log.debug('Node {parent}{slug} was added'.format(parent=parent, slug=slug))

    def call_idm_rolerequests(self, login, path):
        data = {
            'system': IDM_SYSTEM,
            'user': login,
            'path': path,
        }
        headers = {
            'X-System-Request-Id': get_request_id(),
            'Content-Type': 'application/json',
            'Authorization': 'OAuth {token}'.format(token=IDM_OAUTH_TOKEN)
        }
        response = self.post(api_handle='rolerequests', json_data=data, headers=headers)
        response.raise_for_status()
        return response.json()


def add_new_consumer_to_idm(consumer, login):
    parent = '/tus_consumer/'
    parent_with_consumer = '/tus_consumer/{consumer}/'.format(consumer=consumer)
    parent_with_consumer_and_role = '/tus_consumer/{consumer}/role/'.format(consumer=consumer)
    responsibilities = [{'username': login, 'notify': True}]

    log.debug('Call IDM rolenodes')
    IdmApiRequest().call_idm_rolenodes(parent, consumer, consumer, responsibilities)
    IdmApiRequest().call_idm_rolenodes(parent_with_consumer, 'role', role_name)
    IdmApiRequest().call_idm_rolenodes(parent_with_consumer_and_role, admin_role_name, admin_name)
    IdmApiRequest().call_idm_rolenodes(parent_with_consumer_and_role, user_role_name, user_name)


def give_role_for_user(login, consumer, role):
    path = IDM_ROLE_REQUEST_PATH_PATTERN.format(consumer=consumer, role=role)
    idm_response = IdmApiRequest().call_idm_rolerequests(login, path)
    log.debug('rolerequests result: {}'.format(idm_response))
