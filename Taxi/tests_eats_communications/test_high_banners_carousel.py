# pylint: disable=import-error
from eats_analytics import eats_analytics  # noqa: F401

from . import experiments
from . import utils


URL = 'http://yandex.ru'
APP_LINK = 'http://yandex.ru/mobile'
IMAGE_URL = 'beautiful_image.png'
REQ_EXP = 'request_exp'
EXTRA_EXP = 'extra_exp'
WIDTH = 'triple'


def make_feeds_banner(banner_id: int, experiment: str) -> dict:
    return {
        'banner_id': banner_id,
        'experiment': experiment,
        'recipients': {'type': 'info'},
        'url': URL,
        'appLink': APP_LINK,
        'priority': 10,
        'width': WIDTH,
        'images': [
            {'url': IMAGE_URL, 'theme': 'light', 'platform': 'web'},
            {'url': IMAGE_URL, 'theme': 'dark', 'platform': 'web'},
        ],
    }


def make_response_banner(banner_id: int) -> dict:
    context = eats_analytics.AnalyticsContext(item_id=str(banner_id))

    return {
        'id': str(banner_id),
        'url': URL,
        'app_link': APP_LINK,
        'images': [
            {'url': IMAGE_URL, 'theme': 'light', 'platform': 'web'},
            {'url': IMAGE_URL, 'theme': 'dark', 'platform': 'web'},
        ],
        'meta': {'analytics': eats_analytics.encode(context)},
    }


@experiments.feed(REQ_EXP)
@experiments.feed(EXTRA_EXP)
async def test_high_banners_carousel(taxi_eats_communications, mockserver):

    """
    Проверяем, что сервис корректно обрабатывает запрос
    блока карусели высоких баннеров
    и возвращает баннер сформированный из feeds
    """

    @mockserver.json_handler('/feeds/v1/fetch')
    def feeds(_):
        return utils.make_feeds_payload(
            make_feeds_banner(1, REQ_EXP),
            make_feeds_banner(2, REQ_EXP),
            make_feeds_banner(3, EXTRA_EXP),
        )

    expected_block = 'block_1'
    unexpected_block = 'block_2'
    block_type = 'high_banners_carousel'

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
                    'block_id': expected_block,
                    'type': block_type,
                    'experiments': [REQ_EXP],
                },
                {
                    'block_id': unexpected_block,
                    'type': block_type,
                    'experiments': [unexpected_block],
                },
            ],
        },
    )

    assert feeds.times_called == 1
    assert response.status_code == 200
    data = response.json()

    payload_banners = data['payload']['banners']

    # Проверяем что в основной выдаче
    # нет банеров с шириной
    assert not payload_banners

    payload_blocks = data['payload'].get('blocks')
    assert payload_blocks
    assert len(payload_blocks) == 1

    block = payload_blocks[0]

    assert block['block_id'] == expected_block
    assert block['type'] == block_type

    banners = block['payload']['banners']
    assert len(banners) == 2
    assert banners[0] == make_response_banner(2)
    assert banners[-1] == make_response_banner(1)
