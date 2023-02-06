import datetime
import json
import time

from dateutil.tz import tzlocal

from sandbox import sdk2
from sandbox.projects.autobudget.resources import YabsAutoBudgetDailyLimitsBackup
from sandbox.projects.autobudget.resources import YabsAutoBudgetDailyLimitsExecuterBin
from sandbox.projects.yabs.base_bin_task import BaseBinTask
from sandbox.sdk2.helpers import subprocess as sp
from sandbox.common.types.resource import State


class AutoBudgetDailyLimitsExecuter(BaseBinTask):
    class Parameters(BaseBinTask.Parameters):
        description = 'Execute dynamic daily calculator for b2b'

        with BaseBinTask.Parameters.version_and_task_resource() as version_and_task_resource:
            resource_attrs = sdk2.parameters.Dict('Filter resource by', default={'name': 'AutoBudgetDailyLimitsB2B'})

        binary_resource = sdk2.parameters.LastReleasedResource(
            'Auto budget daily limits executer binary',
            resource_type=YabsAutoBudgetDailyLimitsExecuterBin,
            state=State.READY,
            required=True
        )
        cluster = sdk2.parameters.String(
            'cluster with source tables',
            default='hahn'
        )
        secret_name = sdk2.parameters.YavSecret(
            'yav secret id',
            default='sec-01dg9pn791asxk9xpagtqx2q2f'
        )
        expiration_time = sdk2.parameters.Integer(
            'expiration time for temp tables in days (default 12)',
            default=12
        )

        backup_resource = sdk2.parameters.LastReleasedResource(
            'Backup resource',
            resource_type=YabsAutoBudgetDailyLimitsBackup,
            state=State.READY,
        )
        output_prefix = sdk2.parameters.String(
            'yt path prefix for output',
            default='//home/autobudget/dynamic_daily_limits/b2b/executer'
        )

    def on_execute(self):
        import yt.wrapper as yt

        bin_res = sdk2.ResourceData(self.Parameters.binary_resource)
        output_path = '{}/{}'.format(self.Parameters.output_prefix, self.id)

        yt_token = self.Parameters.secret_name.data()['token']
        ytc = yt.YtClient(token=yt_token, proxy='hahn')
        ytc.remove(output_path, recursive=True, force=True)
        ytc.create('map_node', output_path, recursive=True)

        ts = datetime.datetime.now(tzlocal())
        ts += datetime.timedelta(days=self.Parameters.expiration_time)
        ytc.set_attribute(output_path, 'expiration_time', ts.isoformat())

        backup_file = sdk2.ResourceData(self.Parameters.backup_resource)
        with open(str(backup_file.path), 'r') as f:
            backup_data = json.load(f)

        now_timestamp = backup_data.get(
            'now_timestamp', int(time.mktime(self.Parameters.backup_resource.created.timetuple())))

        cmd = [
            str(bin_res.path),
            '--cluster={}'.format(self.Parameters.cluster),
            '--result-cluster=_',
            '--orders-table={}'.format(backup_data['orders_table']),
            '--ab-orders-table={}'.format(backup_data['ab_orders_table']),
            '--time-targets-table={}'.format(backup_data['time_targets_table']),
            '--holidays-table={}'.format(backup_data['holidays_table']),
            '--order-daily-stat={}'.format(backup_data['ab_orders_daily_spent']),
            '--order-period-stat={}'.format(backup_data['ab_orders_period_spent']),
            '--ab-orders-daily-limits-table={}'.format(backup_data['ab_orders_daily_limits_table']),
            '--week-history-table={}'.format(backup_data['orders_weekly_limits_history_table']),
            '--ab-coeffs-table={}'.format(backup_data['ab_coeffs_table']),
            '--expiration-time={}'.format(self.Parameters.expiration_time),

            '--orders-limits-tmp-table={}/OrdersWithLimits'.format(output_path),
            '--plain-orders-tmp-table={}/PlainOrders'.format(output_path),
            '--plain-orders-targets-tmp-table={}/PlainOrdersTargets'.format(output_path),
            '--orders-targets-tmp-table={}/OrdersTargets'.format(output_path),
            '--orders-daily-limits-tmp-table={}/OrdersDailyLimits'.format(output_path),
            '--orders-weekly-limits-tmp-table={}/OrdersWeeklyLimits'.format(output_path),

            '--current-time={}'.format(now_timestamp),

            '--results-appending-disable',
        ]

        env = {'YT_TOKEN': yt_token}

        with sdk2.helpers.ProcessLog(self, logger='ab_daily_limits_calc') as pl:
            sp.check_call(cmd, stdout=pl.stdout, stderr=pl.stderr, env=env)
