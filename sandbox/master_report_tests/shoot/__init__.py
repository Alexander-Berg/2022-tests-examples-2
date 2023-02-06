from __future__ import print_function

import cPickle as pickle
import json
import logging
import StringIO

from multiprocessing.pool import ThreadPool

from sandbox.sdk2 import (
    ResourceData,
    Vault,
    parameters,
)
from sandbox.projects.yabs.master_report_tests.resources import (
    YabsMasterReportBackupDescription,
    YabsMasterReportRequests,
    YabsMasterReportShootResults
)
from sandbox.projects.yabs.base_bin_task import BaseBinTask


class YabsMasterReportShoot(BaseBinTask):
    '''Shoots requests at master report installation for B2B tests'''

    class Parameters(BaseBinTask.Parameters):
        description = 'Master report B2B shoot'

        with BaseBinTask.Parameters.version_and_task_resource() as version_and_task_resource:
            resource_attrs = parameters.Dict('Filter resource by', default={'name': 'YabsMasterReportTests'})

        with parameters.Group('Shoot') as shoot_params:
            result_resource = parameters.ParentResource(
                'Parent resource to fill',
                resource_type=YabsMasterReportShootResults,
                do_not_copy=True,
            )
            requests_resource = parameters.Resource(
                'Resource with requests',
                resource_type=YabsMasterReportRequests,
                required=True,
            )
            backup_resource = parameters.Resource(
                'Resource with backup description',
                resource_type=YabsMasterReportBackupDescription,
                required=True,
            )
            target_host = parameters.String(
                'Target host',
                required=True,
            )
            threads = parameters.Integer(
                'Number of threads',
                default=5,
                required=True,
            )
            username = parameters.String(
                'Username for ssh connection',
                required=True
            )
            ssh_key_vault = parameters.String(
                'Vault with ssh private key',
                required=True
            )
            timeout = parameters.Integer(
                'Request timeout',
                default=300,
                required=True
            )

    def create_resource(self, responses):
        if self.Parameters.result_resource:
            resource = self.Parameters.result_resource
        else:
            resource = YabsMasterReportShootResults(
                self,
                description='Master report B2B shoot results',
                path='responses.pkl',
            )

        resource_data = ResourceData(resource)
        with open(str(resource_data.path), 'wb') as f:
            for resp in responses:
                pickle.dump(resp, f)

        resource_data.ready()

    def do_shoot(self, requests):
        from yabs.interface.yabs_export_scripts_fast.comparing_request import get_response

        target_url = 'http://{}/export/master-report.cgi'.format(self.Parameters.target_host)

        def shoot_one(req):
            return get_response(
                req,
                target_url,
                'b2b_tests',
                self.Parameters.timeout,
                True
            )

        pool = ThreadPool(self.Parameters.threads)
        return pool.imap(shoot_one, requests)

    def set_table_host_option(self):
        import paramiko

        backup_file = ResourceData(self.Parameters.backup_resource)
        with open(str(backup_file.path), 'r') as f:
            table_name = json.load(f)['table']

        ssh_key = Vault.data(self.Parameters.ssh_key_vault)

        with paramiko.SSHClient() as ssh_client:
            ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            pkey = paramiko.RSAKey.from_private_key(StringIO.StringIO(ssh_key))
            ssh_client.connect(hostname=self.Parameters.target_host, username=self.Parameters.username, pkey=pkey, timeout=300)

            command = 'sudo bash -c \'echo "master-report-main-table {}" > /etc/testing\''.format(table_name)
            logging.info('Executing command %s', command)

            _, stdout, stderr = ssh_client.exec_command(command)

            exit_code = stdout.channel.recv_exit_status()
            if exit_code != 0:
                logging.error('Failed to execute remote command, stderr:')
                for line in stderr:
                    logging.error(line)

                raise Exception('Failed to set host option on remote host')

    def on_execute(self):
        requests_file = ResourceData(self.Parameters.requests_resource)
        with open(str(requests_file.path), 'r') as f:
            requests = json.load(f)['requests']

        self.set_table_host_option()
        responses = self.do_shoot(requests)
        self.create_resource(responses)
