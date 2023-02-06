import json

import pytest

from taxi.conf import settings
from taxi.core import async
from taxi.external import corp_integration_api
from taxi.external import tvm


@pytest.fixture
def tvm_mock(patch):
    @patch('taxi.external.tvm.get_auth_headers')
    @async.inline_callbacks
    def get_auth_headers(src_service, dst_service, log_extra):
        assert src_service == 'stq'
        assert dst_service == 'corp-integration-api'
        yield
        async.return_value({tvm.TVM_TICKET_HEADER: 'tvm_ticket'})
    return get_auth_headers


@pytest.mark.parametrize('status_code', [200, 400, 404, 409, 500])
@pytest.mark.parametrize('personal_phone_id', [
    None,
    '',
    {},  # for humbledb default missing attribute value in embedded objects
    'test_personal_phone_id'
])
@pytest.inline_callbacks
def test_corp_paymentmethods_only_phone(
        status_code,
        tvm_mock,
        areq_request,
        monkeypatch,
        personal_phone_id,
):
    @areq_request
    def requests_request(method, url, **kwargs):
        assert method == 'POST'
        assert url == 'kek/v1/corp_paymentmethods'
        expected_kwargs = {
            'class': 'buisness',
            'client_id': 'hz122323',
            'cost_center': 'old_cost_center',
            'cost_centers': [
                {
                    'id': 'cost_center',
                    'title': 'Cost center',
                    'value': 'business trip',
                }
            ],
            'driver_cost': 100,
            'identity': {
                'phone_id': '+71234567890',
                'uid': 23423423,
            },
            'route': [{'geopoint': [33.671, 55.15]}],
            'source': {'app': 'support'}
        }
        if personal_phone_id:
            expected_kwargs['identity']['personal_phone_id'] = personal_phone_id
        assert kwargs['json'] == expected_kwargs

        assert kwargs['headers']['Accept-Language'] == 'ru'
        assert kwargs['headers']['X-YaRequestId'] == 'something'
        assert kwargs['headers'][tvm.TVM_TICKET_HEADER] == 'tvm_ticket'
        if status_code == 200:
            return areq_request.response(
                status_code, body=json.dumps({})
            )
        else:
            return areq_request.response(status_code, body=json.dumps({}))

    monkeypatch.setattr(settings, 'CORP_INTEGRATION_API_URL', 'kek',
                        raising=False)
    try:
        response = yield corp_integration_api.corp_paymentmethods(
            tvm_src_service='stq',
            phone_id='+71234567890',
            personal_phone_id=personal_phone_id,
            uid=23423423,
            client_id='hz122323',
            source='support',
            route=[{'geopoint': [33.671, 55.150]}],
            driver_cost=100,
            tariff='buisness',
            cost_centers={
                'old': 'old_cost_center',
                'new': [
                    {
                        'id': 'cost_center',
                        'title': 'Cost center',
                        'value': 'business trip',
                    }
                ],
            },
            retries=5,
            retry_interval=0,
            link_id='something'
        )
        assert status_code == 200
        assert response == {}

    except corp_integration_api.BadRequestError:
        assert status_code == 400
        assert len(requests_request.calls) == 1
    except corp_integration_api.NotFoundError:
        assert status_code == 404
        assert len(requests_request.calls) == 1
    except corp_integration_api.ConflictError:
        assert status_code == 409
        assert len(requests_request.calls) == 1
    except corp_integration_api.RequestRetriesExceeded:
        assert len(requests_request.calls) == 5
