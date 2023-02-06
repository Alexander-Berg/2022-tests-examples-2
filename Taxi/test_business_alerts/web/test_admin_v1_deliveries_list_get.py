import pytest

URI = '/admin/v1/deliveries/list'


@pytest.mark.parametrize(
    'tst_request, expected_status',
    [pytest.param(dict(offset=0, count=10), 200, id='base')],
)
async def test_base(
        taxi_business_alerts_web, tst_request, expected_status, atlas_backend,
):
    response = await taxi_business_alerts_web.get(URI, params=tst_request)
    assert response.status == expected_status
    assert await response.json()
