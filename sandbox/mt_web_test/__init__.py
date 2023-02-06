import logging
import os
# noinspection PyUnresolvedReferences
from string import Template

from sandbox import sdk2
from sandbox.common.errors import TaskFailure
from sandbox.common.types.misc import DnsType
from sandbox.projects.mt.product import MtWebTestArtifact, TranslateWebLxcContainer
from sandbox.projects.mt.util.arc_mixin import ArcMixin
from sandbox.projects.mt.util.mt_web import MtWebMixin
from sandbox.projects.mt.util.task_profiler import TaskProfilerMixin


class MtWebTest(TaskProfilerMixin, ArcMixin, MtWebMixin, sdk2.Task):
    """
    Run MT web test script
    """

    class Requirements(sdk2.Requirements):
        cores = 16
        ram = 16000
        disk_space = 16000
        dns = DnsType.DNS64

        class Caches(sdk2.Requirements.Caches):
            pass

    class Parameters(sdk2.Parameters):
        with sdk2.parameters.Group('Test params') as test_params_group:
            test_command = sdk2.parameters.String('Test command', required=True)
            arc_params = ArcMixin.ArcParams()

        with sdk2.parameters.Group('Report params') as report_params_group:
            report_file = sdk2.parameters.String('Report file', required=True, default_value='report.txt')
            error_file = sdk2.parameters.String('Error file', required=True, default_value='errors.txt')

        with sdk2.parameters.Group('Service server config') as service_server_params_group:
            service_params = MtWebMixin.ServiceParams()

        with sdk2.parameters.Group('Caching params', collapse=True) as caching_params_group:
            caching_params = MtWebMixin.CachingParams()

        with sdk2.parameters.Group('Advanced task params', collapse=True) as advanced_task_params_group:
            additional_tags = sdk2.parameters.List('Additional tags')
            flow_launch_id = sdk2.parameters.String('Flow launch ID', default_value='None')
            process_params = MtWebMixin.ProcessParams()

        _container = sdk2.parameters.Container(
            label='Translate container',
            resource_type=TranslateWebLxcContainer,
            platform='linux_ubuntu_16.04_xenial',
            required=True,
        )

    class Context(TaskProfilerMixin.Context, MtWebMixin.Context, sdk2.Context):
        test_report = ''
        test_errors = ''

        test_report_name = ''
        test_errors_name = ''

    @sdk2.header()
    def header(self):
        if not self.Context.test_report:
            return ''

        tpl_file = os.path.join(os.path.dirname(__file__), 'header.html')
        with open(tpl_file) as fp:
            tpl = Template(fp.read())

        return tpl.safe_substitute(
            report_link=self.Context.test_report,
            report_name=self.Context.test_report_name,
            errors_link=self.Context.test_errors,
            errors_name=self.Context.test_errors_name,
            log_link=self.Context.service_logs,
        )

    @sdk2.footer()
    def footer(self):
        return self.get_profiler_html(task=self)

    def on_prepare(self):
        super(MtWebTest, self).on_prepare()

        tags = list(self.Parameters.tags)
        for tag in self.Parameters.additional_tags:
            if tag not in tags:
                tags.append(tag)

        self.Parameters.tags = tags

    def on_execute(self):
        super(MtWebTest, self).on_execute()
        self.init_mt_web(task=self)
        self.init_arc(task=self)
        self.init_task_profiler(task=self)

        try:
            with self.profiler.action('Mount Arc'):
                self.mount_arc()

            self.run_main_actions()
        finally:
            with self.profiler.action('Unmount Arc'):
                self.unmount_arc()

    def run_main_actions(self):
        with self.profiler.action('Setup venv'):
            self.setup_venv()

        with self.profiler.action('Prepare project for testing'):
            self.run_project_method('ci-prepare-for-testing')

        with self.profiler.action('Collect node_modules from cache'):
            self.collect_node_modules_from_cache()

        with self.profiler.action('Run tests'):
            test_ok = self.run_tests()

        with self.profiler.action('Cache node_modules'):
            self.store_node_modules_to_cache()

        with self.profiler.action('Finalize'):
            self.finalize_mt_web()
            if not test_ok:
                raise TaskFailure('Test run failed')

    def run_tests(self):
        service_p = self.launch_service_if_needed()

        test_command, report_file, error_file = self.get_test_command()
        ret_code = self.run_process(test_command, tag='test').wait()

        self.stop_service(service_p)
        self.save_results(report_file, error_file)

        test_ok = ret_code == 0
        return test_ok

    def get_test_command(self):
        test_raw_command = str(self.Parameters.test_command).split(' ')
        test_raw_command = filter(bool, test_raw_command)
        if not test_raw_command:
            raise TaskFailure('Empty test command')

        test_script = os.path.join(self.project_dir, test_raw_command[0])
        if not os.path.isfile(test_script):
            raise TaskFailure('Test script was not found')

        report_file_name = str(self.Parameters.report_file)
        self.Context.test_report_name = report_file_name

        error_file_name = str(self.Parameters.error_file)
        self.Context.test_errors_name = error_file_name

        report_file = os.path.join(self.work_dir, report_file_name)
        error_file = os.path.join(self.work_dir, error_file_name)

        test_command = [test_script] + test_raw_command[1:] + ['--report=%s' % report_file, '--errors=%s' % error_file]
        logging.debug('Test command: %s', test_command)

        return test_command, report_file, error_file

    def save_results(self, report_file, error_file):
        # noinspection PyUnresolvedReferences
        commit = str(self.Parameters.commit)
        flow_launch_id = str(self.Parameters.flow_launch_id)

        self.save_logs(commit, flow_launch_id=flow_launch_id)
        self.save_report(report_file, commit, flow_launch_id)
        self.save_errors(error_file, commit, flow_launch_id)

    def save_report(self, report_file, commit, flow_launch_id):
        if not os.path.exists(report_file):
            with open(report_file, 'w') as fp:
                fp.write('No report file found')

        if os.path.isdir(report_file) and not os.listdir(report_file):
            with open(os.path.join(report_file, 'info.txt'), 'w') as fp:
                fp.write('No report data found')

        res = MtWebTestArtifact(
            self, 'Test report', report_file,
            commit=commit, flow_launch_id=flow_launch_id, type='report',
        )
        sdk2.ResourceData(res).ready()

        self.Context.test_report = str(res.http_proxy)

    def save_errors(self, error_file, commit, flow_launch_id):
        if not os.path.exists(error_file):
            with open(error_file, 'w') as fp:
                fp.write('No error file found')

        if os.path.isdir(error_file) and not os.listdir(error_file):
            with open(os.path.join(error_file, 'info.txt'), 'w') as fp:
                fp.write('No error data found')

        res = MtWebTestArtifact(
            self, 'Test errors', error_file,
            commit=commit, flow_launch_id=flow_launch_id, type='errors',
        )
        sdk2.ResourceData(res).ready()

        self.Context.test_errors = str(res.http_proxy)
