# -*- coding: utf-8 -*-

import logging

from sandbox import sdk2
from sandbox.sdk2.vcs import svn
from sandbox.common.types import client as ctc

from sandbox.projects.common import solomon
from sandbox.projects.common import testenv_client
from sandbox.projects.common import error_handlers as eh


class MonitorTestEnvironmentVersion(sdk2.Task):

    class Requirements(sdk2.Task.Requirements):
        client_tags = ctc.Tag.GENERIC
        disk_space = 10
        ram = 256

    def on_execute(self):
        client = testenv_client.TEClient()
        engine_revision = int(client.get_sys_info().json()['test_environment_revision'])
        engine_revision_info = svn.Arcadia.log('arcadia:/arc/trunk/arcadia', engine_revision, 1, limit=1)[0]
        logging.info(engine_revision_info)

        top_revision_info = svn.Arcadia.log('arcadia:/arc/trunk/arcadia/testenv', "HEAD", 1, limit=1)[0]
        logging.info(top_revision_info)
        top_revision = top_revision_info['revision']

        logging.info('engine_revision: %s, top_revision: %s', engine_revision, top_revision)

        time_delta = (top_revision_info['date'] - engine_revision_info['date']).total_seconds()
        logging.info('time_delta: %s', time_delta)

        try:
            sensor = {
                "labels": {
                    "sensor": "testenv_deploy_delay",
                },
                "value": time_delta,
                # "ts":  "2019-02-03T04:11:43.000000Z"  # optional time in ISO-8601 format
            }
            solomon_token = sdk2.Vault.data('SEARCH-RELEASERS', 'common_release_token')

            solomon_params = {
                # хз что сюда писать?
                'project': 'testenv',
                'cluster': 'production',
                'service': 'main',
            }

            solomon.push_to_solomon_v2(
                token=solomon_token,
                params=solomon_params,
                sensors=[sensor],
            )
        except Exception as exc:
            eh.log_exception('Cannot push sensors to Solomon', exc, task=self)
