# -*- coding: utf-8 -*-
import logging
import os
from sandbox import sdk2
from sandbox.projects.modadvert.resource_types import MODADVERT_LAAS_MR_RUNNER_BINARY
from sandbox.projects.modadvert.rm.constants import CUPID_OBJECT_TYPES
from sandbox.projects.modadvert.RunComparison import ModadvertRunB2B
from sandbox.projects.modadvert.RunCupidMR import ModadvertRunCupidMR


class ModadvertTestCupidB2B(ModadvertRunB2B):
    """
    Runs B2B of Cupid automoderator on MapReduce
    """

    name = 'MODADVERT_TEST_CUPID_B2B'
    automoderator_name = 'cupid'

    class Parameters(ModadvertRunB2B.Parameters):

        with sdk2.parameters.Group('Comparison parameters') as comparison_group:
            comparison_root_dir = ModadvertRunB2B.Parameters.comparison_root_dir(default='//home/modadvert/test/cupid_comparison/')

        with sdk2.parameters.Group('Launch parameters') as launch_group:
            src_tables_dir = ModadvertRunB2B.Parameters.src_tables_dir(default='//logs/modadvert-sm-automoderator-results-log/1h')
            tmp_directory = ModadvertRunCupidMR.Parameters.tmp_directory(default='//home/modadvert/test/tmp/')
            runner_memory_limit = ModadvertRunCupidMR.Parameters.memory_limit()
            runner_job_count = ModadvertRunCupidMR.Parameters.job_count()
            runner_user_slots = ModadvertRunCupidMR.Parameters.user_slots()
            runner_max_failed_job_count = ModadvertRunCupidMR.Parameters.max_failed_job_count()
            runner_pool = ModadvertRunCupidMR.Parameters.pool()
            mount_sandbox_in_tmpfs = ModadvertRunCupidMR.Parameters.mount_sandbox_in_tmpfs()
            lock_attempts = ModadvertRunCupidMR.Parameters.lock_attempts()

        with sdk2.parameters.Group('Base parameters') as base_cupid_group:
            use_last_released_runners = sdk2.parameters.Bool('Use last released resources with Cupid MR runners as base runners', default=True)
            with use_last_released_runners.value[False]:
                base_mr_runners = sdk2.parameters.Dict('Named list with base LaaS MR-runners (key = object_type, value = resource_id)')

        with sdk2.parameters.Group('Feature parameters') as feature_cupid_group:
            feature_mr_runners = sdk2.parameters.Dict(
                'Named list with feature LaaS MR-runners (key = object_type, value = resource_id)',
                required=True
            )

    def _get_last_released_runners(self):
        return {
            object_type: sdk2.Resource.find(
                resource_type=MODADVERT_LAAS_MR_RUNNER_BINARY,
                attrs={'released': 'stable', 'component': 'cupid', 'object_type': object_type}
            ).first()
            for object_type in CUPID_OBJECT_TYPES
        }

    def create_runner_subtask(self, branch):
        comparison_dir = getattr(self.Context, 'comparison_{}_dir'.format(branch))
        if branch == 'base' and self.Parameters.use_last_released_runners:
            mr_runners = {
                object_type: resource.id
                for object_type, resource in self._get_last_released_runners().items()
                if resource is not None  # Handling case when released binaries for a object type doesn't exist yet (e.g. new object type)
            }
            logging.warning('Using last released resources as base resources: {}'.format(mr_runners))
        else:
            mr_runners = getattr(self.Parameters, '{}_mr_runners'.format(branch))
        return self.create_subtask(
            ModadvertRunCupidMR,
            {
                ModadvertRunCupidMR.Parameters.mr_runners.name: mr_runners,
                ModadvertRunCupidMR.Parameters.src_tables.name: [self.Context.src_table],
                ModadvertRunCupidMR.Parameters.dst_table.name: os.path.join(comparison_dir, 'verdicts'),
                ModadvertRunCupidMR.Parameters.tmp_directory.name: self.Parameters.tmp_directory,
                ModadvertRunCupidMR.Parameters.memory_limit.name: self.Parameters.runner_memory_limit,
                ModadvertRunCupidMR.Parameters.job_count.name: self.Parameters.runner_job_count,
                ModadvertRunCupidMR.Parameters.user_slots.name: self.Parameters.runner_user_slots,
                ModadvertRunCupidMR.Parameters.max_failed_job_count.name: self.Parameters.runner_max_failed_job_count,
                ModadvertRunCupidMR.Parameters.vault_user.name: self.Parameters.vault_user,
                ModadvertRunCupidMR.Parameters.tokens.name: self.Parameters.tokens,
                ModadvertRunCupidMR.Parameters.pool.name: self.Parameters.runner_pool,
                ModadvertRunCupidMR.Parameters.mount_sandbox_in_tmpfs.name: self.Parameters.mount_sandbox_in_tmpfs,
                ModadvertRunCupidMR.Parameters.lock_attempts.name: self.Parameters.lock_attempts,
            }
        )
