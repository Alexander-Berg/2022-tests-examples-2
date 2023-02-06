import json
import os

import sandbox.common.types.client as ctc
import sandbox.common.types.misc as ctm
from sandbox import sdk2
from sandbox.projects.browser.common.git import Git
from sandbox.projects.browser.sb_lite.common import AbstractSBLiteResource
from sandbox.projects.browser.sb_lite.common import AbstractSBLiteTask
from sandbox.sandboxsdk.environments import SandboxEnvironment
from sandbox.sdk2 import paths


class TestSBLiteResource(AbstractSBLiteResource):
    """
    Test Sandbox Lite resource.
    """


class TestSBLiteTask(AbstractSBLiteTask):
    """
    Test Sandbox Lite worker task.
    """

    _TEST_CODE_MODULE = 'sandbox_lite_test'
    _TEST_REQUIREMENTS = 'requirements.txt'

    class Requirements(AbstractSBLiteTask.Requirements):
        client_tags = ctc.Tag.BROWSER & ctc.Tag.LINUX_TRUSTY
        cores = 1
        dns = ctm.DnsType.DNS64
        ram = 2 * 1024

        class Caches(AbstractSBLiteTask.Requirements.Caches):
            pass

    class Parameters(AbstractSBLiteTask.Parameters):
        with sdk2.parameters.Group('Repository') as repository_settings:
            git_url = sdk2.parameters.String(
                'Git URL',
                description='Git URL to clone repository.')
            git_branch = sdk2.parameters.String(
                'Git branch',
                description='Git branch to build on.')
            git_commit = sdk2.parameters.String(
                'Git commit',
                description='Git commit to build on.')

        with sdk2.parameters.Group('Test') as test_settings:
            task_requirements_paths = sdk2.parameters.String(
                'Requirements paths',
                description='Task requirements paths in git repository.',
                multiline=True)
            task_requirements_text = sdk2.parameters.String(
                'Requirements text',
                description='Task requirements to save and install.',
                multiline=True)
            task_work_dir = sdk2.parameters.String(
                'Task work directory',
                description='Relative path of task working directory in git repository.',
                multiline=True)
            task_import_paths = sdk2.parameters.String(
                'Task import paths',
                description='List of import paths relative of git repository root dir.',
                multiline=True)
            task_class = sdk2.parameters.String(
                'Task class',
                description='Task class to execute.')
            task_code_text = sdk2.parameters.String(
                'Task code',
                description='Task code to save and execute.',
                multiline=True)
            task_args_json = sdk2.parameters.String(
                'Task arguments (JSON)',
                description='JSON with task arguments to pass.',
                multiline=True)

        with sdk2.parameters.Group('Credentials') as credentials_group:
            yav_token_vault = sdk2.parameters.String(
                'Vault item with YAV OAuth token.',
                default='robot-browser-infra_yav_token')

    def _create_worker_helper(self):
        """
        :rtype: sandbox_lite_runner.helper.WorkerHelper
        """
        from sandbox_lite_runner.helper import WorkerHelper

        class TestWorkerHelper(WorkerHelper):
            def __init__(self, my_task):
                """
                :type my_task: TestSBLiteTask
                """
                super(TestWorkerHelper, self).__init__(
                    my_task,
                    TestSBLiteTask, TestSBLiteResource,
                    dict(my_task.Parameters),
                    str(my_task.Parameters.git_url),
                    str(my_task.Parameters.git_branch),
                    str(my_task.Parameters.git_commit))

            def arguments_to_parameters(self, arguments):
                return {
                    TestSBLiteTask.Parameters.task_args_json.name: json.dumps(arguments),
                }

            def parameters_to_arguments(self, parameters):
                """
                :type parameters: TestSBLiteTask.Parameters
                """
                return json.loads(parameters.task_args_json) if parameters.task_args_json else {}

        return TestWorkerHelper(self)

    def _start_first_worker(self, worker_helper):
        return worker_helper.start_worker(
            worker_helper.parameters_to_arguments(self.Parameters))

    @property
    def _python_version(self):
        return '2.7.17'

    def on_execute_worker(self):
        # Checkout git repository.
        repo_dir = self.path('work')
        paths.make_folder(repo_dir)
        if self.Parameters.git_url:
            Git(self.Parameters.git_url, filter_branches=False).clone(
                target_dir=str(repo_dir),
                branch=self.Parameters.git_branch, commit=self.Parameters.git_commit)

        # Save test data.
        test_dir = self.path('test')
        paths.make_folder(test_dir)
        test_requirements_path = test_dir.joinpath(self._TEST_REQUIREMENTS)
        test_requirements_path.write_text(self.Parameters.task_requirements_text)
        if '.' in self.Parameters.task_class:
            task_class = self.Parameters.task_class
        else:
            test_module_path = test_dir.joinpath(self._TEST_CODE_MODULE + '.py')
            test_module_path.write_text(self.Parameters.task_code_text)
            task_class = '{}.{}'.format(self._TEST_CODE_MODULE, self.Parameters.task_class)

        # Run the test.

        requirements_paths = [test_requirements_path] + [
            repo_dir.joinpath(p)
            for p in self.Parameters.task_requirements_paths.splitlines()]
        task_import_paths = [test_dir] + [
            repo_dir.joinpath(p)
            for p in self.Parameters.task_import_paths.splitlines()]
        env = {
            'PYTHONPATH': os.pathsep.join(str(p) for p in task_import_paths),
            'YAV_TOKEN': sdk2.Vault.data(self.Parameters.yav_token_vault),
        }
        resources_dir = self.path('resources')
        cache_dir = SandboxEnvironment.exclusive_build_cache_dir('sandbox-lite-cache')
        output_dir = self.path('output')
        work_dir = repo_dir.joinpath(self.Parameters.task_work_dir)

        worker_helper = self._create_worker_helper()
        ipc_runner = self._create_ipc_runner(
            worker_helper, resources_dir, cache_dir, output_dir, work_dir)
        self._run_task(
            ipc_runner, requirements_paths,
            task_class, env, output_dir, work_dir)
