from . import experiments
from . import utils


EATER_ID = 12345


@experiments.feed('my_feed')
async def test_show_strategy_once(taxi_eats_communications, mockserver):
    """
    Проверяем, что если коммуникация помечена как просмотренная
    и ее стратегия once,
    то она будет исключена из выдачи
    """

    @mockserver.json_handler('/eda-catalog/v1/_internal/banner-places')
    def _banner_places(request):
        return {}

    @mockserver.json_handler('/eats-collections/internal/v1/collections')
    def _collections(request):
        return {}

    @mockserver.json_handler('/feeds/v1/fetch')
    def feeds(request):
        assert f'user_id:{EATER_ID}' in request.json['channels']
        return utils.make_feeds(
            {
                'payload': {
                    'banner_id': 1,
                    'experiment': 'feed_1',
                    'recipients': {'type': 'info'},
                    'priority': 10,
                    'show_strategy': 'once',
                    'wide_and_short': [
                        {
                            'url': 'BANNER_FROM_FEEDS.png',
                            'theme': 'light',
                            'platform': 'web',
                        },
                    ],
                },
                'last_status': {
                    'created': '2020-09-02T13:34:37.97935+0000',
                    'status': 'viewed',
                },
            },
        )

    response = await taxi_eats_communications.post(
        '/eats-communications/v1/layout/banners',
        headers={
            'x-device-id': 'test_device',
            'x-app-version': '5.4.0',
            'x-platform': 'eda_ios_app',
            'x-eats-user': f'user_id={EATER_ID}',
        },
        json={'latitude': 0, 'longitude': 0},
    )

    assert feeds.times_called == 1
    assert response.status_code == 200
    banners = response.json()['payload']['banners']
    assert not banners


@experiments.feed('my_feed')
@experiments.feed('feed_2')
async def test_show_strategy_low_priority(
        taxi_eats_communications, mockserver,
):
    """
    Проверяем, что если коммуникация помечена как просмотренная
    и у нее стратегия low_priority, ее приоритет будет понижен
    """

    @mockserver.json_handler('/eda-catalog/v1/_internal/banner-places')
    def _banner_places(request):
        return {}

    @mockserver.json_handler('/eats-collections/internal/v1/collections')
    def _collections(request):
        return {}

    @mockserver.json_handler('/feeds/v1/fetch')
    def feeds(request):
        assert f'user_id:{EATER_ID}' in request.json['channels']
        return utils.make_feeds(
            {
                'payload': {
                    'banner_id': 1,
                    'experiment': 'my_feed',
                    'recipients': {'type': 'info'},
                    'priority': 10,
                    'show_strategy': 'low_priority',
                    'wide_and_short': [
                        {
                            'url': 'BANNER_FROM_FEEDS.png',
                            'theme': 'light',
                            'platform': 'web',
                        },
                    ],
                },
                'last_status': {
                    'created': '2020-09-02T13:34:37.97935+0000',
                    'status': 'viewed',
                },
            },
            {
                'payload': {
                    'banner_id': 2,
                    'experiment': 'feed_2',
                    'recipients': {'type': 'info'},
                    'priority': 5,
                    'show_strategy': 'always',
                    'wide_and_short': [
                        {
                            'url': 'BANNER_FROM_FEEDS.png',
                            'theme': 'light',
                            'platform': 'web',
                        },
                    ],
                },
                'last_status': {
                    'created': '2020-09-02T13:34:37.97935+0000',
                    'status': 'published',
                },
            },
        )

    response = await taxi_eats_communications.post(
        '/eats-communications/v1/layout/banners',
        headers={
            'x-device-id': 'test_device',
            'x-app-version': '5.4.0',
            'x-platform': 'eda_ios_app',
            'x-eats-user': f'user_id={EATER_ID}',
        },
        json={'latitude': 0, 'longitude': 0},
    )

    assert feeds.times_called == 1
    assert response.status_code == 200
    banners = response.json()['payload']['banners']
    ids = list(banner['id'] for banner in banners)
    # Банер 2 имеет меньший приоритет, чем 1,
    # но приоритет 1 был сброшен,
    # так как он имеет стратегию low_priority
    # и помечен как viewed
    assert ids == [2, 1]


@experiments.feed('my_feed')
async def test_non_requested_channels(taxi_eats_communications, mockserver):
    """
    Проверяем что если в ответе feed пришел банер с экспериментом
    который мы не запрашивали, он будет отфильтрован
    """

    @mockserver.json_handler('/eda-catalog/v1/_internal/banner-places')
    def _banner_places(request):
        return {}

    @mockserver.json_handler('/eats-collections/internal/v1/collections')
    def _collections(request):
        return {}

    @mockserver.json_handler('/feeds/v1/fetch')
    def feeds(request):
        assert f'experiment:feed_1' not in request.json['channels']
        return utils.make_feeds(
            {
                'payload': {
                    'banner_id': 1,
                    'experiment': 'feed_1',
                    'recipients': {'type': 'info'},
                    'priority': 10,
                    'show_strategy': 'once',
                    'wide_and_short': [
                        {
                            'url': 'BANNER_FROM_FEEDS.png',
                            'theme': 'light',
                            'platform': 'web',
                        },
                    ],
                },
                'last_status': {
                    'created': '2020-09-02T13:34:37.97935+0000',
                    'status': 'published',
                },
            },
        )

    response = await taxi_eats_communications.post(
        '/eats-communications/v1/layout/banners',
        headers={
            'x-device-id': 'test_device',
            'x-app-version': '5.4.0',
            'x-platform': 'eda_ios_app',
            'x-eats-user': f'user_id={EATER_ID}',
        },
        json={'latitude': 0, 'longitude': 0},
    )

    assert feeds.times_called == 1
    assert response.status_code == 200
    banners = response.json()['payload']['banners']
    assert not banners
