# coding: utf-8

from passport.backend.vault.cli.yav_deploy.tests.base import (
    BaseYavDeployTestCase,
    TEST_SECRETS_RESPONSES,
)
from vault_client_deploy.configs import DeployConfig


DEFAULTS_CONF_PATH = 'default'


class TestCreateEnvironement(BaseYavDeployTestCase):
    def test_create_minimum_environment(self):
        with self.get_environment('base', type_='unknown', name='unknown') as env:
            self.assertListEqual(
                env.confs,
                ['defaults.conf'],
            )

    def test_create_environment_by_type(self):
        with self.get_environment('base', type_='testing', name='localhost') as env:
            self.assertListEqual(
                env.confs,
                ['testing.conf'],
            )

    def test_create_environment_by_environments_conf(self):
        with self.get_environment('base', type_='development', name='localhost') as env:
            self.assertListEqual(
                env.confs,
                ['dev.conf'],
            )

    def test_create_environment_by_multiple_environments_conf(self):
        with self.get_environment('base', type_='multitype', name='multiname') as env:
            self.assertListEqual(
                env.confs,
                ['dev.conf'],
            )

    def test_create_environment_by_files_list(self):
        with self.get_environment(
            'base', type_='development', name='localhost',
            config_files=['production.conf', 'testing.conf', 'unknown.conf'],
        ) as env:
            self.assertListEqual(
                env.confs,
                ['production.conf', 'testing.conf'],
            )

    def test_create_environment_with_tags(self):
        with self.get_environment('tags', type_='development', name='localhost') as env:
            self.assertEqual(
                env.tags,
                set(['passport.blackbox', 'passport.grantushka', 'passport.vault', 'some_tags']),
            )
            self.assertListEqual(
                env.confs,
                ['dev.conf', 'testing.conf'],
            )

    def test_create_environment_with_tags_from_env(self):
        with self.mock_env(dict(YAV_DEPLOY_TAGS='tag1, tag2, tag3,,,tag5,tag7')):
            with self.get_environment('tags', type_='development', name='localhost') as env:
                self.assertEqual(
                    env.tags,
                    set(['tag1', 'tag2', 'tag3', 'tag5', 'tag7']),
                )

    def test_create_environment_with_deprecated_tags_from_env(self):
        with self.mock_env(dict(YAV_DEPLOY_TAGS='tag1, conductor.tag2, tag3,,,tag5,tag7')):
            with self.assertRaises(ValueError) as e:
                with self.get_environment('tags', type_='development', name='localhost'):
                    pass
            self.assertEqual(
                str(e.exception),
                'conductor. is a reserved tags prefix',
            )


class TestDeployConfig(BaseYavDeployTestCase):
    def test_create_deploy_config(self):
        with self.get_environment('base', type_='development', name='localhost', config_files=['dev.conf']) as env:
            with self.mock_secrets(TEST_SECRETS_RESPONSES):
                dc = DeployConfig(env, env.confs[0])
                self.assertListEqual(
                    sorted(dc.sections.keys()),
                    ['backend', 'frontend', 'tvm2'],
                )

    def test_create_deploy_config_with_limited_sections(self):
        with self.get_environment('base', type_='development', name='localhost', config_files=['dev.conf']) as env:
            with self.mock_secrets(TEST_SECRETS_RESPONSES):
                dc = DeployConfig(env, env.confs[0], valid_sections=['backend', 'tvm2', 'unknown'])
                self.assertListEqual(
                    sorted(dc.sections.keys()),
                    ['backend', 'tvm2'],
                )

    def test_detect_actions(self):
        with self.get_environment('base', type_='development', name='localhost', config_files=['dev.conf']) as env:
            with self.mock_secrets(TEST_SECRETS_RESPONSES):
                dc = DeployConfig(env, env.confs[0])
                section = dc.sections['frontend']
                self.assertTrue(section.has_actions)
                self.assertListEqual(
                    [repr(v) for v in section.actions.values()],
                    [
                        'SingleFileAction</file.name = sec-90000000000000000000000004[test.key]>',
                        'MultiFileAction</. = sec-90000000000000000000000004[*]>',
                        'MultiFileAction</* = sec-90000000000000000000000004[*]>',
                        'SingleFileAction</path/to/files/ = sec-90000000000000000000000004[test.key]>',
                        'MultiFileAction</path/to/files/. = sec-90000000000000000000000004[*]>',
                        'MultiFileAction</path/to/files/* = sec-90000000000000000000000004[*]>',
                        'MultiFileAction</path/to/new_files/. = sec-90000000000000000000000004[*], '
                        'sec-90000000000000000000000005[*.crt, new_test.key]>',
                        'FileTemplateAction</settings1.py = settings.py:ver-90000000000000000000000004>',
                    ],
                )
