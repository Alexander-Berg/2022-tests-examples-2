from copy import deepcopy

from ._default import params as default_params


params = deepcopy(default_params)


params['fastcgi.conf'].update(
    {
        'work_pool_size': 32,
        'async_pool_size': 32,
        'log_level': 'DEBUG',
        'highload_log_level': 'DEBUG',
    },
)
