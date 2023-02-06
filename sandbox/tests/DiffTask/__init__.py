import os

import sandbox.sdk2 as sdk2
from sandbox.projects.images.robot.tests.resources import ImagesTestlibOutput
from sandbox.sdk2.helpers import subprocess as sp


class ImagesTestlibDiffOutput(sdk2.Resource):
    """ Testlib Diff task output """
    releasable = True


class ImagesTestlibDiffTask(sdk2.Task):
    """ Diff task for testlib output """

    class Parameters(sdk2.Parameters):
        old_revision_resource = sdk2.parameters.Resource('Old revision output', resource_type=ImagesTestlibOutput, required=True)
        new_revision_resource = sdk2.parameters.Resource('New revision output', resource_type=ImagesTestlibOutput, required=True)

        with sdk2.parameters.Output:
            diff_output = sdk2.parameters.Resource('Out diff', resource_type=ImagesTestlibDiffOutput)

    def on_execute(self):
        old_revision = str(sdk2.ResourceData(self.Parameters.old_revision_resource).path)
        new_revision = str(sdk2.ResourceData(self.Parameters.new_revision_resource).path)

        work_dir = os.getcwd()
        diff_out_file = os.path.join(work_dir, 'diff.out')
        diff_cmd = ['diff', '-rN', old_revision, new_revision, '>', diff_out_file]

        sp.Popen(' '.join(diff_cmd), shell=True).wait()

        resource_file_name = 'diff'
        self.Parameters.diff_output = ImagesTestlibDiffOutput(self, 'Diff output', resource_file_name, ttl=30)

        with open(diff_out_file) as f:
            if f.read():
                self.Context.has_diff = True
            else:
                self.Context.has_diff = False

        os.rename(diff_out_file, str(self.Parameters.diff_output.path))
