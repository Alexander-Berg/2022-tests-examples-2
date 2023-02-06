import pytest

from . import utils as test_utils


@pytest.mark.parametrize(
    'json, expected_code, pg_response',
    [
        (
            {
                'zone': 'moscow',
                'status': 'bronze',
                'reward': 'point_b',
                'title_key': 'loyalty.reward.title_point_b',
                'description_key': 'loyalty.reward.description_point_b',
                'navigate_type': 'navigate_loyalty_info',
                'can_be_locked': False,
            },
            200,
            [
                (
                    'loyalty.reward.title_point_b',
                    'loyalty.reward.description_point_b',
                    'navigate_loyalty_info',
                    False,
                    None,
                ),
            ],
        ),
        (
            {
                'zone': 'moscow',
                'status': 'bronze',
                'reward': 'bank',
                'title_key': 'loyalty.reward.title_bank',
                'description_key': 'loyalty.reward.description_bank',
                'navigate_type': 'navigate_loyalty_info',
                'can_be_locked': True,
                'lock_reasons': {'activity': 90},
            },
            200,
            [
                (
                    'loyalty.reward.title_bank',
                    'loyalty.reward.description_bank',
                    'navigate_loyalty_info',
                    True,
                    '(90,)',
                ),
            ],
        ),
        (
            {
                'zone': 'spb',
                'status': 'platinum',
                'reward': 'bank',
                'title_key': 'loyalty.reward.title_bank',
                'description_key': 'loyalty.reward.description_bank',
                'navigate_type': 'navigate_loyalty_bank_cards',
                'can_be_locked': False,
            },
            200,
            [
                (
                    'loyalty.reward.title_bank',
                    'loyalty.reward.description_bank',
                    'navigate_loyalty_bank_cards',
                    False,
                    None,
                ),
            ],
        ),
        (
            {
                'zone': 'moscow',
                'status': 'gold',
                'reward': 'point_b',
                'title_key': 'loyalty.reward.title_point_b',
                'description_key': 'loyalty.reward.description_point_b',
                'navigate_type': 'navigate_loyalty_info',
                'can_be_locked': True,
                'lock_reasons': {'tags': ['bad_driver', 'good_tag']},
            },
            200,
            [
                (
                    'loyalty.reward.title_point_b',
                    'loyalty.reward.description_point_b',
                    'navigate_loyalty_info',
                    True,
                    '(,"{bad_driver,good_tag}")',
                ),
            ],
        ),
        (
            {
                'zone': 'moscow',
                'status': 'bronze',
                'reward': 'bank',
                'title_key': 'loyalty.reward.title_new_bank',
                'description_key': 'loyalty.reward.description_new_bank',
                'navigate_type': 'navigate_loyalty_info',
                'can_be_locked': True,
            },
            400,
            None,
        ),
        (
            {
                'zone': 'moscow',
                'status': 'bronze',
                'reward': 'new_reward',
                'title_key': 'loyalty.reward.title_bank',
                'description_key': 'loyalty.reward.description_bank',
                'navigate_type': 'navigate_loyalty_info',
                'can_be_locked': True,
            },
            400,
            None,
        ),
    ],
)
@pytest.mark.pgsql('loyalty', files=['loyalty_rewards.sql'])
async def test_admin_driver_reward_post(
        taxi_loyalty, pgsql, load_json, json, expected_code, pg_response,
):
    def select_reward(zone, status, reward):
        cursor = pgsql['loyalty'].cursor()
        cursor.execute(
            'SELECT title_key, description_key, navigate_type, '
            'can_be_locked, lock_reasons FROM loyalty.rewards '
            'WHERE zone = \'{}\' AND status = \'{}\' AND '
            'reward = \'{}\''.format(zone, status, reward),
        )
        result = list(row for row in cursor)
        cursor.close()
        return result

    response = await taxi_loyalty.post(
        'admin/loyalty/v1/reward',
        json=json,
        headers={'X-Ya-Service-Ticket': test_utils.LOYALTY_SERVICE_TICKET},
    )

    assert response.status_code == expected_code
    if response.status_code == 200:
        pg_reward = select_reward(json['zone'], json['status'], json['reward'])
        assert pg_reward == pg_response
        assert 'reward_id' in response.json()
