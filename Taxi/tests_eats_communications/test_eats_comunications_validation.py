import pytest

from . import experiments

HANDLE = '/eats/v1/eats-communications/v1/communications'
HADLE_RETRIEVE = '/eats/v1/eats-communications/v1/communications/retrieve'
FEEDS_HANDLE = '/feeds/v1/fetch'
FEEDS_HANDLE_RETRIEVE = '/feeds/v1/fetch_by_id'

FEEDS_FETCH_RESPONSE_INVALID = {
    'polling_delay': 30,
    'etag': '5b750d8bbe805737aead72de77ebf7da',
    'feed': [
        {
            # этот фид валидный и проходит
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
                            'content': 'Валидный фулскрин',
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
                        # дополнительные поля не ломают валидацию
                        'extra_field': 'extra_data',
                    },
                ],
                'screens': ['restlist'],
                'priority': 1,
            },
        },
        {
            # этот фид не валидный и будет отфильтрован
            'feed_id': '7a41a7bb43a3427ab61cbafc58079371',
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
                            'content': 'Невалидный фулскрин',
                        },
                        'title': {'color': 'FF5157', 'content': 'Фулскрин'},
                        # поле widgets отсутствует
                        'alt_title': {
                            'color': 'EA503F',
                            'content': 'будет отфильтрован из выдачи',
                        },
                        'backgrounds': [
                            {'type': 'color', 'content': 'E7ECF2'},
                        ],
                    },
                ],
                'screens': ['restlist'],
                'priority': 1,
            },
        },
    ],
    'has_more': False,
}

EXPECTED_RESULT_ALL = {
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
                            'content': 'Валидный фулскрин',
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
                        'extra_field': 'extra_data',
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
                'id': '7a41a7bb43a3427ab61cbafc58079371',
                'pages': [
                    {
                        'text': {
                            'color': '00691F',
                            'content': 'Невалидный фулскрин',
                        },
                        'title': {'color': 'FF5157', 'content': 'Фулскрин'},
                        'alt_title': {
                            'color': 'EA503F',
                            'content': 'будет отфильтрован из выдачи',
                        },
                        'backgrounds': [
                            {'type': 'color', 'content': 'E7ECF2'},
                        ],
                    },
                ],
                'screen': 'restlist',
                'priority': 1,
            },
        },
    ],
}

EXPECTED_RESULT_FILTERED = {
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
                            'content': 'Валидный фулскрин',
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
                        'extra_field': 'extra_data',
                    },
                ],
                'screen': 'restlist',
                'priority': 1,
            },
        },
    ],
}


@pytest.mark.parametrize(
    'url,fetch_url,expected',
    [
        pytest.param(
            HANDLE,
            FEEDS_HANDLE,
            EXPECTED_RESULT_FILTERED,
            marks=(experiments.feed_validation(remove_invalid=True)),
            id='communications exp on',
        ),
        pytest.param(
            HADLE_RETRIEVE,
            FEEDS_HANDLE_RETRIEVE,
            EXPECTED_RESULT_FILTERED,
            marks=(experiments.feed_validation(remove_invalid=True)),
            id='communications/retrieve exp on',
        ),
        pytest.param(
            HANDLE,
            FEEDS_HANDLE,
            EXPECTED_RESULT_ALL,
            marks=(experiments.feed_validation(remove_invalid=False)),
            id='communications exp off',
        ),
        pytest.param(
            HADLE_RETRIEVE,
            FEEDS_HANDLE_RETRIEVE,
            EXPECTED_RESULT_ALL,
            marks=(experiments.feed_validation(remove_invalid=False)),
            id='communications/retrieve exp off',
        ),
        pytest.param(
            HANDLE,
            FEEDS_HANDLE,
            EXPECTED_RESULT_ALL,
            id='communications no exp',
        ),
        pytest.param(
            HADLE_RETRIEVE,
            FEEDS_HANDLE_RETRIEVE,
            EXPECTED_RESULT_ALL,
            id='communications/retrieve no exp',
        ),
    ],
)
@experiments.channel('fake_test')
async def test_fetch_communications_validation(
        taxi_eats_communications, mockserver, url, fetch_url, expected,
):
    # Тест проверяет что невалидные фиды не попадут в выдачу

    @mockserver.json_handler(fetch_url)
    def feeds(_):
        return FEEDS_FETCH_RESPONSE_INVALID

    response = await taxi_eats_communications.post(
        url,
        json={
            'application': {
                'device_id': 'fake_device_id',
                'platform': 'eda_desktop_web',
                'screen_resolution': {'width': 1024, 'height': 768},
            },
            'location': {'latitude': 0.0, 'longitude': 0.0},
            'ids': ['id_1'],
        },
    )
    assert feeds.times_called == 1
    assert response.status_code == 200
    assert response.json() == expected
