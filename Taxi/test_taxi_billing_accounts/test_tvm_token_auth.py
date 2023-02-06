# coding=utf-8
import pytest


@pytest.mark.config(TVM_ENABLED=True)
@pytest.mark.pgsql('billing_accounts@0', files=('meta.sql',))
@pytest.mark.pgsql('billing_accounts@1', files=('meta.sql',))
async def test_tvm_token_auth(
        billing_accounts_client, request_headers, patched_tvm_ticket_check,
):
    # pylint: disable=too-many-statements
    # Write handlers
    # Without token
    response = await billing_accounts_client.post(
        '/v1/accounts/create', json={},
    )
    assert response.status == 403
    response = await billing_accounts_client.post(
        '/v1/entities/create', json={},
    )
    assert response.status == 403
    response = await billing_accounts_client.post(
        '/v2/journal/append', json={},
    )
    assert response.status == 403

    # With token
    response = await billing_accounts_client.post(
        '/v1/accounts/create', headers=request_headers, json={},
    )
    assert response.status == 400
    response = await billing_accounts_client.post(
        '/v1/entities/create', headers=request_headers, json={},
    )
    assert response.status == 400
    response = await billing_accounts_client.post(
        '/v2/journal/append', headers=request_headers, json={},
    )
    assert response.status == 400

    # Read handlers
    # Without token
    response = await billing_accounts_client.post(
        '/v1/accounts/search', json={},
    )
    assert response.status == 403
    response = await billing_accounts_client.post(
        '/v1/entities/search', json={},
    )
    assert response.status == 403
    response = await billing_accounts_client.post(
        '/v1/balances/select', json={},
    )
    assert response.status == 403
    response = await billing_accounts_client.post(
        '/v2/accounts/search', json={},
    )
    assert response.status == 403
    response = await billing_accounts_client.post(
        '/v2/journal/select', json={},
    )
    assert response.status == 403
    response = await billing_accounts_client.post(
        '/v2/balances/select', json={},
    )
    assert response.status == 403

    # With token
    response = await billing_accounts_client.post(
        '/v1/accounts/search', headers=request_headers, json={},
    )
    assert response.status == 400
    response = await billing_accounts_client.post(
        '/v1/entities/search', headers=request_headers, json={},
    )
    assert response.status == 400
    response = await billing_accounts_client.post(
        '/v1/balances/select', headers=request_headers, json={},
    )
    assert response.status == 400
    response = await billing_accounts_client.post(
        '/v2/accounts/search', headers=request_headers, json={},
    )
    assert response.status == 400
    response = await billing_accounts_client.post(
        '/v2/journal/select', headers=request_headers, json={},
    )
    assert response.status == 400
    response = await billing_accounts_client.post(
        '/v2/balances/select', headers=request_headers, json={},
    )
    assert response.status == 400
