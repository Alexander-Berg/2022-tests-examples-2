import jinja2
import json
import logging
import os
import multiprocessing as mp

from sandbox import sdk2
from sandbox import common

from sandbox.common.types.misc import DnsType
import sandbox.common.types.client as ctc


class TestConductorTarball(sdk2.Task):
    """Test conductor tarball"""

    class Requirements(sdk2.Requirements):
        dns = DnsType.DNS64
        disk_space = 1024
        client_tags = (
            ctc.Tag.GENERIC | ctc.Tag.LINUX_XENIAL
        )
        cores = 4

    class Context(sdk2.Task.Context):
        mysqld_pid = None

    class Parameters(sdk2.Task.Parameters):
        _container = sdk2.parameters.Container(
            "Environment container resource",
            default_value=575696901,
            required=True
        )
        ref_id = sdk2.parameters.String('Git ref id', default='master', required=True)
        ref_sha = sdk2.parameters.String('Git ref SHA', required=False)
        release = sdk2.parameters.Bool('Create resources', default=False)

    # Checkout
    # Run bundle install
    # create db and apply migrates
    #   db:create db:migrate RAILS_ENV=test
    # run test
    #   rake test - not needed
    #   rake spec

    REPO_URL = 'ssh://git@bb.yandex-team.ru/search_infra/conductor.git'
    CHECKOUT_PATH = 'src'
    MYSQL_PATH = 'mysql'
    GEM_HOME = 'gems'

    def _get_gems_home(self):
        return self.path().joinpath(self.GEM_HOME).as_posix()

    @property
    def get_env(self):
        env = os.environ.copy()
        env['GEM_HOME'] = self._get_gems_home()
        env['RAILS_ENV'] = 'test'
        return env

    def checkout(self):
        logging.info('Fetching data from repository')
        clone_command = 'git clone {repo} {path}'.format(repo=self.REPO_URL, path=self.CHECKOUT_PATH)
        fetch_command = 'git fetch origin'
        checkout_command = 'git checkout -f {ref_id}'.format(ref_id=self.Parameters.ref_sha or self.Parameters.ref_id)
        with sdk2.helpers.ProcessLog(self, logger='git_checkout') as pl:
            if not os.path.exists(self.CHECKOUT_PATH):
                sdk2.helpers.subprocess.Popen(
                    clone_command.split(),
                    stdout=pl.stdout,
                    stderr=pl.stderr
                ).wait()
            else:
                sdk2.helpers.subprocess.Popen(
                    fetch_command.split(),
                    cwd=self.CHECKOUT_PATH,
                    stdout=pl.stdout,
                    stderr=pl.stderr
                ).wait()
            sdk2.helpers.subprocess.Popen(
                checkout_command.split(),
                cwd=self.CHECKOUT_PATH,
                stdout=pl.stdout,
                stderr=pl.stderr
            ).wait()

    def prepare_env(self):
        logging.info('Preparing environment')
        commands = [
            '/usr/bin/gem2.1 install --no-document --install-dir {} -E bundler'.format(self._get_gems_home()),
            '{}/bin/bundle install --deployment --jobs={}'.format(self._get_gems_home(), mp.cpu_count())
        ]
        with sdk2.helpers.ProcessLog(self, logger='prepare') as pl:
            for cmd in commands:
                sdk2.helpers.subprocess.Popen(
                    cmd.split(),
                    cwd=self.path().joinpath(self.CHECKOUT_PATH, 'src').as_posix(),
                    stdout=pl.stdout,
                    env=self.get_env,
                    stderr=pl.stderr
                ).wait()
        common_path = self.path().joinpath(self.MYSQL_PATH)
        dbpath = common_path.joinpath('db')
        logpath = common_path.joinpath('logs')
        for path in common_path, dbpath, logpath:
            path.mkdir(mode=0o775, parents=True, exist_ok=True)
        install_db_cmd = '/usr/sbin/mysqld --no-defaults --initialize-insecure --datadir={dbpath}'.format(dbpath=dbpath.as_posix())
        mysql_cmd = (
            '/usr/sbin/mysqld '
            '--no-defaults '
            '--datadir={dbpath} '
            '--log-error={logpath}/mysqld-3306_err.log '
            '--pid-file={common_path}/mysqld-3306.pid '
            '--socket={common_path}/mysqld-3306.sock '
            '--port=3306 '
            '--sql-mode=STRICT_TRANS_TABLES,NO_ENGINE_SUBSTITUTION'
        ).format(
            dbpath=dbpath.as_posix(),
            logpath=logpath.as_posix(),
            common_path=common_path.as_posix()
        )
        # Patching some files. TODO: delete this
        with open(self.path().joinpath(self.CHECKOUT_PATH, 'src', '.rspec').as_posix(), 'r+') as f:
            data = f.read().replace('--color', '--color\n--format json\n--out out.json\n--format html\n--out out.html')
            f.seek(0)
            f.write(data)
        with open(self.path().joinpath(self.CHECKOUT_PATH, 'src', 'config', 'database.yml').as_posix(), 'r+') as f:
            data = f.read().replace('encoding: utf8', 'encoding: utf8\n  socket: {}/mysqld-3306.sock'.format(common_path.as_posix()))
            f.seek(0)
            f.write(data)
        with sdk2.helpers.ProcessLog(self, logger='mysql') as pl:
            sdk2.helpers.subprocess.Popen(
                install_db_cmd.split(),
                stdout=pl.stdout,
                stderr=pl.stderr
            ).wait()
        self.Context.mysqld_pid = sdk2.helpers.subprocess.Popen(mysql_cmd.split()).pid
        # self.suspend()

    @sdk2.footer()
    def build_footer(self):
        if not self.Context.json_report:
            report_file_path = self.path().joinpath(self.CHECKOUT_PATH, 'src', 'out.json').as_posix()
            if not os.path.exists(report_file_path):
                return "No report file found"
            report_file = open(report_file_path, 'r').read().strip()
        result = self.Context.json_report or report_file
        data = json.loads(result)
        template_path = os.path.dirname(os.path.abspath(__file__))
        env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_path), extensions=['jinja2.ext.do'])
        return env.get_template("footer.html").render(data)

    @sdk2.report(title='RSpec test results')
    def build_report(self):
        if not self.Context.html_report:
            report_file_path = self.path().joinpath(self.CHECKOUT_PATH, 'src', 'out.html').as_posix()
            if not os.path.exists(report_file_path):
                return "No report file found"
            report_file = open(report_file_path, 'r').read().strip()
            return report_file
        return self.Context.html_report

    def run_tests(self):
        cmds = [
            'bin/rake db:drop db:create db:migrate',
            'bin/rake spec'
        ]
        with sdk2.helpers.ProcessLog(self, logger='rake') as pl:
            for cmd in cmds:
                process = sdk2.helpers.subprocess.Popen(
                    cmd.split(),
                    cwd=self.path().joinpath(self.CHECKOUT_PATH, 'src').as_posix(),
                    env=self.get_env,
                    stdout=pl.stdout,
                    stderr=pl.stderr
                )
                process.wait()
        # res = sdk2.ResourceData(ConductorTestResults(
        #    self,
        #    'RSpec test results',
        #    self.path().joinpath(self.CHECKOUT_PATH, 'src', 'out.html').as_posix()
        # ))
        self.Context.html_report = open(self.path().joinpath(self.CHECKOUT_PATH, 'src', 'out.html').as_posix()).read().strip()
        self.Context.json_report = open(self.path().joinpath(self.CHECKOUT_PATH, 'src', 'out.json').as_posix()).read().strip()
        if process.returncode != 0:
            raise common.errors.TaskFailure("At least one test failed.\nSee footer for brief or report tab for detailed info")

    def on_execute(self):
        self.checkout()
        self.prepare_env()
        self.run_tests()
