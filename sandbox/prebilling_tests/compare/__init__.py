import os
import json

from sandbox.sdk2 import (
    ResourceData,
    parameters
)
from sandbox.projects.yabs.base_bin_task import BaseBinTask
from sandbox.projects.yabs.prebilling_tests.resources import PrebillingCompareResultrs


PREBILLING_STAT_PARSED_COLUMN_NAME_SUFFIX = 'Parsed'
PREBILLING_STAT_TABLE_NAME = 'PrebillingStat'
PATH_TO_LOGS_FOR_COMPARE = [
    'joined-chevent-log:logid:logid,eventcost,costcur,fraudbits,widefraudbits,initcost,initcostcur,costbits',
    'chaction:logid,sign:actioncost,actioncostcur']
DICTS_FOR_COMPARE = [
    'PrebillingStat',
    'PrebillingOrderStat',
    'AutoBudgetStatExternal',
    'PrebillingOrderStopDays',
    'AutoBudgetStopDays']


class PrebillingCompare(BaseBinTask):
    class Parameters(BaseBinTask.Parameters):
        description = 'Compare tables after b2b'

        with BaseBinTask.Parameters.version_and_task_resource() as version_and_task_resource:
            resource_attrs = parameters.Dict('Filter resource by', default={'name': 'PrebillingB2B'})

        secret_name = parameters.YavSecret(
            'yav secret id',
            default='sec-01eqfz6a8j1rqs267tfn54hbg5',
        )

        yt_cluster = parameters.String(
            'YT cluster',
            default='freud',
        )

        stable_path = parameters.String(
            'Stable results path',
            required=True,
        )

        test_path = parameters.String(
            'Test results path',
            required=True,
        )

        max_relative_diff = parameters.Integer(
            'Max relative diff (percent)',
            default=2,
        )

        compare_dir_path = parameters.String(
            'Compare dir path',
            default='//home/yabs/dict/tmp/tmp_prebilling_b2b/compare',
        )

        dicts_for_compare = parameters.List(
            'dicts for compare',
            default=DICTS_FOR_COMPARE,
        )

        logs_for_compare = parameters.List(
            'logs for compare',
            default=PATH_TO_LOGS_FOR_COMPARE,
        )

        num_rows_in_diff_report = parameters.Integer(
            'num rows in diff report',
            default=33
        )

    def get_value_fields(self, yql_client, table_name):
        import textwrap as tw
        query = tw.dedent('''\
            $script = @@
            import cyson

            def get_keys(value):
                return ",".join([key.decode() for key in value])

            get_keys._yql_convert_yson = (cyson.loads, cyson.dumps)
            @@;
            $convert_keys_to_string = Python3::get_keys(Callable<(Yson?)->String>, $script);

            SELECT
                column_names,
            FROM `{table_name}`
            group by $convert_keys_to_string(`Value`) as column_names;'''.format(table_name=table_name))
        request = yql_client.query(query, syntax_version=1)
        result = request.run().get_results()
        rows = []
        for table in result:
            for row in table.get_iterator():
                rows.append(row[0])
        result_set = set()
        for row in rows:
            for column_name in row.split(","):
                result_set.add(column_name)
        return result_set

    def parse_prebilling_stat(self, dict_dir, table_path):
        from yql.api.v1.client import YqlClient
        src_table = "{}/{}Test".format(dict_dir, table_path)
        dst_table = "{}/{}TestCopy".format(dict_dir, table_path)
        yql_client = YqlClient(db=self.Parameters.yt_cluster, token=self.yql_token)
        columns = self.get_value_fields(yql_client, src_table)
        query = "INSERT INTO `{dst_table}`\n SELECT\n".format(dst_table=dst_table)
        query += "`OrderID`,\n `Hash`,\n"
        for column_name in columns:
            query += "Yson::LookupInt64(`Value`, \"{column_name}\", Yson::Options(false as Strict)) as {column_name}{suffix},\n".format(
                column_name=column_name, suffix=PREBILLING_STAT_PARSED_COLUMN_NAME_SUFFIX)
        query += "FROM `{src_table}`;".format(src_table=src_table)
        request = yql_client.query(query, syntax_version=1)
        request.run().get_results()

    def compare_tables(self, ytc, stable_path, test_path, out_prefix, keys, vals, table_name):
        from yabs.sbyt.devutils.yt_compare.compareytlib.ytcompare import process
        result = process([
            '-proxy={}'.format(self.Parameters.yt_cluster),
            '-rowdiff',
            '-rowcount',
            '-keys={}'.format(keys),
            '-vals={}'.format(vals),
            '-mail',
            '-yqltoken={}'.format(self.yql_token),
            '-extract-schema',
            '-extract-difkeys',
            '-report-dir=report_b2b_prebilling',
            '-session=prebilling-b2b-result',
            '-dif-path={}'.format(out_prefix),
            stable_path,
            test_path
        ])

        row_count_val = 0
        for row_count in result['rowcount']:
            if row_count_val == 0:
                row_count_val = row_count
            if row_count_val != row_count:
                self.Context.has_diff = True
                return "Different numbers of rows"

        for key, vals in result['rowdiff'].iteritems():
            if 'stat' in vals:
                for val_column_name, val_column_stat in vals['stat'].iteritems():
                    if 'MAX' in val_column_stat and 'MIN' in val_column_stat:
                        delta_val = max(abs(val_column_stat['MAX']), abs(val_column_stat['MIN'])) * 100.0
                        if delta_val > self.Parameters.max_relative_diff:
                            self.Context.has_diff = True
                            return 'Max diff with keys {} is {} {}%'.format(key, val_column_name, delta_val)
        return 'OK!'

    def compare_dicts(self, ytc, out_directory, results):
        for table in self.Parameters.dicts_for_compare:
            if PREBILLING_STAT_TABLE_NAME not in table:
                table_name = table + 'Test'
            else:
                table_name = table + 'TestCopy'
            stable_path = '{}/dict/{}'.format(self.Parameters.stable_path, table_name)
            test_path = '{}/dict/{}'.format(self.Parameters.test_path, table_name)

            stable_exists = ytc.exists(stable_path)
            test_exists = ytc.exists(test_path)
            if stable_exists and not test_exists:
                results[table_name] = 'No table in test'
                self.Context.has_diff = True
            elif not stable_exists and test_exists:
                results[table_name] = 'New table in test'
                self.Context.has_diff = True
            elif not stable_exists and not test_exists:
                results[table_name] = 'No tables'
            else:
                keys = []
                vals = []
                schema = ytc.get(stable_path + '/@schema', format="json")
                for field in json.loads(str(schema.decode()))['$value']:
                    if 'sort_order' in field or (PREBILLING_STAT_TABLE_NAME in table_name and PREBILLING_STAT_PARSED_COLUMN_NAME_SUFFIX not in field['name']):
                        if field['name'] != "YTHash":
                            keys.append(field['name'])
                    else:
                        if field['type'] in ['int64', 'uint64', 'float']:
                            vals.append(field['name'])
                results[table_name] = self.compare_tables(ytc, stable_path, test_path, '{}/diff'.format(
                    out_directory), ",".join(keys), ",".join(vals), table_name)
        return results

    def compare_logs(self, ytc, out_directory, results):
        for log in self.Parameters.logs_for_compare:
            log_splited = log.split(':')
            log_name = log_splited[0]
            keys = log_splited[1]
            vals = log_splited[2]
            stable_path = '{}/prebilling/b2b/shared/{}/batch-00000001'.format(self.Parameters.stable_path, log_name)
            test_path = '{}/prebilling/b2b/shared/{}/batch-00000001'.format(self.Parameters.test_path, log_name)
            stable_exists = ytc.exists(stable_path)
            test_exists = ytc.exists(test_path)
            if stable_exists and not test_exists:
                results[log_name] = 'No log in test'
                self.Context.has_diff = True
            elif not stable_exists and test_exists:
                results[log_name] = 'New log in test'
                self.Context.has_diff = True
            elif not stable_exists and not test_exists:
                results[log_name] = 'No logs'
            else:
                results[log_name] = self.compare_tables(ytc, stable_path, test_path, '{}/diff'.format(out_directory), keys, vals, log_name)
        return results

    def on_execute(self):
        import yt.wrapper as yt
        from yabs.sbyt.devutils.yt_compare.compareytlib import conf
        conf.leaders_count = self.Parameters.num_rows_in_diff_report

        yt_token = self.Parameters.secret_name.data()['yt_token']
        self.yql_token = self.Parameters.secret_name.data()['yql_token']
        os.environ['YT_TOKEN'] = yt_token
        os.environ['YQL_TOKEN'] = self.yql_token
        ytc = yt.YtClient(token=yt_token, proxy=self.Parameters.yt_cluster)
        out_directory = '{}/{}'.format(self.Parameters.compare_dir_path, self.id)
        if ytc.exists(out_directory):
            ytc.remove(out_directory, recursive=True, force=True)

        ytc.create('map_node', out_directory, recursive=True)

        results = {}
        results = self.compare_logs(ytc, out_directory, results)
        self.Context.has_diff = False
        self.parse_prebilling_stat('{}/dict'.format(self.Parameters.test_path), 'PrebillingStat')
        self.parse_prebilling_stat('{}/dict'.format(self.Parameters.stable_path), 'PrebillingStat')
        results = self.compare_dicts(ytc, out_directory, results)
        result_text = 'Results differ!\n' if self.Context.has_diff else ''
        result_text += '<br>'.join('{table}:\n{res}'.format(table=table, res=results[table]) for table in results)
        result_resource = ResourceData(
            PrebillingCompareResultrs(
                self,
                description='Prebilling B2B compare results',
                path='result_b2b_prebilling.html',
            ),
        )

        with open(str(result_resource.path), 'w') as f:
            f.write('{}<br>{}'.format(result_text, open('report_b2b_prebilling/session/prebilling-b2b-result.html', 'r').read()))
        result_resource.ready()
        self.set_info(result_text, do_escape=False)
