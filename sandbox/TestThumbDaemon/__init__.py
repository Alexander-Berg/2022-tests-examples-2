# -*- coding: utf-8 -*-

import logging

from sandbox.sandboxsdk.task import SandboxTask
from sandbox.sandboxsdk.parameters import LastReleasedResource
from sandbox.sandboxsdk.parameters import SandboxBoolParameter
from sandbox.projects.common.dolbilka import DolbilkaExecutor
from sandbox.projects.common.search.components import DefaultThumbDaemonParameters, get_thumb_daemon


class TestThumbDaemonPlan(LastReleasedResource):
    name = 'thumb_daemon_dolbilo_plan_resource_id'
    description = 'Thumb daemon plan:'
    resource_type = 'THUMB_DAEMON_PLAN'


class RunProfilerParameter(SandboxBoolParameter):
    name = 'run_profiler'
    description = 'Run profiler (gperf tools)'
    default_value = False


class TestThumbDaemon(SandboxTask):
    CPU_COUNT = 24
    MAX_RPS_KEY = 'max_rps'
    ALL_RPS_KEY = 'requests_per_sec'

    type = 'TEST_THUMB_DAEMON'

    input_parameters = DefaultThumbDaemonParameters.params +\
                       (TestThumbDaemonPlan,) +\
                       DolbilkaExecutor.input_task_parameters +\
                       (RunProfilerParameter,)

    cpu_model = 'E5645'

    def get_results(self):
        if not self.is_completed():
            return 'Results are not ready yet.'

        return 'Max rps: %s. All rps: %s' % (self.ctx.get(self.MAX_RPS_KEY, 'unknown'),
                                             self.ctx.get(self.ALL_RPS_KEY, 'unknown'))

    def get_short_task_result(self):
        if not self.is_completed():
            return None

        return str(self.ctx.get(self.MAX_RPS_KEY, ""))

    def on_execute(self):
        thumb_daemon_plan = self.sync_resource(self.ctx['thumb_daemon_dolbilo_plan_resource_id'])

        logging.info('Run thumb daemon...')

        use_profiler = self.ctx[RunProfilerParameter.name]
        thumb_daemon = get_thumb_daemon(
            use_profiler=use_profiler,
            use_gperftools=use_profiler
        )

        d_executor = DolbilkaExecutor()
        results = d_executor.run_sessions(thumb_daemon_plan, thumb_daemon)

        self.ctx['results'] = results
        self.ctx[self.ALL_RPS_KEY] = [float(i['rps']) for i in results]
        self.ctx[self.MAX_RPS_KEY] = max(self.ctx[self.ALL_RPS_KEY])


__Task__ = TestThumbDaemon
