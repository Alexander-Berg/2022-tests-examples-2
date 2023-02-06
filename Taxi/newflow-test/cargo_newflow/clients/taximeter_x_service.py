from .base import BaseClient


class TaximeterXServiceClient(BaseClient):
    _base_url = 'https://taximeter-xservice.taxi.tst.yandex.net/'
    _tvm_id = '2001830'

    def change_status(self, *, alias_id, park_id, driver_id, reason, status):
        return self._perform_post(
            'utils/order/change_status',
            params={'origin': 'dispatch'},
            json={
                'db': park_id,
                'order_alias_id': alias_id,
                'driver': driver_id,
                'reason': reason,
                'status': status,
            },
            verify=False,
        )
