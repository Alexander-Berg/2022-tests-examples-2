import json
from collections import defaultdict

from sandbox.sdk2 import (
    ResourceData,
    parameters,
)
from sandbox.projects.common.yabs.server.util.general import check_tasks
from sandbox.projects.yabs.YabsYTBackupRestore import YabsYtBackupRestore
from sandbox.projects.yabs.base_bin_task import BaseBinTask
from sandbox.projects.yabs.prebilling_tests.resources import PrebillingBackup

DICTS = [
    '//home/yabs/dict/CaesarOrderInfo',
    '//home/yabs/dict/CaesarAutoBudgetOrder',
    '//home/yabs/dict/OrderStatCurDay',
    '//home/yabs/dict/logos/AdsCurrencyRates',
    '//home/yabs/dict/replica/Currency',
    '//home/yabs/dict/replica/AutoBudgetStopDays',
    '//home/yabs/dict/replica/AutobudgetOrderDailyLimits',
    '//home/yabs/dict/replica/AutoBudgetOrderWeeklyValues',
    '//home/yabs/dict/CaesarAutoBudgetOrderWithHistory',
    '//home/yabs/dict/replica/GoodEvent',
    '//home/yabs/dict/replica/GroupToOrderIndex',
    '//home/yabs/dict/replica/CaesarGroupToOrderIndex',
    '//home/yabs/dict/replica/TaxHistory',
    '//home/yabs/dict/replica/WideGoodEvent',
    '//home/yabs/dict/PrestablePrebillingAutoBudgetPeriodStat',
    '//home/yabs/dict/PrestablePrebillingAutoBudgetStatCurWeek',
    '//home/yabs/dict/PrestablePrebillingOrderStat',
    '//home/yabs/dict/PrestablePrebillingOrderStatCurDay',
    '//home/yabs/dict/PrestablePrebillingOrderStopDays',
    '//home/yabs/dict/PrestablePrebillingStat',
    '//home/yabs/dict/PrestableAutoBudgetStatExternal',
    '//home/yabs/dict/PrebillingGoodEvent'
]
RENAME = {"AutobudgetOrderDailyLimits": "AutoBudgetOrderDailyValues"}
PREFFIXES_TO_REMOVE = ['Prestable']


def remove_prefix_from_name(name):
    for prefix in PREFFIXES_TO_REMOVE:
        if name.startswith(prefix):
            return name[len(prefix):]
    return name


class PrebillingMakeBackup(BaseBinTask):
    class Parameters(BaseBinTask.Parameters):
        description = 'Backup YT tables'

        with BaseBinTask.Parameters.version_and_task_resource() as version_and_task_resource:
            resource_attrs = parameters.Dict('Filter resource by', default={'name': 'PrebillingB2B'})

        secret_name = parameters.YavSecret(
            'yav secret id',
            default='sec-01eqfz6a8j1rqs267tfn54hbg5'
        )
        yt_src_prebilling_clusters = parameters.String(
            'YT clusters',
            default='landau,bohr',
        )
        yt_src_cluster = parameters.String(
            'YT cluster',
            default='freud',
        )
        yt_dst_cluster = parameters.String(
            'YT dst cluster',
            default='freud',
        )
        backup_base = parameters.String(
            'Backup directory path',
            default='//home/yabs/dict/tmp/tmp_prebilling_b2b/b2b_backups',
        )
        log_dir = parameters.String(
            'Path to dir with logs',
            default='//home/antifraud/xurma/prebilling/preprod/input-logs-archive',
        )

        dict_pathes = parameters.List(
            'dict pathes for copy',
            default=DICTS,
        )

        result_attrs = parameters.Dict(
            'Result resource attributes',
            default={},
        )

    def get_all_logs_tables_name(self, ytc_src_prebilling_cluster):
        log_dir = self.Parameters.log_dir
        all_logs_names = ytc_src_prebilling_cluster.list(log_dir)
        logs_to_copy = defaultdict(str)
        logs_to_copy_pred = defaultdict(str)
        for log_name in all_logs_names:
            log_type = log_name.split('.')[-1]
            logs_to_copy_pred[log_type] = logs_to_copy[log_type]
            logs_to_copy[log_type] = log_name
        return [(log_name, 'batch-00000001.' + log_type_name) for log_type_name, log_name in logs_to_copy_pred.items()]

    def clone_table(self, yt_token, src_table_path, dst_table_path, ytc_src_prebilling_cluster, ytc_src, mode):
        if 'prestable' not in src_table_path.lower() and 'preprod' not in src_table_path.lower():
            if not ytc_src.exists(src_table_path):
                raise Exception("{} not exist on freud".format(src_table_path))
            src_cluster = self.Parameters.yt_src_cluster
        elif ytc_src_prebilling_cluster.exists(src_table_path):
            src_cluster = self.yt_src_prebilling_cluster
        else:
            raise Exception("Table {} not found".format(src_table_path))
        clone_task = YabsYtBackupRestore(
            parent=self,
            description="Prebilling b2b backup tables",
            src_cluster=src_cluster,
            dst_cluster=self.Parameters.yt_dst_cluster,
            tables_dict={src_table_path: dst_table_path},
            mode=mode,
            primary_medium='default',
            yt_vault_token=yt_token,
        ).enqueue()
        return clone_task

    def create_resource(self, backup_description):
        backup_resource = ResourceData(
            PrebillingBackup(
                self,
                description='Prebilling YT backup description',
                path='backup.json',
                **self.Parameters.result_attrs
            ),
        )
        backup_resource.path.write_bytes(json.dumps(backup_description))
        backup_resource.ready()

    def on_execute(self):
        import yt.wrapper as yt

        yt_token = self.Parameters.secret_name.data()['yt_token']

        ytc_src_prebilling_cluster = None
        max_num_logs_on_cluster = 0
        for cluster in self.Parameters.yt_src_prebilling_clusters.split(','):
            client = yt.YtClient(token=yt_token, proxy=cluster)
            num_logs = len(self.get_all_logs_tables_name(client))
            if max_num_logs_on_cluster < num_logs:
                max_num_logs_on_cluster = num_logs
                ytc_src_prebilling_cluster = client
                self.yt_src_prebilling_cluster = cluster

        ytc_src = yt.YtClient(token=yt_token, proxy=self.Parameters.yt_src_cluster)
        ytc_dst = yt.YtClient(token=yt_token, proxy=self.Parameters.yt_dst_cluster)
        dest_path = '{}/{}'.format(self.Parameters.backup_base, self.id)

        tasks = []
        backup_description = dict()
        with self.memoize_stage.create_children:
            ytc_dst.create('map_node', dest_path, recursive=True)
            dest_path = '{}/{}/logs'.format(self.Parameters.backup_base, self.id)
            ytc_dst.create('map_node', dest_path, recursive=True)
            for src_log_name, dst_log_name in self.get_all_logs_tables_name(ytc_src_prebilling_cluster):
                src_table_path = "{}/{}".format(self.Parameters.log_dir, src_log_name)
                dst_table_path = "{}/{}".format(dest_path, dst_log_name)
                tasks.append(self.clone_table(yt_token, src_table_path, dst_table_path, ytc_src_prebilling_cluster, ytc_src, 'transfer'))
                backup_description[dst_log_name] = dst_table_path
            dest_path = '{}/{}/dict'.format(self.Parameters.backup_base, self.id)
            ytc_dst.create('map_node', dest_path, recursive=True)
            for src_table_path in self.Parameters.dict_pathes:
                table = remove_prefix_from_name(src_table_path.split('/')[-1])
                if table in RENAME:
                    dst_table_path = "{}/{}".format(dest_path, RENAME[table])
                else:
                    dst_table_path = "{}/{}".format(dest_path, table)
                tasks.append(self.clone_table(yt_token, src_table_path, dst_table_path, ytc_src_prebilling_cluster, ytc_src, 'clone'))
                backup_description[table] = dst_table_path
            tasks = [task for task in tasks if task]
            old_versions = ytc_dst.list(self.Parameters.backup_base)
            old_versions.remove(str(self.id))
            for ver in old_versions:
                ytc_dst.remove('{}/{}'.format(self.Parameters.backup_base, ver), recursive=True, force=True)
            self.create_resource(backup_description)
            check_tasks(self, tasks, wait_all=True)
