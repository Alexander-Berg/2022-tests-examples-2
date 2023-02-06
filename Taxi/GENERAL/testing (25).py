from copy import deepcopy

from ._default import params as default_params


params = deepcopy(default_params)


params['fastcgi.conf'].update(
    {'work_pool_size': 32, 'write_work_pool_size': 32, 'async_pool_size': 32},
)
