import pytest

from tests_achievements import utils

PATH = '/driver/v1/achievements/v1/reward/list'
PARK_ID = 'driver_db_id1'
DRIVER_ID = 'driver_uuid1'

DRIVER_UI_RESPONSE = {'display_mode': 'orders', 'display_profile': 'orders'}


def get_response_body(time_in_response):
    return {
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
                    'icon': {
                        'type': 'png',
                        'url': 'http://icons/300_sharing.png',
                    },
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
                'code': 'courier_orders',
                'level': 3000,
                'state': 'locked',
                'title': 'Турбо-курьер 3000',
                'description': 'Турбо-курьер 3000 - описание',
                'icons': {
                    'full': {
                        'type': 'lottie',
                        'url': 'http://icons/3000_locked.json',
                    },
                    'small': {
                        'type': 'png',
                        'url': 'http://icons/3000_locked.png',
                    },
                },
                'progress_for_locked': (
                    'Турбо-курьер - next_level: 3000, '
                    'current_progress: 1000, last_recount: ' + time_in_response
                ),
            },
        ],
    }


@pytest.mark.pgsql('achievements_pg', files=['achievements.sql'])
@pytest.mark.experiments3(filename='experiments3.json')
@pytest.mark.parametrize(
    ['time_in_response'],
    [
        pytest.param(
            'Сегодня 00:00',
            id='today',
            marks=[pytest.mark.now('2019-02-01T00:00:00+0300')],
        ),
        pytest.param(
            'Вчера 00:00',
            id='tommorow',
            marks=[pytest.mark.now('2019-02-02T00:00:00+0300')],
        ),
        pytest.param(
            '1 февраля 00:00',
            id='2 days later',
            marks=[pytest.mark.now('2019-02-03T00:00:00+0300')],
        ),
    ],
)
async def test_driver_progress_list_get(
        taxi_achievements,
        unique_drivers,
        driver_ui_profile_mock,
        driver_tags_mocks,
        time_in_response,
):
    unique_drivers.set_unique_driver(PARK_ID, DRIVER_ID, 'udid4')
    driver_ui_profile_mock.set_response(DRIVER_UI_RESPONSE)

    request_data = utils.prepare_rq(PATH, PARK_ID, DRIVER_ID)
    response = await taxi_achievements.post(**request_data)
    assert response.status_code == 200
    assert response.json() == get_response_body(time_in_response)
    assert driver_ui_profile_mock.v1_mode_get.times_called == 1
