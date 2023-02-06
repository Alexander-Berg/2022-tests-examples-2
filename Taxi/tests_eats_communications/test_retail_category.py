import pytest

from . import experiments
from . import utils


PLACE_ID = 1
BRAND_ID = 2
PLACE_SLUG = 'place_1'
PATCHED_NAME = 'patched_banner'
INVALID_RETAIL_CATEGORY = 'invalid_retail_category'
RETAIL_CATEGORY = 'retail_category'
FEED = 'my_feed'


@experiments.feed('feed_1')
@pytest.mark.parametrize(
    'name,recipients,available_categories,expected',
    (
        pytest.param(
            PATCHED_NAME,
            {
                'type': 'restaurant',
                'places': [PLACE_ID],
                'menu_categories': [RETAIL_CATEGORY],
            },
            [],
            None,
            id='no available categories, filter banner',
        ),
        pytest.param(
            PATCHED_NAME,
            {
                'type': 'restaurant',
                'places': [PLACE_ID],
                'menu_categories': [RETAIL_CATEGORY],
            },
            [RETAIL_CATEGORY],
            {
                'url': (
                    utils.URL_ROOT + '/shop/'
                    f'{PLACE_SLUG}?category={RETAIL_CATEGORY}'
                ),
                'appLink': (
                    'eda.yandex://shop/'
                    f'{PLACE_SLUG}?category={RETAIL_CATEGORY}'
                ),
            },
            id=' available categories, rest targeting',
        ),
        pytest.param(
            PATCHED_NAME,
            {
                'type': 'brand',
                'brands': [BRAND_ID],
                'menu_categories': [RETAIL_CATEGORY],
            },
            [RETAIL_CATEGORY],
            {
                'url': (
                    utils.URL_ROOT + '/shop/'
                    f'{PLACE_SLUG}?category={RETAIL_CATEGORY}'
                ),
                'appLink': (
                    'eda.yandex://shop/'
                    f'{PLACE_SLUG}?category={RETAIL_CATEGORY}'
                ),
            },
            id='patch, available categories, brand targeting',
        ),
    ),
)
async def test_retail_category_from_feeds(
        taxi_eats_communications,
        mockserver,
        name,
        recipients,
        available_categories,
        expected,
):
    """
    Проверяем, что если у банера указана категория через сервис feeds
    происходит запрос в nomenclature, в ответе сервиса будет правильный диплинк
    Проверяем, что старый способ указывать категории через конфиг,
    не перетирает категории из feeds
    """

    @mockserver.json_handler('/eda-catalog/v1/_internal/banner-places')
    def _banner_places(request):
        return {
            'payload': [
                {
                    'id': PLACE_ID,
                    'slug': PLACE_SLUG,
                    'type': 'shop',
                    'brand': {
                        'id': BRAND_ID,
                        'slug': 'brand_1',
                        'placeSlug': PLACE_SLUG,
                    },
                },
            ],
        }

    @mockserver.json_handler('/eats-collections/internal/v1/collections')
    def _collections(request):
        return {}

    @mockserver.json_handler('/feeds/v1/fetch')
    def _feeds(request):
        return utils.make_feeds(
            {
                'payload': {
                    'banner_id': 1,
                    'experiment': 'feed_1',
                    'recipients': recipients,
                    'priority': 10,
                    'wide_and_short': [
                        {
                            'url': 'BANNER_FROM_FEEDS.png',
                            'theme': 'light',
                            'platform': 'web',
                        },
                    ],
                },
                'meta': {'name': name},
            },
        )

    @mockserver.json_handler('/eats-nomenclature/v1/places/categories')
    def _nomenclature(request):
        req = request.json

        assert len(req['places_categories']) == 1
        assert req['places_categories'][0]['place_id'] == PLACE_ID
        req_categories = req['places_categories'][0]['categories']
        assert sorted(req_categories) == sorted([RETAIL_CATEGORY])

        return {
            'places_categories': [
                {'place_id': PLACE_ID, 'categories': available_categories},
            ],
        }

    response = await taxi_eats_communications.post(
        '/eats-communications/v1/layout/banners',
        headers={
            'x-device-id': 'test_device',
            'x-app-version': '5.4.0',
            'x-platform': 'eda_ios_app',
        },
        json={'latitude': 0, 'longitude': 0},
    )

    assert response.status_code == 200
    banners = response.json()['payload']['banners']

    if expected is None:
        assert not banners
    else:
        payload = banners[0]['payload']
        for key, value in expected.items():
            assert payload[key] == value, key
