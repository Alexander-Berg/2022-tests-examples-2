# -*- coding: utf-8 -*-

from sandbox.sandboxsdk import parameters as sp

from sandbox.projects.common.fusion import distributor
from sandbox.projects.common.middlesearch import single_host
from sandbox.projects.common.search import components as sc
from sandbox.projects.common import dolbilka
from sandbox.projects.common import footers
from sandbox.projects import resource_types
from sandbox.projects.websearch.middlesearch import resources as ms_res


Fusion1Params = sc.create_fusion_params(1, old_task=True)
Fusion2Params = sc.create_fusion_params(2, old_task=True)

FusionPort1 = sc.DEFAULT_BASESEARCH_PORT
FusionPort2 = sc.DEFAULT_BASESEARCH_PORT + 100

FusionParams = sc.DefaultMiddlesearchParams.params + Fusion1Params.params + Fusion2Params.params + (
    # profiling
    single_host.RunProfilerParameter,
    single_host.UseGPerfToolsParameter,
    single_host.IgnoreBadDHErrors,
)

DistributorParams = distributor.DefaultDistributorParams.params


class PlanParameter(sp.ResourceSelector):
    name = 'dolbilo_plan_resource_id'
    description = 'Plan'
    resource_type = [
        ms_res.MiddlesearchPlan,
        resource_types.IMAGES_MIDDLESEARCH_PLAN,
        resource_types.VIDEO_MIDDLESEARCH_PLAN,
    ]
    required = True


class TestMiddlesearchSingleHostFusion(single_host.MiddlesearchSingleHostTask):
    """
        1 middlesearch 2 fusion instances on single host + d-executor
    """

    type = 'TEST_MIDDLESEARCH_SINGLE_HOST_FUSION'

    current_shard = 0
    total_shards = 2
    distributor = None

    input_parameters = \
        FusionParams \
        + DistributorParams \
        + (PlanParameter, ) \
        + dolbilka.DolbilkaExecutor.input_task_parameters

    @property
    def footer(self):
        return footers.exec_stats_footer(self)

    def init_search_component(self, middlesearch):
        middlesearch.disable_cache()

    def _use_middlesearch_component(self, middlesearch):
        plan = self.sync_resource(self.ctx[PlanParameter.name])

        d_executor = dolbilka.DolbilkaExecutor()

        results = d_executor.run_sessions(plan, middlesearch, run_once=True)
        dolbilka.DolbilkaPlanner.fill_rps_ctx(results, self.ctx)

    def _create_basesearch(self, params_, port_):
        db_source = self.ctx[params_.DbSource.name]
        use_distributor = self.ctx[distributor.DefaultDistributorParams.EnableDistributor.name]

        if use_distributor and self.distributor is None:
            self.distributor = distributor.create_distributor()
            self.distributor.start()

        get_db = False
        waiter = sc.FUSION_WAIT_SEARCHER
        if db_source == sc.FUSION_DB_PRE_CREATED:
            get_db = True
            waiter = sc.FUSION_WAIT_INDEX
        if use_distributor:
            waiter = sc.FUSION_WAIT_MEMORY_FILLED

        shard = self.current_shard
        shards_count = self.total_shards
        self.current_shard += 1

        return sc.get_fusion_search(
            params=params_,
            port=port_,
            shard=shard,
            shards_count=shards_count,
            get_db=get_db,
            default_wait=waiter
        )

    def _get_basesearch_params(self):
        return Fusion1Params, Fusion2Params

    def _get_basesearch_ports_for_basesearch(self):
        return FusionPort1, FusionPort2


__Task__ = TestMiddlesearchSingleHostFusion
