from copy import deepcopy

from ._default import params as default_params


params = deepcopy(default_params)

params['fastcgi.conf'].update(
    {
        'via_base_url': 'https://sandbox-yandex.ridewithvia.com',
        'geotracks_base_url': 'http://geotracks.taxi.tst.yandex.net',
    },
)
