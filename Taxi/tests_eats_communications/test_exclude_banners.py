import pytest

from testsuite.utils import matching

from . import experiments
from . import utils

RESPONSE_DEFAULT = [
    {
        'id': 2,
        'kind': 'place',
        'formats': ['wide_and_short'],
        'place_id': 2,
        'payload': {
            'id': 2,
            'kind': 'restaurant',
            'url': utils.URL_ROOT + '/restaurant/place_2',
            'appLink': 'eda.yandex://restaurant/place_2',
            'payload': {'badge': {}},
            'images': [],
            'shortcuts': [],
            'wide_and_short': [
                {
                    'url': 'beautiful_pic.png',
                    'theme': 'light',
                    'platform': 'web',
                },
            ],
            'meta': {'analytics': matching.AnyString()},
        },
    },
    {
        'id': 1,
        'kind': 'place',
        'formats': ['wide_and_short'],
        'place_id': 1,
        'payload': {
            'id': 1,
            'kind': 'restaurant',
            'url': utils.URL_ROOT + '/restaurant/place_1',
            'appLink': 'eda.yandex://restaurant/place_1',
            'payload': {'badge': {}},
            'images': [],
            'shortcuts': [],
            'wide_and_short': [
                {
                    'url': 'beautiful_pic.png',
                    'theme': 'light',
                    'platform': 'web',
                },
            ],
            'meta': {'analytics': matching.AnyString()},
        },
    },
]

RESPONSE_EXCLUDED = [
    {
        'id': 1,
        'kind': 'place',
        'formats': ['wide_and_short'],
        'place_id': 1,
        'payload': {
            'id': 1,
            'kind': 'restaurant',
            'url': utils.URL_ROOT + '/restaurant/place_1',
            'appLink': 'eda.yandex://restaurant/place_1',
            'payload': {'badge': {}},
            'images': [],
            'shortcuts': [],
            'wide_and_short': [
                {
                    'url': 'beautiful_pic.png',
                    'theme': 'light',
                    'platform': 'web',
                },
            ],
            'meta': {'analytics': matching.AnyString()},
        },
    },
]

RETAIL_NOTE = {
    'type': 'shop_free_delivery',
    'payload': {
        'icon': {
            'color': [{'theme': 'dark', 'value': '#BADA55'}],
            'uri': 'htttp://all-icons.com',
        },
        'text': {
            'color': [{'theme': 'light', 'value': '#000000'}],
            'text': 'Free retail',
        },
    },
}

EATS_NOTE = {
    'type': 'eats_free_delivery',
    'payload': {
        'icon': {
            'color': [{'theme': 'light', 'value': '#BADA55'}],
            'uri': 'htttp://all-icons.com',
        },
        'text': {
            'color': [{'theme': 'light', 'value': '#000010'}],
            'text': 'Free fooood!',
        },
    },
}

BANNER_PLACES = {
    'payload': [
        {
            'id': 1,
            'slug': 'place_1',
            'type': 'restaurant',
            'brand': {'id': 1, 'slug': 'brand_1', 'placeSlug': 'place_1'},
        },
        {
            'id': 2,
            'slug': 'place_2',
            'type': 'restaurant',
            'brand': {'id': 2, 'slug': 'brand_2', 'placeSlug': 'place_2'},
        },
    ],
}

COMMUNICATIONS = {
    'banners': [
        {
            'id': 1,
            'type': 'place',
            'place_id': 1,
            'priority': 10,
            'payload': {
                'pages': [
                    {
                        'wide': [
                            {
                                'url': 'beautiful_pic.png',
                                'theme': 'light',
                                'platform': 'web',
                            },
                        ],
                    },
                ],
            },
        },
        {
            'id': 2,
            'type': 'place',
            'place_id': 2,
            'priority': 10,
            'payload': {
                'pages': [
                    {
                        'wide': [
                            {
                                'url': 'beautiful_pic.png',
                                'theme': 'light',
                                'platform': 'web',
                            },
                        ],
                    },
                ],
            },
        },
    ],
}


@pytest.mark.parametrize(
    'expected_response',
    [
        pytest.param(RESPONSE_DEFAULT, id='no filter'),
        pytest.param(
            RESPONSE_EXCLUDED,
            marks=experiments.filter_banners([2]),
            id='filter',
        ),
    ],
)
@pytest.mark.eats_regions_cache(
    [
        {
            'id': 1,
            'name': 'Moscow',
            'slug': 'moscow',
            'genitive': '',
            'isAvailable': True,
            'isDefault': True,
            'bbox': [35.918658, 54.805858, 39.133684, 56.473673],
            'center': [37.642806, 55.724266],
            'timezone': 'Europe/Moscow',
            'sort': 1,
            'yandexRegionIds': [213, 216],
            'country': {'id': 35, 'code': 'RU', 'name': 'Русь'},
        },
    ],
)
async def test_exclude_banner(
        taxi_eats_communications, mockserver, expected_response,
):
    @mockserver.json_handler('/eda-delivery-price/v1/user-promo')
    def eda_delivery_time(request):
        return {}

    @mockserver.json_handler('/eda-catalog/v1/_internal/banner-places')
    def _banner_places(request):
        return BANNER_PLACES

    @mockserver.json_handler('/eats-collections/internal/v1/collections')
    def _collections(request):
        return {}

    @mockserver.json_handler(
        '/inapp-communications/inapp-communications/v1/eda-communications',
    )
    def _communications(request):
        return COMMUNICATIONS

    response = await taxi_eats_communications.post(
        '/eats-communications/v1/layout/banners',
        headers={
            'x-device-id': 'test_device',
            'x-app-version': '5.4.0',
            'x-platform': 'eda_ios_app',
        },
        json={'latitude': 55.752344, 'longitude': 37.541332},
    )

    assert eda_delivery_time.times_called == 1

    assert response.status_code == 200
    data = response.json()

    assert data['payload']['banners'] == expected_response
