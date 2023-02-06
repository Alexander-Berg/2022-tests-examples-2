from copy import deepcopy

from ._default import params as default_params


params = deepcopy(default_params)


params['fastcgi.conf'].update(
    {
        'log_level': 'INFO',
        'work_pool_threads': 10,
        'logbroker_client_id': 'taxi_geofence_nonexisting',
        'logbroker_log_type': 'tracker-statuses-nonexistin-log',
        'logbroker_balancer_hostname': '127.0.0.1',
        'logbroker_force_disabled': '1',
    },
)
