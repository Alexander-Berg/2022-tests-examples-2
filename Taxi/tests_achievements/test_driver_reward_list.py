import pytest

from tests_achievements import utils

PATH = '/driver/v1/achievements/v1/reward/list'
PARK_ID = 'driver_db_id1'
DRIVER_ID = 'driver_uuid1'


@pytest.mark.pgsql('achievements_pg', files=['achievements.sql'])
@pytest.mark.experiments3(filename='experiments3.json')
@pytest.mark.parametrize(
    'udid, expect_code, response_body',
    [
        (
            'udid1',
            200,
            {
                'rewards': [
                    {
                        'code': 'covid_hero',
                        'state': 'unlocked-new',
                        'level': 1,
                        'title': 'Ковидный герой',
                        'description': 'Ковидный герой - описание',
                        'unlocked_at': '2019-01-31T22:00:00+00:00',
                        'icons': {
                            'full': {
                                'type': 'lottie',
                                'url': (
                                    'http://icons/'
                                    'covid_hero_unlocked_full.json'
                                ),
                            },
                            'small': {
                                'type': 'png',
                                'url': (
                                    'http://icons/'
                                    'covid_hero_unlocked_small.png'
                                ),
                            },
                            'background': {
                                'type': 'png',
                                'url': (
                                    'http://icons/covid_hero_background.png'
                                ),
                            },
                        },
                        'sharing': {
                            'text': 'Ковидный герой - текст для шеринга',
                            'icon': {
                                'url': 'http://icons/covid_hero_sharing.png',
                                'type': 'png',
                            },
                        },
                    },
                    {
                        'code': 'express',
                        'state': 'unlocked-new',
                        'level': 1,
                        'category': 'Крутая категория',
                        'category_code': 'super_category',
                        'title': 'Народный курьер',
                        'description': 'Народный курьер - описание',
                        'unlocked_at': '2019-01-31T22:00:00+00:00',
                        'icons': {
                            'full': {
                                'type': 'lottie',
                                'url': (
                                    'http://icons/express_unlocked_full.json'
                                ),
                            },
                            'small': {
                                'type': 'png',
                                'url': (
                                    'http://icons/express_unlocked_small.png'
                                ),
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
                'category_ordering': ['super_category'],
            },
        ),
        # ------------------------------------------
        (
            'udid2',
            200,
            {
                'rewards': [
                    {
                        'code': 'express',
                        'state': 'unlocked-new',
                        'level': 1,
                        'category': 'Крутая категория',
                        'category_code': 'super_category',
                        'title': 'Народный курьер',
                        'description': 'Народный курьер - описание',
                        'unlocked_at': '2019-01-31T22:00:00+00:00',
                        'icons': {
                            'full': {
                                'type': 'lottie',
                                'url': (
                                    'http://icons/express_unlocked_full.json'
                                ),
                            },
                            'small': {
                                'type': 'png',
                                'url': (
                                    'http://icons/express_unlocked_small.png'
                                ),
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
                    {
                        'code': 'star',
                        'state': 'unlocked',
                        'level': 1,
                        'category': 'Другая категория',
                        'category_code': 'other_category',
                        'title': 'Звезданутый водитель',
                        'description': 'Звезданутый водитель - описание',
                        'unlocked_at': '2019-01-31T22:00:00+00:00',
                        'icons': {
                            'full': {
                                'type': 'lottie',
                                'url': 'http://icons/star_unlocked_full.json',
                            },
                            'small': {
                                'type': 'png',
                                'url': 'http://icons/star_unlocked_small.png',
                            },
                            'background': {
                                'type': 'lottie',
                                'url': 'http://icons/star_background.json',
                            },
                        },
                        'sharing': {
                            'text': 'Звезданутый водитель - текст для шеринга',
                            'icon': {
                                'url': 'http://icons/star_sharing.png',
                                'type': 'png',
                            },
                        },
                    },
                ],
                'category_ordering': ['super_category', 'other_category'],
            },
        ),
        (None, 404, None),
        ('udid3', 200, {'rewards': [], 'category_ordering': []}),
    ],
)
async def test_driver_reward_list_get(
        taxi_achievements,
        unique_drivers,
        driver_ui_profile_mock,
        udid,
        expect_code,
        response_body,
):
    if udid:
        unique_drivers.set_unique_driver(PARK_ID, DRIVER_ID, udid)

    request_data = utils.prepare_rq(PATH, PARK_ID, DRIVER_ID)
    response = await taxi_achievements.post(**request_data)
    assert response.status_code == expect_code
    if expect_code == 200:
        assert response.json() == response_body

        assert driver_ui_profile_mock.v1_mode_get.times_called == 1
