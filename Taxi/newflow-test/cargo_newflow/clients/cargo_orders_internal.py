import typing

from .base import BaseClient


class CargoOrdersInternalClient(BaseClient):
    _base_url = 'http://cargo-orders.taxi.tst.yandex.net'
    _tvm_id = '2020955'

    def performers_bulk_info(self, orders_ids: typing.List[str]):
        return self._perform_post(
            '/v1/performers/bulk-info', json={'orders_ids': orders_ids},
        )

    def get_performer_info(self, order_id: str):
        response = self.performers_bulk_info([order_id])
        return response['performers'][0]

    def _get_headers(self, headers):
        return {**super()._get_headers(headers), 'Accept-Language': 'ru'}
