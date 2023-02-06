from __future__ import print_function

import datetime
import os

from dateutil.tz import tzlocal

from sandbox.sdk2 import (
    ResourceData,
    parameters
)
from sandbox.projects.autobudget.resources import YabsAutoBudgetDailyLimitsResult
from sandbox.projects.yabs.base_bin_task import BaseBinTask

TABLES_FOR_COMPARE = ['OrdersDailyLimits']


class AutoBudgetDailyLimitsComparator(BaseBinTask):

    class Parameters(BaseBinTask.Parameters):
        description = 'Compare tables after b2b'

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
        output_prefix = parameters.String(
            'Output prefix',
            default='//home/autobudget/dynamic_daily_limits/b2b/comparator',
        )
        result_ttl = parameters.Integer(
            'Output ttl (days)',
            default=12,
        )
        stable_path = parameters.String(
            'Stable results path',
            required=True,
        )
        test_path = parameters.String(
            'Test results path',
            required=True,
        )
        max_diff = parameters.Integer(
            'Max diff for LimitDayMoney and LimitDayMoneyCur (percent)',
            default=5,
        )
        tables_for_compare = parameters.List(
            'List of tables for compare',
            default=TABLES_FOR_COMPARE,
        )

    def compare_tables(self, ytc, stable_path, test_path, out_prefix):

        from yabs.sbyt.devutils.yt_compare.compareytlib.ytcompare import process

        result = process([
            '-proxy={}'.format(self.Parameters.yt_cluster),
            '-rowdiff',
            '-rowcount',
            '-keys=OrderID,Date',
            '-vals=LimitDayMoney,LimitDayMoneyCur',
            '-extract-difkeys',
            '-totals',
            '-rowshred',
            '-mail=yt_compare@',
            '-session=testenv-autobudget-b2b',
            '-dif-path={}'.format(out_prefix),
            stable_path,
            test_path
        ])
        day_money_delta = max(abs(result['rowdiff']['OrderID,Date']['stat']['LimitDayMoney']['MAX']), abs(result['rowdiff']['OrderID,Date']['stat']['LimitDayMoney']['MIN'])) * 100.0
        day_money_cur_delta = max(abs(result['rowdiff']['OrderID,Date']['stat']['LimitDayMoneyCur']['MAX']), abs(result['rowdiff']['OrderID,Date']['stat']['LimitDayMoneyCur']['MIN'])) * 100.0

        diff_keys = ytc.get('{}k/@row_count'.format(out_prefix))
        if diff_keys:
            self.Context.has_diff = True
            return 'Keys are different, look {}k'.format(out_prefix)
        if day_money_delta >= self.Parameters.max_diff or day_money_cur_delta >= self.Parameters.max_diff:
            self.Context.has_diff = True
            return 'Max diff LimitDayMoney: {}%, LimitDayMoneyCur: {}%'.format(day_money_delta, day_money_cur_delta)
        return 'OK!'

    def on_execute(self):
        import yt.wrapper as yt

        yt_token = self.Parameters.secret_name.data()['token']
        os.environ['YT_TOKEN'] = yt_token
        ytc = yt.YtClient(token=yt_token, proxy=self.Parameters.yt_cluster)
        out_directory = '{}/{}'.format(self.Parameters.output_prefix, self.id)
        ytc.remove(out_directory, recursive=True, force=True)
        ytc.create('map_node', out_directory, recursive=True)

        ts = datetime.datetime.now(tzlocal())
        ts += datetime.timedelta(days=self.Parameters.result_ttl)
        ytc.set_attribute(out_directory, 'expiration_time', ts.isoformat())

        self.Context.has_diff = False

        results = {}
        for table in self.Parameters.tables_for_compare:
            stable_path = '{}/{}'.format(self.Parameters.stable_path, table)
            test_path = '{}/{}'.format(self.Parameters.test_path, table)

            stable_exists = ytc.exists(stable_path)
            test_exists = ytc.exists(test_path)
            if stable_exists and not test_exists:
                results[table] = 'No table in test'
                self.Context.has_diff = True
            elif not stable_exists and test_exists:
                results[table] = 'New table in test'
                self.Context.has_diff = True
            elif not stable_exists and not test_exists:
                results[table] = 'No tables'
            else:
                results[table] = self.compare_tables(ytc, stable_path, test_path, '{}/diff'.format(out_directory))

        result_text = '<br>'.join('{table}:\n{res}'.format(table=table, res=results[table]) for table in results)

        result_resource = ResourceData(
            YabsAutoBudgetDailyLimitsResult(
                self,
                description='AutoBudgetDailyLimits comparator results',
                path='result.html',
            ),
        )

        with open(str(result_resource.path), 'w') as f:
            f.write('{}<br>{}'.format(result_text, open('{}/.yt_compare/report/session/testenv-autobudget-b2b.html'.format(os.environ['HOME']), 'r').read()))
        result_resource.ready()

        self.set_info(result_text, do_escape=False)
