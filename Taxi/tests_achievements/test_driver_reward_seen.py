import copy

import pytest

from tests_achievements import utils


PATH = '/driver/v1/achievements/v1/reward/seen'
PARK_ID = 'driver_db_id1'
DRIVER_ID = 'driver_uuid1'

SEEN_RESPONSE_TEMPLATE = {
    'category_ordering': [],
    'rewards': [
        {
            'code': 'express',
            'state': None,
            'level': 1,
            'title': 'Народный курьер',
            'description': 'Народный курьер - описание',
            'unlocked_at': '2019-02-01T01:00:00+00:00',
            'icons': {
                'full': {
                    'type': 'lottie',
                    'url': 'http://icons/express_unlocked_full.json',
                },
                'small': {
                    'type': 'png',
                    'url': 'http://icons/express_unlocked_small.png',
                },
                'background': {
                    'type': 'png',
                    'url': 'http://icons/express_background.png',
                },
            },
            'sharing': {
                'text': 'Народный курьер - текст для шеринга',
                'icon': {
                    'url': 'http://icons/express_sharing.png',
                    'type': 'png',
                },
            },
        },
    ],
}


@pytest.mark.pgsql('achievements_pg', files=['achievements.sql'])
@pytest.mark.parametrize(
    'udid, seen_rewards, expect_marked_seen',
    [
        ('udid1', [], set()),
        ('udid1', [{'code': 'express', 'level': 1}], {'express'}),
        ('udid1', [{'code': 'express', 'level': 2}], set()),
        ('udid1', [{'code': 'express', 'level': 0}], set()),
        (
            'udid1',
            [
                {'code': 'express', 'level': 1},
                {'code': 'star', 'level': 1},
                {'code': 'covid_hero', 'level': 1},
                {'code': 'top_fives', 'level': 1},
            ],
            {'express', 'star'},
        ),
        (
            'udid2',
            [
                {'code': 'express', 'level': 1},
                {'code': 'star', 'level': 1},
                {'code': 'covid_hero', 'level': 1},
                {'code': 'top_fives', 'level': 1},
            ],
            {'express', 'top_fives'},
        ),
        (
            'udid2',
            [
                # Even if input values are not unique,
                # only one correct value will be matched for UPDATE
                {'code': 'express', 'level': 0},
                {'code': 'express', 'level': 1},
                {'code': 'express', 'level': 1},
                {'code': 'express', 'level': 2},
                {'code': 'covid_hero', 'level': 1},
                {'code': 'top_fives', 'level': 1},
            ],
            {'express', 'top_fives'},
        ),
    ],
)
@pytest.mark.now('2020-01-01T12:00:00+0000')
async def test_driver_reward_seen(
        taxi_achievements,
        unique_drivers,
        driver_ui_profile_mock,
        udid,
        pgsql,
        seen_rewards,
        expect_marked_seen,
):
    unique_drivers.set_unique_driver(PARK_ID, DRIVER_ID, udid)
    request_data = utils.prepare_rq(PATH, PARK_ID, DRIVER_ID)
    request_data['json'] = {'seen_rewards': seen_rewards}

    response = await taxi_achievements.post(**request_data)
    assert response.status_code == 200

    cursor = pgsql['achievements_pg'].cursor()
    cursor.execute(
        """
        SELECT
            reward_code
        FROM achievements_pg.driver_rewards
        WHERE
            udid=%(udid)s
            AND seen_at = %(seen_at)s
            AND updated_at = %(updated_at)s
        ;
        """,
        {
            'udid': udid,
            'seen_at': '2020-01-01T12:00:00+0000',
            'updated_at': '2020-01-01T12:00:00+0000',
        },
    )
    marked_seen_rewards = {item[0] for item in cursor.fetchall()}
    assert marked_seen_rewards == expect_marked_seen


def make_seen_response(expect_state):
    response = copy.deepcopy(SEEN_RESPONSE_TEMPLATE)
    response['rewards'][0]['state'] = expect_state
    return response


@pytest.mark.parametrize(
    'udid, seen_rewards, expect_code, expect_response',
    [
        (None, [], 404, None),
        ('udid3', [], 200, make_seen_response('unlocked-new')),
        (
            'udid3',
            [{'code': 'express', 'level': 1}],
            200,
            make_seen_response('unlocked'),
        ),
        ('udid4', [], 200, {'rewards': [], 'category_ordering': []}),
    ],
)
@pytest.mark.pgsql('achievements_pg', files=['achievements.sql'])
async def test_driver_reward_seen_with_list(
        taxi_achievements,
        unique_drivers,
        driver_ui_profile_mock,
        udid,
        seen_rewards,
        expect_code,
        expect_response,
):
    unique_drivers.set_unique_driver(PARK_ID, DRIVER_ID, udid)
    request_data = utils.prepare_rq(PATH, PARK_ID, DRIVER_ID)
    request_data['json'] = {'seen_rewards': seen_rewards}

    response = await taxi_achievements.post(**request_data)
    assert response.status_code == expect_code
    if expect_code == 200:
        response_body = response.json()
        assert response_body == expect_response
