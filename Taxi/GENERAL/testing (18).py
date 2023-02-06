from copy import deepcopy

from ._default import params as default_params


params = deepcopy(default_params)

params['fastcgi.conf'].update(
    {
        'log_level': 'DEBUG',
        'work_pool_size': 32,
        'async_pool_size': 32,
        'parks_base_url': 'http://parks.taxi.tst.yandex.net',
        'driver_protocol_base_url': (
            'http://driver-protocol.taxi.tst.yandex.net'
        ),
        'protocol_base_url': 'http://taxi-protocol.taxi.tst.yandex.net',
    },
)
