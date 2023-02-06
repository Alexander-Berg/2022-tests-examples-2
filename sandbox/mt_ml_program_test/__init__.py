import logging
import os
import re
import shlex
from subprocess import Popen

from sandbox import sdk2
from sandbox.common.errors import TaskFailure
from sandbox.common.types.client import Tag
from sandbox.projects.mt.product import MtMlTestArtifact
from sandbox.projects.mt.util.arc_mixin import ArcMixin
from sandbox.projects.mt.util.task_profiler import TaskProfilerMixin

RESOURCE_DIR = 'resources'
RESOURCE_BUNDLE = 'resources.tar.gz'


class MtMlProgramTest(TaskProfilerMixin, ArcMixin, sdk2.Task):
    """
    Run tests for ML program with Arcadia build and GPU requirement
    """

    class Requirements(sdk2.Requirements):
        client_tags = Tag.Group.LINUX
        cores = 16
        ram = 32768
        disk_space = 32768

        class Caches(sdk2.Requirements.Caches):
            pass

    class Parameters(sdk2.Parameters):
        with sdk2.parameters.Group('Test params') as test_params_group:
            arc_params = ArcMixin.ArcParams()
            arc_params.arcadia_path.default_value = 'dict/mt/video/servers/asr'

            yt_token_name = sdk2.parameters.String('YT token name', default_value='glycine_oauth_token')
            definition_flags = sdk2.parameters.String('Definition flags', default_value='')

        with sdk2.parameters.Group('Advanced task params', collapse=True) as advanced_task_params_group:
            additional_tags = sdk2.parameters.List('Additional tags')
            flow_launch_id = sdk2.parameters.String('Flow launch ID', default_value='None')

    class Context(TaskProfilerMixin.Context, sdk2.Context):
        pass

    @sdk2.footer()
    def footer(self):
        return self.get_profiler_html(task=self)

    def on_prepare(self):
        super(MtMlProgramTest, self).on_prepare()

        tags = list(self.Parameters.tags)
        for tag in self.Parameters.additional_tags:
            if tag not in tags:
                tags.append(tag)

        self.Parameters.tags = tags

    def on_execute(self):
        super(MtMlProgramTest, self).on_execute()
        self.init_task_profiler(task=self)
        self.init_arc(task=self)

        try:
            with self.profiler.action('Mount Arc'):
                self.mount_arc(fetch_all=False)

            with self.profiler.action('Run tests'):
                if not self.run_tests():
                    raise TaskFailure('Test run has been failed')
        finally:
            with self.profiler.action('Unmount Arc'):
                self.unmount_arc()

    def run_tests(self):
        logging.debug('Start to test')
        # noinspection PyUnresolvedReferences
        code_path = os.path.join(self.repo_path, str(self.Parameters.arcadia_path))
        os.chdir(code_path)

        test_logs_dir = os.path.join(self.work_dir, 'test_logs')
        os.makedirs(test_logs_dir)
        test_stdout = os.path.join(test_logs_dir, 'test.out.txt')
        test_stderr = os.path.join(test_logs_dir, 'test.err.txt')

        yt_token = sdk2.Vault.data(self.owner, self.Parameters.yt_token_name)

        with open(test_stdout, 'w') as ofp, open(test_stderr, 'w') as efp:
            cmd = [
                os.path.join(self.repo_path, 'ya'), 'make', '-rtA',
                '--run-tagged-tests-on-yt', '--yt-store', '--test-stdout', '--test-stderr',
            ] + shlex.split(self.Parameters.definition_flags)
            logging.info('Run: {}'.format(cmd))
            process = Popen(cmd, stdout=ofp, stderr=efp, env={'YT_TOKEN': yt_token})

        logging.debug('Start to communicate')
        process.communicate()
        logging.info('Test run finished')

        with open(test_stderr) as fp:
            stderr_content = fp.read()

        matches = re.match(r'.+[^=](=+ test session starts =+.+)$', stderr_content, re.DOTALL | re.IGNORECASE)
        if not matches:
            matches = re.match(r'.+(Total \d+ suites:.+)$', stderr_content, re.DOTALL | re.IGNORECASE)
        if matches:
            self.set_info(matches.group(1).strip())

        logging.debug('Start to publish resource')
        sdk2.ResourceData(
            MtMlTestArtifact(self, 'Test logs', test_logs_dir, type='test_logs'),
        ).ready()

        logging.info('Test logs are published')

        return process.returncode == 0
