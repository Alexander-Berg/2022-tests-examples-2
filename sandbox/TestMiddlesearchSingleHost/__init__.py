# -*- coding: utf-8 -*-

from sandbox.sandboxsdk import parameters as sp

import sandbox.common.types.client as ctc

from sandbox.projects.common.middlesearch import single_host
from sandbox.projects.common import error_handlers as eh
from sandbox.projects.common import utils
from sandbox.projects.common import dolbilka
from sandbox.projects.common import footers
from sandbox.projects.common.search import metadebug
from sandbox.projects.common.search.eventlog import eventlog
from sandbox.projects import PatchPlan


class PlanParameter(sp.ResourceSelector):
    name = 'dolbilo_plan_resource_id'
    description = 'Plan'
    resource_type = [
        'MIDDLESEARCH_PLAN',
        'IMAGES_MIDDLESEARCH_PLAN',
        'VIDEO_MIDDLESEARCH_PLAN',
    ]
    required = True


class TestMiddlesearchSingleHost(single_host.MiddlesearchSingleHostTask):
    """
        1 middlesearch 2 basesearch instances on single host + d-executor
    """

    type = 'TEST_MIDDLESEARCH_SINGLE_HOST'

    required_ram = 96 << 10
    client_tags = ctc.Tag.LINUX_PRECISE

    input_parameters = (
        single_host.PARAMS +
        (
            PlanParameter,
            PatchPlan.AddCgiParameter,
            PatchPlan.RemoveCgiParameters,
            metadebug.PARAMS.UseTcpdump,
        ) +
        dolbilka.DolbilkaExecutor.input_task_parameters
    )

    @property
    def footer(self):
        return footers.exec_stats_footer(self)

    def init_search_component(self, middlesearch):
        middlesearch.disable_cache()

    def _use_middlesearch_component(self, middlesearch):
        plan_id = self.ctx[PlanParameter.name]
        cgi_params = utils.get_or_default(self.ctx, PatchPlan.AddCgiParameter)
        remove_cgi_params = utils.get_or_default(self.ctx, PatchPlan.RemoveCgiParameters)
        if cgi_params or remove_cgi_params:
            plan_path = dolbilka.patch_plan_resource(plan_id, cgi_params, remove_cgi_params).path
        else:
            plan_path = self.sync_resource(plan_id)

        d_executor = dolbilka.DolbilkaExecutor()

        tcp_dump_proc = metadebug.start_tcpdump(
            self.ctx,
            ports=[
                single_host.BASE1_PORT,
                single_host.BASE2_PORT,
            ],
        )
        try:
            results = d_executor.run_sessions(plan_path, middlesearch, run_once=True)
        except:
            raise
        finally:
            # any problem with running can raise exception
            # but tcpdump should be stopped before we fail the task
            metadebug.stop_tcpdump(tcp_dump_proc)

        dolbilka.DolbilkaPlanner.fill_rps_ctx(results, self.ctx)

        try:
            eventlog.locate_instability_problems(self)
        except Exception as err:
            eh.log_exception("Unanswers locating failed. ", err)


__Task__ = TestMiddlesearchSingleHost
