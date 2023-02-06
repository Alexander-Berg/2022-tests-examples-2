# -*- coding: utf-8 -*-

import logging
from sandbox.projects.common.dolbilka import DolbilkaExecutor
from sandbox.projects.websearch.basesearch.TestBasesearchPerformance import PlanParameter
from sandbox.projects.common.fusion.task import FusionTestTask
from sandbox.projects.common.fusion.task import FusionParamsDescription
from sandbox.projects.common import footers

import sandbox.common.types.client as ctc


class TestFusionPerformance(FusionTestTask):
    """
        An analogue of TEST_BASESEARCH_PERFORMANCE task with fusion specific taken into account.
    """
    type = 'TEST_FUSION_PERFORMANCE'
    client_tags = ctc.Tag.Group.LINUX

    input_parameters = FusionTestTask.input_parameters + (PlanParameter, ) + DolbilkaExecutor.input_task_parameters

    @property
    def footer(self):
        return footers.exec_stats_footer(self)

    execution_space = 120000

    def on_execute(self):
        plan = self.sync_resource(self.ctx['dolbilo_plan_resource_id'])

        distributor = None
        if self.use_distributor():
            distributor = self.get_distributor()

        fusion = self.get_fusion(get_db=self.is_db_resource_required(), max_documents=self.get_max_docs())
        if self.use_distributor():
            fusion.wait(is_ready=fusion.is_memorysearch_filled)

        d_executor = DolbilkaExecutor()
        results = []
        try:
            for i in xrange(d_executor.sessions):
                results.append(d_executor.run_session_and_dumper(plan, fusion, str(i), run_once=True))
                logging.debug("Tass data: %r", fusion.fetch_tass())
        finally:
            fusion.stop()
            if distributor is not None:
                distributor.stop()

        self.ctx['results'] = results
        self.ctx['requests_per_sec'] = [float(i['rps']) for i in results]
        self.ctx['max_rps'] = max(self.ctx['requests_per_sec'])
        self.dump_metrics({'max_rps': self.ctx['max_rps']}, self.log_path("teamcity-info.xml"))


TestFusionPerformance.__doc__ += FusionParamsDescription

__Task__ = TestFusionPerformance
