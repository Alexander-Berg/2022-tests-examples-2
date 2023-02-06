# -*- coding: utf-8 -*-

import logging

from sandbox import sdk2

from sandbox.common.types import task as ctt

from sandbox.projects.sandbox_ci.sandbox_ci_testpalm_suite_runner import SandboxCiTestpalmSuiteRunner


def find_testpalm_suite_runner_task(input_parameters):
    """
    Ищет последнюю задачу SANDBOX_CI_TESTPLAM_SUITE_RUNNER, которая является дочерней и в статусе SUCCESS

    :param input_parameters: входные параметры, по которым нужно искать
    :type input_parameters: dict
    :rtype: object
    """
    return sdk2.Task.find(
        type=SandboxCiTestpalmSuiteRunner,
        children=True,
        status=ctt.Status.SUCCESS,
        input_parameters=input_parameters,
    ).order(-sdk2.Task.id).first()


def should_start_testpalm_suite_runner_task(testpalm_base_project_name, testpalm_project_suffix, config_path, is_release, force_run, ticket_id=''):
    """
    Проверяет, нужно ли создавать задачу или нет.
    В случае релиза проверяет на существование успешной таски: если есть, то создавать задачу не нужно.

    :param testpalm_base_project_name: название базового проекта в TestPalm
    :type testpalm_base_project_name: str
    :param testpalm_project_suffix: префикс проекта в TestPalm
    :type testpalm_project_suffix: str
    :param config_path: путь до конфига в проекте
    :type config_path: str
    :param is_release: релиз или нет
    :type is_release: bool
    :param force_run: принудительно заводим задачу
    :type force_run: bool
    :param ticket_id: ключ тикета в Трекере
    :type ticket_id: str
    :rtype: bool
    """
    if config_path == '':
        logging.debug('Skip SANDBOX_CI_TESTPALM_SUITE_RUNNER creation by empty config path')
        return False

    if force_run:
        logging.debug('Force SANDBOX_CI_TESTPALM_SUITE_RUNNER creation by manual request')
        return True

    if not is_release:
        logging.debug('Force SANDBOX_CI_TESTPALM_SUITE_RUNNER creation for non-release context')
        return True

    if not testpalm_base_project_name:
        raise Exception('SANDBOX_CI_TESTPALM_SUITE_RUNNER: testpalm_base_project_name Parameter should be presented')

    input_params = dict(
        testpalm_project_suffix=testpalm_project_suffix,
        config_path=config_path,
        testpalm_base_project_name=testpalm_base_project_name,
        ticket_id=ticket_id,
    )

    original_task = find_testpalm_suite_runner_task(input_params)

    if original_task:
        logging.debug('Skip SANDBOX_CI_TESTPALM_SUITE_RUNNER creation by already processed run in {}'.format(original_task))
        return False

    logging.debug('Force SANDBOX_CI_TESTPALM_SUITE_RUNNER creation for previously unprocessed run')
    return True
