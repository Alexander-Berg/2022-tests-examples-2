import datetime
import os

from sandbox.common.types import client as ctc
from sandbox.sandboxsdk.environments import PipEnvironment
from sandbox.sandboxsdk import process
from sandbox import sdk2

from sandbox.projects.browser.common.git import repositories
from sandbox.projects.browser.common.hpe import HermeticPythonEnvironment

CONTAINER_RESOURCE_ID = 550671163
DATE_FORMAT = '%Y-%m-%d'


class DateParameter(sdk2.parameters.String):
    @classmethod
    def cast(cls, value):
        if value:
            datetime.datetime.strptime(value, DATE_FORMAT)
            return value


class BrowserPerfUpdateTestMongo(sdk2.Task):
    """Manual update mongo data from production to testing"""

    class Requirements(sdk2.Task.Requirements):
        client_tags = ctc.Tag.GENERIC
        environments = [PipEnvironment('virtualenv', '15.1.0')]

    class Parameters(sdk2.Parameters):
        kill_timeout = 6 * 60 * 60  # 6 hours

        with sdk2.parameters.Group('General settings') as general_settings:
            since = DateParameter('Update data since date %Y-%m-%d',
                                  required=False)
            till = DateParameter('Update data till date %Y-%m-%d',
                                 required=False)
            contexts = sdk2.parameters.String('Contexts list to update')
            host = sdk2.parameters.String(
                'Target mongo host (use @testing to select testing replicaset '
                'from envconfig', required=True, default='@testing')
            branch = sdk2.parameters.String(
                'Performance repo branch', required=True, default='master')
            drop = sdk2.parameters.Bool(
                'Drop collections before restoring them on target database',
                default=True)

        with sdk2.parameters.Group('Mongo credentials') as mongo_credentials:
            source_username = sdk2.parameters.String('Source mongo username')
            source_password_vault = sdk2.parameters.YavSecret(
                'YAV secret with source Mongo password',
                description=('YAV source mongo secret. "password" field '
                             'expected')
            )
            target_username = sdk2.parameters.String(
                'Target mongo username', default='pulse-test')
            target_password_vault = sdk2.parameters.YavSecret(
                'YAV secret with target Mongo password',
                description=('YAV target mongo secret. "password" field '
                             'expected'),
                default='sec-01exmhepjgyqdk8rq62bmncpmc'
            )

        _container = sdk2.parameters.Container(
            "Environment container resource",
            default_value=CONTAINER_RESOURCE_ID, required=True)

    def perf_path(self, *args):
        return str(self.path('performance', *args))

    def on_execute(self):
        repositories.Stardust.performance().clone(
            self.perf_path(), self.Parameters.branch)
        with HermeticPythonEnvironment(
            python_version='2.7.17',
            pip_version='9.0.2',
            requirements_files=[sdk2.Path(self.perf_path('tools', 'mongo_import', 'requirements.txt'))]
        ) as hpe:

            cmd = [
                str(hpe.python_executable),
                os.path.join(self.perf_path(), 'tools', 'mongo_import',
                             'main.py'),
                '--host', self.Parameters.host]
            (
                source_username,
                source_password_vault,
                target_username,
                target_password_vault,
                since,
                till,
                contexts,
                drop
            ) = (
                self.Parameters.source_username,
                self.Parameters.source_password_vault,
                self.Parameters.target_username,
                self.Parameters.target_password_vault,
                self.Parameters.since,
                self.Parameters.till,
                self.Parameters.contexts,
                self.Parameters.drop
            )
            if source_username:
                cmd.extend(['--source-username', source_username])
            if source_password_vault:
                source_password = source_password_vault.data()['password']
                cmd.extend(['--source-password', source_password])
            if target_username:
                cmd.extend(['--target-username', target_username])
            if target_password_vault:
                target_password = target_password_vault.data()['password']
                cmd.extend(['--target-password', target_password])
            if since:
                cmd.extend(['--since', since])
            if till:
                cmd.extend(['--till', till])
            if contexts:
                cmd.extend(['--contexts', contexts])
            if drop:
                cmd.append('--drop')

            process.run_process(
                cmd,
                work_dir=self.perf_path(),
                log_prefix='mongo_import',
                outputs_to_one_file=False,
                shell=True
            )
