import pytest

from . import configs
from . import utils


@configs.keep_empty_layout()
@pytest.mark.layout(
    autouse=True,
    slug='popup_layout',
    widgets=[
        utils.Widget(
            name='popup_banner',
            type='popup_banner',
            meta={
                'experiments': ['hello'],
                'size': {'width': 102, 'height': 201},
            },
        ),
    ],
)
async def test_popup_banner(taxi_eats_layout_constructor, mockserver):
    block_id = '1_popup_banner'
    block_type = 'popup_banner'
    popup_payload = {
        'id': '1',
        'url': 'http://noeda.yandex.net',
        'app_link': 'edayandex://page',
        'image': {
            'picture': {
                'light': {'url': 'image_light'},
                'dark': {'url': 'image_dark'},
            },
            'dimensions': {'width': 102, 'height': 201},
        },
        'meta': {'analytics': ''},
    }

    @mockserver.json_handler(
        '/eats-communications/eats-communications/v1/layout/banners',
    )
    def eats_comminications(request):
        blocks = request.json['blocks']
        assert len(blocks) == 1
        assert blocks[0] == {
            'block_id': block_id,
            'type': block_type,
            'experiments': ['hello'],
            'parameters': {
                'type': block_type,
                'dimensions': {'width': 102, 'height': 201},
            },
        }

        return {
            'payload': {
                'banners': [],
                'header_notes': [],
                'blocks': [
                    {
                        'block_id': block_id,
                        'type': block_type,
                        'payload': {
                            'block_type': block_type,
                            'banner': popup_payload,
                        },
                    },
                ],
            },
        }

    response = await taxi_eats_layout_constructor.post(
        'eats/v1/layout-constructor/v1/layout',
        headers={
            'x-device-id': 'dev_id',
            'x-platform': 'ios_app',
            'x-app-version': '12.11.12',
            'cookie': '{}',
            'X-Eats-User': 'user_id=12345',
            'x-request-application': 'application=1.1.0',
            'x-request-language': 'enUS',
            'Content-Type': 'application/json',
        },
        json={'location': {'latitude': 55.750028, 'longitude': 37.534397}},
    )

    assert eats_comminications.times_called == 1
    assert response.status_code == 200

    data = response.json()
    assert data['data']['popup_banner']['payload'] == popup_payload
    assert data['layout'] == [
        {'id': '1_popup_banner', 'payload': {}, 'type': 'popup_banner'},
    ]


@configs.keep_empty_layout()
@pytest.mark.layout(
    autouse=True,
    slug='popup_layout',
    widgets=[
        utils.Widget(
            name='popup_banner_1',
            type='popup_banner',
            meta={'experiments': ['hello'], 'size': {'width': 1, 'height': 1}},
        ),
        utils.Widget(
            name='popup_banner_2',
            type='popup_banner',
            meta={'experiments': ['hello'], 'size': {'width': 2, 'height': 2}},
        ),
    ],
)
async def test_popup_multiple_banner(taxi_eats_layout_constructor, mockserver):
    """
    Проверяет, что в случае если в лейауте несколько popup_banner виджетов
    то в коммункиации передается только один.
    NOTE(nk2ge5k): из-за того что блоки хранятся в unordered_map будет
    выбран произвольный виджет.
    """

    @mockserver.json_handler(
        '/eats-communications/eats-communications/v1/layout/banners',
    )
    def eats_comminications(request):
        blocks = request.json['blocks']
        assert len(blocks) == 1

        return {'payload': {'banners': [], 'header_notes': [], 'blocks': []}}

    response = await taxi_eats_layout_constructor.post(
        'eats/v1/layout-constructor/v1/layout',
        headers={
            'x-device-id': 'dev_id',
            'x-platform': 'ios_app',
            'x-app-version': '12.11.12',
            'cookie': '{}',
            'X-Eats-User': 'user_id=12345',
            'x-request-application': 'application=1.1.0',
            'x-request-language': 'enUS',
            'Content-Type': 'application/json',
        },
        json={'location': {'latitude': 55.750028, 'longitude': 37.534397}},
    )

    assert eats_comminications.times_called == 1
    assert response.status_code == 200
