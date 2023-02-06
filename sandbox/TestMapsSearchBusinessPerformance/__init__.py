# -*- coding: utf-8 -*-

import sandbox.common.types.client as ctc
from sandbox.sandboxsdk.task import SandboxTask
from sandbox.sandboxsdk.parameters import SandboxBoolParameter
from sandbox.sandboxsdk.parameters import LastReleasedResource
from sandbox.projects.common.dolbilka import DolbilkaExecutor

from sandbox.projects.common.geosearch.search_components import GetMapsSearchBusinessParams
from sandbox.projects.common.geosearch.search_components import get_maps_search_business
from sandbox.projects.common import footers


class PlanParameter(LastReleasedResource):
    name = 'dolbilo_plan_resource_id'
    description = 'Plan'
    resource_type = ['BASESEARCH_PLAN']


class RunProfilerParameter(SandboxBoolParameter):
    name = 'run_profiler'
    description = 'Run profiler'
    default_value = False


class TestMapsSearchBusinessPerformance(SandboxTask):
    type = 'TEST_MAPS_SEARCH_BUSINESS_PERFORMANCE'

    required_ram = 50 << 10
    client_tags = ctc.Tag.Group.LINUX & ctc.Tag.INTEL_E5_2650

    @property
    def footer(self):
        return footers.exec_stats_footer(self)

    MapsSearchBusinessParams = GetMapsSearchBusinessParams()

    input_parameters = \
        MapsSearchBusinessParams.params \
        + (PlanParameter,
           RunProfilerParameter) \
        + DolbilkaExecutor.input_task_parameters

    def on_execute(self):

        component = get_maps_search_business(self.ctx)

        self.init_search_component(component)

        plan = self.sync_resource(self.ctx[PlanParameter.name])
        d_executor = DolbilkaExecutor()

        results = d_executor.run_sessions(plan, component, run_once=True)

        self.ctx['results'] = results
        self.ctx['requests_per_sec'] = []
        for result in results:
            try:
                rps = float(result['rps'])
            except ValueError:
                rps = 0
            self.ctx['requests_per_sec'].append(rps)
        self.ctx['max_rps'] = max(self.ctx['requests_per_sec'])

    def init_search_component(self, search_component):
        pass

    def get_results(self):
        if not self.is_completed():
            return 'Results are not ready yet.'

        return 'Max rps: %s. All rps: %s' % (self.ctx.get('max_rps', 'unknown'),
                                             self.ctx.get('requests_per_sec', 'unknown'))

    def get_short_task_result(self):
        if not self.is_completed():
            return None

        rps = self.ctx.get('max_rps', None)
        if rps:
            return str(rps)


__Task__ = TestMapsSearchBusinessPerformance
