# coding: utf-8
import logging
import os
from os.path import join as pj
import tarfile
import shutil
import subprocess
import re
import fileinput

from sandbox import sdk2
from sandbox import common
from sandbox.projects.common import link_builder as lb
from sandbox.projects.rthub.resources import RTHubTestData


class RTHubTestTask(sdk2.Task):

    class Parameters(sdk2.Task.Parameters):
        test_data = sdk2.parameters.Resource(
            "Data for test",
            required=True,
            resource_type=RTHubTestData
        )

    # overridable
    def get_config_path(self, pkg_dir):
        # return pj(test_dir, "conf/conf-production/pages.pb.txt")
        pass

    def patch_config(self, config, threads_limit):
        # Patch InstanceStateFilePath
        for line in fileinput.FileInput(config, inplace=True):
            line = re.sub('MultipleInstancesOnSingleHost:.*', '', line.rstrip())
            print line

        # Patch ExecutionTimeoutMillis
        for line in fileinput.FileInput(config, inplace=True):
            line = re.sub('^.*ExecutionTimeoutMillis:.*', '', line.rstrip())
            print line

        # Patch CpuOversubscription
        for line in fileinput.FileInput(config, inplace=True):
            line = re.sub('^.*CpuOversubscription:.*', '', line.rstrip())
            print line

        # Patch WorkerThreadsCount
        with open(config, 'r') as f:
            if 'WorkerThreadsCount:' in f.read():
                logging.info("WorkerThreadsCount is already set")
                return
        for line in fileinput.FileInput(config, inplace=True):
            line = re.sub('OutputInflightLimit {', 'WorkerThreadsCount: ' + str(threads_limit) + '\n    OutputInflightLimit {', line.rstrip())
            print line

    def run_rthub(self, pkg_dir, cfg, test_data, output_dir):
        os.environ['RTHUB_TEST_MODE'] = "true"
        logging.info("Running RTHub...")
        work_dir = os.getcwd()
        os.chdir(pkg_dir)
        rthub_bin = pj(pkg_dir, 'rthub')
        rthub_cmd = [
            rthub_bin,
            '--config', cfg,
            '--input-directory', test_data,
            '--output-directory', output_dir,
            '--workers-count', '1',
            '--use-binary-format',
        ]

        os.listdir(pkg_dir)
        os.listdir(test_data)

        with sdk2.helpers.ProcessLog(self, logger='rthub') as rl:
            logging.info("Running: {}".format(rthub_cmd))
            try:
                subprocess.check_call(
                    rthub_cmd,
                    stdout=rl.stdout,
                    stderr=subprocess.STDOUT
                )
            except subprocess.CalledProcessError:
                self.Context.test_run_success = False
                raise common.errors.TaskFailure("Test run failed. See rthub.out.log for details.")
            finally:
                os.chdir(work_dir)

            self.Context.test_run_success = True

    # overridable
    def on_package_unpacked(self, pkg_dir, test_dir):
        # Run processing in 16 "thread" by default
        config = pj(test_dir, "config.pb.txt")
        shutil.copy(self.get_config_path(pkg_dir), config)
        self.patch_config(config, 16)
        return config

    @staticmethod
    def unpack_resource(target_dir, resource):
        resource_data = sdk2.ResourceData(resource)
        resource_path = str(resource_data.path)
        logging.info("Unpacking archive...")
        with tarfile.open(resource_path) as archive:
            archive.extractall(target_dir)

    def unpack_test_data(self, test_dir):
        logging.info("RTHub test data resource: {}".format(self.Parameters.test_data.id))
        self.unpack_resource(test_dir, self.Parameters.test_data)

    def unpack_package(self, test_dir):
        logging.info("RTHub package resource: {}".format(self.Parameters.rthub_pkg_build.id))
        self.unpack_resource(test_dir, self.Parameters.rthub_pkg_build)
        logging.info("RTHub configs resource: {}".format(self.Parameters.rthub_configs_pkg.id))
        self.unpack_resource(test_dir, self.Parameters.rthub_configs_pkg)

    def collect_results(self, output_dir):
        out_res_entries = os.listdir(output_dir)
        if out_res_entries:
            out_resource = sdk2.Resource['RTHUB_TEST_OUTPUT'](
                self,
                "RTHub test output form task {}".format(self.id),
                output_dir
            )
            out_resource_data = sdk2.ResourceData(out_resource)
            out_resource_data.path.mkdir(0o755, parents=True, exist_ok=True)
            out_resource_data.ready()
            self.Context.test_results_res_id = out_resource.id

    def create_diff_tool_resource(self, pkg_path, test_dir):
        diff_tool_dir = pj(test_dir, 'diff_tool')
        os.mkdir(diff_tool_dir)
        diff_tool_bin = pj(pkg_path, 'tools/diff_tool')
        shutil.copy(diff_tool_bin, diff_tool_dir)
        protos_dir = pj(pkg_path, 'data/protos')
        shutil.copytree(protos_dir, pj(diff_tool_dir, 'data/protos'))
        target_config = pj(diff_tool_dir, "config.pb.txt")
        shutil.copy(self.get_config_path(pkg_path), target_config)
        diff_tool_res = sdk2.Resource['RTHUB_DIFF_TOOL'](
            self,
            "RTHub diff_tool form task {}".format(self.id),
            diff_tool_dir
        )
        diff_tool_res_data = sdk2.ResourceData(diff_tool_res)
        diff_tool_res_data.path.mkdir(0o755, parents=True, exist_ok=True)
        diff_tool_res_data.ready()

    def on_execute(self):
        logging.info("Prepare for test...")
        os.mkdir(pj(os.getcwd(), 'rthub_test'))
        test_dir = pj(os.getcwd(), 'rthub_test')
        os.mkdir(pj(test_dir, 'output'))
        output_dir = pj(test_dir, 'output')

        # Prepare test data
        self.unpack_test_data(test_dir)
        test_data_path = pj(test_dir, 'test_data')

        # Prepare package
        package_resource_data = sdk2.ResourceData(self.Parameters.rthub_pkg_build)
        logging.info("package_resource_data.path == {}".format(str(package_resource_data.path)))
        package_path = str(package_resource_data.path)
        os.chmod(package_path, 0755)
        patched_cfg = self.on_package_unpacked(package_path, test_dir)

        self.Context.test_pkg_res_id = self.Parameters.rthub_pkg_build.id
        self.run_rthub(package_path, patched_cfg, test_data_path, output_dir)

        self.collect_results(output_dir)
        self.create_diff_tool_resource(package_path, test_dir)

    @sdk2.header()
    def report_header(self):
        if self.Context.test_run_success:
            return "Tested RTHub package resource: " + lb.resource_link(self.Context.test_pkg_res_id)
        else:
            return ''
