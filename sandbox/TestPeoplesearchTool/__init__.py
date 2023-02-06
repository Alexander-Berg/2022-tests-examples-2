# -*- coding: utf-8 -*-
from contextlib import closing

import os
import sys
import tarfile
import traceback

from sandbox.projects import resource_types
from sandbox.sandboxsdk import paths
from sandbox.sandboxsdk.errors import SandboxTaskFailureError
from sandbox.sandboxsdk.process import run_process
from sandbox.sandboxsdk.channel import channel
from sandbox.sandboxsdk.svn import Arcadia
from sandbox.sandboxsdk.task import SandboxTask
from sandbox.sandboxsdk import parameters

import sandbox.common.types.client as ctc


SKYNET_PYTHON_DIR = '/skynet/python'
SITE_PACKAGES_DIR = 'lib/python2.7/site-packages'


class BranchSvnUrlParameter(parameters.SandboxArcadiaUrlParameter):
    name = 'branch_url'
    description = 'branch url'
    default_value = 'arcadia:/arc/trunk/'


class TestDataSvnPathParameter(parameters.SandboxStringParameter):
    name = 'test_data_path'
    description = 'testing data path (relative branch url)'
    default_value = ''


class BinariesResourceParameter(parameters.LastReleasedResource):
    name = 'tools_id'
    description = 'archive with peoplesearch binaries for test'
    resource_type = resource_types.PEOPLESEARCH_TOOLS_ARCHIVE
    required = False


class MapReduceBinariesResourceParameter(parameters.LastReleasedResource):
    name = 'mapreduce_tools_id'
    description = 'archive with mapreduce and mr_apps binaries for test'
    resource_type = resource_types.PEOPLESEARCH_TOOLS_ARCHIVE
    required = False


class ExternalBinariesResourceParameter(parameters.LastReleasedResource):
    name = 'ext_bins_id'
    description = 'archive with peoplesearch external binaries for test'
    resource_type = resource_types.PEOPLESEARCH_EXTERNAL_BINARIES


class TestingCmdParameter(parameters.SandboxStringParameter):
    description = 'cmd, that launches test'
    name = 'test_cmd'


class MRHomeParameter(parameters.SandboxStringParameter):
    description = 'path to data in mapreduce'
    name = 'mr_home'


class ExternalPacketsResourceParameter(parameters.LastReleasedResource):
    name = 'ext_packs_id'
    description = 'archive with external python packets for PPL'
    resource_type = resource_types.PEOPLESEARCH_EXTERNAL_PY_PACKS
    required = False


class SetupParameters(parameters.SandboxStringParameter):
    name = 'setup_parameters'
    description = 'run setup with this parameters'
    default_value = '--skip_suggest'


class SkipSetup(parameters.SandboxBoolParameter):
    name = 'skip_setup'
    description = 'skip any setupping'
    default_value = False


class TestPeoplesearchTool(SandboxTask):
    """
        запускает быстрое (без построение Social Users Environment) тестирвание отдельных
        вскриптов и бинарников для построения базы Peoplesearch
    """
    type = 'TEST_PEOPLESEARCH_TOOL'
    client_tags = ctc.Tag.LINUX_PRECISE

    input_parameters = [
        BranchSvnUrlParameter,
        BinariesResourceParameter, MapReduceBinariesResourceParameter, ExternalBinariesResourceParameter,
        TestingCmdParameter, TestDataSvnPathParameter,
        MRHomeParameter,
        ExternalPacketsResourceParameter,
        SetupParameters, SkipSetup,
    ]

    def on_enqueue(self):
        testing_data_path = self.ctx[TestDataSvnPathParameter.name]
        if testing_data_path.endswith('arcadia') or testing_data_path.endswith('arcadia_tests_data'):
            raise SandboxTaskFailureError('impossible svn path to data %s'
                                          % testing_data_path)
        if not self.ctx[TestingCmdParameter.name]:
            raise SandboxTaskFailureError('no cmd for testing given')

    def add_pythonpath(self, path):
        self.env['PYTHONPATH'] = self.env.get('PYTHONPATH', '') + ':' + path

    def on_execute(self):
        self.svn_branch_url_info = Arcadia.info(self.ctx[BranchSvnUrlParameter.name])

        self.peoplesearch_dir = self.abs_path('peoplesearch')
        self.mr_peoplesearch_home = self.ctx[MRHomeParameter.name] or 'peoplesearch/sandbox_test%s_%s' % (self.parent_id, self.id)
        self.logs_dir = self.log_path('other_logs')
        self.env = os.environ.copy()

        self.set_info('create local peoplesearch environment ...')
        self.create_local_peoplesearch_env()
        self.__get_external_py_packets()

        if self.ctx[TestDataSvnPathParameter.name]:
            self.test_data_dir = self.__checkout('data', self.ctx[TestDataSvnPathParameter.name])

        self.set_info('run test ...')
        try:
            test_cmd = self.ctx[TestingCmdParameter.name].format(self=self).split(' ')
        except AttributeError as err:
            raise SandboxTaskFailureError('cannot launch test, due to invalid cmd: %s' % err)
        run_process(test_cmd, log_prefix='test', environment=self.env, timeout=7000)

    def __get_external_py_packets(self):
        external_packets_dir = self.extract_from_archive(
            self.ctx[ExternalPacketsResourceParameter.name], 'external_pypacks')
        if external_packets_dir:
            self.add_pythonpath(external_packets_dir)

    def check_mr_server(self):
        if self.ctx[MapReduceBinariesResourceParameter.name]:
            self.mapreduce_bin = self.extract_from_archive(self.ctx[MapReduceBinariesResourceParameter.name], 'mapreduce_bin')
            self.env['PATH'] += ':' + self.mapreduce_bin
            mapreduce_binary = os.path.join(self.mapreduce_bin, 'mapreduce')
            mr_check = run_process(
                [
                    mapreduce_binary, '-list', '-prefix', 'peoplesearch/some_empty/table/',
                    '--server', self.mr_server,
                    '-opt', 'user=%s' % self.mr_user
                ],
                log_prefix='mr_server_check', check=False
            )
            if mr_check.returncode == 1:
                raise SandboxTaskFailureError('cannot operate with mapreduce on this host with this binary')
            assert mr_check.returncode == 0, \
                'mr server %s is not accessible, due to %s, restart later' % (self.mr_server, mr_check.returncode)
        else:
            self.mapreduce_bin = None

    def create_local_peoplesearch_env(self):
        self.create_configs()
        self.check_mr_server()
        if not self.ctx.get(SkipSetup.name, False):
            self.create_setup()
            self.run_setup()

    def create_configs(self):
        self.set_info('create configs ...')
        self.ppl_configs_source_dir = self.__checkout('ppl_configs', 'arcadia/yweb/peoplesearch/social_users/ppl_configs')
        self.ppl_configs_dir = self.abs_path('ppl_configs_active')

        generate_configs_dir = [
            sys.executable, os.path.join(self.ppl_configs_source_dir, 'read_ppl_configs.py'),
            '-s', os.path.join(self.ppl_configs_source_dir, 'ppl_configs_default'),
            '-d', self.ppl_configs_dir,
            '--peoplesearch_home', self.peoplesearch_dir,
            '--mr_peoplesearch_home', self.mr_peoplesearch_home,
            '--svn_ssh_branch', Arcadia.svn_url(self.svn_branch_url_info['url']),
            '--other_default', 'peoplesearch_var=' + self.log_path('ppl_var')]
        run_process(generate_configs_dir, log_prefix='ppl_configs_reload', environment=self.env)

        self.add_pythonpath(self.ppl_configs_source_dir)

        sys.path.insert(0, self.ppl_configs_source_dir)
        try:
            from config_parsers import PeoplesearchConfig
        except ImportError as err:
            raise SandboxTaskFailureError('cannot import config_parsers with sys.path="%s", due to %s' %
                                          (', '.join(sys.path), err))
        try:
            config = PeoplesearchConfig(self.ppl_configs_dir)
        except:
            raise SandboxTaskFailureError('fail to load PeoplesearchConfig, due to\n%s' %
                                          ''.join(traceback.format_exception(*sys.exc_info())))

        self.pylib_dir = config.DEFAULT.LOCAL.pylib
        self.mr_server = config.SHARED.MAPREDUCE.server
        self.mr_user = config.SHARED.MAPREDUCE.user

        self.social_users_bin = config.DEFAULT.LOCAL.social_users_bin
        self.social_users_dir = config.DEFAULT.LOCAL.social_users_home
        self.social_users_scripts_dir = config.DEFAULT.LOCAL.social_users_scripts

        self.crawler_bin = config.DEFAULT.LOCAL.crawler_bin
        self.crawler_dir = config.DEFAULT.LOCAL.crawler_home
        self.crawler_scripts_dir = config.DEFAULT.LOCAL.crawler_scripts

    def create_setup(self):
        self.set_info('create setup ...')
        self.setup_dir = self.__checkout('setup', 'arcadia/yweb/peoplesearch/social_users/setup')
        self.setup_script = os.path.join(self.setup_dir, 'setup.py')
        if not os.access(self.setup_script, os.X_OK):
            raise SandboxTaskFailureError('setup script %s is not executable' % self.setup_script)

    def run_setup(self):
        self.set_info('run setup ...')
        setup_parameters = self.ctx.get(SetupParameters.name, SetupParameters.default_value).split(' ')
        if '-r' not in setup_parameters and '--revision' not in setup_parameters:
            setup_parameters.extend(['-r', str(self.svn_branch_url_info['commit_revision'])])
        if '-c' not in setup_parameters and '--config' not in setup_parameters:
            setup_parameters.extend(['-c', self.ppl_configs_dir])
        setup_cmd = [sys.executable, self.setup_script] + setup_parameters

        skip_crawler = '-C' in setup_parameters or '--skip_crawler' in setup_parameters
        if not skip_crawler:
            self.env['PATH'] += ':' + self.crawler_bin
            self.crawler_tools_dir = self.__checkout('crawler_tools', 'arcadia/yweb/peoplesearch/social_users/crawler/tools')

        skip_social_users = '-U' in setup_parameters or '--skip_social_users' in setup_parameters
        skip_pylib = '-P' in setup_parameters or '--skip_pylib' in setup_parameters

        skip_peoplesearch = '-I' in setup_parameters or '--skip_peoplesearch' in setup_parameters
        if not skip_peoplesearch:
            self.peoplesearch_tools_dir = self.__checkout('peoplesearch_tools', 'arcadia/yweb/peoplesearch/tools')

        if not skip_social_users:
            self.social_users_tools_dir = self.__checkout('social_users_tools', 'arcadia/yweb/peoplesearch/social_users/tools')

        skip_suggest = '-S' in setup_parameters or '--skip_suggest' in setup_parameters
        if not skip_suggest:
            self.social_users_suggest_dir = self.__checkout('suggest_tools', 'arcadia/yweb/peoplesearch/tools/suggest')

        if not skip_pylib:
            self.add_pythonpath(self.pylib_dir)

        self.extract_from_archive(self.ctx.get(BinariesResourceParameter.name, None), self.social_users_bin)
        self.extract_from_archive(self.ctx[ExternalBinariesResourceParameter.name], self.social_users_bin)
        self.env['PATH'] += ':' + self.social_users_bin

        if not skip_crawler and self.crawler_bin != self.social_users_bin:
            self.extract_from_archive(self.ctx.get(BinariesResourceParameter.name, None), self.crawler_bin)
            self.extract_from_archive(self.ctx[ExternalBinariesResourceParameter.name], self.crawler_bin)
            self.env['PATH'] += ':' + self.crawler_bin

        run_process(setup_cmd, log_prefix='run_setup', environment=self.env)

    def extract_from_archive(self, resource_id, local_path):
        if resource_id:
            self.set_info('extract %s to %s ...' % (resource_id, local_path))
            local_path = os.path.join(self.peoplesearch_dir, local_path)
            self.sync_resource(resource_id)
            resource = channel.sandbox.get_resource(resource_id)
            try:
                with closing(tarfile.TarFile.gzopen(resource.path, mode='r')) as archive:
                    for member in archive.getmembers():
                        if member.isfile():
                            archive.extract(member, local_path)
            except Exception as err:
                raise SandboxTaskFailureError('fail to extract from archive: %s' % err)
            return local_path

    def __checkout(self, local_path, svn_path='', **kwgs):
        local_path = os.path.join(self.peoplesearch_dir, local_path)
        paths.make_folder(local_path)
        svn_url = os.path.join(self.svn_branch_url_info['url'], svn_path)
        self.set_info('checkout %s to %s ...' % (svn_url, local_path))
        Arcadia.checkout(svn_url, local_path, revision=self.svn_branch_url_info['commit_revision'], **kwgs)
        return local_path


__Task__ = TestPeoplesearchTool
