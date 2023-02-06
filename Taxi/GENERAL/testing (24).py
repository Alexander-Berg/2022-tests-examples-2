from copy import deepcopy

from ._default import params as default_params


params = deepcopy(default_params)

params['fastcgi.conf'].update(
    {
        'env_name': 'testing',
        'log_level': 'DEBUG',
        'highload_log_level': 'DEBUG',
        'work_pool_size': 32,
        'async_pool_size': 32,
        'router_here_url': 'http://route.cit.api.here.com',
        'router_here_matrix_url': 'http://matrix.route.cit.api.here.com',
        'heatmap_storage_base_url': (
            'http://heatmap-storage.taxi.tst.yandex.net'
        ),
        'territories_base_url': 'http://territories.taxi.tst.yandex.net',
    },
)
