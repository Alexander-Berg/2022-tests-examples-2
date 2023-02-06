from copy import deepcopy

from ._default import params as default_params


params = deepcopy(default_params)

_MOCKSERVER_URL = 'http://@@MOCKSERVER@@'

params['fastcgi.conf'].update(
    {
        'log_level': 'DEBUG',
        'highload_log_level': 'DEBUG',
        'work_pool_size': 10,
        'async_pool_size': 10,
    },
)
