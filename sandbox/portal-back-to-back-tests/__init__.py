"""
"""

import logging
import re

from sandbox import sdk2
import sandbox.common.errors as ce
from sandbox.sandboxsdk import environments
from sandbox.sdk2.service_resources import SandboxTasksBinary
from sandbox.projects.tank.load_resources.resources import AMMO_FILE
from logging import getLogger, DEBUG, INFO, StreamHandler, debug, exception
import json


class PortalGenerateAmmoFromYT(sdk2.Task):
    """
        Task for executing YQL-requests and storing results as ammo file
    """

    class Parameters(sdk2.Parameters):
        description = "Task for executing YQL-requests and storing results as ammo file"
        kill_timeout = 60 * 60 * 3

        with sdk2.parameters.Group('YQL parameters'):
            yql_query = sdk2.parameters.String('YQL query', multiline=True, required=True)
            yql_token = sdk2.parameters.YavSecret('YQL token YAV secret id', required=True, default="sec-01daxhqve0wybwapm1ej6yget4")
            yql_result_save = sdk2.parameters.Bool('Save YQL results to resources?', default=False)

        with sdk2.parameters.Group('Ammo parameters'):
            ignore_values = sdk2.parameters.String(
                'Ignore lines containing:',
                description='Filter patterns, should be separated by newline',
                default='',
                multiline=True
            )
            headers = sdk2.parameters.Dict('Request headers',
                                           description='Headers will be added to every single request',
                                           default={'Connection': 'Close'})
            ammo_label = sdk2.parameters.String(
                'Ammo label',
                description='Ammo will be saved as AMMO_FILE resource with this label'
            )

    class Requirements(sdk2.Requirements):
        environments = (environments.PipEnvironment('yql', use_wheel=True),
                        environments.PipEnvironment('yandex-yt', version='0.10.8'))
        disk_space = 1024 * 5

    def filter_line(self, line):
        filter_applied = False
        for item in self.Parameters.ignore_values.split():
            pattern = re.compile(item)
            if pattern.search(line):
                filter_applied = True
                logging.debug('Log line %s was filtered by filter %s', line, item)
        return filter_applied

    def get_yt_logs(self):

        from yql.api.v1.client import YqlClient

        logging.info("Getting yql token from YAV")
        yql_token = self.Parameters.yql_token.data()["secret"]
        logging.info("self.Parameters.yql_token.data() '{}'".format(self.Parameters.yql_token.data()))
        logging.info("yql_token '{}'".format(str(yql_token)))

        with YqlClient(token=yql_token) as yql_client:
            logging.info("Making YQL query")
            query = yql_client.query(query=self.Parameters.yql_query, syntax_version=1)
            query.run()

            logging.info("Getting query result")
            for table in query.get_results():
                table.fetch_full_data()
                for row in table.rows:
                    if not self.filter_line(row[0]):
                        yield row

    @staticmethod
    def make_ammo_line(row):
        line = {
            "request": row[0],
            "cookies": row[1],
            "user-agent": row[2],
        }
        if row[3] is not None:
            line["host"] = row[3].split(":")[0]
        return json.dumps(line)

    def on_execute(self):
        resource_data = sdk2.ResourceData(
            AMMO_FILE(self, 'Resource generated by sandbox task #{}'.format(self.id),
                      'ammo', ammo_label=self.Parameters.ammo_label)
        )
        ammo_file_path = str(resource_data.path)
        headers = '\n'.join(
            ['[{}: {}]'.format(header, value) for header, value in self.Parameters.headers.items()]
        ) if self.Parameters.headers else ''

        with open(ammo_file_path, 'w') as ammo_file:
            if headers:
                ammo_file.write(headers + '\n')
            for row in self.get_yt_logs():
                if row:
                    logging.debug('Line from YT: %s', row)
                    ammo_file.write(self.make_ammo_line(row) + '\n')
        logging.info('File %s is written', ammo_file_path)
        resource_data.ready()
