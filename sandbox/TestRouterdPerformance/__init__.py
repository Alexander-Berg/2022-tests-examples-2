# -*- coding: utf-8 -*-

from sandbox.sandboxsdk.task import SandboxTask
from sandbox.sandboxsdk import parameters as sp
from sandbox.sandboxsdk import paths

from sandbox.projects import resource_types
from sandbox.projects.common import dolbilka
from sandbox.projects.common import footers
from sandbox.projects.common.news.routerd import Routerd, create_routerd_params

import sandbox.common.types.client as ctc


class PlanParameter(sp.LastReleasedResource):
    name = 'dolbilo_plan_resource_id'
    description = 'Plan'
    resource_type = [
        resource_types.BASESEARCH_PLAN,
    ]


class TestRouterdPerformance(SandboxTask):
    """
        Измеряет производительность Routerd с заданным планом обстрела.
        Проводит 1 серию из N стрельб, замеряет RPS с помощью dolbilo.
    """

    type = 'TEST_ROUTERD_PERFORMANCE'
    client_tags = ctc.Tag.Group.LINUX

    @property
    def footer(self):
        return footers.exec_stats_footer(self)

    routerd_params = create_routerd_params()
    input_parameters = \
        routerd_params.params \
        + (
            PlanParameter,
        ) \
        + dolbilka.DolbilkaExecutor.input_task_parameters

    def on_execute(self):
        workdir = self.path('work')
        paths.make_folder(workdir, True)
        port = 17171

        routerd = Routerd(
            binary=self.sync_resource(self.ctx[self.routerd_params.Binary.name]),
            workdir=workdir,
            port=port,
            geobase=self.sync_resource(self.ctx[self.routerd_params.Geobase.name]),
            newsdata=self.sync_resource(self.ctx[self.routerd_params.NewsData.name])+"/newsdata2.json",
            newsdata_exp=self.sync_resource(self.ctx[self.routerd_params.NewsDataExp.name])+"/newsdata2.json",
            device_data=self.sync_resource(self.ctx[self.routerd_params.DeviceData.name]),
            allowed_origins=self.sync_resource(self.ctx[self.routerd_params.AllowedOrigins.name]),
            dynamic_robots_txt=self.sync_resource(self.ctx[self.routerd_params.DynamicRobotsTxtConfig.name]),
        )

        d_executor = dolbilka.DolbilkaExecutor()

        results = d_executor.run_sessions(
            self.sync_resource(self.ctx[PlanParameter.name]),
            routerd,
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


__Task__ = TestRouterdPerformance
