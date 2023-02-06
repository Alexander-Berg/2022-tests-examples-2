from copy import deepcopy

from ._default import params as default_params


params = deepcopy(default_params)

_MOCKSERVER_URL = 'http://@@MOCKSERVER@@'

params['fastcgi.conf'].update(
    {
        'log_level': 'DEBUG',
        'work_pool_size': 10,
        'async_pool_size': 10,
        'parks_base_url': _MOCKSERVER_URL + '/parks',
        'driver_protocol_base_url': _MOCKSERVER_URL + '/driver-protocol',
        'protocol_base_url': _MOCKSERVER_URL + '/protocol',
    },
)
