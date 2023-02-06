# -*- coding: utf-8 -*-

from sandbox.sandboxsdk.task import SandboxTask
from sandbox.sandboxsdk import parameters as sp
from sandbox.sandboxsdk import paths

from sandbox.projects import resource_types
from sandbox.projects.common import dolbilka
from sandbox.projects.common import footers
from sandbox.projects.common.news.newsd import SlaveNewsd, create_newsd_params

import sandbox.common.types.client as ctc


class PlanParameter(sp.LastReleasedResource):
    name = 'dolbilo_plan_resource_id'
    description = 'Plan'
    resource_type = [
        resource_types.BASESEARCH_PLAN,
    ]


class ApphostMode(sp.SandboxBoolParameter):
    name = 'apphost_mode'
    description = 'Shoot to AppHost port'
    default_value = False


class RedefineApphostSlaveQueueSize(sp.SandboxBoolParameter):
    name = 'redefine_apphost_slave_queue_size'
    description = 'Redefine apphost slave queue size'
    default_value = False
    group = "Newsd apphost params"


class ApphostSlaveQueueSize(sp.SandboxIntegerParameter):
    name = 'apphost_slave_queue_size'
    description = 'Apphost slave queue size (It\'s better to be more than <Max simultaneous requests> param in dolbilo params )'
    default_value = 300
    group = "Newsd apphost params"


class TestNewsdPerformance(SandboxTask):
    """
        Измеряет производительность newsd с заданным планом обстрела.
        Проводит 1 серию из N стрельб, замеряет RPS с помощью dolbilo.
    """

    type = 'TEST_NEWSD_PERFORMANCE'
    client_tags = ctc.Tag.LINUX_PRECISE

    @property
    def footer(self):
        return footers.exec_stats_footer(self)

    newsd_params = create_newsd_params()
    input_parameters = \
        newsd_params.params \
        + (
            PlanParameter,
            ApphostMode,
            RedefineApphostSlaveQueueSize,
            ApphostSlaveQueueSize,
        ) \
        + dolbilka.DolbilkaExecutor.input_task_parameters

    def on_execute(self):
        workdir = self.path('work')
        paths.make_folder(workdir, True)
        port = 17171

        newsd = SlaveNewsd(
            workdir=workdir,
            binary=self.sync_resource(self.ctx[self.newsd_params.Binary.name]),
            cfg=self.sync_resource(self.ctx[self.newsd_params.Config.name]),
            port=port,
            state=self.sync_resource(self.ctx[self.newsd_params.StateDump.name]),
            geobase=self.sync_resource(self.ctx[self.newsd_params.Geobase.name]),
            index_config_path=self.sync_resource(self.ctx[self.newsd_params.IndexConfig.name]),
            app_host_mode=self.ctx.get(ApphostMode.name),
            app_host_queue_size=self.ctx.get(ApphostSlaveQueueSize.name) if self.ctx.get(RedefineApphostSlaveQueueSize.name) else None,
        )

        d_executor = dolbilka.DolbilkaExecutor()

        results = d_executor.run_sessions(
            self.sync_resource(self.ctx[PlanParameter.name]),
            newsd,
            run_once=True,
        )

        dolbilka.DolbilkaPlanner.fill_rps_ctx(results, self.ctx)

    def get_results(self):
        if not self.is_completed():
            return 'Results are not ready yet.'

        return 'Max RPS: {}. All RPS: {}'.format(
            self.ctx.get('max_rps', 'unknown'), self.ctx.get('requests_per_sec', 'unknown')
        )

    def get_short_task_result(self):
        if not self.is_completed():
            return None

        rps = self.ctx.get('max_rps', None)
        if rps:
            return str(rps)


__Task__ = TestNewsdPerformance
