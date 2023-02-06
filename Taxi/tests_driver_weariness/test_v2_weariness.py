import pytest

from tests_driver_weariness import const

WEARINESS = {
    'action': 'notify',
    'is_tired': False,
    'tired_at': '2022-05-16T17:02:00.000000Z',
    'placeholders_for_stories': {},
    'notifications': [
        {
            'content': {
                'show_home_button': True,
                'can_be_closed': True,
                'title': 'Фуллскрин тайтл',
                'text': 'Фуллскрин текст',
            },
            'start_at': '2022-05-16T13:02:00.000000Z',
            'stop_at': '2022-05-16T13:07:00.000000Z',
            'type': 'fullscreen',
            'repeat': False,
            'time_shift': 180,
        },
        {
            'content': {
                'show_home_button': True,
                'can_be_closed': True,
                'title': 'Оверлей тайтл',
                'text': 'Оверлей текст',
            },
            'start_at': '2022-05-16T16:32:00.000000Z',
            'stop_at': '2022-05-16T17:02:00.000000Z',
            'type': 'overlay',
            'repeat': False,
            'time_shift': 180,
        },
        {
            'content': {
                'show_home_button': False,
                'can_be_closed': False,
                'title': 'Файнал тайтл',
                'text': 'Файнал текст',
            },
            'start_at': '2022-05-16T17:02:00.000000Z',
            'stop_at': '2022-05-16T18:02:00.000000Z',
            'type': 'final',
            'repeat_interval': 180,
            'repeat': True,
        },
    ],
}
HEADERS = {
    'Accept-Language': 'ru',
    'X-YaTaxi-Park-Id': 'park1',
    'X-YaTaxi-Driver-Profile-Id': 'driverSS1',
    'X-Request-Application': 'taximeter',
    'X-Request-Application-Version': '8.80 (562)',
    'X-Request-Version-Type': '',
    'X-Request-Platform': 'android',
}


@pytest.mark.translations(
    taximeter_backend_messages={
        'driver_weariness_notification.fullscreen.title': {
            'ru': 'Фуллскрин тайтл',
        },
        'driver_weariness_notification.fullscreen.text': {
            'ru': 'Фуллскрин текст',
        },
        'driver_weariness_notification.overlay.title': {'ru': 'Оверлей тайтл'},
        'driver_weariness_notification.overlay.text': {'ru': 'Оверлей текст'},
        'driver_weariness_notification.final.title': {'ru': 'Файнал тайтл'},
        'driver_weariness_notification.final.text': {'ru': 'Файнал текст'},
    },
    taximeter_backend_driver_messages={
        'driver_weariness_hour_placeholder': {
            'ru': ['%(hours)s час', '%(hours)s часа', '%(hours)s часов'],
        },
        'driver_weariness_minutes_placeholder': {
            'ru': ['%(time)s минуту', '%(time)s минуты', '%(time)s минут'],
        },
    },
)
@pytest.mark.now('2022-05-16T00:00:00+0000')
@pytest.mark.unique_drivers(stream=const.DEFAULT_UNIQUE_DRIVERS)
async def test_weariness(taxi_driver_weariness):
    response = await taxi_driver_weariness.get(
        'v2/driver-weariness', headers=HEADERS,
    )
    assert response.status_code == 200
    parsed = response.json()
    assert 'weariness' in parsed
    assert parsed['weariness'] == WEARINESS


@pytest.mark.experiments3(filename='exp3_weariness_notifications.json')
@pytest.mark.translations(
    taximeter_backend_driver_messages={
        'driver_weariness_notification.base_pannel.title': {
            'ru': 'Про усталость',
        },
        'driver_weariness_notification.base_pannel.text': {
            'ru': 'Блокировка через %(time_to_block)s',
        },
        'driver_weariness_hour_placeholder': {
            'ru': ['%(hours)s час', '%(hours)s часа', '%(hours)s часов'],
        },
        'driver_weariness_minutes_placeholder': {
            'ru': ['%(time)s минуту', '%(time)s минуты', '%(time)s минут'],
        },
    },
)
@pytest.mark.now('2022-05-16T00:00:00+0000')
@pytest.mark.unique_drivers(stream=const.DEFAULT_UNIQUE_DRIVERS)
async def test_notifications_exp3(taxi_driver_weariness, load_json):
    response = await taxi_driver_weariness.get(
        'v2/driver-weariness', headers=HEADERS,
    )

    assert response.status_code == 200
    parsed = response.json()
    assert 'weariness' in parsed
    assert parsed['weariness'] == load_json('expected_response_v2.json')
