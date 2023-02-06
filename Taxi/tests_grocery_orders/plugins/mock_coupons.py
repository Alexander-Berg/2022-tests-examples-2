import pytest


@pytest.fixture(name='coupons')
def mock_coupons(mockserver):
    class Context:
        def __init__(self):
            self.phone_id = None
            self.series_id = None
            self.token = None
            self.value = None
            self.yandex_uid = None
            self.cost_usage = None
            self.coupon_id = None
            self.order_id = None
            self.coupon_finish_order_id = None
            self.service = None
            self.success = None
            self.expire_at = None
            self.reserve_error_code = None
            self.generate_error_code = None
            self.referral_error_code = None
            self.valid = True
            self.value_numeric = None

            self.check_request_flag = False

        def check_request(
                self,
                phone_id=None,
                series_id=None,
                token=None,
                value=None,
                yandex_uid=None,
                cost_usage=None,
                coupon_id=None,
                order_id=None,
                coupon_finish_order_id=None,
                referral_error_code=None,
                service=None,
                success=None,
                expire_at=None,
                value_numeric=None,
        ):
            self.phone_id = phone_id
            self.series_id = series_id
            self.token = token
            self.value = value
            self.yandex_uid = yandex_uid
            self.cost_usage = cost_usage
            self.coupon_id = coupon_id
            self.order_id = order_id
            self.coupon_finish_order_id = coupon_finish_order_id
            self.referral_error_code = referral_error_code
            self.service = service
            self.success = success
            self.expire_at = expire_at
            self.value_numeric = value_numeric

            self.check_request_flag = True

        def set_valid(self, valid):
            self.valid = valid

        def set_reserve_error_code(self, code):
            self.reserve_error_code = code

        def set_generate_error_code(self, code):
            self.generate_error_code = code

        def set_referral_error_code(self, code):
            self.referral_error_code = code

        def times_generate_called(self):
            return mock_generate.times_called

        def times_coupon_finish_called(self):
            return mock_coupon_finish.times_called

        def times_coupon_reserve_called(self):
            return mock_coupon_reserve.times_called

        def times_referral_complete_called(self):
            return mock_coupon_referral_complete.times_called

        def flush(self):
            mock_generate.flush()

    context = Context()

    @mockserver.json_handler('coupons/internal/generate')
    def mock_generate(request):
        if context.generate_error_code is not None:
            return mockserver.make_response(
                'fail', status=context.generate_error_code,
            )

        if context.check_request_flag:
            assert 'application_name' in request.json
            assert 'brand_name' in request.json
            if context.phone_id is not None:
                assert request.json['phone_id'] == context.phone_id
            if context.series_id is not None:
                assert request.json['series_id'] == context.series_id
            if context.token is not None:
                assert request.json['token'] == context.token
            if context.expire_at is not None:
                assert request.json['expire_at'] == context.expire_at

            if context.value is not None:
                assert request.json['value'] == context.value
            else:
                assert 'value' not in request.json

            if context.value_numeric is not None:
                assert request.json['value_numeric'] == context.value_numeric
            else:
                assert 'value_numeric' not in request.json

            if context.yandex_uid is not None:
                assert request.json['yandex_uid'] == context.yandex_uid

        return {
            'promocode': 'SOME_PROMOCODE',
            'promocode_params': {
                'value': 30,
                'expire_at': '2021-05-20T00:00:00+00:00',
                'currency_code': 'RUB',
                'value_numeric': '30',
            },
        }

    @mockserver.json_handler('coupons/internal/coupon_finish')
    def mock_coupon_finish(request):
        if context.check_request_flag:
            assert 'application_name' in request.json
            if context.cost_usage is not None:
                assert request.json['cost_usage'] == context.cost_usage
            if context.coupon_id is not None:
                assert request.json['coupon_id'] == context.coupon_id
            if context.coupon_finish_order_id is not None:
                assert (
                    request.json['order_id'] == context.coupon_finish_order_id
                )
            if context.phone_id is not None:
                assert request.json['phone_id'] == context.phone_id
            if context.service is not None:
                assert request.json['service'] == context.service
            if context.yandex_uid is not None:
                assert request.json['yandex_uid'] == context.yandex_uid
            if context.success is not None:
                assert request.json['success'] == context.success
            if context.token is not None:
                assert request.headers['X-Idempotency-Token'] == context.token

        return {}

    @mockserver.json_handler('coupons/v1/couponreserve')
    def mock_coupon_reserve(request):
        if context.reserve_error_code is not None:
            return mockserver.make_response(
                'fail', status=context.reserve_error_code,
            )

        if context.check_request_flag:
            assert 'name' in request.json['application']
            if context.coupon_id is not None:
                assert request.json['code'] == context.coupon_id
            if context.order_id is not None:
                assert request.json['order_id'] == context.order_id
            if context.phone_id is not None:
                assert request.json['phone_id'] == context.phone_id
            if context.service is not None:
                assert request.json['service'] == context.service
            if context.yandex_uid is not None:
                assert request.json['current_yandex_uid'] == context.yandex_uid
            if context.token is not None:
                assert request.headers['X-Idempotency-Token'] == context.token

        return {
            'exists': True,
            'valid': context.valid,
            'value': 100,
            'valid_any': True,
            'series': request.json['code'],
            'expire_at': '2021-05-20T00:00:00+00:00',
            'currency_code': 'RUB',
            'descr': 'Description',
        }

    @mockserver.json_handler('coupons/v1/referral_complete')
    def mock_coupon_referral_complete(request):
        if context.check_request_flag:
            if context.order_id is not None:
                assert request.json['order_id'] == context.order_id
            if context.yandex_uid is not None:
                assert request.json['yandex_uid'] == context.yandex_uid
            if context.coupon_id is not None:
                assert request.json['promocode'] == context.coupon_id
        if context.referral_error_code is not None:
            response_code = context.referral_error_code
            return mockserver.make_response(
                json={'message': 'set response code'}, status=response_code,
            )
        return {}

    return context
