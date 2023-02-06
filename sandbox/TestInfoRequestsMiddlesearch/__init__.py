# -*- coding: utf-8 -*-

from sandbox.projects.common.middlesearch import single_host
from sandbox.projects.common.base_search_quality import info_requests

import logging

class TestInfoRequestsMiddlesearch(single_host.MiddlesearchSingleHostTask):
    """
        Starts 1 middlesearch and 2 basesearch instances
        and tests info requests
    """

    type = 'TEST_INFO_REQUESTS_MIDDLESEARCH'

    input_parameters = single_host.PARAMS + info_requests.PARAMS

    def _use_middlesearch_component(self, middlesearch):
        try:
            info_requests.test_info_requests(middlesearch)
        except Exception as e: # Mute TaskFailure. Motivation see: MIDDLE-625 & MIDDLE-621
            logging.info(e)
            return

    def init_search_component(self, middlesearch):
        middlesearch.set_cache_thread_limit()
        # prevent basesearch DoS
        middlesearch.config.apply_local_patch({
            'Collection/MaxSnippetsPerRequest': 150,
            'Collection/MaxAllfactorsPerBasesearch': 150,
        })


__Task__ = TestInfoRequestsMiddlesearch
