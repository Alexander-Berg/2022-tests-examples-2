# pylint: disable=import-error
from eats_analytics import eats_analytics  # noqa: F401

from . import experiments
from . import utils

URL = 'http://yandex.ru'
APP_LINK = 'http://yandex.ru/mobile'
IMAGE_URL = 'beautiful_image.png'


def make_popup(
        banner_id, experiment: str, priority: int, popup_only: bool = False,
) -> dict:
    images = (
        []
        if popup_only
        else [
            {'url': IMAGE_URL, 'theme': 'light', 'platform': 'web'},
            {'url': IMAGE_URL, 'theme': 'dark', 'platform': 'web'},
        ]
    )

    return {
        'banner_id': banner_id,
        'experiment': experiment,
        'recipients': {'type': 'info'},
        'url': URL,
        'appLink': APP_LINK,
        'priority': priority,
        'popup': [
            {
                'url': 'popup_image_light',
                'theme': 'light',
                'platform': 'mobile',
            },
            {'url': 'popup_image_dark', 'theme': 'dark', 'platform': 'mobile'},
            {
                'url': 'popup_image_light_web',
                'theme': 'light',
                'platform': 'web',
            },
            {
                'url': 'popup_image_dark_web',
                'theme': 'dark',
                'platform': 'web',
            },
        ],
        'images': images,
        'wide_and_short': images,
        'shortcuts': images,
    }


def make_regular_banner(banner_id: int, experiment: str) -> dict:
    return {
        'banner_id': banner_id,
        'experiment': experiment,
        'recipients': {'type': 'info'},
        'url': URL,
        'appLink': APP_LINK,
        'priority': 10000,
        'images': [
            {'url': IMAGE_URL, 'theme': 'light', 'platform': 'web'},
            {'url': IMAGE_URL, 'theme': 'dark', 'platform': 'web'},
        ],
        'wide_and_short': [
            {'url': IMAGE_URL, 'theme': 'light', 'platform': 'web'},
            {'url': IMAGE_URL, 'theme': 'dark', 'platform': 'web'},
        ],
        'shortcuts': [
            {'url': IMAGE_URL, 'theme': 'light', 'platform': 'web'},
            {'url': IMAGE_URL, 'theme': 'dark', 'platform': 'web'},
        ],
    }


EXPERIMENT_ONE = 'experiment_one'
EXPERIMENT_TWO = 'experiment_two'
EXPERIMENT_REGULAR_BANNER = 'experiment_regular'


@experiments.feed(EXPERIMENT_ONE)
@experiments.feed(EXPERIMENT_TWO)
@experiments.feed(EXPERIMENT_REGULAR_BANNER)
async def test_popup_banner(taxi_eats_communications, mockserver):
    """
    Проверяем, что сервис корректно обрабатывает запрос
    блока баннера спецразмещения и возвращает баннер сформированный из feeds
    """

    @mockserver.json_handler('/feeds/v1/fetch')
    def feeds(_):
        return utils.make_feeds_payload(
            make_regular_banner(1, EXPERIMENT_REGULAR_BANNER),
            make_regular_banner(2, EXPERIMENT_REGULAR_BANNER),
            make_popup(3, EXPERIMENT_ONE, 100),
            make_popup(4, EXPERIMENT_ONE, 100),
            make_popup(5, EXPERIMENT_TWO, 50),
            make_popup(6, EXPERIMENT_TWO, 99, True),
        )

    response = await taxi_eats_communications.post(
        '/eats-communications/v1/layout/banners',
        headers={
            'x-device-id': 'test_device',
            'x-app-version': '5.4.0',
            'x-platform': 'eda_ios_app',
        },
        json={
            'latitude': 0,
            'longitude': 0,
            'blocks': [
                {
                    'block_id': 'popup_1',
                    'type': 'popup_banner',
                    'experiments': [
                        EXPERIMENT_REGULAR_BANNER,
                        EXPERIMENT_ONE,
                        EXPERIMENT_TWO,
                    ],
                },
            ],
        },
    )

    assert feeds.times_called == 1
    assert response.status_code == 200
    data = response.json()

    assert len(data['payload']['banners']) == 4
    for banner in data['payload']['banners']:
        assert banner['id'] != 6 and banner['id'] != 4

    blocks = data['payload']['blocks']
    assert len(blocks) == 1

    context = eats_analytics.AnalyticsContext(item_id='4')

    assert blocks[0] == {
        'block_id': 'popup_1',
        'type': 'popup_banner',
        'payload': {
            'block_type': 'popup_banner',
            'banner': {
                'id': '4',
                'app_link': APP_LINK,
                'url': URL,
                'image': {
                    'dimensions': {'width': 96, 'height': 96},
                    'picture': {
                        'light': {'url': 'popup_image_light'},
                        'dark': {'url': 'popup_image_dark'},
                    },
                },
                'meta': {'analytics': eats_analytics.encode(context)},
            },
        },
    }
