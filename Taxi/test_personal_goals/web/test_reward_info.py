import json

import pytest

from personal_goals import const


@pytest.mark.parametrize(
    'goal_id, expected_code, expected_json',
    [
        ('random_goal_id', 409, None),
        ('9921d89db101479ab1e476d8910d72fb', 409, None),
        (
            'c69e65c601c04ffdaa6277c80cafe7f8',
            200,
            {
                'user_goal_id': 'c69e65c601c04ffdaa6277c80cafe7f8',
                'reward': {
                    'status': const.REWARD_STATUS_NOT_REWARDED,
                    'yandex_uid': '666666',
                    'bonus': {
                        'type': 'promocode',
                        'currency': 'RUB',
                        'value': '400',
                        'percent': '10',
                        'series': 'bonus',
                    },
                },
            },
        ),
        (
            'bcf19460bdc34c439842a63fadb20fa8',
            200,
            {
                'user_goal_id': 'bcf19460bdc34c439842a63fadb20fa8',
                'reward': {
                    'status': const.REWARD_STATUS_REWARDED,
                    'yandex_uid': '666666',
                    'bonus': {
                        'type': 'promocode',
                        'currency': 'RUB',
                        'value': '150',
                        'series': 'cool',
                    },
                },
            },
        ),
    ],
)
@pytest.mark.pgsql('personal_goals', files=['basic_personal_goals.sql'])
async def test_reward_info(
        web_app_client, goal_id, expected_code, expected_json,
):
    data = {'user_goal_id': goal_id}
    response = await web_app_client.post(
        '/internal/reward/info', data=json.dumps(data),
    )
    assert response.status == expected_code

    if expected_json:
        response_json = await response.json()
        assert response_json == expected_json
