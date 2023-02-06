import pytest


@pytest.mark.pgsql('billing_docs@0', files=('meta.sql',))
@pytest.mark.pgsql('billing_docs@1', files=('meta.sql',))
async def test_ping(taxi_billing_docs_client):
    response = await taxi_billing_docs_client.get('/ping')
    assert response.status == 200
    content = await response.text()
    assert content == ''
