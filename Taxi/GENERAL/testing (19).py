from copy import deepcopy

from ._default import params as default_params


params = deepcopy(default_params)

params['fastcgi.conf'].update(
    {
        'log_level': 'DEBUG',
        'env_name': 'testing',
        'work_pool_size': 32,
        'exp3_cache_path': '/var/cache/yandex/exp3',
        'experiments_base_url': 'http://experiments.taxi.tst.yandex.net',
        'userplaces_base_url': 'http://userplaces.taxi.tst.yandex.net',
        'routehistory_base_url': 'http://routehistory.taxi.tst.yandex.net',
        'pickup_points_manager_base_url': (
            'http://pickup-points-manager.taxi.tst.yandex.net'
        ),
    },
)
