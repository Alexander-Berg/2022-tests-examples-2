import copy

import pytest

EXP_NAME = 'my_publication'
SCREEN = 'tracking'
PLACE_BUSINESS_TYPE = 'shop'
EATER_ID = 12345

PREVIEW = {
    'text': {'color': 'bada55', 'content': 'feed preview text'},
    'title': {'color': 'bada55', 'content': 'feed preview title'},
    'backgrounds': [
        {'type': 'image', 'content': 'http://preview_image.png'},
        {'type': 'color', 'content': 'ffffff'},
    ],
}

PAGES = [
    {
        'text': {'color': '00691F', 'content': 'Воу воу воу!\nПалехче'},
        'title': {'color': 'FF5157', 'content': 'Фулскрин'},
        'widgets': {'pager': {}, 'close_button': {}},
        'backgrounds': [{'type': 'color', 'content': 'E7ECF2'}],
        'autonext': False,
    },
    {
        'text': {'color': '143264', 'content': 'Сам в шоке!!!'},
        'title': {'color': 'FF5157', 'content': 'И даже второй слайд есть!'},
        'widgets': {
            'pager': {},
            'close_button': {},
            'action_buttons': [
                {
                    'text': 'Текст кнопки',
                    'text_color': '#ffffff',
                    'color': '#bada55',
                    'deeplink': 'eda.yandex://my-deeplink',
                },
            ],
        },
        'backgrounds': [{'type': 'color', 'content': 'C4CDD6'}],
        'autonext': False,
    },
]


FEEDS_FETCH_RESPONSE = {
    'polling_delay': 60,
    'etag': '9fa57b4f16945a7eb9a1cfecd474849f',
    'feed': [
        {
            'feed_id': '333c69c8afe947ba887fd6404428b31c',
            'created': '2018-12-03T00:00:00+0000',
            'request_id': 'request_id',
            'last_status': {
                'status': 'published',
                'created': '2018-12-01T00:00:00+0000',
            },
            'payload': {
                'screens': ['screen1'],
                'priority': 1,
                'groups': ['a', 'b', 'c'],
                'is_tapable': True,
                'mark_read_after_tap': True,
                'preview': PREVIEW,
                'pages': PAGES,
            },
        },
    ],
    'has_more': False,
}


def preview_to_offer(preview: dict, shortcut_id: str) -> dict:
    result = copy.deepcopy(preview)
    result['subtitle'] = result.pop('text')
    result['shortcut_id'] = shortcut_id
    return result


@pytest.mark.experiments3(
    match={'predicate': {'init': {}, 'type': 'true'}, 'enabled': True},
    name=EXP_NAME,
    consumers=['eats-communications/stories'],
    clauses=[
        {
            'title': 'Match retail first order',
            'predicate': {
                'type': 'all_of',
                'init': {
                    'predicates': [
                        {
                            'init': {
                                'arg_name': 'screen',
                                'arg_type': 'string',
                                'value': SCREEN,
                            },
                            'type': 'eq',
                        },
                        {
                            'init': {
                                'arg_name': 'retail_orders_count',
                                'arg_type': 'int',
                                'value': 1,
                            },
                            'type': 'eq',
                        },
                        {
                            'init': {
                                'arg_name': 'version',
                                'arg_type': 'version',
                                'value': '5.27.1',
                            },
                            'type': 'gte',
                        },
                    ],
                },
            },
            'enabled': True,
            'value': {'enabled': True},
        },
    ],
)
@pytest.mark.parametrize('feed_by_id', [False, True])
async def test_stories(taxi_eats_communications, mockserver, feed_by_id):
    """
    Проверяет логику работы ручки /v1/stories
    1) Ходит в эксы по консьюмеру, передает в кварги
    контекст пользователя из запроса и статистику заказов в ретейле
    из order_stats
    2) Ходит в feeds за сторизами по полученным каналам
    и сервису
    3) Формирует ответ
    """

    @mockserver.json_handler('/eda-catalog/v1/shortlist')
    def _catalog(_):
        return mockserver.make_response(json={}, status=500)

    @mockserver.json_handler('/feeds/v1/fetch')
    def feeds(request):
        assert f'experiment:{EXP_NAME}' in request.json['channels']
        return FEEDS_FETCH_RESPONSE

    @mockserver.json_handler('/feeds/v1/fetch_by_id')
    def feeds_by_id(request):
        assert f'experiment:{EXP_NAME}' in request.json['channels']
        return FEEDS_FETCH_RESPONSE

    @mockserver.json_handler(
        '/eats-order-stats/internal/eats-order-stats/v1/orders',
    )
    def order_stats(request):
        assert request.json == {
            'identities': [{'type': 'eater_id', 'value': f'{EATER_ID}'}],
            'filters': [{'name': 'business_type', 'values': ['retail']}],
            'group_by': ['business_type'],
        }

        return {
            'data': [
                {
                    'identity': {'type': 'eater_id', 'value': f'{EATER_ID}'},
                    'counters': [
                        {
                            'properties': [
                                {'name': 'business_type', 'value': 'retail'},
                            ],
                            'value': 1,
                            'first_order_at': '2021-09-16T14:40:21+0000',
                            'last_order_at': '2021-09-17T11:42:57+0000',
                        },
                    ],
                },
            ],
        }

    request_body = {
        'application': {
            'device_id': 'fake_device_id',
            'platform': 'eda_ios_app',
            'screen_resolution': {'width': 1024, 'height': 768},
        },
        'location': {'latitude': 0.0, 'longitude': 0.0},
        'user_context': {
            'screen': SCREEN,
            'place_business_type': PLACE_BUSINESS_TYPE,
        },
    }

    if feed_by_id:
        request_body['feed_ids'] = ['333c69c8afe947ba887fd6404428b31c']

    response = await taxi_eats_communications.post(
        '/eats/v1/eats-communications/v1/stories',
        headers={
            'X-Eats-User': f'user_id={EATER_ID}',
            'X-App-Version': '5.27.1',
        },
        json=request_body,
    )

    assert order_stats.times_called == 1
    if feed_by_id:
        assert feeds_by_id.times_called == 1
    else:
        assert feeds.times_called == 1
    assert response.status_code == 200

    assert response.json() == {
        'stories': [
            {
                'offer': preview_to_offer(
                    PREVIEW, '333c69c8afe947ba887fd6404428b31c',
                ),
                'pages': PAGES,
            },
        ],
    }
