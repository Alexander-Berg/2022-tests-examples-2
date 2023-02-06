from copy import deepcopy

from ._default import params as default_params


params = deepcopy(default_params)

_MOCKSERVER_URL = 'http://@@MOCKSERVER@@'

params['fastcgi.conf'].update(
    {
        'log_level': 'DEBUG',
        'highload_log_level': 'DEBUG',
        'archive_base_url': _MOCKSERVER_URL + '/archive-api',
        'order_archive_base_url': _MOCKSERVER_URL + '/order-archive',
        'stq_agent_base_url': _MOCKSERVER_URL + '/stq-agent',
        'bulk_pool_size': 3,
        'push_wanted_pool_size': 5,
        'work_pool_size': 5,
        'write_pool_size': 3,
        'async_pool_size': 10,
    },
)
