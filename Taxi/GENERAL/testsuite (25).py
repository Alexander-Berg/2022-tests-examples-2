from copy import deepcopy

from ._default import params as default_params


_MOCKSERVER_URL = 'http://@@MOCKSERVER@@'


params = deepcopy(default_params)


params['fastcgi.conf'].update(
    {
        'work_pool_size': 10,
        'write_work_pool_size': 10,
        'async_pool_size': 10,
        'user_position_path': '',
    },
)
