# -*- coding: utf-8 -*-
import json
import os
import os.path
import logging
import requests
import time

from sandbox.projects.cvdup import resource_types as resource_types_cvdup
from sandbox import sdk2
from sandbox.sandboxsdk import process
from sandbox.sandboxsdk.environments import PipEnvironment
import sandbox.sandboxsdk.paths as sdk_paths

from sandbox.projects.images.CvdupAcceptanceTasks import common_functions
from sandbox.projects.images.CvdupAcceptanceTasks import nirvana_functions

class TestCvdupTolokaEstimating(sdk2.Task):

    class Requirements(sdk2.Task.Requirements):
        ram = 16 * 1024
        disk_space = 32 * 1024
        environments = (
            PipEnvironment('yandex-yt'),
            PipEnvironment('startrek_client', use_wheel=True)
        )

    class Parameters(sdk2.task.Parameters):
        kill_timeout = 24 * 3600
        nirvana_api_host = sdk2.parameters.String('API host for Nirvana', required=False, default='https://nirvana.yandex-team.ru/api/public/v1')
        nirvana_workflow_id = sdk2.parameters.String('Nirvana workflow id to sent results in toloka', required=False, default='df80fb76-d9ef-42fb-8396-053b73155393')
        nirvana_workflow_instance_id = sdk2.parameters.String('Nirvana workflow instance id to clone', required=False, default='2df5b25f-d96d-4cf6-ade9-2988cd9bf04e')
        url_pairs_json = sdk2.parameters.Resource('Url pairs for semidups estimating', required=True, resource_type = resource_types_cvdup.CvdupAcceptanceImageUrlPairsJson)
        branch_number_for_tag = sdk2.parameters.String('Release machine integration parameter (leave empty when launching not from rm images_semidups)', required=False)

    def on_execute(self):
        self.startrack_api_token = sdk2.Vault.data('robot-cvdup', 'st_token')
        self.nirvana_token = sdk2.Vault.data('robot-cvdup', 'nirvana_token')
        self.ticket_id = common_functions.find_ticket_by_branch(self.startrack_api_token, self.Parameters.branch_number_for_tag)
        common_functions.log_task_begin_in_ticket(self.startrack_api_token, self.ticket_id, self)

        result_resource_data = sdk2.ResourceData(resource_types_cvdup.CvdupAcceptanceTolokaEstimatesJson(
            self, "Toloka semidups estimates for url pairs", "toloka_estimates.json", ttl=30
        ))

        result = nirvana_functions.CloneWorkflowInstance(self.nirvana_token, self.Parameters.nirvana_workflow_id, self.Parameters.nirvana_workflow_instance_id, self.Parameters.nirvana_api_host)
        self.new_instance_id = result['result']

        if not self.new_instance_id :
            raise Exception('Error while cloning Nirvana instance!')

        logging.info("Workflow {} instance {} cloned sucessfully, new instance id - {}".format(self.Parameters.nirvana_workflow_id, self.Parameters.nirvana_workflow_instance_id, self.new_instance_id))

        result = nirvana_functions.SetAllBlocksParameter(self.nirvana_token, self.Parameters.nirvana_workflow_id, self.new_instance_id, 'resource_id', str(self.Parameters.url_pairs_json.id), self.Parameters.nirvana_api_host)
        result = nirvana_functions.StartWorkflowInstance(self.nirvana_token, self.Parameters.nirvana_workflow_id, self.new_instance_id, self.Parameters.nirvana_api_host)

        common_functions.log_nirvana_instance_launch_in_ticket(self.startrack_api_token, self.ticket_id, self, self.Parameters.nirvana_workflow_id, self.new_instance_id)

        need_to_fail = False
        while True:
            time.sleep(60)
            try:
                progress = dict(nirvana_functions.GetExecutionState(self.nirvana_token, self.Parameters.nirvana_workflow_id, self.new_instance_id, self.Parameters.nirvana_api_host)['result'])
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

        storagePath = ''
        result = nirvana_functions.GetAllBlocksResults(self.nirvana_token, self.Parameters.nirvana_workflow_id, self.new_instance_id, self.Parameters.nirvana_api_host)['result']

        for res in result :
            if 'endpoint' in res['results'][0] :
                if res['results'][0]['endpoint'] != 'executionResult' :
                    continue
            if 'storagePath' in res['results'][0] :
                storagePath = res['results'][0]['storagePath']
                break

        if not storagePath :
            raise Exception('Error while extracting storagePath from Nirvana instance results!')

        headers = {'Authorization': 'OAuth ' + self.nirvana_token}
        r = requests.get(storagePath, headers=headers, verify=False, stream=True, timeout=60)
        if r.status_code != 200:
            raise Exception('Failed to load result ' + storagePath)
        with open("toloka_estimates.json", 'wb') as fd:
            for chunk in r.iter_content(1024):
                fd.write(chunk)

