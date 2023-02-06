import json

import pytest

from taxi.conf import settings
from taxi.core import async
from taxi.external import corp_users
from taxi.external import tvm


@pytest.fixture
def tvm_mock(patch):
    @patch('taxi.external.tvm.get_auth_headers')
    @async.inline_callbacks
    def get_auth_headers(src_service, dst_service, log_extra):
        assert src_service == 'stq'
        assert dst_service == 'corp-users'
        yield
        async.return_value({tvm.TVM_TICKET_HEADER: 'tvm_ticket'})
    return get_auth_headers


@pytest.mark.parametrize('status_code', [200, 400, 500])
@pytest.inline_callbacks
def test_v2_users_get(
        status_code,
        tvm_mock,
        areq_request,
        monkeypatch,
):
    @areq_request
    def requests_request(method, url, **kwargs):
        assert method == 'GET'
        assert url == 'kek/v2/users'
        assert kwargs['params'] == {'user_id': 'some_user_id'}
        assert kwargs['headers']['Accept-Language'] == 'ru'
        assert kwargs['headers']['X-YaRequestId'] == 'something'
        assert kwargs['headers'][tvm.TVM_TICKET_HEADER] == 'tvm_ticket'
        if status_code == 200:
            return areq_request.response(
                status_code, body=json.dumps({})
            )
        else:
            return areq_request.response(status_code, body=json.dumps({}))

    monkeypatch.setattr(settings, 'CORP_USERS_URL', 'kek',
                        raising=False)
    try:
        response = yield corp_users.v2_users_get(
            'some_user_id',
            tvm_src_service='stq',
            link_id='something',
            retries=5,
            retry_interval=0,
        )
        assert status_code == 200
        assert response == {}

    except corp_users.BadRequestError:
        assert status_code == 400
        assert len(requests_request.calls) == 1
    except corp_users.RequestRetriesExceeded:
        assert len(requests_request.calls) == 5
