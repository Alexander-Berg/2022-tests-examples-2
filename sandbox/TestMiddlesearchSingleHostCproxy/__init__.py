# -*- coding: utf-8 -*-

from sandbox.projects.websearch.middlesearch.TestMiddlesearchSingleHost import TestMiddlesearchSingleHost
from sandbox.projects.common.middlesearch.single_host import BASE1_PORT, BASE2_PORT
from sandbox.projects.common.search.components.cproxy import get_cproxy


class TestMiddlesearchSingleHostCproxy(TestMiddlesearchSingleHost):
    type = 'TEST_MIDDLESEARCH_SINGLE_HOST_CPROXY'

    def _get_basesearch_ports_for_middlesearch(self):
        proxy_port1 = BASE1_PORT + 10
        proxy_port2 = BASE2_PORT + 10

        proxy = {
            proxy_port1: "localhost:%s" % BASE1_PORT,
            proxy_port2: "localhost:%s" % BASE2_PORT
        }
        cproxy = get_cproxy(self, proxy)
        cproxy.start(timeout=None, save_logs=True)
        cproxy.wait_port()

        return proxy_port1, proxy_port2


__Task__ = TestMiddlesearchSingleHostCproxy
