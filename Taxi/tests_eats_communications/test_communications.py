import pytest

EDA_CATALOG_SHORTLIST_RESPONSE = {
    'payload': {
        'places': [
            {
                'id': 1,
                'name': 'Fake place',
                'slug': 'fake_place_99',
                'service': 'eats',
                'brand': {'id': 1},
                'location': {'longitude': 0.121, 'latitude': -0.21},
                'deliveryTime': {'min': 10, 'max': 15},
                'promos': [
                    {
                        'id': 100,
                        'name': 'Скидка на все чего нет',
                        'description': '',
                        'type': {
                            'id': 10,
                            'name': 'Скидка на все',
                            'pictureUri': '/fake_picture.png',
                            'detailedPictureUrl': '',
                        },
                    },
                ],
            },
        ],
    },
}

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
                'recipients': {'places': [1, 2, 3]},
                'screens': ['screen1'],
                'priority': 1,
                'groups': ['a', 'b', 'c'],
                'is_tapable': True,
                'mark_read_after_tap': True,
                'preview': {
                    'text': {
                        'color': 'bada55',
                        'content': 'feed preview text',
                    },
                    'title': {
                        'color': 'bada55',
                        'content': 'feed preview title',
                    },
                    'backgrounds': [
                        {
                            'type': 'image',
                            'content': 'http://preview_image.png',
                        },
                        {'type': 'color', 'content': 'ffffff'},
                    ],
                },
                'pages': [
                    {
                        'autonext': False,
                        'duration': 1,
                        'text': {
                            'color': '000000',
                            'content': 'first page text',
                        },
                        'title': {
                            'color': '000000',
                            'content': 'first page title',
                        },
                        'backgrounds': [
                            {
                                'type': 'image',
                                'content': 'http://page_1_background.png',
                            },
                            {'type': 'color', 'content': 'ffffff'},
                        ],
                        'widgets': {
                            'close_button': {'color': 'ffffff'},
                            'menu_button': {'color': '1d1d1d1'},
                            'pager': {
                                'color_on': 'ededed',
                                'color_off': 'fafafa',
                            },
                            'link': {
                                'text': 'link text',
                                'text_color': '2d2f2d',
                                'action': {
                                    'type': 'deeplink',
                                    'payload': {
                                        'content': 'eda://widget_deeplink.com',
                                        'need_authorization': True,
                                    },
                                },
                            },
                            'action_buttons': [
                                {
                                    'text': 'action button deeplink',
                                    'text_color': 'dadada',
                                    'color': 'dbdbdb',
                                    'deeplink': 'http://yandex.ru',
                                },
                            ],
                        },
                    },
                ],
            },
            'meta': {'actions': ['sad']},
            'statistics': {'meta': {'very_good': 1, 'sad': 1, 'like': 1}},
        },
        {
            'feed_id': '222c69c8afe947ba887fd6404428b31c',
            'created': '2018-12-02T00:00:00+0000',
            'request_id': 'request_id',
            'last_status': {
                'status': 'published',
                'created': '2018-12-01T00:00:00+0000',
            },
            'payload': {
                'recipients': {'type': 'info'},
                'screens': [],
                'priority': 1,
                'groups': [],
                'is_tapable': True,
                'mark_read_after_tap': True,
                'preview': {
                    'text': {
                        'color': 'bada55',
                        'content': 'feed preview text',
                    },
                    'title': {
                        'color': 'bada55',
                        'content': 'feed preview title',
                    },
                    'backgrounds': [
                        {
                            'type': 'image',
                            'content': 'http://preview_image.png',
                        },
                        {'type': 'color', 'content': 'ffffff'},
                    ],
                },
                'pages': [
                    {
                        'autonext': False,
                        'duration': 1,
                        'text': {
                            'color': '000000',
                            'content': 'first page text',
                        },
                        'title': {
                            'color': '000000',
                            'content': 'first page title',
                        },
                        'backgrounds': [
                            {
                                'type': 'image',
                                'content': 'http://page_1_background.png',
                            },
                            {'type': 'color', 'content': 'ffffff'},
                        ],
                        'widgets': {
                            'close_button': {'color': '000000'},
                            'pager': {
                                'color_off': 'fafafa',
                                'color_on': 'bababa',
                            },
                            'link': {
                                'text': 'link text',
                                'text_color': '2d2f2d',
                                'action': {
                                    'type': 'deeplink',
                                    'payload': {
                                        'content': 'eda://widget_deeplink.com',
                                        'need_authorization': True,
                                    },
                                },
                            },
                            'action_buttons': [
                                {
                                    'text': 'action button deeplink',
                                    'text_color': 'dadada',
                                    'color': 'dbdbdb',
                                    'deeplink': 'http://yandex.ru',
                                },
                            ],
                        },
                    },
                ],
            },
            'meta': {},
        },
        {
            'feed_id': '111c69c8afe947ba887fd6404428b31c',
            'created': '2018-12-01T00:00:00+0000',
            'request_id': 'request_id',
            'last_status': {
                'status': 'published',
                'created': '2018-12-01T00:00:00+0000',
            },
            'payload': {'text': 'feed1'},
            'meta': {},
            'statistics': {'meta': {'like': 1}},
        },
    ],
    'has_more': False,
}

VALID_PAGE = {
    'text': {'color': '00691F', 'content': 'Я валиден'},
    'title': {'color': 'FF5157', 'content': 'Фулскрин'},
    'widgets': {
        'pager': {'color_on': '00691F', 'color_off': '00691F'},
        'close_button': {'color': 'FF5157'},
    },
    'backgrounds': [{'type': 'color', 'content': 'E7ECF2'}],
    'autonext': False,
    'duration': 1,
}
INVALID_PAGE = {
    'text': {'color': '00691F', 'content': 'Я сломан :('},
    'title': {'color': 'FF5157', 'content': 'Невалидный фулскрин'},
    'widgets': {
        'action_buttons': [
            {
                'text': 'action button deeplink',
                'text_color': 'dadada',
                'color': 'dbdbdb',
            },
        ],
    },
    'backgrounds': [],
    'autonext': False,
}

FEEDS_FETCH_RESPONSE_WITH_INVALID_STORIES = {
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
                'recipients': {'places': [1, 2, 3]},
                'screens': ['screen1'],
                'priority': 1,
                'groups': ['a', 'b', 'c'],
                'is_tapable': True,
                'mark_read_after_tap': True,
                'preview': {
                    'text': {'color': '', 'content': ''},
                    'title': {'color': '', 'content': ''},
                    'backgrounds': [{'type': 'color', 'content': ''}],
                },
                'pages': [INVALID_PAGE],
            },
            'meta': {},
        },
        {
            'feed_id': '222c69c8afe947ba887fd6404428b31c',
            'created': '2018-12-02T00:00:00+0000',
            'request_id': 'request_id',
            'last_status': {
                'status': 'published',
                'created': '2018-12-01T00:00:00+0000',
            },
            'payload': {
                'recipients': {'type': 'info'},
                'screens': ['screen1', 'screen2'],
                'priority': 1,
                'groups': [],
                'is_tapable': True,
                'mark_read_after_tap': True,
                'preview': {
                    'text': {'color': '', 'content': ''},
                    'title': {'color': '', 'content': ''},
                    'backgrounds': [{'type': 'color', 'content': ''}],
                },
                'pages': [VALID_PAGE, INVALID_PAGE],
            },
            'meta': {},
        },
        {
            'feed_id': '111c69c8afe947ba887fd6404428b31c',
            'created': '2018-12-01T00:00:00+0000',
            'request_id': 'request_id',
            'last_status': {
                'status': 'published',
                'created': '2018-12-01T00:00:00+0000',
            },
            'payload': {
                'recipients': {'type': 'info'},
                'screens': ['screen2'],
                'priority': 1,
                'groups': [],
                'is_tapable': True,
                'mark_read_after_tap': True,
                'preview': {
                    'text': {'color': '', 'content': ''},
                    'title': {'color': '', 'content': ''},
                    'backgrounds': [{'type': 'color', 'content': ''}],
                },
                'pages': [VALID_PAGE],
            },
            'meta': {},
        },
    ],
    'has_more': False,
}

_COMMUNICATIONS_EXP = {
    'match': {'predicate': {'init': {}, 'type': 'true'}, 'enabled': True},
    'name': 'fake_test',
    'consumers': ['eats-communications/communications'],
    'clauses': [
        {
            'title': 'Matching device',
            'value': {'enabled': True},
            'predicate': {
                'type': 'eq',
                'init': {
                    'arg_name': 'device_id',
                    'arg_type': 'string',
                    'value': 'fake_device_id',
                },
            },
        },
    ],
}


@pytest.mark.experiments3(**_COMMUNICATIONS_EXP)
async def test_layout_communications(taxi_eats_communications, mockserver):
    @mockserver.json_handler('/eda-catalog/v1/shortlist')
    def _shortlist(request):
        return EDA_CATALOG_SHORTLIST_RESPONSE

    @mockserver.json_handler('/feeds/v1/fetch')
    def _feeds(request):
        assert request.json['service'] == 'eats-promotions-story'
        assert 'experiment:fake_test' in request.json['channels']
        return FEEDS_FETCH_RESPONSE

    response = await taxi_eats_communications.post(
        '/eats-communications/v1/layout/communications',
        headers={
            'x-device-id': 'fake_device_id',
            'x-platform': 'eda_desktop_web',
        },
        json={
            'application': {
                'device_id': 'fake_device_id',
                'platform': 'eda_desktop_web',
                'screen_resolution': {'width': 1024, 'height': 768},
            },
            'location': {'latitude': 0.0, 'longitude': 0.0},
        },
    )

    assert response.status_code == 200
    assert response.json() == {
        'stories': [
            {
                'meta': {'groups': ['a', 'b', 'c'], 'screens': ['screen1']},
                'payload': {
                    'offer': {
                        'shortcut_id': '333c69c8afe947ba887fd6404428b31c',
                        'title': {
                            'content': 'feed preview title',
                            'color': 'bada55',
                        },
                        'subtitle': {
                            'content': 'feed preview text',
                            'color': 'bada55',
                        },
                        'backgrounds': [
                            {
                                'type': 'image',
                                'content': 'http://preview_image.png',
                            },
                            {'type': 'color', 'content': 'ffffff'},
                        ],
                    },
                    'pages': [
                        {
                            'autonext': False,
                            'duration': 1,
                            'text': {
                                'color': '000000',
                                'content': 'first page text',
                            },
                            'title': {
                                'color': '000000',
                                'content': 'first page title',
                            },
                            'backgrounds': [
                                {
                                    'type': 'image',
                                    'content': 'http://page_1_background.png',
                                },
                                {'type': 'color', 'content': 'ffffff'},
                            ],
                            'widgets': {
                                'close_button': {'color': 'ffffff'},
                                'menu_button': {'color': '1d1d1d1'},
                                'pager': {
                                    'color_on': 'ededed',
                                    'color_off': 'fafafa',
                                },
                                'link': {
                                    'text': 'link text',
                                    'text_color': '2d2f2d',
                                    'action': {
                                        'type': 'deeplink',
                                        'payload': {
                                            'content': (
                                                'eda://widget_deeplink.com'
                                            ),
                                            'need_authorization': True,
                                        },
                                    },
                                },
                                'action_buttons': [
                                    {
                                        'text': 'action button deeplink',
                                        'text_color': 'dadada',
                                        'color': 'dbdbdb',
                                        'deeplink': 'http://yandex.ru',
                                    },
                                ],
                            },
                        },
                    ],
                },
            },
            {
                'meta': {'groups': [], 'screens': []},
                'payload': {
                    'offer': {
                        'shortcut_id': '222c69c8afe947ba887fd6404428b31c',
                        'title': {
                            'content': 'feed preview title',
                            'color': 'bada55',
                        },
                        'subtitle': {
                            'content': 'feed preview text',
                            'color': 'bada55',
                        },
                        'backgrounds': [
                            {
                                'type': 'image',
                                'content': 'http://preview_image.png',
                            },
                            {'type': 'color', 'content': 'ffffff'},
                        ],
                    },
                    'pages': [
                        {
                            'autonext': False,
                            'duration': 1,
                            'text': {
                                'color': '000000',
                                'content': 'first page text',
                            },
                            'title': {
                                'color': '000000',
                                'content': 'first page title',
                            },
                            'backgrounds': [
                                {
                                    'type': 'image',
                                    'content': 'http://page_1_background.png',
                                },
                                {'type': 'color', 'content': 'ffffff'},
                            ],
                            'widgets': {
                                'close_button': {'color': '000000'},
                                'pager': {
                                    'color_off': 'fafafa',
                                    'color_on': 'bababa',
                                },
                                'link': {
                                    'text': 'link text',
                                    'text_color': '2d2f2d',
                                    'action': {
                                        'type': 'deeplink',
                                        'payload': {
                                            'content': (
                                                'eda://widget_deeplink.com'
                                            ),
                                            'need_authorization': True,
                                        },
                                    },
                                },
                                'action_buttons': [
                                    {
                                        'text': 'action button deeplink',
                                        'text_color': 'dadada',
                                        'color': 'dbdbdb',
                                        'deeplink': 'http://yandex.ru',
                                    },
                                ],
                            },
                        },
                    ],
                },
            },
        ],
    }


@pytest.mark.experiments3(**_COMMUNICATIONS_EXP)
async def test_layout_communications_all_500(
        taxi_eats_communications, mockserver,
):
    @mockserver.json_handler('/eda-catalog/v1/shortlist')
    def _shortlist(request):
        return mockserver.make_response(
            status=500,
            json=[{'code': 'fatal', 'title': 'something gone wrong'}],
        )

    @mockserver.json_handler('/feeds/v1/fetch')
    def _feeds(request):
        assert 'experiment:fake_test' in request.json['channels']
        return mockserver.make_response(status=500, json={})

    response = await taxi_eats_communications.post(
        '/eats-communications/v1/layout/communications',
        json={
            'application': {
                'device_id': 'fake_device_id',
                'platform': 'eda_desktop_web',
                'screen_resolution': {'width': 1024, 'height': 768},
            },
            'location': {'latitude': 0.0, 'longitude': 0.0},
        },
    )

    assert response.status_code == 200
    assert response.json() == {'stories': []}


@pytest.mark.config(
    EATS_COMMUNICATIONS_VALIDATION_SETTINGS={'validate_stories': True},
)
@pytest.mark.experiments3(**_COMMUNICATIONS_EXP)
async def test_layout_communications_validate_stories(
        taxi_eats_communications, mockserver,
):
    """
    Тест проверяет, что сторисы, которые содержат невалидный
    payload будут отфильтрованы из выдачи
    """

    @mockserver.json_handler('/eda-catalog/v1/shortlist')
    def _shortlist(request):
        return EDA_CATALOG_SHORTLIST_RESPONSE

    @mockserver.json_handler('/feeds/v1/fetch')
    def _feeds(request):
        assert request.json['service'] == 'eats-promotions-story'
        assert 'experiment:fake_test' in request.json['channels']
        return FEEDS_FETCH_RESPONSE_WITH_INVALID_STORIES

    response = await taxi_eats_communications.post(
        '/eats-communications/v1/layout/communications',
        headers={
            'x-device-id': 'fake_device_id',
            'x-platform': 'eda_desktop_web',
        },
        json={
            'application': {
                'device_id': 'fake_device_id',
                'platform': 'eda_desktop_web',
                'screen_resolution': {'width': 1024, 'height': 768},
            },
            'location': {'latitude': 0.0, 'longitude': 0.0},
        },
    )

    assert response.status_code == 200
    assert response.json() == {
        'stories': [
            {
                'payload': {
                    'offer': {
                        'backgrounds': [{'content': '', 'type': 'color'}],
                        'shortcut_id': '111c69c8afe947ba887fd6404428b31c',
                        'subtitle': {'color': '', 'content': ''},
                        'title': {'color': '', 'content': ''},
                    },
                    'pages': [VALID_PAGE],
                },
                'meta': {'screens': ['screen2'], 'groups': []},
            },
        ],
    }
