# -*- coding: utf-8 -*-

import exceptions
import logging
import os
import os.path
import traceback

from sandbox import sdk2
import sandbox.common
from sandbox.common.errors import TaskFailure
from sandbox.common.types import resource as ctr

from sandbox.projects import resource_types
from sandbox.projects.release_machine.components import all as rmc
from sandbox.projects.release_machine.helpers.startrek_helper import STHelper

from sandbox.sandboxsdk import process
from sandbox.sandboxsdk.environments import PipEnvironment
import sandbox.sandboxsdk.paths as sdk_paths

from sandbox.projects.images.CvdupAcceptanceTasks import common_functions


class TestCvdupMergeStates(sdk2.Task):

    class Requirements(sdk2.Task.Requirements):
        ram = 16 * 1024
        disk_space = 32 * 1024
        environments = (
            PipEnvironment('yandex-yt'),
            PipEnvironment('startrek_client', use_wheel=True)
        )

    class Parameters(sdk2.task.Parameters):
        kill_timeout = 100 * 3600
        image_reducer_binary = sdk2.parameters.Resource('Image reducer binary (last released taken if empty)', required=False, resource_type = resource_types.CVDUP_IMAGEREDUCE)
        mr_cluster = sdk2.parameters.String('MR cluster where all jobs will work', required=True, default='arnold.yt.yandex.net')
        mr_path_1 = sdk2.parameters.String('Path on MR cluster for first state', required=True)
        mr_path_2 = sdk2.parameters.String('Path on MR cluster for second state (merging to this state)', required=True)
        state_id = sdk2.parameters.Integer('Result state id', required=True, default=2)
        mr_states_cache_path = sdk2.parameters.String('Path on MR cluster for semidups states cache', required=True, default='//home/cvdup/semidups/acceptance_states/cache_small_v7')
        timestamp = sdk2.parameters.String('Release machine integration parameter (leave empty when launching not from rm images_semidups)', required=False, default='')
        branch_number_for_tag = sdk2.parameters.String('Release machine integration parameter (leave empty when launching not from rm images_semidups)', required=False)


    def generate_merge_states_commands(self):
        commands = [
            '{imagereduce} convert2state --srv {mr_cluster} --target-state-prefix {state_path} --state-id {id}'.format(
                imagereduce=self.imagereduce_binary,
                mr_cluster=self.Parameters.mr_cluster,
                state_path=self.Parameters.mr_path_1,
                id=1
            ),
            '{imagereduce} simple-inc --srv {mr_cluster} --base-state-prefix {base} --target-state-prefix {inc} --state-id {id}'.format(
                imagereduce=self.imagereduce_binary,
                mr_cluster=self.Parameters.mr_cluster,
                base=self.Parameters.mr_path_1,
                inc=self.Parameters.mr_path_2,
                id=self.Parameters.state_id
            )
        ]
        return commands


    def on_execute(self):
        import yt.wrapper as yt
        from yt.wrapper.ypath import ypath_join

        self.startrack_api_token = sdk2.Vault.data('robot-cvdup', 'st_token')
        self.ticket_id = common_functions.find_ticket_by_branch(self.startrack_api_token, self.Parameters.branch_number_for_tag)
        common_functions.log_task_begin_in_ticket(self.startrack_api_token, self.ticket_id, self)

        env = dict(os.environ)

        env['MR_RUNTIME'] = 'YT'
        env['YT_USE_YAMR_STYLE_PREFIX'] = '1'
        env['YT_POOL'] = 'cvdup'
        env['YT_SPEC'] = '{"job_io": {"table_writer": {"max_row_weight": 67108864}}, "map_job_io": {"table_writer": {"max_row_weight": 67108864}}, "reduce_job_io": {"table_writer": {"max_row_weight": 67108864}}, "sort_job_io": {"table_writer": {"max_row_weight": 67108864}}, "partition_job_io": {"table_writer": {"max_row_weight": 67108864}}, "merge_job_io": {"table_writer": {"max_row_weight": 67108864}}}'
        env['YT_TOKEN'] = sdk2.Vault.data('robot-cvdup', 'yt_token')

        if self.Parameters.image_reducer_binary :
            self.imagereduce_resource = self.Parameters.image_reducer_binary
        else :
            self.imagereduce_resource = sdk2.Resource.find(type=resource_types.CVDUP_IMAGEREDUCE, state=ctr.State.READY, attrs=dict(released="stable")).first()

        self.imagereduce_id = self.imagereduce_resource.id
        self.imagereduce_binary = sdk2.ResourceData(self.imagereduce_resource).path

        stdout_path = os.path.join(sdk_paths.get_logs_folder(), 'stdout.log')
        stderr_path = os.path.join(sdk_paths.get_logs_folder(), 'stderr.log')
        stdout_file = open(stdout_path, 'wa')
        stderr_file = open(stderr_path, 'wa')

        yt_client = yt.YtClient(proxy=self.Parameters.mr_cluster, token=sdk2.Vault.data('robot-cvdup', 'yt_token'))

        if not yt_client.exists(self.Parameters.mr_path_1) :
            logging.error("Error! Node %s does not exists", self.Parameters.mr_path_1)
            return False

        if not yt_client.exists(self.Parameters.mr_path_2) :
            logging.error("Error! Node %s does not exists", self.Parameters.mr_path_2)
            return False

        state_path_in_cache = ypath_join(self.Parameters.mr_states_cache_path, str(self.imagereduce_id) + "_merged")

        if yt_client.exists(state_path_in_cache):
            yt_client.remove(self.Parameters.mr_path_2, recursive=True, force=True)
            yt_client.link(state_path_in_cache, self.Parameters.mr_path_2)
        else :
            for cmd in self.generate_merge_states_commands():
                logging.info("Start command %s", cmd)
                process.run_process(
                    [cmd], work_dir="./", timeout=100*3600, shell=True, check=True, stdout=stdout_file, stderr=stderr_file, environment=env
                )
            logging.info("Copying state to cache...")
            yt_client.copy(self.Parameters.mr_path_2, state_path_in_cache, force=True, recursive=True)

        logging.info("Finished succesfully...")


