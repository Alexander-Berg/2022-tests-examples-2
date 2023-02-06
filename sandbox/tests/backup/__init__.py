from __future__ import print_function

import datetime
import json
import time

from dateutil.tz import tzlocal

from sandbox.sdk2 import (
    ResourceData,
    parameters,
    Requirements
)
from sandbox.projects.autobudget.resources import YabsAutoBudgetDailyLimitsBackup
from sandbox.projects.yabs.base_bin_task import BaseBinTask


class AutoBudgetDailyLimitsPrepareBackup(BaseBinTask):
    class Requirements(Requirements):
        cores = 1
        ram = 2048
        disk_space = 2048

        class Caches(Requirements.Caches):
            pass

    class Parameters(BaseBinTask.Parameters):
        description = 'Backup YT tables'

        with BaseBinTask.Parameters.version_and_task_resource() as version_and_task_resource:
            resource_attrs = parameters.Dict('Filter resource by', default={'name': 'AutoBudgetDailyLimitsB2B'})

        secret_name = parameters.YavSecret(
            'yav secret id',
            default='sec-01dg9pn791asxk9xpagtqx2q2f'
        )
        yt_cluster = parameters.String(
            'YT cluster',
            default='hahn',
        )
        backup_base = parameters.String(
            'Backup directory path',
            default='//home/autobudget/dynamic_daily_limits/b2b/backup',
        )
        orders_table = parameters.String(
            'orders info table path',
            default='//home/yabs/dict/replica/OrderInfo',
        )
        ab_orders_table = parameters.String(
            'ab orders table path',
            default='//home/yabs/dict/replica/AutoBudgetOrder',
        )
        ab_orders_daily_limits_table = parameters.String(
            'orders daily limits table path',
            default='//home/yabs/autobudget/OrderDailyLimits',
        )
        holidays_table = parameters.String(
            'holidays table path',
            default='//home/yabs/dict/Holiday'
        )
        orders_weekly_limits_history_table = parameters.String(
            'orders weekly limits history table path',
            default='//home/yabs/autobudget/OrderWeeklyLimitsHistory',
        )
        ab_coeffs_table = parameters.String(
            'ab coeffs table path',
            default='//home/yabs/dict/AutoBudgetCoeffs',
        )
        time_targets_table = parameters.String(
            'order time targets table path',
            default='//home/autobudget/stable/autobudget_stable_0/public/import_bs/ExcessiveOrdersWithContextJoined'
        )
        ab_orders_daily_spent = parameters.String(
            'orders daily stat table path',
            default='//home/yabs/stat/AutobudgetOrderDailySpent'
        )
        ab_orders_period_spent = parameters.String(
            'orders period stat table path',
            default='//home/yabs/dict/AutoBudgetStatExternal'
        )
        result_ttl = parameters.Integer(
            'Output ttl (days)',
            default=12,
        )
        result_attrs = parameters.Dict(
            'Result resource attributes',
            default={},
        )

    def create_resource(self, backup_description):
        backup_resource = ResourceData(
            YabsAutoBudgetDailyLimitsBackup(
                self,
                description='AutobudgetDailyLimits YT backup description',
                path='backup.json',
                **self.Parameters.result_attrs
            ),
        )
        backup_resource.path.write_bytes(json.dumps(backup_description))
        backup_resource.ready()

    def on_execute(self):
        import yt.wrapper as yt

        yt_token = self.Parameters.secret_name.data()['token']
        ytc = yt.YtClient(token=yt_token, proxy=self.Parameters.yt_cluster)

        dest_path = '{}/{}'.format(self.Parameters.backup_base, self.id)
        ytc.remove(dest_path, recursive=True, force=True)
        ytc.create('map_node', dest_path, recursive=True)

        now = datetime.datetime.now(tzlocal())
        ts = now + datetime.timedelta(days=self.Parameters.result_ttl)
        ytc.set_attribute(dest_path, 'expiration_time', ts.isoformat())

        backup_description = {
            'orders_table': '{}/OrderInfo'.format(dest_path),
            'ab_orders_table': '{}/AutoBudgetOrder'.format(dest_path),
            'ab_orders_daily_limits_table': '{}/OrderDailyLimits'.format(dest_path),
            'holidays_table': '{}/Holidays'.format(dest_path),
            'orders_weekly_limits_history_table': '{}/OrderWeeklyLimitsHistory'.format(dest_path),
            'ab_coeffs_table': '{}/AutoBudgetCoeffs'.format(dest_path),
            'time_targets_table': '{}/TimeTargetsTable'.format(dest_path),
            'ab_orders_daily_spent': '{}/AutobudgetOrderDailySpent'.format(dest_path),
            'ab_orders_period_spent': '{}/AutoBudgetPeriodStat'.format(dest_path),
        }

        for table in backup_description:
            ytc.run_merge(getattr(self.Parameters, table), backup_description[table])

        backup_description['now_timestamp'] = int(time.mktime(now.timetuple()))

        self.create_resource(backup_description)
