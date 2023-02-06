# pylint: disable=import-error
from eats_analytics import eats_analytics  # noqa: F401

from . import experiments
from . import utils


URL = 'http://yandex.ru'
APP_LINK = 'http://yandex.ru/mobile'
IMAGE_URL = 'beautiful_shortcut.png'
REQ_EXP = 'request_exp'
EXTRA_EXP = 'extra_exp'


def make_feeds_banner(
        banner_id: int, experiment: str, width: str = 'single',
) -> dict:
    return {
        'banner_id': banner_id,
        'experiment': experiment,
        'recipients': {'type': 'info'},
        'url': URL,
        'appLink': APP_LINK,
        'priority': 10,
        'width': width,
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


def make_response_banner(banner_id: int, width: str = 'single') -> dict:
    analytics_width: eats_analytics.BannerWidth = 0
    if width == 'single':
        analytics_width = eats_analytics.BannerWidth.SINGLE
    if width == 'double':
        analytics_width = eats_analytics.BannerWidth.DOUBLE
    if width == 'triple':
        analytics_width = eats_analytics.BannerWidth.TRIPLE

    context = eats_analytics.AnalyticsContext(
        item_id=str(banner_id), banner_width=analytics_width,
    )

    return {
        'id': str(banner_id),
        'url': URL,
        'app_link': APP_LINK,
        'images': [
            {'url': IMAGE_URL, 'theme': 'light', 'platform': 'web'},
            {'url': IMAGE_URL, 'theme': 'dark', 'platform': 'web'},
        ],
        'width': width,
        'meta': {'analytics': eats_analytics.encode(context)},
    }


@experiments.feed(REQ_EXP)
@experiments.feed(EXTRA_EXP)
async def test_banners_carousel(taxi_eats_communications, mockserver):

    """
    Проверяем, что сервис корректно обрабатывает запрос
    блока карусели баннеров
    и возвращает баннер сформированный из feeds
    """

    @mockserver.json_handler('/feeds/v1/fetch')
    def feeds(_):
        return utils.make_feeds_payload(
            make_feeds_banner(1, REQ_EXP),
            make_feeds_banner(2, REQ_EXP, 'double'),
            make_feeds_banner(3, EXTRA_EXP),
        )

    expected_block = 'block_1'
    unexpected_block = 'block_2'
    block_type = 'banners_carousel'

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

    pages = block['payload']['pages']
    assert len(pages) == 1

    banners = pages[0]['banners']
    assert len(banners) == 2
    assert banners[0] == make_response_banner(2, 'double')
    assert banners[-1] == make_response_banner(1, 'single')


@experiments.feed('old_retail_users_banner')
async def test_mystical_banner(taxi_eats_communications, mockserver):
    @mockserver.json_handler('/feeds/v1/fetch')
    def feeds(request):
        if request.json['earlier_than'] == '2020-09-02T13:34:37.97935+00:00':
            return {
                'etag': 'etag',
                'feed': [
                    {
                        'feed_id': 'feed_2',
                        'created': '2020-09-01T13:34:37.97935+0000',
                        'request_id': 'request_id',
                        'payload': make_feeds_banner(
                            2, 'old_retail_users_banner',
                        ),
                    },
                ],
                'polling_delay': 1,
                'has_more': False,
            }
        return {
            'etag': 'etag',
            'feed': [
                {
                    'feed_id': 'feed_1',
                    'created': '2020-09-02T13:34:37.97935+0000',
                    'request_id': 'request_id',
                    'payload': make_feeds_banner(1, 'old_retail_users_banner'),
                },
            ],
            'polling_delay': 1,
            'has_more': True,
        }

    response = await taxi_eats_communications.post(
        '/eats-communications/v1/layout/banners',
        headers={
            'x-device-id': 'test_device',
            'x-app-version': '5.4.0',
            'x-platform': 'eda_ios_app',
        },
        json={
            'blocks': [
                {
                    'block_id': 'test_block',
                    'experiments': [
                        'old_retail_users_banner',
                        'new_retail_banner_carousel',
                        'new_retail_users_banner',
                    ],
                    'type': 'banners_carousel',
                },
            ],
            'latitude': 55.750028,
            'longitude': 37.534406,
        },
    )

    assert feeds.times_called == 2
    assert response.status_code == 200
    data = response.json()

    assert len(data['payload']['blocks']) == 1

    block = data['payload']['blocks'][0]

    assert block['block_id'] == 'test_block'
    assert len(block['payload']['pages']) == 1
    assert len(block['payload']['pages'][0]['banners']) == 2
