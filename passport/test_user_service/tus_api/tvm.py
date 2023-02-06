# -*- coding: utf-8 -*-
import logging

from passport.backend.qa.test_user_service.tus_api import settings
from passport.backend.qa.test_user_service.tus_api.exceptions import TvmToolError
import requests


log = logging.getLogger(__name__)


def get_tvm_service_tickets(destination):
    r = requests.get(
        'http://localhost:11111/tvm/tickets',
        params={
            'dsts': destination
        },
        headers={
            'Authorization': settings.TVMTOOL_LOCAL_AUTHTOKEN
        },
    )
    if r.status_code == 200:
        return r.json()[destination]['ticket']
    raise TvmToolError(r.text)


def validate_service_ticket(service_ticket):
    r = requests.get(
        'http://localhost:11111/tvm/checksrv',
        headers={
            'Authorization': settings.TVMTOOL_LOCAL_AUTHTOKEN,
            'X-Ya-Service-Ticket': service_ticket,
        },
    )
    data = r.json()
    if r.status_code == 403:
        raise TvmToolError(r.json()['error'])
    if data['src'] != settings.IDM_ENV[settings.TUS_ENV]['client_id']:
        raise TvmToolError('Undefined client service')


class TvmToolCredentialsManager:

    def get_dst(self, dst_alias):
        if dst_alias == 'kolmogor':
            return settings.kolmogor_config[settings.TUS_ENV]['tvmtool_dst']

    def get_ticket_by_alias(self, dst_alias):
        dst = self.get_dst(dst_alias)
        return get_tvm_service_tickets(dst)
