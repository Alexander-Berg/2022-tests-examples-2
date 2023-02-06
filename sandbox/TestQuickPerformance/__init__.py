# -*- coding: utf-8 -*-

from sandbox.projects.common.dolbilka import DolbilkaExecutor
from sandbox.projects.websearch.basesearch.TestBasesearchPerformance import PlanParameter
from sandbox.projects.common.fusion.task import FusionTestTask
from sandbox.projects.common.search import components as sc
from sandbox.projects.common import footers

import sandbox.common.types.client as ctc


class TestQuickPerformance(FusionTestTask):
    type = 'TEST_QUICK_PERFORMANCE'

    input_parameters = FusionTestTask.input_parameters + (PlanParameter, ) + DolbilkaExecutor.input_task_parameters + sc.DefaultMiddlesearchParams.params
    client_tags = ctc.Tag.LINUX_PRECISE

    @property
    def footer(self):
        return footers.exec_stats_footer(self)

    execution_space = 90000

    def on_execute(self):
        plan = self.sync_resource(self.ctx['dolbilo_plan_resource_id'])

        distributor = None
        if self.use_distributor():
            distributor = self.get_distributor()

        fusion = self.get_fusion(get_db=self.is_db_resource_required(), max_documents=self.get_max_docs())
        if self.use_distributor():
            fusion.wait(is_ready=fusion.is_memorysearch_filled)

        middlesearch = sc.get_middlesearch(
            basesearches=[
                {
                    'basesearch_type': 'FUSION_KUBR',
                    'hosts_and_ports': [('localhost', fusion.get_port())],
                    'collection': '',
                }
            ]
        )

        middlesearch.disable_cache()

        d_executor = DolbilkaExecutor()
        results = []
        try:
            for i in xrange(d_executor.sessions):
                results.append(d_executor.run_session_and_dumper(plan, middlesearch, str(i), run_once=True))
        finally:
            fusion.stop()
            if distributor is not None:
                distributor.stop()

        self.ctx['results'] = results
        self.ctx['requests_per_sec'] = [float(i['rps']) for i in results]
        self.ctx['max_rps'] = max(self.ctx['requests_per_sec'])
        self.dump_metrics({'max_rps': self.ctx['max_rps']}, self.log_path("teamcity-info.xml"))


__Task__ = TestQuickPerformance
