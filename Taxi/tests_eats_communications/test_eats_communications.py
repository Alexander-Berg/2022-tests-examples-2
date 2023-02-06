from . import experiments


FEEDS_FETCH_RESPONSE = {
    'polling_delay': 30,
    'etag': '5b750d8bbe805737aead72de77ebf7da',
    'feed': [
        {
            'feed_id': '7a41a7bb43a3427ab61cbafc58079370',
            'created': '2020-09-02T13:34:37.894921+0000',
            'request_id': 'request_id',
            'last_status': {
                'status': 'published',
                'created': '2020-09-02T13:34:37.97935+0000',
            },
            'payload': {
                'pages': [
                    {
                        'text': {
                            'color': '00691F',
                            'content': 'Воу воу воу!\nПалехче',
                        },
                        'title': {'color': 'FF5157', 'content': 'Фулскрин'},
                        'widgets': {'pager': {}, 'close_button': {}},
                        'alt_title': {
                            'color': 'EA503F',
                            'content': 'неужели работает',
                        },
                        'backgrounds': [
                            {'type': 'color', 'content': 'E7ECF2'},
                        ],
                    },
                    {
                        'text': {
                            'color': '143264',
                            'content': 'Сам в шоке!!!',
                        },
                        'title': {
                            'color': 'FF5157',
                            'content': 'И даже второй слайд есть!',
                        },
                        'widgets': {
                            'pager': {},
                            'close_button': {},
                            'action_buttons': [
                                {
                                    'text': 'Текст кнопки',
                                    'text_color': '#ffffff',
                                    'color': '#bada55',
                                    'action': {
                                        'type': 'deeplink',
                                        'payload': {
                                            'content': 'http://localhost',
                                            'need_authorization': True,
                                        },
                                    },
                                },
                            ],
                        },
                        'alt_title': {
                            'color': 'E14138',
                            'content': 'И такое бывает!',
                        },
                        'backgrounds': [
                            {'type': 'color', 'content': 'C4CDD6'},
                        ],
                    },
                ],
                'screens': ['restlist', 'menu'],
                'priority': 1,
            },
        },
    ],
    'has_more': False,
}


@experiments.channel('fake_test')
async def test_fetch_communications(taxi_eats_communications, mockserver):
    @mockserver.json_handler('/feeds/v1/fetch')
    def feeds(request):
        assert 'experiment:fake_test' in request.json['channels']
        return FEEDS_FETCH_RESPONSE

    response = await taxi_eats_communications.post(
        '/eats/v1/eats-communications/v1/communications',
        json={
            'application': {
                'device_id': 'fake_device_id',
                'platform': 'eda_desktop_web',
                'screen_resolution': {'width': 1024, 'height': 768},
            },
            'location': {'latitude': 0.0, 'longitude': 0.0},
        },
    )
    assert feeds.times_called == 1
    assert response.status_code == 200
    assert response.json() == {
        'feed': [
            {
                'created': '2020-09-02T13:34:37.894921+0000',
                'last_status': {
                    'status': 'published',
                    'created': '2020-09-02T13:34:37.97935+0000',
                },
                'payload': {
                    'id': '7a41a7bb43a3427ab61cbafc58079370',
                    'pages': [
                        {
                            'text': {
                                'color': '00691F',
                                'content': 'Воу воу воу!\nПалехче',
                            },
                            'title': {
                                'color': 'FF5157',
                                'content': 'Фулскрин',
                            },
                            'widgets': {'pager': {}, 'close_button': {}},
                            'alt_title': {
                                'color': 'EA503F',
                                'content': 'неужели работает',
                            },
                            'backgrounds': [
                                {'type': 'color', 'content': 'E7ECF2'},
                            ],
                        },
                        {
                            'text': {
                                'color': '143264',
                                'content': 'Сам в шоке!!!',
                            },
                            'title': {
                                'color': 'FF5157',
                                'content': 'И даже второй слайд есть!',
                            },
                            'widgets': {
                                'pager': {},
                                'close_button': {},
                                'action_buttons': [
                                    {
                                        'action': {
                                            'type': 'deeplink',
                                            'payload': {
                                                'content': 'http://localhost',
                                                'need_authorization': True,
                                            },
                                        },
                                        'color': '#bada55',
                                        'text': 'Текст кнопки',
                                        'text_color': '#ffffff',
                                    },
                                ],
                            },
                            'alt_title': {
                                'color': 'E14138',
                                'content': 'И такое бывает!',
                            },
                            'backgrounds': [
                                {'type': 'color', 'content': 'C4CDD6'},
                            ],
                        },
                    ],
                    'screen': 'restlist',
                    'priority': 1,
                },
            },
            {
                'created': '2020-09-02T13:34:37.894921+0000',
                'last_status': {
                    'status': 'published',
                    'created': '2020-09-02T13:34:37.97935+0000',
                },
                'payload': {
                    'id': '7a41a7bb43a3427ab61cbafc58079370',
                    'pages': [
                        {
                            'text': {
                                'color': '00691F',
                                'content': 'Воу воу воу!\nПалехче',
                            },
                            'title': {
                                'color': 'FF5157',
                                'content': 'Фулскрин',
                            },
                            'widgets': {'pager': {}, 'close_button': {}},
                            'alt_title': {
                                'color': 'EA503F',
                                'content': 'неужели работает',
                            },
                            'backgrounds': [
                                {'type': 'color', 'content': 'E7ECF2'},
                            ],
                        },
                        {
                            'text': {
                                'color': '143264',
                                'content': 'Сам в шоке!!!',
                            },
                            'title': {
                                'color': 'FF5157',
                                'content': 'И даже второй слайд есть!',
                            },
                            'widgets': {
                                'pager': {},
                                'close_button': {},
                                'action_buttons': [
                                    {
                                        'action': {
                                            'type': 'deeplink',
                                            'payload': {
                                                'content': 'http://localhost',
                                                'need_authorization': True,
                                            },
                                        },
                                        'color': '#bada55',
                                        'text': 'Текст кнопки',
                                        'text_color': '#ffffff',
                                    },
                                ],
                            },
                            'alt_title': {
                                'color': 'E14138',
                                'content': 'И такое бывает!',
                            },
                            'backgrounds': [
                                {'type': 'color', 'content': 'C4CDD6'},
                            ],
                        },
                    ],
                    'screen': 'menu',
                    'priority': 1,
                },
            },
        ],
    }


@experiments.has_ya_plus('only_plus', ['eats-communications/communications'])
async def test_fullscreen_has_ya_plus(taxi_eats_communications, mockserver):
    @mockserver.json_handler('/feeds/v1/fetch')
    def feeds(request):
        assert 'experiment:only_plus' in request.json['channels']
        return {
            'polling_delay': 30,
            'etag': '5b750d8bbe805737aead72de77ebf7da',
            'feed': [],
        }

    response = await taxi_eats_communications.post(
        '/eats/v1/eats-communications/v1/communications',
        headers={
            'X-YaTaxi-User': 'eats_user_id=12345',
            'X-YaTaxi-Session': 'session',
            'X-YaTaxi-Pass-Flags': 'portal,ya-plus',
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
    assert feeds.times_called == 1
    assert response.status_code == 200
