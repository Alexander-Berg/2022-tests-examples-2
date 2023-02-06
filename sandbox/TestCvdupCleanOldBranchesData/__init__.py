
# -*- coding: utf-8 -*-

import os
import os.path
import logging

from sandbox import sdk2

from sandbox.sandboxsdk.environments import PipEnvironment
import sandbox.sandboxsdk.paths as sdk_paths

from sandbox.projects.images.CvdupAcceptanceTasks import common_functions

class TestCvdupCleanOldBranchesData(sdk2.Task):

    class Requirements(sdk2.Task.Requirements):
        environments = (
            PipEnvironment('yandex-yt'),
            PipEnvironment('startrek_client', use_wheel=True)
        )

    class Parameters(sdk2.task.Parameters):
        kill_timeout = 24 * 3600
        mr_cluster = sdk2.parameters.String('MR cluster where all jobs will work', required=True, default='arnold.yt.yandex.net')
        mr_path = sdk2.parameters.String('MR path with data to clean', required=True)
        num_branches = sdk2.parameters.Integer('Max number of branches to keep data for them', required=True, default=10)
        branch_number_for_tag = sdk2.parameters.String('Release machine integration parameter (leave empty when launching not from rm images_semidups)', required=False)

    def on_execute(self):

        from yt.wrapper import YtClient, ypath_join, ypath_split

        self.startrack_api_token = sdk2.Vault.data('robot-cvdup', 'st_token')
        self.ticket_id = common_functions.find_ticket_by_branch(self.startrack_api_token, self.Parameters.branch_number_for_tag)
        common_functions.log_task_begin_in_ticket(self.startrack_api_token, self.ticket_id, self)

        yt_client = YtClient(proxy=self.Parameters.mr_cluster, token=sdk2.Vault.data('robot-cvdup', 'yt_token'))
        paths = yt_client.list(self.Parameters.mr_path, absolute=False)
        paths_filtered = [p for p in paths if p.startswith('launch_images-semidups-')]
        paths_to_sort = [ ( x, int(x.split("-")[2].split("_")[0]), x.split("-")[2].split("_")[1] + x.split("-")[3]) for x in paths_filtered ]
        paths_to_sort.sort(key=lambda x: (x[1], x[2]))

        if(len(paths_to_sort) > self.Parameters.num_branches) :
            num_elements_to_delete = len(paths_to_sort) - self.Parameters.num_branches
            paths_to_delete = paths_to_sort[0:num_elements_to_delete]
            for p in paths_to_delete :
                logging.info("Removing branch data " + ypath_join(self.Parameters.mr_path, p[0]))
                yt_client.remove(ypath_join(self.Parameters.mr_path, p[0]), recursive=True, force=True)

        logging.info("Finished succesfully...")


