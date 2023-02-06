# coding: utf-8

from collections import OrderedDict
import re

from passport.backend.vault.cli.yav_deploy.tests.base import (
    BaseYavDeployTestCase,
    FakeSection,
    LogMock,
    TEST_SECRETS_RESPONSES,
)
from vault_client_deploy.actions import (
    ActionError,
    FileTemplateAction,
    MultiFileAction,
    SingleFileAction,
    UnknownFileAction,
)
from vault_client_deploy.configs import DeployConfig


class TestFakeSecretsApi(BaseYavDeployTestCase):
    def test_get_secrets(self):
        with self.get_environment('base', type_='unknown', name='unknown') as env:
            secrets_storage = env.get_secrets_storage()
            with self.mock_secrets(TEST_SECRETS_RESPONSES):
                self.assertEqual(
                    secrets_storage.vault_client.ping().text,
                    'Mocked ping',
                )
                self.assertEqual(
                    secrets_storage.vault_client.get_status(),
                    {u'status': u'ok', u'_mocked': True, u'is_deprecated_client': False},
                )
                for secret_uuid in TEST_SECRETS_RESPONSES:
                    self.assertListEqual(
                        secrets_storage.get(secret_uuid, packed_value=False),
                        TEST_SECRETS_RESPONSES[secret_uuid]['version']['value'],
                    )


class TestUnknownFileAction(BaseYavDeployTestCase):
    def test_unknown_file_action(self):
        with self.get_environment('base', type_='unknown', name='unknown') as env:
            with self.assertRaises(ActionError) as e:
                UnknownFileAction(
                    FakeSection(env),
                    env.get_secrets_storage(),
                    'action target',
                    'action source',
                )
            self.assertEqual(
                str(e.exception),
                'UnknownFileAction<action target = action source>: '
                'Unknown file action: action target = action source',
            )


class TestFileTemplateAction(BaseYavDeployTestCase):
    def test_render_multiple_secrets_action(self):
        with self.get_environment('templates', type_='unknown', name='unknown') as env:
            conf = DeployConfig(env, env.confs[0])
            section = conf.sections['template with multiple secrets']
            action = section.actions['/test.file']
            self.assertListEqual(
                list(action.template_secrets.items()),
                [
                    ('sec-90000000000000000000000001', {'add_keys': False, 'aliases': {'secret1'}, 'keys': set()}),
                    ('sec-90000000000000000000000002', {'add_keys': True, 'aliases': set(), 'keys': {'login', 'password'}}),
                    ('ver-90000000000000000000000004', {'add_keys': True, 'aliases': set(), 'keys': set()}),
                ],
            )

            self.assertListEqual(
                list(sorted(action.data.items())),
                [
                    ('DB_LOGIN', 'passport_db'),
                    ('DB_PASSWORD', 'fksdjfw348jdsjfsdlkgj@fsdg'),
                    ('login', 'arhibot'),
                    ('password', '564323123'),
                    ('secret1', OrderedDict([('login', 'ppodolsky'), ('password', '123455')])),
                ],
            )

            self.assertDictEqual(
                action.get_jenv(),
                {
                    'GLOBAL_VAR': 'global var',
                    'LOCAL_VAR_1': 'local var 1',
                    'localVar2': 'local var 2',
                    'secret1': 'my_login',
                },
            )

            action.prepare()
            action.commit()
            self.assertEnvOperations(
                env,
                [{
                    'args': (
                        '/test.file',
                        b'unknown\n'
                        b'unknown\n'
                        b'\n'
                        b'    login -> ppodolsky\n'
                        b'    password -> 123455\n'
                        b'\n'
                        b'DATABASE_LOGIN = passport_db\n'
                        b'DATABASE_PASSOWRD = fksdjfw348jdsjfsdlkgj@fsdg\n'
                        b'\n'
                        b'GLOBAL_VAR = global var\n'
                        b'LOCAL_VAR_1 = local var 1\n'
                        b'localVar2 = local var 2\n'
                        b'\n'
                        b'local_password = 564323123\n'
                    ),
                    'kwargs': {'force': False, 'owner': None, 'permissions': None},
                    'name': 'save_file',
                }],
            )

    def test_templates_filters(self):
        with self.get_environment('templates', type_='unknown', name='unknown') as env:
            conf = DeployConfig(env, env.confs[0])
            section = conf.sections['template with filters']
            action = section.actions['/test.file']

            action.prepare()
            action.commit()
            self.assertEnvOperations(
                env,
                [{
                    'args': (
                        '/test.file',
                        b'unknown\n'
                        b'unknown\n'
                        b'\n'
                        b'\n'
                        b'LOGIN = arhibot\n'
                        b'PASSWORD = 564323123\n'
                        b'\n'
                        b'TOKEN_1 = token 1\n'
                        b'TOKEN_2 = token 2\n'
                    ),
                    'kwargs': {'force': False, 'owner': None, 'permissions': None},
                    'name': 'save_file',
                }],
            )

    def test_fail_if_secret_hasnt_keys(self):
        with self.get_environment('empty', type_='unknown', name='unknown') as env:
            with self.assertRaises(ActionError) as e:
                FileTemplateAction(
                    FakeSection(env),
                    env.get_secrets_storage(),
                    '/dest.ext',
                    'template.tpl:sec-90000000000000000000000002[login, name]',
                )
            self.assertEqual(
                str(e.exception),
                'FileTemplateAction</dest.ext = template.tpl:sec-90000000000000000000000002[login, name]>: '
                'The keys matched the "name" template is not found in the secret "sec-90000000000000000000000002"',
            )

    def test_multiple_secrets_with_some_uuid(self):
        with self.get_environment('empty', type_='unknown', name='unknown') as env:
            action = FileTemplateAction(
                FakeSection(env),
                env.get_secrets_storage(),
                '/dest.ext',
                'template.tpl:sec-90000000000000000000000002->alias1[login], sec-90000000000000000000000002->alias2[password], sec-90000000000000000000000002',
            )
            self.assertDictEqual(
                action.template_secrets,
                {
                    'sec-90000000000000000000000002': {
                        'add_keys': True,
                        'keys': set(['login', 'password']),
                        'aliases': set(['alias1', 'alias2']),
                    },
                },
            )
            self.assertDictEqual(
                action.data,
                {
                    u'alias2': {u'login': u'arhibot', u'password': u'564323123'},
                    u'alias1': {u'login': u'arhibot', u'password': u'564323123'},
                    u'login': u'arhibot',
                    u'password': u'564323123',
                }
            )

    def test_warning_if_secrets_contains_files(self):
        logger = LogMock()
        warn_re = re.compile(r'^\[template with files\] Warning:')

        with self.get_environment('templates', type_='unknown', name='unknown', logger=logger) as env:
            conf = DeployConfig(env, env.confs[0])
            section = conf.sections['template with files']
            action = section.actions['/test.wfile']
            action.prepare()
            self.assertListEqual(
                list(
                    sorted(
                        filter(
                            lambda x: warn_re.match(x[0]) is not None,
                            logger.entries,
                        ),
                        key=lambda x: x[0],
                    ),
                ),
                [("[template with files] Warning: sec-90000000000000000000000004[test2.crt] contains a binary file. Don't use this key in the template",
                  'DEBUG'),
                 ("[template with files] Warning: sec-90000000000000000000000004[test2.key] contains a binary file. Don't use this key in the template",
                  'DEBUG'),
                 ("[template with files] Warning: sec-90000000000000000000000005[new_test.crt] contains a binary file. Don't use this key in the template",
                  'DEBUG'),
                 ("[template with files] Warning: sec-90000000000000000000000005[new_test.key] contains a binary file. Don't use this key in the template",
                  'DEBUG')],
            )


class TestSingleFileAction(BaseYavDeployTestCase):
    def test_single_file_action_ok(self):
        with self.get_environment('base', type_='unknown', name='unknown') as env:
            section = FakeSection(
                env,
                dict(
                    mode='0444',
                    owner='www:www',
                )
            )
            action = SingleFileAction(
                section,
                env.get_secrets_storage(),
                '/test.key',
                'sec-90000000000000000000000004[test.key]',
            )
            action.prepare()
            action.commit()
            self.assertEnvOperations(
                env,
                [{
                    'args': ('/test.key', 'key file'),
                    'kwargs': {'force': False, 'owner': 'www:www', 'permissions': 0o0444},
                    'name': 'save_file'
                }],
            )

    def test_single_file_action_witn_encoded_value_ok(self):
        with self.get_environment('base', type_='unknown', name='unknown') as env:
            action = SingleFileAction(
                FakeSection(env),
                env.get_secrets_storage(),
                '/test2.key:0444',
                'sec-90000000000000000000000004[test2.key]',
            )
            action.prepare()
            action.commit()
            self.assertEnvOperations(
                env,
                [{
                    'args': ('/test2.key', b'key file'),
                    'kwargs': {'force': False, 'owner': None, 'permissions': 0o0444},
                    'name': 'save_file'
                }],
            )

    def test_file_not_found_in_secret_error(self):
        with self.get_environment('base', type_='unknown', name='unknown') as env:
            with self.assertRaises(ActionError) as e:
                SingleFileAction(
                    FakeSection(env),
                    env.get_secrets_storage(),
                    '/test.key',
                    'sec-90000000000000000000000004[new_test.key]',
                )
            self.assertEqual(
                str(e.exception),
                'SingleFileAction</test.key = sec-90000000000000000000000004[new_test.key]>: '
                'The keys matched the "new_test.key" template is not found in the secret "sec-90000000000000000000000004"',
            )

    def test_multiple_keys_in_source(self):
        with self.get_environment('base', type_='unknown', name='unknown') as env:
            with self.assertRaises(ActionError) as e:
                SingleFileAction(
                    FakeSection(env),
                    env.get_secrets_storage(),
                    '/test.key',
                    'sec-90000000000000000000000004[test.key, test2.key]',
                )
            self.assertEqual(
                str(e.exception),
                'SingleFileAction</test.key = sec-90000000000000000000000004[test.key, test2.key]>: '
                'The source must contain a single key value',
            )


class TestMultiFileAction(BaseYavDeployTestCase):
    def test_single_secret_ok(self):
        with self.get_environment('base', type_='unknown', name='unknown') as env:
            action = MultiFileAction(
                FakeSection(env),
                env.get_secrets_storage(),
                '/*:0444',
                'sec-90000000000000000000000004[test.key, *.crt]',
            )
            action.prepare()
            action.commit()
            self.assertEnvOperations(
                env,
                [
                    {'args': ('/test.crt', 'cert file'),
                     'kwargs': {'force': False, 'owner': None, 'permissions': 0o0444},
                     'name': 'save_file'},
                    {'args': ('/test.key', 'key file'),
                     'kwargs': {'force': False, 'owner': None, 'permissions': 0o0444},
                     'name': 'save_file'},
                    {'args': ('/test2.crt', b'cert file'),
                     'kwargs': {'force': False, 'owner': None, 'permissions': 0o0444},
                     'name': 'save_file'},
                ],
            )

    def test_multiple_secrets_ok(self):
        with self.get_environment('base', type_='unknown', name='unknown') as env:
            section = FakeSection(
                env,
                dict(
                    mode='0444',
                    owner='www:www',
                )
            )
            action = MultiFileAction(
                section,
                env.get_secrets_storage(),
                '/*',
                'sec-90000000000000000000000004[*.crt],'
                'sec-90000000000000000000000005[new*],'
                'sec-90000000000000000000000004[*.key,test2.key],'
            )
            action.prepare()
            action.commit()
            self.assertEnvOperations(
                env,
                [
                    {'args': ('/new_test.crt', b'cert file'),
                     'kwargs': {'force': False, 'owner': 'www:www', 'permissions': 0o0444},
                     'name': 'save_file'},
                    {'args': ('/new_test.key', b'key file'),
                     'kwargs': {'force': False, 'owner': 'www:www', 'permissions': 0o0444},
                     'name': 'save_file'},
                    {'args': ('/test.crt', 'cert file'),
                     'kwargs': {'force': False, 'owner': 'www:www', 'permissions': 0o0444},
                     'name': 'save_file'},
                    {'args': ('/test.key', 'key file'),
                     'kwargs': {'force': False, 'owner': 'www:www', 'permissions': 0o0444},
                     'name': 'save_file'},
                    {'args': ('/test2.crt', b'cert file'),
                     'kwargs': {'force': False, 'owner': 'www:www', 'permissions': 0o0444},
                     'name': 'save_file'},
                    {'args': ('/test2.key', b'key file'),
                     'kwargs': {'force': False, 'owner': 'www:www', 'permissions': 0o0444},
                     'name': 'save_file'},
                ],
            )

    def test_fail_if_secret_hasnt_keys(self):
        with self.get_environment('empty', type_='unknown', name='unknown') as env:
            with self.assertRaises(ActionError) as e:
                MultiFileAction(
                    FakeSection(env),
                    env.get_secrets_storage(),
                    '/*',
                    'sec-90000000000000000000000002[login, *.crt]',
                )
            self.assertEqual(
                str(e.exception),
                'MultiFileAction</* = sec-90000000000000000000000002[login, *.crt]>: '
                'The keys matched the "*.crt" template is not found in the secret "sec-90000000000000000000000002"',
            )
