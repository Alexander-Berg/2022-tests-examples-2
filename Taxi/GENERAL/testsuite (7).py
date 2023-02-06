from copy import deepcopy

from ._default import params as default_params


_MOCKSERVER_URL = 'http://@@MOCKSERVER@@'


params = deepcopy(default_params)


params['fastcgi.conf'].update(
    {
        'log_level': 'DEBUG',
        'highload_log_level': 'DEBUG',
        'work_pool_size': 10,
        'async_pool_size': 10,
        'stq_agent_base_url': _MOCKSERVER_URL + '/stq-agent',
    },
)
