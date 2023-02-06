import pytest

# Enable tvm autentification, it's disabled in tests by default
@pytest.mark.config(TVM_ENABLED=True)
async def test_retries_fallback_count(taxi_userver_sample):
    response = await taxi_userver_sample.get('auth/tvm2')
    assert response.status_code == 401
    assert response.content == b'missing or empty X-Ya-Service-Ticket header'
