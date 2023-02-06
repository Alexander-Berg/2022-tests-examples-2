from copy import deepcopy

from ._default import params as default_params


params = deepcopy(default_params)

params['fastcgi.conf'].update(
    {
        'log_level': 'DEBUG',
        'yt_environment': 'testing',
        'replication_base_url': 'http://replication.taxi.tst.yandex.net',
        'archive_base_url': 'http://archive-api.taxi.tst.yandex.net',
        'order_archive_base_url': 'http://order-archive.taxi.tst.yandex.net',
    },
)
