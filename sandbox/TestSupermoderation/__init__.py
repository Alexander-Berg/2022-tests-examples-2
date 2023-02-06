# -*- coding: utf-8 -*-
import sandbox.projects.release_machine.core.task_env as task_env
import sandbox.common.types.task as ctt

from sandbox import sdk2
from sandbox.common.types.misc import NotExists
from sandbox.common.utils import get_task_link
from sandbox.projects.release_machine.core import const as rm_const
from sandbox.projects.release_machine.helpers.startrek_helper import STHelper
from sandbox.projects.release_machine.components import all as rmc
from sandbox.projects.modadvert.SupermoderationB2B import ModadvertSupermoderationB2B
from sandbox.sandboxsdk.environments import PipEnvironment


class ModadvertTestSupermoderation(ModadvertSupermoderationB2B):

    class Requirements(sdk2.Task.Requirements):
        environments = (
            task_env.TaskRequirements.startrek_client,
            PipEnvironment('yandex-yt', '0.8.38a1', use_wheel=True),
            PipEnvironment('yandex-yt-yson-bindings-skynet', use_wheel=True),
        )
        client_tags = task_env.TaskTags.startrek_client

    class Parameters(ModadvertSupermoderationB2B.Parameters):

        with sdk2.parameters.Group('Testenv parameters') as testenv_parameters:
            release_number = sdk2.parameters.Integer('release number', default=None)
            with sdk2.parameters.String('Component name', multiline=True, default=None) as component_name:
                for name in rmc.get_component_names():
                    setattr(component_name.values, name, name)

    def get_c_info(self):
        return rmc.COMPONENTS[self.Parameters.component_name]()

    def on_save(self):
        """
        Testenv is badly compatible with SDK2
        it fills Context instead of Parameters
        """

        resource_names = [
            'broker_package',
            'api_package',
            'conf_package',
            'service_confs_package',
        ]
        context_parameters = [
            'yt_proxy_url',
            'vault_user',
            'tokens',
            'component_name',
            'release_number',
            'b2b_binary_package',
            'input_table',
        ] + ['feature_{}'.format(resource_name) for resource_name in resource_names]

        for parameter_name in context_parameters:
            context_value = getattr(self.Context, parameter_name)
            if context_value and context_value is not NotExists:
                setattr(self.Parameters, parameter_name, context_value)

        for resource_name in resource_names:
            base_name = 'base_{}'.format(resource_name)
            feature_value = getattr(self.Parameters, 'feature_{}'.format(resource_name))
            base_value = getattr(self.Parameters, base_name)
            if (not base_value or base_value is NotExists) and (feature_value and feature_value is not NotExists):
                base_resource = sdk2.Resource.find(
                    resource_type=feature_value.type,
                    state='READY',
                    attr_name='released',
                    attr_value='stable',
                    order='-id'
                ).first()
                setattr(self.Parameters, base_name, base_resource)

        return super(ModadvertTestSupermoderation, self).on_save()

    def on_before_execute(self):
        c_info = self.get_c_info()
        st_helper = STHelper(sdk2.Vault.data(rm_const.COMMON_TOKEN_OWNER, rm_const.COMMON_TOKEN_NAME))

        if not getattr(self.Context, 'priemka_ticket', None):
            self.Context.priemka_ticket = st_helper.find_ticket_by_release_number(self.Parameters.release_number, c_info).id
            st_helper.comment(
                self.Parameters.release_number,
                'B2B started\n{}'.format(get_task_link(self.id)),
                c_info
            )

        super(ModadvertTestSupermoderation, self).on_before_execute()

    def on_execute_inner(self):
        pass

    def on_finish(self, prev_status, status):
        c_info = self.get_c_info()
        st_helper = STHelper(sdk2.Vault.data(rm_const.COMMON_TOKEN_OWNER, rm_const.COMMON_TOKEN_NAME))
        st_helper.comment(
            self.Parameters.release_number,
            'B2B finished with status {}\n{}'.format(status, get_task_link(self.id)),
            c_info
        )
        if status == ctt.Status.SUCCESS:
            st_helper.comment(
                self.Parameters.release_number,
                'All tests passed\n' + c_info.get_deploy_message(self.Parameters.release_number),
                c_info
            )

        super(ModadvertTestSupermoderation, self).on_finish(prev_status, status)
