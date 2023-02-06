import copy
import typing

URL_ROOT = ''


class MatchingSet:
    def __init__(self, values: typing.List):
        self._set: typing.Set = set(values)

    def __repr__(self):
        return str(self._set)

    def __eq__(self, other):
        return self._set == set(other)


def make_feeds_payload(*args):
    result = {
        'etag': 'etag1',
        'feed': [],
        'polling_delay': 1,
        'has_more': False,
    }

    for payload in args:
        result['feed'].append(
            {
                'feed_id': 'feed_1',
                'created': '2020-09-02T13:34:37.97935+0000',
                'request_id': 'request_id',
                'payload': payload,
            },
        )

    return result


def make_feeds(*args):
    result = {
        'etag': 'etag1',
        'feed': [],
        'polling_delay': 1,
        'has_more': False,
    }

    for patch in args:
        result['feed'].append(
            {
                'feed_id': 'feed_1',
                'created': '2020-09-02T13:34:37.97935+0000',
                'request_id': 'request_id',
            },
        )
        result['feed'][-1].update(patch)

    return result


def make_eats_orders_stats_response(
        request,
        eater_id,
        brand_id,
        retail_orders_count,
        brand_orders_count,
        has_retail_orders_count=True,
):
    group_by = 'brand_id' if brand_id else 'business_type'
    assert request.json == {
        'identities': [{'type': 'eater_id', 'value': eater_id}],
        'filters': [{'name': 'business_type', 'values': ['retail']}],
        'group_by': [group_by],
    }
    if not has_retail_orders_count:
        counters = []
    elif brand_id:
        counters = [
            {
                'properties': [{'name': 'brand_id', 'value': brand_id}],
                'value': brand_orders_count,
                'first_order_at': '2021-09-16T14:40:21+0000',
                'last_order_at': '2021-09-17T11:42:57+0000',
            },
            {
                'properties': [
                    {'name': 'brand_id', 'value': 'other_brand_id'},
                ],
                'value': retail_orders_count - brand_orders_count,
                'first_order_at': '2021-09-16T14:40:21+0000',
                'last_order_at': '2021-09-17T11:42:57+0000',
            },
        ]
    else:
        counters = [
            {
                'properties': [{'name': 'business_type', 'value': 'retail'}],
                'value': retail_orders_count,
                'first_order_at': '2021-09-16T14:40:21+0000',
                'last_order_at': '2021-09-17T11:42:57+0000',
            },
        ]
    return {
        'data': [
            {
                'identity': {'type': 'eater_id', 'value': f'{eater_id}'},
                'counters': counters,
            },
        ],
    }


def assert_feeds_channels(request, exp_names, eater_id, device_id):
    channels = [f'experiment:{exp}' for exp in exp_names]
    if eater_id:
        channels.append(f'user_id:{eater_id}')
    if device_id:
        channels.append(f'device_id:{device_id}')
    assert set(channels) == set(request.json['channels'])


STORY_PREVIEW = {
    'text': {'color': 'bada55', 'content': 'feed preview text'},
    'title': {'color': 'bada55', 'content': 'feed preview title'},
    'backgrounds': [
        {'type': 'image', 'content': 'http://preview_image.png'},
        {'type': 'color', 'content': 'ffffff'},
    ],
}

STORY_PAGES = [
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


def make_feed_status(feed):
    status = feed.get('status', 'published')
    if status is None:
        return None

    return {'status': status, 'created': '2018-12-01T00:00:00+0000'}


def make_fetch_stories_response(feeds):
    response = {
        'polling_delay': 60,
        'etag': '9fa57b4f16945a7eb9a1cfecd474849f',
        'feed': [],
        'has_more': False,
    }
    for feed in feeds:
        payload = {
            'screens': ['screen1'],
            'priority': feed['priority'],
            'groups': ['a', 'b', 'c'],
            'is_tapable': True,
            'mark_read_after_tap': True,
            'preview': STORY_PREVIEW,
            'pages': STORY_PAGES,
        }
        if 'categories' in feed:
            payload['recipients'] = {
                'story_type': 'category',
                'categories': feed['categories'],
            }
        response['feed'].append(
            {
                'feed_id': feed['id'],
                'created': '2018-12-03T00:00:00+0000',
                'request_id': 'request_id',
                'last_status': make_feed_status(feed),
                'payload': payload,
            },
        )
    return response


INFORMER = {
    'content': {
        'background': {
            'dark': {'content': 'dark_background', 'type': 'image'},
            'light': {'content': 'FF0000', 'type': 'color'},
        },
        'image': {
            'dark': {'content': 'dark_image', 'media_type': 'image'},
            'light': {'content': 'light_image', 'media_type': 'image'},
        },
        'text': {
            'color': {'dark': 'FF0000', 'light': '0000FF'},
            'content': 'some_text',
        },
        'type': 'text_with_image',
    },
    'deeplink': 'http://yandex.ru/mobile',
    'has_close_button': True,
    'url': 'http://yandex.ru',
}


BACKGROUND_INFORMER = {
    'content': {
        'background': {
            'dark': {'content': '6D131C', 'type': 'color'},
            'light': {'content': 'media_id_example_light', 'type': 'image'},
        },
        'text': {
            'color': {'dark': 'FF0000', 'light': '0000FF'},
            'content': 'some text',
        },
        'type': 'background',
    },
    'deeplink': 'http://yandex.ru/mobile',
    'has_close_button': False,
    'url': 'http://yandex.ru',
}


def format_informer(feeds_payload, feed_id):
    def format_image(image):
        image['light'] = image.pop('light')['content']
        image['dark'] = image.pop('dark')['content']

    def format_color(color):
        return f'#{color}'

    def format_background_color(background):
        if background['type'] == 'color':
            background['content'] = format_color(background['content'])

    def format_text_color(text_color):
        text_color['dark'] = format_color(text_color['dark'])
        text_color['light'] = format_color(text_color['light'])

    result = copy.deepcopy(feeds_payload)
    result['id'] = feed_id
    result['payload'] = result.pop('content')
    payload = result['payload']
    if 'image' in payload:
        format_image(payload['image'])
    if 'text' in payload:
        payload['text']['value'] = payload['text'].pop('content')
        format_text_color(payload['text']['color'])
    format_background_color(payload['background']['light'])
    format_background_color(payload['background']['dark'])
    return result


def make_fetch_informers_response(feeds):
    response = {
        'polling_delay': 60,
        'etag': '9fa57b4f16945a7eb9a1cfecd474849f',
        'feed': [],
        'has_more': False,
    }
    for feed in feeds:
        payload = copy.deepcopy(feed.get('payload', INFORMER))
        payload['priority'] = feed.get('priority', 0)
        payload['experiment'] = feed.get('experiment', '')
        payload['show_strategy'] = feed.get('show_strategy', None)
        response['feed'].append(
            {
                'feed_id': feed['id'],
                'created': '2018-12-03T00:00:00+0000',
                'request_id': 'request_id',
                'last_status': make_feed_status(feed),
                'payload': payload,
            },
        )
    return response
