from __future__ import print_function

import json

from sandbox.sdk2 import (
    ResourceData,
    Vault,
    parameters,
)
from sandbox.projects.yabs.master_report_tests.resources import YabsMasterReportRequests
from sandbox.projects.yabs.base_bin_task import BaseBinTask


YQL_QUERY = '''
use hahn;

select String::UnescapeC(request_body) as request_body
from `//logs/bsfastexport-access-post-log/1d/{date}`
where
    Re2::Grep('bsfastexport\\\\d\\\\d[a-z]')(source_uri)
    and request = '/export/master-report.cgi'
    and server_port = '80'
    and String::UnescapeC(request_body) like '%"with_performance_coverage":0%'
order by Digest::MurMurHash(request_body)
limit {limit}
'''


class YabsMasterReportPrepareRequests(BaseBinTask):
    '''Collect master report requests for B2B tests'''

    class Parameters(BaseBinTask.Parameters):
        description = 'Collect master report requests for B2B tests'

        with BaseBinTask.Parameters.version_and_task_resource() as version_and_task_resource:
            resource_attrs = parameters.Dict('Filter resource by', default={'name': 'YabsMasterReportTests'})

        with parameters.Group('Backup') as backup_params:
            yql_token_vault = parameters.String(
                'Vault with YQL token',
                required=True,
            )
            yt_cluster = parameters.String(
                'YT cluster',
                default='hahn',
                required=True,
            )
            date = parameters.String(
                'Requests date',
                required=True,
            )
            requests_limit = parameters.Integer(
                'Maximum number of requests',
                default=10000,
                required=True,
            )
            logs_path = parameters.String(
                'Path to YT directory with daily logs tables',
                default='//logs/bsfastexport-access-post-log/1d',
                required=True,
            )
            result_attrs = parameters.Dict(
                'Result resource attributes',
                default={},
            )

    def create_resource(self, data):
        backup_resource = ResourceData(
            YabsMasterReportRequests(
                self,
                description='Master report b2b requests',
                path='requests.json',
                **self.Parameters.result_attrs
            ),
        )
        backup_resource.path.write_bytes(json.dumps(data))
        backup_resource.ready()

    def get_requests(self, yql_client):
        request = yql_client.query(YQL_QUERY.format(date=self.Parameters.date, limit=self.Parameters.requests_limit), syntax_version=1)
        request.run()
        request_url = request.share_url
        self.set_info("YQL query: {}".format(request_url))

        results = request.get_results()
        table = None
        for res in results:
            table = res
            break

        return [row[0] for row in table.get_iterator()]

    def on_execute(self):
        from yql.api.v1.client import YqlClient

        yql_token = Vault.data(self.Parameters.yql_token_vault)
        yql_client = YqlClient(token=yql_token, db=self.Parameters.yt_cluster)

        requests = self.get_requests(yql_client)
        result = {'date': self.Parameters.date, 'requests': requests}

        self.create_resource(result)
