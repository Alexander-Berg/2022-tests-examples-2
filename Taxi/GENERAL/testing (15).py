from copy import deepcopy

from ._default import params as default_params


params = deepcopy(default_params)


params['fastcgi.conf'].update(
    {
        'log_level': 'DEBUG',
        'tigraph_base_url': 'http://yaga-adjust.taxi.tst.yandex.net',
    },
)
