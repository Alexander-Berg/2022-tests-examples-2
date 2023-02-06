from copy import deepcopy

from ._default import params as default_params


params = deepcopy(default_params)

params['fastcgi.conf'][
    'dispatch_buffer_base_url'
] = 'http://dispatch-buffer.taxi.tst.yandex.net'
params['fastcgi.conf'][
    'ride_discounts_base_url'
] = 'http://ride-discounts.taxi.tst.yandex.net'

params['fastcgi.conf']['mlaas_base_url'] = 'http://ml.taxi.tst.yandex.net'
params['fastcgi.conf']['tags_base_url'] = 'http://tags.taxi.tst.yandex.net'
params['fastcgi.conf'][
    'passenger_tags_base_url'
] = 'http://passenger-tags.taxi.tst.yandex.net'
params['fastcgi.conf'][
    'archive_base_url'
] = 'http://archive-api.taxi.tst.yandex.net'
params['fastcgi.conf'][
    'order_archive_base_url'
] = 'http://order-archive.taxi.tst.yandex.net'
params['fastcgi.conf'][
    'stq_agent_base_url'
] = 'http://stq-agent.taxi.tst.yandex.net'
params['fastcgi.conf'][
    'territories_base_url'
] = 'http://territories.taxi.tst.yandex.net'
params['fastcgi.conf'][
    'cars_catalog_base_url'
] = 'http://cars-catalog.taxi.tst.yandex.net'
params['fastcgi.conf'][
    'user_api_base_url'
] = 'http://user-api.taxi.tst.yandex.net'
params['fastcgi.conf'][
    'selfemployed_base_url'
] = 'http://selfemployed.taxi.tst.yandex.net'

params['fastcgi.conf']['log_level'] = 'DEBUG'

params['fastcgi.conf'][
    'geotracks_base_url'
] = 'http://driver-trackstory.taxi.tst.yandex.net/legacy'

params['fastcgi.conf'][
    'pool_logger_path'
] = '/var/log/yandex/uploads/taxi-integration-api'
params['fastcgi.conf'][
    'ml_logger_path'
] = '/var/log/yandex/uploads/taxi-integration-api'
params['fastcgi.conf']['parks_base_url'] = 'http://parks.taxi.tst.yandex.net'
params['fastcgi.conf']['exp3_cache_path'] = '/var/cache/yandex/exp3'
params['fastcgi.conf']['vgw_api_url'] = 'http://vgw-api.taxi.tst.yandex.net'
params['fastcgi.conf']['afs_base_url'] = 'http://antifraud.taxi.tst.yandex.net'
params['fastcgi.conf'][
    'uafs_base_url'
] = 'http://uantifraud.taxi.tst.yandex.net'
params['fastcgi.conf'][
    'driver_ratings_codegen_base_url'
] = 'http://driver-ratings.taxi.tst.yandex.net'

params['fastcgi.conf'][
    'driver_profiles_base_url'
] = 'http://driver-profiles.taxi.tst.yandex.net'
