from . import base


class CargoCorpClient(base.BaseClient):
    _base_url = 'http://cargo-corp.taxi.tst.yandex.net'
    _tvm_id = '2027868'

    def client_info(self, corp_client_id):
        return self._perform_get(
            '/internal/cargo-corp/v1/client/info',
            headers={'X-B2B-Client-Id': corp_client_id},
        )

    def get_corp_client_storage(self, corp_client_id):
        try:
            response = self.client_info(corp_client_id)
        except base.HttpNotFoundError:
            return 'taxi'
        else:
            return 'cargo'
        return 'taxi'
