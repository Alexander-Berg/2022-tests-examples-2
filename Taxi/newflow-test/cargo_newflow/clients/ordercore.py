from .base import BaseClient


class OrderCoreClient(BaseClient):

    _base_url = 'http://order-core.taxi.tst.yandex.net/'
    _tvm_id = '2015591'

    def get_order_fields(self, order_id, fields):
        return self._perform_post(
            '/v1/tc/order-fields',
            json={'order_id': order_id, 'fields': fields},
        )
