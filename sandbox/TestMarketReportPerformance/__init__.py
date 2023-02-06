# -*- coding: utf-8 -*-
import sandbox.projects.common.search.components.market_report as mr
import sandbox.projects.common.profiling as search_profiling
from sandbox.projects.common import dolbilka
from sandbox.projects.common import utils
from sandbox.common.types.misc import RamDriveType


class TestMarketReportPerformance(mr.MarketReportFiringTask, search_profiling.ProfilingTask):

    type = 'TEST_MARKET_REPORT_PERFORMANCE'
    execution_space = 204800  # 200Gb

    input_parameters = mr.REPORT_PERF_PARAMS + list(search_profiling.ProfilingTask.input_parameters)

    def on_execute(self):
        plan = self.sync_resource(self.ctx[mr.Plan.name])
        report = self._get_prepare_report()

        perf_data_path = self.abs_path('profiling_results')

        self._profiling_init(report, perf_data_path)

        self._set_up_dolbilka_ctx_params()
        d_executor = dolbilka.DolbilkaExecutor()
        results = d_executor.run_sessions(
            plan,
            report,
            run_once=True,
            need_warmup=True)

        dolbilka.DolbilkaPlanner.fill_rps_ctx(results, self.ctx)

        self._profiling_report(report, perf_data_path)

    def _set_up_dolbilka_ctx_params(self):
        # Долбилка будет долбить фиксированым RPS: --mode=plan --rps-fixed=160
        self.ctx[dolbilka.DolbilkaExecutorMode.name] = dolbilka.DolbilkaExecutorMode.PLAN_MODE
        session_count = 5
        profiling_type = utils.get_or_default(self.ctx, search_profiling.ProfilingTypeParameter)
        if profiling_type != search_profiling.ProfilingTypeParameter.NONE:
            # One iteration is more than enough for profiling.
            session_count = 1
        self.ctx[dolbilka.DolbilkaSessionsCount.name] = session_count
        self.ctx[dolbilka.DolbilkaExecutorRequestsLimit.name] = self._get_requests_limit(desired_request_limits=100000)

    def on_enqueue(self):
        mr.MarketReportFiringTask.on_enqueue(self)
        if self.ctx[mr.RamdriveEnabled.name]:
            self.ramdrive = self.RamDrive(
                RamDriveType.TMPFS,
                self.ctx[mr.RamdriveSizeParameter.name] * 1024,
                None)


__Task__ = TestMarketReportPerformance
