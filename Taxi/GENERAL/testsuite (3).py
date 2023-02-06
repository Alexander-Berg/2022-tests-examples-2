from copy import deepcopy

from ._default import params as default_params


params = deepcopy(default_params)

MOCKSERVER_URL = 'http://@@MOCKSERVER@@'
# mypy: ignore-errors
params['fastcgi.conf'].update({'log_level': 'DEBUG', 'work_pool_threads': 10})
