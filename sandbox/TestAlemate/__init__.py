# coding: utf-8
import os
import logging

from sandbox.common.types.client import Tag
from sandbox.projects.common import environments
from sandbox.sandboxsdk.task import SandboxTask
from sandbox.sandboxsdk.parameters import SandboxStringParameter
from sandbox.sandboxsdk.process import run_process


class GitRefIdParameter(SandboxStringParameter):
    name = 'ref_id'
    description = 'Git ref id'
    default_value = 'master'
    required = True


class GitRefShaParameter(SandboxStringParameter):
    name = 'ref_sha'
    description = 'Git ref SHA'
    default_value = ''
    required = False


class AlemateTestRunner(object):

    GIT_URL = 'https://{username}:{password}@bb.yandex-team.ru/scm/nanny/alemate.git'

    @classmethod
    def checkout(cls, oauth_token, dest, ref=None):
        checkout_url = cls.GIT_URL.format(username='x-oauth-token', password=oauth_token)
        run_process(
            ['git', 'clone', checkout_url, dest],
            log_prefix='git_clone',
            shell=True,
        )
        if ref is not None:
            run_process(
                ['git', 'checkout', ref],
                work_dir=dest,
                log_prefix='git_checkout',
                shell=True)

    @staticmethod
    def run_tests(task_context, virtualenv_path, sources_path, test_script, timeout):
        """
        Запуск скрипта тестов :param test_script: в директории с исходниками с таймаутом :param timeout:
        """
        env = dict(os.environ)
        path_parts = [os.path.join(virtualenv_path, 'bin')]
        if 'PATH' in env:
            path_parts.append(env['PATH'])
        env_path = ':'.join(path_parts)
        env.update({'PATH': env_path})

        # set do_not_restart to let gobabygo know that a tests failure
        # must not be restarted
        old_do_not_restart = task_context['do_not_restart']
        task_context['do_not_restart'] = True
        process = run_process(
            [
                os.path.join('.', test_script),
                '--zookeeper={}'.format(os.environ['ZOOKEEPER_DIR']),
            ],
            environment=env,
            log_prefix=test_script.replace('.', '_'),
            work_dir=sources_path,
            timeout=timeout
        )
        return_code = process.poll()
        logging.info('%s exit code: %s', test_script, return_code)

        task_context['do_not_restart'] = old_do_not_restart

    @staticmethod
    def build_virtualenv(sources_path, virtualenv_path):
        env = dict(os.environ)
        env['PYTHONNOUSERSITE'] = 'True'
        env['LDFLAGS'] = '-L/skynet/python/lib'
        env['PYTHONDONTWRITEBYTECODE'] = 'True'
        pip_path = os.path.join(virtualenv_path, 'bin', 'pip')

        # create virtualenv using *skynet* python
        # --system-site-packages is required for cqudp runner
        run_process(['/skynet/python/bin/virtualenv', '--system-site-packages', virtualenv_path])

        if os.path.exists(os.path.join(sources_path, 'pip-18.0.tar.gz')):
            pip_tar_gz_name = 'pip-18.0.tar.gz'
            log_prefix = 'pip_18_0_install'
        else:
            pip_tar_gz_name = 'pip-7.1.0.tar.gz'
            log_prefix = 'pip_7_1_0_install'
        # install old pip to be able to install ALL dependencies from wheels
        run_process(
            [pip_path, 'install', '-U', pip_tar_gz_name],
            log_prefix=log_prefix,
            work_dir=sources_path,
            environment=env,
        )

        # install dependencies from local dir, fail if some are not satisfied
        run_process(
            [
                pip_path, 'install',
                '--no-index',
                '--find-links=wheels',
                '-r', 'pip-requirements.txt',
                '-r', 'pip-requirements-dev.txt',
                '-i', 'https://pypi.yandex-team.ru/simple/'
            ],
            log_prefix='venv_reqs_pip_install',
            work_dir=sources_path,
            environment=env,
        )

        # install project itself
        run_process(
            [pip_path, 'install', '--no-index', '.'],
            log_prefix='alemate_pip_install',
            work_dir=sources_path,
            environment=env,
        )


class TestAlemate(SandboxTask):

    type = 'TEST_ALEMATE'

    input_parameters = [
        GitRefIdParameter,
        GitRefShaParameter,
    ]

    execution_space = 4096

    environment = [
        environments.SandboxJavaJdkEnvironment('1.8.0'),
        environments.SwatMongoDbEnvironment('2.6.11'),
        environments.SwatZookeeperEnvironment('3.4.6'),
    ]

    release_to = ['alximik', 'alonger', 'frolstas']

    client_tags = Tag.LINUX_XENIAL

    cores = 1

    def on_execute(self):
        """
        Plan is:

        * git clone and checkout specified tag
        * build virtualenv
        * run unittests
        """
        sources_path = self.path('alemate')
        virtualenv_path = self.path('venv')
        test_runner = AlemateTestRunner()

        logging.info('Checking out the source code')
        oauth_token = self.get_vault_data('GBG', 'nanny_robot_bb_oauth_token')
        test_runner.checkout(oauth_token=oauth_token,
                             dest=sources_path,
                             ref=self.ctx.get('ref_sha') or self.ctx['ref_id'])

        logging.info('Building virtualenv')
        test_runner.build_virtualenv(sources_path=sources_path,
                                     virtualenv_path=virtualenv_path)

        logging.info('Running unit tests')
        test_runner.run_tests(task_context=self.ctx,
                              virtualenv_path=virtualenv_path,
                              sources_path=sources_path,
                              test_script='test.sh',
                              timeout=600)

    def arcadia_info(self):
        """
        Получение информации о задаче при релизе

        :return список из трёх значений revision, tag, branch
        """
        return None, self.ctx.get('tag'), None


__Task__ = TestAlemate
