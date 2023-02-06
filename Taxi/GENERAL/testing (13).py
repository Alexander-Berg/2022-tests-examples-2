from copy import deepcopy

from ._default import params as default_params


params = deepcopy(default_params)


params['fastcgi.conf'].update(
    {
        'log_level': 'INFO',
        'logbroker_client_id': 'taxi_geofence_test',
        'logbroker_log_type': 'tracker-positions-testing-log',
        'events_file_directory': '/var/cache/yandex/taxi-geofence-stats',
    },
)
