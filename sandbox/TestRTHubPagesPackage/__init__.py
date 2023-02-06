# coding: utf-8

from sandbox import sdk2
from sandbox.projects.rthub.TestRTHubCommon import RTHubTestTask
from sandbox.projects.rthub.resources import RthubPagesFullPackage
from os.path import join as pj


class TestRTHubPagesPackage(RTHubTestTask):

    class Parameters(RTHubTestTask.Parameters):

        rthub_pkg_build = sdk2.parameters.Resource(
            "RTHub package build to use in test",
            required=True,
            resource_type=RthubPagesFullPackage
        )

    def get_config_path(self, test_dir):
        return pj(test_dir, "conf/conf-production/pages.pb.txt")
