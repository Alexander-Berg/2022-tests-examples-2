import pytest


@pytest.fixture(name='default_cargo_order_id')
def _default_cargo_order_id():
    return 'c8979166-e428-43be-8b37-5ea1c958debb'


@pytest.fixture(name='default_taxi_order_id')
def _default_taxi_order_id():
    return 'taxi'


def default_dbid_uuid():
    return {'dbid': 'park_id_1', 'uuid': 'driver_id_1'}


@pytest.fixture(name='default_dbid_uuid')
def _default_dbid_uuid():
    return default_dbid_uuid()


@pytest.fixture(name='performer_request_property')
def _performer_request_property(load_json):
    def handler(path='cargo-orders/performer_default.json'):
        return load_json(path)

    return handler
