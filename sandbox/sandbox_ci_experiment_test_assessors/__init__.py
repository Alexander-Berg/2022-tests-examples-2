# -*- coding: utf-8 -*-
import logging

from sandbox import sdk2
from sandbox.common.types import misc as ctm

from sandbox.projects.sandbox_ci import parameters
from sandbox.projects.sandbox_ci.experiments.utils import TestSuites
from sandbox.projects.sandbox_ci.experiments.utils import Resource

from sandbox.projects.sandbox_ci.sandbox_ci_testpalm_suite_runner import SandboxCiTestpalmSuiteRunner

TESTSUITES_FILENAME = 'testsuites.json'
RESOURCE_SYNC_DIRECTORY = 'project'


class SandboxCiExperimentTestAssessors(sdk2.Task):
    """Запуск ранов на асессоров при тестировании экспериментов"""

    class Requirements(sdk2.Requirements):
        dns = ctm.DnsType.LOCAL
        cores = 1

        class Caches(sdk2.Requirements.Caches):
            pass

    class Parameters(sdk2.Task.Parameters):
        _container = parameters.environment_container()

        with sdk2.parameters.Group('Resource') as resource_block:
            resource_type = sdk2.parameters.String(
                'Type',
                required=True,
                default='SANDBOX_CI_ARTIFACT',
                description=u'Тип ресурса с проектом.'
            )
            resource_attrs = sdk2.parameters.Dict(
                'Attributes',
                required=True,
                description=u'Аттрибуты ресурса.'
            )

        with sdk2.parameters.Group('Project') as project_block:
            config_path = sdk2.parameters.String(
                'Config path',
                required=True,
                description=u'Путь до конфига.',
            )

        with sdk2.parameters.Group('Tracker') as tracker_block:
            ticket_id = sdk2.parameters.String(
                'Ticket',
                required=True,
                description=u'Ключ тикета в Трекере.',
            )
            responsible_user = sdk2.parameters.String(
                'Responsible User',
                required=True,
                description=u'Логин пользователя, ответственного за тест-раны.',
            )

        with sdk2.parameters.Group('AB Experiments') as ab_experiments_block:
            test_id = sdk2.parameters.List(
                'TestId',
                value_type=sdk2.parameters.Integer,
                required=True,
                default=[],
                description=u'Список тестидов.',
            )
            platforms = sdk2.parameters.List(
                'Platforms',
                required=True,
                default=('desktop', 'touch-pad', 'touch-phone'),
            )

        with sdk2.parameters.Output():
            with sdk2.parameters.Group('Config') as config_block:
                testsuites = sdk2.parameters.JSON(
                    'Test suites',
                    description='Конфиг, с которым запускается таск SandboxCiTestpalmSuiteRunner',
                )

    def on_execute(self):
        resource = self.create_resource_with_testsuites()

        self.run_testpalm_suite_runner_task(
            is_resource_run=True,
            is_flags_release=True,
            need_clone_testpalm_project=True,
            testpalm_project_suffix=self.format_testpalm_project_suffix(),
            build_artifacts_resources=resource.id,
            config_path=TESTSUITES_FILENAME,
        )

    def create_resource_with_testsuites(self):
        resource_type = self.Parameters.resource_type
        resource_attrs = self.Parameters.resource_attrs

        resource = Resource.find(resource_type=resource_type, **resource_attrs)

        Resource.unpack(resource, RESOURCE_SYNC_DIRECTORY)

        config_path = '{resource_path}/{config_path}'.format(
            resource_path=RESOURCE_SYNC_DIRECTORY,
            config_path=self.Parameters.config_path,
        )

        config = TestSuites.load(config_path)
        testsuites = config.get('suites', [])

        logging.debug('Loaded testsuites from {path}: {testsuites}'.format(
            path=config_path,
            testsuites=TestSuites.dump(testsuites),
        ))

        testsuites = TestSuites.get_release_exp_flags_testsuites(testsuites)

        logging.debug('Filtered experiments release testsuites: {}'.format(TestSuites.dump(testsuites)))

        platforms = self.normalize_platforms(self.Parameters.platforms)
        if platforms:
            testsuites = TestSuites.filter_testsuites_by_platforms(testsuites, platforms)

            logging.debug('Filtered by {platforms}: {testsuites}'.format(
                platforms=platforms,
                testsuites=TestSuites.dump(testsuites),
            ))

        test_id = self.Parameters.test_id
        testsuites = TestSuites.add_testids_to_testsuites(testsuites, test_id)

        logging.debug('Added testid "{test_id}": {testsuites}'.format(
            test_id=test_id,
            testsuites=TestSuites.dump(testsuites),
        ))

        ticket_id = self.Parameters.ticket_id
        testsuites = TestSuites.add_ticket_id_to_testsuites(testsuites, ticket_id)

        logging.debug('Added ticket id "{ticket_id}": {testsuites}'.format(
            ticket_id=ticket_id,
            testsuites=TestSuites.dump(testsuites),
        ))

        responsible_user = self.Parameters.responsible_user
        testsuites = TestSuites.add_responsible_user_to_testsuites(testsuites, responsible_user)

        logging.debug('Added responsible_user "{user}": {testsuites}'.format(
            user=responsible_user,
            testsuites=TestSuites.dump(testsuites),
        ))

        self.Parameters.testsuites = testsuites

        config['suites'] = testsuites

        return Resource.create(
            task=self,
            data=TestSuites.dump(config),
            resource_type=resource_type,
            filename=TESTSUITES_FILENAME,
        )

    def normalize_platforms(self, platforms):
        """
        :param platforms: платформы
        :type platforms: list of str
        :rtype: list of str
        """
        platform_map = {
            'touch-pad': ('pad', 'searchapp',),
            'touch-phone': ('touch', 'searchapp',)
        }
        normalized = []

        for platform in platforms:
            normalized.extend(platform_map.get(platform, (platform,)))

        return list(set(normalized))

    def format_testpalm_project_suffix(self):
        return 'issue-{}'.format(self.Parameters.ticket_id).lower()

    def run_testpalm_suite_runner_task(self, **params):
        """
        :param params: Параметры запуска
        :type params: dict
        :rtype: sdk2.Task
        """
        logging.debug('Starting child task {type} with params: {params}'.format(
            type=SandboxCiTestpalmSuiteRunner,
            params=params,
        ))

        task = SandboxCiTestpalmSuiteRunner(
            self,
            description='Running tests by {} [{}]'.format(self.type, self.id),
            **params
        ).enqueue()

        logging.info('Started child task {type} with id: {id}'.format(
            type=task.type,
            id=task.id,
        ))

        return task
