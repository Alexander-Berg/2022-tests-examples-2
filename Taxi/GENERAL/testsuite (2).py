from copy import deepcopy

from ._default import params as default_params


params = deepcopy(default_params)

_MOCKSERVER_URL = 'http://@@MOCKSERVER@@'

params['fastcgi.conf'].update(
    {
        'log_level': 'DEBUG',
        'work_pool_threads': 10,
        'restore_pool_threads': 10,
        'yt_pool_threads': 10,
        'replication_base_url': _MOCKSERVER_URL + '/replication',
        'archive_base_url': _MOCKSERVER_URL + '/archive-api',
        'order_archive_base_url': _MOCKSERVER_URL + '/order-archive',
    },
)
