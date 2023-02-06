from copy import deepcopy

from ._default import params as default_params


params = deepcopy(default_params)

MOCKSERVER_URL = 'http://@@MOCKSERVER@@'

params['fastcgi.conf'].update(
    {
        'log_level': 'DEBUG',
        'work_pool_size': 16,
        'work_read_pool_size': 16,
        'async_pool_size': 8,
        'notification_push_pool_size': 16,
        'notification_push_pool_queue_size': 16,
        'test_mode_enabled': 1,
        'xiva_base_url': MOCKSERVER_URL + '/xiva',
        'device_notify_base_url': MOCKSERVER_URL + '/device-notify',
        'territories_base_url': MOCKSERVER_URL + '/territories',
        'selfreg_base_url': MOCKSERVER_URL + '/selfreg',
        'client_notify_base_url': MOCKSERVER_URL + '/client_notify',
    },
)
