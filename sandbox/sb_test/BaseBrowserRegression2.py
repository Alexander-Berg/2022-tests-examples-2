# -*- coding: utf-8 -*-
import logging
import os
import yaml
import json
from copy import deepcopy

import sandbox
from sandbox import sdk2
from sandbox.common.errors import TaskFailure
from sandbox.common.utils import get_task_link
import sandbox.common.types.client as ctc
from sandbox.common.types.task import Status
from sandbox.common.types import resource as ctr
from sandbox.projects.browser.autotests_qa_tools.classes.ya_booking import get_booking_state
from sandbox.projects.browser.autotests_qa_tools.classes.ya_clients import YaClients
from sandbox.projects.browser.autotests_qa_tools.classes.testing_groups import MAX_ASSESSOR_RUN, get_groups_conf_by_activities
import sandbox.projects.browser.autotests_qa_tools.configs.regression as configs_module
from sandbox.projects.browser.autotests_qa_tools.configs.regression import validate_regression_config, DEFAULT_SETTINGS_FILE_NAME, SCHEME_FILE_NAME, SETTINGS_SCHEME_FILE_NAME
from sandbox.projects.browser.autotests_qa_tools.common import (
    html_link, is_dev_sandbox, ROBOT_BRO_QA_INFRA_TOKEN_VAULT, build_number_tuple,
    DEFAULT_REGRESSION_AUTOTESTS_TIMEOUT, REGRESSION_GROUPS_ACTIVITIES)
from sandbox.projects.browser.autotests_qa_tools.sb_common.resources import AutotestsReportResource, RegressionState
from sandbox.projects.browser.util.BrowserWaitTeamcityBuilds import BrowserWaitTeamcityBuilds
from sandbox.sandboxsdk.environments import PipEnvironment


class RegressionResult(object):
    def __init__(self, main_ticket,
                 manual_tickets,
                 manual_runs,
                 assessors_tickets,
                 assessors_runs):
        self.main_ticket = main_ticket
        self.manual_tickets = manual_tickets
        self.manual_runs = manual_runs
        self.assessors_tickets = assessors_tickets
        self.assessors_runs = assessors_runs


class BaseBrowserRegression2(sdk2.Task):

    assessors_testrun_properties_to_show = ""
    STATE_RESOURCE_PATH = "regression_state_data"
    STATE_DATA_FILE_NAME = "regression_state.json"
    INTEREST_CONTEXT_FIELDS = [
        "main_ticket",
        "manual_tickets",
        "manual_runs",
        "assessors_tickets",
        "assessors_runs",
        "monitor_assessors_task_id",
        "monitor_manuak_task_id",
        "deadline",
        "assessors_links",
        "groups",
        "regression_type_name",
        "settings",
    ]
    EXPECTED_CONSISTENT_BUILDS = [
        "browser_build", "fake_build", "tests_build"
    ]

    @property
    def affected_version(self):
        """
        Used in hitman https://st.yandex-team.ru/ASSESSORTEST-1665
        :return: str
        """
        return None

    def get_component(self, case):
        raise NotImplementedError()

    @property
    def whom_notify_about_asessors_start(self):
        raise NotImplementedError()

    # link to build that assessors/tolokers will see in yang
    @property
    def test_stend(self):
        raise NotImplementedError()

    @property
    def whom_notify_from_hitman(self):
        raise NotImplementedError()

    @property
    def regression_manager_class(self):
        raise NotImplementedError()

    @property
    def configs_module(self):
        raise NotImplementedError()

    @property
    def requester_code(self):
        """
        Parameter for hitman process to check, that assessors test specified build.
        If not needed return None
        :return: str
        """
        raise NotImplementedError()

    @property
    def min_leeway_time_for_autotests(self):
        # TODO: fit it
        return 30

    @property
    @sandbox.common.utils.singleton
    def test_suite_configs_path(self):
        return os.path.dirname(self.configs_module.__file__)

    @property
    def autotests_result_resource_type(self):
        return AutotestsReportResource

    class Context(sdk2.Context):
        main_ticket = None
        manual_tickets = {}
        manual_runs = {}
        assessors_tickets = {}
        assessors_runs = {}
        monitor_assessors_task_id = None
        monitor_manuak_task_id = None
        deadline = None
        assessors_links = {}
        groups = {}
        autotests_timeout = DEFAULT_REGRESSION_AUTOTESTS_TIMEOUT
        regression_type_name = None
        settings = None

    class Parameters(sdk2.Parameters):
        issues_filter = None
        test_suites = sdk2.parameters.JSON(
            'Testsuites and platforms',
            default={
                'deadline': 24,
                'testsuites': {
                    'testsuites': [
                        {
                            'project': '',
                            'id': '',
                            'assessors_platforms': [],
                            'manual_platforms': [],
                        }
                    ]
                }
            }
        )
        main_regression_ticket_assignee = sdk2.parameters.String('Regression assignee')
        with sdk2.parameters.Group('Assessors parameters') as assessors_params:
            @property
            def hitman_process_id(self):
                raise NotImplementedError()

            @property
            def assessors_quota(self):
                raise NotImplementedError()

            booking_id = sdk2.parameters.Integer(
                'Booking id', required=True,
                description='Id from <a href="https://booking.yandex-team.ru">booking</a>.')
            check_booking = sdk2.parameters.Bool(
                'Check booking', default=True,
                description='Check if booking is actual before regression start. '
                            'Uncheck this option during booking.yandex-team.ru maintenance '
                            '(when any booking id is accepted). '
                            'Do not skip booking check in other cases, because information from booking is used '
                            'to calculate possible duration of autotests launch.'
            )
            assessors_launch_comment = sdk2.parameters.String('Assessors launch comment', multiline=True)
            max_run_duration = sdk2.parameters.Integer('Testrun max duration', required=True, default=MAX_ASSESSOR_RUN)
            deadline = sdk2.parameters.Integer(
                'Deadline for assessors', default=24, description='In hours', required=True)
            start_hitman_jobs_automatically = sdk2.parameters.Bool(
                'Start hitman jobs automatically', default=True,
                description='If checked, assessors will get their tasks after testruns are created without any approve')

        with sdk2.parameters.Group('Builds, autotests and diff parameters') as build_params:
            build_id = sdk2.parameters.Integer(
                'Browser build id',
                description='Id of browser teamcity build. See: https://wiki.yandex-team.ru/users/nik-isaev/starship_run_faq/#builds')
            old_build_id = sdk2.parameters.Integer('Previous build id',
                                                   description='Use to calculate diff tickets')
            fake_build_id = sdk2.parameters.Integer(
                'Fake browser build id',
                description='Id of fake browser teamcity build ')
            browser_tests_build_id = sdk2.parameters.Integer(
                'Tests build id',
                description='Id of teamcity build with browser tests ')
            enable_autotests = sdk2.parameters.Bool('Run and use autotests', default=True)
            with sdk2.parameters.RadioGroup("Diff type") as diff_type:
                diff_type.values.functionalities_diff = diff_type.Value("Functionalities diff", default=True)
                diff_type.values.component_diff = diff_type.Value("Component diff")
                diff_type.values.disabled = diff_type.Value("Diff disabled")
            scope_filter = sdk2.parameters.String(
                'Scope filter', default='', multiline=True,
                description='This filter will be applied to issues that are found'
                            ' in diff before computing components that will be checked in this regression. '
                            'For example, if "Priority: Blocker" filter, then components from blocker issues with'
                            'recent commits will be checked.'
                            '  See <a href="https://wiki.yandex-team.ru/browser/dev/infra/qa/regression-launcher/diff/#nastrojjkadiffavregressionnyxtaskax">documentation</a>')
            skip_builds_consistency_check = sdk2.parameters.Bool('Skip builds consistency check',
                                                                 default=False,
                                                                 description='Skip builds consistency check')

    @sandbox.common.utils.singleton
    def get_builds(self):
        result = {}
        if self.Parameters.build_id:
            result["browser_build"] = self.teamcity_client.Build(id=self.Parameters.build_id)
        if self.Parameters.fake_build_id:
            result["fake_build"] = self.teamcity_client.Build(id=self.Parameters.fake_build_id)
        if self.Parameters.browser_tests_build_id:
            result["tests_build"] = self.teamcity_client.Build(id=self.Parameters.browser_tests_build_id)
        if self.Parameters.old_build_id:
            result["old_build"] = self.clients.teamcity.Build(id=self.Parameters.old_build_id)

        # Sort browser_build and fake_build by version
        browser_build, fake_build = result.get("browser_build"), result.get("fake_build")
        if browser_build and fake_build and browser_build.state == 'finished' and fake_build.state == 'finished':
            browser_build, fake_build = sorted([browser_build, fake_build], key=build_number_tuple)
        result["browser_build"] = browser_build
        result["fake_build"] = fake_build
        return result

    def get_builds_consistency_problems(self):
        consistency_problems = []
        builds = [self.get_builds().get(_b) for _b in self.EXPECTED_CONSISTENT_BUILDS]
        if builds and builds[0]:
            reference_build = builds[0]
            browser_commit = self.clients.get_build_commit(reference_build)
            if browser_commit is None:
                consistency_problems.append(
                    u'Не удалось определить commit сборки <a href="{}">#{}</a>. Проверка соответствия сборок не возможна.'
                    u' Регрессия может быть не корректной'.format(reference_build.web_url, reference_build.id))
            else:
                for build in builds[1:]:
                    if not build:
                        continue
                    build_commit = self.clients.get_build_commit(build)
                    if build_commit is None:
                        consistency_problems.append(
                            u'Не удалось определить commit сборки <a href="{}">#{}</a>. Проверка соответствия сборок не возможна. '
                            u'Регрессия может быть не корректной'.format(build.web_url, build.id))
                    elif build_commit != browser_commit:
                        consistency_problems.append(
                            u'Сборки <a href="{}">#{}</a> и <a href="{}">#{}</a> собраны на разных коммитах.'
                            u' Регрессия может быть не корректной'.format(
                                reference_build.web_url, reference_build.id,
                                build.web_url, build.id))
        return consistency_problems

    def check_input(self):
        from jsonschema import ValidationError
        fail_reasons = []

        with open(os.path.join(os.path.join(self.test_suite_configs_path, SCHEME_FILE_NAME))) as _f:
            config_scheme = json.load(_f)
        with open(os.path.join(os.path.join(os.path.dirname(configs_module.__file__), SETTINGS_SCHEME_FILE_NAME))) as _f:
            settings_scheme = json.load(_f)

        try:
            validate_regression_config(self.regression_config,
                                       config_scheme=config_scheme,
                                       settings_scheme=settings_scheme,
                                       avalible_groups=get_groups_conf_by_activities(REGRESSION_GROUPS_ACTIVITIES),
                                       all_settings_required=True)
        except ValidationError as e:
            logging.exception('Failed to parse JSON')
            fail_reasons.append(u'Невалидный JSON: {}'.format(e.message))

        if self.Parameters.scope_filter:
            fail_reasons.extend(self.check_filter(self.Parameters.scope_filter))

        consistency_problems = self.get_builds_consistency_problems()
        if not self.Parameters.skip_builds_consistency_check:
            fail_reasons += consistency_problems
        else:
            for problem in consistency_problems:
                self.set_info(problem, do_escape=False)
        return fail_reasons

    def validate_input(self):
        fail_reasons = self.check_input()
        if fail_reasons:
            self.set_info(
                ''.join([u'Ошибка в параметрах таски:<ul>'] + [
                    '<li>{}</li>'.format(problem) for problem in fail_reasons] + [
                    '</ul>']),
                do_escape=False
            )
            raise TaskFailure(u'Ошибка во входных данных')

    def check_filter(self, filter):
        problems = []
        try:
            _ = self.clients.startrek.issues.find(filter)
        except:
            problems = [u'Некорректный фильтр "{}"'.format(filter)]
        return problems

    def check_booking(self):
        booking_check_state = None
        if self.Parameters.booking_id and self.Parameters.check_booking:
            booking_check_state = get_booking_state(self.clients.ya_booking, self.Parameters.booking_id)
            if booking_check_state["problems"]:
                raise TaskFailure(u'Ошибка проверки брони: \n{}'.format(u'\n'.join(booking_check_state["problems"])))
            if booking_check_state["available_time"] < 10 * 60:
                raise TaskFailure(
                    u'Ошибка проверки брони: бронь booking_id={} просрочена'.format(self.Parameters.booking_id))
        return booking_check_state

    def calculate_autotests_timeout(self, booking_check_state):
        if booking_check_state is not None and self.Parameters.enable_autotests:
            # Определить таймаут автотестов или отключить авотесты, если бронь истекает.
            autotests_avalible_time = int(booking_check_state["available_time"] / 60) - self.min_leeway_time_for_autotests
            if autotests_avalible_time <= 0:
                self.Context.autotests_timeout = 0
                self.set_info(u"Время брони {} имеет в запасе менее {} минут."
                              u"\nАвтотесты запущены не будут".format(self.Parameters.booking_id, self.min_leeway_time_for_autotests))
            self.Context.autotests_timeout = min(self.Context.autotests_timeout, autotests_avalible_time)

    def get_assessors_deadline(self, assessors_runs):
        return self.Parameters.deadline

    def create_assessors_task(self, *args, **kwargs):
        self.set_info(u"create_assessors_task")

    def enqueue_asessor_tasks(self, *args, **kwargs):
        self.set_info(u"enqueue_asessor_tasks")

    def _reformat_runs(self, created_runs, created_issues=None):
        created_issues = created_issues if created_issues else {}
        return {
            group.name: [
                {
                    'suite_id': suite.id,
                    'project': suite.project,
                    'testruns': [run.id for run in runs],
                    'issue': created_issues.get(group)
                }
                for suite, runs in suites.iteritems()
            ]
            for group, suites in created_runs.iteritems()
        }

    def start_runs_monitoring(self, *args, **kwargs):
        pass

    def on_create(self):
        if not self.Parameters.main_regression_ticket_assignee:
            self.Parameters.main_regression_ticket_assignee = (
                self.author if not is_dev_sandbox()
                else 'robot-bro-qa-infra'  # author is always "guest" on dev sandbox and there is no such user on staff
            )

    @sandbox.common.utils.singleton
    def get_config(self, config_file):
        with open(os.path.join(self.test_suite_configs_path, config_file)) as config_file:
            return yaml.load(config_file)

    @property
    @sandbox.common.utils.singleton
    def regression_config(self):
        if self.Parameters.regression_type != 'custom':
            config = self.get_config(self.Parameters.regression_type)
        else:
            config = self.Parameters.test_suites_override
        settings = deepcopy(self.default_settings)
        settings.update(config.get("settings", {}))
        config["settings"] = settings
        return config

    @property
    @sandbox.common.utils.singleton
    def default_settings(self):
        with open(os.path.join(self.test_suite_configs_path, DEFAULT_SETTINGS_FILE_NAME)) as config_file:
            default_settings = yaml.load(config_file)
        return default_settings

    def on_execute(self):
        raise NotImplementedError()

    @sdk2.report(title=u"Асессорские раны")
    def assessors_runs(self):
        if not self.Context.monitor_assessors_task_id:
            return u'Нет информации про раны'

        task = sdk2.Task.find(id=self.Context.monitor_assessors_task_id, children=True).limit(1).first()
        return task.Context.report

    @sdk2.report(title=u"Ручные раны")
    def manual_runs(self):
        if not self.Context.monitor_manual_task_id:
            return u'Нет информации про раны'

        task = sdk2.Task.find(id=self.Context.monitor_manual_task_id, children=True).limit(1).first()
        return task.Context.report

    class Requirements(sdk2.Task.Requirements):
        disk_space = 150
        cores = 1
        client_tags = ctc.Tag.Group.LINUX & ctc.Tag.BROWSER
        environments = [
            PipEnvironment('teamcity-client==3.0.0'),
            PipEnvironment('testpalm-api-client', version='4.0.2'),
            PipEnvironment('startrek_client', version='1.7.0', use_wheel=True),
            PipEnvironment('jsonschema==2.5.1'),
            PipEnvironment('ya-booking-client==1.0.1'),
        ]

        class Caches(sdk2.Requirements.Caches):
            pass

    @property
    @sandbox.common.utils.singleton
    def oauth_vault(self):
        return sdk2.Vault.data(ROBOT_BRO_QA_INFRA_TOKEN_VAULT)

    @property
    @sandbox.common.utils.singleton
    def clients(self):
        return YaClients(self.oauth_vault)

    @property
    @sandbox.common.utils.singleton
    def st_base_url(self):
        return self.clients.st_base_url

    @property
    @sandbox.common.utils.singleton
    def startrek_client(self):
        return self.clients.startrek

    @property
    @sandbox.common.utils.singleton
    def teamcity_client(self):
        return self.clients.teamcity

    @property
    @sandbox.common.utils.singleton
    def testpalm_client(self):
        return self.clients.testpalm

    @property
    @sandbox.common.utils.singleton
    def bitbucket_client(self):
        return self.clients.bitbucket

    def create_regression_state_resource(self):
        saved_data = {
            "initial_config": self.regression_config,
            "context": {}
        }

        for field in self.INTEREST_CONTEXT_FIELDS:
            saved_data['context'][field] = getattr(self.Context, field)
        data_path = str(self.path(self.STATE_RESOURCE_PATH))
        os.mkdir(data_path)
        resource = RegressionState(self, "Regression State",
                                   str(data_path))
        with open(os.path.join(data_path, self.STATE_DATA_FILE_NAME), 'w') as _f:
            json.dump(saved_data, _f)
        sdk2.ResourceData(resource).ready()

    @property
    @sandbox.common.utils.singleton
    def initial_regression_state(self):
        state_resource = RegressionState.find(task=self.Parameters.run_regression_task,
                                              state=ctr.State.READY).first()
        if not state_resource:
            raise RuntimeError(u"Не найден ресурс состояния регрессии")

        file_path = os.path.join(str(sdk2.ResourceData(state_resource).path))

        with open(os.path.join(file_path, self.STATE_DATA_FILE_NAME), "r") as _f:
            state_data = json.load(_f)
        return state_data

    def get_autotests_results_path(self, autotests_task):

        autotests_result_resource = self.autotests_result_resource_type.find(
            task=autotests_task,
            state=ctr.State.READY).first()
        if autotests_result_resource is None:
            self.set_info(u"Отчет автотестов не найден")
            return None
        else:
            return str(sdk2.ResourceData(autotests_result_resource).path)

    def update_context_from_state(self):
        for field, value in self.initial_regression_state["context"].iteritems():
            setattr(self.Context, field, value)

    def wait_run_regression_and_autotests_tasks(self):

        run_regression_task = self.Parameters.run_regression_task
        autotests_task = self.Parameters.autotests_task

        with self.memoize_stage.run_regression_task:
            raise sdk2.WaitTask(run_regression_task,
                                [Status.Group.FINISH, Status.Group.BREAK])

        if run_regression_task.status != Status.SUCCESS:
            self.set_info(u'Родительская таска {} не успешна статус={}'.format(
                html_link(get_task_link(run_regression_task.id)),
                run_regression_task.status),
                do_escape=False)
            raise TaskFailure()

        with self.memoize_stage.autotests_task:
            raise sdk2.WaitTask(autotests_task,
                                [Status.Group.FINISH, Status.Group.BREAK])

        with self.memoize_stage.check_booking:
            self.check_booking()

        self.set_info(u' Запуск автотестов {}'.format(
            html_link(get_task_link(autotests_task.id))),
            do_escape=False)

        if autotests_task.status != Status.SUCCESS:
            self.set_info(u' WARNING Запуск автотестов не завершился успешно, статус={}'.format(
                autotests_task.status))

        return run_regression_task, autotests_task

    def continue_regression(self):

        run_regression_task, autotests_task = self.wait_run_regression_and_autotests_tasks()
        autotests_report_path = self.get_autotests_results_path(autotests_task)

        self.update_context_from_state()
        manager = self.regression_manager_class(
            regression_config=self.regression_config,
            task_parameters=self.Parameters,
            task_context=self.Context,
            oauth_vault=self.oauth_vault
        )
        creation_result = manager.continue_regression(autotests_report_path, self.Parameters.issues_filter)
        if creation_result.get("info_message"):
            self.set_info(creation_result["info_message"],
                          do_escape=False)

        main_ticket, manual_tickets, manual_runs, assessors_tickets, assessors_runs = creation_result["runs_and_tickets"]

        if assessors_runs:
            assessors_tasks = [self.create_assessors_task(assessors_runs, assessors_tickets)]
            self.enqueue_asessor_tasks(assessors_tasks)
        self.start_runs_monitoring(assessors_runs, manual_runs, manual_tickets, main_ticket)
        self.create_regression_state_resource()

    def launch_autotests_and_continue_regression_tasks(self, automated_info):
        raise NotImplementedError()

    def wait_builds(self, builds):
        if any(b.state != 'finished' for b in builds):
            raise sdk2.WaitTask(
                BrowserWaitTeamcityBuilds(
                    self,
                    description='Wait browser regression builds',
                    mode='WAIT_GIVEN',
                    builds=' '.join(str(build.id) for build in builds),
                    oauth_vault=ROBOT_BRO_QA_INFRA_TOKEN_VAULT,
                ).enqueue(),
                list(Status.Group.FINISH + Status.Group.BREAK),
                True,
            )
        else:
            if any(b.status != 'SUCCESS' for b in builds):
                raise TaskFailure('Одна из сборок упала')
