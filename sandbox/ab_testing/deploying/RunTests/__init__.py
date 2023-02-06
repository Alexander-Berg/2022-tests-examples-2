# -*- coding: utf-8 -*-
import logging
import json

from sandbox import sdk2
from sandbox.common import errors
from sandbox.common.types import task as ctt
from sandbox.sandboxsdk.environments import PipEnvironment

from sandbox.projects.ab_testing.deploying.Tests import TEST_LIST, TESTID_TEST_LIST, SEARCH_INTERFACES_RELEASE_TEST_LIST
from sandbox.projects.common.arcadia import sdk as arcadia_sdk
from sandbox.projects.common import task_env
import sandbox.projects.abc.client as abc_client


TESTID_TESTS = 'TESTID_TESTS'
BULK_TESTS = 'BULK_TESTS'
TESTERS_DICT_DEFAULT = {'default': 'default'}


def get_onduty(abc_helper, service_id, schedule_id):
    resp = abc_helper._do_get(
        'duty/on_duty/?service={}&schedule={}&fields=person.login'.format(service_id, schedule_id)
    )
    return [str(elem.get('person', {}).get('login')) for elem in resp]


def get_testers():
    try:
        token = sdk2.Vault.data('robot-eksperimentus-abc')
        abc_helper = abc_client.AbcClient(token)
        return dict(
            web=', '.join(get_onduty(abc_helper, 1021, 2522)),
            video=', '.join(get_onduty(abc_helper, 2269, 2023)),
            images=', '.join(get_onduty(abc_helper, 2290, 3292)),
        )
    except Exception as e:
        logging.debug('Failed to get testers: ' + str(e))
        return dict(
            web='',
            video='kulagin-iv, kirrysin',
            images='masloval',
        )


def get_developer():
    try:
        token = sdk2.Vault.data('robot-eksperimentus-abc')
        abc_helper = abc_client.AbcClient(token)
        return ', '.join(get_onduty(abc_helper, 1021, 688))
    except Exception as e:
        logging.debug('Failed to get developer: ' + str(e))
        return ''


class AbDeployingRunTests(sdk2.Task):
    '''
        Automatic deployment tests runner
    '''
    class Parameters(sdk2.Task.Parameters):
        run_type = sdk2.parameters.String(
            "Test type",
            choices=[
                (TESTID_TESTS, TESTID_TESTS),
                (BULK_TESTS, BULK_TESTS),
            ],
            default=BULK_TESTS,
        )
        testid = sdk2.parameters.Integer("TestId", required=True)
        flagsjson_id = sdk2.parameters.Integer("Flags.json id", required=True)
        ticket_id = sdk2.parameters.String("Startrack ticket for report")
        # USEREXP-6913
        services = sdk2.parameters.List(
            'Services list',
            default=[],
            required=False,
        )

        with sdk2.parameters.Group('Release regression') as release_regress_block:
            # FEI-13588
            service_regress_responsible_testers = sdk2.parameters.Dict(
                "Responsible testers",
                default=TESTERS_DICT_DEFAULT,
            )
            ready_to_regress_comment = sdk2.parameters.String(
                "Comment",
                default="**TO_TESTERS**\nTests are finished, ticket is ready for regression.",
                multiline=True,
            )

        with sdk2.parameters.Group('Release regression for developer') as release_regress_for_developer_block:
            # USEREXP-11415
            regress_responsible_developer = sdk2.parameters.String(
                "Responsible developer",
                default="",
            )
            ready_to_regress_comment_for_developer = sdk2.parameters.String(
                "Comment",
                default="**TO_DEVELOPER**\nTests are finished, check sandbox task statuses and validate failed test.",
                multiline=True,
            )

    class Requirements(task_env.TinyRequirements):
        environments = (
            PipEnvironment(
                'yandex_tracker_client', version="1.3", custom_parameters=["--upgrade-strategy only-if-needed"],
            ),
            PipEnvironment(
                'startrek_client', version="2.5.0", custom_parameters=["--upgrade-strategy only-if-needed"]
            ),
        )

    def get_web4_assessors_config(self):
        with arcadia_sdk.mount_arc_path('arcadia-arc:/#trunk') as mount_point:
            with open('{}/{}'.format(mount_point, self.web4_assessors_config_path), 'r') as f:
                config = json.load(f)
                config['suites'] = self.add_ticket_id_to_testsuites(
                    self.add_testid_to_testsuites(self.get_exp_flags_release_testsuites(config.get('suites', [])))
                )

        return config

    @property
    def web4_assessors_config_path(self):
        return 'frontend/projects/web4/.config/assessors/release.tsr.json'

    def get_exp_flags_release_testsuites(self, testsuites):
        '''Returns testcases with release_exp_flags only'''
        return [item for item in testsuites if item.get('release_exp_flags', False)]

    def add_testid_to_testsuites(self, testsuites):
        '''Returns testcases with additional testid for each testcase'''
        for item in testsuites:
            item['release_exp_flags_testid'] = self.Parameters.testid

        return testsuites

    def add_ticket_id_to_testsuites(self, testsuites):
        '''Adds ticket_id to tags for each testcase'''
        for item in testsuites:
            item['tags'].append(self.Parameters.ticket_id)

        return testsuites

    def start_test(self, test):
        params = dict(
            description='Test {}\nStarted by {} [{}]'.format(test.type, self.type, self.id),
            testid=self.Parameters.testid,
            flagsjson_id=self.Parameters.flagsjson_id,
        )

        subtask = test(self, **params)
        subtask.enqueue()
        return subtask.id

    def get_task_list(self):
        all_test_list = {BULK_TESTS: TEST_LIST, TESTID_TESTS: TESTID_TEST_LIST}.get(self.Parameters.run_type)

        if len(self.Parameters.services) == 0:
            return [test for (_, test, ) in all_test_list]

        return [test for (service, test, ) in all_test_list if service is None or service in self.Parameters.services]

    def report_startrek(self):
        ticket_id = self.Parameters.ticket_id
        sandbox_url = 'https://sandbox.yandex-team.ru/task/{}'
        self_sandbox_url = sandbox_url.format(self.id)

        children_sandbox_urls = []
        for subtask_id in self.Context.subtasks:
            subtask = sdk2.Task[subtask_id]
            doc = subtask.__doc__
            if doc is not None:
                doc = doc.strip()
                logging.debug('subtask #{} doc: `{}`'.format(subtask_id, doc))
                child_sandbox_url = '**{}**|{}'.format(doc, sandbox_url.format(subtask_id))
            else:
                logging.debug('subtask #{} doc is None'.format(subtask_id))
                child_sandbox_url = sandbox_url.format(subtask_id)
            children_sandbox_urls.append('||' + child_sandbox_url + '||')

        children_sandbox_urls_str = '\n'.join(children_sandbox_urls)
        if children_sandbox_urls:
            children_sandbox_urls_str = '#|\n' + children_sandbox_urls_str + '\n|#'

        # USEREXP-6904, USEREXP-7228
        testpalm_url = 'https://testpalm.yandex-team.ru/serp-js-issue-{}/testruns'.format(ticket_id.lower())

        text = 'Started sandbox test:\n{}\n\nChild tasks are:\n{}\n\n(({} Web Testpalm testruns link)).'.format(
            self_sandbox_url,
            children_sandbox_urls_str,
            testpalm_url
        )

        logging.debug('comment text: `{}`'.format(text))

        self.comment_ticket(ticket_id=ticket_id, text=text)

    def comment_ticket(self, ticket_id, text, **kwargs):
        import startrek_client

        token = sdk2.Vault.data('robot-eksperimentus-startrek')
        st = startrek_client.Startrek(token=token, useragent='sandbox-task')

        ticket = st.issues[ticket_id]
        ticket.comments.create(text=text, **kwargs)

    def inform_service_responsible_testers(self):
        services = self.Parameters.services

        ticket_id = self.Parameters.ticket_id
        comment = self.Parameters.ready_to_regress_comment
        service_regress_responsible_testers = self.Parameters.service_regress_responsible_testers
        if service_regress_responsible_testers == TESTERS_DICT_DEFAULT:
            service_regress_responsible_testers = get_testers()

        has_responsible = any(service in service_regress_responsible_testers for service in services)
        if not has_responsible:
            logging.debug('Service responsible testers not found, skipping')
            return

        summonees = []

        for service in services:
            responsible_testers = [
                tester.strip()
                for tester in service_regress_responsible_testers.get(service, '').split(',')
                if tester.strip()
            ]

            logging.debug('Service "{}" responsible testers: {}'.format(service, responsible_testers))

            summonees.extend(responsible_testers)

        logging.debug('Informing: {}'.format(summonees))

        self.comment_ticket(ticket_id=ticket_id, text=comment, summonees=summonees)

    def inform_responsible_developer(self):
        ticket_id = self.Parameters.ticket_id
        comment = self.Parameters.ready_to_regress_comment_for_developer
        regress_responsible_developer = self.Parameters.regress_responsible_developer
        if regress_responsible_developer == '':
            regress_responsible_developer = get_developer()

        summonees = [
            developer.strip()
            for developer in regress_responsible_developer.split(',')
            if developer.strip()
        ]

        if not summonees:
            logging.debug('Responsible developer not found, skipping')
            return

        logging.debug('Informing: {}'.format(summonees))

        self.comment_ticket(ticket_id=ticket_id, text=comment, summonees=summonees)

    @staticmethod
    def filter_search_interfaces_tests(subtasks):
        tests = []
        for task_id in subtasks:
            task = sdk2.Task[task_id]
            is_search_interfaces_test = any([
                isinstance(task, test_task_type)
                for (_, test_task_type, ) in SEARCH_INTERFACES_RELEASE_TEST_LIST
            ])

            if is_search_interfaces_test:
                tests.append(task)

        return tests

    def on_execute(self):
        with self.memoize_stage.create_subtasks():
            logging.info('Starting tests')
            self.Context.subtasks = []
            for test in self.get_task_list():
                self.Context.subtasks.append(self.start_test(test))
                logging.info('Started test {} [{}]'.format(test.type, self.Context.subtasks[-1]))
            if self.Parameters.ticket_id:
                logging.info('Reporting to startrek ticket {}'.format(self.Parameters.ticket_id))
                self.report_startrek()

        wait_statuses = ctt.Status.Group.FINISH | ctt.Status.Group.BREAK

        # do not wait non SERP tasks to inform testers
        # see FEI-12836, FEI-13588
        search_interfaces_tests = self.filter_search_interfaces_tests(self.Context.subtasks)
        if search_interfaces_tests and self.Parameters.run_type == BULK_TESTS:
            with self.memoize_stage.wait_search_interfaces_tests():
                logging.info('Search interfaces test tasks: {}'.format(search_interfaces_tests))
                raise sdk2.WaitTask(search_interfaces_tests, wait_statuses, wait_all=True)

            with self.memoize_stage.inform_service_responsible_testers():
                logging.info('Informing search interfaces responsible testers')
                self.inform_service_responsible_testers()

            with self.memoize_stage.inform_responsible_developer():
                logging.info('Informing search interfaces responsible developer')
                self.inform_responsible_developer()

        with self.memoize_stage.wait_all_subtasks():
            logging.info('Waiting for tasks')
            raise sdk2.WaitTask(self.Context.subtasks, wait_statuses, wait_all=True)

        with self.memoize_stage.check_status():
            for task_id in self.Context.subtasks:
                task = sdk2.Task[task_id]
                msg = 'Subtask {} [{}] done with status {}'.format(task_id, task.type, task.status)
                logging.info(msg)
                if task.status not in ctt.Status.Group.SUCCEED:
                    raise errors.TaskFailure(msg)
            logging.info('All tests checked')
