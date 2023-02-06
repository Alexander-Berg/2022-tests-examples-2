from copy import deepcopy

from ._default import params as default_params


params = deepcopy(default_params)

MOCKSERVER_URL = 'http://@@MOCKSERVER@@'

params['fastcgi.conf'].update(
    {
        'log_level': 'DEBUG',
        'highload_log_level': 'DEBUG',
        'work_pool_size': 10,
        'async_pool_size': 10,
        'territories_base_url': MOCKSERVER_URL + '/territories',
        'mds_upload_host': MOCKSERVER_URL + '/mds-int-host:1111',
        'taximeter_mds_get_url': (
            'https://storage.mds.yandex.net/get-taximeter/'
        ),
        'dadata_base_url': MOCKSERVER_URL + '/dadata',
        'yandex_enviroment': 'test',
        'yandex_team_enviroment': 'test',
        'driver_ratings_codegen_base_url': MOCKSERVER_URL + '/driver-ratings',
        'experiments_base_url': MOCKSERVER_URL + '/experiments',
        'ext_drivematics_codegen_base_url': (
            MOCKSERVER_URL + '/ext_drivematics_codegen'
        ),
        'driver_profiles_cache_path': '',
        'cars_cache_path': '',
    },
)
