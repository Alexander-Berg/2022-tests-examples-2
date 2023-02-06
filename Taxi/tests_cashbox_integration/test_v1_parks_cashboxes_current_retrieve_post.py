import pytest


ENDPOINT = '/v1/parks/cashboxes/current/retrieve'


@pytest.mark.parametrize(
    'park_id, expected_response',
    [
        ('park_123', {'park_id': 'park_123', 'cashbox_id': 'id_abc456'}),
        ('park_wo_current', {'park_id': 'park_wo_current'}),
        ('park_net_takogo', {'park_id': 'park_net_takogo'}),
    ],
)
async def test_ok(taxi_cashbox_integration, park_id, expected_response):
    response = await taxi_cashbox_integration.post(
        ENDPOINT, json={'park_id': park_id},
    )
    assert response.status_code == 200, response.text
    assert response.json() == expected_response
