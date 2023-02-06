import json
import logging
import os
import subprocess
from subprocess import Popen

from sandbox import sdk2
from sandbox.common.errors import TaskFailure
from sandbox.common.types.client import Tag
from sandbox.common.types.resource import State
from sandbox.projects.mt.product import MtMlTestArtifact, MtMlTestRunner
from sandbox.projects.mt.util.arc_mixin import ArcMixin
from sandbox.projects.mt.util.task_profiler import TaskProfilerMixin

RESOURCE_DIR = 'resources'
RESOURCE_BUNDLE = 'resources.tar.gz'


class MtMlPackageTest(TaskProfilerMixin, ArcMixin, sdk2.Task):
    """
    Run tests for ML package without Arcadia build and GPU requirement
    """

    class Requirements(sdk2.Requirements):
        client_tags = Tag.Group.LINUX
        cores = 2
        ram = 8000
        disk_space = 16000

        class Caches(sdk2.Requirements.Caches):
            pass

    class Parameters(sdk2.Parameters):
        with sdk2.parameters.Group('Test params') as test_params_group:
            arc_params = ArcMixin.ArcParams()
            arc_params.arcadia_path.default_value = 'dict/mt/video/servers/tts'

            package_file = sdk2.parameters.String('Package file', default_value='package.json')
            requirements_file = sdk2.parameters.String('Requirements file', default_value='requirements.txt')
            setup_requires_file = sdk2.parameters.String('Setup requires file', default_value='setup_requires.txt')

            test_command = sdk2.parameters.String(
                'Test command',
                default_value='python -m pytest dict/mt/video/servers/tts/test',
            )
            test_env_vars = sdk2.parameters.Dict('Test env vars', default={'TEST_CONFIG': 'config.yaml'})

            test_resources = sdk2.parameters.Dict('Test resources', description='id: dest_path')
            test_config = sdk2.parameters.String('Test config', multiline=True)

            target_workflow = sdk2.parameters.String('Target workflow')

            show_stderr = sdk2.parameters.Bool('Show stderr', default_value=False)
            check_timeout = sdk2.parameters.Integer('Check timeout', default_value=180)

        with sdk2.parameters.Group('Advanced task params', collapse=True) as advanced_task_params_group:
            additional_tags = sdk2.parameters.List('Additional tags')
            flow_launch_id = sdk2.parameters.String('Flow launch ID', default_value='None')

            runner_resource = sdk2.parameters.Resource('Runner', resource_type=MtMlTestRunner, default=None)

    class Context(TaskProfilerMixin.Context, sdk2.Context):
        code_package_id = 0
        graph_ids_res_id = 0

    @sdk2.footer()
    def footer(self):
        return self.get_profiler_html(task=self)

    def on_prepare(self):
        super(MtMlPackageTest, self).on_prepare()

        tags = list(self.Parameters.tags)
        for tag in self.Parameters.additional_tags:
            if tag not in tags:
                tags.append(tag)

        self.Parameters.tags = tags

    def on_execute(self):
        super(MtMlPackageTest, self).on_execute()
        self.init_task_profiler(task=self)

        with self.memoize_stage.start_test_graph:
            self.start_test_graph()

        with self.profiler.action('Wait for graph finish'):
            self.wait_for_graph_finish()

    def start_test_graph(self):
        self.init_arc(task=self)
        try:
            with self.profiler.action('Mount Arc'):
                self.mount_arc(fetch_all=False)

            with self.profiler.action('Build package'):
                code_package_res_id = self.build_package()

            with self.profiler.action('Call runner start'):
                self.call_runner_start(code_package_res_id)
        finally:
            with self.profiler.action('Unmount Arc'):
                self.unmount_arc()

    def wait_for_graph_finish(self):
        runner = self.get_runner()
        graph_ids_file = str(sdk2.ResourceData(MtMlTestArtifact[self.Context.graph_ids_res_id]).path)

        process = Popen([runner, 'get-result', '--graph-id-result', graph_ids_file], env={
            'NIRVANA_TOKEN': sdk2.Vault.data('MT', 'NIRVANA_TOKEN')
        }, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        out, err = process.communicate()
        logging.debug('Start test out: %s', out)
        logging.debug('Start test err: %s', err)
        if process.returncode:
            raise TaskFailure('Start test failed')

        result = json.loads(out)
        if result['status'] != 'completed':
            raise sdk2.WaitTime(self.Parameters.check_timeout)

        if 'stdout.log' in result and result['stdout.log']:
            self.set_info('<p>Test STDOUT:</p><pre>%s</pre>' % result['stdout.log'], do_escape=False)

        if self.Parameters.show_stderr and 'stderr.log' in result and result['stderr.log']:
            self.set_info('<p>Test STDERR:</p><pre>%s</pre>' % result['stderr.log'], do_escape=False)

        if result['result'] != 'success':
            raise TaskFailure('Test result is ' + result['result'])

    def build_package(self):
        logging.debug('Start to build package')
        result_dir = os.path.join(self.work_dir, 'package')
        # noinspection PyUnresolvedReferences
        process = Popen([
            os.path.join(self.repo_path, 'ya'), 'package',
            os.path.join(str(self.Parameters.arcadia_path), str(self.Parameters.package_file)),
            '--tar', '--compression-filter=gzip', '--package-output=' + result_dir
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        logging.debug('Start to communicate')
        out, err = process.communicate()
        logging.debug('Package out: %s', out)
        logging.debug('Package err: %s', err)

        if process.returncode:
            raise TaskFailure('Package build failed')

        result_file = None
        for dir_path, dir_names, file_names in os.walk(result_dir):
            logging.debug('Walk for package: %s, %s, %s', dir_path, dir_names, file_names)
            for file_name in file_names:
                if file_name.endswith('.tar.gz'):
                    result_file = os.path.join(dir_path, file_name)
                    break

        if not result_file:
            raise RuntimeError('Package not found')

        logging.debug('Start to publish resource')
        res = MtMlTestArtifact(self, 'Code package', result_file, type='code_package')
        sdk2.ResourceData(res).ready()
        self.Context.code_package_id = res.id

        logging.debug('Package has been built')
        return res.id

    def call_runner_start(self, code_package_res_id):
        runner = self.get_runner()

        config_file = 'config.cfg'
        with open(config_file, 'w') as fp:
            fp.write(str(self.Parameters.test_config))

        # noinspection PyUnresolvedReferences
        requirements_txt = os.path.join(self.repo_path, str(self.Parameters.arcadia_path),
            str(self.Parameters.requirements_file))
        test_env = ' '.join(n + '=' + v for n, v in self.Parameters.test_env_vars.items())
        args = [
            runner, 'start',
            '--config', config_file, '--code-package-res-id', str(code_package_res_id),
            '--requirements-txt', requirements_txt,
            '--test-command', self.Parameters.test_command, '--test-env', test_env,
            '--graph-id-result', 'graph-id-result.json',
        ]
        setup_requires_txt = os.path.join(self.repo_path, str(self.Parameters.arcadia_path),
                                          str(self.Parameters.setup_requires_file))
        if os.path.exists(setup_requires_txt):
            args.extend(('--setup-requires-txt', setup_requires_txt))
        for res_id, dest_path in self.Parameters.test_resources.items():
            args.extend(('--resource', '%s=%s' % (res_id, dest_path)))
        if self.Parameters.target_workflow:
            args.extend(('--target-workflow', self.Parameters.target_workflow))
        process = Popen(args, env={
            'NIRVANA_TOKEN': sdk2.Vault.data('MT', 'NIRVANA_TOKEN')
        }, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        out, err = process.communicate()
        logging.debug('Start test out: %s', out)
        logging.debug('Start test err: %s', err)
        if process.returncode:
            raise TaskFailure('Start test failed')

        res = MtMlTestArtifact(self, 'Graph IDs', 'graph-id-result.json')
        sdk2.ResourceData(res).ready()
        self.Context.graph_ids_res_id = res.id

        with open('graph-id-result.json') as fp:
            graph_ids = json.load(fp)

        self.set_info(
            'Test graph launched: <a href="https://nirvana.yandex-team.ru/flow/{0}/{1}/graph">{1}</a>'.format(
                graph_ids['workflow_id'],
                graph_ids['workflow_instance_id'],
            ),
            do_escape=False,
        )

    def get_runner(self):
        res = self.Parameters.runner_resource
        if not res:
            res = MtMlTestRunner.find(state=State.READY).order(-sdk2.Resource.id).first()
        return str(sdk2.ResourceData(res).path)
