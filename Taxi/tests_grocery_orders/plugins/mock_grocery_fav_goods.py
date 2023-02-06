import pytest


@pytest.fixture(name='grocery_fav_goods')
def mock_grocery_fav_goods(mockserver):
    class Context:
        def __init__(self):
            self.expected_yandex_uid = None
            self.expected_product_ids = None

        def setup_request_checking(self, yandex_uid=None, product_ids=None):
            if yandex_uid is not None:
                self.expected_yandex_uid = yandex_uid
            if product_ids is not None:
                self.expected_product_ids = product_ids

        @property
        def times_called(self):
            return mock_recent_goods_add.times_called

    context = Context()

    @mockserver.json_handler('/grocery-fav-goods/internal/v1/recent-goods/add')
    def mock_recent_goods_add(request):
        if context.expected_yandex_uid is not None:
            assert (
                request.headers['X-Yandex-UID'] == context.expected_yandex_uid
            )
        if context.expected_product_ids is not None:
            assert sorted(request.json['product_ids']) == sorted(
                context.expected_product_ids,
            )

        return {}

    return context
