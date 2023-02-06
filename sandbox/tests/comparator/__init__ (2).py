from __future__ import print_function

import logging
import datetime
import json

from dateutil.tz import tzlocal

from sandbox.sdk2 import (
    ResourceData,
    parameters,
)
from sandbox.projects.yabs.cpm_multiplier.resources import YabsCpmMultiplierTestResults
from sandbox.projects.yabs.base_bin_task import BaseBinTask


DEFAULT_TABLES_CONFIG = '''{
    "CPMMultiplier": {
        "key_columns": ["PageID", "ImpID", "ExperimentBits", "ProductBlock"],
        "value_columns": ["CPMMultiplier", "CPMMultiplierRaw", "UpdateTime"]
    },
    "Regulator": {
        "key_columns": ["PageID", "ImpID", "ProductBlock"],
        "value_columns": ["Diff", "Coeff", "UpdateTime"]
    }
}'''

QUERY_BASE = '''
PRAGMA DisableSimpleColumns;

insert into `{out_path}`
select * from `{stable_path}`as stable
full join `{test_path}` as test
    using ({key_columns})
where
    stable.{key} is null or test.{key} is null
    or {value_clause}
'''


class YabsCpmMultiplierComparator(BaseBinTask):
    '''Compares CPMMultiplier execution results
    '''

    class Parameters(BaseBinTask.Parameters):
        with BaseBinTask.Parameters.version_and_task_resource() as version_and_task_resource:
            resource_attrs = parameters.Dict('Filter resource by', default={'name': 'YabsCpmMultiplierB2B'})

        with parameters.Group('YT parameters') as yt_params:
            yt_token_secret_id = parameters.YavSecret(
                label="YT token secret id",
                required=True,
                description='secret should contain keys: YT_TOKEN',
                default="sec-01dbk7b8f40jq2nh6ym7y0hhgh",
            )
            yt_cluster = parameters.String(
                'YT cluster',
                default='hahn',
                required=True,
            )
            yt_prefix = parameters.String(
                'Output prefix',
                default='//home/yabs/stat/tests/cpm_multiplier/comparator',
                required=True,
            )
            result_ttl = parameters.Integer(
                'Output ttl (days)',
                default=14,
            )
            stable_path = parameters.String(
                'Stable results path',
                required=True,
            )
            test_path = parameters.String(
                'Test results path',
                required=True,
            )
            tables_config = parameters.String(
                'Tables configuration',
                required=True,
                default=DEFAULT_TABLES_CONFIG,
            )
            check_schemas = parameters.Bool(
                'Compare schemas',
                required=True,
                default=True,
            )

    def compare_tables(self, ytc, yql_client, stable_path, test_path, out_prefix, table):
        if self.Parameters.check_schemas:
            stable_schema = ytc.get_attribute(stable_path, 'schema')
            test_schema = ytc.get_attribute(test_path, 'schema')

            if test_schema != stable_schema:
                self.Context.has_diff = True
                return 'Tables have different schemas'

        out_path = '{}/{}'.format(out_prefix, table)

        tables_config = json.loads(self.Parameters.tables_config)

        columns = tables_config[table]
        single_value_clauses = ['stable.{column} != test.{column}'.format(column=col) for col in columns['value_columns']]

        query = QUERY_BASE.format(
            out_path=out_path,
            stable_path=stable_path,
            test_path=test_path,
            key_columns=', '.join(columns['key_columns']),
            key=columns['key_columns'][0],
            value_clause=' or '.join(single_value_clauses),
        )
        request = yql_client.query(query, syntax_version=1)
        request.run()
        logging.info('Running yql operation: %s', request.share_url)
        request.get_results()

        if ytc.get_attribute(out_path, 'row_count') > 0:
            self.Context.has_diff = True
            yt_url = 'https://yt.yandex-team.ru/{}/navigation?path={}'.format(self.Parameters.yt_cluster, out_path)
            return 'Different content: <a href="{}">diff</a>, <a href="{}">YQL</a>'.format(yt_url, request.share_url)
        else:
            return 'OK (<a href="{}">YQL</a>)'.format(request.share_url)

    def on_execute(self):
        import yt.wrapper as yt
        from yql.api.v1.client import YqlClient
        yt_token = self.Parameters.yt_token_secret_id.data()["YT_TOKEN"]
        ytc = yt.YtClient(token=yt_token, proxy=self.Parameters.yt_cluster)
        out_prefix = '{}/{}'.format(self.Parameters.yt_prefix, self.id)
        ytc.remove(out_prefix, force=True)
        ytc.create('map_node', out_prefix)

        ts = datetime.datetime.now(tzlocal())
        ts += datetime.timedelta(days=self.Parameters.result_ttl)
        ytc.set_attribute(out_prefix, 'expiration_time', ts.isoformat())

        yql_client = YqlClient(token=yt_token, db=self.Parameters.yt_cluster)
        results = {}
        self.Context.has_diff = False

        tables_config = json.loads(self.Parameters.tables_config)

        for table in tables_config:
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
                results[table] = self.compare_tables(ytc, yql_client, stable_path, test_path, out_prefix, table)

        result_text = 'Results differ!\n' if self.Context.has_diff else ''
        result_text += '\n'.join('{table}: {res}'.format(table=table, res=res) for table, res in results.iteritems())

        result_resource = ResourceData(
            YabsCpmMultiplierTestResults(
                self,
                description='CPMMultiplier comparator results',
                path='result.html',
            ),
        )
        with open(str(result_resource.path), 'w') as f:
            f.write(result_text.replace('\n', '<br>'))
        result_resource.ready()

        self.set_info(result_text, do_escape=False)
