from copy import deepcopy

from ._default import params as default_params


params = deepcopy(default_params)

params['fastcgi.conf'].update(
    {
        'log_level': 'DEBUG',
        'highload_log_level': 'DEBUG',
        'archive_base_url': 'http://archive-api.taxi.tst.yandex.net',
        'order_archive_base_url': 'http://order-archive.taxi.tst.yandex.net',
        'stq_agent_base_url': 'http://stq-agent.taxi.tst.yandex.net',
        'bulk_pool_size': 8,
        'push_wanted_pool_size': 16,
        'work_pool_size': 16,
        'write_pool_size': 8,
        'async_pool_size': 32,
        'yt_environment': 'testing',
    },
)
