from copy import deepcopy

from ._default import params as default_params


params = deepcopy(default_params)


params['fastcgi.conf'].update(
    {
        'log_level': 'DEBUG',
        'work_pool_threads': 32,
        'polling_pool_threads': 32,
        'high_js_pool_threads': 4,
        'signature_pool_threads': 4,
        'events_pool_threads': 32,
        'eda_pool_threads': 1,
        'async_pool_size': 64,
        'mlaas_base_url': 'http://ml.taxi.tst.yandex.net',
        'user_api_base_url': 'http://user-api.taxi.tst.yandex.net',
        'afs_base_url': 'http://antifraud.taxi.tst.yandex.net',
        'uafs_base_url': 'http://uantifraud.taxi.tst.yandex.net',
        'tg_base_url': 'http://antifraud-py.taxi.tst.yandex.net',
        'driver_profiles_base_url': (
            'http://driver-profiles.taxi.tst.yandex.net'
        ),
        'rt_xaron_base_url': (
            'http://fury-rtxaron-responder-test.search.yandex.net:14000'
        ),
        'passenger_tags_base_url': 'http://passenger-tags.taxi.tst.yandex.net',
    },
)
