#!/usr/bin/env python
# coding: utf-8

import glob
import logging
import shlex
import subprocess

import sandbox.common.types.misc as ctm

from sandbox.sandboxsdk.channel import channel
from sandbox.sandboxsdk.parameters import SandboxStringParameter
from sandbox.sandboxsdk.task import SandboxTask
import sandbox.common.types.client as ctc


class HostParameter(SandboxStringParameter):
    name = 'host'
    description = 'Source host of the backup'
    default_value = 'testenv-dbs01.search.yandex.net'


class QueryParameter(SandboxStringParameter):
    name = 'query'
    description = 'SQL query for check backup'
    default_value = "mysql -u testenv_ro -protestenv testenv -e 'select count(*) > 0 from autocheck_trunk_revisions where from_unixtime(timestamp) >= now() - interval 1 day;'"


class TestEnvironmentBackupTest(SandboxTask):
    type = 'TEST_ENVIRONMENT_BACKUP_TEST'
    privileged = True
    execution_space = 200 * 1024
    dns = ctm.DnsType.DNS64
    client_tags = ctc.Tag.LINUX_TRUSTY

    input_parameters = [
        HostParameter,
        QueryParameter,
    ]

    def initCtx(self):
        ten_hours = 10 * 60 * 60
        self.ctx['kill_timeout'] = ten_hours

    def _get_backup_resource(self):
        res = channel.sandbox.list_resources(
            resource_type='TESTENV_DB_BACKUP',
            attribute_name='from_host',
            attribute_value=self.ctx[HostParameter.name],
            status='READY',
            limit=1,
        )[0]
        logging.info('Download resource %s', res.id)
        return self._read_resource(res.id).abs_path()

    def on_execute(self):
        self._run('wget https://repo.percona.com/apt/percona-release_0.1-5.trusty_all.deb')
        self._run('dpkg -i percona-release_0.1-5.trusty_all.deb')
        self._run('echo percona-server-server-5.6 percona-server-server/root_password password asfdlkjh | debconf-set-selections')
        self._run('echo percona-server-server-5.6 percona-server-server/root_password_again password asfdlkjh | debconf-set-selections')
        self._run('apt-get update')
        self._run('apt-get install -y percona-server-server-5.6 percona-xtrabackup-24')
        self._run('service mysql stop')
        resource_path = self._get_backup_resource()
        archive_path = glob.glob('{}/mysql_backup/*.gz'.format(resource_path))
        backup_path = self.abs_path('backup')
        self._run('mkdir {}'.format(backup_path))
        self._run('zcat {} | xbstream -x'.format(archive_path[0]), cwd=backup_path, shell=True)
        self._run('innobackupex --apply-log {}'.format(backup_path), cwd=backup_path)
        self._run('rm -rf /var/lib/mysql')
        self._run('mkdir /var/lib/mysql')
        self._run('innobackupex --move-back {}'.format(backup_path), cwd=backup_path)
        self._run('rm -rf {}'.format(backup_path))
        self._run('chown -R mysql:mysql /var/lib/mysql')
        self._run('service mysql start')
        self._run(
            self.ctx[QueryParameter.name],
            reference_stdout='''Warning: Using a password on the command line interface can be insecure.
count(*) > 0
1
'''
        )

    def _run(self, command, cwd=None, reference_stdout=None, shell=False):
        logging.debug(command)
        if not shell:
            command = shlex.split(command)
        popen = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, cwd=cwd, shell=shell)
        stdout, stderr = popen.communicate()
        logging.error('stdout: %s', stdout)
        logging.error('stderr: %s', stderr)
        if popen.returncode:
            raise Exception("non zero return code")
        if reference_stdout is not None and stdout != reference_stdout:
            raise Exception('Bad stdout %s %s' % (reference_stdout, stdout))
