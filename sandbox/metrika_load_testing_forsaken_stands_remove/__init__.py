# coding=utf-8
import logging

from datetime import datetime
import sandbox.sdk2 as sdk2
import sandbox.projects.metrika.utils.settings as settings
import sandbox.projects.metrika.utils as utils

import sandbox.projects.common.binary_task as binary_task

import sandbox.projects.metrika.utils.base_metrika_task as base_metrika_task


@base_metrika_task.with_parents
class MetrikaLoadTestingForsakenStandsRemove(binary_task.LastRefreshableBinary, sdk2.Task):
    class Parameters(utils.CommonParameters):
        with sdk2.parameters.Group('Secrets parameters') as secrets_parameters:
            deploy_token_yav_secret = sdk2.parameters.YavSecret(
                'YP access secret',
                required=True,
                default=settings.yav_uuid,
                description='Used in requests to yp api',
            )
            deploy_token_yav_secret_key = sdk2.parameters.String(
                'YP access secret key',
                required=True,
                default='deploy-token',
            )

        _binary = binary_task.binary_release_parameters_list(stable=True)

    @property
    def deploy_client(self):
        import metrika.pylib.deploy.client

        secret = self.Parameters.deploy_token_yav_secret.data()
        token = secret[self.Parameters.deploy_token_yav_secret_key]

        return metrika.pylib.deploy.client.DeployAPI(token=token)

    def on_execute(self):
        for stage in self.deploy_client.stage.list_project_stages('metrika-load-testing'):
            created_timestamp = self.deploy_client.stage.get_stage_meta(stage['id']).get('creation_time')
            created = datetime.fromtimestamp(created_timestamp / 1000000)
            logging.info('Stage {} was created: {}'.format(stage['id'], created))
