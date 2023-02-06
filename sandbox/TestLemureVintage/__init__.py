import os
import re
import logging

from sandbox.projects import resource_types
from sandbox.sandboxsdk.task import SandboxTask
from sandbox.sandboxsdk.svn import Arcadia
from sandbox.sandboxsdk.paths import make_folder, remove_path
from sandbox.sandboxsdk import process
from sandbox.sandboxsdk.channel import channel
from sandbox.sandboxsdk.parameters import SandboxArcadiaUrlParameter, SandboxBoolParameter, ResourceSelector


class TestLemurVintage(SandboxTask):
    type = 'TEST_LEMUR_VINTAGE'
    arcadia_checkout_dir = "arcadia"
    ya_make_file = os.path.join(arcadia_checkout_dir, "robot/lemur/ci_yt/diff/ya.make")
    execution_space = 85 * 1024  # 85 Gb
    sb_token = "AQAD-qJSJkYDAAACBkoF1RNnMU3aiknshzMVYF8"

    class ArcadiaRootUrl(SandboxArcadiaUrlParameter):
        name = 'arcadia_root_url'
        default_value = Arcadia.trunk_url()
        description = 'Arcadia svn url:'

    class CanonizeTest(SandboxBoolParameter):
        name = 'canonize_test'
        default_value = False
        description = 'Canonize test'

    class DebugBuild(SandboxBoolParameter):
        name = 'debug_build'
        default_value = False
        description = 'Debug build (release by default)'

    class InputDataRes(ResourceSelector):
        name = 'input_data_res'
        description = 'Test input data (leave it blank to use data from test ya.make)'
        resource_type = resource_types.LEMUR_VINTAGE_MAP_TEST_DATA

    class UpdateInputData(SandboxBoolParameter):
        name = 'update_input_data'
        description = 'Update input data'
        default_value = False

    input_parameters = [ArcadiaRootUrl, CanonizeTest, DebugBuild, InputDataRes, UpdateInputData]

    def print_ctx(self):
        logging.debug("CTX:")
        for i in self.ctx:
            logging.debug("{}: {}".format(i, self.ctx[i]))

    def get_revision(self):
        url_split = self.ctx['arcadia_root_url'].split('@')
        revision = "HEAD"

        if len(url_split) > 1:
            revision = url_split[1]

        return revision

    def change_test_data(self):
        new_lines = []
        ya_make_file = os.path.join(self.path(), self.ya_make_file)
        logging.debug("YA MAKE FILE:{}".format(ya_make_file))
        with open(ya_make_file) as f:
            lines = f.readlines()
            for l in lines:
                match = re.search(r'sbr:\/\/(\d+)', l)
                if match:
                    res_id = match.group(1)
                    if channel.sandbox.get_resource(res_id).type == resource_types.LEMUR_VINTAGE_MAP_TEST_DATA:
                        l = l.replace(res_id, str(self.ctx['input_data_res']))
                new_lines.append(l)

        remove_path(ya_make_file)
        with open(ya_make_file, 'w') as f:
            for l in new_lines:
                f.write(l)

    def on_execute(self):
        ya_test_name = "test_vintage_map"
        self.ctx['arcadia_path'] = Arcadia.checkout(self.ctx['arcadia_root_url'], self.arcadia_checkout_dir, revision=self.get_revision())
        if self.ctx['input_data_res']:
            logging.debug("Test will be run with data from: #{}".format(self.ctx['input_data_res']))
            self.change_test_data()

        self.ctx['ya'] = "{}/ya".format(self.ctx['arcadia_path'])
        self.ctx['test_path'] = "{}/robot/lemur/ci_yt/diff".format(self.ctx['arcadia_path'])
        self.ctx['test_output'] = "test_output"
        make_folder(self.ctx['test_output'])
        self.print_ctx()
        cmd = [self.ctx['ya'], 'make', '-t', '-A', '-F', ya_test_name, '-v', '-C',
               self.ctx['test_path'], '--output', self.ctx['test_output']]

        if not self.ctx['debug_build']:
            cmd.append('-r')

        if self.ctx['canonize_test']:
            cmd.extend(['-Z', '--token', self.sb_token])

        test_process = process.run_process(cmd, check=True, log_prefix=ya_test_name, outputs_to_one_file=True, wait=True)

        logging.debug("Ya make return code: {}".format(test_process.returncode))
        self.ctx['resource_dir'] = (
            "{0}/{1}/{2}/{3}/{4}/"
            "{5}/test-results/"
            "{1}-{2}-{3}-{4}-{5}/testing_out_stuff/"
            "{6}.py.{6}/"
            "test_out"
        ).format(self.ctx['test_output'], "yweb", "robot", "lemur", "ci_yt", "diff", ya_test_name)

        logging.debug("UPDATE INPUT DATA flag: {}".format(self.ctx['update_input_data']))
        if not test_process.returncode and self.ctx['update_input_data']:
            logging.debug("Commiting changes in '{}'".format(self.ya_make_file))
            Arcadia.update(os.path.dirname(self.ya_make_file))
            Arcadia.commit(self.ya_make_file, "Test data update with resource #{}".format(self.ctx['input_data_res']), 'zomb-sandbox-rw')

        out_resource = self.create_resource(
            description="{} Task:#{} Revision:{}".format(self.type, self.id, self.get_revision()),
            resource_path=self.ctx['resource_dir'],
            resource_type=resource_types.TEST_LEMUR_VINTAGE_OUT,
        )

        self.mark_resource_ready(out_resource.id)


__Task__ = TestLemurVintage
