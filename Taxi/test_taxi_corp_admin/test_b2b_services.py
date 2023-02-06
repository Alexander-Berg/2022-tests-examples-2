import pytest


@pytest.mark.parametrize(
    'expected_result',
    [
        ([{'service': 'drive', 'is_active': True}]),
        (
            [
                {'service': 'drive', 'is_active': True},
                {'service': 'eats', 'is_active': False},
            ]
        ),
    ],
)
async def test_get_b2b_services(taxi_corp_admin_client, expected_result):
    config = taxi_corp_admin_client.server.app.config
    config.CORP_ADMIN_B2B_SERVICES = expected_result

    response = await taxi_corp_admin_client.get('/v1/b2b-services')

    assert response.status == 200
    assert await response.json() == expected_result
