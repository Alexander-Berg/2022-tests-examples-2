# coding: utf-8

from sandbox.projects.rthub.TestRTHubCommon import RTHubImagesTestTask
from os.path import join as pj


class TestRTHubImagesPackage(RTHubImagesTestTask):

    def get_config_path(self, test_dir):
        return pj(test_dir, "conf/conf-production/images.pb.txt")
