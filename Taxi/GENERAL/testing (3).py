from copy import deepcopy

from ._default import params as default_params


params = deepcopy(default_params)


params['fastcgi.conf'].update(
    {'log_level': 'DEBUG', 'yt_environment': 'testing'},
)
