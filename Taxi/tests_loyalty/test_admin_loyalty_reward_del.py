import pytest

from . import utils as test_utils


@pytest.mark.parametrize(
    'reward_id, expected_code, expected_response',
    [
        ('bb331ff042b68d75d0bd708488fb4711', 200, 'expected_response1.json'),
        ('bb331ff042b68d75d0bd708488fb4715', 200, 'expected_response2.json'),
        ('bb331ff042b68d75d0bd708488fb4700', 404, None),
    ],
)
@pytest.mark.pgsql('loyalty', files=['loyalty_rewards.sql'])
async def test_admin_driver_reward_del(
        taxi_loyalty,
        pgsql,
        load_json,
        reward_id,
        expected_code,
        expected_response,
):
    def select_reward(reward_id):
        cursor = pgsql['loyalty'].cursor()
        cursor.execute(
            'SELECT * FROM loyalty.rewards '
            'WHERE id = \'{}\''.format(reward_id),
        )
        result = list(row for row in cursor)
        cursor.close()
        return result

    response = await taxi_loyalty.delete(
        'admin/loyalty/v1/reward',
        params={'id': reward_id},
        headers={'X-Ya-Service-Ticket': test_utils.LOYALTY_SERVICE_TICKET},
    )

    assert response.status_code == expected_code
    if response.status_code == 200:
        reward = select_reward(reward_id)
        assert reward == []
        assert response.json() == load_json('response/' + expected_response)
