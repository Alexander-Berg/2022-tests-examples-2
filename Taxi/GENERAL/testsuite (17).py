from copy import deepcopy

from ._default import params as default_params

params = deepcopy(default_params)

MOCKSERVER_URL = 'http://@@MOCKSERVER@@'

params['fastcgi.conf'].update(
    {
        'log_level': 'DEBUG',
        'async_pool_size': 8,
        'http_pool_size': 1,
        'test_mode_enabled': 1,
        'taximeter_core_base_url': MOCKSERVER_URL + '/taximeter-core',
        'driver_protocol_base_url': MOCKSERVER_URL + '/driver-protocol',
        'cars_catalog_base_url': MOCKSERVER_URL + '/cars-catalog',
        'experiments_base_url': MOCKSERVER_URL + '/experiments',
        'tags_base_url': MOCKSERVER_URL + '/tags',
        'conductor_base_url': MOCKSERVER_URL + '/conductor',
    },
)
