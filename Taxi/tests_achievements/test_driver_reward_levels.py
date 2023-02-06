import pytest

from tests_achievements import utils

PATH = '/driver/v1/achievements/v1/reward/list'
PARK_ID = 'driver_db_id1'
DRIVER_ID = 'driver_uuid1'

DRIVER_UI_RESPONSE = {'display_mode': 'orders', 'display_profile': 'orders'}

RESPONSE_UDID1 = {
    'category_ordering': [],
    'rewards': [
        {
            'code': 'driver_years',
            'level': 1,
            'state': 'unlocked-new',
            'unlocked_at': '2019-01-31T21:00:00+00:00',
            'title': 'Годовасик 1',
            'description': 'Годовасик 1 - описание',
            'sharing': {
                'text': 'Годовасик 1 - шеринг',
                'icon': {'type': 'png', 'url': 'http://icons/1_sharing.png'},
            },
            'icons': {
                'background': {'type': 'png', 'url': 'http://icons/1_bg.png'},
                'full': {
                    'type': 'lottie',
                    'url': 'http://icons/1_unlocked.json',
                },
                'small': {'type': 'png', 'url': 'http://icons/1_unlocked.png'},
            },
        },
        {
            'code': 'driver_years',
            'level': 2,
            'state': 'locked',
            'title': 'Годовасик 2',
            'description': 'Годовасик 2 (залочен) - описание',
            'icons': {
                'full': {'type': 'png', 'url': 'http://icons/2_locked.png'},
                'small': {'type': 'png', 'url': 'http://icons/2_locked.png'},
            },
        },
        {
            'code': 'express',
            'level': 1,
            'state': 'locked',
            'title': 'Народный курьер',
            'description': 'Народный курьер (залочен) - описание',
            'icons': {
                'full': {
                    'type': 'png',
                    'url': 'http://icons/express_locked_full.png',
                },
                'small': {
                    'type': 'png',
                    'url': 'http://icons/express_locked_small.png',
                },
            },
        },
    ],
}

RESPONSE_UDID2 = {
    'category_ordering': [],
    'rewards': [
        {
            'code': 'driver_years',
            'level': 1,
            'state': 'unlocked',
            'unlocked_at': '2019-01-31T21:00:00+00:00',
            'title': 'Годовасик 1',
            'description': 'Годовасик 1 - описание',
            'sharing': {
                'text': 'Годовасик 1 - шеринг',
                'icon': {'type': 'png', 'url': 'http://icons/1_sharing.png'},
            },
            'icons': {
                'background': {'type': 'png', 'url': 'http://icons/1_bg.png'},
                'full': {
                    'type': 'lottie',
                    'url': 'http://icons/1_unlocked.json',
                },
                'small': {'type': 'png', 'url': 'http://icons/1_unlocked.png'},
            },
        },
        {
            'code': 'driver_years',
            'level': 2,
            'state': 'locked',
            'title': 'Годовасик 2',
            'description': 'Годовасик 2 (залочен) - описание',
            'icons': {
                'full': {'type': 'png', 'url': 'http://icons/2_locked.png'},
                'small': {'type': 'png', 'url': 'http://icons/2_locked.png'},
            },
        },
        {
            'code': 'express',
            'level': 1,
            'state': 'unlocked-new',
            'unlocked_at': '2019-01-31T21:00:00+00:00',
            'title': 'Народный курьер',
            'description': 'Народный курьер - описание',
            'icons': {
                'background': {
                    'type': 'png',
                    'url': 'http://icons/express_background.png',
                },
                'full': {
                    'type': 'lottie',
                    'url': 'http://icons/express_unlocked_full.json',
                },
                'small': {
                    'type': 'png',
                    'url': 'http://icons/express_unlocked_small.png',
                },
            },
            'sharing': {
                'text': 'Народный курьер - текст для шеринга',
                'icon': {
                    'type': 'png',
                    'url': 'http://icons/express_sharing.png',
                },
            },
        },
    ],
}

RESPONSE_UDID3 = {
    'category_ordering': [],
    'rewards': [
        {
            'code': 'driver_years',
            'level': 1,
            'state': 'unlocked',
            'unlocked_at': '2019-01-31T21:00:00+00:00',
            'title': 'Годовасик 1',
            'description': 'Годовасик 1 - описание',
            'sharing': {
                'text': 'Годовасик 1 - шеринг',
                'icon': {'type': 'png', 'url': 'http://icons/1_sharing.png'},
            },
            'icons': {
                'background': {'type': 'png', 'url': 'http://icons/1_bg.png'},
                'full': {
                    'type': 'lottie',
                    'url': 'http://icons/1_unlocked.json',
                },
                'small': {'type': 'png', 'url': 'http://icons/1_unlocked.png'},
            },
        },
        {
            'code': 'driver_years',
            'level': 2,
            'state': 'unlocked-new',
            'unlocked_at': '2019-01-31T21:00:00+00:00',
            'title': 'Годовасик 2',
            'description': 'Годовасик 2 - описание',
            'sharing': {
                'text': 'Годовасик 2 - шеринг',
                'icon': {'type': 'png', 'url': 'http://icons/2_sharing.png'},
            },
            'icons': {
                'background': {'type': 'png', 'url': 'http://icons/2_bg.png'},
                'full': {
                    'type': 'lottie',
                    'url': 'http://icons/2_unlocked.json',
                },
                'small': {'type': 'png', 'url': 'http://icons/2_unlocked.png'},
            },
        },
        {
            'code': 'express',
            'level': 1,
            'state': 'locked',
            'title': 'Народный курьер',
            'description': 'Народный курьер (залочен) - описание',
            'icons': {
                'full': {
                    'type': 'png',
                    'url': 'http://icons/express_locked_full.png',
                },
                'small': {
                    'type': 'png',
                    'url': 'http://icons/express_locked_small.png',
                },
            },
        },
    ],
}

RESPONSE_UDID4 = {
    'category_ordering': [],
    'rewards': [
        {
            'code': 'courier_orders',
            'level': 300,
            'state': 'unlocked-new',
            'unlocked_at': '2019-01-31T21:00:00+00:00',
            'title': 'Турбо-курьер 300',
            'description': 'Турбо-курьер 300 - описание',
            'sharing': {
                'text': 'Турбо-курьер 300 - шеринг',
                'icon': {'type': 'png', 'url': 'http://icons/300_sharing.png'},
            },
            'icons': {
                'background': {
                    'type': 'png',
                    'url': 'http://icons/300_bg.png',
                },
                'full': {
                    'type': 'lottie',
                    'url': 'http://icons/300_unlocked.json',
                },
                'small': {
                    'type': 'png',
                    'url': 'http://icons/300_unlocked.png',
                },
            },
        },
        {
            'code': 'courier_orders',
            'level': 1000,
            'state': 'unlocked-new',
            'unlocked_at': '2019-01-31T21:00:00+00:00',
            'title': 'Турбо-курьер 1000',
            'description': 'Турбо-курьер 1000 - описание',
            'sharing': {
                'text': 'Турбо-курьер 1000 - шеринг',
                'icon': {
                    'type': 'png',
                    'url': 'http://icons/1000_sharing.png',
                },
            },
            'icons': {
                'background': {
                    'type': 'png',
                    'url': 'http://icons/1000_bg.png',
                },
                'full': {
                    'type': 'lottie',
                    'url': 'http://icons/1000_unlocked.json',
                },
                'small': {
                    'type': 'png',
                    'url': 'http://icons/1000_unlocked.png',
                },
            },
        },
        {
            'code': 'driver_years',
            'level': 1,
            'state': 'locked',
            'title': 'Годовасик 1',
            'description': 'Годовасик 1 (залочен) - описание',
            'icons': {
                'full': {'type': 'png', 'url': 'http://icons/1_locked.png'},
                'small': {'type': 'png', 'url': 'http://icons/1_locked.png'},
            },
        },
        {
            'code': 'express',
            'level': 1,
            'state': 'locked',
            'title': 'Народный курьер',
            'description': 'Народный курьер (залочен) - описание',
            'icons': {
                'full': {
                    'type': 'png',
                    'url': 'http://icons/express_locked_full.png',
                },
                'small': {
                    'type': 'png',
                    'url': 'http://icons/express_locked_small.png',
                },
            },
        },
    ],
}


@pytest.mark.pgsql('achievements_pg', files=['achievements.sql'])
@pytest.mark.experiments3(filename='experiments3.json')
@pytest.mark.parametrize(
    'udid, expect_code, response_body',
    [
        (None, 404, None),
        ('udid1', 200, RESPONSE_UDID1),
        ('udid2', 200, RESPONSE_UDID2),
        ('udid3', 200, RESPONSE_UDID3),
        ('udid4', 200, RESPONSE_UDID4),
    ],
)
async def test_driver_reward_list_get(
        taxi_achievements,
        unique_drivers,
        driver_ui_profile_mock,
        driver_tags_mocks,
        udid,
        expect_code,
        response_body,
):
    if udid:
        unique_drivers.set_unique_driver(PARK_ID, DRIVER_ID, udid)

    driver_ui_profile_mock.set_response(DRIVER_UI_RESPONSE)

    request_data = utils.prepare_rq(PATH, PARK_ID, DRIVER_ID)
    response = await taxi_achievements.post(**request_data)
    assert response.status_code == expect_code
    if expect_code == 200:
        assert response.json() == response_body
        assert driver_ui_profile_mock.v1_mode_get.times_called == 1
