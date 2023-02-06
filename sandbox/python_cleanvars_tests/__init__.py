from sandbox.projects.home.resources import HomeCleanvarsPythonTestsLxc, HomeAllureReport
from sandbox import sdk2
import logging
from sandbox.sdk2.helpers import subprocess as sp
from sandbox.sdk2.vcs.git import Git
import sandbox.common.types.misc as ctm
import os


class HomePythonCleanvarsTests(sdk2.Task):

    class Requirements(sdk2.Task.Requirements):
        privileged = True
        dns = ctm.DnsType.DNS64

    class Parameters(sdk2.Task.Parameters):
        container = sdk2.parameters.Container("Container", required=True, resource_type=HomeCleanvarsPythonTestsLxc, platform='linux_ubuntu_14.04_trusty')

        with sdk2.parameters.Group("Git parameters") as git_block:
            git_repo = sdk2.parameters.String('Git repository', required=True, default='https://github.yandex-team.ru/morda/main')
            branch = sdk2.parameters.String('Branch', required=True, default_value='dev')

        with sdk2.parameters.Group("Test parameters") as tests_block:
            is_monitoring = sdk2.parameters.Bool('Is monitoring', required=True, default=False)
            with is_monitoring.value[False]:
                morda_env = sdk2.parameters.String('Morda environment', required=True, default_value='production')
            threads = sdk2.parameters.Integer('Threads', required=True, default_value=10)
            test_file = sdk2.parameters.String('Test file', required=False)
            allure_features = sdk2.parameters.String('Allure features', required=False)
            allure_stories = sdk2.parameters.String('Allure stories', required=False)
            dns_morda = sdk2.parameters.String('Override morda DNS: %ip%', required=False)
            dns_override = sdk2.parameters.String('Override DNS: %regex%=%ip%,%regex2%=%ip2%', required=False)
            generate_allure = sdk2.parameters.Bool('Generate Allure report', default=True)
            with generate_allure.value[True]:
                allure_ttl = sdk2.parameters.Integer('Allure TTL', required=True, default=7)

    def git_clone(self):
        root_dir = 'repository'
        git = Git(self.Parameters.git_repo)
        git.clone(root_dir, self.Parameters.branch)
        self.Context.root_dir = root_dir + '/' + 'function_tests'

    def on_prepare(self):
        self.git_clone()
        self.Context.env = os.environ.copy()
        self.Context.env['PYTHONPATH'] = "/usr/local/lib/python2.7/site-packages:/usr/lib/python2.7/site-packages"
        self.Context.env['PATH'] = ':'.join([self.Context.env['PATH'], '/usr/bin', '/usr/local/bin'])

    def prepare_deps(self):
        with sdk2.helpers.ProcessLog(self, logger=logging.getLogger("install_deps")) as pl:
            sp.Popen('python2.7 -m pip install -r requirements.txt', shell=True, stdout=pl.stdout, stderr=sp.STDOUT, cwd=self.Context.root_dir, env=self.Context.env).wait()
            sp.Popen('make schemas', shell=True, stdout=pl.stdout, stderr=sp.STDOUT, cwd=self.Context.root_dir, env=self.Context.env).wait()

    def _add_run_parameter(self, command, key, value):
        if value:
            command.extend(['--{}'.format(key), '"{}"'.format(value)])

    def create_run_command(self):
        command = ['py.test',
                   '-n', str(self.Parameters.threads)]

        self._add_run_parameter(command, 'morda_env', self.Parameters.morda_env)
        self._add_run_parameter(command, 'allure_features', self.Parameters.allure_features)
        self._add_run_parameter(command, 'allure_stories', self.Parameters.allure_stories)
        self._add_run_parameter(command, 'dns_morda', self.Parameters.dns_morda)
        self._add_run_parameter(command, 'dns_override', self.Parameters.dns_override)

        if self.Parameters.is_monitoring:
            self._add_run_parameter(command, 'monitoring', '1')

        if self.Parameters.test_file:
            command.append(self.Parameters.test_file)

        return command

    def generate_allure_report(self):
        with sdk2.helpers.ProcessLog(self, logger=logging.getLogger("generate_allure")) as pl:
            status = sp.Popen('allure generate allure-results -o ../../allure-report', env=self.Context.env, shell=True, stdout=pl.stdout, stderr=sp.STDOUT, cwd=self.Context.root_dir).wait()
            if status != 0:
                raise Exception('Failed to generate allure report')
            report = HomeAllureReport(self, "Allure report", path='allure-report', ttl=self.Parameters.allure_ttl)
            report_data = sdk2.ResourceData(report)
            report_data.ready()
            report_url = self.server.resource[report.id][:]["http"]["proxy"] + '/index.html'
            self.set_info('REPORT: <a href="{}">{}</a>'.format(report_url, report_url), False)

    def run_tests(self):
        command = self.create_run_command()
        logging.info(str(command))
        with sdk2.helpers.ProcessLog(self, logger=logging.getLogger("tests_execute")) as pl:
            sp.Popen(' '.join(command), env=self.Context.env, shell=True, stdout=pl.stdout, stderr=sp.STDOUT, cwd=self.Context.root_dir).wait()

    def on_execute(self):
        self.prepare_deps()
        self.run_tests()
        if self.Parameters.generate_allure:
            self.generate_allure_report()
