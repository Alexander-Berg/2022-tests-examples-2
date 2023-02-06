from copy import deepcopy

from ._default import params as default_params


params = deepcopy(default_params)
MOCKSERVER_URL = 'http://@@MOCKSERVER@@'


params['fastcgi.conf'].update(
    {
        'log_level': 'DEBUG',
        'tracing_reporter': 'noop',
        'work_pool_threads': 8,
        'polling_pool_threads': 8,
        'high_js_pool_threads': 2,
        'async_pool_size': 16,
        'signature_pool_threads': 2,
        'events_pool_threads': 8,
        'eda_pool_threads': 1,
        'mlaas_base_url': MOCKSERVER_URL + '/mlaas',
        'user_api_base_url': MOCKSERVER_URL + '/user-api',
        'afs_base_url': MOCKSERVER_URL + '/antifraud',
        'uafs_base_url': MOCKSERVER_URL + '/uantifraud',
        'tg_notify_direct_url': MOCKSERVER_URL + '/afs_tg_direct',
        'tg_notify_inner_url': MOCKSERVER_URL + '/afs_tg_inner',
        'tg_base_url': MOCKSERVER_URL + '/afs_tg_base',
        'driver_profiles_base_url': MOCKSERVER_URL + '/driver_profile_base',
        'rt_xaron_base_url': MOCKSERVER_URL + '/rt_xaron_base',
        'passenger_tags_base_url': MOCKSERVER_URL + '/passenger-tags',
        'test_mode_enabled': 1,
        'geobase_config': '/etc/yandex/geobase/geobase6.conf',
    },
)
