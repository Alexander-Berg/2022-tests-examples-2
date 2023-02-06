# -*- coding: utf-8 -*-

import os
import os.path
import logging
import sys
import time

from sandbox import sdk2
from sandbox.sandboxsdk import process
from sandbox.sandboxsdk.environments import PipEnvironment
import sandbox.sandboxsdk.paths as sdk_paths

from sandbox.projects.images.CvdupAcceptanceTasks import common_functions
from sandbox.projects.images.CvdupAcceptanceTasks import nirvana_functions


class TestCvdupLoadTolokaEstimates(sdk2.Task):

    class Requirements(sdk2.Task.Requirements):
        environments = (
            PipEnvironment('yandex-yt'),
            PipEnvironment('startrek_client', use_wheel=True)
        )

    class Parameters(sdk2.task.Parameters):
        kill_timeout = 10 * 3600
        nirvana_api_host = sdk2.parameters.String('API host for Nirvana', required=False, default='https://nirvana.yandex-team.ru/api/public/v1')
        nirvana_workflow_id = sdk2.parameters.String('Nirvana workflow id to sent results in toloka', required=False, default='810f49b2-6c92-4342-85e1-fc7a4f404e67')
        nirvana_workflow_instance_id = sdk2.parameters.String('Nirvana workflow instance id to clone', required=False, default='1e5f2b16-b06a-42f1-86bc-7bc1503ba770')
        output_table_path = sdk2.parameters.String('Yt table to store results', required=True)
        branch_number_for_tag = sdk2.parameters.String('Release machine integration parameter (leave empty when launching not from rm images_semidups)', required=False)

    def on_execute(self):
        self.startrack_api_token = sdk2.Vault.data('robot-cvdup', 'st_token')
        self.nirvana_token = sdk2.Vault.data('robot-cvdup', 'nirvana_token')
        self.ticket_id = common_functions.find_ticket_by_branch(self.startrack_api_token, self.Parameters.branch_number_for_tag)
        common_functions.log_task_begin_in_ticket(self.startrack_api_token, self.ticket_id, self)

        result = nirvana_functions.CloneWorkflowInstance(self.nirvana_token, self.Parameters.nirvana_workflow_id, self.Parameters.nirvana_workflow_instance_id, self.Parameters.nirvana_api_host)
        self.new_instance_id = result['result']

        if not self.new_instance_id :
            raise Exception('Error while cloning Nirvana instance!')

        result = nirvana_functions.SetAllBlocksParameter(self.nirvana_token, self.Parameters.nirvana_workflow_id, self.new_instance_id, 'table', self.Parameters.output_table_path, self.Parameters.nirvana_api_host)
        result = nirvana_functions.StartWorkflowInstance(self.nirvana_token, self.Parameters.nirvana_workflow_id, self.new_instance_id, self.Parameters.nirvana_api_host)

        common_functions.log_nirvana_instance_launch_in_ticket(self.startrack_api_token, self.ticket_id, self, self.Parameters.nirvana_workflow_id, self.new_instance_id)

        need_to_fail = False
        while True:
            time.sleep(60)
            try:
                progress = dict(nirvana_functions.GetExecutionState(self.nirvana_token, self.Parameters.nirvana_workflow_id, self.new_instance_id)['result'])
                print progress
                if progress['status'] == 'completed':
                    if progress['result'] != 'success':
                        sys.stderr.write('Nirvana workflow has failed. Recreate it.\n')
                        need_to_fail = True
                    break
            except:
                logging.info('Failed to execute GetExecutionState')

        if need_to_fail:
            raise Exception('Error while executing Nirvana instance!')

