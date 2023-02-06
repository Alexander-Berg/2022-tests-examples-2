import pytest

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
                ],
                'screens': ['restlist'],
                'priority': 1,
            },
        },
    ],
    'has_more': False,
}

RESPONSE = {
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
                ],
                'screen': 'restlist',
                'priority': 1,
            },
        },
    ],
}


@pytest.mark.experiments3(
    name='fake_test',
    consumers=['eats-communications/communications'],
    clauses=[
        {
            'predicate': {
                'init': {
                    'arg_name': 'is_eda_new_user',
                    'arg_type': 'bool',
                    'value': True,
                },
                'type': 'eq',
            },
            'value': {'enabled': True},
        },
        {
            'predicate': {
                'init': {
                    'arg_name': 'is_retail_new_user',
                    'arg_type': 'bool',
                    'value': True,
                },
                'type': 'eq',
            },
            'value': {'enabled': True},
        },
    ],
)
@pytest.mark.parametrize(
    'is_eda_new_user,is_retail_new_user,feeds_times_called,expected_response',
    [
        (False, False, 0, {}),
        (False, True, 1, RESPONSE),
        (True, False, 1, RESPONSE),
        (True, True, 1, RESPONSE),
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
async def test_fetch_communications(
        taxi_eats_communications,
        mockserver,
        is_eda_new_user,
        is_retail_new_user,
        feeds_times_called,
        expected_response,
):
    @mockserver.json_handler('/eda-delivery-price/v1/user-promo')
    def eda_delivery_time(request):
        assert request.json['region_id'] == 1
        return {
            'is_eda_new_user': is_eda_new_user,
            'is_retail_new_user': is_retail_new_user,
        }

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
            'location': {'latitude': 55.752344, 'longitude': 37.541332},
        },
    )
    assert eda_delivery_time.times_called == 1
    assert feeds.times_called == feeds_times_called
    assert response.status_code == 200
    assert response.json() == expected_response
