import pytest

from testsuite.utils import matching

from . import configs
from . import utils

CATALOG_FOR_LC_PATH = '/eats-catalog/internal/v1/catalog-for-layout'

ULTIMA_LAYOUT = pytest.mark.layout(
    autouse=True,
    slug='ultima',
    widgets=[
        utils.Widget(
            name='ultima',
            type='ultima_places_list',
            meta={'place_filter_type': 'open'},
            payload={},
            payload_schema={},
        ),
    ],
)

ADS_URLS = {
    'view_url': 'https://yandex.ru/view',
    'click_url': 'https://yandex.ru/count',
}

ADS_TEXT = 'Реkлама'


def build_catalog_response(
        block_id, block_type, places_count, with_ads: bool = False,
):
    places = []
    for i in range(places_count):
        availability_data = {'is_available': True}
        payload: dict = {
            'name': f'Ресторан Name {i}',
            'slug': f'place_slug_{i}',
            'availability': availability_data,
            'brand': {
                'name': f'brand_name_{i}',
                'slug': f'brand_slug_{i}',
                'business': 'restaurant',
            },
            'data': {
                'features': {'delivery': {'text': '1000 МИН'}},
                'meta': [],
            },
        }

        if with_ads:
            payload['data']['features']['advertisement'] = ADS_URLS
            payload['data']['meta'].append(
                {
                    'id': 'ca99959abe9e49099c89b5b3f6851093',
                    'type': 'advertisements',
                    'payload': {
                        'text': {
                            'color': [
                                {'theme': 'light', 'value': '#999588'},
                                {'theme': 'dark', 'value': '#999588'},
                            ],
                            'text': ADS_TEXT,
                        },
                        'background': [
                            {'theme': 'light', 'value': '#EBE7DA'},
                            {'theme': 'dark', 'value': '#56544D'},
                        ],
                    },
                },
            )

        place_data = {
            'payload': payload,
            'meta': {'place_id': i, 'brand_id': i},
        }
        places.append(place_data)

    return {
        'blocks': [{'id': block_id, 'type': block_type, 'list': places}],
        'filters': {},
        'sort': {},
        'timepicker': [],
    }


@ULTIMA_LAYOUT
@configs.ultima_places(
    {
        'place_slug_0': {
            'image': 'http://place_slug_0',
            'menu_image': {
                'light': 'http://place_slug_0/menu/light',
                'dark': 'http://place_slug_0/menu/dark',
            },
            'carousel_settings': {
                'items': [
                    {
                        'image': 'http://carousel',
                        'link': {
                            'app': 'eda.yandex://carousel/link',
                            'web': 'http://carousel/link',
                        },
                    },
                ],
            },
            'info': {
                'image': 'http://info/face',
                'title': 'info title',
                'description': 'info description',
                'deeplink': {
                    'app': 'eda.yandex://info/link',
                    'web': 'http://info/link',
                },
            },
        },
        'place_slug_1': {
            'image': 'http://place_slug_1',
            'carousel_settings': {'items': []},
        },
    },
)
async def test_ultima_places_list(layout_constructor, mockserver):
    @mockserver.json_handler(CATALOG_FOR_LC_PATH)
    def catalog(request):
        utils.assert_request_block(
            request.json,
            'ultima_open',
            {
                'id': 'ultima_open',
                'type': 'open',
                'disable_filters': False,
                'round_eta_to_hours': False,
                'condition': {
                    'predicates': [
                        {'init': {'arg_name': 'is_ultima'}, 'type': 'bool'},
                    ],
                    'type': 'all_of',
                },
            },
        )
        return build_catalog_response('ultima_open', 'open', 3)

    response = await layout_constructor.post()

    assert response.status_code == 200
    assert catalog.times_called == 1

    data = response.json()

    assert 'ultima_places_list' in data['data']
    assert len(data['data']['ultima_places_list']) == 1
    assert data['layout'] == [
        {
            'id': '1_ultima_places_list',
            'payload': {},
            'type': 'ultima_places_list',
        },
    ]

    widget_data = data['data']['ultima_places_list'][0]
    assert widget_data == {
        'id': '1_ultima_places_list',
        'payload': {
            'header': {
                'image': {
                    'dark': 'http://header/dark',
                    'light': 'http://header/light',
                },
                'button': {
                    'background_color': {
                        'dark': '#RETEXT',
                        'light': '#RETEXT',
                    },
                    'deeplink': {
                        'app': 'eda.yandex://carousel/link',
                        'web': 'http://carousel/link',
                    },
                    'icon': {
                        'light': 'http://eda.yandex.ru/light',
                        'dark': 'http://eda.yandex.ru/dark',
                    },
                },
            },
            'places': [
                {
                    'analytics': matching.any_string,
                    'availability': {'is_available': True},
                    'brand': {
                        'business': 'restaurant',
                        'name': 'brand_name_0',
                        'slug': 'brand_slug_0',
                    },
                    'data': {
                        'features': {
                            'carousel': {
                                'elements': [
                                    {
                                        'image': 'http://carousel',
                                        'link': {
                                            'app': (
                                                'eda.yandex://carousel/link'
                                            ),
                                            'web': 'http://carousel/link',
                                        },
                                    },
                                ],
                            },
                            'delivery': {
                                'background_color': {
                                    'dark': '#DEBACK',
                                    'light': '#DEBACK',
                                },
                                'text': {
                                    'color': {
                                        'dark': '#DETEXT',
                                        'light': '#DETEXT',
                                    },
                                    'value': '1000 МИН',
                                },
                            },
                            'info': {
                                'deeplink': {
                                    'app': 'eda.yandex://info/link',
                                    'web': 'http://info/link',
                                },
                                'description': {
                                    'color': {
                                        'dark': '#IDESCR',
                                        'light': '#IDESCR',
                                    },
                                    'value': 'info ' 'description',
                                },
                                'image': 'http://info/face',
                                'title': {
                                    'color': {
                                        'dark': '#ITITLE',
                                        'light': '#ITITLE',
                                    },
                                    'value': 'info ' 'title',
                                },
                            },
                        },
                    },
                    'media': {
                        'additional_image': {
                            'dark': 'http://place_slug_0/menu/dark',
                            'light': 'http://place_slug_0/menu/light',
                        },
                        'image': 'http://place_slug_0',
                    },
                    'name': {
                        'color': {'dark': '#TTITLE', 'light': '#TTITLE'},
                        'value': 'РЕСТОРАН NAME 0',
                    },
                    'slug': 'place_slug_0',
                },
                {
                    'analytics': matching.any_string,
                    'availability': {'is_available': True},
                    'brand': {
                        'business': 'restaurant',
                        'name': 'brand_name_1',
                        'slug': 'brand_slug_1',
                    },
                    'data': {
                        'features': {
                            'delivery': {
                                'background_color': {
                                    'dark': '#DEBACK',
                                    'light': '#DEBACK',
                                },
                                'text': {
                                    'color': {
                                        'dark': '#DETEXT',
                                        'light': '#DETEXT',
                                    },
                                    'value': '1000 МИН',
                                },
                            },
                        },
                    },
                    'media': {'image': 'http://place_slug_1'},
                    'name': {
                        'color': {'dark': '#TTITLE', 'light': '#TTITLE'},
                        'value': 'РЕСТОРАН NAME 1',
                    },
                    'slug': 'place_slug_1',
                },
            ],
        },
        'template_name': 'ultima_template',
    }


@ULTIMA_LAYOUT
@configs.ultima_places(
    {
        'place_slug_0': {
            'image': 'http://place_slug_0',
            'menu_image': {
                'light': 'http://place_slug_0/menu/light',
                'dark': 'http://place_slug_0/menu/dark',
            },
            'carousel_settings': {'items': []},
            'info': {
                'image': '',
                'title': 'this wont show',
                'description': 'this wont show either',
                'deeplink': {
                    'app': 'http://does-not.matter',
                    'web': 'http://does-not.metter',
                },
            },
        },
    },
)
async def test_ultima_info_empty_image(layout_constructor, mockserver):
    """
    Проверяет, что в случае, если в конфиге, в качестве ссылки на изображение
    info фичи, указана пустая строка, то info фича не вернется в ответе
    """

    @mockserver.json_handler(CATALOG_FOR_LC_PATH)
    def catalog(request):
        return build_catalog_response('ultima_open', 'open', 1)

    response = await layout_constructor.post()

    assert response.status_code == 200
    assert catalog.times_called == 1

    data = response.json()

    assert 'ultima_places_list' in data['data']
    assert len(data['data']['ultima_places_list']) == 1

    widget_data = data['data']['ultima_places_list'][0]

    places = widget_data['payload']['places']
    assert len(places) == 1

    assert 'info' not in places[0]['data']['features']


@ULTIMA_LAYOUT
@configs.ultima_places(
    {
        'place_slug_0': {
            'image': 'http://place_slug_0',
            'carousel_settings': {'items': []},
        },
        'place_slug_1': {
            'image': 'http://place_slug_1',
            'carousel_settings': {'items': []},
        },
    },
)
async def test_ads_in_ultima(layout_constructor, mockserver):
    """
    Проверяет, что если каталог присылыет рекламную информацию среди данных
    заведения, то она будет возвращена, в ответе ручки, для сниппета Ультимы.
    """

    @mockserver.json_handler(CATALOG_FOR_LC_PATH)
    def catalog(request):
        return build_catalog_response('ultima_open', 'open', 2, with_ads=True)

    response = await layout_constructor.post()

    assert response.status_code == 200
    assert catalog.times_called == 1

    data = response.json()

    assert 'ultima_places_list' in data['data']

    widget_data = data['data']['ultima_places_list'][0]

    places = widget_data['payload']['places']
    assert len(places) == 2

    for place in places:
        assert place['advertisement'] == ADS_URLS
        assert place['data']['features']['ads'] == {
            'background_color': {'dark': '#ADBACK', 'light': '#ADBACK'},
            'text': {
                'color': {'dark': '#ADTEXT', 'light': '#ADTEXT'},
                'value': ADS_TEXT.upper(),
            },
        }
