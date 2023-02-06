from copy import deepcopy

from ._default import params as default_params


params = deepcopy(default_params)

params['jobs.json'].update(
    {
        'TRACKER_BASE_URL': 'http://tracker.taxi.tst.yandex.net',
        'SURGE_BASE_URL': 'http://surge.taxi.tst.yandex.net',
        'CONFIGS_URL': 'http://configs.taxi.tst.yandex.net',
        'GEOTRACKS_BASE_URL': (
            'http://driver-trackstory.taxi.tst.yandex.net/legacy'
        ),
        'GEOAREAS_BASE_URL': 'http://geoareas.taxi.tst.yandex.net',
        'INDIVIDUAL_TARIFFS_BASE_URL': (
            'http://individual-tariffs.taxi.tst.yandex.net'
        ),
    },
)
