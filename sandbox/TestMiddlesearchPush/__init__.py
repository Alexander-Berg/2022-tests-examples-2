# -*- coding: utf-8 -*-

import logging
import time

from sandbox.sandboxsdk import parameters as sp
from sandbox.sandboxsdk.channel import channel

from sandbox.projects import resource_types
from sandbox.projects.common.middlesearch.response_patcher import response_patcher
from sandbox.projects.common.middlesearch import single_host
from sandbox.projects.common.base_search_quality import response_saver
from sandbox.projects.common.base_search_quality import threadPool
from sandbox.projects.common import utils
from sandbox.projects.common.search.response import cgi as response_cgi

_RESPONSE_SAVER_PARAMS = response_saver.create_response_saver_params(
    queries_resource=[
        resource_types.PLAIN_TEXT_QUERIES,
        resource_types.IMAGES_MIDDLESEARCH_PLAIN_TEXT_REQUESTS,
        resource_types.VIDEO_MIDDLESEARCH_PLAIN_TEXT_REQUESTS
    ]
)


class WaitPushedResponses(sp.SandboxIntegerParameter):
    name = "wait_pushed_responses"
    description = 'Wait for pushed responses (time in seconds)'
    default_value = 5 * 60


class TestMiddlesearchPush(single_host.MiddlesearchSingleHostTask):
    """
        Тестирует push-технологию (SEARCH-986)
    """

    type = 'TEST_MIDDLESEARCH_PUSH'

    input_parameters = single_host.PARAMS + _RESPONSE_SAVER_PARAMS.params + threadPool.PARAMS + (WaitPushedResponses,)

    def on_enqueue(self):
        single_host.MiddlesearchSingleHostTask.on_enqueue(self)

        for n in ["initial", "timeouted", "pushed"]:
            self.ctx["{}_responses_id".format(n)] = self.create_resource(
                "{}_responses, {}".format(n, self.descr),
                "{}_responses.txt".format(n),
                resource_types.BASESEARCH_HR_RESPONSES,
                arch='any',
            ).id

    def _use_middlesearch_component(self, middlesearch):
        #  исходные ответы
        logging.info("Start getting initial responses")
        self._get_responses(middlesearch, "initial_responses_id")
        #  ответы, полученные с маленьким таймаутом
        logging.info("Start getting timeouted responses")
        self._get_responses(
            middlesearch, "timeouted_responses_id",
            queries_patchers=[lambda q: response_cgi.force_timeout(q, 4000)],
            prepare_session_callback=middlesearch.clear_cache,
            need_max_timeout=False,
            on_end_get_responses=self._wait_func()
        )
        #  ответы, полученные из кеша через push-технологию
        logging.info("Start getting pushed responses")
        self._get_responses(
            middlesearch, "pushed_responses_id",
            queries_patchers=[lambda q: response_cgi.force_timeout(q, 4000)],
            need_max_timeout=False,
        )

        #brp.compare_responses(first_resource_to_save, second_resource_to_save)

    def _get_responses(
        self, middlesearch, res_name,
        queries_patchers=None,
        prepare_session_callback=None,
        need_max_timeout=True,
        on_end_get_responses=None
    ):
        response_saver.save_responses(
            self.ctx,
            search_component=middlesearch,
            responses_resource=channel.sandbox.get_resource(self.ctx[res_name]),
            queries_patchers=queries_patchers,
            response_patchers=[response_patcher],
            need_max_timeout=need_max_timeout,
            prepare_session_callback=prepare_session_callback,
            need_dbgrlv=False,  # иначе не пишет запросы в кеш
            on_end_get_responses=on_end_get_responses
        )

    def _wait_func(self):
        wait_time = utils.get_or_default(self.ctx, WaitPushedResponses)

        def wait_push():
            logging.info("WAIT pushed queries for %s seconds", wait_time)
            time.sleep(wait_time)

        return wait_push


__Task__ = TestMiddlesearchPush
