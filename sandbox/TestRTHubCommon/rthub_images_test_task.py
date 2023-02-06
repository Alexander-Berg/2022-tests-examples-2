# coding: utf-8

from rthub_test_task import RTHubTestTask
from sandbox import sdk2
from sandbox.projects.rthub.resources import RthubImagesFullPackage
import os


class RTHubImagesTestTask(RTHubTestTask):

    class Parameters(RTHubTestTask.Parameters):

        rthub_pkg_build = sdk2.parameters.Resource(
            "RTHub package build to use in test",
            required=True,
            resource_type=RthubImagesFullPackage
        )

    def run_rthub(self, pkg_dir, cfg, test_data, output_dir):
        os.environ['KMP_DUPLICATE_LIB_OK'] = 'TRUE'
        os.environ['MDS_URL'] = "localhost:13000"
        RTHubTestTask.run_rthub(self, pkg_dir, cfg, test_data, output_dir)
