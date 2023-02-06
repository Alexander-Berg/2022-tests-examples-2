from copy import deepcopy

from ._default import params as default_params


params = deepcopy(default_params)

params['fastcgi.conf'].update(
    {
        'log_level': 'DEBUG',
        'highload_log_level': 'DEBUG',
        'work_pool_size': 32,
        'async_pool_size': 32,
        'territories_base_url': 'http://territories.taxi.tst.yandex.net',
        'mds_upload_host': 'http://storage-int.mdst.yandex.net:1111',
        'taximeter_mds_get_url': (
            'https://storage.mdst.yandex.net/get-taximeter/'
        ),
        'dadata_base_url': 'https://suggestions.dadata.ru',
        'yandex_enviroment': 'test',
        'yandex_team_enviroment': 'prod',
        'driver_ratings_codegen_base_url': (
            'http://driver-ratings.taxi.tst.yandex.net'
        ),
        'experiments_base_url': 'http://experiments.taxi.tst.yandex.net',
        'exp3_cache_path': '/var/cache/yandex/exp3',
        'ext_drivematics_codegen_base_url': (
            'https://testing.leasing-cabinet.carsharing.yandex.net'
        ),
    },
)
