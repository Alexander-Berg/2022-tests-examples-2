# -*- coding: utf-8 -*-

import os
import os.path
import logging

from sandbox import sdk2

from sandbox.common.types import resource as ctr
from sandbox.projects import resource_types
from sandbox.sandboxsdk.environments import PipEnvironment
import sandbox.sandboxsdk.paths as sdk_paths

from sandbox.projects.images.CvdupAcceptanceTasks import common_functions

class TestCvdupCleanCache(sdk2.Task):

    class Requirements(sdk2.Task.Requirements):
        environments = (
            PipEnvironment('yandex-yt'),
            PipEnvironment('startrek_client', custom_parameters=["requests==2.18.4"], use_wheel=True)
        )

    class Parameters(sdk2.task.Parameters):
        kill_timeout = 24 * 3600
        mr_cluster = sdk2.parameters.String('MR cluster where all jobs will work', required=True, default='arnold.yt.yandex.net')
        mr_path = sdk2.parameters.String('MR path with data to clean', required=True)
        num_binaries = sdk2.parameters.Integer('Max number of binaries to keep data for them', required=True, default=10)
        branch_number_for_tag = sdk2.parameters.String('Release machine integration parameter (leave empty when launching not from rm images_semidups)', required=False)

    def on_execute(self):

        from yt.wrapper import YtClient, ypath_join, ypath_split

        self.startrack_api_token = sdk2.Vault.data('robot-cvdup', 'st_token')
        self.ticket_id = common_functions.find_ticket_by_branch(self.startrack_api_token, self.Parameters.branch_number_for_tag)
        common_functions.log_task_begin_in_ticket(self.startrack_api_token, self.ticket_id, self)

        stable_id = int(sdk2.Resource.find(type=resource_types.CVDUP_IMAGEREDUCE, state=ctr.State.READY, attrs=dict(released="stable")).first().id)

        logging.info("Stable id for CVDUP_IMAGEREDUCE resource " + str(stable_id))

        yt_client = YtClient(proxy=self.Parameters.mr_cluster, token=sdk2.Vault.data('robot-cvdup', 'yt_token'))
        paths = yt_client.list(self.Parameters.mr_path, absolute=False)

        id_set = set()
        try:
            for p in paths :
                id = int(p.split("_")[0])
                id_set.add(id)
        except ValueError as ex:
            logging.error("Incorrect cache folder.")
            raise
        logging.info("Found " + str(len(id_set)) + " ids in the cache " + self.Parameters.mr_path)

        if stable_id in id_set:
            id_set.remove(stable_id)

        if len(id_set) > self.Parameters.num_binaries:
            num_elements_to_delete = len(id_set) - self.Parameters.num_binaries
            ids_to_remove = sorted(list(id_set))[0:num_elements_to_delete]
        else:
            ids_to_remove = []

        logging.info("Selected " + str(len(ids_to_remove)) + " ids to remove")
        for p in paths :
            if int(p.split("_")[0]) in ids_to_remove :
                logging.info("Removing cache " + ypath_join(self.Parameters.mr_path, p))
                yt_client.remove(ypath_join(self.Parameters.mr_path, p), recursive=True, force=True)

        logging.info("Finished succesfully...")


