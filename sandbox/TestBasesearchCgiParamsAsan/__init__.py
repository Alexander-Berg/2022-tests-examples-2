# -*- coding: utf-8 -*-

from sandbox.projects.websearch.basesearch.TestBasesearchCgiParams import TestBasesearchCgiParams
from sandbox.projects.common import sanitizer
from sandbox.projects.common.search import components as sc


AddressSanitized = sanitizer.generate_task(
    sc.DefaultBasesearchParams,
    TestBasesearchCgiParams,
    start_timeout=sc.DEFAULT_START_TIMEOUT * 2
)


class TestBasesearchCgiParamsAsan(AddressSanitized):
    type = 'TEST_BASESEARCH_CGI_PARAMS_ASAN'

    def initCtx(self):
        AddressSanitized.initCtx(self)
        # test is very slow so we need to filter source queries before mixing them with cgi params
        self.ctx['use_queries_with_found_docs'] = True


__Task__ = TestBasesearchCgiParamsAsan
