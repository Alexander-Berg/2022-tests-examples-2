# coding=utf-8
from __future__ import unicode_literals

import logging
import os
import shutil
import tempfile
from datetime import datetime
from subprocess import Popen, PIPE

from sandbox import sdk2
from sandbox.projects.common import binary_task

from sandbox.projects.avia.base import AviaBaseTask

logger = logging.getLogger(__name__)

AVIA_SQL_SIZE_ROUGHLY = 11693982636
DEFAULT_TABLES_TO_SKIP = [
    'auth_group',
    'auth_group_permissions',
    'auth_message',
    'auth_permission',
    'auth_user',
    'auth_user_groups',
    'auth_user_user_permissions',
    'feature_flag_app__feature_flag',
    'feature_flag_app__service',
    'feature_flag_app__service_feature_flag_relation',
]


class AviaMysqlTestingDump(sdk2.Resource):
    releasable = False
    executable = False
    auto_backup = True


class AviaMysqlSyncTestingWithProd(binary_task.LastBinaryTaskRelease, AviaBaseTask):
    class Requirements(sdk2.Requirements):
        # configure this for your task, the more accurate - the better
        cores = 1  # exactly 1 core
        disk_space = 4096  # 4096 Megs
        ram = 128  # 128 Megs or less

        # https://wiki.yandex-team.ru/sandbox/cookbook/#use-custom-lxc-image
        # LXC_IMAGE avia-lxc-mysql-ops
        container_resource = 1718293390

        class Caches(sdk2.Requirements.Caches):
            pass  # means that task do not use any shared caches

    class Parameters(sdk2.Parameters):
        # binary task release parameters
        ext_params = binary_task.binary_release_parameters(stable=True)

        with sdk2.parameters.Group('Db testing parameters') as db_testing_params:
            mysql_testing_host = sdk2.parameters.String('Mysql testing host name', required=True,
                                                        default='c-mdbs73ogk0n953v775se.rw.db.yandex.net')
            mysql_testing_port = sdk2.parameters.String('Mysql testing port', required=True, default=3306)
            mysql_testing_user = sdk2.parameters.String('Mysql testing user', default='avia', required=True)
            mysql_testing_dbname = sdk2.parameters.String('Mysql testing dbname', default='avia', required=True)
            mysql_testing_password_vault = sdk2.parameters.YavSecret('Mysql testing password', required=True,
                                                                     default='sec-01dvzx8m6rcvpb6dz2hcagpvvn')
        with sdk2.parameters.Group('Db production parameters') as db_prod_params:
            mysql_prod_host = sdk2.parameters.String('Mysql production host name', required=True,
                                                     default='c-mdbtlvdfboec7qou9je5.ro.db.yandex.net')
            mysql_prod_port = sdk2.parameters.String('Mysql production port', required=True, default=3306)
            mysql_prod_user = sdk2.parameters.String('Mysql production user', default='avia', required=True)
            mysql_prod_dbname = sdk2.parameters.String('Mysql production dbname', default='avia', required=True)
            mysql_prod_password_vault = sdk2.parameters.YavSecret('Mysql production password', required=True,
                                                                  default='sec-01dvzx5stx4qtdjmd4jcv8dvzy')
            mysql_prod_skip_tables = sdk2.parameters.List('Do not copy this tables from production to testing',
                                                          required=True, default=DEFAULT_TABLES_TO_SKIP)

    def on_execute(self):
        logger.info('Make testing dump and make resource from it')
        self.make_resource_from_avia_testing_db()
        logger.info('Done')

        logger.info('Make prod dump and load it into testing')
        self.load_prod_dump_into_testing()
        logger.info('Done')

    def make_resource_from_avia_testing_db(self):
        dump_filename = 'avia-testing-dump.sql.gz'
        cwd = os.getcwd()
        dump_file = os.path.join(cwd, dump_filename)
        logger.info('Avia testing dump -> %s', dump_file)
        with open(dump_file, 'wb') as f:
            make_avia_dump(
                f,
                host=self.Parameters.mysql_testing_host,
                port=self.Parameters.mysql_testing_port,
                user=self.Parameters.mysql_testing_user,
                password=self.Parameters.mysql_testing_password_vault.data()['password'],
                dbname=self.Parameters.mysql_testing_dbname,
            )

        resource = AviaMysqlTestingDump(
            self,
            description='Avia mysql testing dump {}'.format(datetime.now().strftime('%Y-%m-%d %H:%M:%S')),
            path=dump_file,
            ttl=120,
        )

        resource_data = sdk2.ResourceData(resource)
        resource_data.ready()
        self.set_info("""<a href="https://sandbox.yandex-team.ru/resource/{r.id}/view">{r.description}</a>""".format(
            r=resource), do_escape=False)

    def load_prod_dump_into_testing(self):
        dump_filename = 'avia-prod-dump.sql.gz'

        tmpdir = None
        try:
            tmpdir = tempfile.mkdtemp()
            dump_file = os.path.join(tmpdir, dump_filename)
            logger.info('Avia production dump -> %s', dump_file)
            with open(dump_file, 'wb') as f:
                make_avia_dump(
                    f,
                    host=self.Parameters.mysql_prod_host,
                    port=self.Parameters.mysql_prod_port,
                    user=self.Parameters.mysql_prod_user,
                    password=self.Parameters.mysql_prod_password_vault.data()['password'],
                    dbname=self.Parameters.mysql_prod_dbname,
                    tables_to_skip=self.Parameters.mysql_prod_skip_tables,
                )
            logger.info('Load prod dump %s into testing', dump_file)
            load_avia_dump(
                dump_file,
                host=self.Parameters.mysql_testing_host,
                port=self.Parameters.mysql_testing_port,
                user=self.Parameters.mysql_testing_user,
                password=self.Parameters.mysql_testing_password_vault.data()['password'],
                dbname=self.Parameters.mysql_testing_dbname,
            )
        finally:
            if tmpdir:
                shutil.rmtree(tmpdir)


def make_avia_dump(out_file, host, port, user, password, dbname, tables_to_skip=()):
    skip_args = ['--ignore-table={}.{}'.format(dbname, table) for table in tables_to_skip]
    p0 = Popen(
        [
            'mysqldump',
            '--host={}'.format(host),
            '--port={}'.format(port),
            '--user={}'.format(user),
            '--password={}'.format(password),
            '--set_gtid_purged=OFF',
            '--max_allowed_packet=2147483648',
        ] + skip_args + [
            dbname,
        ],
        stdin=PIPE,
        stdout=PIPE,
    )
    p1 = Popen(
        ['pv', '-f', '-i30', '-p', '-t', '-e', '-s', str(AVIA_SQL_SIZE_ROUGHLY)],  # -f to force output
        stdin=p0.stdout,
        stdout=PIPE,
        stderr=PIPE,
        universal_newlines=True,  # for parsing pv output
    )
    p2 = Popen(
        ['gzip'],
        stdout=out_file,
        stdin=p1.stdout
    )
    for line in p1.stderr:
        logger.info(line.strip())


def load_avia_dump(dump_file, host, port, user, password, dbname):
    p0 = Popen(
        ['pv', '-f', '-i30', '-p', '-t', '-e', dump_file],  # -f to force output
        stdout=PIPE,
        stderr=PIPE,
        universal_newlines=True,  # for parsing pv output
    )
    p1 = Popen(
        ['gunzip'],
        stdout=PIPE,
        stdin=p0.stdout,
    )
    p2 = Popen(
        [
            'mysql',
            '--max_allowed_packet=2147483648',
            '--host={}'.format(host),
            '--port={}'.format(port),
            '--user={}'.format(user),
            '--password={}'.format(password),
            dbname
        ],
        stdout=PIPE,
        stdin=p1.stdout
    )
    for line in p0.stderr:
        logger.info(line.strip())
