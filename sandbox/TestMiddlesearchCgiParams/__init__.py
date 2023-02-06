# -*- coding: utf-8 -*-

from sandbox.sandboxsdk.task import SandboxTask
from sandbox.sandboxsdk.channel import channel

from sandbox.projects.common import utils
from sandbox.projects.common.search.eventlog import eventlog
from sandbox.projects.common.middlesearch import single_host
from sandbox.projects.common.base_search_quality import cgi_params
from sandbox.projects import resource_types


class TestMiddlesearchCgiParams(single_host.MiddlesearchSingleHostTask):
    """
        Starts 1 middlesearch and 2 basesearch instances
        and tests cgi params declared in
        https://a.yandex-team.ru/arc/trunk/arcadia/search/request/consumers
    """
    type = 'TEST_MIDDLESEARCH_CGI_PARAMS'

    required_ram = 120 << 10

    input_parameters = single_host.PARAMS + cgi_params.PARAMS

    def on_enqueue(self):
        SandboxTask.on_enqueue(self)
        self.ctx['eventlog_out_resource_id'] = self.create_resource(
            'eventlog', 'event.log', resource_types.EVENTLOG_DUMP, arch='any'
        ).id

    def on_failure(self):
        eventlog.locate_instability_problems(self)
        single_host.MiddlesearchSingleHostTask.on_failure(self)

    def _get_middlesearch_additional_params(self):
        return {"event_log": channel.sandbox.get_resource(self.ctx['eventlog_out_resource_id']).path}

    def _use_middlesearch_component(self, middlesearch):
        with middlesearch:
            optimized = utils.get_or_default(self.ctx, cgi_params.CgiDiagonalMode)
            middlesearch.use_component(
                lambda: cgi_params.test_params(self.ctx, middlesearch, optimized=optimized)
            )


__Task__ = TestMiddlesearchCgiParams
