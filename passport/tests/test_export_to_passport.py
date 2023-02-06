# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json
from StringIO import StringIO

from django.conf import settings
from django.contrib.auth.models import User
from django.core.management import call_command
from django.test import TestCase
from mock import patch, Mock, mock_open

import passport_grants_configurator.apps.core.export_utils as export_utils
from passport_grants_configurator.apps.core.exceptions import (
    NetworkResolveError,
    ExportError,
    ProcessError,
)
from passport_grants_configurator.apps.core.models import (
    Environment,
    Namespace,
)
from passport_grants_configurator.apps.core.test.utils import (
    MockNetworkApi,
    MockRequests,
    MockRedis,
    MockUserPermissions,
)

TEST_LAST_COMMIT_HASH = '4cc7abc9d5197e3ca07652494c0200f3778db86a'

TEST_KOPALKA_MACROS = [
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
]


class TestExportPassport(TestCase):
    maxDiff = None
    fixtures = ['default.json']
    _data = settings.GRANTS_PROJECTS['passport']
    safe_git_api = {
        'project': 'passport',
        'committer': {'DEBEMAIL': 'passport-admin@yandex-team.ru', 'DEBFULLNAME': 'Passport Grants Robot'},
        'working_dir': '/tmp/passport-grants-configurator/exports/passport-grants/',
        'api_token': 'd19f6b2e2eab6ad6b723534f9e1e6312073accfc',
        'commits': 'https://bb.yandex-team.ru/rest/api/1.0/projects/tvm/repos/passport-grants/commits',
        'api_timeout': 1,
        'repo': None,
    }

    def setUp(self):
        self.requests = MockRequests()
        self.requests.start()
        self.redis = MockRedis()
        self.redis.start()

        self.network_api = MockNetworkApi()
        self.network_api.start()

        self.user = User.objects.get(id=1)
        self.namespaces = Namespace.objects.filter(name='passport')
        self.environments = Environment.objects.filter(namespace__in=self.namespaces)

        self.mock_user_permissions = MockUserPermissions(
            'passport_grants_configurator.apps.core.export_utils.UserPermissions'
        )
        self.mock_user_permissions.start()

        self.file_mock = StringIO()
        self.environment = Environment.objects.get(id=1)  # production localhost

    def create_patch(self, *args, **kwargs):
        patcher = patch(*args, **kwargs)
        thing = patcher.start()
        self.addCleanup(patcher.stop)
        return thing

    def tearDown(self):
        self.mock_user_permissions.stop()
        self.network_api.stop()
        self.redis.stop()
        self.requests.stop()

    def get_exporter(self):
        return export_utils.PassportExporter(
            namespaces=self.namespaces,
            git_api=self.safe_git_api,
            user=self.user,
            env_filenames=self._data['file_names'],
        )

    @property
    def expected_response(self):
        return {
            'consumer_with_client': {
                'client': {
                    'client_id': 2,
                    'client_name': u'Test Passport Client With Consumer',
                },
                u'grants': {},
                u'networks': [],
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
        }

    def setup_bitbucket_last_commit_info(self, commit_hash=TEST_LAST_COMMIT_HASH):
        self.requests.response.text = '{"values": [{"id": "%s"}]}' % commit_hash

    def test_export(self):
        # Раскроем макрос _KOPALKA_
        self.network_api.setup_response(
            'expand_firewall_macro',
            {
                '_KOPALKA_': TEST_KOPALKA_MACROS,
            },
        )

        export_utils.export_passport_like_grants_to_file(self.environment, self.file_mock)

        actual = json.loads(''.join(self.file_mock.buflist))
        self.assertEqual(actual, self.expected_response)

    def test_export_after_resolving(self):
        # Раскроем макрос _KOPALKA_
        self.network_api.setup_response(
            'expand_firewall_macro',
            {
                '_KOPALKA_': TEST_KOPALKA_MACROS,
            },
        )

        call_command('resolve_networks')
        export_utils.export_passport_like_grants_to_file(self.environment, self.file_mock)

        actual = json.loads(''.join(self.file_mock.buflist))
        self.assertEqual(actual, self.expected_response)

    def test_network_resolver_error(self):
        test_error_message = 'test-error-message'

        with patch('passport_grants_configurator.apps.core.network_apis.NetworkResolver.get_ips',
                   Mock(side_effect=NetworkResolveError(test_error_message))):
            exported = export_utils.export_passport_like_grants_to_file(self.environment, self.file_mock)

            manual_resolve = map(
            lambda s: s % test_error_message,
            [
                u'ОШИБКА - сеть "127.0.0.1", потребитель "some_consumer": %s',
                u'ОШИБКА - сеть "127.0.0.3", потребитель "some_consumer": %s',
                u'ОШИБКА - сеть "77.88.40.96/28", потребитель "some_consumer": %s',
                u'ОШИБКА - сеть "_KOPALKA_", потребитель "some_consumer": %s',
            ]
        )
        self.assertEqual(exported, {
            'errors': [],
            'warnings': [],
            'manual_resolve': manual_resolve,
        })

    def test_no_environment_namespaces(self):
        self.setup_bitbucket_last_commit_info()
        exporter = export_utils.PassportExporter(
            namespaces=[],
            git_api=self.safe_git_api,
            user=self.user,
            env_filenames=self._data['file_names'],
        )

        patch_yenv = patch('yenv.type', 'production')
        with self.assertRaises(ExportError) as assertion, patch_yenv:
            exporter.prepare()

        self.assertEqual(
            assertion.exception.message,
            [u'У Вас нет прав для совершения данной операции']
        )

    def test_lock_file_exists__error(self):
        self.setup_bitbucket_last_commit_info()
        exporter = self.get_exporter()

        patch_yenv = patch('yenv.type', 'production')
        patch_lock_check = patch('os.path.exists', Mock(return_value=True))
        with self.assertRaises(ExportError) as assertion, patch_lock_check, patch_yenv:
            exporter.prepare()

        self.assertEqual(
            assertion.exception.message,
            [u'Предыдущая выгрузка грантов еще не завершена'],
        )

    def test_directory_no_access__error(self):
        self.setup_bitbucket_last_commit_info()
        exporter = self.get_exporter()

        patch_yenv = patch('yenv.type', 'production')
        patch_makedirs = patch('os.makedirs', Mock(side_effect=OSError))
        with self.assertRaises(ExportError) as assertion, patch_makedirs, patch_yenv:
            exporter.prepare()

        self.assertEqual(len(assertion.exception.message), 1)
        # В сообщении будет путь к временной директории - проверяем только базовую часть пути
        message = u'Нет доступа к директории для работы с дистрибутивом %s' % self.safe_git_api['working_dir']
        self.assertTrue(
            message in assertion.exception.message[0],
        )

    def test_import_subprocess_error__error(self):
        self.setup_bitbucket_last_commit_info()
        exporter = self.get_exporter()

        patch_git_pull = patch(
            'passport_grants_configurator.apps.core.export_utils.git_pull',
            Mock(side_effect=ProcessError('test error text'))
        )
        with self.assertRaises(ExportError) as assertion, patch_git_pull:
            exporter.import_grants()

        self.assertEqual(
            assertion.exception.message,
            ['test error text']
        )

    def test_error_during_update(self):
        exporter = self.get_exporter()

        open_patch = patch('passport_grants_configurator.apps.core.export_utils.open', mock_open(), create=True)
        with self.assertRaises(ExportError) as assertion, open_patch:
            exporter.export_function = Mock(
                return_value={
                    'errors': ['test error text'],
                    'warnings': [],
                    'manual_resolve': [],
                })
            exporter.update_grants()

        self.assertEqual(
            assertion.exception.message,
            ['test error text']
        )

    def test_no_diff(self):
        self.network_api.setup_response(
            'expand_firewall_macro',
            {
                '_KOPALKA_': ['37.140.181.0/28'],
            },
        )
        exporter = self.get_exporter()

        open_patch = self.create_patch('passport_grants_configurator.apps.core.export_utils.open', mock_open(), create=True)
        git_status_patch = self.create_patch('passport_grants_configurator.apps.core.export_utils.git_status', Mock(return_value=''))
        git_diff_patch = self.create_patch('passport_grants_configurator.apps.core.export_utils.git_diff', Mock(return_value=''))
        with self.assertRaises(ExportError) as assertion:
            exporter.update_grants()

        self.assertEqual(
            assertion.exception.message,
            [u'В экспортированных грантах не найдено изменений по сравнению с грантами из репозитория']
        )

    def test_error_during_changelog(self):
        self.network_api.setup_response(
            'expand_firewall_macro',
            {
                '_KOPALKA_': ['37.140.181.0/28'],
            },
        )
        exporter = self.get_exporter()

        open_patch = self.create_patch('passport_grants_configurator.apps.core.export_utils.open', mock_open(), create=True)
        git_status_patch = self.create_patch('passport_grants_configurator.apps.core.export_utils.git_status', Mock(return_value=''))
        git_diff_patch = self.create_patch('passport_grants_configurator.apps.core.export_utils.git_diff', Mock(return_value='+1'))
        with self.assertRaises(ExportError) as assertion:
            exporter.update_grants()

        self.assertEqual(
            assertion.exception.message,
            ['Не удалось обновить версию пакета, вызов dch вернул ошибку: No such file or directory']
        )

    def test_add_files(self):
        self.network_api.setup_response(
            'expand_firewall_macro',
            {
                '_KOPALKA_': ['37.140.181.0/28'],
            },
        )
        exporter = self.get_exporter()

        open_patch = self.create_patch('passport_grants_configurator.apps.core.export_utils.open', mock_open(), create=True)
        git_status_patch = self.create_patch(
            'passport_grants_configurator.apps.core.export_utils.git_status',
            Mock(return_value=
            """
            # On branch master
            # Your branch is up-to-date with 'origin/master'.
            #
            # Changes not staged for commit:
            #   (use "git add <file>..." to update what will be committed)
            #   (use "git checkout -- <file>..." to discard changes in working directory)
            #
            #	modified:   grants/consumer_grants.development.json
            #	modified:   grants/consumer_grants.testing.json
            #
            # Untracked files:
            #   (use "git add <file>..." to include in what will be committed)
            #
            #	grants/consumer_grants.intranet.testing.json
            #
            no changes added to commit (use "git add" and/or "git commit -a")
            """),
        )
        git_add_patch = self.create_patch('passport_grants_configurator.apps.core.export_utils.git_add', Mock(return_value=1))
        git_diff_patch = self.create_patch('passport_grants_configurator.apps.core.export_utils.git_diff', Mock(return_value='+1'))
        deb_changelog_pathc = self.create_patch('passport_grants_configurator.apps.core.export_utils.deb_changelog', Mock(return_value=1))
        exporter.update_grants()
        self.assertEqual(git_add_patch.call_count, 1)

    def test_export_grants_error(self):
        exporter = self.get_exporter()

        open_patch = patch('passport_grants_configurator.apps.core.export_utils.open', mock_open(), create=True)
        git_push_patch = patch(
            'passport_grants_configurator.apps.core.export_utils.git_push',
            Mock(side_effect=ProcessError('test error text'))
        )
        with self.assertRaises(ExportError) as assertion, open_patch, git_push_patch:
            exporter.export_grants()

        self.assertEqual(
            assertion.exception.message,
            ['test error text']
        )

    def test_cleanup_oserror(self):
        exporter = self.get_exporter()
        exporter.lock_file = None

        os_remove_patch = patch(
            'passport_grants_configurator.apps.core.export_utils.os.remove',
            Mock(side_effect=OSError('test error text'))
        )

        with os_remove_patch:
            exporter.cleanup()
