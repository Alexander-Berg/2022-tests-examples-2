from .base import BaseClient


class CargoMiscClient(BaseClient):
    _base_url = 'http://cargo-misc.taxi.tst.yandex.net'
    _tvm_id = '2017967'

    def create_profile(self, json):
        return self._perform_post('/couriers/v1/create', json=json)
