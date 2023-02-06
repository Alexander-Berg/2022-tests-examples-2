from copy import deepcopy

from ._default import params as default_params


params = deepcopy(default_params)

_MOCKSERVER_URL = 'http://@@MOCKSERVER@@'

params['fastcgi.conf'].update(
    {
        'env_name': 'testsuite',
        'log_level': 'DEBUG',
        'highload_log_level': 'DEBUG',
        'work_pool_size': 10,
        'async_pool_size': 10,
        'etags_cache_path': (
            '/var/tmp/cache/yandex/reposition_etags@@WORKER_SUFFIX@@'
        ),
        'router_here_url': _MOCKSERVER_URL + '/router_here',
        'router_here_matrix_url': _MOCKSERVER_URL + '/router_here',
        'experiments_base_url': _MOCKSERVER_URL + '/experiments',
        'conductor_base_url': _MOCKSERVER_URL + '/conductor',
        'heatmap_storage_base_url': _MOCKSERVER_URL + '/heatmap-storage',
        'cron_enabled': 'false',
        'driver_protocol_base_url': _MOCKSERVER_URL + '/driver-protocol',
        'territories_base_url': _MOCKSERVER_URL + '/territories',
    },
)
