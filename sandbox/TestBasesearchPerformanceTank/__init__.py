from sandbox.sandboxsdk import parameters as sp

from sandbox.projects.common.search.basesearch import task as search_task
from sandbox.projects.common.search import performance as search_performance
from sandbox.projects.common.search import components as sc
from sandbox.projects.common.base_search_quality import settings as bss
from sandbox.projects.common import profiling as search_profiling
from sandbox.projects.common import error_handlers as eh
from sandbox.projects.common import utils
from sandbox.projects.websearch.basesearch import TestBasesearchPerformance as tbp


class UseOldStyleStats(sp.SandboxBoolParameter):
    name = 'old_style_stats'
    description = 'Use old style stats'
    default_value = False


class TestBasesearchPerformanceTank(
    search_performance.OldShootingTask,
    search_profiling.ProfilingTask,
    search_task.BasesearchComponentTask
):
    type = 'TEST_BASESEARCH_PERFORMANCE_TANK'
    client_tags = search_performance.OldShootingTask.client_tags & search_task.BasesearchComponentTask.client_tags
    required_ram = 100 << 10
    execution_space = bss.DOLBILKA_SPACE + bss.RESERVED_SPACE

    input_parameters = (
        sc.DefaultBasesearchParams.params + (tbp.PlanParameter,) +
        (
            tbp.FailRateThreshold,
            tbp.NotFoundRateThreshold,
            tbp.MinDataReadPerRequestParameter,
            tbp.IgnoreFirstNSessions,
            UseOldStyleStats,
        ) +
        search_task.BasesearchComponentTask.basesearch_common_parameters +
        search_performance.OldShootingTask.shoot_input_parameters +
        search_profiling.ProfilingTask.input_parameters
    )

    @property
    def footer(self):
        foot = []
        profiling_foot = search_profiling.ProfilingTask.profiling_footer(self)
        if profiling_foot:
            foot.append({
                'helperName': '',
                'content': profiling_foot,
            })
        performance_foot = search_performance.OldShootingTask.footer.fget(self)
        foot.append({
            'helperName': '',
            'content': performance_foot,
        })
        return foot

    @property
    def old_style_stats(self):
        return utils.get_or_default(self.ctx, UseOldStyleStats)

    def on_execute(self):
        basesearch = self._basesearch(sc.DefaultBasesearchParams)
        self._profiling_init(basesearch, self.__get_perf_data_path())
        self._init_virtualenv()
        with basesearch:
            self._old_shoot(basesearch, self.ctx[tbp.PlanParameter.name])
        self._profiling_report(basesearch, self.__get_perf_data_path())
        self._validate_responses()

    def _validate_responses(self):
        notfound_rate_threshold = self.ctx.get(tbp.NotFoundRateThreshold.name, 0.0)
        fail_rate_threshold = self.ctx.get(tbp.FailRateThreshold.name, 0.0)
        tbp.check_rate(fail_rate_threshold, self.ctx.get('min_fail_rate', 0.0), 'Fail')
        tbp.check_rate(notfound_rate_threshold, self.ctx.get('min_notfound_rate', 0.0), 'NotFound')

        min_median_response_size = utils.get_or_default(self.ctx, tbp.MinDataReadPerRequestParameter)
        shoot_results = self.ctx.get("results", [])
        if min_median_response_size and shoot_results:
            for r in shoot_results[utils.get_or_default(self.ctx, tbp.IgnoreFirstNSessions):]:
                size_median = r.get("resp_size_quantile_0.5")
                if size_median and size_median < min_median_response_size:
                    eh.check_failed(
                        "Too small response size: {} < {} bytes".format(size_median, min_median_response_size)
                    )
        self.ctx["average_q95_response_time"] = utils.count_avg([
            shoot_result.get("latency_0.95", 0) for shoot_result in shoot_results
        ])

    def get_short_task_result(self):
        if self.is_completed() and "max_rps" in self.ctx:
            return "{:0.2f}".format(self.ctx["max_rps"])

    def __get_perf_data_path(self):
        return self.abs_path("perf.data")


__Task__ = TestBasesearchPerformanceTank
