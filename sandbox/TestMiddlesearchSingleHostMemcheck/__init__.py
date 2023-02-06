# -*- coding: utf-8 -*-

from sandbox.projects.websearch.middlesearch.TestMiddlesearchSingleHost import TestMiddlesearchSingleHost
from sandbox.projects.common.search import memcheck
from sandbox.projects.common.search import components as sc

Memchecked = memcheck.generate_task(
    sc.DefaultMiddlesearchParams,
    TestMiddlesearchSingleHost,
    start_timeout=sc.DEFAULT_START_TIMEOUT * 3,
    valgrind_version='3.9.0a1')


class TestMiddlesearchSingleHostMemcheck(Memchecked):
    type = 'TEST_MIDDLESEARCH_SINGLE_HOST_MEMCHECK'
    required_ram = 120 << 10  # 120Gb


__Task__ = TestMiddlesearchSingleHostMemcheck
