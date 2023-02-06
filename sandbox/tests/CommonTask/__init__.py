import logging
import os
from os.path import join as pjoin

import sandbox.projects.resource_types as resource_types
import sandbox.sdk2 as sdk2

import sandbox.common.types.resource as ctr
from sandbox.projects.images.robot.tests.resources import ImagesTestlibOutput, ImagesTestlibBinOutput
from sandbox.projects.images.robot.tests.CommonResources import TestlibSbrIds
from sandbox.projects.samovar.SamovarTest.yt_runner import YTRunner
from sandbox.sandboxsdk.process import run_process
from sandbox.sandboxsdk.paths import make_folder, get_logs_folder


class TestlibCommonTask(sdk2.Task):
    """ Common task for TestLib. """
    # Redefine your uniqe test name w/o spaces
    test_name = 'Test'
    testenv_database_trunk = 'images-robot-trunk'

    yt_tables = []
    other_resources = []

    class Parameters(sdk2.Task.Parameters):
        UseLastBinary = sdk2.parameters.Bool('Use last binary archive', default=True)

        local_yt = sdk2.parameters.Resource('Local YT', resource_type=resource_types.YT_LOCAL, default_value=TestlibSbrIds.CommonResources.YtLocal, required=True)
        bin_package = sdk2.parameters.Resource('Resource with binaries', resource_type=resource_types.YA_PACKAGE, default_value=TestlibSbrIds.CommonResources.BinPackage, required=True)

        with sdk2.parameters.Output:
            output_resource = sdk2.parameters.Resource('Test output', resource_type=ImagesTestlibOutput)
            output_bin_resource = sdk2.parameters.Resource('Test bin output', resource_type=ImagesTestlibBinOutput)

        with sdk2.parameters.Group('Local YT parameters') as local_yt_params:
            node_count = sdk2.parameters.Integer('--node-count', required=False)
            node_chunk_store_quota = sdk2.parameters.Integer('--node-chunk-store-quota', required=False)

    def on_save(self):
        if self.Parameters.UseLastBinary:
            self.Requirements.tasks_resource = sdk2.service_resources.SandboxTasksBinary.find(
                attrs={'target': '/images/robot/tests/' + self.test_name}).first().id

    def _pre_setup(self):
        self.work_dir = os.getcwd()
        self.yt_local_dir = pjoin(self.work_dir, 'yt_client')
        self.cypress_dir = pjoin(self.work_dir, 'cypress_data')
        self.config_dir = pjoin(self.work_dir, 'config')
        self.dump_dir = pjoin(self.work_dir, 'dump_dir')
        self.dump_bin_dir = pjoin(self.work_dir, 'dump_bin_dir')
        self.sysconfig_dir = pjoin(self.work_dir, 'input_files')

        make_folder(self.yt_local_dir)
        make_folder(self.dump_dir)
        make_folder(self.dump_bin_dir)
        make_folder(self.cypress_dir)
        make_folder(self.config_dir)
        make_folder(self.sysconfig_dir)

        self.binary_dir = str(sdk2.ResourceData(self.Parameters.bin_package).path)

        self.log_dir = get_logs_folder()

        self.directories = {
            'binary_dir': self.binary_dir,
            'dump_dir': self.dump_dir,
            'dump_bin_dir': self.dump_bin_dir,
            'config_dir': self.config_dir,
            'sysconfig_dir': self.sysconfig_dir
        }

    def _merge_yt_tables(self):
        chmod_cmd = ['chmod', 'a+rw', '-R', self.cypress_dir]

        if hasattr(self, "yt_table_resources"):
            for resource in self.yt_table_resources:
                yt_table_path = str(sdk2.ResourceData(resource).path)
                run_process(['cp', '-r', yt_table_path, self.cypress_dir])
                run_process(chmod_cmd)

        if hasattr(self, "yt_table_bin_resources"):
            for resource in self.yt_table_bin_resources:
                src = pjoin(str(sdk2.ResourceData(resource).path), ".")
                dst = pjoin(self.cypress_dir, "tables_dir")
                run_process(['cp', '-r', src, dst])
                run_process(chmod_cmd)

        run_process(['du', '-a', self.cypress_dir])

    def _collect_all_resources(self):
        res_paths = []
        for resource in self.other_resources:
            res_paths.append(str(sdk2.ResourceData(resource).path))

        chmod_cmd = ['chmod', 'a+rw', '-R', self.work_dir]
        for path in res_paths:
            run_process(['cp', '-r', path, self.work_dir])
            run_process(chmod_cmd)

    def find_last_valid_resource(self, test_name):
        if hasattr(self.Context, "testenv_database"):
            last_in_same_testenv_db = sdk2.Resource.find(
                type=ImagesTestlibBinOutput,
                status=ctr.State.READY,
                attrs={
                    "parent_task_type": test_name,
                    "testenv_database": self.Context.testenv_database
                }
            ).first()

            if last_in_same_testenv_db:
                return last_in_same_testenv_db

            return sdk2.Resource.find(
                type=ImagesTestlibBinOutput,
                status=ctr.State.READY,
                attrs={
                    "parent_task_type": test_name,
                    "testenv_database": self.testenv_database_trunk
                }
            ).first()

    def add_resource(self, test_name, resource):
        if not hasattr(self, "yt_table_bin_resources"):
            self.yt_table_bin_resources = []

        if resource:
            self.yt_table_bin_resources.append(resource)
        else:
            output_resource = self.find_last_valid_resource(test_name)
            if output_resource:
                self.yt_table_bin_resources.append(output_resource)

    def _collect_results(self):
        out_resource_entries = os.listdir(self.dump_dir)
        if out_resource_entries:
            self.Parameters.output_resource = ImagesTestlibOutput(
                self,
                '{} output from task {}'.format(self.test_name if self.test_name else 'Test', self.id),
                self.dump_dir
            )

        out_bin_resource_entries = os.listdir(self.dump_bin_dir)
        if out_bin_resource_entries:
            self.Parameters.output_bin_resource = ImagesTestlibBinOutput(
                self,
                '{} bin output from task {}'.format(self.test_name if self.test_name else 'Test', self.id),
                self.dump_bin_dir
            )

            self.Parameters.output_bin_resource.parent_task = self.id
            self.Parameters.output_bin_resource.parent_task_type = self.type.name
            if hasattr(self.Context, "testenv_database"):
                self.Parameters.output_bin_resource.testenv_database = self.Context.testenv_database

    def _start_yt(self):
        self._merge_yt_tables()

        local_yt_resource_path = str(sdk2.ResourceData(self.Parameters.local_yt).path)
        extract_yt_cmd = ['tar', '-xf', local_yt_resource_path, '-C', self.yt_local_dir]
        run_process(extract_yt_cmd)
        self.yt_wrapper = pjoin(self.yt_local_dir, 'bin', 'yt_local')
        self.yt_bin = pjoin(self.yt_local_dir, 'bin', 'yt2')

        os.chdir(self.yt_local_dir)

        yt_local_params = []
        if self.Parameters.node_count:
            yt_local_params += ['--node-count', str(self.Parameters.node_count)]
        if self.Parameters.node_chunk_store_quota:
            yt_local_params += ['--node-chunk-store-quota', str(self.Parameters.node_chunk_store_quota)]

        self.yt_runner = YTRunner(self.yt_wrapper, self.yt_bin, self.log_dir)
        self.yt_runner.start(None, cypress_dir=pjoin(self.cypress_dir, 'tables_dir'), additional_params=yt_local_params)
        self.yt_proxy = '{}:{}'.format(self.yt_runner.get_proxy(), self.yt_runner.get_port())

        logging.debug('YT proxy: {}'.format(self.yt_proxy))

        self.yt_parameters = {
            'bin': self.yt_bin,
            'proxy': self.yt_proxy,
            'env': self.yt_runner.env
        }

        os.chdir(self.work_dir)

    def _stop_yt(self):
        os.chdir(self.yt_local_dir)

        self.yt_runner.stop()
        self.yt_runner.delete()

        os.chdir(self.work_dir)

    def _run_tests(self):
        self.test(self.yt_parameters, self.directories).run_tests()

    def _prepare(self):
        """Define yt_tables you want to merge and other resources here.

        self.yt_tables = [
            self.Parameters.yt_tables
        ]

        self.other_resources = [
            self.Parameters.config,
            self.Parameters.ini_file
        ]

        Also define your test class.

        from linkdb_test import Test
        self.test = Test
        """
        pass

    def on_execute(self):
        self._pre_setup()
        self._prepare()
        self._collect_all_resources()
        self._start_yt()
        self._run_tests()
        self._collect_results()
        self._stop_yt()
