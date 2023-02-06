import pytest
import json

from sandbox.projects.tank.Firestarter.tasks import FirestarterTask
from sandbox.projects.tank.Firestarter.status import FirestarterError


NON_PARSED_CONFIGS = [
    (
        {'uploader': {'operator': 'ananiev', 'meta': {}}},
        'No task defined in uploader'
    ),
    (
        {'uploader': {'operator': 'bezrodnykh', 'task': 'T-64BV', 'meta': {}}},
        'Wrong task format'
    ),
    (
        {'uploader': {'operator': 'belashev', 'task': 'https://st.yandex-team.ru/LOAD-666', 'meta': {}}},
        'Wrong task format'
    ),
    (
        {'uploader': {'operator': 'bondarenko', 'task': 'T-34'},
         'metaconf': {'enabled': False, 'firestarter': {'tank': 'lee.tanks.yandex.net:8083'}}},
        'No one tank defined in config'
    ),
    (
        {'uploader': {'operator': 'vasiliev', 'task': 'KV-2', 'meta': {'use_tank_port': 8083}},
         'metaconf': {'enabled': False, 'firestarter': {'tank': 'lee.tanks.yandex.net:8083'}}},
        'No one tank defined in config'
    ),
    (
        {'uploader': {'operator': 'dobrobabin', 'task': 'KV-220', 'meta': {}},
         'metaconf': {'enabled': True, 'firestarter': {'tank_port': 8083}}},
        'No one tank defined in config'
    ),
    (
        {'uploader': {'operator': 'dutov', 'task': 'T-150', 'meta': {}},
         'metaconf': {'enabled': True, 'firestarter': {'target': 'lee.tanks.yandex.net:8083'}}},
        'No one tank defined in config'
    ),
    (
        {'uploader': {'operator': 'emtsov', 'task': 'IS-8', 'meta': {}},
         'metaconf': {'enabled': True, 'firestarter': {'tank': '[2a02:6b8:c14:1788:0:43af:a742:8083'}}},
        'No one tank defined in config'
    ),
    (
        {'uploader': {'operator': 'esebulatov', 'task': 'A-32', 'meta': {'use_tank': 8083}},
         'metaconf': {'enabled': False, 'firestarter': {'tank': 'lee.tanks.yandex.net:8083'}}},
        'Wrong tank format'
    ),
    (
        {'uploader': {'operator': 'kaleinikov', 'task': 'MS-1', 'meta': {}},
         'metaconf': {'enabled': True, 'firestarter': {'tank': {'host': 'lee.tanks.yandex.net', 'port': 8083}}}},
        'Wrong tank format'
    ),
    (
        {'uploader': {'operator': 'klochkov', 'task': 'BT-2', 'meta': {}},
         'metaconf': {'enabled': True, 'firestarter': {'tank': ['lee.tanks.yandex.net', 'stuart.tanks.yandex.net']}}},
        'No one target defined in config'
    ),
    (
        {'phantom': {'enabled': True, 'load_profile': 'line(1,10,30s)', 'ammofile': './uri.ammo', 'uris': []},
         'uploader': {'operator': 'kozhubergenov', 'task': 'T-26', 'meta': {'use_tank': 'lee.tanks.yandex.net:8083'}}},
        'No one target defined in config'
    ),
    (
        {'phantom': {'enabled': True, 'address': '[2a02:6b8:c14:1788:0:43af:a742:80', 'load_profile': 'line(1,10,30s)', 'ammofile': './uri.ammo', 'uris': []},
         'uploader': {'operator': 'konkin', 'task': 'PT-76', 'meta': {'use_tank': 'lee.tanks.yandex.net:8083'}}},
        'No one target defined in config'
    ),
    (
        {'phantom': {'enabled': True, 'load_profile': 'line(1,10,30s)', 'ammofile': './uri.ammo', 'uris': []},
         'uploader': {'operator': 'kosaev', 'task': 'SU-18', 'meta': {'use_tank': '[2a02:6b8:c14:1788:0:43af:a742]:8083'}},
         'metaconf': {'enabled': False, 'firestarter': {'tank': 'lee.tanks.yandex.net:8083', 'target': 'bmpt01i.tanks.yandex.net:80'}}},
        'No one target defined in config'
    ),
    (
        {'phantom': {'enabled': True, 'address': 'comet.tanks.yandex.net:8083', 'load_profile': 'line(1,10,30s)', 'ammofile': './uri.ammo', 'uris': []},
         'uploader': {'operator': 'kruchkov', 'task': 'T-44', 'meta': {}},
         'metaconf': {'enabled': True, 'firestarter': {'tank': 'lee.tanks.yandex.net:8083', 'target': '[2a02:6b8:c14:1788:0:43af:a742:80'}}},
        'No one target defined in config'
    ),
    (
        {'phantom': {'enabled': False, 'address': '', 'load_profile': 'line(1,10,30s)', 'ammofile': './uri.ammo', 'uris': []},
         'pandora': {'enabled': True, 'config_content': {'pools': [{'id': 'HTTP', 'gun': {'type': 'http', 'target': '[2a02:6b8:c14:1788:0:43af:a742:80'}, 'rps': [], 'ammo': {}}]}},
         'uploader': {'operator': 'maksimov', 'task': 'SU-85', 'meta': {'use_tank': '127.0.0.1:8083'}},
         'metaconf': {'enabled': False, 'firestarter': {'tank': 'lee.tanks.yandex.net:8083'}}},
        'No one target defined in config'
    ),
    (
        {'phantom': {'enabled': True, 'address': 80, 'load_profile': 'line(1,10,30s)', 'ammofile': './uri.ammo', 'uris': []},
         'uploader': {'operator': 'mitin', 'task': 'BM-13', 'meta': {}},
         'metaconf': {'enabled': True, 'firestarter': {'tank': 'lee.tanks.yandex.net:8083'}}},
        'Wrong target format'
    ),
    (
        {'phantom': {'enabled': False, 'address': '', 'load_profile': 'line(1,10,30s)', 'ammofile': './uri.ammo', 'uris': []},
         'pandora': {'enabled': True, 'config_content': {'pools': [{'id': 'HTTP', 'gun': {'type': 'http', 'target': {'host': '192.168.144.120', 'port': '80'}}, 'rps': [], 'ammo': {}}]}},
         'uploader': {'operator': 'mitchenko', 'task': 'T-60', 'meta': {'use_tank': '127.0.0.1:8083'}},
         'metaconf': {'enabled': False, 'firestarter': {'tank': 'lee.tanks.yandex.net:8083'}}},
        'Wrong target format'
    ),
    (
        {'phantom': {'enabled': True, 'address': 'comet.tanks.yandex.net:8083', 'load_profile': 'line(1,10,30s)', 'ammofile': './uri.ammo', 'uris': []},
         'uploader': {'operator': 'moskalenko', 'task': 'ISU-152', 'meta': {}},
         'metaconf': {'enabled': True, 'firestarter': {'tank': 'lee.tanks.yandex.net:8083', 'target': ['2a02:6b8:c14:1788:0:43af:a742', 'bmpt01i.tamnks.yandex.net']}}},
        'Wrong target format'
    ),
    (
        {'phantom': {'enabled': False, 'address': '', 'load_profile': 'line(1,10,30s)', 'ammofile': './uri.ammo', 'uris': []},
         'pandora': {'enabled': True, 'config_file': './load.yaml'},
         'uploader': {'operator': 'natarov', 'task': 'BA-10', 'meta': {}},
         'metaconf': {'enabled': True, 'firestarter': {'tank': 'common'}}},
        'Detected custom load scenario on the pandora or bfg.\nPlease specify the single or sandbox tank in config.'
    ),
    (
        {'phantom': {'enabled': False, 'address': '', 'load_profile': 'line(1,10,30s)', 'ammofile': './uri.ammo', 'uris': []},
         'pandora': {'enabled': True, 'config_file': './load.yaml'},
         'uploader': {'operator': 'petrenko', 'task': 'ZSU-37', 'meta': {}},
         'metaconf': {'enabled': True, 'firestarter': {'tank': 'nanny:production_yandex_tank'}}},
        'Detected custom load scenario on the pandora or bfg.\nPlease specify the single or sandbox tank in config.'
    ),
    (
        {'phantom': {'enabled': False, 'address': '', 'load_profile': 'line(1,10,30s)', 'ammofile': './uri.ammo', 'uris': []},
         'bfg': {'enabled': True, 'address': 'proxy.sandbox.yandex-team.ru'},
         'uploader': {'operator': 'sengirbaev', 'task': 'HTZ-16', 'meta': {}},
         'metaconf': {'enabled': True, 'firestarter': {'tank': 'nanny:production_yandex_tank'}}},
        'Detected custom load scenario on the pandora or bfg.\nPlease specify the single or sandbox tank in config.'
    ),
    (
        {'phantom': {'enabled': False, 'address': '', 'load_profile': 'line(1,10,30s)', 'ammofile': './uri.ammo', 'uris': []},
         'bfg2020': {'enabled': True, 'gun_config': {'class_name': 'LoadTest', 'module_path': '/etc/grut-load/', 'module_name': 'gun', 'init_param': {'target': 'api.grut-load.yandex.net:1309'}}},
         'uploader': {'operator': 'timofeev', 'task': 'ZIS-30', 'meta': {}},
         'metaconf': {'enabled': True, 'firestarter': {'tank': 'sandbox'}}},
        'Detected custom load scenario on the pandora or bfg.\nPlease specify the single or sandbox tank in config.'
    )
]

CONFIGS_SINGLE_TANK = [
    (
        {
            'phantom': {'enabled': True, 'address': 'bmpt01i.tanks.yandex.net', 'load_profile': 'line(1,10,30s)', 'ammofile': './uri.ammo', 'uris': []},
            'uploader': {'operator': 'aronova', 'task': 'IS-1', 'meta': {'use_tank': 'lee.tanks.yandex.net'}}
        },
        {
            'target': {'value': 'bmpt01i.tanks.yandex.net', 'port': 80},
            'tank': {'value': 'lee.tanks.yandex.net', 'port': 8083},
            'operator': 'aronova', 'task': 'IS-1', 'dc': '',
        }
    ),
    (
        {
            'phantom': {'enabled': False, 'address': 'bmpt01i.tanks.yandex.net', 'load_profile': 'line(1,10,30s)', 'ammofile': './uri.ammo', 'uris': []},
            'pandora': {'enabled': True, 'config_content': {'pools': [{'id': 'HTTP', 'gun': {'type': 'http', 'target': '[2a02:6b8:c14:1788:0:43af:a742]:80'}, 'rps': [], 'ammo': {}}]}},
            'uploader': {'operator': 'baida', 'task': 'KV-8', 'meta': {'use_tank': '37.9.119.137:3808'}}
        },
        {
            'target': {'value': '2a02:6b8:c14:1788:0:43af:a742', 'port': '80'},
            'tank': {'value': '37.9.119.137', 'port': '3808'},
            'operator': 'baida', 'task': 'KV-8', 'dc': '',
        }
    ),
    (
        {
            'phantom': {'enabled': True, 'address': 'slb-lunapark.yandex-team.ru:443', 'load_profile': 'line(1,10,30s)', 'ammofile': './uri.ammo', 'uris': []},
            'pandora': {'enabled': False, 'config_content': {'pools': [{'id': 'HTTP', 'gun': {'type': 'http', 'target': '[2a02:6b8:c14:1788:0:43af:a742]:80'}, 'rps': [], 'ammo': {}}]}},
            'uploader': {'operator': 'litvyak', 'task': 'IS-2', 'meta': {'use_tank': '2a02:6b8::1a45:225:90ff:fe83:17a4', 'use_tank_port': '9876'}},
            'metaconf': {'enabled': False, 'firestarter': {'tank': 'lee.tanks.yandex.net:8083'}}
        },
        {
            'target': {'value': 'slb-lunapark.yandex-team.ru', 'port': '443'},
            'tank': {'value': '2a02:6b8::1a45:225:90ff:fe83:17a4', 'port': '9876'},
            'operator': 'litvyak', 'task': 'IS-2', 'dc': '',
        }
    ),
    (
        {
            'phantom': {'enabled': True, 'address': '2a02:6b8:c14:1788:0:43af:a742', 'load_profile': 'line(1,10,30s)', 'ammofile': './uri.ammo', 'uris': []},
            'uploader': {'operator': 'batrakova', 'task': 'KV-85', 'meta': {'use_tank': 'lee.tanks.yandex.net'}},
            'metaconf': {'enabled': True, 'firestarter': {'tank': 'lee.tanks.yandex.net', 'dc': 'sas'}}
        },
        {
            'target': {'value': '2a02:6b8:c14:1788:0:43af:a742', 'port': 80},
            'tank': {'value': 'lee.tanks.yandex.net', 'port': 8083},
            'operator': 'batrakova', 'task': 'KV-85', 'dc': 'sas',
        }
    ),
    (
        {
            'phantom': {'enabled': False, 'address': 'bmpt01i.tanks.yandex.net', 'load_profile': 'line(1,10,30s)', 'ammofile': './uri.ammo', 'uris': []},
            'pandora': {'enabled': True, 'config_content': {'pools': [{'id': 'HTTP', 'gun': {'type': 'http', 'target': 'webmail.qloud.yandex.net'}, 'rps': [], 'ammo': {}}]}},
            'uploader': {'operator': 'belick', 'task': 'KV-4', 'meta': {'use_tank': 'bumblebee.tanks.yandex.net:3808'}},
            'metaconf': {'enabled': True, 'firestarter': {'tank': '37.9.119.137', 'tank_port': 303, 'target_port': 1205}}
        },
        {
            'target': {'value': 'webmail.qloud.yandex.net', 'port': '1205'},
            'tank': {'value': '37.9.119.137', 'port': '303'},
            'operator': 'belick', 'task': 'KV-4', 'dc': '',
        }
    ),
    (
        {
            'phantom': {'enabled': True, 'address': 'slb-lunapark.yandex-team.ru:443', 'load_profile': 'line(1,10,30s)', 'ammofile': './uri.ammo', 'uris': []},
            'pandora': {'enabled': False, 'config_content': {'pools': [{'id': 'HTTP', 'gun': {'type': 'http', 'target': '[2a02:6b8:c14:1788:0:43af:a742]:80'}, 'rps': [], 'ammo': {}}]}},
            'uploader': {'operator': 'shchetinina', 'task': 'IS-3', 'meta': {'use_tank': 'mars.tanks.yandex.net', 'use_tank_port': '6574'}},
            'metaconf': {'enabled': True, 'firestarter': {'tank': '[2a02:6b8::1a45:225:90ff:fe83:17a4]:8083', 'target': '192.168.11.13', 'target_port': 1380, 'dc': 'MYT'}}
        },
        {
            'target': {'value': '192.168.11.13', 'port': '1380'},
            'tank': {'value': '2a02:6b8::1a45:225:90ff:fe83:17a4', 'port': '8083'},
            'operator': 'shchetinina', 'task': 'IS-3', 'dc': 'MYT',
        }
    )
]

CONFIGS_GROUP_TANK = [
    (
        {
            'phantom': {'enabled': True, 'address': '2a02:6b8:c14:1788:0:43af:a742', 'load_profile': 'line(1,10,30s)', 'ammofile': './uri.ammo', 'uris': []},
            'uploader': {'operator': 'pavlichenko', 'task': 'HI-26', 'meta': {'use_tank': 'lee.tanks.yandex.net'}},
            'metaconf': {'enabled': True, 'firestarter': {'tank': 'common', 'dc': 'man', 'target': 'nanny:maps_front_prod', 'target_port': 1380}}
        },
        {
            'target': {'value': 'nanny:maps_front_prod', 'port': '1380'},
            'tank': {'value': 'common', 'port': 8083},
            'operator': 'pavlichenko', 'task': 'HI-26', 'dc': 'man',
        }
    ),
    (
        {
            'phantom': {'enabled': True, 'address': 'bmpt01i.tanks.yandex.net', 'load_profile': 'line(1,10,30s)', 'ammofile': './uri.ammo', 'uris': []},
            'pandora': {'enabled': False, 'config_content': {'pools': [{'id': 'HTTP', 'gun': {'type': 'http', 'target': 'webmail.qloud.yandex.net'}, 'rps': [], 'ammo': {}}]}},
            'uploader': {'operator': 'rugo', 'task': 'OT-133', 'meta': {'use_tank': 'bumblebee.tanks.yandex.net:3808', 'use_tank_port': 30169}},
            'metaconf': {'enabled': True, 'firestarter': {'tank': 'nanny:production_yandex_tank', 'target': 'deploy:yandex-tank-finder-testing'}}
        },
        {
            'target': {'value': 'deploy:yandex-tank-finder-testing', 'port': 80},
            'tank': {'value': 'nanny:production_yandex_tank', 'port': '30169'},
            'operator': 'rugo', 'task': 'OT-133', 'dc': '',
        }
    ),
    (
        {
            'phantom': {'enabled': True, 'address': 'slb-lunapark.yandex-team.ru:443', 'load_profile': 'line(1,10,30s)', 'ammofile': './uri.ammo', 'uris': []},
            'pandora': {'enabled': False, 'config_content': {'pools': [{'id': 'HTTP', 'gun': {'type': 'http', 'target': 'mama.myla.ra.mu'}, 'rps': [], 'ammo': {}}]}},
            'uploader': {'operator': 'vasilieva', 'task': 'IT-1', 'meta': {'use_tank': 'mars.tanks.yandex.net', 'use_tank_port': '6574'}},
            'metaconf': {'enabled': True, 'firestarter': {'tank': 'deploy:caliban.caliban.man'}}
        },
        {
            'target': {'value': 'slb-lunapark.yandex-team.ru', 'port': '443'},
            'tank': {'value': 'deploy:caliban.caliban.man', 'port': '6574'},
            'operator': 'vasilieva', 'task': 'IT-1', 'dc': '',
        }
    )
]

CONFIGS_SANDBOX_TANK = [
    (
        {
            'phantom': {'enabled': True, 'address': '[2a02:6b8:c14:1788:0:43af:a742]:1910', 'load_profile': 'line(1,10,30s)', 'ammofile': './uri.ammo', 'uris': []},
            'uploader': {'operator': 'grizodubova', 'task': 'LI-2', 'meta': {'use_tank': 'lee.tanks.yandex.net'}},
            'metaconf': {'enabled': True, 'firestarter': {'tank': 'sandbox', 'dc': 'sas'}}
        },
        {
            'target': {'value': '2a02:6b8:c14:1788:0:43af:a742', 'port': '1910'},
            'tank': {'value': 'sandbox', 'port': 8083},
            'operator': 'grizodubova', 'task': 'LI-2', 'dc': 'sas',
        }
    ),
    (
        {
            'phantom': {'enabled': False, 'address': 'bmpt01i.tanks.yandex.net', 'load_profile': 'line(1,10,30s)', 'ammofile': './uri.ammo', 'uris': []},
            'pandora': {'enabled': True, 'config_content': {'pools': [{'id': 'HTTP', 'gun': {'type': 'http', 'target': 'webmail.qloud.yandex.net:29734'}, 'rps': [], 'ammo': {}}]}},
            'uploader': {'operator': 'osipenko', 'task': 'AN-32', 'meta': {'use_tank': 'bumblebee.tanks.yandex.net:3808'}},
            'metaconf': {'enabled': True, 'firestarter': {'tank': 'sandbox', 'target': '10.9.8.7', 'target_port': 1380}}
        },
        {
            'target': {'value': '10.9.8.7', 'port': '1380'},
            'tank': {'value': 'sandbox', 'port': 8083},
            'operator': 'osipenko', 'task': 'AN-32', 'dc': '',
        }
    ),
    (
        {
            'phantom': {'enabled': True, 'address': 'slb-lunapark.yandex-team.ru:443', 'load_profile': 'line(1,10,30s)', 'ammofile': './uri.ammo', 'uris': []},
            'pandora': {'enabled': False, 'config_content': {'pools': [{'id': 'HTTP', 'gun': {'type': 'http', 'target': '[2a02:6b8:c14:1788:0:43af:a742]:80'}, 'rps': [], 'ammo': {}}]}},
            'uploader': {'operator': 'raskova', 'task': 'AIR-12', 'meta': {'use_tank': 'mars.tanks.yandex.net', 'use_tank_port': '6574'}},
            'metaconf': {'enabled': True, 'firestarter': {'tank': 'sandbox', 'target': 'nanny:production_overload', 'dc': 'man'}}
        },
        {
            'target': {'value': 'nanny:production_overload', 'port': 80},
            'tank': {'value': 'sandbox', 'port': '6574'},
            'operator': 'raskova', 'task': 'AIR-12', 'dc': 'man',
        }
    ),
    (
        {
            'phantom': {'enabled': True, 'address': 'sandbox.yandex-team.ru:13131', 'load_profile': 'line(1,10,30s)', 'ammofile': './uri.ammo', 'uris': []},
            'pandora': {'enabled': False, 'config_content': {'pools': [{'id': 'HTTP', 'gun': {'type': 'http', 'target': '[2a02:6b8:c14:1788:0:43af:a742]:80'}, 'rps': [], 'ammo': {}}]}},
            'uploader': {'operator': 'bershanskaya', 'task': 'LA-5', 'meta': {'use_tank': 'mars.tanks.yandex.net', 'use_tank_port': '6574'}},
            'metaconf': {'enabled': True, 'firestarter': {'tank': 'sandbox', 'target': 'deploy:caliban', 'dc': 'man'}}
        },
        {
            'target': {'value': 'deploy:caliban', 'port': 80},
            'tank': {'value': 'sandbox', 'port': '6574'},
            'operator': 'bershanskaya', 'task': 'LA-5', 'dc': 'man',
        }
    )
]


REPR_CONFIGS = [
    (
        {
            'phantom': {'enabled': False, 'address': 'slb-lunapark.yandex-team.ru:443', 'load_profile': 'line(1,10,30s)', 'ammofile': './uri.ammo', 'uris': []},
            'pandora': {'enabled': True, 'config_content': {'pools': [{'id': 'HTTP', 'gun': {'type': 'http', 'target': '[2a02:6b8::43af:a742]:80'}, 'rps': [], 'ammo': {}}]}},
            'uploader': {'operator': 'baramzina', 'task': 'IS-2', 'meta': {'use_tank': '2a02:6b8::fe83:17a4', 'use_tank_port': '9876'}},
            'metaconf': {'enabled': True, 'firestarter': {'tank': 'lee.tanks.yandex.net:8083', 'target': 'deploy:lunapark_production'}}
        },
        {
            'phantom': {'enabled': False, 'address': 'slb-lunapark.yandex-team.ru:443', 'load_profile': 'line(1,10,30s)', 'ammofile': './uri.ammo', 'uris': []},
            'pandora': {'enabled': True, 'config_content': {'pools': [{'id': 'HTTP', 'gun': {'type': 'http', 'target': '[2a02:6b8::43af:a742]:80'}, 'rps': [], 'ammo': {}}]}},
            'uploader': {'operator': 'baramzina', 'task': 'IS-2', 'meta': {'launched_from': 'https://sandbox.yandex-team.ru/task/1', 'use_tank': '2a02:6b8::fe83:17a4', 'use_tank_port': '9876'}},
            'metaconf': {'enabled': True, 'firestarter': {'tank': 'lee.tanks.yandex.net:8083', 'target': 'deploy:lunapark_production'}}
        }
    ),
    (
        {
            'phantom': {'enabled': True, 'address': '2a02:6b8:c14:1788:0:43af:a742', 'load_profile': 'line(1,10,30s)', 'ammofile': './uri.ammo', 'uris': []},
            'uploader': {'operator': 'batrakova', 'task': 'KV-85', 'meta': {'use_tank': 'lee.tanks.yandex.net'}},
            'metaconf': {'enabled': True, 'firestarter': {'tank': 'lee.tanks.yandex.net', 'target': 'nanny:production_yandex_tank', 'dc': 'sas'}}
        },
        {
            'phantom': {'enabled': True, 'address': '2a02:6b8:c14:1788:0:43af:a742', 'load_profile': 'line(1,10,30s)', 'ammofile': './uri.ammo', 'uris': []},
            'uploader': {'operator': 'batrakova', 'task': 'KV-85', 'meta': {'launched_from': 'https://sandbox.yandex-team.ru/task/1', 'use_tank': 'lee.tanks.yandex.net'}},
            'metaconf': {'enabled': True, 'firestarter': {'tank': 'lee.tanks.yandex.net', 'target': 'nanny:production_yandex_tank', 'dc': 'sas'}}
        }
    ),
]


def create_sb_tank(*args, **kwargs):
    return 1, ''


class TestExceptionConfigs:

    @pytest.mark.parametrize('config, error_msg', NON_PARSED_CONFIGS)
    def test_fail_parse_config(self, config, error_msg):
        fs_task = FirestarterTask(1, json.dumps(config), None, create_sb_tank)
        with pytest.raises(FirestarterError):
            assert fs_task.parse_config()

    @pytest.mark.parametrize('config, error_msg', NON_PARSED_CONFIGS)
    def test_error_massage(self, config, error_msg):
        fs_task = FirestarterTask(1, json.dumps(config), None, create_sb_tank)
        with pytest.raises(FirestarterError) as fe:
            fs_task.parse_config()
        assert fe.type is FirestarterError
        assert fe.value.section == 'parse_config'
        assert fe.value.error == error_msg

    @pytest.mark.parametrize('config, parsing_result', CONFIGS_SINGLE_TANK + CONFIGS_GROUP_TANK + CONFIGS_SANDBOX_TANK)
    def test_correct_parse_config(self, config, parsing_result):
        fs_task = FirestarterTask(1, json.dumps(config), None, create_sb_tank)
        fs_task.parse_config()
        assert fs_task.parsing_result == parsing_result

    def test_fail_validation(self, mocker):
        with mocker.patch('sandbox.projects.tank.Firestarter.external_calls.external_call', return_value=({'config': {'uploader': {'enabled': False}}, 'errors': {'a': 1, 'b': 2}}, '')):
            fs_task = FirestarterTask(1, json.dumps({}), None, create_sb_tank)
            with pytest.raises(FirestarterError) as fe:
                fs_task.validate_config()
            assert fe.type is FirestarterError
            assert fe.value.section == 'validate_config'
            assert fe.value.error == 'Config invalid. [\'a: 1\', \'b: 2\']'

    @pytest.mark.parametrize('config, repr_config', REPR_CONFIGS)
    def test_repr_task(self, mocker, config, repr_config):
        class MockLunaTank:
            def __init__(self, host, port):
                self.host = host
                self.port = port
        task_repr = {
            'id_': '1',
            'lunapark_id': 0,
            'config': repr_config,
            'errors': False,
            'error_message': {},
            'status': 'tank found',
            'tank_version': None
        }
        with mocker.patch('sandbox.projects.tank.Firestarter.tasks.DefineHosts.get_target', return_value=('in_config', 80)):
            with mocker.patch('sandbox.projects.tank.Firestarter.tasks.DefineHosts.get_tanks', return_value=[MockLunaTank('lee.tanks.yandex.net', '8083')]):
                with mocker.patch('sandbox.projects.tank.Firestarter.tasks.define_host_dc', return_value='fru'):
                    fs_task = FirestarterTask(1, json.dumps(config), None, create_sb_tank)
                    fs_task.task_id = '1'
                    fs_task.parse_config()
                    fs_task.define_hosts()
        assert json.loads(repr(fs_task)) == task_repr
