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
        'yandex_enviroment': 'test',
        'yandex_team_enviroment': 'test',
        # clients
        'dispatcher_access_control_base_url': (
            MOCKSERVER_URL + '/dispatcher-access-control'
        ),
        'driver_protocol_base_url': MOCKSERVER_URL + '/driver_protocol',
        'parks_base_url': MOCKSERVER_URL + '/parks',
    },
)
