# -*- coding: utf-8 -*-

import os
import logging
import signal
import traceback
from datetime import datetime
import time

from sandbox.common.types.client import Tag

from sandbox.sandboxsdk.process import run_process, kill_process

from sandbox.sandboxsdk import parameters
from sandbox.sandboxsdk.paths import copy_path, remove_path, chmod, get_unique_file_name, make_folder
from sandbox.projects import resource_types
from sandbox.sandboxsdk.errors import SandboxTaskFailureError
from sandbox.projects.common.environments import ValgrindEnvironment, PipEnvironment
from sandbox.projects.TestRTYServerTask import TestRTYServerTask
from sandbox.projects.TestRTYServerTask import RtyInfrastructureRunner
from sandbox.sandboxsdk.channel import channel

from sandbox.projects.common import apihelpers


class TestRTYServerMulti(TestRTYServerTask, RtyInfrastructureRunner, object):
    class RtyserverMultitesterResourceId(parameters.ResourceSelector):
        name = 'rtyserver_multitester_resource_id'
        description = 'RTYServer multitester binary'
        resource_type = resource_types.RTYSERVER_MULTITESTER

    class SproxyResourceId(parameters.ResourceSelector):
        name = 'sproxy_resource_id'
        description = 'RTYServer SearchProxy'
        resource_type = resource_types.RTYSERVER_SEARCHPROXY

    class IproxyResourceId(parameters.ResourceSelector):
        name = 'iproxy_resource_id'
        description = 'RTYServer Indexer Proxy'
        resource_type = resource_types.RTYSERVER_INDEXER_PROXY

    class RtyemulatorResourceId(parameters.ResourceSelector):
        name = 'rtyemulator_resource_id'
        description = 'RTYServer Emulator'
        resource_type = resource_types.RTYSERVER_UTILS_RTYSERVER_EMULATOR

    class UnstableProcesses(parameters.SandboxBoolParameter):
        name = 'unstable_processes'
        default_value = False
        description = 'do not check processes after task'

    class RtyserverMultiScriptPath(parameters.ResourceSelector):
        name = 'rtyserver_multi_script_path'
        description = 'Scripts for multitester'
        resource_type = resource_types.RTYSERVER_MULTI_CONFIGS

    class RtyserverMultiScriptName(parameters.SandboxStringParameter):
        name = 'rtyserver_multi_script_name'
        description = 'Script name'

    class DelResources(parameters.SandboxBoolParameter):
        name = 'del_resources'
        default_value = False
        description = 'delete resources of choosen type'
        sub_fields = {'false': [], 'true': ['del_res_type', 'del_time']}

    class DelResType(parameters.SandboxStringParameter):
        name = 'del_res_type'
        description = 'type to delete'

    class DelTime(parameters.SandboxIntegerParameter):
        name = 'del_time'
        description = 'days to delete'

    class MscriptText(parameters.SandboxStringParameter):
        name = 'mscript_text'
        description = 'script text'
        multiline = True

    class RtyserverConfigsPath(parameters.SandboxStringParameter):
        name = 'rtyserver_configs_path'
        description = 'Remote configs path'

    class RtyserverScriptsPath(parameters.SandboxStringParameter):
        name = 'rtyserver_scripts_path'
        description = 'Remote scripts path'

    class Branch(parameters.SandboxStringParameter):
        name = 'branch'
        default_value = 'svn+ssh://arcadia.yandex.ru/arc/trunk'
        description = 'Branch (svn root path)'

    # --------------------------------------------------------------------------------
    class RtyserverResourceId(parameters.ResourceSelector):
        name = 'rtyserver_resource_id'
        description = 'RTYServer binary'
        resource_type = resource_types.RTYSERVER

    class RtyserverConfigsResourceId(parameters.ResourceSelector):
        name = 'rtyserver_configs_resource_id'
        description = 'Configs for tester'
        resource_type = resource_types.RTYSERVER_CONFIGS

    class TesterTimeout(parameters.SandboxIntegerParameter):
        name = 'tester_timeout'
        default_value = 1200
        description = 'timeout for test (sec)'

    class UseValgrind(parameters.SandboxBoolParameter):
        name = 'use_valgrind'
        default_value = False
        description = 'Use valgrind'

    class UsePerftools(parameters.SandboxBoolParameter):
        name = 'use_perftools'
        default_value = False
        description = 'Use gperftools'
        sub_fields = {'true': ['profile_rtyserver', 'gprof_frequency'], 'false': []}

    class ProfileRtyserver(parameters.SandboxBoolParameter):
        name = 'profile_rtyserver'
        default_value = False
        description = 'Do profiles for backend'

    class GprofFrequency(parameters.SandboxIntegerParameter):
        name = 'gprof_frequency'
        default_value = 100
        description = 'Gperftools frequency'

    class SystemStatAttr(parameters.SandboxStringParameter):
        name = 'system_stat_attr'
        description = 'Sys stat scripts attr'

    input_parameters = [
        RtyserverMultitesterResourceId, SproxyResourceId, IproxyResourceId, RtyemulatorResourceId,
        UnstableProcesses, RtyserverMultiScriptPath, RtyserverMultiScriptName,
        DelResources, DelResType, DelTime, MscriptText, RtyserverConfigsPath, RtyserverScriptsPath, Branch,
        # --------------------------------------------------------------------------------
        RtyserverResourceId, RtyserverConfigsResourceId, TesterTimeout, UseValgrind, UsePerftools,
        ProfileRtyserver, GprofFrequency, SystemStatAttr
    ]
    type = 'TEST_RTYSERVER_MULTI'
    client_tags = Tag.LINUX_PRECISE
    default_configs_path = 'arcadia/saas/rtyserver_test/func/configs'
    default_keys_path = 'arcadia_tests_data/rtyserver/test_data/keys'
    main_script = ''

    MTESTER_TIMEOUT = 1200

    @property
    def environment(self):
        environment = list(super(TestRTYServerMulti, self).environment)
        logging.info('env: %s' % environment)
        if self.ctx.get('use_valgrind', False):
            if environment:
                environment.append(ValgrindEnvironment())
            else:
                environment = [ValgrindEnvironment()]
        if self.ctx.get('system_stat_attr'):
            if environment:
                environment.append(PipEnvironment('matplotlib', '1.4', use_wheel=True))
            else:
                environment = [PipEnvironment('matplotlib', '1.4', use_wheel=True)]
        return environment

    def prepMultitester(self):
        """
        if multitester resource is valid run it
        :return: path to multitester binary
        """
        multitester_path = ''
        if self.ctx['rtyserver_multitester_resource_id']:
            self.sync_resource(self.ctx['rtyserver_multitester_resource_id'])
            multitester = channel.sandbox.get_resource(self.ctx['rtyserver_multitester_resource_id'])
            if multitester.arch != self.arch:
                raise SandboxTaskFailureError('Incorrect server resource #%s arch "%s" on host with arch "%s".'
                                              % (multitester.id, multitester.arch, self.arch))
            multitester_path = multitester.path

        return multitester_path

    def doPaths(self):
        self.log_path_ = self.log_path()
        self.abs_path_ = self.abs_path()
        self.config_dir = os.path.join(self.log_path(), 'configs')
        self.prof_tools_path = ''
        self.sys_metrics_path = ''
        self.scr_vars['CONF_PATH'] = self.config_dir
        self.scr_vars['SCRIPTS_PATH'] = self.log_path_
        self.scr_vars['ABS_PATH'] = self.abs_path_

        root_svn = self.ctx.get('branch', '')
        if root_svn == '':
            root_svn = self.default_root
        self.default_configs_path = os.path.join(root_svn, self.default_configs_path)
        self.default_keys_path = os.path.join(root_svn, self.default_keys_path)

    def prepConfigs(self):

        # check configs and scripts ids, if not selected, copy from remote path
        if not self.ctx.get('rtyserver_configs_resource_id', 0):
            downPath = self.ctx.get('rtyserver_configs_path', '')
            if downPath.strip() == '':
                downPath = self.default_configs_path
            conf_path = self.get_resource_to_task_dir(resource_types.RTYSERVER_CONFIGS, 'from_path', downPath)
            copy_path(conf_path, self.config_dir)
        else:
            default_config_dir = self.sync_resource(self.ctx['rtyserver_configs_resource_id'])
            if os.path.exists(self.config_dir):
                chmod(self.config_dir, 0o777)
                remove_path(self.config_dir)
            copy_path(default_config_dir, self.config_dir)
        chmod(self.config_dir, 0o777)
        os.chmod(self.config_dir, 0o777)
        mscr_id = self.ctx.get('rtyserver_multi_script_path', 0)
        if not mscr_id or not channel.sandbox.get_resource(mscr_id).is_ready():
            self.ctx['rtyserver_multi_script_path'] = 0
            downPath = self.ctx.get('rtyserver_scripts_path', '')
            if downPath == '':
                downPath = self.ctx.get('rtyserver_multi_scripts_path', '')
            if downPath.strip() == '':
                return
            m_res = self.resources.get_or_download_resource(self, resource_types.RTYSERVER_MULTI_CONFIGS,
                                                            'from_path', downPath,
                                                            os.path.join(self.abs_path_, 'multiscripts'))
            self.ctx['rtyserver_multi_script_path'] = m_res.id

    def clearResType(self, res_type, dtime):
        ntime = time.time()
        offs = 0
        lim = 500
        deleted_total = 0
        deleted = 0
        dsize = 0

        def allowed_rem(reso):
            return (reso.owner == 'RTYSERVER-ROBOT') \
                and not channel.sandbox.get_resource_attribute(reso.id, 'do_not_remove') \
                and channel.sandbox.get_resource_attribute(reso.id, 'ttl') != 'inf' \
                and '201' not in reso.description
        while True:
            ress = self.get_resources_list(res_type, lim, offs)
            if not ress or len(ress) == 0:
                break
            deleted_total += deleted
            deleted = 0
            for res in ress:
                reso = res
                rtime = reso.timestamp
                needs_rem = ((ntime - rtime) > dtime) and allowed_rem(reso)
                if res_type == 'TASK_LOGS' and needs_rem:
                    needs_rem = self.need_rem_log(reso)
                logging.info('resource %s, timestamp %s, needs removing %s' % (reso, rtime, needs_rem))
                if needs_rem:
                    sz = reso.size
                    rem_res = channel.sandbox.delete_resource(res.id, True)
                    logging.info('resource %s removing result %s' % (res, rem_res))
                    if rem_res:
                        deleted += 1
                        dsize += sz
            if len(ress) == 0:
                break
            if deleted == 0 and deleted_total > 10:
                break
            else:
                if res_type == 'TASK_LOGS':
                    offs += lim
                else:
                    offs += (len(ress) - deleted)
        self.set_info('deleted %s kb' % dsize)

    def need_rem_log(self, reso):
        logging.info('log size %s' % reso.size)
        return reso.size > 500000

    def get_resources_list(self, res_type, lim, offs):
        if res_type != 'TASK_LOGS':
            return channel.sandbox.list_resources(
                resource_type=res_type, status='READY',
                limit=lim, offset=offs,
                hidden=1, omit_failed=True)
        load_tasks = channel.sandbox.list_tasks(task_type='TEST_RTYSERVER_DOLBILOM',
                                                limit=lim, offset=offs, get_id_only=True)
        logs = []
        for ltask in load_tasks:
            tres = apihelpers.list_task_resources(ltask, 'TASK_LOGS')
            logs.extend(tres)
        return logs

    def clearRes(self):
        res_type = self.ctx.get('del_res_type', '')
        if res_type == '':
            res_types = ['RTYSERVER', 'RTYSERVER_SEARCHPROXY', 'RTYSERVER_INDEXER_PROXY',
                         'RTYSERVER_TEST', 'RTYSERVER_MULTITESTER']
        else:
            res_types = [res_type]

        dtime = self.ctx.get('del_time', 7) * 3600 * 24
        if dtime == 0:
            dtime = 7

        for rtype in res_types:
            if rtype not in channel.sandbox.list_resource_types():
                logging.info('%s not resource type' % rtype)
                continue
            self.clearResType(rtype, dtime)

        return

    def do_execute(self):
        if self.ctx.get('del_resources'):
            self.clearRes()
            return

        self.doPaths()
        self.prepConfigs()

        if self.ctx.get('use_perftools', False):
            self.prof_tools_path = self.get_resource_to_task_dir(resource_types.RTY_RELATED, 'type', 'google_perftools')
            os.environ['GPERFTOOLS_PATH'] = os.path.join(self.prof_tools_path, '.libs')
            os.environ['CONVERTER'] = os.path.join(self.prof_tools_path, 'src', 'pprof')
            os.environ['PROFILES_PATH'] = os.path.join(self.log_path_, 'PROFILES')

        if self.ctx.get('system_stat_attr', False):
            self.sys_metrics_path = self.get_resource_to_task_dir(resource_types.RTY_RELATED, 'type', self.ctx['system_stat_attr'])

        mscrs_path = get_unique_file_name(self.abs_path(), 'mscripts')
        if self.ctx['rtyserver_multi_script_path']:
            copy_path(self.sync_resource(self.ctx['rtyserver_multi_script_path']), mscrs_path)
        else:
            make_folder(mscrs_path)
        scr_file_name = os.path.join(mscrs_path, self.ctx.get('rtyserver_multi_script_name'))
        chmod(mscrs_path, 0o777)
        if not scr_file_name.endswith('.rtyts'):
            scr_file_name += '.rtyts'
        if self.ctx.get('mscript_text', '').strip():
            mscr_text = self.ctx['mscript_text'].replace('\r\n', '\n')
            with open(scr_file_name, 'w') as scr:
                scr.write(mscr_text)
        if not os.path.exists(scr_file_name):
            raise SandboxTaskFailureError('script file %s does not exist' % scr_file_name)

        try:
            self.main_script = self.Configure(scr_file_name)
        except Exception as e:
            logging.info(traceback.format_exc())
            raise e

        self.run_Test()

        self.ParseCustom(self.parse_files, self.scr_vars)
        self.SaveCustom(self.save_files, self.scr_vars)

    def on_execute(self):

        self.do_execute()

        self.set_info('Done')

    def run_Test(self):
        """
        runs a single test, writes results and time
        :return:
        """
        # if timeout
        def on_timeout(process):
            process.send_signal(signal.SIGABRT)
            for i in range(25):
                if process.poll():
                    break
                time.sleep(5)
            kill_process(process.pid)
            self.ctx['task_result_type'] = 'timeout'

        multitester_path = self.prepMultitester()
        self.run_profilers()

        try:
            start_time = datetime.now()
            self.ctx['start_rty_tests_time_stamp'] = str(start_time)

            os.chmod(multitester_path, 0o777)
            cmd = [multitester_path, self.main_script]

            log_prefix = 'test_%s_execution' % self.ctx.get('rtyserver_multi_script_name').replace('/', '_')
            if self.ctx.get('tester_timeout', 0):
                tout = self.ctx['tester_timeout']
            else:
                timeend = self.timestamp_start + self.ctx.get('kill_timeout', 18000) - 180
                tout = max(timeend - time.time(), self.MTESTER_TIMEOUT)
            try:
                run_process(cmd,
                            timeout=tout,
                            log_prefix=log_prefix,
                            on_timeout=on_timeout,
                            outputs_to_one_file=False)
            finally:
                self.process_memory_usage()
                if self.ctx.get('use_perftools'):
                    self.send_signal_prof()

            self.calcTime(start_time)
        finally:
            self.saveLogs()


__Task__ = TestRTYServerMulti
