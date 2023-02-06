import pytest


@pytest.fixture(name='grocery_fav_goods', autouse=True)
def mock_grocery_fav_goods(mockserver):
    class Context:
        def __init__(self):
            self.expected_yandex_uid = None
            self.raise_timeout = {}
            self.error_status = {}
            self.response_product_ids = []
            self.favorites_by_uid = {}

        def setup_request_checking(self, yandex_uid):
            self.expected_yandex_uid = yandex_uid

        def set_to_raise_timeout(self, handler_name):
            self.raise_timeout[handler_name] = True

        def set_error_status(self, handler_name, error_status):
            self.error_status[handler_name] = error_status

        def set_response_product_ids(self, product_ids):
            self.response_product_ids = product_ids

        def add_favorite(self, yandex_uid, product_id, is_favorite=True):
            if yandex_uid not in self.favorites_by_uid:
                self.favorites_by_uid[yandex_uid] = []
            self.favorites_by_uid[yandex_uid].append(
                {'product_id': product_id, 'is_favorite': is_favorite},
            )

        @property
        # pylint: disable=invalid-name
        def recent_goods_check_presence_times_called(self):
            return mock_recent_goods_check_presence.times_called

        @property
        def recent_goods_get_times_called(self):
            return mock_recent_goods_get.times_called

    context = Context()

    def check_request(request):
        if context.expected_yandex_uid is not None:
            assert (
                request.headers['X-Yandex-UID'] == context.expected_yandex_uid
            )

    def handle_request(request, response, handler_name):
        check_request(request)
        if context.raise_timeout.get(handler_name, False):
            raise mockserver.TimeoutError()
        if context.error_status.get(handler_name, None) is not None:
            return mockserver.make_response(
                status=context.error_status[handler_name],
            )
        return response

    @mockserver.json_handler(
        '/grocery-fav-goods/internal/v1/recent-goods/check-presence',
    )
    # pylint: disable=invalid-name
    def mock_recent_goods_check_presence(request):
        return handle_request(
            request=request,
            response={'presented': bool(context.response_product_ids)},
            handler_name='recent-goods/check-presence',
        )

    @mockserver.json_handler('/grocery-fav-goods/internal/v1/recent-goods/get')
    def mock_recent_goods_get(request):
        return handle_request(
            request=request,
            response={'product_ids': context.response_product_ids},
            handler_name='recent-goods/get',
        )

    @mockserver.json_handler('/grocery-fav-goods/internal/v1/favorites/list')
    def _mock_favorites_list(request):
        yandex_uid = request.headers.get('X-Yandex-UID')
        if yandex_uid not in context.favorites_by_uid:
            return {'products': []}
        return {'products': context.favorites_by_uid[yandex_uid]}

    @mockserver.json_handler(
        '/grocery-fav-goods/internal/v1/favorites/selected',
    )
    def _mock_favorites_selected(request):
        yandex_uid = request.headers.get('X-Yandex-UID')
        if yandex_uid not in context.favorites_by_uid:
            return {'products': []}
        product_ids = request.json.get('product_ids')
        response_products = []
        for fav_product in context.favorites_by_uid[yandex_uid]:
            if fav_product['product_id'] in product_ids:
                response_products.append(fav_product)
        return {'products': response_products}

    return context
