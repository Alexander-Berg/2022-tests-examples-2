from copy import deepcopy

from ._default import params as default_params


params = deepcopy(default_params)

params['fastcgi.conf'].update(
    {
        'log_level': 'DEBUG',
        'highload_log_level': 'DEBUG',
        'work_pool_size': 32,
        'async_pool_size': 32,
        'yandex_enviroment': 'test',
        'yandex_team_enviroment': 'prod',
        # clients
        'dispatcher_access_control_base_url': (
            'http://dispatcher-access-control.taxi.tst.yandex.net'
        ),
        'driver_protocol_base_url': (
            'http://driver-protocol.taxi.tst.yandex.net'
        ),
        'parks_base_url': 'http://parks.taxi.tst.yandex.net',
    },
)
