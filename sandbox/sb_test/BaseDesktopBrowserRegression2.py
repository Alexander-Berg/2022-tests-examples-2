# -*- coding: utf-8 -*-
import sandbox
from sandbox import sdk2
from sandbox.projects.browser.autotests_qa_tools.classes.regression_manager.desktop import DBroRegressionManager

from sandbox.projects.browser.autotests_qa_tools.classes.testing_groups import (
    REPORT_OVERHEAD, TSP_HOURS, REGRESSION_MAILLIST)
from sandbox.projects.browser.autotests_qa_tools.configs.regression import RegressionConfigs
from sandbox.projects.browser.autotests_qa_tools.sb_test.BaseBrowserRegression2 import BaseBrowserRegression2
from sandbox.projects.browser.autotests_qa_tools.common import (
    is_dev_sandbox, check_browser_build, check_tests_build, get_platform, get_browser_version_number)

CONFIGS_MODULE = RegressionConfigs.dbro.value


class BaseDesktopBrowserRegression2(BaseBrowserRegression2):

    regression_manager_class = DBroRegressionManager
    assessors_testrun_properties_to_show = 'Brand/PartnerID,build,lite_installer,alice,arc,mini_installer,rss,fake,fake_mini_installer,fake_rss'
    configs_module = CONFIGS_MODULE

    class Context(BaseBrowserRegression2.Context):
        deadline = None
        assessors_links = {}
        task_id = None

    class Parameters(BaseBrowserRegression2.Parameters):
        test_suites = None
        regression_type = sdk2.parameters.String(
            'Regression type', required=True, choices=[(_, _) for _ in CONFIGS_MODULE.TEST_SUITE_CONFIGS + ['custom']],
            ui=sdk2.parameters.String.UI('select')
        )
        with regression_type.value['custom']:
            test_suites_override = BaseBrowserRegression2.Parameters.test_suites()

        deadline = None
        hitman_process_id = sdk2.parameters.String('Hitman process', default='testing_browser_automatic',
                                                   required=True)
        assessors_quota = sdk2.parameters.String('Assessors launch quota', default='brocase', required=True)
        start_hitman_jobs_automatically = BaseBrowserRegression2.Parameters.start_hitman_jobs_automatically(
            default=True)
        with sdk2.parameters.Group('DBRO specific parameters') as dbro_params:
            distribution_type = sdk2.parameters.String('Distribution type', required=True, default='brands',
                                                       choices=[(_, _) for _ in ['brands', 'partners']])
            distribution_name = sdk2.parameters.String('Brand/Partner name', required=True, default='yandex')
            check_resolves = sdk2.parameters.Bool('Aggregator needed', default=False)
            with check_resolves.value[True]:
                resolves_filter = sdk2.parameters.String(
                    'Aggregator filter', default='', multiline=True,
                     description='Filter to search for additional resolved issues (aside from source code diff)'
                                 ' See <a href="https://wiki.yandex-team.ru/browser/dev/infra/qa/regression-launcher/diff/#nastrojjkadiffavregressionnyxtaskax">documentation</a>')
            configuration_ticket = sdk2.parameters.String('Configuration ticket')
            release_ticket = sdk2.parameters.String('Release ticket')
            regression_deadline = sdk2.parameters.Integer('Regression deadline', required=True,
                                                          description='Regression duration in hours')
            manual_launch_comment = sdk2.parameters.String('Manual launch comment', multiline=True,
                                                           description='Special parameters for manual runs')
            link_for_tolokers = sdk2.parameters.String('Test stend for tolokers', description='link to yandex disk')

    def on_enqueue(self):
        with self.memoize_stage.add_params_from_config:
            if self.Parameters.regression_type != 'custom':
                self.Parameters.test_suites_override = {}

    def on_execute(self):
        self.Context.task_id = self.id
        self.validate_input()

    def check_input(self):
        builds = self.get_builds()
        build_problems = super(BaseDesktopBrowserRegression2, self).check_input()
        build_problems.extend(check_browser_build(builds.get("browser_build")))
        if builds.get("fake_build", None):
            build_problems.extend(check_browser_build(builds.get("fake_build")))
        if builds.get("tests_build", None):
            build_problems.extend(check_tests_build(builds["tests_build"]))
        if self.platform != 'Linux' and self.Parameters.enable_autotests and (not builds.get("fake_build", None) or not builds.get("tests_build", None)):
            build_problems.append(u'Для автотестов требуется фейковая сборка браузера и сборка с тестами')
        if self.Parameters.check_resolves and not self.Parameters.old_build_id:
            build_problems.append(u'Требуется проверка тикетов из диффа тестированием,'
                                  u' но не указана предыдущая сборка для подсчета диффа')
        if self.Parameters.resolves_filter:
            build_problems.extend(self.check_filter(self.Parameters.resolves_filter))
        return build_problems

    @property
    def whom_notify_about_asessors_start(self):
        return REGRESSION_MAILLIST

    @property
    def whom_notify_from_hitman(self):
        return REGRESSION_MAILLIST

    @property
    def affected_version(self):
        return get_browser_version_number(self.get_builds()["browser_build"])

    @property
    def test_stend(self):
        return self.Context.assessors_links[self.Parameters.distribution_type][self.Parameters.distribution_name]['build'] + (
            u'\nСсылка на сборку в Яндекс.Диск: {}'.format(self.Parameters.link_for_tolokers)
            if self.Parameters.link_for_tolokers else ''
        )

    @property
    def min_leeway_time_for_autotests(self):
        return 30

    @property
    def requester_code(self):
        return self.get_builds()["browser_build"].last_changes[0].version

    def get_assessors_deadline(self, assessors_runs):
        return self.regression_config['deadline']

    @property
    @sandbox.common.utils.singleton
    def platform(self):
        return get_platform(self.get_builds()["browser_build"])

    # TODO: move 2 regression manager
    def update_tickets(self, regression_result):
        for group, assessors_ticket in regression_result.assessors_tickets.iteritems():
            estimate_ms = self.count_assessors_time(regression_result.assessors_runs.get(group, {}))
            self.startrek_client.issues.update(
                self.startrek_client.issues[assessors_ticket],
                ignore_version_change=True,
                qaEstimation='PT{}S'.format(int(estimate_ms / 1000))
            )
        total_tsp = 0
        for group, manual_ticket in regression_result.manual_tickets.iteritems():
            issue = self.startrek_client.issues[manual_ticket]
            estimate_ms = sum(run.fixed_average_duration
                              for suite, suite_runs in regression_result.manual_runs.get(group, {}).iteritems()
                              for run in suite_runs)
            time_to_test_ms = estimate_ms * REPORT_OVERHEAD
            tsp = round(time_to_test_ms / 1000.0 / 60 / 60 / TSP_HOURS, 1)
            total_tsp += tsp
            fields = {"ignore_version_change": True}
            if not is_dev_sandbox():
                fields['testingStoryPoints'] = tsp
            self.startrek_client.issues.update(issue, **fields)

        if not is_dev_sandbox() and regression_result.main_ticket:
            self.startrek_client.issues.update(
                self.startrek_client.issues[regression_result.main_ticket],
                testingStoryPoints=total_tsp,
                ignore_version_change=True
            )

    def count_assessors_time(self, runs):
        all_time = 0
        for suite, suite_runs in runs.iteritems():
            # Assessors cases are run on different environments just to check same case with different assessors
            # Here we count time only from one of environments
            # https://st.yandex-team.ru/BYIN-7264
            environment = suite_runs[0].currentEnvironment['title']
            all_time += sum(run.estimate_with_default for run in
                            filter(lambda r: r.currentEnvironment['title'] == environment, suite_runs))
        return all_time

    def upload_files_to_s3(self, build, fake_build, distributions):
        return {}
