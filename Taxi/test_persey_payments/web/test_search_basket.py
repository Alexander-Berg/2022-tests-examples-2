import pytest


@pytest.mark.pgsql('persey_payments', files=['simple.sql'])
async def test_simple(
        taxi_persey_payments_web, mock_trust_check_basket, load_json,
):
    for item in load_json('request_response.json'):
        response = await taxi_persey_payments_web.post(
            '/v1/basket/search', json=item['request'],
        )

        assert response.status == 200
        assert await response.json() == item['response']
