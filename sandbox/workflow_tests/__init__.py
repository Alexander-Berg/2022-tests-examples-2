from __future__ import print_function as _print_function

import os
import re
import shutil
import logging
import tarfile
import tempfile
from io import BytesIO

import requests

from sandbox import sdk2
from sandbox.common import errors


class WorkflowCheckerBaseTask(sdk2.Task):

    _MIN_PING_INTERVAL_SECONDS = 5 * 60

    class Parameters(sdk2.Task.Parameters):
        description = "Basic task to check workflow successfull execution"
        base_workflow = sdk2.parameters.String("Test workflow base id", required=True)
        nirvana_token = sdk2.parameters.YavSecret("Nirvana Token", required=True)
        nirvana_token_key = sdk2.parameters.String("Nirvana Token Key", default='secret')
        workflow_ttl = sdk2.parameters.Integer("Test workflow ttl in seconds", default=60*60)
        workflow_name = sdk2.parameters.String("Test workflow name", default="Test worflow")
        local_params_update = sdk2.parameters.JSON("Test workflow local parameters update", default=[{}])
        global_params_update = sdk2.parameters.JSON("Test workflow global parameters update", default=[{}])

        with sdk2.parameters.Output():
            result = sdk2.parameters.String("Workflow check result")

        with sdk2.parameters.Output():
            workflow_id = sdk2.parameters.String("Testing Workflfow id")

    class Context(sdk2.Task.Context):
        test_workflow = None

    def _check_local_params(self, params):
        try:
            for param in params:
                _, _, _ = param['blockCode'], param['param'], param['value']
        except (TypeError, KeyError) as e:
            logging.error("Got illegal parameters: {}. {}".format(params, e))
            raise errors.TaskFailure("local_params_update must be a list, where each element is a dict,"
                                     "containing 'blockCode', 'param', 'value' keys")

    def _get_nirvana(self):
        from nirvana_api import NirvanaApi
        return NirvanaApi(self.Parameters.nirvana_token.data()["secret"])

    def update_test_workflow(self, workflow):
        from api_tools.set_parameters import set_local_params
        self._check_local_params(self.Parameters.local_params_update)
        local_params_to_update = self.Parameters.local_params_update
        if local_params_to_update:
            set_local_params(self._nirvana, workflow, None, local_params_to_update)
        if any(self.Parameters.global_params_update) > 0:
            assert False, "Not supported yet"

    @property
    def test_workflow_name(self):
        return self.Parameters.workflow_name

    def setup_test_workflow(self, base_workflow):
        return self._nirvana.clone_workflow(base_workflow, new_name=self.test_workflow_name)

    def on_execute(self):
        self._nirvana = self._get_nirvana()
        if self.Context.test_workflow is None:
            logging.info("Cloning base workflow: {}".format(self.Parameters.base_workflow))
            test_workflow = self.setup_test_workflow(self.Parameters.base_workflow)
            logging.info("Created test workflow: {}".format(test_workflow))
            self.update_test_workflow(test_workflow)
            self._nirvana.start_workflow(test_workflow)
            self.Context.test_workflow = test_workflow
        self.Parameters.workflow_id = test_workflow = self.Context.test_workflow

        state = self._nirvana.get_execution_state(workflow_id=test_workflow)
        if state['status'] != "completed":
            logging.info("\tProgress: {}".format(state["progress"]))
            raise sdk2.WaitTime(self._MIN_PING_INTERVAL_SECONDS)

        workflow_result = state.get("result", None)
        if workflow_result != 'success':
            raise errors.TaskFailure("Test workflow exited with non-success status {}".format(workflow_result))

        result = self.check_test_workflow(test_workflow)
        logging.info("Check result: ", result)
        self.Parameters.result = result

    def check_test_workflow(self, workflow):
        # Base checker only checks that the workflow exited with the success result
        # Implement your test logic in this method
        return 'success'


class WorkflowCheckBlockResult(WorkflowCheckerBaseTask):

    class Parameters(WorkflowCheckerBaseTask.Parameters):
        block_code = sdk2.parameters.String("Code of block that will be tested", required=True)
        block_output = sdk2.parameters.String("Block output that will be tested", required=True)

    def _get_block_results(self, workflow, block_code, output):
        from nirvana_api import BlockPattern
        block_results = self._nirvana.get_block_results(workflow, BlockPattern(code=block_code), [output])
        if not block_results:
            raise errors.TaskFailure("Empty response from NirvanaApi while output {} from block {} in workflow {}".format(output, block_code, workflow))
        nirvana_token = self.Parameters.nirvana_token.data()['secret']
        req = requests.get(block_results[0].results[0].storagePath, headers={"Authorization": "OAuth {}".format(nirvana_token)})
        req.raise_for_status()
        return req.content

    def check_test_workflow(self, workflow):
        block_results = self._get_block_results(workflow, self.Parameters.block_code, self.Parameters.block_output)
        return self.check_block_result(block_results)

    def check_block_result(self, block_results):
        # Base checker only checks that the workflow has the specified block
        # Implement your test logic in this method
        return "Success"


class WorkflowCheckLossEqual(WorkflowCheckBlockResult):
    LOG_FILENAME = "./ytf_app_run.log"

    class Parameters(WorkflowCheckBlockResult.Parameters):
        loss_key = sdk2.parameters.String("Loss key in ytf_app_run.log", required=True)
        target_loss = sdk2.parameters.Float("Target loss value for success", required=True)
        eps = sdk2.parameters.Float("Eps", default=1e-2)

    def check_block_result(self, block_results):
        tmp_dir = tempfile.mkdtemp()
        last_match = None
        try:
            with tarfile.open(fileobj=BytesIO(block_results), mode='r') as logs:
                logs.extract(self.LOG_FILENAME, path=tmp_dir)
                with open(os.path.join(tmp_dir, self.LOG_FILENAME)) as f:
                    regexp = re.compile(r"{} = (\d+\.\d+)".format(self.Parameters.loss_key))
                    for line in f.readlines():
                        match = re.search(regexp, line)
                        if match:
                            last_match = float(match.group(1))
        except (tarfile.TarError, KeyError) as e:
            logging.error("Can't unpack {} from block_results: {}.".format(self.LOG_FILENAME, e))
            raise errors.TaskFailure(e)
        finally:
            shutil.rmtree(tmp_dir, ignore_errors=True)

        if last_match is None:
            raise errors.TaskFailure("Loss pattern '{}' not found in {}".format(self.Parameters.loss_key, self.LOG_FILENAME))

        result = "Success" if abs(last_match - self.Parameters.target_loss) < self.Parameters.eps else "Failure"

        return "{}: {} = {}".format(result, self.Parameters.loss_key, last_match)
