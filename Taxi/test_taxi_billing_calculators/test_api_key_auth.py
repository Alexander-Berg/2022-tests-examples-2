# coding=utf-8
import pytest


@pytest.mark.config(TVM_ENABLED=True)
async def test_tvm_ticket_auth(
        taxi_billing_calculators_client,
        request_headers,
        patched_tvm_ticket_check,
):
    # Without token
    response = await taxi_billing_calculators_client.post(
        '/v1/process_doc', json={},
    )
    assert response.status == 403

    # Via invalid ticket
    bad_header = {'X-Ya-Service-Ticket': 'bad_ticket'}
    response = await taxi_billing_calculators_client.post(
        '/v1/process_doc', headers=bad_header, json={},
    )
    assert response.status == 403

    # Via correct ticket
    response = await taxi_billing_calculators_client.post(
        '/v1/process_doc', headers=request_headers, json={},
    )
    assert response.status == 400
