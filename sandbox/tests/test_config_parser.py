import pytest
from sandbox.projects.tank.Firestarter.config_parser import ConfigManager, parse_tank


test_cm = ConfigManager(task_id=12, config='uploader:\n  task: LOAD-666')


class TestConfigManager:

    operator_input_expected = [
        (
            {'phantom': {'address': 'ya.ru'}, 'uploader': {'ver': '1.3.5', 'operator': 'test_user   '}},
            'test_user'
        ),
        (
            {'phantom': {'address': 'ya.ru'}, 'uploader': {'ver': '1.3.5'}},
            ''
        )
    ]

    target_input_expected = [
        (
            {'phantom': {'address': '  ya.ru'}},
            ('ya.ru', '')
        ),
        (
            {'phantom': {'enabled': True}},
            ('', ''),
        ),
        (
            {'phantom': {'address': 'ya.ru:443 '}},
            ('ya.ru', '443')
        ),
        (
            {'phantom': {'address': '[2a02:6b8:c1a:2ebf:0:43ae:3677:3]'}},
            ('2a02:6b8:c1a:2ebf:0:43ae:3677:3', '')
        ),
        (
            {'phantom': {'address': '  [2a02:6b8:c1a:2ebf:0:43ae:3677:3]:443  '}},
            ('2a02:6b8:c1a:2ebf:0:43ae:3677:3', '443')
        ),
        (
            {
                'phantom': {
                    'address': 'eda-eats-full-text-search-tank-1.sas.yp-c.yandex.net',
                    'ammofile':
                        'https://storage-int.mds.yandex.net/get-load-ammo/21373/9d0d3b0cae5c4dbfbee008d81d194b7b',
                    'load_profile': {'load_type': 'rps', 'schedule': ' line(1,10,30s)'},
                    'uris': []
                },
                'uploader': {
                    'enabled': True,
                    'task': 'EDACAT-666',
                    'ver': ''
                },
            },
            ('eda-eats-full-text-search-tank-1.sas.yp-c.yandex.net', '')
        ),
        (
            {'pandora': {'config_content': {
                'log': {'level': 'error'},
                'pools': [
                    {
                        'ammo': {
                            'source': {'path': './ammo.json', 'type': 'file'},
                            'type': 'retriever_provider'
                        },
                        'gun': {
                            'target': 'retriever-1.retriever.load.retriever.mail.stable.qloud-d.yandex.net',
                            'type': 'retriever_gun'
                        },
                        'id': 'HTTP pool',
                        'result': {'destination': './phout.log', 'type': 'phout'},
                        'rps': {'duration': '600s', 'ops': 150, 'type': 'const'},
                        'startup': {'times': 5000, 'type': 'once'}
                    },
                ]
            },
                'enabled': True
            },
                'phantom': {'address': '', 'enabled': False}
            },
            ('retriever-1.retriever.load.retriever.mail.stable.qloud-d.yandex.net', '')
        ),
        (
            {'pandora': {'config_content': {
                'log': {'level': 'error'},
                'pools': [
                    {
                        'ammo': {'source': {'path': './ammo.json', 'type': 'file'},
                                 'type': 'retriever_provider'},
                        'gun': {
                            'target': 'retriever-1.retriever.load.retriever.mail.stable.qloud-d.yandex.net:443',
                            'type': 'retriever_gun'},
                        'id': 'HTTP pool',
                        'result': {'destination': './phout.log', 'type': 'phout'},
                        'rps': {'duration': '600s', 'ops': 150, 'type': 'const'},
                        'startup': {'times': 5000, 'type': 'once'}
                    }, ]
            },
                'enabled': True},
                'phantom': {'address': '', 'enabled': False}
            },
            ('retriever-1.retriever.load.retriever.mail.stable.qloud-d.yandex.net', '443')
        ),
        (
            {'pandora': {'config_content': {
                'log': {'level': 'error'},
                'pools': [
                    {
                        'ammo': {'source': {'path': './ammo.json', 'type': 'file'},
                                 'type': 'retriever_provider'},
                        'gun': {
                            'target': 'retriever-1.retriever.load.retriever.mail.stable.qloud-d.yandex.net:80',
                            'type': 'retriever_gun'},
                        'id': 'HTTP pool',
                        'result': {'destination': './phout.log', 'type': 'phout'},
                        'rps': {'duration': '600s', 'ops': 150, 'type': 'const'},
                        'startup': {'times': 5000, 'type': 'once'}
                    }, ]
            },
                'enabled': True},
                'phantom': {'address': 'ya.ru:995', 'enabled': False}},
            ('retriever-1.retriever.load.retriever.mail.stable.qloud-d.yandex.net', '80')
        )
    ]

    tanks_input_expected = [
        ({'uploader': {'meta': {'use_tank': 'uploader tank', 'use_tank_port': 13}}}, ('uploader tank', '13')),
        (
            {'uploader': {'meta': {'use_tank': '  nanny:production_yandex_tank '}}},
            ('nanny:production_yandex_tank', '')
        ),
        (
            {'uploader': {'meta': {'use_tank': 'nanny:production_yandex_tank', 'use_tank_port': 23}}},
            ('nanny:production_yandex_tank', '23')
        ),
        (
            {'uploader': {'task': 'MAILPG-2716', 'ver': '1.1', 'package': 'yandextank.plugins.DataUploader',
                          'enabled': True, 'job_name': 'test', 'api_address': 'https://lunapark.yandex-team.ru/',
                          'meta': {'use_tank': 'man1-3948-all-rcloud-tanks-30169.gencfg-c.yandex.net:30169'},
                          'operator': 'lunapark', 'job_dsc': 'test'}},
            ('man1-3948-all-rcloud-tanks-30169.gencfg-c.yandex.net', '30169')
        ),
        (
            {'uploader': {'task': 'KP-21618',
                          'ver': '',
                          'package': 'yandextank.plugins.DataUploader',
                          'job_name': 'Расписание с апи (10rps)',
                          'api_address': 'https://lunapark.yandex-team.ru/',
                          'meta': {'use_tank': 'vla1-f50466766cbc.qloud-c.yandex.net'},
                          'operator': 'machekhin-am',
                          'job_dsc': ''}},
            ('vla1-f50466766cbc.qloud-c.yandex.net', '')
        ),
        (
            {'uploader': {'meta': {'use_tank': '[2a02:6b8:c0b:671e:0:43af:5716:1]'}}},
            ('2a02:6b8:c0b:671e:0:43af:5716:1', '')
        ),
        (
            {'uploader': {'meta': {'use_tank': '[2a02:6b8:c0b:671e:0:43af:5716:1]:8083'}}},
            ('2a02:6b8:c0b:671e:0:43af:5716:1', '8083')
        ),
        ({}, ('', ''))
    ]

    target_metaconf_expected = [
        (
            {'metaconf': {'firestarter': {'target': 'load.yandex-team.ru', 'target_port': 443}}},
            ('load.yandex-team.ru', '443')),
        (
            {'metaconf': {'firestarter': {'target': 'nanny:arina_rodionovna'}}},
            ('nanny:arina_rodionovna', '')
        ),
        (
            {'metaconf': {'firestarter': {'target': 'nanny:vyxodnogo_dnya   ', 'target_port': 67}}},
            ('nanny:vyxodnogo_dnya', '67')
        ),
        (
            {'metaconf': {'firestarter': {'target': '  deploy:mir.trud.mai  ', 'target_port': 105}}},
            ('deploy:mir.trud.mai', '105')
        ),
        (
            {'metaconf': {'firestarter': {'target': '   deploy:slo..don'}}},
            ('deploy:slo..don', '')
        ),
        (
            {'metaconf': {'enabled': True, 'ver': '1.1', 'package': 'yandextank.plugins.MetaConf',
                          'jenkins': 'Will not be used', 'gitlab': 'Deprecated', 'bitbucket': 'Not configured',
                          'firestarter': {'tank': 'man1-3948-all-rcloud-tanks-30169.gencfg-c.yandex.net:30169', 'target': 'lunapark.yandex-team.ru:443'},
                          'ci': 'a.yaml', 'trendbox': '4front'}},
            ('lunapark.yandex-team.ru', '443')
        ),
        (
            {'metaconf': {'enabled': True,
                          'romashka': 'vesna',
                          'jvachka': 'desna',
                          'perenositsa': 'gaimorit',
                          'ispania': 'madrid',
                          'firestarter': {'target': '169.58.4.12', 'target_port': 8888},
                          'nevesta': 'fata',
                          'jeludok': 'eda'}},
            ('169.58.4.12', '8888')
        ),
        (
            {'metaconf': {'firestarter': {'target': '[2a02:6b8:c0b:671e:0:43af:5716:1]'}}},
            ('2a02:6b8:c0b:671e:0:43af:5716:1', '')
        ),
        (
            {'metaconf': {'firestarter': {'target': '[2a02:6b8:c0b:671e:0:43af:5716:1]:3038'}}},
            ('2a02:6b8:c0b:671e:0:43af:5716:1', '3038')
        ),
        (
            {'phantom': {'address': ['load.yandex-team.ru']}, 'pandora': {}, 'metaconf': {}},
            (['load.yandex-team.ru'], '')
        ),
        (
            {'phantom': {}, 'pandora': {}, 'metaconf': {'firestarter': {'target': {'a': 1, 'b': 2}}}},
            ({'a': 1, 'b': 2}, '')
        ),
        ({}, ('', ''))
    ]

    tanks_metaconf_expected = [
        (
            {'metaconf': {'firestarter': {'tank': 'uploader tank', 'tank_port': 13}}},
            ('uploader tank', '13')),
        (
            {'metaconf': {'firestarter': {'tank': 'nanny:production_yandex_tank'}}},
            ('nanny:production_yandex_tank', '')
        ),
        (
            {'metaconf': {'firestarter': {'tank': 'nanny:production_yandex_tank', 'tank_port': 23}}},
            ('nanny:production_yandex_tank', '23')
        ),
        (
            {'metaconf': {'enabled': True, 'ver': '1.1', 'package': 'yandextank.plugins.MetaConf',
                          'jenkins': 'Will not be used', 'gitlab': 'Deprecated', 'bitbucket': 'Not configured',
                          'firestarter': {'tank': 'man1-3948-all-rcloud-tanks-30169.gencfg-c.yandex.net:30169', 'target': 'lunapark.yandex-team.ru:443'},
                          'ci': 'a.yaml', 'trendbox': '4front'}},
            ('man1-3948-all-rcloud-tanks-30169.gencfg-c.yandex.net', '30169')
        ),
        (
            {'metaconf': {'enabled': True,
                          'romashka': 'vesna',
                          'jvachka': 'desna',
                          'perenositsa': 'gaimorit',
                          'ispania': 'madrid',
                          'firestarter': {'tank': 'vla1-f50466766cbc.qloud-c.yandex.net'},
                          'nevesta': 'fata',
                          'jeludok': 'eda'}},
            ('vla1-f50466766cbc.qloud-c.yandex.net', '')
        ),
        (
            {'metaconf': {'firestarter': {'tank': '[2a02:6b8:c0b:671e:0:43af:5716:1]'}}},
            ('2a02:6b8:c0b:671e:0:43af:5716:1', '')
        ),
        (
            {'metaconf': {'firestarter': {'tank': '[2a02:6b8:c0b:671e:0:43af:5716:1]:8083'}}},
            ('2a02:6b8:c0b:671e:0:43af:5716:1', '8083')
        ),
        (
            {'metaconf': {'firestarter': {'tank': 'deploy:mama.myla.ramu:8083'}}},
            ('deploy:mama.myla.ramu', '8083')
        ),
        (
            {'metaconf': {'firestarter': {'tank': 'deploy:ko..on', 'tank_port': 23}}},
            ('deploy:ko..on', '23')
        ),
        (
            {'metaconf': {'firestarter': {'tank': 'common'}}},
            ('common', '')
        ),
        (
            {'metaconf': {'firestarter': {'tank': 'sandbox'}}},
            ('sandbox', '')
        ),
        ({}, ('', ''))
    ]

    pandora_config_file_expected = [
        (
            {'pandora': {'config_file': '/tmp/load/pandora.yaml'}},
            True
        ),
        (
            {'pandora': {'resources': [{'src': 'http_link', 'dst': './pandora.yaml'}], 'config_file': './pandora.yaml'}},
            True
        ),
        (
            {'pandora': {'config_content': {}}},
            False
        )
    ]

    @pytest.mark.parametrize('test_input, expected', operator_input_expected)
    def test_get_operator(self, test_input, expected):
        test_cm.config = test_input
        assert test_cm.get_operator() == expected

    @pytest.mark.skip
    def test_get_operator_without_user(self):
        test_cm.config = {'phantom': {'address': 'ya.ru'}, 'uploader': {'ver': '1.3.5', 'operator': ''}},
        assert test_cm.get_operator() == ''

    @pytest.mark.parametrize('test_input, expected', target_input_expected)
    def test_get_target_from_config(self, test_input, expected):
        test_cm.config = test_input
        assert test_cm.get_target() == expected

    @pytest.mark.parametrize('test_input, expected', target_metaconf_expected)
    def test_get_target_with_metaconf(self, test_input, expected):
        test_cm.config = test_input
        assert test_cm.get_target() == expected

    @pytest.mark.parametrize('test_input, expected', tanks_input_expected)
    def test_get_tank_meta(self, test_input, expected):
        test_cm.config = test_input
        assert test_cm.get_tank() == expected

    @pytest.mark.parametrize('test_input, expected', tanks_metaconf_expected)
    def test_get_tank_metaconf(self, test_input, expected):
        test_cm.config = test_input
        assert test_cm.get_tank() == expected

    def test_get_task(self):
        test_cm.config = {'uploader': {'task': 'LOAD-318'}}
        assert test_cm.get_task() == 'LOAD-318'

    def test_get_datacenter(self):
        test_cm.config = {'metaconf': {'firestarter': {'dc': 'sas'}}}
        assert test_cm.get_datacenter() == 'sas'
        test_cm.config = {'metaconf': {'firestarter': {'ddt': 'sas'}}}
        assert test_cm.get_datacenter() == ''
        test_cm.config = {'metaconf': {'enabled': False, 'firestarter': {'dc': 'sas'}}}
        assert test_cm.get_datacenter() is None

    @pytest.mark.skip
    def test_task_http_link(self):
        pass

    @pytest.mark.parametrize('test_input, expected', pandora_config_file_expected)
    def test_get_pandora_config_file(self, test_input, expected):
        test_cm.config = test_input
        assert test_cm.check_pandora_config_file() == expected


class TestParseTank:

    parse_tank_data = [
        ('', ('', '', '')),
        ('matilda.tanks.yandex.net', ('matilda.tanks.yandex.net', '', '')),
        ('nanny:production_yandex_tanks', ('', 'nanny:production_yandex_tanks', '')),
        ('nanny:production_market_tanks#market', ('', 'nanny:production_market_tanks', 'market'))
    ]

    @pytest.mark.parametrize('test_input, expected', parse_tank_data)
    def test_parse_tank(self, test_input, expected):
        assert expected == parse_tank(test_input)
