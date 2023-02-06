URL = '4.0/persuggest/v1/confirm'

PA_HEADERS = {
    'X-YaTaxi-UserId': 'b300bda7d41b4bae8d58dfa93221ef16',
    'X-YaTaxi-Pass-Flags': 'phonish',
    'X-Yandex-UID': '4003514353',
    'X-YaTaxi-PhoneId': '5714f45e98956f06baaae3d4',
    'X-Request-Language': 'ru',
    'X-Request-Application': 'app_name=yango_android',
    'X-Ya-User-Ticket': 'user_ticket',
    'Date': 'Tue, 01 Aug 2017 15:00:00 GMT',
}

PA_HEADERS_NO_AUTH = {
    'X-Request-Language': 'ru',
    'X-Request-Application': 'app_name=yango_android',
    'X-YaTaxi-UserId': 'b300bda7d41b4bae8d58dfa93221ef16',
    'Date': 'Tue, 01 Aug 2017 15:00:00 GMT',
}

BASIC_REQUEST = {
    'state': {
        'accuracy': 20,
        'bbox': [30.3, 50.5, 40.4, 60.6],
        'fields': [
            {'type': 'a', 'position': [10.12, 11.12], 'log': '{\"a\": 1}'},
            {'type': 'b', 'position': [12.12, 13.12], 'log': '{\"b\": 2}'},
            {
                'type': 'mid9',
                'position': [13.12, 14.12],
                'log': '{\"mid9\": 3}',
                'entrance': 'mid_e',
            },
        ],
        'location': [37.1, 55.1],
        'coord_providers': [
            {'type': 'gps', 'position': [14.1234, 15.1234], 'accuracy': 10.3},
            {
                'type': 'platform_lbs',
                'position': [16.1, 17.1],
                'accuracy': 4.2,
            },
        ],
    },
}


async def test_4_0_confirm_basic(taxi_persuggest, mockserver):
    @mockserver.json_handler('/yamaps-suggest-personal/suggest-personal-add')
    def _mock_suggest_personal_add(request):
        assert request.headers['X-Ya-User-Ticket'] == 'user_ticket'
        assert request.args == {
            'client': 'taxi',
            'timestamp': '1501599600',
            'action': 'route',
            'drive': '1',
            'pointa': '{\"a\": 1}',
            'pointb': '{\"b\": 2}',
            'pointmid9': 'mid_e',
            'entrancemid9': 'mid_e',
        }
        return {}

    response = await taxi_persuggest.post(
        URL, BASIC_REQUEST, headers=PA_HEADERS,
    )
    assert response.status_code == 200
    assert response.json() == {}


async def test_4_0_confirm_no_auth(taxi_persuggest):
    response = await taxi_persuggest.post(
        URL, BASIC_REQUEST, headers=PA_HEADERS_NO_AUTH,
    )
    assert response.status_code == 200
    assert response.json() == {}


async def test_4_0_confirm_no_date(taxi_persuggest):
    response = await taxi_persuggest.post(URL, BASIC_REQUEST)
    assert response.status_code == 400
    assert response.json() == {
        'code': '400',
        'message': 'Missing Date in header',
    }
