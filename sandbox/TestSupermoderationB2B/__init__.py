# -*- coding: utf-8 -*-
import sandbox.projects.release_machine.core.task_env as task_env
import sandbox.common.types.task as ctt

from sandbox import sdk2
from sandbox.common.types.misc import NotExists
from sandbox.common.utils import get_task_link
from sandbox.projects.release_machine.core import const as rm_const
from sandbox.projects.release_machine.helpers.startrek_helper import STHelper
from sandbox.projects.release_machine.components import all as rmc
from sandbox.projects.modadvert.SupermoderationInstance import ModadvertSupermoderationInstanceCreator


class ModadvertTestSupermoderationB2B(ModadvertSupermoderationInstanceCreator):

    name = 'MODADVERT_TEST_SUPERMODERATION_B2B'

    class Requirements(sdk2.Task.Requirements):
        environments = (
            task_env.TaskRequirements.startrek_client,
        )
        client_tags = task_env.TaskTags.startrek_client

    class Parameters(ModadvertSupermoderationInstanceCreator.Parameters):

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

        context_parameters = [
            'yt_proxy_url',
            'vault_user',
            'tokens',
            'component_name',
            'release_number',
            'binary_sm_database_creator',
            'binary_test_requests_generator',
            'binary_save_sm_results',
            'binary_diff_sm_results',
        ]

        for parameter_name in context_parameters:
            context_value = getattr(self.Context, parameter_name)
            if context_value and context_value is not NotExists:
                setattr(self.Parameters, parameter_name, context_value)

        return super(ModadvertTestSupermoderationB2B, self).on_save()

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

        super(ModadvertTestSupermoderationB2B, self).on_before_execute()

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

        super(ModadvertTestSupermoderationB2B, self).on_finish(prev_status, status)
