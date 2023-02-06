import logging
import os
import shutil
import sys

import sandbox.sdk2.vcs.svn as sdk_svn
from sandbox import sdk2
from sandbox.projects.common import file_utils

from sandbox.projects.ab_testing.resource_types import RUN_ABT_RESOURCES


class PrepareBsFeatures(sdk2.Task):
    class Requirements(sdk2.Requirements):
        cores = 1
        ram = 16 * 1024
        disk_space = 20 * 1024

    class Parameters(sdk2.Parameters):
        kill_timeout = 10 * 60  # 10 minutes is enough
        description = 'Save actual bs features as resource'

    def on_execute(self):
        logging.info("PrepareBsFeatures execution started")

        # prepare save_custom_features module
        scripts_path = sdk_svn.Arcadia.get_arcadia_src_dir("arcadia:/arc/trunk/arcadia/quality/ab_testing/scripts")
        src_save_custom_features = os.path.join(scripts_path, "rem_processes/save_custom_features.py")
        dst_save_custom_features = os.path.join(scripts_path, "monitoring/save_custom_features.py")
        shutil.copy(src_save_custom_features, dst_save_custom_features)
        sys.path.append(scripts_path + "/monitoring/")
        import save_custom_features

        # generate features file
        result_file = 'features_bs.json'
        save_custom_features.read_and_save_custom_features_json('bs', result_file, '', need_load_all=True)

        # save features as resource
        logging.info('Create "{}" resource'.format(result_file))
        resource = RUN_ABT_RESOURCES(self, result_file, result_file)
        resource_data = sdk2.ResourceData(resource)
        resource_data.path.write_bytes(file_utils.read_file(result_file))
        resource_data.ready()

        logging.info("PrepareBsFeatures execution completed")
