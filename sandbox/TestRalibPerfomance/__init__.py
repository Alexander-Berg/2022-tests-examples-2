import statface_utils as stat_utils

import sandbox.projects.logs.common as us_ci
import sandbox.projects.logs.common.binaries as us_bin
import sandbox.projects.logs.resources as us_ci_rst

from sandbox.projects.common import apihelpers
from sandbox.projects.common import utils
from sandbox.sandboxsdk.svn import Svn
from sandbox.sandboxsdk.paths import make_folder
from sandbox.sandboxsdk.paths import copy_path
from sandbox.sandboxsdk.channel import channel
from sandbox.sandboxsdk import parameters as sp
from sandbox.sandboxsdk.task import SandboxTask
from sandbox.sandboxsdk import environments

import datetime
import httplib
import json
import urllib2
import re
import logging

import os
from os.path import join as pj


CONFIDENCE_LEVELS = [0.7, 0.75, 0.8, 0.85, 0.9, 0.95]


BRANCH_DATE_TO_TASK_ID_AND_SVN_URL = 'branch_date_to_task_id_and_svn_url'
BRANCH_DATE_TO_READY_RESOURCE_ID = 'branch_date_to_ready_resource_id'
BUILD_SVN_PATH_ATTR_NAME = 'build_from_svn_url'
READY_ATTR_VALUE = 'ready'
TEST_RESULTS = 'test_results'
TESTS_FINISHED = 'tests_finished'
START_TIME = 'start_time'
END_TIME = 'end_time'

DATETIME_FORMAT = "%Y%m%d:%H:%M:%S"
BRANCH_DATE_FORMAT = "%Y-%m-%d"
SOLOMON_FORMAT = "%Y-%m-%dT%H:%M:%SZ"

OUR_BRANCHES = 'our_branches'
OUR_REVISIONS = 'our_revisions'

SOLOMON_PRODUCTION_ADDRESS = "api.solomon.search.yandex.net"

URL = "svn+ssh://arcadia.yandex.ru/arc/branches/user_sessions"

SENT_TO_SOLOMON = 'sent_to_solomon'
SENT_TO_STATFACE = 'sent_to_statface'


def GetNowStr():
    return datetime.datetime.strftime(datetime.datetime.now(), DATETIME_FORMAT)


class CommandInfo(object):
    def __init__(self, branch_date_str, launch_index, command_parts):
        self.branch_date_str = branch_date_str
        self.launch_index = launch_index
        self.command_parts = command_parts

    def __iter__(self):
        return iter(self.command_parts)


class TestResults(object):
    def __init__(self, task_ctx):
        self.task_ctx = task_ctx
        self.task_ctx[TEST_RESULTS] = {}

    def __call__(self, cmd_info, result):
        if cmd_info.branch_date_str not in self.task_ctx[TEST_RESULTS]:
            self.task_ctx[TEST_RESULTS][cmd_info.branch_date_str] = []

        current_len = len(self.task_ctx[TEST_RESULTS][cmd_info.branch_date_str])
        if current_len <= cmd_info.launch_index:
            self.task_ctx[TEST_RESULTS][cmd_info.branch_date_str] += [None for i in xrange(cmd_info.launch_index - current_len + 1)]

        self.task_ctx[TEST_RESULTS][cmd_info.branch_date_str][cmd_info.launch_index] = result


class FetcherBinaryResourceId(sp.SandboxStringParameter):
    name = 'fetcher_binary_resource_id'
    description = 'Id of resource fetcher_binary'


class LaunchesCount(sp.SandboxIntegerParameter):
    name = 'launches_count'
    description = 'N. How many times we should launch every experiment'
    default_value = 1


class MemoryLimitGB(sp.SandboxIntegerParameter):
    name = 'memory_limit_gb'
    description = 'Memory_limit in GB'
    default_value = 8


class MaxProcessesCount(sp.SandboxIntegerParameter):
    name = 'max_processes_count'
    description = 'M. How many processes can run at the same time'
    default_value = 10


class FetchedSessionsPercent(sp.SandboxIntegerParameter):
    name = 'fetched_sessions_percent'
    description = 'Ksi%. Percentage size of fetched sessions (Integer)'
    default_value = 10


class FetchedSessionsPath(sp.SandboxStringParameter):
    name = 'fetched_sessions_path'
    description = 'Fetched sessions path for test'
    default_value = ''


class RAlibVersionsCount(sp.SandboxIntegerParameter):
    name = 'ralib_versions_count'
    description = 'K RAlib versions. How many last ones to check'
    default_value = 12


class RAlibVersionsToIgnore(sp.SandboxStringParameter):
    name = 'ralib_versions_to_ignore'
    description = 'RAlib versions to ignore. \',\'-separated, like dates. For example, 2017-09-04'
    default_value = ''


class ArcadiaPatch(sp.SandboxStringParameter):
    name = 'arcadia_patch'
    description = 'Arcadia patch, which will be applied to old branches in order to have ralib_perfomance_tester project there'
    default_value = ''


class ShouldSendToStatface(sp.SandboxBoolParameter):
    name = 'send_to_statface'
    description = 'Whether we should send results to Statface'
    default_value = False


class ReleaseMachineMode(sp.SandboxBoolParameter):
    name = 'is_release_machine_mode'
    description = 'Turn on release machine mode'
    default_value = False


class RevisionsMode(sp.SandboxBoolParameter):
    name = 'revisions_mode'
    description = 'Turn on revisions mode'
    default_value = False


class Revisions(sp.SandboxStringParameter):
    name = 'revisions'
    description = 'Revisions for revisions mode. \',\'-separated'
    default_value = ''


class RevisionsModeFetchDate(sp.SandboxStringParameter):
    name = 'revisions_mode_fetched_date'
    description = 'Revisions mode fetched date'
    default_value = ''


class TestRalibPerfomance(SandboxTask):
    ''' Task for testing speed perfomance of ralib '''

    type = 'TEST_RALIB_PERFOMANCE'
    environment = (environments.PipEnvironment('yandex-yt', use_wheel=False, version='0.10.8'),)

    input_parameters = [
        RAlibVersionsCount,
        RAlibVersionsToIgnore,
        ArcadiaPatch,
        MemoryLimitGB,
        FetchedSessionsPercent,
        FetcherBinaryResourceId,
        FetchedSessionsPath,
        MaxProcessesCount,
        ShouldSendToStatface,
        RevisionsMode,
        Revisions,
        RevisionsModeFetchDate,
        ReleaseMachineMode,
    ]

    def CreateBuildSubtasksIfNeeded(self):
        if BRANCH_DATE_TO_TASK_ID_AND_SVN_URL not in self.ctx:
            task_id_and_svn_url = {}
            ready_resource_id = {}

            our_bins_ids = self.ctx[OUR_REVISIONS] if self.ctx[RevisionsMode.name] else self.ctx[OUR_BRANCHES]
            for our_branch_date in our_bins_ids:
                if self.ctx[RevisionsMode.name]:
                    full_branch_url = "arcadia:/arc/trunk/arcadia@{revision}".format(revision=our_branch_date)
                    patch = self.ctx[ArcadiaPatch.name]
                else:
                    branch_url = pj(URL, our_branch_date)
                    branch_url_revision = Svn.log(branch_url, 2000000, 'HEAD', stop_on_copy=True)[0]['revision']
                    full_branch_url = "arcadia:/arc/branches/userdata/{date_str}/arcadia@{revision}".format(date_str=our_branch_date, revision=branch_url_revision)

                    logs_tools_folder_url = "arcadia:/arc/branches/userdata/{date_str}/arcadia/quality/logs/tools@{revision}".format(date_str=our_branch_date, revision=branch_url_revision)
                    should_use_patch = 'ralib_etalon_perfomance_tester' not in Svn.list(logs_tools_folder_url, as_list=True)
                    patch = self.ctx[ArcadiaPatch.name] if should_use_patch else ''

                self.ctx['used_patch'] = patch
                attrs_for_fetching_ready_bin = {BUILD_SVN_PATH_ATTR_NAME: full_branch_url, 'arcadia_patch': patch}

                (bin_resource_id, bin_build_task_id) = us_bin.get_binary_from_svn_path('ralib_etalon_perfomance_tester',
                                                                                       us_ci_rst.RALIB_ETALON_BINARY,
                                                                                       self, full_branch_url,
                                                                                       attrs_for_fetching_ready_bin=attrs_for_fetching_ready_bin,
                                                                                       patch=patch)

                if bin_resource_id is not None:
                    ready_resource_id[our_branch_date] = bin_resource_id
                else:
                    task_id_and_svn_url[our_branch_date] = (bin_build_task_id, full_branch_url)

            self.ctx[BRANCH_DATE_TO_TASK_ID_AND_SVN_URL] = task_id_and_svn_url
            self.ctx[BRANCH_DATE_TO_READY_RESOURCE_ID] = ready_resource_id

            utils.wait_all_subtasks_stop()
        elif not utils.check_all_subtasks_done():
            utils.restart_broken_subtasks()

    def DoSyncBinary(self, res_id, branch_date, bin_folder):
        tmp_bin_path = self.sync_resource(res_id)
        bin_name = branch_date
        self.bin_path[branch_date] = pj(bin_folder, bin_name)
        copy_path(tmp_bin_path, self.bin_path[branch_date])

    def ApplyBinariesCashinLogicAndTtl(self, resource_id, build_from_svn_url):
        attr_value_to_set = build_from_svn_url
        channel.sandbox.set_resource_attribute(resource_id,
                                                BUILD_SVN_PATH_ATTR_NAME,
                                                attr_value_to_set)
        if 'used_patch' in self.ctx:
            channel.sandbox.set_resource_attribute(resource_id,
                                                    'arcadia_patch',
                                                    self.ctx['used_patch'])
        channel.sandbox.set_resource_attribute(resource_id,
                                               "ttl",
                                               "14")

    def SyncBinaries(self, local_bin_folder):
        # build subtasks have been created and have already finished
        self.bin_path = {}

        # sync binaries which have already been built long ago
        for branch_date, res_id in self.ctx[BRANCH_DATE_TO_READY_RESOURCE_ID].iteritems():
            self.DoSyncBinary(res_id, branch_date, local_bin_folder)

        failed_builds_count = 0
        # sync binaries which our subtasks have just built
        for branch_date, build_task_id_and_svn_url in self.ctx[BRANCH_DATE_TO_TASK_ID_AND_SVN_URL].iteritems():
            build_task_id, build_from_svn_url = build_task_id_and_svn_url
            task = channel.sandbox.get_task(build_task_id)
            if task.is_failure():
                failed_builds_count += 1
                continue
            res_id = task.ctx["{bin_name}_resource_id".format(bin_name="ralib_etalon_perfomance_tester")]
            self.DoSyncBinary(res_id, branch_date, local_bin_folder)
            self.ApplyBinariesCashinLogicAndTtl(res_id, build_from_svn_url)

        if failed_builds_count > 0:
            raise Exception("You can relaunch only by cloning this task. Some binaries failed to build!")

    def PrepareBinaries(self):
        local_bin_folder = pj(self.abs_path(), "bins")
        make_folder(local_bin_folder)

        self.SyncBinaries(local_bin_folder)

    def GetYTToken(self):
        return self.get_vault_data("USERSESSIONSTOOLS", "userdata-sessions-build-ci-token")

    def GetStafaceToken(self):
        return self.get_vault_data("USERSESSIONSTOOLS", "USER_SESSIONS_STATFACE_TOKEN")

    def MakeYTPreparations(self):
        import yt.wrapper as yt

        yt.config["proxy"]["url"] = "hahn"
        yt.config["token"] = self.GetYTToken()

    def Prepare(self):
        self.MakeYTPreparations()

        if OUR_BRANCHES not in self.ctx and OUR_REVISIONS not in self.ctx:
            if self.ctx[RevisionsMode.name]:
                self.ctx[OUR_REVISIONS] = [rev.strip(' ') for rev in self.ctx[Revisions.name].split(',')]
            else:
                ralib_versions_count = self.ctx[RAlibVersionsCount.name]
                if ralib_versions_count < 1:
                    raise Exception("It looks like you have to relaunch by cloning and changing the field. Ralib versions count is incorrect: {}!".format(ralib_versions_count))

                branches_to_ignore = [branch.strip(' ') for branch in self.ctx[RAlibVersionsToIgnore.name].split(',')]
                branches = [branch.strip('/') for branch in Svn.list(URL, as_list=True)]
                logging.info("{}".format(branches[-1]))
                regex = re.compile('^(19|20)\d\d-(0[1-9]|1[012])-(0[1-9]|[12][0-9]|3[01])$')
                self.ctx[OUR_BRANCHES] = [branch for branch in filter(lambda x: regex.search(x) and x not in branches_to_ignore, branches)[-ralib_versions_count:]]

    def IsFetchedSessionsReady(self, yt_path_to_fetched_sessions):
        import yt.wrapper as yt

        if yt.exists(yt_path_to_fetched_sessions):
            return bool(yt.get_attribute(yt_path_to_fetched_sessions, READY_ATTR_VALUE, default=False))
        return False

    def GetEnv(self):
        env = dict(os.environ)
        env['MR_RUNTIME'] = 'YT'
        env['YT_PREFIX'] = '//'
        env['YT_TOKEN'] = self.GetYTToken()
        env['YT_PROXY'] = 'hahn'

        gb_memory_limit = self.ctx[MemoryLimitGB.name]
        if not gb_memory_limit:
            gb_memory_limit = MemoryLimitGB.default_value

        YTSpec = {
            "reducer": {"memory_limit": gb_memory_limit * 1024 * 1024 * 1024},
            "data_size_per_job": 8589934592,
            "job_io": {
                "table_writer": {
                    "max_row_weight": 128 * 1024 * 1024
                }
            }
        }
        env['YT_SPEC'] = json.dumps(YTSpec)

        return env

    def GetInputSessionsPath(self, date_of_sessions_to_fetch_str):
        return "//user_sessions/pub/search/daily/{}/clean".format(date_of_sessions_to_fetch_str)

    def MakeFetchCmd(self, date_of_sessions_to_fetch_str, yt_path_to_fetched_sessions, ksi_percent):
        fetcher_path = SandboxTask.sync_resource(self, self.ctx[FetcherBinaryResourceId.name])
        result = [fetcher_path, '-c', 'hahn',
                  '--input', self.GetInputSessionsPath(date_of_sessions_to_fetch_str),
                  '--output', yt_path_to_fetched_sessions,
                  '-p', str(ksi_percent)]

        return result

    def CreateFetchedSessionsIfNeeded(self):
        import yt.wrapper as yt

        self.ksi_percent = self.ctx[FetchedSessionsPercent.name]
        if self.ctx[ReleaseMachineMode.name]:
            return
        if self.ksi_percent <= 0 or self.ksi_percent > 100:
            raise Exception("It looks like you have to relaunch by cloning and changing the field. Ksi percent is incorrect: {}!".format(self.ksi_percent))
        if self.ksi_percent == 100:
            return

        date_of_sessions_to_fetch_str = self.ctx[RevisionsModeFetchDate.name] if self.ctx[RevisionsMode.name] else self.ctx[OUR_BRANCHES][0]
        self.date_of_sessions_to_fetch_str = date_of_sessions_to_fetch_str

        fetched_sessions_table_name = "{date_str}_{ksi}%".format(date_str=date_of_sessions_to_fetch_str, ksi=self.ksi_percent)
        yt_path_to_fetched_sessions = "//tmp/ralib_speed_test/fetched_sessions/{}".format(fetched_sessions_table_name)
        if not self.IsFetchedSessionsReady(yt_path_to_fetched_sessions):
            cmd = self.MakeFetchCmd(date_of_sessions_to_fetch_str, yt_path_to_fetched_sessions, self.ksi_percent)
            us_ci.RunProcesses([cmd], self.GetEnv())
            yt.set_attribute(yt_path_to_fetched_sessions, READY_ATTR_VALUE, True)

        self.yt_path_to_fetched_sessions = yt_path_to_fetched_sessions
        logging.info('Row_count = {}'.format(yt.get_attribute(yt_path_to_fetched_sessions, 'row_count')))
        logging.info('Uncompressed_data_size = {}'.format(yt.get_attribute(yt_path_to_fetched_sessions, 'uncompressed_data_size') / 1024. / 1024. / 1024. / 1024.))

    def FilesCmdPart(self):
        blockstat_path = self.sync_resource(apihelpers.get_last_resource(us_ci_rst.SESSIONS_BLOCKSTAT))

        return ['--blockstat', blockstat_path]

    def MakeTestCommand(self, branch_date, launch_index, input_path):
        tester_path = self.bin_path[branch_date]
        output_table = "{}_{}_{}".format(branch_date, launch_index, GetNowStr())
        output_path = "//tmp/ralib_speed_test/times_outputs/{}".format(output_table)
        return [tester_path, '-c', 'hahn', '--src', input_path, '--dst', output_path] + self.FilesCmdPart()

    def MakeTestCommandsTwoDimsContainer(self):
        launch_index_to_cmd = {}
        our_bins_ids = self.ctx[OUR_REVISIONS] if self.ctx[RevisionsMode.name] else self.ctx[OUR_BRANCHES]
        self.input_path = {}
        for branch_date in our_bins_ids:
            if self.ctx[FetchedSessionsPath.name]:
                input_path = self.ctx[FetchedSessionsPath.name]
            else:
                if self.ksi_percent == 100:
                    if self.ctx[RevisionsMode.name]:
                        input_path = "//user_sessions/pub/search/daily/{}/clean".format(self.ctx[RevisionsModeFetchDate.name])
                    else:
                        input_path = "//user_sessions/pub/search/daily/{}/clean".format(branch_date)
                else:
                    input_path = self.yt_path_to_fetched_sessions
            self.input_path[branch_date] = input_path

            launch_index_to_cmd[branch_date] = []
            for launch_index in xrange(self.ctx[LaunchesCount.name]):
                launch_index_to_cmd[branch_date].append(self.MakeTestCommand(branch_date, launch_index, input_path))

        return launch_index_to_cmd

    def TransformTestCmdsIntoSnakeLikeArray(self, launch_index_to_cmd):
        commands_infos = []
        our_bins_ids = self.ctx[OUR_REVISIONS] if self.ctx[RevisionsMode.name] else self.ctx[OUR_BRANCHES]
        reverse_our_branches = list(our_bins_ids)
        reverse_our_branches.reverse()
        for launch_index in xrange(self.ctx[LaunchesCount.name]):
            if launch_index % 2 == 0:
                our_branches_sequence = our_bins_ids
            else:
                our_branches_sequence = reverse_our_branches
            for branch_date in our_branches_sequence:
                commands_infos.append(CommandInfo(branch_date, launch_index, launch_index_to_cmd[branch_date][launch_index]))

        return commands_infos

    def MakeTestCommandsInfos(self):
        launch_index_to_cmd = self.MakeTestCommandsTwoDimsContainer()
        commands_infos = self.TransformTestCmdsIntoSnakeLikeArray(launch_index_to_cmd)
        return commands_infos

    def get_adjusted_adjusted_test_results(self, launch_index_to_test_result, N):
        launch_index_to_test_result_adjusted = {}

        ralib_versions_count = self.ctx[RAlibVersionsCount.name]
        cluster_states_metrics = [sum([launch_index_to_test_result[branch_date][j] for branch_date in self.ctx[OUR_BRANCHES]])
                                  / float(ralib_versions_count) for j in xrange(N)]
        avg_cluster_state_metric = sum(cluster_states_metrics) / N

        for branch_date in launch_index_to_test_result.keys():
            launch_index_to_test_result_adjusted[branch_date] = [None for i in xrange(N)]
            for launch_index in xrange(N):
                launch_index_to_test_result_adjusted[branch_date][launch_index] = \
                    launch_index_to_test_result[branch_date][launch_index] / \
                    cluster_states_metrics[launch_index] * avg_cluster_state_metric

        return launch_index_to_test_result_adjusted

    def DoCalculateMetrics(self, launch_index_to_test_result, N, confidence_level):
        import student_quantiles as t_quantiles
        import math

        alpha = 1 - confidence_level
        quantile_level = 1 - alpha / 2.
        from_ksi_to_100percent_norming_coef = 100. / self.ksi_percent
        logging.info("from_ksi_to_100percent_norming_coef -  {}".format(from_ksi_to_100percent_norming_coef))
        quantile = t_quantiles.QUANTILE_LEVEL_TO_FREEDOM_DEGREE_TO_QUANTILE[quantile_level][N - 1]
        coefficient_for_sigma = quantile / math.sqrt(N - 1)

        launch_index_to_test_result_adjusted = self.get_adjusted_adjusted_test_results(launch_index_to_test_result, N)

        to_100percent_normed_avg = {}
        to_confidence_interval_left_bound = {}
        to_confidence_interval_right_bound = {}

        to_100percent_normed_avg_adjusted = {}
        to_confidence_interval_left_bound_adjusted = {}
        to_confidence_interval_right_bound_adjusted = {}

        for branch_date_str, test_results in launch_index_to_test_result.iteritems():
            adjusted_test_results = launch_index_to_test_result_adjusted[branch_date_str]

            def adjust_bounds(normed_test_results, to_100percent_normed_avg, to_confidence_interval_left_bound, to_confidence_interval_right_bound):
                to_100percent_normed_avg[branch_date_str] = sum(normed_test_results) / float(N)
                sigma = math.sqrt(sum([x**2 for x in normed_test_results]) / float(N) - (sum(normed_test_results) / float(N))**2)
                to_confidence_interval_left_bound[branch_date_str] = to_100percent_normed_avg[branch_date_str] - coefficient_for_sigma * sigma
                to_confidence_interval_right_bound[branch_date_str] = to_100percent_normed_avg[branch_date_str] + coefficient_for_sigma * sigma

            normed_test_results = [from_ksi_to_100percent_norming_coef * res / 3600 for res in test_results]
            normed_adjusted_test_results = [from_ksi_to_100percent_norming_coef * res / 3600 for res in adjusted_test_results]

            logging.info("normed_test_results -  {}".format(normed_test_results))
            logging.info("normed_adjusted_test_results -  {}".format(normed_adjusted_test_results))

            adjust_bounds(normed_test_results, to_100percent_normed_avg,
                          to_confidence_interval_left_bound, to_confidence_interval_right_bound)
            adjust_bounds(normed_adjusted_test_results, to_100percent_normed_avg_adjusted,
                          to_confidence_interval_left_bound_adjusted, to_confidence_interval_right_bound_adjusted)

        return (to_100percent_normed_avg,
                to_confidence_interval_left_bound,
                to_confidence_interval_right_bound,
                to_100percent_normed_avg_adjusted,
                to_confidence_interval_left_bound_adjusted,
                to_confidence_interval_right_bound_adjusted)

    def ChooseBestSubsample(self):
        confidence_level = 0.9

        best_subsample_launch_index_to_test_result = None
        best_adjusted_confidence_intervals_lens_avg = None
        for beg in xrange(self.ctx[LaunchesCount.name] - 2):
            for end in xrange(beg + 2, self.ctx[LaunchesCount.name] + 1):
                N = end - beg

                launch_index_to_test_result = {}
                for br in self.ctx[TEST_RESULTS].keys():
                    launch_index_to_test_result[br] = self.ctx[TEST_RESULTS][br][beg:end]

                results_tuple = self.DoCalculateMetrics(launch_index_to_test_result, N, confidence_level)

                to_100percent_normed_avg = results_tuple[0]
                to_confidence_interval_left_bound = results_tuple[1]
                to_confidence_interval_right_bound = results_tuple[2]

                to_100percent_normed_avg_adjusted = results_tuple[3]
                to_confidence_interval_left_bound_adjusted = results_tuple[4]
                to_confidence_interval_right_bound_adjusted = results_tuple[5]

                confidence_intervals_lens_sum = 0
                confidence_intervals_lens_max = None
                adjusted_confidence_intervals_lens_sum = 0
                adjusted_confidence_intervals_lens_max = None

                for br in self.ctx[OUR_BRANCHES]:
                    def update_sum_and_max(to_100percent_normed_avg, to_confidence_interval_left_bound,
                                           to_confidence_interval_right_bound, confidence_intervals_lens_sum, confidence_intervals_lens_max):
                        cur_len = (to_confidence_interval_right_bound[br] - to_confidence_interval_left_bound[br]) / to_100percent_normed_avg[br] * 100
                        new_sum = confidence_intervals_lens_sum + cur_len
                        new_max = cur_len if confidence_intervals_lens_max is None else max(cur_len, confidence_intervals_lens_max)
                        return new_sum, new_max

                    confidence_intervals_lens_sum, confidence_intervals_lens_max = \
                        update_sum_and_max(to_100percent_normed_avg, to_confidence_interval_left_bound,
                                           to_confidence_interval_right_bound, confidence_intervals_lens_sum,
                                           confidence_intervals_lens_max)

                    adjusted_confidence_intervals_lens_sum, adjusted_confidence_intervals_lens_max = \
                        update_sum_and_max(to_100percent_normed_avg_adjusted, to_confidence_interval_left_bound_adjusted,
                                           to_confidence_interval_right_bound_adjusted, adjusted_confidence_intervals_lens_sum,
                                           adjusted_confidence_intervals_lens_max)

                confidence_intervals_lens_avg = float(confidence_intervals_lens_sum) / self.ctx[RAlibVersionsCount.name]
                adjusted_confidence_intervals_lens_avg = float(adjusted_confidence_intervals_lens_sum) / self.ctx[RAlibVersionsCount.name]

                if confidence_intervals_lens_avg > 4.55 or \
                   confidence_intervals_lens_max > 5.2 or \
                   adjusted_confidence_intervals_lens_avg > 1.64 or \
                   adjusted_confidence_intervals_lens_max > 3.6:
                    continue
                elif best_subsample_launch_index_to_test_result is None or \
                     adjusted_confidence_intervals_lens_avg < best_adjusted_confidence_intervals_lens_avg:
                    best_subsample_launch_index_to_test_result = launch_index_to_test_result
                    best_adjusted_confidence_intervals_lens_avg = adjusted_confidence_intervals_lens_avg
        return best_subsample_launch_index_to_test_result

    def SendToSolomon(self, results_tuple, confidence_level):
        to_100percent_normed_avg_adjusted = results_tuple[3]
        to_confidence_interval_left_bound_adjusted = results_tuple[4]
        to_confidence_interval_right_bound_adjusted = results_tuple[5]

        self.data = {}
        self.data["commonLabels"] = {
            "project": "user_sessions",
            "cluster": "hahn",
            "service": "rem-tasks",
            "task-name": "ralib",
            "speed-graph": "etalon_sess-{sess_date}.measure_start-{start}.measure_end-{end}".format(
                sess_date=self.date_of_sessions_to_fetch_str,
                start=self.ctx[START_TIME],
                end=self.ctx[END_TIME],
            )
        }
        self.data["sensors"] = []

        mere_avgs_were_sent = (confidence_level != CONFIDENCE_LEVELS[0])
        metric_name_and_values_and_extra_labels = [] if mere_avgs_were_sent else [("cpu_hours", to_100percent_normed_avg_adjusted, {})]

        should_append_zero_for_confidence_level = ((confidence_level * 100) % 10) == 0
        metric_name_and_values_and_extra_labels += [
            ("cpu_hours_confidence_interval_of_level_{}{}".format(confidence_level, 0 if should_append_zero_for_confidence_level else ""),
             to_confidence_interval_left_bound_adjusted,
             {"confidence_interval_bound": "left"}),
            ("cpu_hours_confidence_interval_of_level_{}{}".format(confidence_level, 0 if should_append_zero_for_confidence_level else ""),
             to_confidence_interval_right_bound_adjusted,
             {"confidence_interval_bound": "right"}),
        ]

        for metric_name, to_metric, extra_labels in metric_name_and_values_and_extra_labels:
            for branch_date_str, metric_value in to_metric.iteritems():
                labels = {"ralib-speed-metric": metric_name}
                labels.update(extra_labels)
                ts = datetime.datetime.strftime(datetime.datetime.strptime(branch_date_str, BRANCH_DATE_FORMAT), SOLOMON_FORMAT)
                self.data["sensors"].append({"labels": labels, "ts": ts, "value": metric_value})

        sensors_json = json.dumps(self.data, indent=4)

        solomon_address = SOLOMON_PRODUCTION_ADDRESS
        http_request = urllib2.Request("http://" + solomon_address + "/push/json", headers={"Content-Type": "application/json"})
        http_response = urllib2.urlopen(http_request, sensors_json, timeout=20)

        if http_response.getcode() != httplib.OK:
            raise Exception(("Later relaunch by pressing 'Run'-button might help, if this is temporary problem. "
                             "Problem: push to Solomon {} failed: error = {}, content = {}".format(solomon_address,
                                                                                                   http_response.getcode(),
                                                                                                   http_response.read())))

    def SendToStatface(self, results, uncomp_tb_input_size, is_release_machine, date_for_graph):
        stat_utils.send_new_vals_to_statface(self, results, uncomp_tb_input_size, is_release_machine, date_for_graph)

    def CalculateMetrics(self, launch_index_to_test_result, confidence_level):
        some_br = self.ctx[OUR_BRANCHES][0]
        N = len(launch_index_to_test_result[some_br])
        return self.DoCalculateMetrics(launch_index_to_test_result, N, confidence_level)

    def ShouldSendToSolomon(self):
        return False

    def ShouldSendToStatface(self):
        return self.ctx[ShouldSendToStatface.name] and not self.ctx.get(SENT_TO_STATFACE, False)

    def ShouldSendSomewhere(self):
        return self.ShouldSendToSolomon() or self.ShouldSendToStatface()

    def on_execute(self):
        self.ctx[LaunchesCount.name] = 1
        self.Prepare()
        self.CreateBuildSubtasksIfNeeded()
        self.PrepareBinaries()
        self.CreateFetchedSessionsIfNeeded()

        commands_infos = self.MakeTestCommandsInfos()

        if not self.ctx.get(TESTS_FINISHED, False):
            self.ctx[START_TIME] = GetNowStr()
            us_ci.RunSimultaneousProcesses(commands_infos, self.GetEnv(), self.ctx[MaxProcessesCount.name], results_callable=TestResults(self.ctx), env_getter=None)
            self.ctx[END_TIME] = GetNowStr()
            self.ctx[TESTS_FINISHED] = True

        import yt.wrapper as yt
        self.ctx["uncompressed_tb_size"] = {}
        for branch_date, input_path in self.input_path.iteritems():
            self.ctx["uncompressed_tb_size"][branch_date] = float(yt.get_attribute(input_path, 'uncompressed_data_size')) / 1024 ** 4

        if self.ShouldSendToStatface():
            is_release_machine = self.ctx[ReleaseMachineMode.name]
            date = self.ctx[RevisionsModeFetchDate.name] if is_release_machine else None
            if not is_release_machine and self.ctx[RevisionsMode.name]:
                raise Exception("You can't send to statface in revisions mode!")

            self.SendToStatface(self.ctx[TEST_RESULTS], self.ctx["uncompressed_tb_size"], is_release_machine, date)

            self.ctx[SENT_TO_STATFACE] = True
