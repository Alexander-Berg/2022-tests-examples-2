# -*- coding: utf-8 -*-
import logging
import re

from sandbox import sdk2
from sandbox.projects.antiadblock.utils import ROBOT_ANTIADB_TOKENS_YAV_ID
import sandbox.common.types.resource as ctr
from sandbox.sdk2.helpers import subprocess as sp

logger = logging.getLogger('argus_test_run')


class AntiadblockArgusTestRunBin(sdk2.Resource):
    """
    antiadblock/tasks/argus_test_run binary
    """
    releasable = True
    any_arch = True
    auto_backup = True
    group = 'ANTIADBLOCK'
    releasers = ['ANTIADBLOCK']
    release_subscribers = ['ANTIADBLOCK']


class AntiadblockArgusTestRunTask(sdk2.Task):
    """Task that runs argus test launch"""

    class Parameters(sdk2.Task.Parameters):
        tvm_id = sdk2.parameters.String('Task TVM id', default='2002631')
        configs_api_host = sdk2.parameters.String('ConfigsAPI host', default='api.aabadmin.yandex.ru')
        configs_api_tvm_id = sdk2.parameters.String('ConfigsAPI TVM id', default='2000629')
        argus_profile_tag = sdk2.parameters.String('Argus profile tag', required=False)
        argus_resource_id = sdk2.parameters.String('Argus binary resource id', required=True)
        service_id = sdk2.parameters.String('Service id', required=False)
        pr_description = sdk2.parameters.String('Pull request description', required=False)
        num_of_launches = sdk2.parameters.String('Number of launches', default='1')
        launch_backoff = sdk2.parameters.String('Backoff between launches', default='0.5')
        env_vars = sdk2.parameters.String('Optional environment variables (expecting "var1=val1;var2=val2")', required=False)

    def on_execute(self):
        service_id = self.Parameters.service_id
        argus_profile_tag = self.Parameters.argus_profile_tag

        pr_description = self.Parameters.pr_description
        if pr_description:
            if '[TEST_PROFILE]' in pr_description:
                service_id = re.search(r'\[TEST_PROFILE\]\s?(?P<service_id>.+)', pr_description, re.IGNORECASE).group('service_id')
            if '[PROFILE_TAG]' in pr_description:
                argus_profile_tag = re.search(r'\[PROFILE_TAG\]\s?(?P<profile_tag>.+)', pr_description, re.IGNORECASE).group('profile_tag')

        if service_id is None:
            err_msg = 'No value specified for service_id'
            logger.error(err_msg)
            raise ValueError(err_msg)

        binary_id = sdk2.Resource.find(
            resource_type=AntiadblockArgusTestRunBin,
            state=ctr.State.READY,
        ).limit(1).first()
        bin_res = sdk2.ResourceData(binary_id)

        env = {
            'TVM_ID': self.Parameters.tvm_id,
            'CONFIGS_API_HOST': self.Parameters.configs_api_host,
            'CONFIGS_API_TVM_ID': self.Parameters.configs_api_tvm_id,
            'ARGUS_RESOURCE_ID': self.Parameters.argus_resource_id,
            'SERVICE_ID': service_id,
            'TVM_SECRET': sdk2.yav.Secret(ROBOT_ANTIADB_TOKENS_YAV_ID).data()['ANTIADBLOCK_SANDBOX_MONITORING_TVM_SECRET'],
            'NUM_OF_LAUNCHES': self.Parameters.num_of_launches,
            'LAUNCH_BACKOFF': self.Parameters.launch_backoff,
        }
        if argus_profile_tag:
            env['ARGUS_PROFILE_TAG'] =  argus_profile_tag

        if self.Parameters.env_vars:
            for kv in self.Parameters.env_vars.strip().strip(';').split(';'):
                key, value = kv.split('=')
                env[key.strip()] = value.strip()

        cmd = [
            str(bin_res.path)
        ]
        with sdk2.helpers.ProcessLog(self, logger="run_task_log") as log:
            sp.check_call(cmd, stdout=log.stdout, stderr=log.stderr, env=env)
