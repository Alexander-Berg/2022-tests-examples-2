import pytest


@pytest.mark.pgsql('billing_accounts@0', files=('meta.sql',))
@pytest.mark.pgsql('billing_accounts@1', files=('meta.sql',))
async def test_ping(billing_accounts_client):
    response = await billing_accounts_client.get('/ping')
    assert response.status == 200
    content = await response.text()
    assert content == ''
