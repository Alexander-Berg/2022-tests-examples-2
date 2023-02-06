from copy import deepcopy

from ._default import params as default_params


params = deepcopy(default_params)

params['fastcgi.conf'].update(
    {
        'log_level': 'DEBUG',
        'work_pool_size': 16,
        'work_read_pool_size': 16,
        'notification_push_pool_size': 16,
        'notification_push_pool_queue_size': 16,
        'device_notify_base_url': 'http://device-notify.taxi.tst.yandex.net',
        'territories_base_url': 'http://territories.taxi.tst.yandex.net',
        'selfreg_base_url': 'http://selfreg.taxi.tst.yandex.net',
        'client_notify_base_url': 'http://client-notify.taxi.tst.yandex.net',
    },
)
