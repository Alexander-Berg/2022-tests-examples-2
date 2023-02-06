from __future__ import print_function

import json
import logging

from datetime import date, timedelta

import sandbox.common.types.task as ctt
from sandbox.common.errors import TaskFailure

from sandbox.sdk2 import (
    Resource,
    ResourceData,
    WaitTask,
    parameters,
)

from sandbox.projects.yabs.master_report_tests.backup_data import YabsMasterReportBackupData
from sandbox.projects.yabs.master_report_tests.prepare_requests import YabsMasterReportPrepareRequests
from sandbox.projects.yabs.master_report_tests.resources import (
    YabsMasterReportSpec,
    YabsMasterReportBackupDescription,
    YabsMasterReportRequests
)
from sandbox.projects.yabs.base_bin_task import BaseBinTask


class YabsMasterReportCreateSpec(BaseBinTask):
    '''Create master report testing spec'''

    class Parameters(BaseBinTask.Parameters):
        description = 'Create master report testing spec'

        with BaseBinTask.Parameters.version_and_task_resource() as version_and_task_resource:
            resource_attrs = parameters.Dict('Filter resource by', default={'name': 'YabsMasterReportTests'})

        with parameters.Group('Execution') as exec_params:
            days_period = parameters.Integer(
                'Number of days to backup',
                default=3,
                required=True,
            )
            requests_limit = parameters.Integer(
                'Maximum number of requests',
                default=100000,
                required=True,
            )
            for_testenv = parameters.Bool(
                'Use resulting spec in testenv',
                default=False,
            )

        with parameters.Group('YT') as yt_params:
            yt_token_secret = parameters.YavSecret(
                'Secret with YT token',
                default='sec-01dbk7b8f40jq2nh6ym7y0hhgh',
                description='Has to contain YT_TOKEN key',
                required=True,
            )
            yt_proxy = parameters.String(
                'YT proxy',
                default='hahn',
                required=True,
            )
            hosts_path = parameters.String(
                'Path to directory with hosts info',
                default='//home/yabs/stat/tests/master_report_hosts',
                required=True,
            )

    def start_tasks(self, hosts):
        yesterday = date.today() - timedelta(hours=30)
        req_task = YabsMasterReportPrepareRequests(
            self,
            yql_token_vault='robot-yabs-yql-token',
            date=yesterday.strftime('%Y-%m-%d'),
            requests_limit=self.Parameters.requests_limit,
        )
        req_task.Requirements.tasks_resource = self.Requirements.tasks_resource
        req_task.save().enqueue()

        backup_task = YabsMasterReportBackupData(
            self,
            dst_hosts=hosts,
            days_period=self.Parameters.days_period,
            kill_timeout=3600 * 9,
        )
        backup_task.Requirements.tasks_resource = self.Requirements.tasks_resource
        backup_task.save().enqueue()

        return req_task, backup_task

    def get_hosts(self):
        import yt.wrapper as yt

        yt_token = self.Parameters.yt_token_secret.data()['YT_TOKEN']
        ytc = yt.YtClient(proxy=self.Parameters.yt_proxy, token=yt_token)

        hosts = []
        for host_node in ytc.list(self.Parameters.hosts_path, absolute=True):
            logging.info('Parsing host info from %s', host_node)
            host = ytc.get(host_node)
            logging.info('Host info: %s', host)

            hosts.append(host['hostname'])

        return hosts

    def create_resource(self):
        res_requests = Resource.find(task_id=self.Context.req_task, resource_type=YabsMasterReportRequests).first()
        res_backup = Resource.find(task_id=self.Context.backup_task, resource_type=YabsMasterReportBackupDescription).first()
        data = {
            'requests': res_requests.id,
            'backup': res_backup.id,
        }

        res = ResourceData(
            YabsMasterReportSpec(
                self,
                description='Master report spec',
                path='spec.json',
                for_testenv=self.Parameters.for_testenv,
            )
        )
        with open(str(res.path), 'w') as f:
            json.dump(data, f)

    def check_tasks(self):
        last_task = None
        for task_id in (self.Context.req_task, self.Context.backup_task):
            upd_task = self.find(id=task_id).first()
            if upd_task.status in (ctt.Status.Group.FINISH | ctt.Status.Group.BREAK):
                if upd_task.status not in ctt.Status.Group.SUCCEED:
                    raise TaskFailure('Task #{} failed'.format(task_id))
            else:
                last_task = upd_task

        return last_task

    def on_execute(self):
        with self.memoize_stage.start_tasks:
            hosts = self.get_hosts()
            req_task, backup_task = self.start_tasks(hosts)

            self.Context.req_task = req_task.id
            self.Context.backup_task = backup_task.id

            tasks = [req_task, backup_task]
            raise WaitTask(tasks, ctt.Status.Group.FINISH | ctt.Status.Group.BREAK, wait_all=False)

        task = self.check_tasks()
        if task:
            raise WaitTask([task], ctt.Status.Group.FINISH | ctt.Status.Group.BREAK, wait_all=False)

        self.create_resource()
