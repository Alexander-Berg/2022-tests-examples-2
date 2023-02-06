import configparser
import pathlib

import requests

TAXI_DEVTOOLS_CONFIG = pathlib.Path('~/.taxi-devtools')


class BaseError(Exception):
    """Base class for exceptions of this module."""


class ConfigNotFound(BaseError):
    pass


class EntityNotFoundError(BaseError):
    pass


class TariffEditorClient:
    _base_user_urls = {
        'testing': 'https://tariff-editor.taxi.tst.yandex-team.ru/',
        'unstable': 'https://tariff-editor-unstable.taxi.tst.yandex-team.ru/',
    }
    _base_urls = {
        'testing': 'https://tariff-editor.taxi.tst.yandex-team.ru/api-t/',
        'unstable': (
            'https://tariff-editor-unstable.taxi.tst.yandex-team.ru/api-u/'
        ),
    }

    def __init__(self, token, environment='testing'):
        self._token = token
        self._environment = environment
        self._base_url = self._base_urls[environment]
        self._base_user_url = self._base_user_urls[environment]

    @property
    def environment(self):
        return self._environment

    def get_config_edit_url(self, config: str):
        return self._base_user_url + f'dev/configs/edit/{config}'

    def get_config(self, name: str):
        response = self._request(f'admin/configs-admin/v1/configs/{name}/')
        return response.json()['value']

    def list_configs(self):
        response = self._request(f'admin/configs-admin/v1/configs/list/')
        return response.json()

    def retrieve_order_entity(self, order_id, entity, object_hook=None):
        response = self._request(
            'admin/admin-orders/v1/raw_objects/get/',
            params={'order_id': order_id, 'objects': entity},
        )
        data = response.json(object_hook=object_hook)
        if entity not in data:
            raise EntityNotFoundError(f'{order_id}: {entity} not found')
        return data[entity]

    def driver_satisfy(self, request):
        response = self._post(
            'admin/candidates/satisfy/',
            json=request,
        )
        return response.json()

    def get_allias_id(self, taxi_order_id):
        response = self._request(
            'payments/orders_info/',
            json={
                'order_id': taxi_order_id
                },
        )
        return response.json()['orders'][0]['alias_id']

    def order_satisfy(self, request):
        response = self._post(
            'admin/candidates/order-satisfy/',
            json=request,
        )
        return response.json()

    def _post(self, path, json=None):
        response = requests.post(
            self._build_url(path),
            headers={'Authorization': f'OAuth {self._token}'},
            json=json,
            # TODO: yandex cert
            verify=False,
        )
        response.raise_for_status()
        content_type = response.headers.get('content-type')
        if content_type:
            content_type = content_type.split(';')[0]
        if content_type != 'application/json':
            raise RuntimeError(f'Invalid content type {content_type!r}')
        return response

    def _request(self, path, params=None, json=None):
        response = requests.get(
            self._build_url(path),
            headers={'Authorization': f'OAuth {self._token}'},
            params=params,
            json=json,
            # TODO: yandex cert
            verify=False,
        )
        if response.status_code == 404:
            raise ConfigNotFound
        response.raise_for_status()
        content_type = response.headers.get('content-type')
        if content_type:
            content_type = content_type.split(';')[0]
        if content_type != 'application/json':
            raise RuntimeError(f'Invalid content type {content_type!r}')
        return response

    def _build_url(self, path: str):
        return self._base_url + path


def load_config(appname='uservices-service-rules'):
    config = configparser.ConfigParser()
    config['default'] = {}
    config[appname] = {}
    config.read(TAXI_DEVTOOLS_CONFIG.expanduser())
    merged = {**config['default'], **config[appname]}
    return merged


def create_tariff_editor_client():
    config = load_config()
    if 'tariff-editor-token' not in config:
        raise RuntimeError(
            f'No tariff-editor-token found in {TAXI_DEVTOOLS_CONFIG}, '
            f'visit https://wiki.yandex-team.ru/taxi/backend/devtools/',
        )
    return TariffEditorClient(config['tariff-editor-token'], 'testing')

TARIFF_EDITOR_CLIENT = create_tariff_editor_client()

if __name__ == '__main__':
    TariffEditorClient()
