import time
import json

import pytest

from taxi.conf import settings
from taxi.core import arequests
from taxi.external import tvm


@pytest.mark.parametrize(
    'key,code,exc', [
        ('my_super_key', 200, None),
        ('key_super_my', 404, tvm.TvmRequestError),
        ('super_my_key', 500, tvm.TvmRequestError),
    ]
)
@pytest.inline_callbacks
def test_tvm_get_keys(key, code, exc, areq_request):
    @areq_request
    def requests_request(method, url, **kwargs):
        assert method == arequests.METHOD_GET
        if code == 200:
            return areq_request.response(200, body=key)
        else:
            return areq_request.response(code, body=None)
    if exc is None:
        result = (yield tvm.get_keys('test_service'))
        assert result is not None
        assert result == key
    else:
        with pytest.raises(exc):
            yield tvm.get_keys('test_service')


class TvmTicket(object):
    def __init__(self, src):
        self.src = src

    def debug_info(self):
        return 'debug_info: %s' % self.src


class DummyTvmServiceContext(object):
    def __init__(self, sc_sign, client_id, serv_id):
        self.sc_sign = sc_sign
        self.client_id = client_id
        self.serv_id = serv_id

    def sign(self, ts, serv_id):
        assert self.serv_id == serv_id
        assert ts == int(time.time())
        return self.sc_sign

    def check(self, body):
        return TvmTicket(self.client_id)


@pytest.mark.now('2016-07-01T00:00:00')
@pytest.mark.parametrize(
    'src_service_name,dst_service_name,tvm_keys,sign,code,service_exc,'
    'tvm_exc,ticket', [
        ('tc', 'antifraud', 'key1', 'sign1', 200, None, None, 'ticket1'),
        (
            'tc', 'antifraud', 'key2', 'sign2', 500, None,
            tvm.TvmRequestError, None,
        ),
        (
            'tc', 'unknown_service', 'key3', 'sign3', 200, tvm.ServiceNotFound,
            None, 'ticket3',
        )
    ]
)
@pytest.mark.config(TVM_ENABLED=True)
@pytest.mark.config(TVM_SERVICES={'tc': 1, 'antifraud': 2})
@pytest.mark.config(TVM_RULES=[{'src': 'tc', 'dst': 'antifraud'}])
@pytest.inline_callbacks
def test_get_ticket(src_service_name, dst_service_name, tvm_keys, sign, code,
                    service_exc, tvm_exc, ticket, patch, areq_request):

    src_service_id = settings.TVM_SERVICES[src_service_name]['id']
    src_service_secret = settings.TVM_SERVICES[src_service_name]['secret']
    if service_exc is not None:
        with pytest.raises(service_exc):
            dst_service_id = (yield tvm._get_service(dst_service_name))['id']
        return
    else:
        dst_service_id = (yield tvm._get_service(dst_service_name))['id']

    @patch('taxi.external.tvm.get_keys')
    def get_keys(service_name, log_extra=None):
        return tvm_keys

    @patch('ticket_parser2.api.v1.ServiceContext')
    def service_context(cli_id, cli_secret, keys):
        assert src_service_id == cli_id
        assert src_service_secret == cli_secret
        assert tvm_keys == keys
        return DummyTvmServiceContext(sign, src_service_id, dst_service_id)

    @areq_request
    def requests_request(method, url, **kwargs):
        assert method == arequests.METHOD_POST
        data = kwargs['data']
        assert data['grant_type'] == 'client_credentials'
        assert data['src'] == src_service_id
        assert data['dst'] == dst_service_id
        assert data['ts'] == 1467331200
        assert data['sign'] == sign
        if code == 200:
            return areq_request.response(
                200, body=json.dumps({str(dst_service_id): {'ticket': ticket}}))
        else:
            return areq_request.response(code, body=None)

    if tvm_exc is None:
        result = yield tvm.get_ticket(
            src_service_name, dst_service_name)
        assert result == ticket
    else:
        with pytest.raises(tvm_exc):
            yield tvm.get_ticket(
                src_service_name, dst_service_name)


@pytest.mark.now('2016-07-01T00:00:00')
@pytest.mark.parametrize(
    'src_service_name,dst_service_name,tvm_keys,sign', [
        ('antifraud', 'tc', 'key1', 'sign1'),
        ('tc', 'experiments', 'key1', 'sign1')
    ]
)
@pytest.mark.config(TVM_ENABLED=True)
@pytest.mark.config(TVM_DISABLE_CHECK=['experiments'])
@pytest.mark.config(TVM_SERVICES={'tc': 1, 'antifraud': 2, 'experiments': 3})
@pytest.mark.config(TVM_RULES=[{'src': 'antifraud', 'dst': 'tc'}])
@pytest.inline_callbacks
def test_check_ticket(src_service_name, dst_service_name, tvm_keys, sign,
                      patch, areq_request):

    src_service_id = (yield tvm._get_service(src_service_name))['id']
    dst_service_id = settings.TVM_SERVICES[dst_service_name]['id']

    @patch('taxi.external.tvm.get_keys')
    def get_keys(service_name, log_extra=None):
        return tvm_keys

    @patch('ticket_parser2.api.v1.ServiceContext')
    def service_context(cli_id, cli_secret, keys):
        return DummyTvmServiceContext(sign, src_service_id, dst_service_id)

    assert (yield tvm.check_ticket(dst_service_name, 'ticket_body'))
    assert not (yield tvm.check_ticket(src_service_name, 'ticket_body'))
