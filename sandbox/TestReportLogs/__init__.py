# -*- coding: utf-8 -*-

import copy
import os
from os.path import join as pj
import logging
from collections import defaultdict

import sandbox.common.types.task as ctt

import sandbox.sandboxsdk.parameters as sdk_parameters
from sandbox.sandboxsdk.parameters import ResourceSelector, SandboxStringParameter
from sandbox.sandboxsdk.paths import make_folder
from sandbox.sandboxsdk.process import run_process
from sandbox.sandboxsdk.task import SandboxTask
from sandbox import sdk2

import sandbox.projects.common.constants as consts
from sandbox.projects.logs import resources
import sandbox.projects.geobase.Geodata6BinXurmaStable.resource as geo_resource
from sandbox.projects.logs.common.binaries import REACTOR_BINARIES

from sandbox.projects.common import error_handlers as eh
from sandbox.projects.common.apihelpers import get_task_resource_id
from sandbox.projects.common.build import parameters

SCARAB_LOG = 'scarab_log'


class MakeBin(sdk_parameters.SandboxBoolParameter):
    name = 'make_bin_by_ya_make'
    description = 'Make bin by ya make for scarab tester'
    required = False
    default_value = False


class LogName(SandboxStringParameter):
    name = 'log_name'
    description = 'Log name'
    multiline = False
    required = True
    choices = (
        ('access_log', 'access_log'),
        ('blockstat_log', 'blockstat_log'),
        ('profile_log', 'profile_log'),
        ('reqans_log', 'reqans_log'),
        ('saas_reqans_log', 'saas_reqans_log'),
        ('saas_access_log', 'saas_access_log'),
        (SCARAB_LOG, SCARAB_LOG),
    )


class InputData(ResourceSelector):
    name = 'input_data'
    description = 'Входные данные'
    multiline = True
    required = True


class IsLogByColumns(sdk_parameters.SandboxBoolParameter):
    name = 'log_by_columns'
    description = 'Лог подлежит раскладыванию в колонки на YT. Выключите если ваш лог в YAMR-формате'
    required = False
    default_value = True


def ReadRecords(file_path, delimiter):
    with open(file_path, 'r') as f:
        content = f.read()

        for record in content.split(delimiter):
            yield record


def CountNonemptyRecords(file_path, delimiter):
    lines_count = 0

    for line in ReadRecords(file_path, delimiter):
        if len(line.strip()) > 0:
            lines_count += 1

    return lines_count


class BaseTester(object):
    def __init__(self, ctx, task):
        self.ctx = ctx
        self.task = task

    def RunProcess(self, cmd, input=None, log_prefix=None):
        process = run_process(cmd,
                              wait=True,
                              outs_to_pipe=False,
                              close_fds=True,
                              check=False,
                              shell=True,
                              log_prefix=log_prefix,
                              environment=self.task.env
                              )
        process.communicate()
        if process.returncode != 0:
            exc_msg = ''

            error_file_path = process.stderr_path
            if error_file_path is not None:
                error = None
                with open(error_file_path, 'r') as error_file:
                    error = error_file.read().strip()
                exc_msg += 'error: {}\n'.format(error)

            result_file_path = process.stdout_path
            if result_file_path is not None:
                result = None
                with open(result_file_path, 'r') as result_file:
                    result = result_file.read().strip()
                exc_msg += 'result: {}\n'.format(result)

            raise Exception(exc_msg)

    def GetExtraCmdFiles(self):
        raise NotImplementedError()

    def GetGeodataOptionName(self):
        raise NotImplementedError()

    def FilesCmdPart(self):
        geodata_path = str(sdk2.ResourceData(sdk2.Resource.find(geo_resource.GEODATA6BIN_XURMA_STABLE, attrs={'released': 'stable'}).limit(1).first()).path)
        return [self.GetGeodataOptionName(), geodata_path] + self.GetExtraCmdFiles()

    def MakeErrorsHistogram(self, errors_file_path):
        raise NotImplementedError()

    def MakeTestCommand(self, *args):
        raise NotImplementedError()

    def GetSessionsDelimiter(self):
        return '\n'

    def GetErrorsDelimiter(self):
        raise NotImplementedError()

    def GetSkipsDelimiter(self):
        raise NotImplementedError()

    def RunTest(self, *args):
        raise NotImplementedError()

    def RunExtraTestsIfNeeded(self, input_path):
        return (False, True, None)

    def GetExtraTestsName(self):
        raise NotImplementedError()


class ScarabTester(BaseTester):
    def __init__(self, ctx, task):
        super(self.__class__, self).__init__(ctx, task)

    PRODUCTION_SERVER = 'veles02.search.yandex.net'

    def DoRsyncFromProductionServer(self, production_full_path, local_path_folder, file_name):
        cmd = ['rsync', 'rsync://' + self.PRODUCTION_SERVER + production_full_path, local_path_folder]
        self.RunProcess(cmd, log_prefix="rsync_{}".format(file_name))

    def CreateBinaryByYaMake(self):
        with self.task.memoize_stage.create_ya_make_children:
            binary_spec = REACTOR_BINARIES['create_scarab_sessions']
            build_from_svn_url = self.ctx.get(parameters.ArcadiaUrl.name)
            ctx = copy.deepcopy(self.ctx)
            ctx.update({
                # Support TemporaryError and task restart
                'checkout_arcadia_from_url': build_from_svn_url,
                'targets': binary_spec.target,
                'arts': binary_spec.resource_type.arcadia_build_path,
                'result_rt': str(binary_spec.resource_type),
                'build_system': 'semi_distbuild',
                'build_type': 'debug',
                'check_return_code': True,
                'result_single_file': True,
                consts.STRIP_BINARIES: False,
                'do_not_restart': False,
                'fail_on_any_error': False,
                'result_ttl': '10',
                'build_output_ttl': 1,
                'build_output_html_ttl': 1,
                'allure_report_ttl': 1,
                'max_restarts': 2,  # SDK2 compatibility
                'kill_timeout': 28800,  # 8h
            })

            subtask = self.task.create_subtask(
                'YA_MAKE',
                'Building %s binary' % binary_spec.name,
                input_parameters=ctx,
            )
            self.task.ctx['ya_make_subtask_id'] = str(subtask.id)
            self.task.wait_tasks(
                tasks=subtask,
                statuses=[ctt.Status.Group.FINISH, ctt.Status.Group.BREAK],
                wait_all=True
            )
        subtask_id = self.task.ctx['ya_make_subtask_id']
        return self.task.sync_resource(get_task_resource_id(subtask_id, 'CREATE_SCARAB_SESSIONS_EXECUTABLE'))

    def GetTestBinaryPath(self):
        if self.ctx['make_bin_by_ya_make']:
            return self.CreateBinaryByYaMake()
        else:
            production_path_folder = "/Berkanavt/sessions/bin"
            bin_name = "create_scarab_sessions"
            production_full_path = pj(production_path_folder, bin_name)
            local_path_folder = pj(self.task.abs_path(), production_path_folder.lstrip('/'))
            local_full_path = pj(local_path_folder, bin_name)
            make_folder(local_path_folder)
            self.DoRsyncFromProductionServer(production_full_path, local_path_folder, bin_name)
            return local_full_path

    def GetExtraCmdFiles(self):
        return []

    def GetGeodataOptionName(self):
        return '--geodata'

    def MakeErrorsHistogram(self, errors_file_path):
        histogram = defaultdict(int)

        for error_rec in ReadRecords(errors_file_path, self.GetErrorsDelimiter()):
            rec_splitted = error_rec.split('\t')
            if len(rec_splitted) >= 3:
                diagnosis = rec_splitted[1]

                histogram[diagnosis] += 1

        return histogram

    def GetErrorsDelimiter(self):
        return '\n'

    def GetSkipsDelimiter(self):
        return '\n'

    def MakeTestCommand(self, tester_path, input_path, external_users_sessions, internal_servers_sessions, staff_users_sessions, errors, skips):
        cmd = [tester_path, '-i', input_path, '--external-users', external_users_sessions, '--internal-servers', internal_servers_sessions,
                '--staff-users', staff_users_sessions, '--errors', errors, '--skips', skips, '--local']

        if self.ctx['log_by_columns']:
            cmd.append('--log-by-columns')

        cmd.extend(self.FilesCmdPart())

        return cmd

    def RunTest(self, tester_path, input_path):
        external_users_sessions, internal_servers_sessions, staff_users_sessions, errors, skips = \
            'external_users_sessions.txt', 'internal_servers_sessions.txt', 'staff_users_sessions.txt', 'errors.txt', 'skips.txt'

        self.RunProcess(self.MakeTestCommand(tester_path, input_path, external_users_sessions, internal_servers_sessions, staff_users_sessions,
                                             errors, skips), log_prefix="run_scarab")

        return [external_users_sessions, internal_servers_sessions, staff_users_sessions], errors, skips


class OldTester(BaseTester):
    def __init__(self, ctx, task):
        super(OldTester, self).__init__(ctx, task)

    def GetTestBinaryPath(self):
        tester_resource = sdk2.Resource.find(resources.REPORT_LOGS_TESTS_EXECUTABLE, attrs={'released': 'stable'}).limit(1).first()
        logging.info('tester resource: ' + str(tester_resource.id))
        return str(sdk2.ResourceData(tester_resource).path)

    def GetExtraCmdFiles(self):
        blockstat_path = str(sdk2.ResourceData(sdk2.Resource.find(resources.SESSIONS_BLOCKSTAT, attrs={'released': 'stable'}).limit(1).first()).path)
        beta_list_path = str(sdk2.ResourceData(sdk2.Resource.find(resources.SESSIONS_BETA_LIST, attrs={'released': 'stable'}).limit(1).first()).path)

        return ['--blockstat', blockstat_path, '--beta_list', beta_list_path]

    def GetGeodataOptionName(self):
        return '--geodata'

    def MakeErrorsHistogram(self, errors_file_path):
        histogram = defaultdict(int)

        for error_rec in ReadRecords(errors_file_path, self.GetErrorsDelimiter()):
            rec_splitted = error_rec.split(':')
            if len(rec_splitted) >= 3:
                diagnosis = rec_splitted[2]

                histogram[diagnosis] += 1

        return histogram

    def GetErrorsDelimiter(self):
        return '\n\n'

    def GetSkipsDelimiter(self):
        return '\n\n'

    def MakeTestCommand(self, tester_path, input_path, sessions, errors, skips):
        return [tester_path, '--log_type', self.ctx['log_name'], '--src', input_path, '--sessions', sessions, '--errors', errors, '--skips', skips] + self.FilesCmdPart()

    def RunTest(self, tester_path, input_path):
        sessions, errors, skips = 'sessions.txt', 'errors.txt', 'skips.txt'

        self.RunProcess(self.MakeTestCommand(tester_path, input_path, sessions, errors, skips), log_prefix="run_old")

        return [sessions], errors, skips


class BlockstatTester(OldTester):
    def __init__(self, ctx, task):
        super(self.__class__, self).__init__(ctx, task)

    def GetBaobabValidatorBinaryPath(self):
        tester_resource = sdk2.Resource.find(resources.BAOBAB_VALIDATOR_EXECUTABLE, attrs={'released': 'stable'}).limit(1).first()
        logging.info('baobab validator resource: ' + str(tester_resource.id))
        return str(sdk2.ResourceData(tester_resource).path)

    def MakeBaobabValidatorCommand(self, tester_path, input_path, result_file):
        return [tester_path,  input_path, result_file]

    def RunExtraTestsIfNeeded(self, input_path):
        return (False, True, None)

    def GetExtraTestsName(self):
        return 'baobab_validator'


class ReportLogsTester(SandboxTask):
    type = "TEST_REPORT_LOGS"

    input_parameters = [LogName, InputData, IsLogByColumns, MakeBin, parameters.ArcadiaUrl]

    def __init__(self, *args, **kwargs):
        SandboxTask.__init__(self, *args, **kwargs)
        self.env = dict(os.environ)

    def StoreHistogram(self, errors_histogram):
        result_filename = 'errors_histogram.txt'

        str_hist = '\n'.join('{}: {}'.format(k, v) for k, v in errors_histogram.items())

        with open(result_filename, 'w') as f:
            f.write(str_hist)

        return result_filename

    def MakeResultResources(self, *args):
        for arg in args:
            name = os.path.basename(arg)
            status = ctt.Status.SUCCESS if self.IsSuccessful() else ctt.Status.FAILURE

            resource = self.create_resource(
                name, arg, sdk2.service_resources.TestTaskResource,
                attributes={'status': status, 'type': name},
            )
            self.ctx['test_task_resources'].append(resource.id)

    def MakeExtraTestsResultResources(self, result_file):
        name = os.path.basename(result_file)
        status = ctt.Status.SUCCESS if self.IsSuccessful() else ctt.Status.FAILURE

        resource = self.create_resource(
            name, result_file, sdk2.service_resources.TestTaskResource,
            attributes={'status': status, 'type': name},
        )
        self.ctx['test_task_resources'].append(resource.id)

    def IsSuccessful(self):
        if 'result_stats' in self.ctx and 'errors_count' in self.ctx['result_stats']:
            success = self.ctx['result_stats']['errors_count'] == 0

            return success

        return None

    def RenderTestResult(self):
        is_successful = self.IsSuccessful()

        if is_successful is True:
            return '<br/><b><div style="color: #009f00">SUCCESS</div></b>'
        elif is_successful is False:
            return '<br/><b><div style="color: #9f0000">ERROR</div></b>'
        else:
            return ''

    @property
    def footer(self):
        if 'result_stats' in self.ctx:
            content = '<b>Test result: {},{} Errors: {}, Skips: {}</b>'.format(self.ctx['result_stats']['test_result'],
                                                                                 self.ctx['sessions_info_for_footer'],
                                                                                 self.ctx['result_stats']['errors_count'],
                                                                                 self.ctx['result_stats']['skips_count'])

            if 'extra_test_result_stats' in self.ctx:
                content += ', <b>{}: {}, look at resource if needed</b>'.format(self.ctx['extra_test_result_stats']['test_type'], self.ctx['extra_test_result_stats']['test_result'])

            content += self.RenderTestResult()

            return [{
                'helperName': '',
                'content': content,
            }]

    def GetTester(self):
        if self.ctx[LogName.name] == SCARAB_LOG:
            return ScarabTester(self.ctx, self)
        elif self.ctx[LogName.name] == 'blockstat_log':
            return BlockstatTester(self.ctx, self)
        else:
            return OldTester(self.ctx, self)

    def FillResultStatsContextField(self, is_success, sessions_table_to_sessions_count, errors_count, skips_count):
        self.ctx['result_stats'] = {
            'test_result': 'OK' if is_success else 'FAILED',
            'errors_count': errors_count,
            'skips_count': skips_count,
        }
        self.ctx['sessions_info_for_footer'] = ''
        for sess_table, sess_count in sessions_table_to_sessions_count.iteritems():
            sess_type = sess_table.rstrip('.txt')
            self.ctx['result_stats']['{}_count'.format(sess_type)] = sess_count
            self.ctx['sessions_info_for_footer'] += ' {}: {},'.format(sess_type, sess_count)

    def FillExtraTestsStatsContextField(self, tester, extra_tests_success, result_file):
        self.ctx['extra_test_result_stats'] = {
            'test_type': tester.GetExtraTestsName(),
            'test_result': 'OK' if extra_tests_success else 'FAILED',
        }
        # self.ctx['baobab_validator_info_for_footer'] = ''
        # for sess_table, sess_count in sessions_table_to_sessions_count.iteritems():
        #    sess_type = sess_table.rstrip('.txt')
        #    self.ctx['result_stats']['{}_count'.format(sess_type)] = sess_count
        #    self.ctx['sessions_info_for_footer'] += ' {}: {},'.format(sess_type, sess_count)

    def on_execute(self):
        self.ctx['test_task_resources'] = []
        input_path = self.sync_resource(self.ctx['input_data'])

        tester = self.GetTester()
        tester_path = tester.GetTestBinaryPath()

        logging.info('tester path: ' + tester_path)

        sessions_tables, errors_table, skips_table = tester.RunTest(tester_path, input_path)
        errors_histogram = tester.MakeErrorsHistogram(errors_table)

        histogram_filename = self.StoreHistogram(errors_histogram)

        sessions_table_to_sessions_count = {}
        for sessions_table in sessions_tables:
            sessions_table_to_sessions_count[sessions_table] = CountNonemptyRecords(sessions_table, tester.GetSessionsDelimiter())
        errors_count = CountNonemptyRecords(errors_table, tester.GetErrorsDelimiter())
        skips_count = CountNonemptyRecords(skips_table, tester.GetSkipsDelimiter())

        was_needed, extra_tests_success, result_file = tester.RunExtraTestsIfNeeded(input_path)

        is_success = (errors_count == 0)

        self.FillResultStatsContextField(is_success, sessions_table_to_sessions_count, errors_count, skips_count)

        if was_needed:
            self.FillExtraTestsStatsContextField(tester, extra_tests_success, result_file)
            self.MakeExtraTestsResultResources(result_file)

        self.MakeResultResources(errors_table, skips_table, histogram_filename, *sessions_tables)

        final_message = ''
        if errors_count != 0:
            final_message += "There are {} errors.".format(errors_count)
        if not extra_tests_success:
            final_message += "\n And, besides, {} found errors".format(self.ctx['extra_test_result_stats']['test_type'])

        eh.ensure(is_success, final_message)


__Task__ = ReportLogsTester
