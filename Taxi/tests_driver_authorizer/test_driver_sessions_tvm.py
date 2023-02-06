import json

import pytest


@pytest.mark.config(TVM_ENABLED=True)
async def test_tvm_invalid_auth_token_deny(taxi_driver_authorizer):
    data = {'client_id': 'taximeter'}
    headers = {'X-Ya-Service-Ticket': 'invalid_ticket'}

    response = await taxi_driver_authorizer.post(
        'driver/sessions/check', headers=headers, data=json.dumps(data),
    )
    assert response.status_code == 401
    message = response.json()['message']
    assert message == 'Bad tvm2 service ticket'


@pytest.mark.config(TVM_ENABLED=True)
async def test_tvm_no_auth_token_deny(taxi_driver_authorizer):
    data = {'client_id': 'taximeter'}

    response = await taxi_driver_authorizer.post(
        'driver/sessions/check', data=json.dumps(data),
    )
    assert response.status_code == 401
    message = response.json()['message']
    assert message == 'missing or empty X-Ya-Service-Ticket header'


@pytest.mark.config(TVM_ENABLED=True)
async def test_tvm_no_auth_token_deny_old(taxi_driver_authorizer):
    data = {'client_id': 'taximeter'}

    response = await taxi_driver_authorizer.post(
        'driver_session', data=json.dumps(data),
    )
    assert response.status_code == 401
