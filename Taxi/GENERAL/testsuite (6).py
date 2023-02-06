from copy import deepcopy

from ._default import params as default_params


params = deepcopy(default_params)

MOCKSERVER_URL = 'http://@@MOCKSERVER@@'

params['fastcgi.conf'].update(
    {
        'log_level': 'DEBUG',
        'highload_log_level': 'DEBUG',
        'tracing_reporter': 'noop',
        'work_pool_size': 16,
        'driver_check_pool_size': 8,
        'polling_pool_size': 32,
        'driver_money_pool_size': 16,
        'subventions_pool_size': 16,
        'yt_pool_size': 8,
        'parks_base_url': MOCKSERVER_URL + '/parks',
        'taximeter_core_base_url': MOCKSERVER_URL + '/taximeter-core',
        'driver_protocol_base_url': MOCKSERVER_URL + '/driver-protocol',
        'experiments_base_url': MOCKSERVER_URL + '/experiments',
        'territories_base_url': MOCKSERVER_URL + '/territories',
        'selfemployed_base_url': MOCKSERVER_URL + '/selfemployed',
        'unique_drivers_base_url': MOCKSERVER_URL + '/unique-drivers',
        'geotracks_base_url': MOCKSERVER_URL + '/geotracks',
        'router_here_url': MOCKSERVER_URL + '/router_here',
        'router_here_matrix_url': MOCKSERVER_URL + '/router_here',
        'tags_base_url': MOCKSERVER_URL + '/tags',
        'stq_agent_base_url': MOCKSERVER_URL + '/stq-agent',
        'billing_reports_base_url': MOCKSERVER_URL + '/billing_reports',
        'billing_accounts_base_url': MOCKSERVER_URL + '/billing_accounts',
        'driver_status_base_url': MOCKSERVER_URL + '/driver-status',
        'dispatch_settings_base_url': MOCKSERVER_URL + '/dispatch-settings',
        'reposition_path': '',
        'tracks_path': './tracks-logs',
        'driver_photos_base_url': MOCKSERVER_URL + '/driver-photos',
        'afs_base_url': MOCKSERVER_URL + '/antifraud',
        'uafs_base_url': MOCKSERVER_URL + '/uantifraud',
        'billing_bank_orders_base_url': (
            MOCKSERVER_URL + '/billing-bank-orders'
        ),
    },
)
