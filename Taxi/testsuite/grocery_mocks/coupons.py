import pytest

MOSCOW_ZONE_NAME = 'moscow'


@pytest.fixture(name='coupons', autouse=True)
def mock_coupons(mockserver):
    check_state = {'status_code': 200, 'body': {}}
    list_state = {
        'status_code': 200,
        'body': {},
        'zone_name': MOSCOW_ZONE_NAME,
    }
    referral_state = {'status_code': 200, 'body': {}, 'headers': {}}
    series_info_state = {
        'status_code': 200,
        'body': {'value': None},
        'series_id': None,
    }
    generate_state = {
        'status_code': 200,
        'body': {'promocode': None},
        'series_id': None,
        'yandex_uid': None,
    }

    @mockserver.json_handler('/coupons/internal/generate')
    def generate(request):
        assert 'application_name' in request.json
        assert 'brand_name' in request.json
        if generate_state['series_id'] is not None:
            assert request.json['series_id'] == generate_state['series_id']

        if generate_state['yandex_uid'] is not None:
            assert request.json['yandex_uid'] == generate_state['yandex_uid']

        promocode = (
            generate_state['body']['promocode']
            if generate_state['body']['promocode']
            else 'SOME_PROMOCODE'
        )

        return {
            'promocode': promocode,
            'promocode_params': {
                'value': 30,
                'expire_at': '2021-05-20T00:00:00+00:00',
                'currency_code': 'RUB',
            },
        }

    @mockserver.json_handler('/coupons/v1/coupons/referral')
    def referral(_request):
        if referral_state['headers']:
            assert (
                _request.headers['X-Yandex-UID']
                == referral_state['headers']['X-Yandex-UID']
            )
            assert (
                _request.headers['X-YaTaxi-User']
                == referral_state['headers']['X-YaTaxi-User']
            )

        if referral_state['status_code'] != '200':
            return mockserver.make_response(
                json=referral_state['body'],
                status=referral_state['status_code'],
            )

        return referral_state['body']

    @mockserver.json_handler('/coupons/internal/couponlist')
    def couponlist(_request):
        body = _request.json
        assert body['service'] == 'grocery'
        assert body['services'] == ['grocery']
        assert body['zone_name'] == list_state['zone_name']
        if 'payment_info' in list_state:
            assert body['payment_info'] == list_state['payment_info']

        if list_state['status_code'] != '200':
            return mockserver.make_response('', list_state['status_code'])

        return list_state['body']

    @mockserver.json_handler('/coupons/v1/couponcheck')
    def validate_promocode(_request):
        body = _request.json

        assert 'application' in body
        assert 'code' in body
        assert 'country' in body
        assert 'current_yandex_uid' in body
        assert 'format_currency' in body
        assert 'locale' in body
        assert 'payment_info' in body
        assert 'payment_options' in body
        assert 'phone_id' in body
        assert 'region_id' in body
        assert 'service' in body
        assert 'time_zone' in body
        assert 'user_ip' in body
        assert 'zone_classes' in body
        assert 'zone_name' in body
        assert 'yandex_uid' in body['payload']

        if 'application' in check_state:
            assert body['application'] == check_state['application']
        if 'country' in check_state:
            assert body['country'] == check_state['country']
        if 'current_yandex_uid' in check_state:
            assert (
                body['current_yandex_uid'] == check_state['current_yandex_uid']
            )
        if 'yandex_uid' in check_state:
            assert body['payload']['yandex_uid'] == check_state['yandex_uid']
        if 'format_currency' in check_state:
            assert body['format_currency'] == check_state['format_currency']
        if 'locale' in check_state:
            assert body['locale'] == check_state['locale']
        if 'payment_info' in check_state:
            assert body['payment_info'] == check_state['payment_info']
        if 'payment_options' in check_state:
            assert body['payment_options'] == check_state['payment_options']
        if 'phone_id' in check_state:
            assert body['phone_id'] == check_state['phone_id']
        if 'region_id' in check_state:
            assert body['region_id'] == check_state['region_id']
        if 'service' in check_state:
            assert body['service'] == check_state['service']
        if 'time_zone' in check_state:
            assert body['time_zone'] == check_state['time_zone']
        if 'user_ip' in check_state:
            assert body['user_ip'] == check_state['user_ip']
        if 'zone_classes' in check_state:
            assert body['zone_classes'] == check_state['zone_classes']
        if 'zone_name' in check_state:
            assert body['zone_name'] == check_state['zone_name']

        if check_state['code'] != '200':
            return mockserver.make_response('', check_state['status_code'])

        return check_state['body']

    @mockserver.json_handler('/coupons/internal/series/info')
    def series_info(_request):
        if series_info_state['series_id'] is not None:
            assert _request.json['series_id'] == series_info_state['series_id']
        if series_info_state['status_code'] != 200:
            return mockserver.make_response(
                json=series_info_state['body'],
                status=series_info_state['status_code'],
            )
        return {
            'series_id': 'first',
            'services': ['taxi'],
            'is_unique': True,
            'start': '2016-03-01',
            'finish': '2020-03-01',
            'descr': 'Уникальный, работает',
            'value': (
                series_info_state['body']['value']
                if series_info_state['body']['value']
                else 500
            ),
            'created': '2016-03-01T03:00:00+0300',
            'user_limit': 2,
            'currency': 'RUB',
            'country': 'rus',
        }

    class Context:
        def check_times_called(self):
            return validate_promocode.times_called

        def referral_times_called(self):
            return referral.times_called

        def couponlist_times_called(self):
            return couponlist.times_called

        @property
        def series_info_times_called(self):
            return series_info.times_called

        @property
        def generate_times_called(self):
            return generate.times_called

        def set_coupons_check_response(self, body=None, status_code=200):
            if body is None:
                body = {}
            status_code = str(status_code)
            check_state['code'] = status_code
            if status_code == '200':
                check_state['body'] = body
            else:
                check_state['body'] = {
                    'code': str(status_code),
                    'message': 'some error message',
                }

        def set_coupons_list_response(self, body=None, status_code=200):
            if body is None:
                body = {}
            status_code = str(status_code)
            list_state['status_code'] = status_code
            if status_code == '200':
                list_state['body'] = body
            else:
                list_state['body'] = {
                    'code': str(status_code),
                    'message': 'some error message',
                }

        def set_coupons_referral_response(self, body=None, status_code=200):
            if body is None:
                body = {}
            status_code = str(status_code)
            referral_state['status_code'] = status_code
            if status_code == '200':
                referral_state['body'] = body
            else:
                referral_state['body'] = {
                    'code': str(status_code),
                    'message': 'some error message',
                }

        def set_coupons_generate_response(self, body=None, status_code=200):
            if body is None:
                body = {}
            status_code = str(status_code)
            generate_state['status_code'] = status_code
            if status_code == '200':
                generate_state['body'] = body
            else:
                generate_state['body'] = {
                    'code': str(status_code),
                    'message': 'some error message',
                }

        def set_series_info_response(self, body=None, status_code=200):
            if body is None:
                body = {}
            series_info_state['status_code'] = status_code
            status_code = str(status_code)
            if status_code == '200':
                series_info_state['body'] = body
            else:
                series_info_state['body'] = {
                    'code': str(status_code),
                    'message': 'some error message',
                }

        def check_check_request(self, **kwargs):
            check_state.update(kwargs)

        def check_list_request(self, **kwargs):
            list_state.update(kwargs)

        def check_referral_request(self, **kwargs):
            referral_state.update(kwargs)

        def check_series_info_request(self, series_id=None):
            series_info_state['series_id'] = series_id

        def check_generate_request(self, yandex_uid=None, series_id=None):
            generate_state['yandex_uid'] = yandex_uid
            generate_state['series_id'] = series_id

    context = Context()
    return context
