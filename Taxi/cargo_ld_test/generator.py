# This is a copy of taxi/logistic-dispatcher/tools/quick-tvm/quick_tvm_generator/generatory.py
# Made in order to make the tool work without arcadia assembly

import argparse
import logging
import time
import os
import sys

import furl

import requests
try:
    from ticket_parser2 import ticket_parser2_pymodule as ticket_parser2
except ModuleNotFoundError:
    from ticket_parser2_py3 import ticket_parser2_pymodule as ticket_parser2


LOGGER = logging.getLogger(__name__)


class TVM2UpdatableEntity:
    KEY_TTL = None  # key_ttl is expected to be given in seconds in descendant classes

    def __init__(self):
        self._last_update_time = 0
        self._key = None

    @property
    def content(self):
        current_time = time.time()
        if current_time - self._last_update_time > self.KEY_TTL:
            self._last_update_time = current_time
            self._key = self._refresh()
        return self._key

    def _refresh(self):
        raise NotImplementedError


class TVM2PublicKey(TVM2UpdatableEntity):
    KEY_TTL = 84540

    def __init__(self, host):
        super().__init__()
        request_furl = furl.furl(host)
        request_furl.join('/2/keys')
        request_furl.add({'lib_version': ticket_parser2.__version__})

        self._update_url = request_furl.url

    def _refresh(self):
        LOGGER.info('Re-downloading the public key.')
        response = requests.get(self._update_url, timeout=5)
        LOGGER.info('Re-download HTTP response status: %d', response.status_code)
        response.raise_for_status()

        return response.content.decode('utf-8')


class TVM2ServiceTicket(TVM2UpdatableEntity):
    KEY_TTL = 3540  # Service ticket is alive to an hour

    def __init__(self, host, source, destination, secret):
        super().__init__()
        self._host = host
        self._source = source
        self._destination = destination
        self._secret = secret

        self._request_url = self._form_request_url(host)
        self._public_key = TVM2PublicKey(host)

    def _refresh(self):
        LOGGER.info('Refreshing service ticket.')

        service_context = ticket_parser2.ServiceContext(
            self._source,
            self._secret,
            self._public_key.content,
        )

        cur_ts = int(time.time())
        signature = service_context.sign(cur_ts, self._destination)

        response = requests.post(
            self._request_url,
            data={
                'grant_type': 'client_credentials',
                'src': self._source,
                'dst': self._destination,
                'ts': cur_ts,
                'sign': signature,
            },
            timeout=5,
        )

        response.raise_for_status()

        return response.json()[str(self._destination)]['ticket']

    def _form_request_url(self, host):
        request_furl = furl.furl(host)
        request_furl.join('/2/ticket/')

        return request_furl.url

    def authenticate_ticket(self, source, ticket_body):
        service_context = ticket_parser2.ServiceContext(
            self._source,
            self._secret,
            self._public_key.content.encode('utf-8'),
        )

        try:
            parsed_ticket = service_context.check(ticket_body.encode('utf-8'))
            LOGGER.info('Parsed ticket src: %d', parsed_ticket.src)
            assert parsed_ticket.src == source
        except Exception:
            LOGGER.exception('unable to verify tvm2 ticket')
            return False

        return True


def get_tvm_secret(tvm_id):
    env_name = 'tvm_' + str(tvm_id)
    return os.environ.get(env_name)


def get_tvm_ticket(tvm_id_from, tvm_id_dest):
    ticket = TVM2ServiceTicket(
        'https://tvm-api.yandex.net/',
        int(tvm_id_from),
        int(tvm_id_dest),
        get_tvm_secret(tvm_id_from)
    )
    return ticket.content
