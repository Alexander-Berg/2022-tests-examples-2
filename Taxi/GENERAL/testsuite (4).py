from copy import deepcopy

from ._default import params as default_params


_MOCKSERVER_URL = 'http://@@MOCKSERVER@@'


params = deepcopy(default_params)


params['fastcgi.conf'].update(
    {
        'log_level': 'DEBUG',
        'highload_log_level': 'DEBUG',
        'exp3_cache_path': '/var/tmp/cache/yandex/exp3@@WORKER_SUFFIX@@',
        'tags_cache_path': '/var/tmp/cache/yandex/tags@@WORKER_SUFFIX@@',
        'work_pool_size': 10,
        'async_pool_size': 10,
        'tigraph_base_url': _MOCKSERVER_URL + '/tigraph/',
        'tigraph_adjust_base_url': _MOCKSERVER_URL + '/tigraph/',
        'router_tigraph_url': _MOCKSERVER_URL + '/tigraph-router/',
        'router_yamaps_url': _MOCKSERVER_URL + '/maps-router',
        'driver_ratings_base_url': _MOCKSERVER_URL + '/driver_ratings',
        'tags_base_url': _MOCKSERVER_URL + '/tags',
        'driver_tags_base_url': _MOCKSERVER_URL + '/driver_tags',
        'tags_topics_base_url': _MOCKSERVER_URL + '/tags-topics',
        'communications_base_url': _MOCKSERVER_URL + '/communications',
        'ucommunications_base_url': _MOCKSERVER_URL + '/ucommunications',
        'driver_eta_base_url': _MOCKSERVER_URL + '/driver-eta',
        'driver_status_base_url': _MOCKSERVER_URL + '/driver-status',
        'driver_freeze_base_url': _MOCKSERVER_URL + '/driver-freeze',
        'driver_categories_base_url': (
            _MOCKSERVER_URL + '/driver-categories-api'
        ),
        'configs_base_url': _MOCKSERVER_URL + '/configs-service',
        'sandbox_jams_path': '/usr/share/yandex/taxi/jams-original-test/',
        'mds_jams_path': '/usr/share/yandex/taxi/jams-original-test/',
        'cargo_claims_base_url': _MOCKSERVER_URL + '/cargo-claims',
        'api_proxy_base_url': _MOCKSERVER_URL + '/api-proxy',
        'ridehistory_base_url': _MOCKSERVER_URL + '/ridehistory',
    },
)
