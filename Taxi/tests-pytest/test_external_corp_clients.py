import json

import pytest

from taxi.conf import settings
from taxi.core import async
from taxi.external import corp_clients
from taxi.external import tvm


@pytest.fixture
def tvm_mock(patch):
    @patch('taxi.external.tvm.get_auth_headers')
    @async.inline_callbacks
    def get_auth_headers(src_service, dst_service, log_extra):
        assert src_service == 'stq'
        assert dst_service == 'corp-clients'
        yield
        async.return_value({tvm.TVM_TICKET_HEADER: 'tvm_ticket'})
    return get_auth_headers


@pytest.mark.parametrize('status_code', [200, 400, 500])
@pytest.mark.parametrize(['request_fields', 'expected_fields'],
    [(None, None), (['_id', 'tz'], '_id,tz')])
@pytest.inline_callbacks
def test_get_client(
        status_code,
        tvm_mock,
        areq_request,
        monkeypatch,
        request_fields,
        expected_fields,
):
    @areq_request
    def requests_request(method, url, **kwargs):
        assert method == 'GET'
        assert url == 'kek/v1/clients'
        expected_params = {'client_id': 'some_client_id'}
        if expected_fields is not None:
            expected_params['fields'] = expected_fields

        assert kwargs['params'] == expected_params
        assert kwargs['headers']['Accept-Language'] == 'ru'
        assert kwargs['headers']['X-YaRequestId'] == 'something'
        assert kwargs['headers'][tvm.TVM_TICKET_HEADER] == 'tvm_ticket'
        if status_code == 200:
            return areq_request.response(
                status_code, body=json.dumps({})
            )
        else:
            return areq_request.response(status_code, body=json.dumps({}))

    monkeypatch.setattr(settings, 'CORP_CLIENTS_URL', 'kek',
                        raising=False)
    try:
        response = yield corp_clients.get_client_by_client_id(
            'some_client_id',
            fields=request_fields,
            tvm_src_service='stq',
            link_id='something',
            retries=5,
            retry_interval=0,
        )
        assert status_code == 200
        assert response == {}

    except corp_clients.BadRequestError:
        assert status_code == 400
        assert len(requests_request.calls) == 1
    except corp_clients.RequestRetriesExceeded:
        assert len(requests_request.calls) == 5


@pytest.mark.parametrize('status_code', [200, 400, 500])
@pytest.inline_callbacks
def test_get_service_taxi(
        status_code,
        tvm_mock,
        areq_request,
        monkeypatch,
):
    @areq_request
    def requests_request(method, url, **kwargs):
        assert method == 'GET'
        assert url == 'kek/v1/services/taxi'
        assert kwargs['params'] == {'client_id': 'some_client_id'}
        assert kwargs['headers']['Accept-Language'] == 'ru'
        assert kwargs['headers']['X-YaRequestId'] == 'something'
        assert kwargs['headers'][tvm.TVM_TICKET_HEADER] == 'tvm_ticket'
        if status_code == 200:
            return areq_request.response(
                status_code, body=json.dumps({})
            )
        else:
            return areq_request.response(status_code, body=json.dumps({}))

    monkeypatch.setattr(settings, 'CORP_CLIENTS_URL', 'kek',
                        raising=False)
    try:
        response = yield corp_clients.get_service_taxi(
            'some_client_id',
            tvm_src_service='stq',
            link_id='something',
            retries=5,
            retry_interval=0,
        )
        assert status_code == 200
        assert response == {}

    except corp_clients.BadRequestError:
        assert status_code == 400
        assert len(requests_request.calls) == 1
    except corp_clients.RequestRetriesExceeded:
        assert len(requests_request.calls) == 5


@pytest.mark.parametrize('status_code', [200, 400, 500])
@pytest.inline_callbacks
def test_get_service_cargo(
        status_code,
        tvm_mock,
        areq_request,
        monkeypatch,
):
    @areq_request
    def requests_request(method, url, **kwargs):
        assert method == 'GET'
        assert url == 'kek/v1/services/cargo'
        assert kwargs['params'] == {'client_id': 'some_client_id'}
        assert kwargs['headers']['Accept-Language'] == 'ru'
        assert kwargs['headers']['X-YaRequestId'] == 'something'
        assert kwargs['headers'][tvm.TVM_TICKET_HEADER] == 'tvm_ticket'
        if status_code == 200:
            return areq_request.response(
                status_code, body=json.dumps({})
            )
        else:
            return areq_request.response(status_code, body=json.dumps({}))

    monkeypatch.setattr(settings, 'CORP_CLIENTS_URL', 'kek',
                        raising=False)
    try:
        response = yield corp_clients.get_service_cargo(
            'some_client_id',
            tvm_src_service='stq',
            link_id='something',
            retries=5,
            retry_interval=0,
        )
        assert status_code == 200
        assert response == {}

    except corp_clients.BadRequestError:
        assert status_code == 400
        assert len(requests_request.calls) == 1
    except corp_clients.RequestRetriesExceeded:
        assert len(requests_request.calls) == 5
