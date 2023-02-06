import json

import pytest


def __get_ids(user_info, type_id):
    print('GET_IDS')
    print(user_info, type_id)
    if user_info is None:
        return None
    for elem in user_info.split(','):
        info_id, value = elem.split('=')
        if info_id == ' personal_phone_id':
            info_id = 'personal_phone_id'
        if info_id == type_id:
            return value
    return None


@pytest.fixture(name='grocery_marketing', autouse=True)
def mock_grocery_marketing(mockserver):
    tags_by_user = {}
    tags_by_device_id = {}
    tags_by_payment_id = {}
    tags_by_eats_id = {}
    tags_by_phone_id = {}
    tags_by_glue = {}

    class Context:
        def __init__(self):
            self.tag = None
            self.request_time = None
            self.depot_id = None
            self.cart_id = None
            self.cart_version = None
            self.min_cart_cost = None
            self.usage_count = 0
            self.products = None

            self.tag_retrieve_error_code = {}
            self.fail_tag_check = None

            self.check_request_flag = False

        def check_request(
                self,
                tag=None,
                request_time=None,
                depot_id=None,
                cart_id=None,
                cart_version=None,
                min_cart_cost=None,
                usage_count=None,
                products=None,
        ):
            if tag is not None:
                self.tag = tag
            if request_time is not None:
                self.request_time = request_time
            if depot_id is not None:
                self.depot_id = depot_id
            if cart_id is not None:
                self.cart_id = cart_id
            if cart_version is not None:
                self.cart_version = cart_version

            self.check_request_flag = True

        def set_response_data(
                self, min_cart_cost=None, usage_count=None, products=None,
        ):
            if min_cart_cost is not None:
                self.min_cart_cost = min_cart_cost
            if usage_count is not None:
                self.usage_count = usage_count
            if products is not None:
                self.products = products

        def set_tag_retrieve_error_code(self, user_id, code):
            self.tag_retrieve_error_code[user_id] = code

        def set_fail_tag_check(self, code=None):
            if code is not None:
                self.fail_tag_check = code

        def times_tag_check(self):
            return mock_tag_check.times_called

        def flush(self):
            mock_tag_check.flush()

        def add_user_tag(self, tag_name, usage_count, *, user_id):
            if user_id not in tags_by_user:
                tags_by_user[user_id] = {}
            tags_by_user[user_id][tag_name] = usage_count

        def add_device_tag(self, tag_name, usage_count, *, device_id):
            if device_id not in tags_by_device_id:
                tags_by_device_id[device_id] = {}
            tags_by_device_id[device_id][tag_name] = usage_count

        def add_payment_id_tag(self, tag_name, usage_count, *, payment_id):
            if payment_id not in tags_by_payment_id:
                tags_by_payment_id[payment_id] = {}
            tags_by_payment_id[payment_id][tag_name] = usage_count

        def add_eats_id_tag(self, tag_name, usage_count, *, eats_id):
            if eats_id not in tags_by_eats_id:
                tags_by_eats_id[eats_id] = {}
            tags_by_eats_id[eats_id][tag_name] = usage_count

        def add_phone_id_tag(self, tag_name, usage_count, *, phone_id):
            if phone_id not in tags_by_phone_id:
                tags_by_phone_id[phone_id] = {}
            tags_by_phone_id[phone_id][tag_name] = usage_count

        def add_glue_tag(self, tag_name, usage_count, *, user_id):
            if user_id not in tags_by_glue:
                tags_by_glue[user_id] = {}
            tags_by_glue[user_id][tag_name] = usage_count

        def update_times_called(self):
            return mock_update_subscription.times_called

        def increment_times_called(self):
            return mock_tag_increment.times_called

        @property
        def retrieve_v2_times_called(self):
            return mock_marketing_retrieve_v2.times_called

    @mockserver.json_handler(
        '/grocery-marketing/internal/v1/marketing/v2/tag/retrieve',
    )
    def mock_marketing_retrieve_v2(request):
        tag_name = request.json['tag']
        payment_id = request.json.get('payment_id')
        user_id = request.json.get('yandex_uid')
        device_id = request.json.get('appmetrica_device_id')
        eats_id = request.json.get('eats_id')
        phone_id = request.json.get('personal_phone_id')

        if user_id in context.tag_retrieve_error_code:
            mockserver.make_response(
                json.dumps({'code': 'NO_CODE', 'message': 'error-message'}),
                context.tag_retrieve_error_code[user_id],
            )

        device_usage_count = None
        usage_count = None
        usage_count_glue = None
        if (user_id in tags_by_user) and (tag_name in tags_by_user[user_id]):
            usage_count = tags_by_user[user_id][tag_name]
        if (user_id in tags_by_glue) and (tag_name in tags_by_glue[user_id]):
            usage_count_glue = tags_by_glue[user_id][tag_name]
        if (device_id in tags_by_device_id) and (
                tag_name in tags_by_device_id[device_id]
        ):
            device_usage_count = tags_by_device_id[device_id][tag_name]
        json_response = {}
        if device_usage_count is not None:
            json_response[
                'appmetrica_device_id_usage_count'
            ] = device_usage_count
        if usage_count is not None:
            json_response['usage_count_according_to_yandex_uid'] = usage_count
            if usage_count_glue is not None:
                json_response['usage_count'] = usage_count + usage_count_glue
                json_response[
                    'usage_count_according_to_glue'
                ] = usage_count_glue
            else:
                json_response['usage_count'] = usage_count
        if (
                payment_id in tags_by_payment_id
                and tag_name in tags_by_payment_id[payment_id]
        ):
            json_response['payment_id_usage_count'] = tags_by_payment_id[
                payment_id
            ][tag_name]
        if eats_id in tags_by_eats_id and tag_name in tags_by_eats_id[eats_id]:
            json_response['eats_id_usage_count'] = tags_by_eats_id[eats_id][
                tag_name
            ]
        if (
                phone_id in tags_by_phone_id
                and tag_name in tags_by_phone_id[phone_id]
        ):
            json_response['personal_phone_id_usage_count'] = tags_by_phone_id[
                phone_id
            ][tag_name]
        return mockserver.make_response(json=json_response, status=200)

    @mockserver.json_handler(
        '/grocery-marketing/internal/v1/marketing/v1/tag/check',
    )
    def mock_tag_check(request):
        request = request.json

        if context.check_request_flag:
            assert request['kind'] == 'promocode'
            if context.tag is not None:
                assert request['tag'] == context.tag
            if context.depot_id is not None:
                assert request['depot_id'] == context.depot_id
            if context.cart_id is not None:
                assert request['cart_id'] == context.cart_id
            if context.cart_version is not None:
                assert request['cart_version'] == context.cart_version

        if context.fail_tag_check is None:
            response = {}
            if context.min_cart_cost is not None:
                response['min_cart_cost'] = context.min_cart_cost
            if context.products is not None:
                response['products'] = context.products
            if context.usage_count is not None:
                response['usage_count'] = context.usage_count
            return response

        return mockserver.make_response('', context.fail_tag_check)

    @mockserver.json_handler(
        '/grocery-marketing/internal/v1/marketing/v1/'
        'coming-soon/update-subscription',
    )
    def mock_update_subscription(request):
        if context.check_request_flag:
            assert request is not None
        return mockserver.make_response()

    context = Context()

    @mockserver.json_handler(
        '/grocery-marketing/internal/v1/marketing/v1/tag/increment',
    )
    def mock_tag_increment(request):
        if context.check_request_flag:
            assert request is not None
        return mockserver.make_response(status=200)

    context = Context()

    return context
