from .base import BaseClient


class IntapiClient(BaseClient):
    _base_url = 'http://int-authproxy.taxi.tst.yandex.net/'
    _tvm_id = '2020096'

    def order_search(self, order_id):
        return self._perform_post(
            'v1/orders/search',
            json={'orderid': order_id, 'sourceid': 'cargo'},
        )
