from copy import deepcopy

from ._default import params as default_params


params = deepcopy(default_params)


params['fastcgi.conf'].update({'log_level': 'INFO', 'work_pool_threads': 10})
