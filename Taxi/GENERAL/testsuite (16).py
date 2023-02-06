from copy import deepcopy

from ._default import params as default_params


params = deepcopy(default_params)

MOCKSERVER_URL = 'http://@@MOCKSERVER@@'

params['jobs.json'].update(
    {
        'TRACKER_BASE_URL': MOCKSERVER_URL + '/tracker',
        'GEOTRACKS_BASE_URL': MOCKSERVER_URL + 'geotracks',
        'DRIVER_PROTOCOL_URL': MOCKSERVER_URL + '/driver_protocol',
        'SURGE_BASE_URL': MOCKSERVER_URL + '/surger',
        'CONFIGS_URL': MOCKSERVER_URL + '/configs-service',
        'GEOAREAS_BASE_URL': MOCKSERVER_URL + '/geoareas',
        'GRAPHITE_PORT': 0,
        'INDIVIDUAL_TARIFFS_BASE_URL': MOCKSERVER_URL + '/individual_tariffs',
    },
)
