import pytest


from . import utils as test_utils


@pytest.mark.parametrize(
    'zone, expected_response',
    [
        ('moscow', 'expected_response1.json'),
        ('minsk', 'expected_response2.json'),
        ('spb', 'expected_response3.json'),
    ],
)
@pytest.mark.pgsql('loyalty', files=['loyalty_rewards.sql'])
async def test_admin_driver_rewards_get(
        taxi_loyalty, load_json, zone, expected_response,
):
    response = await taxi_loyalty.get(
        'admin/loyalty/v1/rewards',
        params={'zone': zone},
        headers={'X-Ya-Service-Ticket': test_utils.LOYALTY_SERVICE_TICKET},
    )

    assert response.status_code == 200
    assert response.json() == load_json('response/' + expected_response)
