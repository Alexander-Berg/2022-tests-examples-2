from __future__ import print_function

import json
import logging
import time

import sandbox.common.types.task as ctt
from sandbox.common.errors import TaskFailure
from sandbox.common.types.resource import State

from sandbox.sdk2 import (
    ResourceData,
    parameters,
)

from sandbox.projects.resource_types import OTHER_RESOURCE
from sandbox.projects.yabs.infra.mdb_clickhouse_apply_config.task import MdbClickhouseApplyConfig
from sandbox.projects.yabs.infra.mdb_clickhouse_apply_config.resources import (
    MdbClickhouseDictsConfig,
    MdbClickhouseUsersConfig,
    MdbClickhouseServerConfig,
)
from sandbox.projects.yabs.master_report_tests.shoot import YabsMasterReportShoot
from sandbox.projects.yabs.master_report_tests.resources import (
    YabsMasterReportSpec,
    YabsMasterReportShootResults,
)
from sandbox.projects.yabs.install_debian_package import InstallDebianPackage
from sandbox.projects.yabs.base_bin_task import BaseBinTask


class YabsMasterReportPrepareAndShoot(BaseBinTask):
    '''Prepare testing stand and shoot requests at it'''

    class Parameters(BaseBinTask.Parameters):
        description = 'Prepare testing stand and shoot requests at it'

        with BaseBinTask.Parameters.version_and_task_resource() as version_and_task_resource:
            resource_attrs = parameters.Dict('Filter resource by', default={'name': 'YabsMasterReportTests'})

        with parameters.Group('Resources') as resource_params:
            dicts_config = parameters.Resource(
                'Dicts config resource',
                resource_type=MdbClickhouseDictsConfig,
                state=State.READY,
            )
            users_config = parameters.Resource(
                'Users config resource',
                resource_type=MdbClickhouseUsersConfig,
                state=State.READY,
            )
            server_config = parameters.Resource(
                'Server config resource',
                resource_type=MdbClickhouseServerConfig,
                state=State.READY,
            )
            deb_version = parameters.Resource(
                'yabs-export-sctipts-fast version resource',
                resource_type=OTHER_RESOURCE,
                state=State.READY,
                required=True,
            )
            spec = parameters.Resource(
                'Backup resources spec',
                resource_type=YabsMasterReportSpec,
                state=State.READY,
                required=True,
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

    def take_host(self, ytc):
        import yt.wrapper as yt

        locked_host = ''

        while True:
            for host_node in ytc.list(self.Parameters.hosts_path, absolute=True):
                try:
                    logging.info('Trying to lock node %s', host_node)
                    ytc.lock(host_node, mode="exclusive", waitable=True, wait_for=10000)
                except yt.YtError as e:
                    logging.info('Failed to lock: %s', e)
                else:
                    locked_host = host_node
                    break

            if locked_host:
                break

        logging.info('Locked node %s', locked_host)
        host = ytc.get(locked_host)
        logging.info('Locked host info: %s', host)
        return host

    def start_task(self, task_type, **params):
        params['auto_search'] = False
        logging.info('Starting task %s with params %s', task_type.type, params)
        task = task_type(self, **params)
        task.Requirements.tasks_resource = self.Requirements.tasks_resource
        task.save().enqueue()
        return task.id

    def start_prepare_tasks(self, host):
        with open(str(ResourceData(self.Parameters.deb_version).path)) as f:
            version = f.read()

        install_task = self.start_task(
            InstallDebianPackage,
            package='yabs-export-scripts-fast',
            version=version,
            hostname=host['hostname'],
            username='robot-yabs-stat-test',
            ssh_key_vault='robot-yabs-stat-test-ssh-key',
        )

        mdb_task = self.start_task(
            MdbClickhouseApplyConfig,
            dicts_config=self.Parameters.dicts_config,
            users_config=self.Parameters.users_config,
            server_config=self.Parameters.server_config,
            cluster_id=host['mdb_cluster_id'],
            mdb_token='robot-yabs-mdb-mdb-token',
            yav_token='robot-yabs-stat-test-yav-token',
        )

        return install_task, mdb_task

    def start_shoot_task(self, host, spec):
        res = YabsMasterReportShootResults(
            self,
            description='Master report B2B shoot results',
            path='responses.pkl',
        )

        task = self.start_task(
            YabsMasterReportShoot,
            result_resource=res,
            requests_resource=spec['requests'],
            backup_resource=spec['backup'],
            target_host=host['hostname'],
            username='robot-yabs-stat-test',
            ssh_key_vault='robot-yabs-stat-test-ssh-key',
        )
        return task, res

    # implement custom method to keep the lock
    def wait_for_tasks(self, task_ids):
        while task_ids:
            time.sleep(10)

            finished = []
            for task_id in task_ids:
                status = self.server.task[task_id].read()['status']
                if status in ctt.Status.Group.EXECUTE or status in ctt.Status.Group.QUEUE:
                    continue
                elif status in ctt.Status.Group.SUCCEED:
                    finished.append(task_id)
                else:
                    raise TaskFailure('Task #{} failed'.format(task_id))

            task_ids = filter(lambda t: t not in finished, task_ids)

    def on_execute(self):
        import yt.wrapper as yt

        yt_token = self.Parameters.yt_token_secret.data()['YT_TOKEN']
        ytc = yt.YtClient(proxy=self.Parameters.yt_proxy, token=yt_token)

        spec_res = ResourceData(self.Parameters.spec)
        with open(str(spec_res.path)) as f:
            spec_data = json.load(f)

        with ytc.Transaction():
            host = self.take_host(ytc)

            prep_tasks = self.start_prepare_tasks(host)
            self.wait_for_tasks(prep_tasks)

            shoot_task, resource = self.start_shoot_task(host, spec_data)
            self.wait_for_tasks([shoot_task])

            self.agentr.resource_sync(resource.id)
