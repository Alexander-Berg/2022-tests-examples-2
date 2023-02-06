# -*- coding: utf-8 -*-
# В этом тесте не мокаются рактейблз и все гитовые операции
import json
import os
import shutil

from copy import deepcopy
from textwrap import dedent
from tempfile import mkdtemp

from django.conf import settings
from django.test import TestCase
from django.contrib.auth.models import User
from mock import patch, Mock

from passport_grants_configurator.apps.core.export_utils import OAuthExporter
from passport_grants_configurator.apps.core.models import Namespace
from passport_grants_configurator.apps.core.test.utils import (
    MockNetworkApi,
    MockUserPermissions,
    MockRequests,
    MockRedis,
    MockGit,
)
from ..test_data import *


class TestExport(TestCase):
    """Эти тесты заставляют выкачать git-репозитории с грантами проектов"""

    maxDiff = None
    fixtures = ['default.json']
    url = '/grants/export/'

    def setUp(self):
        self.patch_yenv = patch('passport_grants_configurator.apps.core.export_utils.yenv.type', 'development')
        self.patch_yenv.start()
        self.permissions = MockUserPermissions('passport_grants_configurator.apps.core.export_utils.UserPermissions')
        self.permissions.start()

        self.requests = MockRequests()
        self.requests.setup_bitbucket_last_commit_info()
        self.requests.start()
        self.redis = MockRedis()
        self.redis.start()
        self.git = MockGit(mock_pull=False)
        self.git.start()

        self.network_api = MockNetworkApi()
        self.network_api.start()

        self.network_api.setup_response(
            'expand_firewall_macro',
            {
                '_C_PASSPORT_GRANTUSHKA_STABLE_': [
                    TEST_GRANTS_IP1,
                    TEST_GRANTS_IP2,
                ],
                '_KOPALKA_': [
                    '37.140.181.0/28',
                    '87.250.232.64/27',
                    '93.158.133.0/26',
                    '95.108.158.0/26',
                    '95.108.225.128/26',
                    '178.154.221.128/25',
                    '2a02:6b8:0:212::/64',
                    '2a02:6b8:0:811::/64',
                    '2a02:6b8:0:c37::/64',
                    '2a02:6b8:0:142b::/64',
                    '2a02:6b8:0:1a41::/64',
                    '2a02:6b8:0:250b::/64',
                ],
            },
        )

        self.temp_dir = mkdtemp(prefix='/tmp/grantushka.')
        self.tree_to_rm = Mock()
        self.rmtree = patch('shutil.rmtree', self.tree_to_rm)
        self.rmtree.start()

    def tearDown(self):
        self.rmtree.stop()
        self.network_api.stop()
        self.git.stop()
        self.redis.stop()
        self.requests.stop()
        self.permissions.stop()
        self.patch_yenv.stop()

        shutil.rmtree(self.temp_dir)

    def assert_ok_response(self, response, status_code=200):
        self.assertEqual(response.status_code, status_code)
        parsed = json.loads(response.content)
        self.assertEqual(parsed['success'], True)

    def get_oauth_exporter(self, oauth_project):
        namespaces = Namespace.objects.filter(name='oauth')
        return OAuthExporter(
            namespaces=namespaces,
            user=User.objects.get(id=1),
            git_api=oauth_project['git_api'],
            env_filenames=oauth_project['file_names'],
        )

    def test_export_to_passport(self):

        passport_project = deepcopy(settings.GRANTS_PROJECTS['passport'])
        passport_project['git_api']['working_dir'] = self.temp_dir

        with self.settings(GRANTS_PROJECTS=dict(passport=passport_project)):
            resp = self.client.post(self.url, {'project_name': 'passport'})

            self.assert_ok_response(resp)

            dir_ = self.tree_to_rm.call_args[0][0]
            files = {
                'consumer_grants.development.json': {},
                'consumer_grants.intranet.development.json': {},
                'consumer_grants.intranet.production.json': {},
                'consumer_grants.intranet.testing.json': {},
                'consumer_grants.production.json': {
                    'consumer_with_client': {
                        'client': {
                            'client_id': 2,
                            'client_name': 'Test Passport Client With Consumer',
                        },
                        'grants': {},
                        'networks': [],
                    },
                    'some_consumer': {
                        'client': {},
                        'grants': {
                            'captcha': [
                                '*',
                            ],
                            'login': [
                                'suggest',
                                'validate',
                            ],
                            'password': [
                                'is_changing_required',
                            ],
                            'session': [
                                'check',
                                'create',
                            ],
                            'subscription': {
                                'something': [
                                    'create',
                                ],
                            },
                        },
                        'networks': [
                            '127.0.0.1',
                            '127.0.0.3',
                            '178.154.221.128/25',
                            '2a02:6b8:0:142b::/64',
                            '2a02:6b8:0:1a41::/64',
                            '2a02:6b8:0:212::/64',
                            '2a02:6b8:0:250b::/64',
                            '2a02:6b8:0:811::/64',
                            '2a02:6b8:0:c37::/64',
                            '37.140.181.0/28',
                            '77.88.40.96/28',
                            '87.250.232.64/27',
                            '93.158.133.0/26',
                            '95.108.158.0/26',
                            '95.108.225.128/26',
                        ],
                    },
                },
                'consumer_grants.stress.stress.json': {},
                'consumer_grants.testing.json': {},
            }
            for filename, content in files.items():
                fullname = os.path.join(dir_, 'grants', filename)
                with open(fullname) as f:
                    self.assertEqual(json.load(f), content)

    def test_export_to_yasms(self):

        yasms_project = deepcopy(settings.GRANTS_PROJECTS['yasms'])
        yasms_project['git_api']['working_dir'] = self.temp_dir

        with self.settings(GRANTS_PROJECTS=dict(yasms=yasms_project)):

            resp = self.client.post(self.url, {'project_name': 'yasms'})

            self.assert_ok_response(resp)

            dir_ = self.tree_to_rm.call_args[0][0]
            files = {
                'yasms_for_passport.development.json': {},
                'yasms_for_passport.testing.json': {},
                'yasms_for_passport.rc.json': {},
                'yasms_for_passport.production.json': {
                    'old_yasms_grants_yasms_consumer': {
                        'client': {},
                        'grants': {
                            'old_yasms_grants_yasms_grant': ['yasms_action'],
                        },
                        'networks': [
                            TEST_GRANTS_IP1,
                            TEST_GRANTS_IP2,
                            '2a02:6b8:0:107:c9d7:f28e:6e24:876f',
                            '2a02:6b8:0:811::/64',
                            '77.88.40.96/28',
                        ],
                    },
                    'old_yasms_grants_yasms_consumer_with_client': {
                        'grants': {
                            'old_yasms_grants_yasms_grant': ['yasms_action'],
                        },
                        'networks': [],
                        'client': {
                            'client_id': 1,
                            'client_name': 'Test Yasms Client With Consumer',
                        },
                    },
                },
            }
            for filename, content in files.items():
                fullname = os.path.join(dir_, 'grants', filename)
                with open(fullname) as f:
                    self.assertEqual(json.load(f), content)

    def test_export_to_blackbox(self):
        bb_project = deepcopy(settings.GRANTS_PROJECTS['blackbox'])
        bb_project['git_api']['working_dir'] = self.temp_dir

        with self.settings(GRANTS_PROJECTS=dict(blackbox=bb_project)):
            resp = self.client.post(self.url, {'project_name': 'blackbox'})

            self.assert_ok_response(resp)

            dir_ = self.tree_to_rm.call_args[0][0]
            files = {
                'grants-prod.conf': dedent('''\
                    <?xml version='1.0' encoding='utf-8'?>
                    <peers>
                      <entry id="%s; %s">
                        <name>bb_consumer</name>
                        <allow_check_sign>oauth_otp,passport_otp</allow_check_sign>
                        <allow_sign>oauth_otp,passport_otp</allow_sign>
                        <allowed_attributes>16,17</allowed_attributes>
                        <allowed_phone_attributes>1,2</allowed_phone_attributes>
                        <bb_grant>bb_action</bb_grant>
                        <can_captcha/>
                        <can_delay>1000</can_delay>
                        <dbfield id="tablename.field_name.1337"/>
                      </entry>
                    </peers>
                    ''') % (TEST_GRANTS_IP1, TEST_GRANTS_IP2),
                'grants-dev.conf': '''<?xml version='1.0' encoding='utf-8'?>\n<peers/>\n''',
                'grants-test.conf': dedent('''\
                    <?xml version='1.0' encoding='utf-8'?>
                    <peers>
                      <entry id="%s; %s">
                        <name>bb_consumer</name>
                        <bb_grant>bb_action</bb_grant>
                      </entry>
                    </peers>
                    ''') % (TEST_GRANTS_IP1, TEST_GRANTS_IP2),
                'grants-stress.conf': '''<?xml version='1.0' encoding='utf-8'?>\n<peers/>\n''',
                'grants-yateam.conf': '''<?xml version='1.0' encoding='utf-8'?>\n<peers/>\n''',
                'grants-mimino.conf': '''<?xml version='1.0' encoding='utf-8'?>\n<peers/>\n''',
            }
            for filename, content in files.items():
                fullname = os.path.join(dir_, 'grants', filename)
                with open(fullname) as f:
                    self.assertEqual(f.read(), content)

    def test_export_to_social(self):

        social_project = deepcopy(settings.GRANTS_PROJECTS['social'])
        social_project['git_api']['working_dir'] = self.temp_dir

        with self.settings(GRANTS_PROJECTS=dict(social=social_project)):

            resp = self.client.post(self.url, {'project_name': 'social'})

            self.assert_ok_response(resp)

            dir_ = self.tree_to_rm.call_args[0][0]
            files = {
                'social_grants/production/social-api2.json': {
                    'social_api_consumer': {
                        'networks': [TEST_GRANTS_IP1, TEST_GRANTS_IP2],
                        'grants': [
                            'social_api_grant-social_api_action',
                            'social_api_grant_with_asterisk',
                        ],
                        'client': {},
                    },
                    'social_api_consumer_with_client': {
                        'networks': [],
                        'grants': [
                            'social_api_grant-social_api_action',
                        ],
                        'client': {
                            'client_id': 1,
                            'client_name': 'Test Social API Client With Consumer',
                        },
                    },
                },
                'social_grants/testing/social-api2.json': {},
                'social_grants/development/social-api2.json': {},
                'social_grants/production/social-proxy.json': {
                    'social_proxy_consumer': {
                        'networks': [TEST_GRANTS_IP1, TEST_GRANTS_IP2],
                        'grants': ['socia_proxy_grant'],
                        'client': {},
                    },
                    'social_proxy_consumer_with_client': {
                        'networks': [],
                        'grants': ['socia_proxy_grant'],
                        'client': {
                            'client_id': 1,
                            'client_name': 'Test Social Proxy Client With Consumer',
                        },
                    },
                },
                'social_grants/testing/social-proxy.json': {},
                'social_grants/development/social-proxy.json': {},
            }
            for filename, content in files.items():
                fullname = os.path.join(dir_, filename)
                with open(fullname) as f:
                    self.assertEqual(json.load(f), content)

    def test_simulate_export_to_oauth(self):

        oauth_project = deepcopy(settings.GRANTS_PROJECTS['oauth'])
        oauth_project['git_api']['working_dir'] = self.temp_dir

        with self.settings(GRANTS_PROJECTS=dict(oauth=oauth_project)):

            exporter = self.get_oauth_exporter(oauth_project)
            exporter.simulate()

            dir_ = self.tree_to_rm.call_args[0][0]
            files = {
                'grants/scope_grants.production.json': {
                    'oauth_consumer': {
                        'client': {},
                        'grants': {
                            'client': [
                                '*'
                            ],
                            'grant_type': [
                                'assertion'
                            ]
                        },
                        'networks': [
                            '127.0.0.1'
                        ]
                    },
                    'oauth_consumer_with_client': {
                        'client': {
                            'client_id': 1,
                            'client_name': 'Test Oauth Client With Consumer',
                        },
                        'grants': {
                            'grant_type': [
                                'assertion'
                            ],
                        },
                        'networks': [],
                    },
                },
                'grants/scope_grants.testing.json': {},
                'grants/scope_grants.development.json': {},
                'grants/scope_grants.intranet.production.json': {},
            }
            for filename, content in files.items():
                fullname = os.path.join(dir_, filename)
                with open(fullname) as f:
                    self.assertEqual(json.load(f), content)

    @patch('passport_grants_configurator.apps.core.export_utils.check_grants')
    def test_export_with_script_checker_errors(self, check_grants_mock):

        check_grants_mock.return_value = {'production': {'oauth_consumer': u'Воу! Ошибка'}}

        oauth_project = deepcopy(settings.GRANTS_PROJECTS['oauth'])
        oauth_project['git_api']['working_dir'] = self.temp_dir

        with self.settings(GRANTS_PROJECTS=dict(oauth=oauth_project)):
            exporter = self.get_oauth_exporter(oauth_project)
            resp = exporter.simulate()
            self.assertEqual(
                resp['manual_resolve'],
                [
                    u'ОШИБКА - в окружении production для потребителя oauth_consumer '
                    u'при дополнительной валидации были выявлены ошибки: Воу! Ошибка',
                ]
            )
            self.assertFalse(resp['diff'])

    @patch('passport_grants_configurator.apps.core.export_utils.check_grants')
    def test_export_with_script_checker_ok(self, check_grants_mock):

        check_grants_mock.return_value = {}

        oauth_project = deepcopy(settings.GRANTS_PROJECTS['oauth'])
        oauth_project['git_api']['working_dir'] = self.temp_dir

        with self.settings(GRANTS_PROJECTS=dict(oauth=oauth_project)):
            exporter = self.get_oauth_exporter(oauth_project)
            resp = exporter.simulate()

            self.assertFalse(resp['manual_resolve'])

            self.assertTrue(bool(resp['diff']))
