from copy import deepcopy

from ._default import params as default_params


params = deepcopy(default_params)


params['fastcgi.conf'].update(
    {
        'log_level': 'DEBUG',
        'highload_log_level': 'DEBUG',
        'work_pool_size': 32,
        'async_pool_size': 32,
        'tigraph_base_url': 'http://graph.taxi.tst.yandex.net',
        'tigraph_adjust_base_url': 'http://yaga-adjust.taxi.tst.yandex.net',
        'router_tigraph_url': 'http://graph.taxi.tst.yandex.net',
        'driver_ratings_base_url': 'http://driver-ratings.taxi.tst.yandex.net',
        'tags_base_url': 'http://tags.taxi.tst.yandex.net',
        'driver_tags_base_url': 'http://driver-tags.taxi.tst.yandex.net',
        'tags_topics_base_url': 'http://tags-topics.taxi.tst.yandex.net',
        'communications_base_url': 'http://communications.taxi.tst.yandex.net',
        'ucommunications_base_url': (
            'http://ucommunications.taxi.tst.yandex.net'
        ),
        'driver_eta_base_url': 'http://driver-eta.taxi.tst.yandex.net',
        'driver_status_base_url': 'http://driver-status.taxi.tst.yandex.net',
        'driver_freeze_base_url': 'http://driver-freeze.taxi.tst.yandex.net',
        'driver_categories_base_url': (
            'http://driver-categories-api.taxi.tst.yandex.net'
        ),
        'configs_base_url': 'http://configs.taxi.tst.yandex.net',
        'cargo_claims_base_url': 'http://cargo-claims.taxi.tst.yandex.net',
        'api_proxy_base_url': 'http://api-proxy.taxi.tst.yandex.net',
        'ridehistory_base_url': 'http://ridehistory.taxi.tst.yandex.net',
    },
)
