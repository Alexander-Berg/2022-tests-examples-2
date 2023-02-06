# coding: utf-8

from sandbox import sdk2
from sandbox.projects.rthub.resources import RthubSitemapsFullPackage
from sandbox.projects.rthub.TestRTHubCommon import RTHubTestTask
from os.path import join as pj


class TestRTHubSitemapsPackage(RTHubTestTask):

    class Parameters(RTHubTestTask.Parameters):
        rthub_pkg_build = sdk2.parameters.Resource(
            "RTHub package build to use in test",
            required=True,
            resource_type=RthubSitemapsFullPackage
        )

    def get_config_path(self, test_dir):
        return pj(test_dir, "conf/conf-production/sitemaps.pb.txt")
