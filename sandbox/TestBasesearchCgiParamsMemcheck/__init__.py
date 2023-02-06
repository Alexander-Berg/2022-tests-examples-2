# -*- coding: utf-8 -*-

from sandbox.projects.websearch.basesearch.TestBasesearchCgiParams import TestBasesearchCgiParams
from sandbox.projects.common.search import memcheck
from sandbox.projects.common.search import components as sc


base_class = memcheck.generate_task(
    sc.DefaultBasesearchParams,
    TestBasesearchCgiParams,
)


class TestBasesearchCgiParamsMemcheck(base_class):
    type = 'TEST_BASESEARCH_CGI_PARAMS_MEMCHECK'

    def initCtx(self):
        base_class.initCtx(self)

        # test is very slow so we need to filter source queries before mixing them with cgi params
        self.ctx['use_queries_with_found_docs'] = True


__Task__ = TestBasesearchCgiParamsMemcheck
