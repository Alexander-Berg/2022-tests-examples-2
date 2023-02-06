# -*- coding: utf-8 -*-

from time import sleep

from sandbox.projects.common.search import memcheck
from sandbox.projects.common.search import components as sc
from sandbox.projects.common.noapacheupper.search_component import create_noapacheupper_params
from sandbox.projects.websearch.upper.GetStandaloneNoapacheupperResponses import GetStandaloneNoapacheupperResponses

Memchecked = memcheck.generate_task(
    create_noapacheupper_params(neh_cache_mode='read'),
    GetStandaloneNoapacheupperResponses,
    start_timeout=sc.DEFAULT_START_TIMEOUT * 2)


class TestStandaloneNoapacheupperMemcheck(Memchecked):
    """
        Search memory leak and other access memory errors in noapacheupper
    """

    type = 'TEST_STANDALONE_NOAPACHEUPPPER_MEMCHECK'

    def on_start_get_responses(self):
        sleep(60)  # give more time for slow start with valgrind

    def on_execute(self):
        self.ctx['process_count'] = 1
        super(TestStandaloneNoapacheupperMemcheck, self).on_execute()


__Task__ = TestStandaloneNoapacheupperMemcheck
