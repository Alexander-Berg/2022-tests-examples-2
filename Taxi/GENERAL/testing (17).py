from copy import deepcopy

from ._default import params as default_params

params = deepcopy(default_params)


params['fastcgi.conf'].update(
    {
        'log_level': 'INFO',
        'destinations_logbroker_path': '/var/cache/yandex/taxi-labor',
        'env_name': 'testing',
        'driver_weariness_path': '/var/cache/yandex/taxi-labor-uploads',
        'cars_catalog_base_url': 'http://cars-catalog.taxi.tst.yandex.net',
        'driver_supply_hours_path': '/var/cache/yandex/taxi-labor-uploads',
        'logbroker_ml_client_id': 'taxi-ml-test@prod@taxi-ml-test',
        'logbroker_pins_ident': 'taxi-ml-test@prod',
        'tags_base_url': 'http://tags.taxi.tst.yandex.net',
    },
)
