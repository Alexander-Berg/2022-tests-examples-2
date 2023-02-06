import shutil
import json
import time
import os

from sandbox import sdk2
from sandbox.projects.yabs.base_bin_task import BaseBinTask
from sandbox.sdk2.helpers import subprocess as sp
from sandbox.common.types.resource import State
from sandbox.projects.common.rem import REMRunner
from sandbox.projects.common.userdata import rem_client
from sandbox.projects.yabs.prebilling_tests.resources import PrebillingBin, PrebillingBackup


NUM_RETRIES = 10
RETRY_TIME = 60
SLEEP_TIME = 60


TABLES_WITH_NOW_UPDATE = [
    "AutoBudgetPeriodStatTable",
    "AutoBudgetStatCurWeekTable",
    "OrderStatCurDayTable",
    "OrderStatTable",
    "OrderStopDaysTable",
    "PrebillingStat",
    "PrebillingStatTable"
]

TABLES_ONLY_FOR_READ = [
    "Currency",
    "CurrencyRates",
    "GoodEvent",
    "TaxHistory",
    "PrebillingGoodEvent",
    "WideGoodEvent",
]

SMALL_TABLES = [
    "Currency",
    "PrebillingGoodEvent",
    "TaxHistory",
    "GoodEvent",
    "WideGoodEvent",
    "CurrencyRates",
    "AutoBudgetStopDays",
    "PrebillingAutoBudgetStatCurWeek",
    "AutoBudgetOrder",
    "PrebillingAutoBudgetPeriodStat",
    "OrderStatCurDay"
]

PACKETS_REGEX_TO_DELETE = [
    ".*00000002.*",
    ".*00000003.*",
    ".*ScheduleNextBatchProcessing-00000001.*",
    ".*CompleteScheduling-00000001.*"]


def check_status_is_unmount(ytc, dict_path):
    return ytc.get("{}/@tablet_state".format(dict_path)) == "unmounted"


def unmount_all_dicts(ytc, path_to_dicts):
    dict_pathes = []
    for dict_name in ytc.list(path_to_dicts):
        if dict_name != "BilledByRtPrebillingTest":
            dict_path = "{}/{}".format(path_to_dicts, dict_name)
            if not check_status_is_unmount(ytc, dict_path):
                dict_pathes.append(dict_path)
    for iter_name in range(NUM_RETRIES):
        for dict_path in dict_pathes:
            try:
                ytc.unmount_table(dict_path)
            except:
                time.sleep(RETRY_TIME)
        dict_pathes = [dict_path for dict_path in dict_pathes if not check_status_is_unmount(ytc, dict_path)]
        if len(dict_pathes) == 0:
            return
    raise Exception("{} couldn't be unmounted".format(str(dict_pathes)))


def run_bin(task, cmd, env):
    cmd = cmd.split(' ')
    with sdk2.helpers.ProcessLog(task, logger='prebillinng_b2b') as pl:
        sp.check_call(cmd, stdout=pl.stdout, stderr=pl.stderr, env=env)


def reshard_table(ytc, table_path, num_tablets=30):
    from yt.wrapper import yson
    ytc.set(table_path + '/@tablet_balancer_config', {"enable_auto_reshard": False, "enable_auto_tablet_move": True})
    pivot_keys = []
    pivot_keys.append([])
    for i in range(num_tablets):
        pivot_keys.append([yson.YsonUint64(2**64 / num_tablets * i)])
        ytc.reshard_table(table_path, pivot_keys=pivot_keys)


def copy_dicts(ytc, src_path_to_dicts, dst_path_to_dicts):
    unmount_all_dicts(ytc, src_path_to_dicts)
    for dict_name in ytc.list(src_path_to_dicts):
        src_path_to_dict = "{}/{}".format(src_path_to_dicts, dict_name)
        if dict_name not in set(TABLES_ONLY_FOR_READ):
            dst_path_to_dict = "{}/{}Test".format(dst_path_to_dicts, dict_name)
        else:
            dst_path_to_dict = "{}/{}".format(dst_path_to_dicts, dict_name)
        ytc.copy(src_path_to_dict, dst_path_to_dict)
        if ytc.get(dst_path_to_dict + '/@primary_medium') == 'default':
            ytc.set(dst_path_to_dict + '/@media/ssd_blobs', {'replication_factor': 3, 'data_parts_only': False})
            ytc.set(dst_path_to_dict + '/@primary_medium', 'ssd_blobs')
        if src_path_to_dict.split('/')[-1] not in SMALL_TABLES:
            reshard_table(ytc, dst_path_to_dict)
            ytc.set_attribute(dst_path_to_dict, "forced_compaction_revision", ytc.get_attribute(dst_path_to_dict, "revision"))
            ytc.set_attribute(dst_path_to_dict, "forced_compaction_revision", ytc.get_attribute(dst_path_to_dict, "revision"))
        ytc.mount_table(dst_path_to_dict)


def copy_logs(ytc, src_dir, dst_dir):
    for log_name in ytc.list(src_dir):
        ytc.copy("{}/{}".format(src_dir, log_name), "{}/{}".format(dst_dir, log_name))
        ytc.set_attribute("{}/{}".format(dst_dir, log_name), "batch_id", 1)


def flush_dicts(ytc, path_to_dicts):
    unmount_all_dicts(ytc, path_to_dicts)
    for dict_name in ytc.list(path_to_dicts):
        if dict_name != "BilledByRtPrebillingTest":
            path_to_dict = "{}/{}".format(path_to_dicts, dict_name)
            ytc.set(path_to_dict + "/@enable_dynamic_store_read", False)
            ytc.set(path_to_dict + "/@enable_dynamic_store_read", True)
            ytc.mount_table(path_to_dict)


class PrebillingExecuter(BaseBinTask):
    class Parameters(BaseBinTask.Parameters):
        description = 'Execute prebilling for b2b'

        with BaseBinTask.Parameters.version_and_task_resource() as version_and_task_resource:
            resource_attrs = sdk2.parameters.Dict('Filter resource by', default={'name': 'PrebillingB2B'})

        binary_resource = sdk2.parameters.LastReleasedResource(
            'PrebillingResorses',
            resource_type=PrebillingBin,
            state=State.READY,
            required=True
        )

        backup_resource = sdk2.parameters.Resource(
            'Backup resource',
            resource_type=PrebillingBackup,
            required=True
        )

        cluster = sdk2.parameters.String(
            'execution cluster',
            default='freud'
        )

        secret_name = sdk2.parameters.YavSecret(
            'yav secret id',
            default='sec-01eqfz6a8j1rqs267tfn54hbg5'
        )
        expiration_time = sdk2.parameters.Integer(
            'expiration time for temp tables in days (default 12)',
            default=12
        )

        path_to_backup = sdk2.parameters.String(
            'yt path for b2b exec',
            default='//home/yabs/dict/tmp/tmp_prebilling_b2b/b2b_backups'
        )

        exec_b2b_dir = sdk2.parameters.String(
            'yt path for b2b exec',
            default='//home/yabs/dict/tmp/tmp_prebilling_b2b/b2b'
        )

    def set_apply_batch_id_now_update(self, ytc):
        for table in TABLES_WITH_NOW_UPDATE:
            ytc.create('int64_node', self.dst_dir + "/prebilling/b2b/state/applied_tables/{}/max_applied_batch_id".format(table), recursive=True)
            ytc.create('boolean_node', self.dst_dir + "/prebilling/b2b/state/applied_tables/{}/now_update".format(table), recursive=True)

    def _setup_rem_server(self, env):
        os.mkdir(self.working_dir + "/rem")
        rem_rev = "2972181"
        self.rem_runner = REMRunner(
            arcadia_root='svn+ssh://arcadia.yandex.ru/arc/trunk/arcadia@{}'.format(rem_rev),
            root_dir=self.working_dir + "/rem",
            log_dir='rem-server',
            environ=env,
        )

        self.rem_runner.setup_server()
        self.rem_client = rem_client.RemClient(self.rem_runner.rem_url, self.rem_runner.rem_tool_path())

    def dump_rem_status(self):
        log_dir = 'rem-server'
        if not os.path.exists(log_dir):
            os.mkdir(log_dir)
        self.rem_client.dump_history(log_dir, self.working_dir)

    def rewrite_xurma_json(self, input_file, output_file, yt_working_dir_path):
        with open(output_file, 'w') as fout:
            for line in open(input_file, 'r'):
                if '\"ProjectRoot\"' in line:
                    fout.write("    \"ProjectRoot\": \"{}\",\n".format(yt_working_dir_path))
                else:
                    fout.write(line.replace('ssd_blobs_xurma', 'default'))

    def rewrite_paths_json(self, input_file, output_file, working_dir, rem_path, rem_url):
        with open(output_file, 'w') as fout:
            for line in open(input_file, 'r'):
                if '\"RemPath\"' in line:
                    fout.write("    \"RemPath\": \"{}\",\n".format(rem_path))
                elif '\"RemServer\"' in line:
                    fout.write("    \"RemServer\": \"{}\",\n".format(rem_url))
                else:
                    if 'sandbox_base_dir_path' in line:
                        line = line.format(sandbox_base_dir_path=working_dir)
                    fout.write(line)

    def prepare_configs(self, bin_res_path):
        os.mkdir('configs')
        output_path = "configs/xurma.json"
        path_to_xurma_json = str(bin_res_path) + "/xurma.json"
        self.rewrite_xurma_json(path_to_xurma_json, output_path, self.dst_dir)
        output_path = "configs/paths.json"
        path_to_paths_json = str(bin_res_path) + "/paths.json"
        self.rewrite_paths_json(path_to_paths_json, output_path, self.working_dir, self.working_dir + "/rem/rem", self.rem_runner.rem_url)
        shutil.copytree(str(bin_res_path) + "/prebilling", "configs/prebilling")
        shutil.copytree(str(bin_res_path) + "/send_metrics/configs", "configs/send_metrics_configs")
        shutil.copytree(str(bin_res_path) + "/send_metrics_solomon/configs", "configs/send_metrics_solomon_configs")
        os.chmod("configs/prebilling", 0o0777)
        os.chmod("configs/prebilling/sensitive", 0o0777)
        os.mkdir("configs/prebilling/models")
        shutil.move("configs/prebilling/sensitive/combos.handcrafted.json", "configs/prebilling/combos.json")
        shutil.move("configs/prebilling/sensitive/rules.handcrafted.json", "configs/prebilling/rules.json")
        shutil.move("configs/prebilling/sensitive/features.handcrafted.json", "configs/prebilling/features.json")

    def run_xurma(self, env):
        cmd = "./bin/xurma_admin -c ./configs/paths.json -g prebilling -p b2b add-cluster {} --role standby".format(self.cluster)
        run_bin(self, cmd, env)
        cmd = "./bin/xurma_admin -c ./configs/paths.json -g prebilling -p b2b enable-cluster {}".format(self.cluster)
        run_bin(self, cmd, env)
        cmd = "./bin/xurma_admin -c ./configs/paths.json -g prebilling -p b2b init-profile --force --batch-id 000"
        run_bin(self, cmd, env)
        cmd = "./bin/xurma_admin -c ./configs/paths.json -g prebilling -p b2b init-reduces --cluster {} --batch-id 000 --no-data-transfer *".format(self.cluster)
        run_bin(self, cmd, env)
        cmd = "./bin/xurma_admin -c ./configs/paths.json -g prebilling -p b2b switch-leader --force {}".format(self.cluster)
        run_bin(self, cmd, env)
        time.sleep(SLEEP_TIME)
        conn = self.rem_client.connector()
        queue = conn.Queue("xurma-prebilling-b2b-{}".format(self.cluster))
        for regex in PACKETS_REGEX_TO_DELETE:
            for pack in queue.ListPackets("all", name_regex=regex):
                pack.Delete()
        cmd = "./bin/xurma_admin -c ./configs/paths.json -g prebilling -p b2b execute LbYtTableReady -v Cluster {}".format(self.cluster)
        run_bin(self, cmd, env)

    def on_execute(self):
        import yalibrary.upload.uploader as uploader
        import yt.wrapper as yt
        yt_token = self.Parameters.secret_name.data()['yt_token']
        sandbox_token = self.Parameters.secret_name.data()['sandbox_token']
        self.working_dir = os.path.abspath(os.path.curdir)
        env = {'YT_TOKEN': yt_token}
        self._setup_rem_server(env)

        self.cluster = self.Parameters.cluster
        ytc = yt.YtClient(token=yt_token, proxy=self.cluster)
        path_to_backup_dir = self.Parameters.path_to_backup
        backup_dir_ver = ytc.list(path_to_backup_dir)

        if len(backup_dir_ver) == 1:
            backup_path = '{}/{}'.format(path_to_backup_dir, backup_dir_ver[0])
        else:
            raise Exception("Backup is not ready now")

        backup_file = sdk2.ResourceData(self.Parameters.backup_resource)
        with open(str(backup_file.path), 'r') as f:
            backup_data = json.load(f)
        for key in backup_data:
            if not ytc.exists(backup_data[key]):
                raise Exception("Backup is not ready now")

        self.dst_dir = "{}/{}".format(self.Parameters.exec_b2b_dir, self.id)
        if ytc.exists(self.dst_dir):
            ytc.remove(self.dst_dir, recursive=True, force=True)
        ytc.create('map_node', self.dst_dir, recursive=True)
        ytc.create('map_node', self.dst_dir + "/prebilling/b2b/input-logs", recursive=True)
        copy_logs(ytc, backup_path + "/logs", self.dst_dir + "/prebilling/b2b/input-logs")
        ytc.create('map_node', self.dst_dir + "/dict", recursive=True)
        copy_dicts(ytc, backup_path + "/dict", self.dst_dir + "/dict")
        ytc.create("table", self.dst_dir + "/dict/BilledByRtPrebillingTest")
        ytc.write_table(self.dst_dir + "/dict/BilledByRtPrebillingTest", [{"Orders": "", "Permille": 0}])
        ytc.create('int64_node', self.dst_dir + "/prebilling/b2b/state/working_permille", recursive=True)
        ytc.set(self.dst_dir + "/prebilling/b2b/state/working_permille", 1000)
        self.set_apply_batch_id_now_update(ytc)
        ytc.create('map_node', self.dst_dir + "/prebilling/b2b/history", recursive=True)

        f = open('.deploy.lock', 'w')
        f.close()
        os.mkdir('secrets')
        f = open('secrets/robot-xurma-pb-solomon-token', 'w')
        f.close()
        f = open('secrets/tvm-secret', 'w')
        f.close()
        with open('secrets/robot-xurma-pb-token', 'w') as f:
            f.write(yt_token)

        bin_res = sdk2.ResourceData(self.Parameters.binary_resource)
        self.prepare_configs(bin_res.path)
        shutil.copytree(str(bin_res.path), "bin")

        try:
            self.run_xurma(env)
            self.rem_client.wait_all_packets()
        except Exception as ex:
            res_id = uploader.do(paths=["rem"], ttl=14, sandbox_token=sandbox_token, resource_owner="YABS-YTSTAT")
            raise Exception("Rem failed. See logs at resourse {}. Exception was {}".format(res_id, str(ex)))

        flush_dicts(ytc, self.dst_dir + "/dict")
