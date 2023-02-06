from copy import deepcopy

from ._default import params as default_params


params = deepcopy(default_params)

params['fastcgi.conf'].update(
    {
        'log_level': 'INFO',
        'yt_environment': 'testing',
        'highload_log_level': 'INFO',
        'work_pool_size': 32,
        'driver_check_pool_size': 16,
        'driver_money_pool_size': 16,
        'subventions_pool_size': 16,
        'parks_base_url': 'http://parks.taxi.tst.yandex.net',
        'taximeter_core_base_url': 'http://taximeter-core.taxi.tst.yandex.net',
        'driver_protocol_base_url': (
            'http://driver-protocol.taxi.tst.yandex.net'
        ),
        'dispatch_settings_base_url': (
            'http://dispatch-settings.taxi.tst.yandex.net'
        ),
        'selfemployed_base_url': 'http://selfemployed.taxi.tst.yandex.net',
        'territories_base_url': 'http://territories.taxi.tst.yandex.net',
        'tags_base_url': 'http://tags.taxi.tst.yandex.net',
        'geotracks_base_url': (
            'http://driver-trackstory.taxi.tst.yandex.net/legacy'
        ),
        'stq_agent_base_url': 'http://stq-agent.taxi.tst.yandex.net',
        'unique_drivers_base_url': 'http://unique-drivers.taxi.tst.yandex.net',
        'billing_reports_base_url': (
            'http://billing-reports.taxi.tst.yandex.net'
        ),
        'billing_accounts_base_url': (
            'http://billing-accounts.taxi.tst.yandex.net'
        ),
        'driver_status_base_url': 'http://driver-status.taxi.tst.yandex.net',
        'tracks_path': '/var/cache/yandex/taxi-driver-protocol',
        'driver_photos_base_url': 'http://driver-photos.taxi.tst.yandex.net',
        'afs_base_url': 'http://antifraud.taxi.tst.yandex.net',
        'uafs_base_url': 'http://uantifraud.taxi.tst.yandex.net',
        'billing_bank_orders_base_url': (
            'http://billing-bank-orders.taxi.tst.yandex.net'
        ),
    },
)
