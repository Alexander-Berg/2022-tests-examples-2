from typing import Optional

import pytest


_ENABLE_AUTH = pytest.mark.config(TRANSACTIONS_ID_NAMESPACE_AUTH_ENABLED=True)
_V2_CREATE_BODY = {
    'id': 'new-order',
    'invoice_due': '2019-05-01 03:00:00Z',
    'currency': 'RUB',
    'yandex_uid': '123',
    'personal_phone_id': 'personal-id',
    'payments': [],
    'pass_params': {},
    'user_ip': '127.0.0.1',
}


def _v2_create_body(id_namespace: Optional[str] = None) -> dict:
    body = dict(_V2_CREATE_BODY)
    if id_namespace is not None:
        body['id_namespace'] = id_namespace
    return body


@pytest.mark.parametrize(
    'path, body, expected_status',
    [
        # legacy handle, no auth
        pytest.param(
            '/invoice/retrieve', {'id': 'my-order'}, 200, marks=[_ENABLE_AUTH],
        ),
        # auth disabled
        ('/v2/invoice/create', _v2_create_body(), 200),
        # auth enabled, no id_namespace in body
        pytest.param(
            '/v2/invoice/create', _v2_create_body(), 403, marks=[_ENABLE_AUTH],
        ),
        # auth enabled, id_namespace not found in *_AUTH_RULES
        pytest.param(
            '/v2/invoice/create',
            _v2_create_body(id_namespace='unknown_namespace'),
            403,
            marks=[_ENABLE_AUTH],
        ),
        # auth enabled, service has no right to access specified id_namespace
        pytest.param(
            '/v2/invoice/create',
            _v2_create_body(id_namespace='restricted_namespace'),
            403,
            marks=[_ENABLE_AUTH],
        ),
        # auth enabled, service has rights to access specified id_namespace
        pytest.param(
            '/v2/invoice/create',
            _v2_create_body(id_namespace='testsuite_namespace'),
            200,
            marks=[_ENABLE_AUTH],
        ),
    ],
)
@pytest.mark.config(
    TRANSACTIONS_ID_NAMESPACE_AUTH_RULES={
        'testsuite_namespace': {'tvm_service_names': ['testsuite']},
        'restricted_namespace': {
            'tvm_service_names': ['super_secret_tvm_service'],
        },
    },
    TVM_ENABLED=True,
    TRANSACTIONS_USE_LIGHTWEIGHT_STATUS_ENABLED=True,
    TRANSACTIONS_USE_LIGHTWEIGHT_STATUS_PROBABILITY=1.0,
)
async def test_id_namespace_auth(
        ng_web_app_client,
        mock_tvm_get_allowed_service_name,
        path,
        body,
        expected_status,
):
    response = await ng_web_app_client.post(
        path, json=body, headers={'X-Ya-Service-Ticket': 'ticket'},
    )
    assert response.status == expected_status


@pytest.fixture(name='mock_tvm_get_allowed_service_name')
def _mock_tvm_get_allowed_service_name(patch):
    @patch('taxi.clients.tvm.TVMClient.get_allowed_service_name')
    async def get_service_name(ticket_body, **kwargs):
        return 'testsuite'

    return get_service_name
