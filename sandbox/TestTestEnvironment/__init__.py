# -*- coding: utf-8 -*-

import glob
import os
import logging

from sandbox.sandboxsdk.task import SandboxTask
from sandbox.sandboxsdk.environments import VirtualEnvironment
from sandbox.sandboxsdk.svn import Arcadia
from sandbox.sandboxsdk import parameters as sp
from sandbox.sandboxsdk import process
from sandbox.sandboxsdk import paths


class RevisionParameter(sp.SandboxIntegerParameter):
    name = 'revision'
    description = 'Revision'
    default_value = 0


class TestTestEnvironment(SandboxTask):
    """
    **Описание**
    Запускает юнит тесты Test Environment и engine в режиме самотестирования.
    Подробнее `здесь <https://wiki.yandex-team.ru/SandboxTestEnvironment/UnitTests>`_.

    **Параметры**
    Номер ревизии для проверки.
    """
    type = 'TEST_TEST_ENVIRONMENT'

    input_parameters = (
        RevisionParameter,
    )

    execution_space = 1 * 1024

    def on_execute(self):
        garden_path = self.abs_path('garden')
        test_environment_path = os.path.join(garden_path, 'test_environment')

        revision = self.ctx['revision']
        if revision == 0:
            revision = None

        Arcadia.export(Arcadia.trunk_url('search/garden'), garden_path, revision=revision)

        with VirtualEnvironment(use_system=True) as venv:
            path_to_requirements = os.path.join(test_environment_path, 'requirements.txt')

            venv.pip('-r {}'.format(path_to_requirements))

            unit_tests_process = self._run_unit_tests(venv, test_environment_path)
            selftest_process = self._run_engine_self_test(venv, test_environment_path)
            web_server_process = self._run_web_server_tests(venv, test_environment_path)

            process.check_process_timeout(unit_tests_process, 300, timeout_sleep=1)
            process.check_process_return_code(unit_tests_process)

            process.check_process_timeout(selftest_process, 300, timeout_sleep=1)

            self._copy_te_scenario_dirs_from_tmp_to_logs()

            process.check_process_return_code(selftest_process)

            process.check_process_timeout(web_server_process, 120, timeout_sleep=1)
            process.check_process_return_code(web_server_process)

    def _run_unit_tests(self, venv, test_environment_path):
        os.chdir(paths.get_logs_folder())

        unit_tests_path = os.path.join(test_environment_path, 'run_system_unit_tests.py')
        cmd = [venv.executable, unit_tests_path]
        return process.run_process(cmd, log_prefix='unit_tests', wait=False)

    def _run_engine_self_test(self, venv, test_environment_path):
        unit_tests_path = os.path.join(test_environment_path, 'run_self_test.py')
        cmd = [venv.executable, unit_tests_path]
        return process.run_process(cmd, log_prefix='selftest', wait=False)

    def _copy_te_scenario_dirs_from_tmp_to_logs(self):
        tmp_pattern = self.abs_path('tmp') + '/te_scenario*/'
        found_paths = glob.glob(tmp_pattern)
        if not found_paths:
            logging.info('cannot find any dir')
            return
        for index, path in enumerate(found_paths):
            dest_path = os.path.join(self.log_path(), unicode(index))
            paths.copy_path(path, dest_path)

    def _run_web_server_tests(self, venv, test_environment_path):
        tests_path = os.path.join(test_environment_path, 'run_web_server_tests.py')
        cmd = [venv.executable, tests_path]
        return process.run_process(cmd, log_prefix='web_server_test', wait=False)


__Task__ = TestTestEnvironment
