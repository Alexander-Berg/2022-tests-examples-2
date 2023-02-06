# -*- coding: utf-8 -*-
import datetime as dt
import logging
import os
from sandbox import sdk2
from sandbox.common.rest import Client
from sandbox.common.types.misc import NotExists
from sandbox.projects.modadvert import resource_types
from sandbox.projects.modadvert.common import modadvert
from sandbox.projects.modadvert.RunComparison import ModadvertRunB2B
from sandbox.projects.modadvert.RunLyncherSDK2 import ModadvertRunLyncherSDK2
from sandbox.projects.modadvert.RunQLyncher import ModadvertRunQlyncher


B2B_SOURCE_SCHEDULER = 4470


class ModadvertTestLyncher(ModadvertRunB2B):

    automoderator_name = 'lyncher'

    class Parameters(ModadvertRunB2B.Parameters):

        with sdk2.parameters.Group('Comparison parameters') as comparison_group:
            comparison_root_dir = ModadvertRunB2B.Parameters.comparison_root_dir(default='//home/modadvert/test/comparison/')

        with sdk2.parameters.Group('Launch parameters') as launch_group:
            child_task_kill_timeout = sdk2.parameters.Timedelta(
                'Child tasks time to kill',
                required=False,
                default=dt.timedelta(hours=24)
            )
            use_qlyncher = sdk2.parameters.Bool('Use Qlyncher instead Lyncher')
            max_rows_count = sdk2.parameters.Integer('Maximum rows count to process per launch')
            src_tables_dir = ModadvertRunB2B.Parameters.src_tables_dir(default='//home/modadvert/lyncher/b2b')
            primary_read_cluster = modadvert.YtCluster('Primary read cluster', default='arnold')
            secondary_read_cluster = modadvert.YtCluster('Secondary read cluster', default='Hahn')
            use_synchrophazotron = sdk2.parameters.Bool('Use synchrophazotron', default=True, required=True)

        with sdk2.parameters.Group('Base parameters') as base_lyncher_group:
            base_lyncher_binaries_resource = sdk2.parameters.Resource(
                'Lyncher binaries resource',
                resource_type=resource_types.MODADVERT_LYNCHER_BINARIES
            )
            base_qlyncher_binaries_resource = sdk2.parameters.Resource(
                'QLyncher binaries resource',
                resource_type=resource_types.MODADVERT_QLYNCHER_BINARIES
            )
            base_config_resource = sdk2.parameters.Resource(
                'Config resource',
                resource_type=resource_types.MODADVERT_LYNCHER_CONFIG
            )

        with sdk2.parameters.Group('Feature lyncher') as feature_lyncher_group:
            feature_lyncher_binaries_resource = sdk2.parameters.Resource(
                'Lyncher binaries resource',
                resource_type=resource_types.MODADVERT_LYNCHER_BINARIES
            )
            feature_qlyncher_binaries_resource = sdk2.parameters.Resource(
                'QLyncher binaries resource',
                resource_type=resource_types.MODADVERT_QLYNCHER_BINARIES
            )
            feature_config_resource = sdk2.parameters.Resource(
                'Config resource',
                resource_type=resource_types.MODADVERT_LYNCHER_CONFIG
            )

    def on_save(self):
        """
        Testenv is badly compatible with SDK2
        it fills Context instead of Parameters
        """

        for parameter_name in [
            'yt_proxy_url',
            'vault_user',
            'tokens',
            'feature_lyncher_binaries_resource',
            'feature_lyncher_config_resource',
            'feature_config_resource',
            'component_name',
            'release_number',
            'use_qlyncher'
        ]:
            context_value = getattr(self.Context, parameter_name)
            if context_value and context_value is not NotExists:
                setattr(self.Parameters, parameter_name, context_value)

        prod_parameters = {
            field['name']: field['value'] for field in
            Client().scheduler[B2B_SOURCE_SCHEDULER].read()['task']['custom_fields']
        }
        if self.Parameters.use_qlyncher:
            self.Parameters.base_qlyncher_binaries_resource = self._find_qlyncher_binary(prod_parameters['binaries_resource'])
            feature_qlyncher_binaries = getattr(self.Context, 'feature_qlyncher_binaries_resource')
            if feature_qlyncher_binaries and feature_qlyncher_binaries is not NotExists:
                self.Parameters.feature_qlyncher_binaries_resource = feature_qlyncher_binaries
        else:
            self.Parameters.base_lyncher_binaries_resource = prod_parameters['binaries_resource']
        self.Parameters.base_config_resource = prod_parameters['config_resource']

        return super(ModadvertTestLyncher, self).on_save()

    def _find_qlyncher_binary(self, lyncher_resource_id):
        released_branch = Client().resource[lyncher_resource_id].read()['attributes']['branch']

        for page in xrange(10):
            json_data = Client().resource.read(limit=50, type='MODADVERT_QLYNCHER_BINARIES', state='READY', offset=page*50)

            for item in json_data['items']:
                if item['attributes'].get('branch') == released_branch:
                    logging.info('Found binary {}'.format(item['http']['proxy']))
                    return item['id']

        logging.error('QLyncher base resource not found for branch {}'.format(released_branch))
        return None

    def create_runner_subtask(self, branch):
        comparison_dir = getattr(self.Context, 'comparison_{}_dir'.format(branch))
        binaries_resource = getattr(
            self.Parameters,
            '{}_{}_binaries_resource'.format(branch, 'qlyncher' if self.Parameters.use_qlyncher else 'lyncher')
        )
        config_resource = getattr(self.Parameters, '{}_config_resource'.format(branch))
        return self.create_subtask(
            ModadvertRunQlyncher if self.Parameters.use_qlyncher else ModadvertRunLyncherSDK2,
            {
                ModadvertRunLyncherSDK2.Parameters.vault_user.name: self.Parameters.vault_user,
                ModadvertRunLyncherSDK2.Parameters.tokens.name: self.Parameters.tokens,
                ModadvertRunLyncherSDK2.Parameters.yt_proxy_url.name: self.Parameters.yt_proxy_url,
                ModadvertRunLyncherSDK2.Parameters.kill_timeout.name: self.Parameters.child_task_kill_timeout,
                ModadvertRunLyncherSDK2.Parameters.max_rows_count.name: self.Parameters.max_rows_count,
                ModadvertRunLyncherSDK2.Parameters.max_tables_age.name: self.Parameters.max_tables_age,
                ModadvertRunLyncherSDK2.Parameters.src_tables_dir.name: self.Context.comparison_data_dir,
                ModadvertRunLyncherSDK2.Parameters.primary_read_cluster.name: self.Parameters.primary_read_cluster,
                ModadvertRunLyncherSDK2.Parameters.secondary_read_cluster.name: self.Parameters.secondary_read_cluster,
                ModadvertRunLyncherSDK2.Parameters.use_synchrophazotron.name: self.Parameters.use_synchrophazotron,
                ModadvertRunLyncherSDK2.Parameters.verdicts_table.name: os.path.join(comparison_dir, 'verdicts'),
                ModadvertRunLyncherSDK2.Parameters.state_path.name: os.path.join(comparison_dir, 'state'),
                ModadvertRunLyncherSDK2.Parameters.debug.name: True,
                ModadvertRunLyncherSDK2.Parameters.binaries_resource.name: binaries_resource,
                ModadvertRunLyncherSDK2.Parameters.config_resource.name: config_resource
            }
        )
