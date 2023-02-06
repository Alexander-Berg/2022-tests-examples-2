from __future__ import print_function

import datetime
import json
import logging
import re
import time

from sandbox.sdk2 import (
    Task,
    Resource,
    ResourceData,
    parameters,
)
from sandbox.projects.yabs.master_report_tests.resources import (
    YabsMasterReportBackupDescription,
    YabsMasterReportSpec,
)
from sandbox.projects.yabs.base_bin_task import BaseBinTask


class YabsMasterReportBackupData(BaseBinTask):
    '''Backup clickhouse data for B2B tests'''

    class Requirements(Task.Requirements):
        cores = 1
        ram = 4096
        disk_space = 4096

        class Caches(Task.Requirements.Caches):
            pass

    class Parameters(BaseBinTask.Parameters):
        description = 'Backup clickhouse data for B2B tests'

        with BaseBinTask.Parameters.version_and_task_resource() as version_and_task_resource:
            resource_attrs = parameters.Dict('Filter resource by', default={'name': 'YabsMasterReportTests'})

        with parameters.Group('Backup') as backup_params:
            days_period = parameters.Integer(
                'Number of days to backup',
                default=3,
                required=True,
            )
            distributed_host = parameters.String(
                'Distributed clickhouse host',
                default='bsclickhouse.yabs.yandex.ru',
                required=True,
            )
            src_password_secret = parameters.YavSecret(
                'Yav secret with readonly passwords for prod clickhouse',
                default='sec-01em26ng6brqy0g5e71233zcgm',
                required=True,
            )
            src_table = parameters.String(
                'Table to backup',
                default='BackupMasterReportStat',
                required=True,
            )
            src_cluster = parameters.String(
                'Source ClickHouse cluster',
                default='dom',
                required=True,
            )
            dst_hosts = parameters.List(
                'Testing hosts',
                default=[
                    'bsfastexport-b2b01i.yabs.yandex.ru',
                    'bsfastexport-b2b01e.yabs.yandex.ru'
                ],
                required=True,
            )
            delete_tables = parameters.Bool(
                'Delete old tables',
                default=True,
            )
            dst_password_secret = parameters.YavSecret(
                'Yav secret with passwords for testing clickhouse',
                default='sec-01dkepv33bbw2xb0y6ebf556qz',
                required=True,
            )

        with parameters.Group('Advanced') as advanced_params:
            chunk_size = parameters.Integer(
                'Insert chunk size',
                default=5000000,
                required=True,
            )
            retries = parameters.Integer(
                'Retries per insert',
                default=5,
                required=True,
            )

    def create_resource(self, data):
        backup_resource = ResourceData(
            YabsMasterReportBackupDescription(
                self,
                description='Master report backup description',
                path='backup.json',
            ),
        )
        backup_resource.path.write_bytes(json.dumps(data))
        backup_resource.ready()

    @staticmethod
    def remote_client(host):
        from clickhouse_driver import Client as ClickHouseClient

        return ClickHouseClient(
            host=host,
            user='remote',
            password='',
            database='system'
        )

    @staticmethod
    def cluster_client(host, port, user, password):
        from clickhouse_driver import Client as ClickHouseClient

        if port == 9000:
            return YabsMasterReportBackupData.remote_client(host)
        else:
            return ClickHouseClient(
                host=host,
                port=port,
                user=user,
                password=password,
                database='system',
                secure=True,
                verify=False,
            )

    def get_table_def(self, client, table):
        query = 'SHOW CREATE TABLE stat.' + table
        create_query = client.execute(query)[0][0]
        create_query = create_query.replace(table, self.dst_table) \
                                   .replace(self.Parameters.src_cluster, 'master_report')
        create_query = re.sub(r'\bMasterReportStat\b', self.dst_table, create_query)
        return re.sub(r', dictGetUInt8\(.*\)\)$', ')', create_query)

    def get_cluster_table_def(self, dist_client):
        from yabs.stat.infra.clickhouse.lib import get_shards_for_cluster

        src_pass = self.Parameters.src_password_secret.data().get('distributed')
        for shard in get_shards_for_cluster(dist_client, self.Parameters.src_cluster).values():
            for host, port in shard:
                try:
                    client = self.cluster_client(host, port, 'distributed', src_pass)
                    return self.get_table_def(client, 'MasterReportStat')
                except Exception as e:
                    logging.warn('Failed to select table definition from host %s, port %s: %s', host, port, e)
        raise Exception('Failed to select table definition')

    def get_last_testenv_table(self):
        if not self.Parameters.delete_tables:
            return None

        spec = Resource.find(
            resource_type=YabsMasterReportSpec,
            attrs={'for_testenv': 'True'}
        ).order(-Resource.id).first()

        if not spec:
            logging.info('Last testenv resource not found')
            return None
        with open(str(ResourceData(spec).path), 'r') as f:
            backup_id = json.load(f)['backup']

        backup_res = Resource.find(id=backup_id).first()
        with open(str(ResourceData(backup_res).path), 'r') as f:
            table = json.load(f)['table']
        logging.info('Last table is %s', table)

        return table

    def delete_old_tables(self, client, last_table):
        res = client.execute("SHOW TABLES FROM stat LIKE '%MasterReport%'")
        tables = [r[0] for r in res]
        for table in tables:
            if table not in (last_table, self.dst_table):
                logging.info('Deleting table %s', table)
                client.execute('DROP TABLE stat.{}'.format(table))

    def create_and_delete_tables(self):
        from yabs.stat.infra.clickhouse.lib import get_shards_for_cluster

        src_client = self.remote_client(self.Parameters.distributed_host)
        dist_query = self.get_table_def(src_client, self.Parameters.src_table)
        cluster_query = self.get_cluster_table_def(src_client)
        last_table = self.get_last_testenv_table()

        logging.info('Distributed table: %s', dist_query)
        logging.info('Cluster table: %s', cluster_query)

        dst_pass = self.Parameters.dst_password_secret.data().get('sbyt_rw')
        for dist_host in self.Parameters.dst_hosts:
            dist_client = self.remote_client(dist_host)
            dist_client.execute(dist_query)

            if self.Parameters.delete_tables:
                logging.info('Deleting old tables on %s', dist_host)
                self.delete_old_tables(dist_client, last_table)

            # testing hosts have only one shard
            for host, port in get_shards_for_cluster(dist_client, 'master_report')[0]:
                client = self.cluster_client(host, port, 'sbyt_rw', dst_pass)
                client.execute(cluster_query)

                if self.Parameters.delete_tables:
                    logging.info('Deleting old tables on %s:%s', host, port)
                    self.delete_old_tables(client, last_table)

    def wait_parts(self, client):
        query = '''
        select max(part_cnt) as value
            from (
                 select
                    partition,
                    count(*) as part_cnt
                 from system.parts
                 where active and database = 'stat' and table='{}'
                 group by partition
            ) as sq
        '''.format(self.dst_table)
        val = client.execute(query)[0][0]
        while val > 400:
            logging.info('Too many parts: %s, waiting', val)
            time.sleep(30)
            val = client.execute(query)[0][0]

    def chunks_generator(self, src_client, src_table, start_date, end_date):
        query = '''
            select EventDate, OrderID, count(*)
            from stat.{}
            where EventDate >= '{}' and EventDate < '{}'
            group by EventDate, OrderID
            order by EventDate, OrderID
        '''.format(src_table, start_date, end_date)
        settings = {'max_block_size': 100000}
        counters = src_client.execute(query, settings=settings)

        cur_rows = 0
        cur_date = ''
        order_from, order_to = 0, 0
        for row in counters:
            if cur_rows > 0 and (cur_rows + row[2] > self.Parameters.chunk_size or row[0] != cur_date):
                yield cur_date, order_from, order_to
                order_from = row[1]
                cur_rows = 0

            cur_date = row[0]
            order_to = row[1]
            cur_rows += row[2]

        if cur_rows > 0:
            yield cur_date, order_from, order_to

    def copy_chunk(self, src_host, src_table, dst_client, date, order_from, order_to, do_check):
        query = '''
            insert into stat.{dst_table}
            select *
            from remote('{host}:9000', stat, {src_table}, 'remote')
            where EventDate = '{date}' and OrderID >= {order_from} and OrderID <= {order_to}
        '''.format(
            dst_table=self.dst_table,
            host=src_host,
            src_table=src_table,
            date=date,
            order_from=order_from,
            order_to=order_to,
        )
        if not do_check:
            query += "limit 100000"
        dst_client.execute(query)

    def do_copy(self, src_host, src_table, dst_host_distr, start_date, end_date, do_check):
        from yabs.stat.infra.clickhouse.lib import get_shards_for_cluster

        dst_client_distr = self.remote_client(dst_host_distr)
        dst_shard = get_shards_for_cluster(dst_client_distr, 'master_report')[0]
        dst_pass = self.Parameters.dst_password_secret.data().get('sbyt_rw')
        src_client = self.remote_client(src_host)

        for chunk in self.chunks_generator(src_client, src_table, start_date, end_date):
            date, order_from, order_to = chunk

            logging.info('Copying day %s, orders %s - %s', date, order_from, order_to)
            success = False
            for host, port in dst_shard:
                try:
                    dst_client = self.cluster_client(host, port, 'sbyt_rw', dst_pass)
                    self.wait_parts(dst_client)
                    self.copy_chunk(src_host, src_table, dst_client, date, order_from, order_to, do_check)
                    success = True
                    break
                except Exception as e:
                    logging.warning('Failed to copy chunk, error: %s', e)

            if not success and do_check:
                raise Exception('Failed to copy chunk')

        if do_check:
            query = 'select sum(Cost), sum(Shows) from stat.{}'.format(self.dst_table)
            src_client = self.remote_client(src_host)
            assert src_client.execute(query) == dst_client.execute(query)

    def on_execute(self):
        today = datetime.date.today()
        start_date = today - datetime.timedelta(days=self.Parameters.days_period)
        start_str = start_date.isoformat()
        end_str = today.isoformat()

        self.dst_table = self.Parameters.src_table + str(self.id)
        self.create_and_delete_tables()

        all_hosts = [self.Parameters.distributed_host] + self.Parameters.dst_hosts

        for idx in range(1, len(all_hosts)):
            logging.info('Copying from %s to %s', all_hosts[idx - 1], all_hosts[idx])
            if idx == 1:
                src_table = self.Parameters.src_table
            else:
                src_table = self.dst_table

            self.do_copy(all_hosts[idx - 1], src_table, all_hosts[idx], start_str, end_str, idx != 1)

        self.create_resource({'table': self.dst_table, 'start_date': start_str, 'end_date': end_str})
