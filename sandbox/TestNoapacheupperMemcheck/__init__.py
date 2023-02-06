# -*- coding: utf-8 -*-

from sandbox.projects.common.search import memcheck
from sandbox.projects.common.search import components as sc
from sandbox.projects.common.noapacheupper.search_component import create_noapacheupper_params
from sandbox.projects.websearch.upper.TestNoapacheupper import TestNoapacheupper

Memchecked = memcheck.generate_task(
    create_noapacheupper_params(),
    TestNoapacheupper,
    start_timeout=sc.DEFAULT_START_TIMEOUT * 2)


class TestNoapacheupperMemcheck(Memchecked):
    """
        Search memory leak and other access memory errors in noapacheupper
    """

    type = 'TEST_NOAPACHEUPPER_MEMCHECK'


__Task__ = TestNoapacheupperMemcheck
