# coding: utf-8
import os
import logging

from sandbox.common.types.client import Tag

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


class InstanceCtlTestRunner(object):

    GIT_URL = 'https://bitbucket.yandex-team.ru/scm/nanny/instance-loop.git'

    @classmethod
    def checkout(cls, dest, ref=None):
        run_process(
            ['git', 'clone', cls.GIT_URL, dest],
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
        process = run_process([os.path.join('.', test_script)],
                              environment=env,
                              log_prefix=test_script.replace('.', '_'),
                              work_dir=sources_path,
                              timeout=timeout)
        return_code = process.poll()
        logging.info('%s exit code: %s', test_script, return_code)

        task_context['do_not_restart'] = old_do_not_restart

    @staticmethod
    def build_virtualenv(sources_path, virtualenv_path):
        env = dict(os.environ)
        env['LDFLAGS'] = '-L/skynet/python/lib'

        pip_path = os.path.join(virtualenv_path, 'bin', 'pip')

        # create virtualenv using *skynet* python
        # --system-site-packages is required for portopy package
        run_process(['/skynet/python/bin/virtualenv', '--system-site-packages', virtualenv_path],
                    environment=env)

        # install dependencies from local dir, fail if some are not satisfied
        run_process(
            [
                pip_path, 'install',
                '-r', 'requirements.txt',
                '-r', 'requirements-dev.txt',
                '-i', 'https://pypi.yandex-team.ru/simple/'
            ],
            log_prefix='venv_reqs_pip_install',
            work_dir=sources_path,
            environment=env,
        )


class TestInstanceCtl(SandboxTask):

    type = 'TEST_INSTANCE_CTL'

    client_tags = Tag.PORTO

    input_parameters = [
        GitRefIdParameter,
        GitRefShaParameter,
    ]

    execution_space = 1024

    def on_execute(self):
        """
        Plan is:

        * git clone and checkout specified tag
        * build virtualenv
        * run unittests
        """
        sources_path = self.path('instance_loop')
        virtualenv_path = self.path('venv')
        test_runner = InstanceCtlTestRunner()

        logging.info('Checking out the source code')
        test_runner.checkout(dest=sources_path,
                             ref=self.ctx.get('ref_sha') or self.ctx['ref_id'])

        logging.info('Building virtualenv')
        test_runner.build_virtualenv(sources_path=sources_path,
                                     virtualenv_path=virtualenv_path)

        logging.info('Running unit tests')

        test_runner.run_tests(task_context=self.ctx,
                              virtualenv_path=virtualenv_path,
                              sources_path=sources_path,
                              test_script='test.sh',
                              timeout=300)


__Task__ = TestInstanceCtl
