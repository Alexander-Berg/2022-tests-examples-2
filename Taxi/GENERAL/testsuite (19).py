from copy import deepcopy

from ._default import params as default_params


params = deepcopy(default_params)

MOCKSERVER_URL = 'http://@@MOCKSERVER@@'

params['fastcgi.conf'].update(
    {
        'log_level': 'DEBUG',
        'experiments_base_url': MOCKSERVER_URL + '/experiments',
        'router_here_url': MOCKSERVER_URL + '/router_here',
        'router_here_matrix_url': MOCKSERVER_URL + '/router_here',
        'userplaces_base_url': MOCKSERVER_URL + '/userplaces',
        'routehistory_base_url': MOCKSERVER_URL + '/routehistory',
        'pickup_points_manager_base_url': (
            MOCKSERVER_URL + '/pickup-points-manager'
        ),
        'ml_request_info_path': 'taxi-ml-request-info.log',
        'work_pool_size': 16,
    },
)
